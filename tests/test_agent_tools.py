"""Unit tests for Unified Agent deterministic tools."""

import pytest
from apps.chat.tools.patch_sql import patch_and_compile_sql
from apps.chat.tools.clarification import request_clarification


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
    res = patch_and_compile_sql(base, "add_filter", {"condition": "status != 'CANCELLED'"})
    assert res["ok"] is True
    sql = res["data"]["sql"].lower()
    assert "status" in sql
    assert "cancelled" in sql
    assert "group by dept" in sql


def test_patch_sql_replace_filter():
    base = "SELECT * FROM orders WHERE status = 'PENDING' AND region = 'EAST'"
    res = patch_and_compile_sql(base, "replace_filter", {
        "old_field": "status",
        "new_condition": "status IN ('PAID', 'SHIPPED')"
    })
    assert res["ok"] is True
    sql = res["data"]["sql"].lower()
    assert "status in ('paid', 'shipped')" in sql


def test_request_clarification_tool():
    questions = [{
        "question": "按哪个日期统计销售额？",
        "why": "订单包含创建日期和付款日期，结果不同",
        "options": [
            {"label": "付款日期", "meaning": "按实付生效时间统计"},
            {"label": "创建日期", "meaning": "按用户下单时间统计"}
        ]
    }]
    res = request_clarification(questions)
    assert res["ok"] is True
    assert res["data"]["interrupt_required"] is True
    card = res["data"]["clarification_card"]
    assert len(card["questions"]) == 1
    assert len(card["questions"][0]["options"]) == 2
