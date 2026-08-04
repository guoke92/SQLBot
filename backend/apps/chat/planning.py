"""Protocol-neutral generated plan batch parsing and validation.

The graph node owns orchestration and streaming; this module owns the atomic
contract between one model response and the executable plan batch.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import orjson

from apps.chat.query_contract import QueryContract, compile_query_contract
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
    plan_validated: bool = False
    contract_satisfied: bool = False

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
    intent_context: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """Derive stable business titles from the confirmed query contract.

    Model-authored ``brief`` text is execution metadata, not a trustworthy
    presentation source: it can repeat clarification instructions or describe
    a rejected candidate.  Result titles therefore have one deterministic
    owner and remain stable across retries and page hydration.
    """
    decisions = [
        decision
        for decision in (intent_context or {}).get("decisions") or []
        if isinstance(decision, dict)
        and decision.get("locked")
        and str(decision.get("effect") or "include") != "omit"
    ]
    multiple = len(plans) > 1
    for index, plan in enumerate(plans):
        covered_keys = {
            str(key) for key in plan.get("covered_requirement_keys") or [] if key
        }
        labels_by_kind: dict[str, list[str]] = {}
        for decision in decisions:
            key = str(decision.get("key") or "")
            if covered_keys and key not in covered_keys:
                continue
            kind = str(decision.get("kind") or "")
            label = str(decision.get("label") or "").strip()
            roles = {
                str(binding.get("role") or "")
                for binding in decision.get("bindings") or []
                if isinstance(binding, dict)
            }
            if kind in {"dimension", "grain"} and roles and "group" not in roles:
                continue
            if label:
                labels_by_kind.setdefault(kind, []).append(label)
        dimensions = list(
            dict.fromkeys(
                [
                    *labels_by_kind.get("dimension", []),
                    *labels_by_kind.get("grain", []),
                ]
            )
        )
        metrics = list(
            dict.fromkeys(
                [
                    *labels_by_kind.get("metric", []),
                    *labels_by_kind.get("calculation", []),
                ]
            )
        )
        if dimensions and metrics:
            fallback = f"按{'、'.join(dimensions)}统计{'、'.join(metrics)}"
        elif metrics:
            fallback = "、".join(metrics)
        elif dimensions:
            fallback = f"按{'、'.join(dimensions)}查询"
        else:
            fallback = " ".join((question or "").split()).strip() or "查询结果"
        suffix = f"（{index + 1}）" if multiple else ""
        plan["brief"] = fallback[: _BRIEF_MAX_LENGTH - len(suffix)] + suffix
        plan["presentation_title"] = fallback + suffix
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
    entry = _plan_dict_from_query_plan(validated)
    entry["format_statement"] = llm_service.protocol.format_statement_for_display(
        validated
    )
    entry["sql"] = validated.payload.get("sql", validated.statement)
    return entry, None


def _validate_batch_contract(
    plans: list[dict[str, Any]],
    llm_service: Any,
    *,
    time_intent: dict[str, Any] | None = None,
    query_contract: QueryContract | None = None,
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
        analyze_sql_contract_structure,
    )

    type_key = getattr(llm_service.protocol, "type_key", None)
    dialect = get_spec(type_key).sqlglot_dialect if type_key else None
    try:
        contract = query_contract
        if contract is None:
            decisions = [
                decision
                for decision in (intent_context or {}).get("decisions") or []
                if isinstance(decision, dict)
            ]
            contract = compile_query_contract(
                decisions,
                time_intent=time_intent,
            )
    except ValueError as exc:
        return f"Invalid confirmed query contract: {exc}"
    validation = analyze_sql_contract_structure(
        [str(plan.get("sql") or plan.get("format_statement") or "") for plan in plans],
        contract,
        dialect=dialect,
    )
    if validation.error is None:
        for plan, coverage, projections in zip(
            plans,
            validation.per_plan_coverage,
            validation.per_plan_projections,
            strict=True,
        ):
            plan["projection_requirements"] = {
                projection.output_name: list(projection.requirement_keys)
                for projection in projections
            }
            plan["covered_requirement_keys"] = sorted(coverage)
    return validation.error


def parse_query_generation(
    raw_text: str,
    llm_service: Any,
    *,
    max_batch_size: int,
    time_intent: dict[str, Any] | None = None,
    query_contract: QueryContract | None = None,
) -> BatchParseResult:
    """Parse and validate one model response as an atomic plan batch."""
    plans: list[dict[str, Any]] = []
    errors: list[str] = []
    chat_question = getattr(llm_service, "chat_question", None)
    intent_context = getattr(chat_question, "intent_context", None)
    question = str(
        getattr(chat_question, "generation_question", "")
        or getattr(chat_question, "question", "")
        or ""
    )

    json_str = extract_nested_json(raw_text)
    if json_str is None:
        plan = llm_service.protocol.parse_llm_output(raw_text)
        if plan.success:
            entry, error = _accept_plan(llm_service, plan)
            if entry:
                contract_error = _validate_batch_contract(
                    [entry],
                    llm_service,
                    time_intent=time_intent,
                    query_contract=query_contract,
                )
                if contract_error:
                    return BatchParseResult(errors=[contract_error])
                return BatchParseResult(
                    plans=_apply_display_defaults([entry], question, intent_context),
                    plan_validated=True,
                    contract_satisfied=True,
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
        contract_error = _validate_batch_contract(
            plans,
            llm_service,
            time_intent=time_intent,
            query_contract=query_contract,
        )
        if contract_error:
            return BatchParseResult(errors=[contract_error])
        return BatchParseResult(
            plans=_apply_display_defaults(plans, question, intent_context),
            plan_validated=True,
            contract_satisfied=True,
        )
    return BatchParseResult(errors=["Failed to generate any valid query plans"])
