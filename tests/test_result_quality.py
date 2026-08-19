from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.result_quality import (  # noqa: E402
    CompletionEvidence,
    build_overall_quality,
    build_step_quality,
)


def _evidence(status: str = "verified") -> CompletionEvidence:
    return {
        "requirements_covered": True,
        "plan_validated": True,
        "semantic_status": status,  # type: ignore[typeddict-item]
        "execution_status": "success",
        "result_structure_valid": True,
        "evidence_confidence": 0.9,
        "assumption_risk": "low",
    }


def _assessment(*, rows: int = 3) -> dict:
    return {
        "row_count": rows,
        "truncated": False,
        "null_rates": {},
        "metrics": {},
    }


def test_verified_contract_scores_user_requirement_completion() -> None:
    report = build_step_quality(_assessment(), evidence=_evidence())
    assert report["score"] >= 90
    assert report["grade"] == "excellent"
    assert "requirements_covered" in report["passed_checks"]
    assert sum(item["weight"] for item in report["dimensions"]) == 100


def test_partial_and_unsupported_verification_are_not_claimed_as_verified() -> None:
    partial = build_step_quality(_assessment(), evidence=_evidence("partial"))
    unsupported = build_step_quality(_assessment(), evidence=_evidence("unsupported"))
    assert partial["score"] < 90
    assert unsupported["score"] < 90
    assert "semantic_review_verified" not in partial["passed_checks"]
    assert "semantic_review_partial" in partial["passed_checks"]
    assert "semantic_review_verified" not in unsupported["passed_checks"]


def test_empty_result_is_a_valid_answer_and_not_a_score_penalty() -> None:
    empty = build_step_quality(_assessment(rows=0), evidence=_evidence())
    populated = build_step_quality(_assessment(rows=8), evidence=_evidence())
    assert empty["score"] == populated["score"]
    assert any(item["code"] == "empty_result" for item in empty["observations"])
    assert "empty_result_answerable" in empty["passed_checks"]


def test_data_characteristics_are_observations_not_completion_dimensions() -> None:
    assessment = {
        **_assessment(),
        "null_rates": {"level": 0.8},
        "metrics": {"amount": {"count": 0, "sum": 0, "max": 0}},
    }
    report = build_step_quality(assessment, evidence=_evidence())
    assert report["score"] >= 90
    assert {item["code"] for item in report["observations"]} >= {
        "dimension_null_severe",
        "metric_without_values",
    }


def test_execution_failure_is_low_confidence_but_still_has_full_weight_definition() -> (
    None
):
    evidence = _evidence()
    evidence["execution_status"] = "failed"
    evidence["result_structure_valid"] = False
    report = build_step_quality(
        {**_assessment(rows=0), "error": "connection refused"},
        evidence=evidence,
    )
    assert report["grade"] == "unreliable"
    assert sum(item["weight"] for item in report["dimensions"]) == 100


def test_batch_quality_uses_the_weakest_required_step() -> None:
    good = build_step_quality(_assessment(rows=2), evidence=_evidence())
    weak = build_step_quality(_assessment(rows=2), evidence=_evidence("partial"))
    overall = build_overall_quality([good, weak])
    assert overall["score"] == weak["score"]
    assert overall["coverage"]["step_count"] == 2
