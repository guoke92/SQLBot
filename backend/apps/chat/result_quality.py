"""Deterministic user-requirement completion scoring for NLQ results.

The score answers whether the published answer fulfils the confirmed request.
Data characteristics such as an empty result, high null rate, all-zero metrics,
or a bounded display window are observations, not automatic score deductions.
This module is the single scoring authority and never acts as a publication
gate.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Literal, TypedDict, cast

from apps.conversation.outcome import (
    DataObservation,
    QualityDetail,
    QualityDimension,
    QualityGrade,
    ResultQuality,
)

_DIMENSION_WEIGHTS: tuple[tuple[str, int], ...] = (
    ("intent_alignment", 25),
    ("contract_completeness", 20),
    ("sql_semantic_correctness", 25),
    ("answer_usability", 15),
    ("evidence_confidence", 10),
    ("limitation_transparency", 5),
)

ExecutionStatus = Literal["not_run", "success", "failed"]


class CompletionEvidence(TypedDict):
    """Facts emitted by graph stages; the scorer must not infer them."""

    intent_ready: bool
    plan_validated: bool
    contract_satisfied: bool
    execution_status: ExecutionStatus
    result_structure_valid: bool


def _grade(score: int) -> QualityGrade:
    if score >= 90:
        return "excellent"
    if score >= 75:
        return "acceptable"
    if score >= 55:
        return "reference_only"
    return "unreliable"


def _detail(code: str, *, params: Mapping[str, Any] | None = None) -> QualityDetail:
    return {"code": code, "params": dict(params or {})}


def _dimension(
    code: str,
    weight: int,
    score: int,
    *details: QualityDetail,
) -> QualityDimension:
    bounded = max(0, min(100, score))
    return {
        "code": code,
        "weight": weight,
        "score": bounded,
        "weighted_score": round(bounded * weight / 100, 1),
        "assessor": "program",
        "details": list(details),
    }


def _observation(
    code: str,
    severity: str,
    *,
    params: Mapping[str, Any] | None = None,
) -> DataObservation:
    return cast(
        DataObservation,
        {"code": code, "severity": severity, "params": dict(params or {})},
    )


def _observations(
    assessment: Mapping[str, Any], evidence: CompletionEvidence
) -> list[DataObservation]:
    result: list[DataObservation] = []
    row_count = int(assessment.get("row_count") or 0)
    if evidence["execution_status"] == "failed":
        result.append(
            _observation(
                "execution_failed",
                "error",
                params={"error": str(assessment.get("error") or "")},
            )
        )
        return result
    if evidence["execution_status"] == "success" and row_count == 0:
        result.append(_observation("empty_result", "info"))
    if assessment.get("truncated"):
        result.append(
            _observation(
                "truncated_result",
                "info",
                params={"rows": row_count},
            )
        )

    for field, rate_value in (assessment.get("null_rates") or {}).items():
        rate = float(rate_value or 0)
        if rate >= 0.60:
            result.append(
                _observation(
                    "dimension_null_severe",
                    "warning",
                    params={"field": field, "rate": round(rate * 100)},
                )
            )
        elif rate >= 0.35:
            result.append(
                _observation(
                    "dimension_null_high",
                    "warning",
                    params={"field": field, "rate": round(rate * 100)},
                )
            )

    for field, stats in (assessment.get("metrics") or {}).items():
        if not isinstance(stats, Mapping):
            continue
        if int(stats.get("count") or 0) == 0:
            result.append(
                _observation(
                    "metric_without_values",
                    "warning",
                    params={"field": field},
                )
            )
        elif float(stats.get("sum") or 0) == 0 and float(stats.get("max") or 0) == 0:
            result.append(
                _observation(
                    "metric_all_zero",
                    "info",
                    params={"field": field},
                )
            )

    # A code and parameter set describe one observation; report it once.
    return list(
        {
            (
                item["code"],
                tuple(sorted((str(k), str(v)) for k, v in item["params"].items())),
            ): item
            for item in result
        }.values()
    )


def _score_dimensions(
    assessment: Mapping[str, Any], evidence: CompletionEvidence
) -> list[QualityDimension]:
    execution_failed = evidence["execution_status"] == "failed"
    executed = evidence["execution_status"] == "success"
    intent_ready = evidence["intent_ready"]
    plan_validated = evidence["plan_validated"]
    contract_valid = evidence["contract_satisfied"]
    structure_valid = evidence["result_structure_valid"]

    intent_score = 100 if intent_ready else 70
    contract_score = (
        100 if plan_validated and contract_valid else (50 if plan_validated else 0)
    )
    if execution_failed:
        sql_score = 0
    elif executed and contract_valid and structure_valid:
        # Deterministic checks prove that the SQL uses the confirmed fields and
        # returns the required shape. They do not yet prove source fact grain
        # or relationship value semantics, so this dimension must not claim
        # perfect semantic verification.
        sql_score = 90
    elif executed and contract_valid and not structure_valid:
        sql_score = 40
    elif executed and structure_valid:
        sql_score = 65
    elif executed:
        sql_score = 30
    else:
        sql_score = 0
    usability_score = 100 if executed and structure_valid else (30 if executed else 0)
    if execution_failed:
        evidence_score = 0
    elif intent_ready and contract_valid and structure_valid:
        # Schema, confirmed contract and result structure are verified. Exact
        # fact-grain and relationship-value evidence is not yet available.
        evidence_score = 75
    elif executed and structure_valid:
        evidence_score = 50
    elif executed:
        evidence_score = 25
    else:
        evidence_score = 0
    transparency_score = (
        100
        if execution_failed or (executed and structure_valid)
        else (60 if executed else 0)
    )

    details: dict[str, QualityDetail] = {
        "intent": _detail(
            "intent_confirmed" if intent_ready else "intent_not_machine_confirmed"
        ),
        "contract": _detail(
            "contract_verified"
            if plan_validated and contract_valid
            else "contract_partially_verified"
        ),
        "sql": _detail(
            "execution_failed"
            if execution_failed
            else (
                "sql_executed_with_partial_checks"
                if executed and contract_valid and structure_valid
                else (
                    "sql_executed_with_partial_checks"
                    if executed
                    else "result_not_executed"
                )
            ),
            params={"error": str(assessment.get("error") or "")},
        ),
        "usability": _detail(
            "empty_result_is_answer"
            if executed
            and structure_valid
            and int(assessment.get("row_count") or 0) == 0
            else (
                "result_is_answerable"
                if executed and structure_valid
                else "result_unavailable"
            )
        ),
        "evidence": _detail(
            "schema_contract_evidence"
            if evidence_score >= 90
            else "limited_verification_evidence"
        ),
        "transparency": _detail(
            "data_observations_disclosed"
            if executed or execution_failed
            else "result_not_executed"
        ),
    }
    scores = (
        ("intent_alignment", intent_score, details["intent"]),
        ("contract_completeness", contract_score, details["contract"]),
        ("sql_semantic_correctness", sql_score, details["sql"]),
        ("answer_usability", usability_score, details["usability"]),
        ("evidence_confidence", evidence_score, details["evidence"]),
        ("limitation_transparency", transparency_score, details["transparency"]),
    )
    weights = dict(_DIMENSION_WEIGHTS)
    return [
        _dimension(code, weights[code], score, detail) for code, score, detail in scores
    ]


def build_step_quality(
    assessment: Mapping[str, Any],
    *,
    evidence: CompletionEvidence,
) -> ResultQuality:
    """Build one immutable completion report from explicit graph evidence."""
    row_count = int(assessment.get("row_count") or 0)
    checks: list[str] = []
    if evidence["intent_ready"]:
        checks.append("intent_contract_ready")
    if evidence["plan_validated"]:
        checks.append("plan_validated")
    if evidence["contract_satisfied"]:
        checks.append("query_contract_satisfied")
    if evidence["execution_status"] == "success":
        checks.append("sql_executed")
        checks.append(
            "empty_result_answerable" if row_count == 0 else "displayable_data"
        )
    if evidence["result_structure_valid"]:
        checks.append("result_structure_valid")
    dimensions = _score_dimensions(assessment, evidence)
    score = round(sum(item["weighted_score"] for item in dimensions))
    return {
        "score": score,
        "grade": _grade(score),
        "dimensions": dimensions,
        "observations": _observations(assessment, evidence),
        "passed_checks": checks,
        "coverage": {
            "returned_rows": row_count,
            "truncated": bool(assessment.get("truncated")),
            "step_count": 1,
        },
    }


def build_overall_quality(reports: Sequence[Mapping[str, Any]]) -> ResultQuality:
    """Aggregate required steps; the weakest score wins within each dimension."""
    if not reports:
        dimensions = [
            _dimension(code, weight, 0, _detail("no_published_result"))
            for code, weight in _DIMENSION_WEIGHTS
        ]
        return {
            "score": 0,
            "grade": "unreliable",
            "dimensions": dimensions,
            "observations": [],
            "passed_checks": [],
            "coverage": {"returned_rows": 0, "truncated": False, "step_count": 0},
        }

    aggregated_dimensions: list[QualityDimension] = []
    for code, weight in _DIMENSION_WEIGHTS:
        candidates = [
            item
            for report in reports
            for item in report.get("dimensions") or []
            if item.get("code") == code
        ]
        weakest = min(candidates, key=lambda item: int(item.get("score") or 0))
        weakest_score = int(weakest.get("score") or 0)
        details: list[QualityDetail] = []
        for step_index, report in enumerate(reports, start=1):
            for item in report.get("dimensions") or []:
                if (
                    item.get("code") != code
                    or int(item.get("score") or 0) != weakest_score
                ):
                    continue
                for raw in item.get("details") or []:
                    details.append(
                        cast(QualityDetail, {**raw, "step_index": step_index})
                    )
        aggregated_dimensions.append(_dimension(code, weight, weakest_score, *details))

    observations: list[DataObservation] = []
    passed_sets: list[set[str]] = []
    for step_index, report in enumerate(reports, start=1):
        for raw in report.get("observations") or []:
            observations.append(
                cast(DataObservation, {**raw, "step_index": step_index})
            )
        passed_sets.append({str(item) for item in report.get("passed_checks") or []})
    score = round(sum(item["weighted_score"] for item in aggregated_dimensions))
    return {
        "score": score,
        "grade": _grade(score),
        "dimensions": aggregated_dimensions,
        "observations": observations,
        "passed_checks": sorted(set.intersection(*passed_sets)) if passed_sets else [],
        "coverage": {
            "returned_rows": sum(
                int((report.get("coverage") or {}).get("returned_rows") or 0)
                for report in reports
            ),
            "truncated": any(
                bool((report.get("coverage") or {}).get("truncated"))
                for report in reports
            ),
            "step_count": len(reports),
        },
    }
