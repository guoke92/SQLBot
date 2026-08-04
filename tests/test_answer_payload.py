"""Canonical NLQ answer payload contract tests."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.answer_payload import (  # noqa: E402
    build_answer_payload,
    get_answer_step_data,
    normalize_answer_payload,
)
from apps.chat.result_data import format_json_data  # noqa: E402
from apps.conversation.outcome import RunOutcome  # noqa: E402


def _outcome() -> RunOutcome:
    return {
        "status": "success",
        "failures": [],
        "successful_steps": 1,
        "total_steps": 1,
        "quality": {
            "score": 92,
            "grade": "excellent",
            "dimensions": [],
            "observations": [],
            "passed_checks": ["contract"],
            "coverage": {
                "returned_rows": 1,
                "truncated": False,
                "step_count": 1,
            },
        },
    }


def test_normalization_preserves_the_complete_terminal_envelope() -> None:
    payload = build_answer_payload(
        [
            {
                "sql": "SELECT amount FROM t",
                "brief": "amount",
                "presentation": {
                    "title": "金额合计",
                    "columns": [
                        {
                            "field": "amount",
                            "label": "金额",
                            "display": "金额(amount)",
                        }
                    ],
                },
                "result": {
                    "fields": ["amount"],
                    "data": [{"amount": 1}],
                    "row_count": 1,
                },
                "chart": {"type": "table"},
            }
        ],
        "done",
        _outcome(),
    )

    normalized = normalize_answer_payload(
        payload,
        normalize_data=lambda data: {**data, "normalized": True},
    )

    assert normalized["analysis"] == "done"
    assert normalized["outcome"] == payload["outcome"]
    assert normalized["steps"][0]["presentation"]["title"] == "金额合计"
    assert normalized["steps"][0]["data"]["normalized"] is True
    assert "normalized" not in payload["steps"][0]["data"]


def test_normalization_rejects_noncanonical_payloads() -> None:
    try:
        normalize_answer_payload(
            {"steps": [], "analysis": ""},
            normalize_data=lambda data: data,
        )
    except ValueError as exc:
        assert "Invalid NLQ answer payload" in str(exc)
    else:
        raise AssertionError("noncanonical payload should be rejected")


def test_chart_data_adapter_preserves_canonical_step_metadata() -> None:
    payload = build_answer_payload(
        [
            {
                "sql": "SELECT amount FROM t",
                "brief": "amount",
                "result": {
                    "fields": ["amount"],
                    "data": [{"amount": 1}],
                    "row_count": 1,
                    "datasource": 8,
                    "truncated": False,
                },
                "chart": {"type": "table"},
            }
        ],
        "done",
        _outcome(),
    )

    step_data = get_answer_step_data(payload)
    formatted = format_json_data(step_data)

    assert formatted["datasource"] == 8
    assert formatted["row_count"] == 1
    assert formatted["data"] == [{"amount": 1}]
