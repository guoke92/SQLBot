"""End-to-end tests for Unified Agent clarification interrupt and Wiki-led context."""

from unittest.mock import MagicMock

from langchain_core.messages import AIMessage

from apps.chat.graphs.nodes.unified_agent import route_after_tools_execution
from apps.chat.semantic_planning import ClarificationCard
from apps.chat.task.agent_prompt import (
    _SYSTEM_PROMPT_TEMPLATE,
    build_agent_system_prompt,
)
from apps.chat.tools.clarification import request_clarification
from apps.chat.tools.registry import (
    ClarificationOptionSchema,
    RequestClarificationInput,
    build_agent_tools,
)
from apps.conversation.tooling import execute_tools_node


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
    assert "<wiki_knowledge>" not in prompt_with_wiki
    assert "<schema_catalog>" not in prompt_with_wiki
    assert "<fallback_schema_summary>" not in prompt_with_wiki
    assert "禁止用 SQL 摸枚举" in prompt_with_wiki
    assert "request_clarification" in prompt_with_wiki
    assert "展示标签" in prompt_with_wiki
    assert "required=false" in prompt_with_wiki
    assert "严禁再次调用" not in prompt_with_wiki
    assert "get_table_schema" in prompt_with_wiki
    assert "search_knowledge" in prompt_with_wiki
    assert "禁止编造" in prompt_with_wiki
    assert "table" in prompt_with_wiki
    assert "information_schema" in prompt_with_wiki
    assert "早停" not in prompt_with_wiki
    assert "再贴 Markdown 样例表" in prompt_with_wiki
    assert "仅展示前 N 条" in prompt_with_wiki
    assert "cust_*" not in prompt_with_wiki
    assert "INVITE_AGW" not in prompt_with_wiki
    assert "要么澄清要么不得写入" not in prompt_with_wiki

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
    assert "<schema_catalog>" not in prompt_fallback


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


def test_clarification_option_schema_exposes_fields():
    properties = ClarificationOptionSchema.model_json_schema()["properties"]
    assert "fields" in properties
    assert "table" in properties
    assert "field" in properties

    parsed = RequestClarificationInput.model_validate(
        {
            "questions": [
                {
                    "question": "渠道和项目码分别对应哪些字段？",
                    "options": [
                        {
                            "label": "渠道用渠道码，项目码用项目编码",
                            "description": "两列各自独立",
                            "fields": [
                                {"table": "cust_company_info", "field": "channel_code"},
                                {"table": "cust_company_info", "name": "project_code"},
                            ],
                        },
                        {
                            "label": "两列都用渠道码",
                            "description": "项目码按 Wiki 别名落到渠道码",
                            "table": "cust_company_info",
                            "field": "channel_code",
                        },
                    ],
                }
            ]
        }
    )
    first_fields = parsed.questions[0].options[0].fields
    assert [item.name for item in first_fields] == ["channel_code", "project_code"]
    assert parsed.questions[0].options[1].field == "channel_code"
    assert parsed.questions[0].options[1].fields == []


def test_multi_field_option_is_grounded_and_round_trips():
    catalog = {
        "cust_company_info": {"channel_code", "project_code", "company_name"},
    }
    res = request_clarification(
        [
            {
                "question": "清单里的渠道和项目码分别取哪套字段？",
                "options": [
                    {
                        "label": "渠道取渠道码，项目码取项目编码",
                        "description": "两列含义不同，各自落独立字段",
                        "fields": [
                            {"table": "cust_company_info", "name": "channel_code"},
                            {"table": "cust_company_info", "name": "project_code"},
                        ],
                    },
                    {
                        "label": "渠道和项目码都取渠道码",
                        "description": "项目码按别名与渠道码同字段",
                        "fields": [
                            {"table": "cust_company_info", "field": "channel_code"},
                        ],
                    },
                ],
            }
        ],
        catalog=catalog,
    )
    assert res["ok"] is True
    payload = res["data"]["clarification_card"]
    option = payload["questions"][0]["options"][0]
    names = {ref["name"] for ref in option["fields"]}
    assert names == {"channel_code", "project_code"}
    round_tripped = ClarificationCard.model_validate(payload)
    restored = round_tripped.questions[0].options[0]
    assert {ref.name for ref in restored.fields} == {"channel_code", "project_code"}


def test_chat_117_output_field_conflict_clarifies_not_probes():
    """Sanitized replay of chat 117: 渠道 vs 项目码 share a Wiki alias.

    After at most one targeted wiki search the agent must merge the conflict
    into request_clarification with two complete mappings. Probe SQL cannot
    decide the business names, and 项目码 must not be silently folded onto
    channel_code.
    """
    assert (
        "一次针对性 `search_knowledge` 或字段核对后输出字段仍冲突，立即合并澄清"
        in _SYSTEM_PROMPT_TEMPLATE
    )
    assert "禁止用 probe 代替" in _SYSTEM_PROMPT_TEMPLATE

    tools = build_agent_tools(MagicMock(), access_scope=None)
    clarify = next(item for item in tools if item.name == "request_clarification")
    assert "output-column" in clarify.description
    assert "alters query results" not in clarify.description

    catalog = {
        "cust_company_info": {"channel_code", "project_code", "company_name"},
    }
    args = RequestClarificationInput.model_validate(
        {
            "questions": [
                {
                    "question": "「渠道」和「项目码」分别对应哪套字段？",
                    "options": [
                        {
                            "label": "渠道=渠道码，项目码=项目编码",
                            "description": "两列返回不同值",
                            "fields": [
                                {"table": "cust_company_info", "name": "channel_code"},
                                {"table": "cust_company_info", "name": "project_code"},
                            ],
                        },
                        {
                            "label": "项目码按渠道码理解",
                            "description": "两列都返回渠道码，不再单独出项目编码",
                            "fields": [
                                {"table": "cust_company_info", "name": "channel_code"},
                            ],
                        },
                    ],
                }
            ]
        }
    )
    res = request_clarification(
        [q.model_dump() for q in args.questions],
        catalog=catalog,
    )
    assert res["ok"] is True
    option_fields = [
        [ref["name"] for ref in opt["fields"]]
        for opt in res["data"]["clarification_card"]["questions"][0]["options"]
    ]
    assert ["channel_code", "project_code"] in option_fields
    assert ["channel_code"] in option_fields


def test_output_field_contrast_cases_do_not_over_clarify():
    """Wiki=schema aliases, unique bindings, and confirmed calibers stay executable."""
    assert "maps_to 或 field_targets 唯一" in _SYSTEM_PROMPT_TEMPLATE
    assert "Wiki 与 schema 指向不同物理字段" in _SYSTEM_PROMPT_TEMPLATE
    assert "仅当两者都有独立唯一落点时不是冲突、不澄清" in _SYSTEM_PROMPT_TEMPLATE
    assert "已确认口径" in _SYSTEM_PROMPT_TEMPLATE
    assert "不重问" in _SYSTEM_PROMPT_TEMPLATE

    prompt = build_agent_system_prompt(
        memory_slots={
            "confirmed_calibers": [
                {
                    "question": "时间以哪个字段为准？",
                    "label": "创建时间",
                    "meaning": "按任务创建时间统计",
                    "fields": [{"table": "d_task", "name": "created_at"}],
                }
            ]
        }
    )
    assert "已确认口径" in prompt
    assert "<memory_slots>" not in prompt
    assert "created_at" not in prompt
