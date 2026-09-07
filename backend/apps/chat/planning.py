"""Protocol-neutral parsing and structural validation of physical plans.

Business consistency belongs to ``intent_validation``. This module knows only
how to turn one model payload into safe protocol-native plans; it never accepts
or reconstructs a business contract.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

import orjson

from apps.protocol import QueryPlan
from common.utils.json_utils import extract_nested_json

logger = logging.getLogger(__name__)
_BRIEF_MAX_LENGTH = 20


@dataclass(frozen=True)
class BatchParseResult:
    plans: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    plan_validated: bool = False

    @property
    def success(self) -> bool:
        return bool(self.plans) and not self.errors

    @property
    def error_message(self) -> str | None:
        return "\n".join(self.errors) if self.errors else None


def executable_plans(parsed: BatchParseResult | None) -> list[dict[str, Any]]:
    return list(parsed.plans) if parsed is not None and parsed.success else []


def _plan_dict_from_query_plan(plan: QueryPlan) -> dict[str, Any]:
    return {
        "sql": plan.payload.get("sql", plan.statement),
        "format_statement": plan.statement,
        "tables": list(plan.resources or []),
        "chart_type": plan.chart_type or "table",
        "brief": plan.brief or "",
        "message": plan.message,
        "payload": dict(plan.payload or {}),
    }


def _apply_display_defaults(
    plans: list[dict[str, Any]], question: str
) -> list[dict[str, Any]]:
    fallback = " ".join((question or "").split()).strip()
    multiple = len(plans) > 1
    for index, plan in enumerate(plans):
        title = str(plan.get("brief") or fallback).strip() or fallback
        suffix = f"（{index + 1}）" if multiple else ""
        plan["brief"] = title[: _BRIEF_MAX_LENGTH - len(suffix)] + suffix
        plan["presentation_title"] = title + suffix
    return plans


_TECHNICAL_ANNOTATION_MARKERS = (
    "兼容",
    "写法",
    "cte",
    "子查询",
    "方言",
    "修复",
    "改写",
    "重写",
    "不使用",
    "未使用",
    "不含",
    "mysql",
    "starrocks",
    "版本",
)


def _strip_technical_annotations(title: str) -> str:
    """Drop trailing（…）/(…) groups that document the implementation.

    Repairer-written descriptions often append notes like
    "（MySQL兼容写法，不使用CTE）" — real information for the fix, noise for
    a tab title. Business parentheticals (conditions, scope) are kept.
    """
    text = title.strip()
    changed = True
    while changed:
        changed = False
        for open_mark, close_mark in (("（", "）"), ("(", ")")):
            if not text.endswith(close_mark):
                continue
            open_index = text.rfind(open_mark)
            if open_index < 0:
                continue
            inner = text[open_index + 1 : -1]
            if any(marker in inner.lower() for marker in _TECHNICAL_ANNOTATION_MARKERS):
                text = text[:open_index].rstrip(" ，,；;-—")
                changed = True
    return text or title


def apply_batch_display_defaults(
    plans: list[dict[str, Any]], question: str
) -> list[dict[str, Any]]:
    """Batch-boundary display defaults: per-dataset description → tab title.

    Per-query parsing applies defaults with a single-plan view, so the batch
    numbering（1）（2）never fires there. The batch caller (decision parse,
    revalidation, repair acceptance) owns the authoritative titles: reset each
    plan's brief from its ``description`` (with technical annotations
    stripped) and apply the defaults once here.
    """
    for plan in plans:
        description = str(plan.get("description") or "").strip()
        if description:
            plan["brief"] = _strip_technical_annotations(description)
    return _apply_display_defaults(plans, question)


def _accept_plan(
    llm_service: Any, plan: QueryPlan
) -> tuple[dict[str, Any] | None, str | None]:
    if not plan.success:
        return None, plan.message or None
    validated = llm_service.protocol.validate_plan(
        llm_service.ds,
        plan,
        llm_service.table_name_list,
    )
    if not validated.success:
        message = validated.message or "Plan validation failed"
        logger.warning("Plan validation failed: %s", message)
        return None, message
    entry = _plan_dict_from_query_plan(validated)
    entry["format_statement"] = llm_service.protocol.format_statement_for_display(
        validated
    )
    entry["sql"] = validated.payload.get("sql", validated.statement)
    return entry, None


def _result(plans: list[dict[str, Any]], question: str) -> BatchParseResult:
    return BatchParseResult(
        plans=_apply_display_defaults(plans, question),
        plan_validated=True,
    )


def parse_query_generation(
    raw_text: str | Mapping[str, Any],
    llm_service: Any,
    *,
    max_batch_size: int,
) -> BatchParseResult:
    """Parse and validate one physical-plan response as an atomic batch.

    ``Mapping`` is the canonical Query Agent boundary and is parsed as a
    protocol-native candidate. ``str`` remains the legacy standalone model
    response boundary until its callers are removed.
    """
    plans: list[dict[str, Any]] = []
    errors: list[str] = []
    chat_question = getattr(llm_service, "chat_question", None)
    question = str(
        getattr(chat_question, "generation_question", "")
        or getattr(chat_question, "question", "")
        or ""
    )
    if isinstance(raw_text, Mapping):
        plan = llm_service.protocol.parse_candidate_payload(raw_text)
        if not plan.success:
            return BatchParseResult(
                errors=[plan.message or "Query plan payload is invalid"]
            )
        entry, error = _accept_plan(llm_service, plan)
        return (
            _result([entry], question)
            if entry
            else BatchParseResult(errors=[error or "Query plan validation failed"])
        )
    json_str = extract_nested_json(raw_text)
    if json_str is None:
        plan = llm_service.protocol.parse_llm_output(raw_text)
        if not plan.success:
            return BatchParseResult(
                errors=[plan.message or "Query answer is not valid JSON"]
            )
        entry, error = _accept_plan(llm_service, plan)
        return (
            _result([entry], question)
            if entry
            else BatchParseResult(errors=[error or "Query plan validation failed"])
        )
    try:
        data = orjson.loads(json_str)
    except Exception:
        return BatchParseResult(errors=["Cannot parse query answer"])
    items = data if isinstance(data, list) else [data]
    if len(items) > max_batch_size:
        return BatchParseResult(
            errors=[f"计划数量 {len(items)} 超过单批上限 {max_batch_size}"]
        )
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"计划 {index + 1}: 不是有效的 JSON 对象")
            continue
        plan = llm_service.protocol.parse_llm_output(orjson.dumps(item).decode())
        if not plan.success:
            errors.append(f"计划 {index + 1}: {plan.message or '计划无效'}")
            continue
        entry, error = _accept_plan(llm_service, plan)
        if entry:
            plans.append(entry)
        else:
            errors.append(f"计划 {index + 1}: {error or '计划校验失败'}")
    if errors:
        return BatchParseResult(errors=errors)
    return (
        _result(plans, question)
        if plans
        else BatchParseResult(errors=["Failed to generate any valid query plans"])
    )
