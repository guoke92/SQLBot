"""Protocol-neutral generated plan batch parsing and validation.

The graph node owns orchestration and streaming; this module owns the atomic
contract between one model response and the executable plan batch.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import orjson

from apps.chat.semantic_intent import decision_selected_values
from apps.protocol import QueryPlan
from apps.protocol.base import CAP_SQL_DIALECT
from common.utils.json_utils import extract_nested_json

logger = logging.getLogger(__name__)
_BRIEF_MAX_LENGTH = 20


@dataclass(frozen=True)
class BatchParseResult:
    """Atomic result of parsing and validating one generated plan batch."""

    plans: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return bool(self.plans) and not self.errors

    @property
    def error_message(self) -> str | None:
        return "\n".join(self.errors) if self.errors else None


def _plan_dict_from_query_plan(plan: QueryPlan) -> dict[str, Any]:
    return {
        "sql": plan.payload.get("sql", plan.statement),
        "format_statement": plan.statement,
        "tables": list(plan.resources or []),
        "chart_type": plan.chart_type or "table",
        "brief": plan.brief or "",
        "plan": plan,
    }


def _apply_display_defaults(
    plans: list[dict[str, Any]],
    question: str,
) -> list[dict[str, Any]]:
    """Guarantee stable presentation metadata from the current plan context."""
    fallback = " ".join((question or "").split()).strip()[:_BRIEF_MAX_LENGTH]
    fallback = fallback or "查询结果"
    multiple = len(plans) > 1
    for index, plan in enumerate(plans):
        brief = " ".join(str(plan.get("brief") or "").split()).strip()
        if not brief:
            suffix = f"（{index + 1}）" if multiple else ""
            brief = fallback[: _BRIEF_MAX_LENGTH - len(suffix)] + suffix
        plan["brief"] = brief[:_BRIEF_MAX_LENGTH]
    return plans


def _accept_plan(
    llm_service: Any,
    plan: QueryPlan,
) -> tuple[dict[str, Any] | None, str | None]:
    if not plan.success:
        return None, (plan.message or None)
    validated = llm_service.protocol.validate_plan(
        llm_service.ds,
        plan,
        llm_service.table_name_list,
    )
    if not validated.success:
        message = validated.message or "Plan validation failed"
        logger.warning("Plan validation failed: %s", message)
        return None, message
    intent_context = getattr(
        getattr(llm_service, "chat_question", None),
        "intent_context",
        None,
    )
    supports = getattr(llm_service.protocol, "supports", None)
    if intent_context and callable(supports) and supports(CAP_SQL_DIALECT):
        missing_values = _missing_confirmed_entity_values(
            validated.statement,
            intent_context,
        )
        if missing_values:
            return None, (
                "Generated SQL does not implement confirmed entity value(s): "
                + ", ".join(missing_values)
            )
    entry = _plan_dict_from_query_plan(validated)
    entry["format_statement"] = llm_service.protocol.format_statement_for_display(
        validated
    )
    entry["sql"] = validated.payload.get("sql", validated.statement)
    return entry, None


def _missing_confirmed_entity_values(
    statement: str,
    intent_context: dict[str, Any] | None,
) -> list[str]:
    """Basic deterministic guard for explicit entity decisions."""
    normalized = (statement or "").casefold()
    missing: list[str] = []
    for decision in (intent_context or {}).get("decisions") or []:
        if (
            not decision.get("locked")
            or not str(decision.get("binding_phrase") or "").strip()
        ):
            continue
        values = decision_selected_values(decision.get("value"))
        missing.extend(
            value
            for value in values
            if not any(
                variant in normalized
                for variant in {
                    value.casefold(),
                    value.replace("'", "''").casefold(),
                }
            )
        )
    return list(dict.fromkeys(missing))


def _validate_batch_contract(
    plans: list[dict[str, Any]],
    llm_service: Any,
) -> str | None:
    """Validate contract requirements across the atomic SQL batch."""
    supports = getattr(llm_service.protocol, "supports", None)
    if not callable(supports) or not supports(CAP_SQL_DIALECT):
        return None
    intent_context = getattr(
        getattr(llm_service, "chat_question", None),
        "intent_context",
        None,
    )
    from apps.protocol.registry import get_spec
    from apps.protocol.sql.identifier_validation import (
        validate_sql_contract_structure,
    )

    type_key = getattr(llm_service.protocol, "type_key", None)
    dialect = get_spec(type_key).sqlglot_dialect if type_key else None
    decisions = [
        decision
        for decision in (intent_context or {}).get("decisions") or []
        if isinstance(decision, dict)
    ]
    error = validate_sql_contract_structure(
        [str(plan.get("sql") or plan.get("format_statement") or "") for plan in plans],
        decisions,
        dialect=dialect,
    )
    return error


def parse_query_generation(
    raw_text: str,
    llm_service: Any,
    *,
    max_batch_size: int,
) -> BatchParseResult:
    """Parse and validate one model response as an atomic plan batch."""
    plans: list[dict[str, Any]] = []
    errors: list[str] = []
    question = str(
        getattr(getattr(llm_service, "chat_question", None), "question", "") or ""
    )

    json_str = extract_nested_json(raw_text)
    if json_str is None:
        plan = llm_service.protocol.parse_llm_output(raw_text)
        if plan.success:
            entry, error = _accept_plan(llm_service, plan)
            if entry:
                contract_error = _validate_batch_contract([entry], llm_service)
                if contract_error:
                    return BatchParseResult(errors=[contract_error])
                return BatchParseResult(
                    plans=_apply_display_defaults([entry], question)
                )
            return BatchParseResult(
                errors=[
                    error or plan.message or "SQL answer is not a valid json object"
                ]
            )
        return BatchParseResult(
            errors=[plan.message or "SQL answer is not a valid json object"]
        )

    try:
        data = orjson.loads(json_str)
    except Exception:
        plan = llm_service.protocol.parse_llm_output(raw_text)
        return BatchParseResult(
            errors=[plan.message if not plan.success else "Cannot parse query answer"]
        )

    items = data if isinstance(data, list) else [data]
    if len(items) > max_batch_size:
        return BatchParseResult(
            errors=[
                f"计划数量 {len(items)} 超过单批上限 {max_batch_size}，"
                "请合并口径或减少拆分查询。"
            ]
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
            errors.append(
                f"计划 {index + 1}: " + (error or plan.message or "计划校验失败")
            )

    if errors:
        return BatchParseResult(errors=errors)
    if plans:
        contract_error = _validate_batch_contract(plans, llm_service)
        if contract_error:
            return BatchParseResult(errors=[contract_error])
        return BatchParseResult(plans=_apply_display_defaults(plans, question))
    return BatchParseResult(errors=["Failed to generate any valid query plans"])
