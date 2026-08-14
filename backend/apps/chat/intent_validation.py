"""Single validation boundary between business intent and physical plans."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from apps.chat.plan_facts import PlanFacts, extract_sql_plan_facts
from apps.chat.query_intent import IntentRevision, QueryIntent, intent_item_catalog


def _identifier(value: str) -> str:
    """Compare dialect identifiers without treating aliases as semantics."""
    return value.rsplit(".", 1)[-1].strip().strip('`"[]').casefold()


def _identifiers(values: tuple[str, ...] | list[str]) -> set[str]:
    return {item for value in values if (item := _identifier(str(value)))}


class IntentIssue(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    code: str
    message: str
    severity: Literal["blocking", "degraded"]
    dataset_index: int | None = None


class PlanValidationReport(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    status: Literal["valid", "degraded", "rejected"]
    issues: tuple[IntentIssue, ...] = ()
    facts: PlanFacts | None = None


def validate_query_intent(intent: QueryIntent) -> tuple[IntentIssue, ...]:
    """Validate business completeness without inspecting SQL or schema names."""
    issues: list[IntentIssue] = []
    for index, dataset in enumerate(intent.datasets):
        if dataset.mode == "aggregate" and not dataset.groupings:
            # A scalar aggregate is valid; only flag when wording promises a
            # dimension that the normalized intent lost.
            dimension_words = ("按", "每", "分组", "维度")
            if any(word in dataset.purpose for word in dimension_words):
                issues.append(
                    IntentIssue(
                        code="INTENT_GRAIN_MISSING",
                        message="The requested dimensional result has no grouping",
                        severity="blocking",
                        dataset_index=index,
                    )
                )
        if dataset.time and not dataset.time.basis_concept:
            issues.append(
                IntentIssue(
                    code="INTENT_TIME_BASIS_MISSING",
                    message="Time range has no business date basis",
                    severity="blocking",
                    dataset_index=index,
                )
            )
    return tuple(issues)


def validate_plan_against_intent(
    revision: IntentRevision,
    candidate: dict[str, Any],
    *,
    dialect: str | None = None,
) -> PlanValidationReport:
    """Compare one plan to accepted intent using its plan-scoped grounding.

    Grounding proves which physical expression implements each business item;
    it never mutates the intent.  Missing proof is degraded unless it concerns
    a required output/filter/time clause, in which case execution is rejected.
    """
    dataset_index = int(candidate.get("dataset_index", -1))
    if dataset_index < 0 or dataset_index >= len(revision.intent.datasets):
        return PlanValidationReport(
            status="rejected",
            issues=(
                IntentIssue(
                    code="PLAN_DATASET_UNKNOWN",
                    message="Plan does not identify a valid intent dataset",
                    severity="blocking",
                ),
            ),
        )
    payload = candidate.get("payload") or {}
    sql = str(
        payload.get("sql") or payload.get("statement") or candidate.get("sql") or ""
    ).strip()
    is_sql_plan = bool(payload.get("sql") or payload.get("statement"))
    try:
        facts = (
            extract_sql_plan_facts(sql, dialect=dialect)
            if is_sql_plan
            else PlanFacts(
                resources=tuple(str(item) for item in candidate.get("tables") or []),
                parser_coverage="partial",
            )
        )
    except Exception as exc:  # sqlglot exposes dialect-specific parse errors
        return PlanValidationReport(
            status="rejected",
            issues=(
                IntentIssue(
                    code="PLAN_PARSE_FAILED",
                    message=f"Physical plan could not be parsed: {exc}",
                    severity="blocking",
                    dataset_index=dataset_index,
                ),
            ),
        )

    catalog = intent_item_catalog(revision.intent)
    prefix = f"d{dataset_index}:"
    required_keys = {key for key in catalog if key.startswith(prefix)}
    grounded = {
        str(item.get("intent_item_id") or "")
        for item in candidate.get("grounding_manifest") or []
        if isinstance(item, dict)
    }
    missing = sorted(required_keys - grounded)
    issues: list[IntentIssue] = []
    if missing:
        issues.append(
            IntentIssue(
                code="PLAN_GROUNDING_INCOMPLETE",
                message="Plan does not prove every required business clause",
                severity="blocking",
                dataset_index=dataset_index,
            )
        )
    known_resources = _identifiers(facts.resources)
    known_fields = _identifiers(facts.fields)
    clause_fields = {
        "output": _identifiers(facts.output_fields),
        "filter": _identifiers(facts.predicate_fields),
        "time": _identifiers(facts.predicate_fields),
        "population": _identifiers(facts.predicate_fields),
        "group": _identifiers(facts.group_fields),
        "order": _identifiers(facts.order_fields),
    }
    for binding in candidate.get("grounding_manifest") or []:
        if not isinstance(binding, dict):
            continue
        item_id = str(binding.get("intent_item_id") or "")
        if item_id not in catalog or not item_id.startswith(prefix):
            issues.append(
                IntentIssue(
                    code="PLAN_GROUNDING_ITEM_UNKNOWN",
                    message="Plan grounding references an unknown business item",
                    severity="blocking",
                    dataset_index=dataset_index,
                )
            )
            continue
        claimed_resources = _identifiers(
            [str(item) for item in binding.get("resources") or []]
        )
        claimed_fields = _identifiers(
            [str(item) for item in binding.get("fields") or []]
        )
        if not claimed_resources and not claimed_fields:
            issues.append(
                IntentIssue(
                    code="PLAN_GROUNDING_EMPTY",
                    message="Grounding does not identify a physical resource or field",
                    severity="blocking",
                    dataset_index=dataset_index,
                )
            )
        if known_resources and claimed_resources - known_resources:
            issues.append(
                IntentIssue(
                    code="PLAN_GROUNDING_RESOURCE_MISMATCH",
                    message="Grounding claims resources absent from the physical plan",
                    severity="blocking",
                    dataset_index=dataset_index,
                )
            )
        if known_fields and claimed_fields - known_fields:
            issues.append(
                IntentIssue(
                    code="PLAN_GROUNDING_FIELD_MISMATCH",
                    message="Grounding claims fields absent from the physical plan",
                    severity="blocking",
                    dataset_index=dataset_index,
                )
            )
        parts = item_id.split(":")
        kind = parts[1] if len(parts) > 1 else ""
        item_value = catalog[item_id]
        actual_clause_fields = clause_fields.get(kind, set())
        if (
            is_sql_plan
            and claimed_fields
            and actual_clause_fields
            and not claimed_fields.intersection(actual_clause_fields)
        ):
            issues.append(
                IntentIssue(
                    code="PLAN_GROUNDING_CLAUSE_MISMATCH",
                    message="Grounding fields do not occur in the claimed plan clause",
                    severity=(
                        "blocking"
                        if kind in {"output", "filter", "time", "population"}
                        else "degraded"
                    ),
                    dataset_index=dataset_index,
                )
            )
        if is_sql_plan and kind in {"filter", "time", "group", "order"}:
            clause_present = {
                "filter": bool(facts.predicates),
                "time": bool(facts.predicates),
                "group": bool(facts.groups),
                "order": bool(facts.ordering),
            }[kind]
            if not clause_present:
                issues.append(
                    IntentIssue(
                        code="PLAN_REQUIRED_CLAUSE_MISSING",
                        message=f"Physical plan has no {kind} clause required by intent",
                        severity="blocking",
                        dataset_index=dataset_index,
                    )
                )
        if is_sql_plan and kind == "output":
            expected_aggregation = str(item_value.get("aggregation") or "").casefold()
            aliases = {
                "count_distinct": "count",
                "distinct_concat": "groupconcat",
            }
            expected_function = aliases.get(expected_aggregation, expected_aggregation)
            matching_outputs = [
                expression.casefold()
                for expression in facts.output_expressions
                if not claimed_fields
                or any(field in expression.casefold() for field in claimed_fields)
            ]
            if not matching_outputs:
                matching_outputs = [
                    item.casefold() for item in facts.output_expressions
                ]
            if (
                expected_function
                and expected_function not in {"value", "ratio", "difference"}
                and not any(
                    f"{expected_function}(" in expression.replace(" ", "")
                    for expression in matching_outputs
                )
            ):
                issues.append(
                    IntentIssue(
                        code="PLAN_AGGREGATION_MISMATCH",
                        message="Physical aggregation differs from the accepted intent",
                        severity="blocking",
                        dataset_index=dataset_index,
                    )
                )
        predicate_text = " ".join(facts.predicates).casefold()
        if is_sql_plan and kind == "filter":
            values = item_value.get("values") or []
            if any(str(value).casefold() not in predicate_text for value in values):
                issues.append(
                    IntentIssue(
                        code="PLAN_FILTER_VALUE_MISMATCH",
                        message="Physical predicates omit an accepted filter value",
                        severity="blocking",
                        dataset_index=dataset_index,
                    )
                )
        if is_sql_plan and kind == "time":
            boundaries = [
                str(item_value.get("start") or ""),
                str(item_value.get("end_exclusive") or ""),
            ]
            if any(
                value and value.casefold() not in predicate_text for value in boundaries
            ):
                issues.append(
                    IntentIssue(
                        code="PLAN_TIME_RANGE_MISMATCH",
                        message="Physical predicates omit an accepted time boundary",
                        severity="blocking",
                        dataset_index=dataset_index,
                    )
                )
        if is_sql_plan and kind == "order" and facts.ordering:
            expected_direction = str(item_value.get("direction") or "asc").casefold()
            matching_order = [
                expression
                for expression in facts.ordering
                if not claimed_fields
                or any(field in expression.casefold() for field in claimed_fields)
            ]
            order_text = " ".join(matching_order or facts.ordering).casefold()
            has_desc = " desc" in f" {order_text}"
            if (expected_direction == "desc") != has_desc:
                issues.append(
                    IntentIssue(
                        code="PLAN_ORDER_DIRECTION_MISMATCH",
                        message="Physical ordering direction differs from accepted intent",
                        severity="blocking",
                        dataset_index=dataset_index,
                    )
                )
    dataset = revision.intent.datasets[dataset_index]
    if dataset.user_limit is not None and facts.explicit_limit != dataset.user_limit:
        issues.append(
            IntentIssue(
                code="PLAN_USER_LIMIT_MISMATCH",
                message="Plan limit differs from the user requested limit",
                severity="blocking",
                dataset_index=dataset_index,
            )
        )
    if facts.parser_coverage != "full":
        issues.append(
            IntentIssue(
                code="PLAN_FACTS_PARTIAL",
                message="Some plan semantics cannot be statically verified",
                severity="degraded",
                dataset_index=dataset_index,
            )
        )
    if any(item.severity == "blocking" for item in issues):
        status: Literal["valid", "degraded", "rejected"] = "rejected"
    elif issues:
        status = "degraded"
    else:
        status = "valid"
    return PlanValidationReport(status=status, issues=tuple(issues), facts=facts)
