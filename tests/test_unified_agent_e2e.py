"""End-to-End tests for Unified Tool-Agent Runtime."""

import pytest
from apps.chat.memory_slots import MemorySlots
from apps.chat.task.agent_prompt import build_agent_system_prompt
from apps.chat.tools.compare_results import compare_query_results
from apps.chat.tools.patch_sql import patch_and_compile_sql
from apps.chat.graphs.nodes.unified_agent import route_after_agent_loop, route_after_tools_execution
from langchain_core.messages import AIMessage, ToolCall


def test_memory_slots_retention_and_baseline_extraction():
    """验证场景1：会话槽位的持久化与多轮修改基线提取."""
    slots = MemorySlots(
        confirmed_calibers={"amount": "actual_amount", "date": "pay_time"},
        excluded_filters=[{"field": "status", "op": "NOT IN", "value": ["CANCELLED"]}],
    )
    # Simulate execution update
    slots.update_from_execution(
        executed_sql="SELECT dept, sum(actual_amount) FROM sales WHERE status NOT IN ('CANCELLED') GROUP BY dept",
        fields=["dept", "sum"],
        row_count=100,
        sample_rows=[{"dept": "Sales", "sum": 50000}],
    )
    baseline = slots.extract_change_baseline()
    assert baseline["sql"].startswith("SELECT dept")
    assert baseline["confirmed_calibers"]["amount"] == "actual_amount"
    assert len(baseline["excluded_filters"]) == 1

    prompt = build_agent_system_prompt(
        memory_slots=slots.model_dump(),
        change_baseline=baseline,
    )
    assert "<memory_slots>" in prompt
    assert "<change_baseline>" in prompt
    assert "actual_amount" in prompt


def test_incremental_patch_preserves_confirmed_filters():
    """验证场景3：增量修改在保留已确认口径（如排除项）的同时安全扩展维度."""
    base_sql = "SELECT dept, sum(actual_amount) AS total FROM sales WHERE status NOT IN ('CANCELLED') GROUP BY dept"
    # User asks: "再按月份看"
    res = patch_and_compile_sql(base_sql, "add_dimension", {"fields": ["month"]})
    assert res["ok"] is True
    patched = res["data"]["sql"].lower()
    assert "month" in patched
    assert "cancelled" in patched and ("status not in" in patched or "not status in" in patched)
    assert "group by dept, month" in patched


def test_agent_route_after_agent_loop_with_tool_call():
    """验证场景4：Agent 大脑调度工具或完成输出的分流路由."""
    ai_msg_with_call = AIMessage(
        content="I will patch the query to add department.",
        tool_calls=[{"name": "patch_and_compile_sql", "args": {}, "id": "call_1"}],
    )
    state_calling = {"messages": [ai_msg_with_call]}
    assert route_after_agent_loop(state_calling) == "execute_tools"

    ai_msg_final = AIMessage(content="Here is the final result: 850 orders.")
    state_final = {"messages": [ai_msg_final]}
    assert route_after_agent_loop(state_final) == "finalize_turn"


def test_route_after_tools_clarification_interrupt():
    """验证场景2：质疑/歧义时触发澄清卡片中断路由."""
    tool_steps_normal = [{"name": "patch_and_compile_sql", "result": {"ok": True, "data": {}}}]
    assert route_after_tools_execution({"tool_steps": tool_steps_normal}) == "agent_loop"

    tool_steps_clarify = [{
        "name": "request_clarification",
        "result": {"ok": True, "data": {"interrupt_required": True}},
    }]
    assert route_after_tools_execution({"tool_steps": tool_steps_clarify}) == "await_clarification"

from apps.chat.graphs.nodes.agent_finalize import finalize_agent_turn_node


def test_finalize_agent_turn_publishes_delivery_datasets_only():
    """Probe SQL stays out of the answer; multiple delivery datasets are kept."""
    state = {
        "run_id": "test_run_123",
        "record_id": 999,
        "final_text": "以下为企业清单。",
        "tool_steps": [
            {
                "ok": True,
                "name": "execute_sql_sandbox",
                "result": {
                    "ok": True,
                    "data": {
                        "sql": "SELECT identify_style, COUNT(*) FROM t GROUP BY 1",
                        "fields": ["identify_style", "cnt"],
                        "preview_rows": [{"identify_style": "INVITE", "cnt": 10}],
                        "row_count": 1,
                        "required": False,
                    },
                },
            },
            {
                "ok": True,
                "name": "execute_sql_sandbox",
                "result": {
                    "ok": True,
                    "data": {
                        "sql": "SELECT code FROM t WHERE identify_style = 'INVITE_AGW'",
                        "fields": ["code"],
                        "preview_rows": [{"code": "c1"}],
                        "row_count": 1,
                        "required": True,
                        "result_title": "企业清单",
                    },
                },
            },
            {
                "ok": True,
                "name": "execute_sql_sandbox",
                "result": {
                    "ok": True,
                    "data": {
                        "sql": "SELECT city, COUNT(*) FROM t GROUP BY city",
                        "fields": ["city", "cnt"],
                        "preview_rows": [{"city": "SZ", "cnt": 3}],
                        "row_count": 1,
                        "required": True,
                        "result_title": "城市分布",
                    },
                },
            },
        ],
    }
    out = finalize_agent_turn_node(state)
    ans = out["terminal_answer"]
    assert ans["status"] == "succeeded"
    assert [item["title"] for item in ans["datasets"]] == ["企业清单", "城市分布"]
    assert "COUNT(*) FROM t GROUP BY 1" not in ans["datasets"][0]["sql"]
    assert ans["content"].startswith("以下为企业清单")
