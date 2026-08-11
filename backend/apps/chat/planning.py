"""Protocol-neutral generated plan batch parsing and validation.

The graph node owns orchestration and streaming; this module owns the atomic
contract between one model response and the executable plan batch.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Literal

import orjson

from apps.chat.query_specification import QuerySpecification
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
    contract_status: Literal["verified", "partial", "unsupported"] = "unsupported"
    #: Advisory only.  Disagreement with the contract never empties ``plans``
    #: and never blocks execution; the quality score reads ``contract_status``.
    contract_message: str | None = None

    @property
    def success(self) -> bool:
        return bool(self.plans) and not self.errors

    @property
    def error_message(self) -> str | None:
        return "\n".join(self.errors) if self.errors else None

    @property
    def requires_contract_repair(self) -> bool:
        """Whether a safe parsed plan has a concrete specification mismatch.

        A ``partial`` status without a message means the SQL AST cannot prove
        a semantic reference. That risk is scored after execution; generating
        the same SQL again cannot resolve it.
        """
        return bool(self.plans and self.contract_message)


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
    plans: list[dict[str, Any]],
    question: str,
    specification: QuerySpecification | None,
) -> list[dict[str, Any]]:
    """Derive stable business titles from the confirmed query contract.

    Model-authored ``brief`` text is execution metadata, not a trustworthy
    presentation source: it can repeat clarification instructions or describe
    a rejected candidate.  Result titles therefore have one deterministic
    owner and remain stable across retries and page hydration.
    """
    requirements = list(specification.requirements) if specification else []
    multiple = len(plans) > 1
    for index, plan in enumerate(plans):
        covered_keys = {
            str(key) for key in plan.get("covered_requirement_keys") or [] if key
        }
        dimensions: list[str] = []
        metrics: list[str] = []
        for requirement in requirements:
            requirement_id = requirement.requirement_id
            if covered_keys and requirement_id not in covered_keys:
                continue
            clause = requirement.clause
            label = requirement.business_label
            if label:
                if clause == "group" or (
                    clause == "output" and getattr(requirement, "aggregation", None) == "value"
                ):
                    dimensions.append(label)
                elif clause == "output":
                    metrics.append(label)
        dimensions = list(dict.fromkeys(dimensions))
        metrics = list(dict.fromkeys(metrics))
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
    specification: QuerySpecification | None = None,
) -> tuple[str | None, Literal["verified", "partial", "unsupported"]]:
    """Validate contract requirements across the atomic SQL batch."""
    supports = getattr(llm_service.protocol, "supports", None)
    if not callable(supports) or not supports(CAP_SQL_DIALECT):
        return None, "unsupported"
    from apps.protocol.registry import get_spec
    from apps.protocol.sql.identifier_validation import (
        analyze_query_specification_alignment,
    )

    type_key = getattr(llm_service.protocol, "type_key", None)
    dialect = get_spec(type_key).sqlglot_dialect if type_key else None
    if specification is None:
        return None, "unsupported"
    validation = analyze_query_specification_alignment(
        [str(plan.get("sql") or plan.get("format_statement") or "") for plan in plans],
        specification,
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
    return validation.error, validation.status


def _contract_checked_result(
    plans: list[dict[str, Any]],
    llm_service: Any,
    *,
    specification: QuerySpecification | None,
    question: str,
) -> BatchParseResult:
    """Attach contract status to an already-parsed batch.

    SQL that parses is always returned.  Contract disagreement only lowers
    ``contract_status`` and records a diagnostic; it does not invent a rewrite
    loop and does not withhold the answer.
    """
    error, status = _validate_batch_contract(
        plans, llm_service, specification=specification
    )
    prepared = _apply_display_defaults(plans, question, specification)
    return BatchParseResult(
        plans=prepared,
        plan_validated=True,
        contract_status=status,
        contract_message=error,
    )


def parse_query_generation(
    raw_text: str,
    llm_service: Any,
    *,
    max_batch_size: int,
    specification: QuerySpecification | None = None,
) -> BatchParseResult:
    """Parse and validate one model response as an atomic plan batch."""
    plans: list[dict[str, Any]] = []
    errors: list[str] = []
    chat_question = getattr(llm_service, "chat_question", None)
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
                return _contract_checked_result(
                    [entry],
                    llm_service,
                    specification=specification,
                    question=question,
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
        return _contract_checked_result(
            plans,
            llm_service,
            specification=specification,
            question=question,
        )
    return BatchParseResult(errors=["Failed to generate any valid query plans"])
