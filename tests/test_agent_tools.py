"""Unit tests for Unified Agent deterministic tools."""

from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from apps.chat.tools.clarification import request_clarification
from apps.chat.tools.patch_sql import patch_and_compile_sql
from apps.chat.tools.registry import (
    ExecuteSqlInput,
    LookupValuesInput,
    PatchSqlInput,
    build_agent_tools,
)


def test_patch_sql_add_dimension():
    base = "SELECT sum(amount) AS total FROM sales WHERE dt = '2026-09-01'"
    res = patch_and_compile_sql(base, "add_dimension", {"fields": ["dept", "region"]})
    assert res["ok"] is True
    sql = res["data"]["sql"]
    assert "dept" in sql.lower()
    assert "region" in sql.lower()
    assert "group by" in sql.lower()


def test_patch_sql_add_filter():
    base = "SELECT dept, sum(amount) AS total FROM sales GROUP BY dept"
    res = patch_and_compile_sql(
        base, "add_filter", {"condition": "status != 'CANCELLED'"}
    )
    assert res["ok"] is True
    sql = res["data"]["sql"].lower()
    assert "status" in sql
    assert "cancelled" in sql
    assert "group by dept" in sql


def test_patch_sql_replace_filter():
    base = "SELECT * FROM orders WHERE status = 'PENDING' AND region = 'EAST'"
    res = patch_and_compile_sql(
        base,
        "replace_filter",
        {"old_field": "status", "new_condition": "status IN ('PAID', 'SHIPPED')"},
    )
    assert res["ok"] is True
    sql = res["data"]["sql"].lower()
    assert "status in ('paid', 'shipped')" in sql


def test_patch_sql_input_rejects_bad_payload():
    with pytest.raises(ValidationError):
        PatchSqlInput.model_validate(
            {
                "base_sql": "SELECT 1",
                "action": "add_filter",
                "payload": {"fields": ["x"]},
            }
        )
    with pytest.raises(ValidationError):
        PatchSqlInput.model_validate(
            {
                "base_sql": "SELECT 1",
                "action": "nope",
                "payload": {},
            }
        )
    ok = PatchSqlInput.model_validate(
        {
            "base_sql": "SELECT 1",
            "action": "add_filter",
            "payload": {"condition": "a = 1"},
        }
    )
    assert ok.action == "add_filter"


def test_execute_sql_chart_type_enum():
    ExecuteSqlInput.model_validate(
        {"sql": "SELECT 1", "required": True, "chart_type": "table"}
    )
    with pytest.raises(ValidationError):
        ExecuteSqlInput.model_validate(
            {"sql": "SELECT 1", "required": True, "chart_type": "scatter"}
        )


def test_lookup_values_schema_has_no_hint_table():
    assert "hint_table" not in LookupValuesInput.model_fields
    LookupValuesInput.model_validate({"phrases": ["刘宁"], "scope": []})
    with pytest.raises(ValidationError):
        LookupValuesInput.model_validate({"phrases": [], "scope": ["only_table"]})


def test_tool_descriptions_state_side_effects():
    tools = {
        t.name: t for t in build_agent_tools(SimpleNamespace(ds=None, datasource=None))
    }
    assert "waits for the user" in (tools["request_clarification"].description or "")
    assert "replaces" in (tools["execute_sql_sandbox"].description or "").lower()
    assert "Terminal exit" in (tools["complete_without_sql"].description or "")
    assert "hint_table" not in str(LookupValuesInput.model_json_schema())


def test_request_clarification_tool():
    questions = [
        {
            "question": "按哪个日期统计销售额？",
            "why": "订单包含创建日期和付款日期，结果不同",
            "options": [
                {"label": "付款日期", "meaning": "按实付生效时间统计"},
                {"label": "创建日期", "meaning": "按用户下单时间统计"},
            ],
        }
    ]
    res = request_clarification(questions)
    assert res["ok"] is True
    assert res["data"]["interrupt_required"] is True
    card = res["data"]["clarification_card"]
    assert len(card["questions"]) == 1
    assert len(card["questions"][0]["options"]) == 2
