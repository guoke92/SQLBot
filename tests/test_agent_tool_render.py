"""Chat-tool model observations (Product render, not Host generic)."""

from __future__ import annotations

from apps.chat.agent.tools.render import render_tool_message


def test_schema_uses_real_newlines() -> None:
    schema = (
        "## 租户产品配置 (tenant_product)\n"
        "id:number, 表主键\n"
        "code:string, 编码"
    )
    text = render_tool_message(
        "get_table_schema",
        {
            "ok": True,
            "summary": "已展开表 ['tenant_product']。不要再为同一张表调用本工具。",
            "payload": {
                "tables": ["tenant_product"],
                "added_tables": ["tenant_product"],
                "already": [],
                "missing": [],
                "schema_text": schema,
                "schema_ready": True,
            },
            "signals": {},
            "error": None,
            "failure": None,
        },
    )
    assert "\\n" not in text
    assert "\n" in text
    assert '"ok"' not in text
    assert "schema_text" not in text
    assert "schema_ready" not in text
    assert "## 租户产品配置 (tenant_product)" in text
    assert "id:number, 表主键" in text.splitlines()


def test_knowledge_keeps_summary_only() -> None:
    summary = (
        "已命中 1 条业务知识。\n"
        "concept: 产品类型\n"
        "  page_key: concepts/product-cate"
    )
    text = render_tool_message(
        "search_knowledge",
        {
            "ok": True,
            "summary": summary,
            "payload": {
                "page_keys": ["concepts/product-cate"],
                "hits": [{"title": "产品类型", "type": "concept"}],
                "hit_count": 1,
            },
            "signals": {},
            "error": None,
            "failure": None,
        },
    )
    assert text == summary
    assert "hit_count" not in text


def test_sql_observation_drops_orchestration_fields() -> None:
    text = render_tool_message(
        "execute_sql_sandbox",
        {
            "ok": True,
            "summary": "Query executed successfully, returned 1 rows.",
            "payload": {
                "sql": "SELECT 1 AS a",
                "fields": ["a"],
                "total_rows": 1,
                "row_count": 1,
                "truncated": False,
                "sample_rows": [{"a": 1}],
                "preview_rows": [{"a": 1}],
                "column_stats": {"a": {"sum": 1}},
                "dataset_id": "ds-1",
                "plan_id": "p-1",
            },
            "signals": {"purpose": "delivery"},
            "error": None,
            "failure": None,
        },
    )
    assert "SELECT 1 AS a" in text
    assert "a=1" in text
    assert "column_stats" not in text
    assert "dataset_id" not in text
    assert '"ok"' not in text


def test_failure_is_one_line() -> None:
    text = render_tool_message(
        "get_table_schema",
        {
            "ok": False,
            "summary": "get_table_schema 需要至少一张可见表名",
            "payload": None,
            "signals": {},
            "error": "get_table_schema 需要至少一张可见表名",
            "failure": {
                "kind": "execution",
                "message": "get_table_schema 需要至少一张可见表名",
                "retryable": True,
            },
        },
    )
    assert text == "Failed: get_table_schema 需要至少一张可见表名"
    assert "retryable" not in text


def test_compare_observation_uses_rev_counts_not_sql() -> None:
    text = render_tool_message(
        "compare_results",
        {
            "ok": True,
            "summary": (
                "Comparison complete. r1: 1000 rows (truncated at 1000). "
                "r2: 100 rows. row_diff: -900."
            ),
            "payload": {
                "hypothesis": "LIMIT",
                "base": {
                    "rev": "r1",
                    "row_count": 1000,
                    "truncated": True,
                    "display_limit": 1000,
                    "fields": ["code"],
                },
                "new": {
                    "rev": "r2",
                    "row_count": 100,
                    "truncated": False,
                    "fields": ["code"],
                },
                "row_diff": -900,
            },
            "signals": {"purpose": "probe"},
            "error": None,
            "failure": None,
        },
    )
    assert "r1: 1000 rows" in text
    assert "truncated at 1000" in text
    assert "r2: 100 rows" in text
    assert "SELECT" not in text
    assert "sql" not in text.lower()
