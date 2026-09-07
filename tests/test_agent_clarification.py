"""End-to-end tests for Unified Agent clarification interrupt and Wiki-led context."""

from unittest.mock import MagicMock, patch
import pytest
from langchain_core.messages import AIMessage, ToolMessage

from apps.chat.graphs.nodes.agent_clarify import await_agent_clarification_node
from apps.chat.graphs.nodes.unified_agent import route_after_tools_execution
from apps.chat.task.agent_prompt import build_agent_system_prompt
from apps.chat.tools.clarification import request_clarification
from apps.conversation.tooling import execute_tools_node, serialize_tool_result


def test_clarification_tool_creates_interrupt_payload():
    """验证 request_clarification 工具输出完整的结构化卡片与 interrupt_required 标识."""
    questions = [
        {
            "field": "platform_entry",
            "question": "“平台录入”具体对应哪个字段口径？",
            "options": [
                {"label": "建档数据来源 cust_source = 'PPLATFORM'", "meaning": "平台录入来源"},
                {"label": "录入方式 cust_build_type = 'PC_BUILD'", "meaning": "PC端录入"},
            ],
        }
    ]
    res = request_clarification(questions)
    assert res["ok"] is True
    data = res["data"]
    assert data["interrupt_required"] is True
    card = data["clarification_card"]
    assert len(card["questions"]) == 1
    assert card["questions"][0]["question"] == "“平台录入”具体对应哪个字段口径？"


def test_execute_tools_preserves_clarification_card_and_routes_to_interrupt(monkeypatch):
    """验证工具执行节点保留完整的 card 载荷，并且路由守卫切入 await_clarification."""
    ai_msg = AIMessage(
        content="",
        tool_calls=[
            {
                "id": "call_clarify_1",
                "name": "request_clarification",
                "args": {
                    "questions": [
                        {
                            "field": "time_field",
                            "question": "时间以哪个字段为准？",
                            "options": [
                                {"label": "建档时间 create_time", "meaning": "建档时间"},
                                {"label": "更新时间 update_time", "meaning": "更新时间"},
                            ],
                        }
                    ]
                },
            }
        ],
    )

    fake_tool = MagicMock()
    fake_tool.name = "request_clarification"
    fake_tool.invoke.return_value = request_clarification([
        {
            "field": "time_field",
            "question": "时间以哪个字段为准？",
            "options": [
                {"label": "建档时间 create_time", "meaning": "建档时间"},
                {"label": "更新时间 update_time", "meaning": "更新时间"},
            ],
        }
    ])

    state = {
        "run_id": "test_run_clarify",
        "record_id": 123,
        "messages": [ai_msg],
        "bound_tools": [fake_tool],
        "sink": "json",
    }

    monkeypatch.setattr(
        "apps.conversation.tooling.open_process_span",
        lambda **_k: None,
    )
    monkeypatch.setattr(
        "apps.conversation.tooling.attach_process_span",
        lambda *_a, **_k: None,
    )

    # 执行 execute_tools_node
    next_state = execute_tools_node(state)
    assert "tool_steps" in next_state
    steps = next_state["tool_steps"]
    assert len(steps) == 1
    assert steps[0]["ok"] is True
    assert steps[0]["result"]["data"]["interrupt_required"] is True
    assert "clarification_card" in steps[0]["result"]["data"]

    # 验证路由走向 await_clarification 而不是继续 agent_loop
    next_node = route_after_tools_execution(next_state)
    assert next_node == "await_clarification"


def test_wiki_primary_prompt_assembly():
    """验证 Wiki 单源机制：Wiki 存在时不混合 Schema 冗余；Wiki 不存在时降级使用 fallback Schema."""
    # 场景 A: Wiki 存在
    prompt_with_wiki = build_agent_system_prompt(
        wiki_knowledge="# 客户信息主表\n判定规则：cust_build_status = 'BUILD_SUCCESS'",
        schema_summary="TABLE ca_certification_info ...",
    )
    assert "<wiki_knowledge>" in prompt_with_wiki
    assert "cust_build_status = 'BUILD_SUCCESS'" in prompt_with_wiki
    assert "<fallback_schema_summary>" not in prompt_with_wiki  # 严禁物理 Schema 冗余混合
    assert "名实冲突" in prompt_with_wiki
    assert "request_clarification" in prompt_with_wiki
    assert "展示标签" in prompt_with_wiki
    assert "required=false" in prompt_with_wiki

    # 场景 B: Wiki 不存在，降级兜底
    prompt_fallback = build_agent_system_prompt(
        wiki_knowledge="",
        schema_summary="TABLE ca_certification_info ...",
    )
    assert "<wiki_knowledge>" not in prompt_fallback
    assert "<fallback_schema_summary>" in prompt_fallback
    assert "TABLE ca_certification_info" in prompt_fallback


def test_execute_sql_normal_query():
    """验证安全沙箱正常接收合法业务 SQL."""
    from apps.chat.tools.execute_sql import execute_sql_sandbox

    fake_service = MagicMock()
    fake_service.protocol.parse_candidate_payload.return_value = MagicMock(
        success=True,
        statement="SELECT * FROM cust ORDER BY create_time DESC LIMIT 10",
        message="",
    )
    fake_service.protocol.validate_plan.return_value = MagicMock(
        success=True,
        message="",
    )
    fake_service.protocol.execute.return_value = MagicMock(
        data=[{"id": 1, "create_time": "2026-09-01"}],
        fields=["id", "create_time"],
    )

    res = execute_sql_sandbox(fake_service, "SELECT * FROM cust ORDER BY create_time DESC LIMIT 10")
    assert res["ok"] is True
    assert res["data"]["total_rows"] == 1
    assert "id" in res["data"]["fields"]
