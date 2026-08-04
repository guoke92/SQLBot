"""Deterministic result-quality scoring tests."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.query_contract import compile_query_contract  # noqa: E402
from apps.chat.result_quality import (  # noqa: E402
    CompletionEvidence,
    ExecutionStatus,
    build_step_quality,
)
from apps.chat.result_validation import validate_result_structure  # noqa: E402


def _evidence(
    *,
    execution_status: ExecutionStatus = "success",
    result_structure_valid: bool = True,
) -> CompletionEvidence:
    return {
        "intent_ready": True,
        "plan_validated": True,
        "contract_satisfied": True,
        "execution_status": execution_status,
        "result_structure_valid": result_structure_valid,
    }


def test_split_multi_metric_grain_is_a_structural_gate_not_a_score() -> None:
    rows = []
    for company in range(10):
        rows.append(
            {
                "company": f"C{company}",
                "level": 1,
                "signed": 100,
                "financed": None,
            }
        )
        rows.append(
            {
                "company": f"C{company}",
                "level": None,
                "signed": None,
                "financed": 80,
            }
        )
    assessment = {
        "row_count": len(rows),
        "truncated": False,
        "null_rates": {"company": 0.0, "level": 0.5},
        "metrics": {
            "signed": {"count": 10, "sum": 1000, "max": 100},
            "financed": {"count": 10, "sum": 800, "max": 80},
        },
        "field_roles": {
            "metrics": ["signed", "financed"],
            "dimensions": ["company", "level"],
        },
        "data_rows": rows,
    }
    report = build_step_quality(
        assessment,
        evidence=_evidence(result_structure_valid=False),
    )
    validation = validate_result_structure([assessment])

    assert report["score"] == 65
    assert report["grade"] == "reference_only"
    assert not any(
        observation["code"] == "split_multi_metric_grain"
        for observation in report["observations"]
    )
    assert {item["code"] for item in report["observations"]} == {"dimension_null_high"}
    assert validation["valid"] is False
    assert validation["issues"][0]["code"] == "split_multi_metric_grain"


def test_query_window_is_coverage_not_a_penalty() -> None:
    report = build_step_quality(
        {
            "row_count": 1000,
            "truncated": True,
            "null_rates": {},
            "metrics": {"amount": {"count": 1000, "sum": 10, "max": 10}},
            "field_roles": {"metrics": ["amount"], "dimensions": []},
            "data_rows": [{"amount": 10}],
        },
        evidence=_evidence(),
    )

    assert report["score"] == 95
    assert report["coverage"]["truncated"] is True
    assert {
        "intent_contract_ready",
        "plan_validated",
        "query_contract_satisfied",
        "sql_executed",
        "result_structure_valid",
    } <= set(report["passed_checks"])
    assert report["observations"][0]["code"] == "truncated_result"


def test_empty_result_is_valid_answer_not_a_score_deduction() -> None:
    report = build_step_quality(
        {
            "row_count": 0,
            "truncated": False,
            "null_rates": {},
            "metrics": {},
            "field_roles": {"metrics": [], "dimensions": ["company"]},
            "data_rows": [],
        },
        evidence=_evidence(),
    )

    assert report["score"] == 95
    assert report["grade"] == "excellent"
    assert "empty_result_answerable" in report["passed_checks"]
    assert [item["code"] for item in report["observations"]] == ["empty_result"]
    usability = next(
        item for item in report["dimensions"] if item["code"] == "answer_usability"
    )
    assert usability["score"] == 100
    assert {item["code"]: item["weight"] for item in report["dimensions"]} == {
        "intent_alignment": 25,
        "contract_completeness": 20,
        "sql_semantic_correctness": 25,
        "answer_usability": 15,
        "evidence_confidence": 10,
        "limitation_transparency": 5,
    }
    assert sum(item["weight"] for item in report["dimensions"]) == 100


def test_unexecuted_plan_is_not_reported_as_an_empty_result() -> None:
    report = build_step_quality(
        {
            "row_count": 0,
            "truncated": False,
            "null_rates": {},
            "metrics": {},
            "data_rows": [],
        },
        evidence=_evidence(
            execution_status="not_run",
            result_structure_valid=False,
        ),
    )

    assert "sql_executed" not in report["passed_checks"]
    assert "empty_result_answerable" not in report["passed_checks"]
    assert report["observations"] == []
    usability = next(
        item for item in report["dimensions"] if item["code"] == "answer_usability"
    )
    assert usability["score"] == 0


def test_confirmed_shared_grain_validates_small_result_sets() -> None:
    rows = [
        {"company": "A", "level": 1, "signed": 100, "financed": None},
        {"company": "A", "level": None, "signed": None, "financed": 80},
        {"company": "B", "level": 2, "signed": 60, "financed": None},
        {"company": "B", "level": None, "signed": None, "financed": 40},
    ]
    contract = compile_query_contract(
        [
            {
                "key": "grain.company",
                "kind": "grain",
                "label": "企业",
                "locked": True,
                "bindings": [
                    {"identifier": "company_id", "role": "group", "aggregation": "none"}
                ],
            },
            {
                "key": "metric.signed",
                "kind": "metric",
                "label": "签收额",
                "locked": True,
                "bindings": [
                    {"identifier": "signed", "role": "measure", "aggregation": "sum"}
                ],
            },
            {
                "key": "metric.financed",
                "kind": "metric",
                "label": "融资额",
                "locked": True,
                "bindings": [
                    {"identifier": "financed", "role": "measure", "aggregation": "sum"}
                ],
            },
        ]
    )
    assessment = {
        "row_count": len(rows),
        "field_roles": {
            "metrics": ["signed", "financed"],
            "dimensions": ["company", "level"],
        },
        "data_rows": rows,
    }

    validation = validate_result_structure([assessment], contract=contract)

    assert validation["valid"] is False
    assert validation["issues"][0]["params"]["contract_metric_keys"] == [
        "metric.signed",
        "metric.financed",
    ]
