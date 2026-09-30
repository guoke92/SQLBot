"""Analyze-mode result tools: compact warehouse stats, no row dump."""

from __future__ import annotations

from apps.chat.agent.mode import AnalyzeMode, QueryMode
from apps.chat.agent.workspace import SqlRevision, SqlWorkspace
from apps.chat.tools.analyze_result import (
    aggregate_sql_result,
    build_aggregate_sql,
    build_breakdown_sql,
    build_profile_sql,
    pick_profile_columns,
    profile_sql_result,
    resolve_field,
    wrap_source_sql,
)
from apps.chat.tools.registry import build_agent_tools


def test_wrap_and_profile_sql_are_compact() -> None:
    inner = "SELECT dept, amount FROM sales WHERE dt = '2026-09-01'"
    wrapped = wrap_source_sql(inner)
    assert wrapped.startswith("(")
    assert "_sqlbot_src" in wrapped
    sql = build_profile_sql(inner, ["dept", "amount"], dialect="mysql")
    assert "COUNT(*)" in sql
    assert "`dept`" in sql
    assert "information_schema" not in sql.lower()
    assert "SELECT dept, amount FROM sales" in sql


def test_breakdown_and_aggregate_sql() -> None:
    inner = "SELECT channel, amt FROM orders"
    br = build_breakdown_sql(inner, "channel", dialect="pg", topk=5)
    assert "GROUP BY" in br
    assert "LIMIT 5" in br
    agg = build_aggregate_sql(
        inner,
        ["channel"],
        [{"fn": "count", "alias": "n"}, {"fn": "sum", "column": "amt", "alias": "amt"}],
        dialect="mysql",
        limit=20,
    )
    assert "GROUP BY" in agg
    assert "SUM(" in agg
    assert "LIMIT 20" in agg


def test_resolve_field_rejects_injection() -> None:
    fields = ["dept", "amount"]
    assert resolve_field("dept", fields) == "dept"
    assert resolve_field("DEPT", fields) == "dept"
    assert resolve_field("amount; DROP TABLE x", fields) is None
    assert resolve_field("missing", fields) is None
    assert pick_profile_columns(["dept", "nope"], fields) == ["dept"]


def test_query_mode_excludes_analyze_tools() -> None:
    query = set(QueryMode().tool_names())
    analyze = set(AnalyzeMode().tool_names())
    assert "profile_sql_result" not in query
    assert "aggregate_sql_result" not in query
    assert "profile_sql_result" in analyze
    assert "aggregate_sql_result" in analyze
    names = {
        tool.name
        for tool in build_agent_tools(
            type("S", (), {"ds": None, "datasource": None})(),
            names=QueryMode().tool_names(),
        )
    }
    assert "profile_sql_result" not in names
    assert "execute_sql_sandbox" in names


def test_profile_requires_executed_revision() -> None:
    ws = SqlWorkspace()
    out = profile_sql_result(type("S", (), {"ds": None})(), ws)
    assert out["ok"] is False


def test_aggregate_rejects_unknown_dimension() -> None:
    ws = SqlWorkspace(
        revisions={
            "r1": SqlRevision(
                rev="r1",
                sql="SELECT dept, amount FROM sales",
                fields=["dept", "amount"],
                status="executed",
                row_count=10,
            )
        },
        current="r1",
        seq=1,
    )
    out = aggregate_sql_result(
        type("S", (), {"ds": None})(),
        ws,
        dimensions=["not_a_col"],
        metrics=[{"fn": "count"}],
    )
    assert out["ok"] is False
    assert "not_a_col" in str(out.get("error") or "")
