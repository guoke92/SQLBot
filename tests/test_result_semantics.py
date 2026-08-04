"""Result metric/dimension classification tests."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.result_semantics import (  # noqa: E402
    apply_display_window,
    classify_field_roles,
    read_result_window,
)


def test_numeric_identifier_and_time_names_remain_dimensions() -> None:
    roles = classify_field_roles(
        ["month", "system_id", "task_count"],
        [
            {"name": "month", "is_numeric": True},
            {"name": "system_id", "is_numeric": True},
            {"name": "task_count", "is_numeric": True},
        ],
    )
    assert roles["metrics"] == {"task_count"}
    assert roles["dimensions"] == {"month", "system_id"}


def test_table_fallback_excludes_ids_and_time_buckets_from_metrics() -> None:
    roles = classify_field_roles(
        ["department_id", "year", "story_count", "workload"],
        [
            {"name": "department_id", "is_numeric": True},
            {"name": "year", "is_numeric": True},
            {"name": "story_count", "is_numeric": True},
            {"name": "workload", "is_numeric": True},
        ],
    )
    assert roles["metrics"] == {"story_count", "workload"}
    assert roles["dimensions"] == {"department_id", "year"}


def test_confirmed_role_overrides_numeric_name_heuristics() -> None:
    roles = classify_field_roles(
        ["apply_level", "amount"],
        [
            {"name": "apply_level", "is_numeric": True},
            {"name": "amount", "is_numeric": True},
        ],
        {"apply_level": "dimension", "amount": "metric"},
    )

    assert roles["metrics"] == {"amount"}
    assert roles["dimensions"] == {"apply_level"}


def test_display_window_does_not_claim_unknown_total() -> None:
    rows = [{"value": index} for index in range(1200)]

    displayed, window = apply_display_window(rows, row_limit=1000)

    assert len(displayed) == 1000
    assert window == {
        "row_count": 1000,
        "limit": 1000,
        "truncated": True,
        "truncation_reason": "query_limit",
    }


def test_result_window_uses_only_rows_actually_returned() -> None:
    window = read_result_window(
        {
            "limit": 1000,
            "truncated": True,
            "truncation_reason": "query_limit",
        },
        [{"value": 1}],
    )

    assert window["row_count"] == 1
    assert window["limit"] == 1000
    assert window["truncation_reason"] == "query_limit"
