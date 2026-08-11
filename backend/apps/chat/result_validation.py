"""Deterministic structural validation for executed NLQ result batches.

Validation decides whether a candidate may continue to presentation. It is
separate from quality scoring: a low score remains publishable, while a
structurally contradictory result must be repaired or rejected.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any, TypedDict

from apps.chat.query_specification import (
    GroupRequirement,
    OutputRequirement,
    QuerySpecification,
)


class ResultValidationIssue(TypedDict):
    code: str
    step_index: int
    params: dict[str, Any]


class ResultValidationReport(TypedDict):
    valid: bool
    issues: list[ResultValidationIssue]


def _has_value(value: Any) -> bool:
    return value is not None and value != ""


def _split_multi_metric_grain(
    assessment: Mapping[str, Any],
    *,
    step_index: int,
    contract: QuerySpecification | None,
) -> ResultValidationIssue | None:
    """Detect mutually exclusive metric rows caused by a sparse dimension."""
    rows = [
        row for row in assessment.get("data_rows") or [] if isinstance(row, Mapping)
    ]
    roles = assessment.get("field_roles") or {}
    metrics = [str(item) for item in roles.get("metrics") or []]
    dimensions = [str(item) for item in roles.get("dimensions") or []]
    contract_metrics = [
        requirement
        for requirement in (contract.requirements if contract else ())
        if isinstance(requirement, OutputRequirement)
        and requirement.operation != "value"
    ]
    contract_grains = [
        requirement
        for requirement in (contract.requirements if contract else ())
        if isinstance(requirement, GroupRequirement)
    ]
    contract_defines_shared_grain = len(contract_metrics) >= 2 and bool(contract_grains)
    if len(metrics) < 2 or not dimensions:
        return None
    if not contract_defines_shared_grain and len(rows) < 10:
        return None

    sparse_dimensions = [
        field
        for field in dimensions
        if (
            any(not _has_value(row.get(field)) for row in rows)
            if contract_defines_shared_grain
            else sum(not _has_value(row.get(field)) for row in rows) / len(rows) >= 0.25
        )
    ]
    stable_dimensions = [
        field for field in dimensions if field not in sparse_dimensions
    ]
    if not sparse_dimensions or not stable_dimensions:
        return None

    exactly_one_metric = sum(
        sum(_has_value(row.get(metric)) for metric in metrics) == 1 for row in rows
    )
    if (
        exactly_one_metric != len(rows)
        if contract_defines_shared_grain
        else exactly_one_metric / len(rows) < 0.60
    ):
        return None

    grain_counts = Counter(
        tuple(str(row.get(field) or "") for field in stable_dimensions) for row in rows
    )
    duplicate_rows = sum(count for count in grain_counts.values() if count > 1)
    if (
        duplicate_rows == 0
        if contract_defines_shared_grain
        else duplicate_rows / len(rows) < 0.10
    ):
        return None

    return {
        "code": "split_multi_metric_grain",
        "step_index": step_index,
        "params": {
            "sparse_dimensions": sparse_dimensions,
            "stable_dimensions": stable_dimensions,
            "contract_metric_keys": [
                requirement.requirement_id for requirement in contract_metrics
            ],
            "contract_grain_keys": [
                requirement.requirement_id for requirement in contract_grains
            ],
        },
    }


def validate_result_structure(
    assessments: Sequence[Mapping[str, Any]],
    *,
    contract: QuerySpecification | None = None,
) -> ResultValidationReport:
    """Validate the complete candidate batch before charting or publication."""
    issues: list[ResultValidationIssue] = []
    for fallback_index, assessment in enumerate(assessments):
        step_index = int(assessment.get("index", fallback_index))
        split_issue = _split_multi_metric_grain(
            assessment,
            step_index=step_index,
            contract=contract,
        )
        if split_issue:
            issues.append(split_issue)
    return {"valid": not issues, "issues": issues}


def validation_issue_prompt_text(issue: Mapping[str, Any]) -> str:
    messages = {
        "split_multi_metric_grain": (
            "多指标结果被稀疏维度拆成互斥行，需要在共同业务粒度上合并"
        ),
    }
    code = str(issue.get("code") or "")
    return messages.get(code, code or "未知结果结构问题")
