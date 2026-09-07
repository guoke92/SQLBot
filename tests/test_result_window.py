"""Tests for result display-window / LIMIT resolution."""

from __future__ import annotations

from apps.chat.plan_policy import ROW_LIMIT, ROW_LIMIT_MAX
from apps.chat.result_window import (
    annotate_result_window,
    apply_result_window,
    extract_sql_limit,
    resolve_exec_row_limit,
)


def test_extract_sql_limit() -> None:
    assert extract_sql_limit("SELECT 1") is None
    assert extract_sql_limit("SELECT * FROM t LIMIT 1000") == 1000
    assert extract_sql_limit("SELECT * FROM t WHERE a=1 LIMIT 2000") == 2000


def test_resolve_prefers_sql_limit_over_default_tool_limit() -> None:
    assert (
        resolve_exec_row_limit(
            "SELECT * FROM t LIMIT 2000",
            tool_limit=ROW_LIMIT,
        )
        == 2000
    )
    assert (
        resolve_exec_row_limit(
            "SELECT * FROM t",
            tool_limit=ROW_LIMIT,
        )
        == ROW_LIMIT
    )
    assert (
        resolve_exec_row_limit(
            "SELECT * FROM t LIMIT 99999",
            tool_limit=ROW_LIMIT,
        )
        == ROW_LIMIT_MAX
    )


def test_apply_result_window_soft_hit() -> None:
    truncated, limit = apply_result_window(
        row_count=1000,
        window_limit=1000,
        truncated=False,
    )
    assert truncated is True
    assert limit == 1000

    truncated, limit = apply_result_window(
        row_count=50,
        window_limit=1000,
        truncated=False,
    )
    assert truncated is False
    assert limit == 1000


def test_annotate_result_window_marks_hit_limit() -> None:
    result = {
        "data": [{"id": i} for i in range(1000)],
        "truncated": False,
    }
    out = annotate_result_window(
        result,
        sql="SELECT * FROM t LIMIT 1000",
        tool_limit=1000,
    )
    assert out["truncated"] is True
    assert out["limit"] == 1000
    assert out["truncation_reason"] == "query_limit"


def test_annotate_result_window_under_limit_clears_tip_meta() -> None:
    result = {
        "data": [{"id": i} for i in range(50)],
        "truncated": False,
        "limit": 50,
    }
    out = annotate_result_window(
        result,
        sql="SELECT * FROM t LIMIT 2000",
        tool_limit=1000,
    )
    assert out["truncated"] is False
    assert "limit" not in out
    assert "truncation_reason" not in out
    assert out["row_count"] == 50
