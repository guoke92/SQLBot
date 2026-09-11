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
                {
                    "label": "建档数据来源 cust_source = 'PPLATFORM'",
                    "meaning": "平台录入来源",
                },
                {
                    "label": "录入方式 cust_build_type = 'PC_BUILD'",
                    "meaning": "PC端录入",
                },
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


def test_execute_tools_preserves_clarification_card_and_routes_to_interrupt(
    monkeypatch,
):
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
                                {
                                    "label": "建档时间 create_time",
                                    "meaning": "建档时间",
                                },
                                {
                                    "label": "更新时间 update_time",
                                    "meaning": "更新时间",
                                },
                            ],
                        }
                    ]
                },
            }
        ],
    )

    fake_tool = MagicMock()
    fake_tool.name = "request_clarification"
    fake_tool.invoke.return_value = request_clarification(
        [
            {
                "field": "time_field",
                "question": "时间以哪个字段为准？",
                "options": [
                    {"label": "建档时间 create_time", "meaning": "建档时间"},
                    {"label": "更新时间 update_time", "meaning": "更新时间"},
                ],
            }
        ]
    )

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
    """Wiki 散文与 schema 分栏共存；不再互斥，也不再用 fallback_schema_summary。"""
    from apps.chat.agent_knowledge import AgentKnowledgePlane

    plane = AgentKnowledgePlane()
    plane.merge_recall(
        {
            "knowledge_text": "# 客户信息主表\n判定规则：cust_build_status = 'BUILD_SUCCESS'",
            "schema_text": (
                "## 认证信息 (ca_certification_info)\n"
                "cust_build_status:varchar, 建档状态"
            ),
            "tables": ["ca_certification_info"],
            "page_keys": ["cust-main"],
        }
    )
    prompt_with_wiki = build_agent_system_prompt(knowledge_plane=plane)
    assert "<wiki_knowledge>" in prompt_with_wiki
    assert "cust_build_status = 'BUILD_SUCCESS'" in prompt_with_wiki
    assert "<schema_catalog>" in prompt_with_wiki
    assert "<fallback_schema_summary>" not in prompt_with_wiki
    wiki_body = prompt_with_wiki.split("<wiki_knowledge>", 1)[1].split(
        "</wiki_knowledge>", 1
    )[0]
    assert "# Table:" not in wiki_body
    assert "TABLE ca_certification_info" not in wiki_body
    assert "禁止用 SQL 摸枚举" in prompt_with_wiki
    assert "request_clarification" in prompt_with_wiki
    assert "展示标签" in prompt_with_wiki
    assert "required=false" in prompt_with_wiki
    assert "严禁再次调用" not in prompt_with_wiki
    assert "允许再次调用" in prompt_with_wiki
    assert "search_wiki" in prompt_with_wiki
    assert "禁止编造" in prompt_with_wiki
    assert "table" in prompt_with_wiki
    assert "information_schema" in prompt_with_wiki
    assert "早停" in prompt_with_wiki
    assert "再贴 Markdown 样例表" in prompt_with_wiki
    assert "仅展示前 N 条" in prompt_with_wiki
    assert "cust_*" not in prompt_with_wiki
    assert "INVITE_AGW" not in prompt_with_wiki
    assert "要么澄清要么不得写入" not in prompt_with_wiki
    assert "名实冲突" not in prompt_with_wiki

    schema_only = AgentKnowledgePlane()
    schema_only.merge_recall(
        {
            "knowledge_text": "",
            "schema_text": ("# Table: ca_certification_info\n[\n(id:bigint, 主键)\n]"),
            "tables": ["ca_certification_info"],
        }
    )
    prompt_fallback = build_agent_system_prompt(knowledge_plane=schema_only)
    assert "</wiki_knowledge>" not in prompt_fallback
    assert "<schema_catalog>" in prompt_fallback
    assert "ca_certification_info" in prompt_fallback


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

    res = execute_sql_sandbox(
        fake_service, "SELECT * FROM cust ORDER BY create_time DESC LIMIT 10"
    )
    assert res["ok"] is True
    assert res["data"]["total_rows"] == 1
    assert "id" in res["data"]["fields"]


def test_clarification_drops_invented_platforms():
    catalog = {"d_task": {"id", "name", "created_at"}, "d_story": {"id", "title"}}
    res = request_clarification(
        [
            {
                "question": "数据来自哪个系统？",
                "options": [
                    {"label": "禅道", "description": "禅道"},
                    {"label": "Jira", "description": "Jira"},
                    {"label": "不确定", "description": "不确定"},
                ],
            }
        ],
        catalog=catalog,
    )
    assert res["ok"] is False


def test_clarification_keeps_grounded_field_options():
    catalog = {"d_task": {"created_at", "updated_at", "assignee_id"}}
    res = request_clarification(
        [
            {
                "question": "时间以哪个字段为准？",
                "options": [
                    {
                        "label": "创建时间",
                        "description": "任务创建时间",
                        "table": "d_task",
                        "field": "created_at",
                    },
                    {
                        "label": "更新时间",
                        "description": "任务更新时间",
                        "table": "d_task",
                        "field": "updated_at",
                    },
                ],
            }
        ],
        catalog=catalog,
    )
    assert res["ok"] is True
    card = res["data"]["clarification_card"]
    assert len(card["questions"]) == 1
    assert {opt["field"] for opt in card["questions"][0]["options"]} == {
        "created_at",
        "updated_at",
    }
