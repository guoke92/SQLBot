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
    ("semantic_coverage", 35),
    ("plan_alignment", 25),
    ("field_relation_evidence", 15),
    ("execution_completeness", 15),
    ("result_reasonableness", 10),
)

ExecutionStatus = Literal["not_run", "success", "failed"]


class CompletionEvidence(TypedDict):
    """Facts emitted by graph stages; the scorer must not infer them."""

    requirements_covered: bool
    plan_validated: bool
    semantic_status: Literal["verified", "partial", "unsupported"]
    execution_status: ExecutionStatus
    result_structure_valid: bool
    evidence_confidence: float
    assumption_risk: Literal["low", "medium", "high"]


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
    requirements_covered = evidence["requirements_covered"]
    plan_validated = evidence["plan_validated"]
    semantic_status = evidence["semantic_status"]
    semantic_valid = semantic_status == "verified"
    structure_valid = evidence["result_structure_valid"]

    semantic_score = (
        max(60, round(float(evidence["evidence_confidence"]) * 100))
        if requirements_covered
        else 40
    )
    alignment_score = (
        100
        if plan_validated and semantic_status == "verified"
        else (
            60
            if plan_validated and semantic_status == "partial"
            else (45 if plan_validated and semantic_status == "unsupported" else 0)
        )
    )
    if execution_failed:
        alignment_score = 0
    if execution_failed:
        execution_score = 0
    elif executed and semantic_valid and structure_valid:
        # Deterministic checks prove that the SQL uses the confirmed fields and
        # returns the required shape. They do not yet prove source fact grain
        # or relationship value semantics, so this dimension must not claim
        # perfect semantic verification.
        execution_score = 100
    elif executed and semantic_valid and not structure_valid:
        execution_score = 60
    elif executed and structure_valid:
        execution_score = 85
    elif executed:
        execution_score = 55
    else:
        execution_score = 0
    if execution_failed:
        evidence_score = 0
    elif requirements_covered and semantic_valid and structure_valid:
        # Schema, confirmed contract and result structure are verified. Exact
        # fact-grain and relationship-value evidence is not yet available.
        evidence_score = 75
    elif executed and structure_valid:
        evidence_score = 50
    elif executed:
        evidence_score = 25
    else:
        evidence_score = 0
    risk_score = {"low": 100, "medium": 75, "high": 55}[evidence["assumption_risk"]]
    if not executed:
        risk_score = 0

    details: dict[str, QualityDetail] = {
        "semantic": _detail(
            "requirements_covered" if requirements_covered else "requirements_not_fully_verified"
        ),
        "alignment": _detail(
            "semantic_review_verified"
            if plan_validated and semantic_valid
            else (
                "contract_partially_verified"
                if semantic_status == "partial"
                else "contract_verification_unsupported"
            )
        ),
        "execution": _detail(
            "execution_failed"
            if execution_failed
            else (
                "sql_executed_with_partial_checks"
                if executed and semantic_valid and structure_valid
                else (
                    "sql_executed_with_partial_checks"
                    if executed
                    else "result_not_executed"
                )
            ),
            params={"error": str(assessment.get("error") or "")},
        ),
        "evidence": _detail(
            "schema_semantic_evidence"
            if semantic_valid
            else "limited_verification_evidence"
        ),
        "risk": _detail(
            "empty_result_is_answer"
            if executed and int(assessment.get("row_count") or 0) == 0
            else (
                "assumption_risk_low"
                if evidence["assumption_risk"] == "low"
                else "assumption_risk_present"
            ),
            params={"risk": evidence["assumption_risk"]},
        ),
    }
    scores = (
        ("semantic_coverage", semantic_score, details["semantic"]),
        ("plan_alignment", alignment_score, details["alignment"]),
        ("field_relation_evidence", evidence_score, details["evidence"]),
        ("execution_completeness", execution_score, details["execution"]),
        ("result_reasonableness", risk_score, details["risk"]),
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
    if evidence["requirements_covered"]:
        checks.append("requirements_covered")
    if evidence["plan_validated"]:
        checks.append("plan_validated")
    if evidence["semantic_status"] == "verified":
        checks.append("semantic_review_verified")
    elif evidence["semantic_status"] == "partial":
        checks.append("semantic_review_partial")
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


def cap_quality(
    quality: ResultQuality, *, maximum: int, reason_code: str
) -> ResultQuality:
    """Apply an explicit architecture-level confidence ceiling."""
    score = min(int(quality.get("score") or 0), max(0, min(100, maximum)))
    observations = list(quality.get("observations") or [])
    observations.append(
        cast(
            DataObservation,
            {"code": reason_code, "severity": "warning", "params": {"cap": maximum}},
        )
    )
    return {
        **quality,
        "score": score,
        "grade": _grade(score),
        "observations": observations,
    }
