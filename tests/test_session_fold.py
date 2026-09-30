"""Session continuation, deterministic turn folding, soft budget, stage copy."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import orjson
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import StructuredTool

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.agent_knowledge import AgentKnowledgePlane  # noqa: E402
from apps.chat.agent.loop import route_after_tools_execution  # noqa: E402
from apps.chat.agent.context_spec import build_continued_messages  # noqa: E402
from apps.chat.task.agent_prompt import build_agent_system_prompt  # noqa: E402
from apps.chat.tools.contract import success_outcome  # noqa: E402
from apps.chat.turn_fold import estimate_tokens, fold_history, split_turns  # noqa: E402
from apps.chat.agent.tools.runtime import execute_tools_node  # noqa: E402
from apps.conversation.messages import deserialize_messages  # noqa: E402
from apps.conversation.tooling import tool_result_from_message  # noqa: E402


def _tool(name: str, data: dict, call_id: str) -> ToolMessage:
    payload = {
        "ok": True,
        "summary": "ok",
        "data": data,
        "error": None,
        "failure": None,
    }
    return ToolMessage(
        content=orjson.dumps(payload).decode(),
        name=name,
        tool_call_id=call_id,
    )


def _schema_turn(
    question: str,
    *,
    table: str,
    sql: str,
    schema_pad: str = "",
    page_key: str = "concepts/foo",
) -> list:
    schema_text = (
        f"## 表 ({table})\n"
        f"id:bigint, 主键\n"
        f"name:varchar, 名称, labels=A:甲|B:乙\n"
        f"{schema_pad}"
    )
    return [
        HumanMessage(content=question),
        AIMessage(
            content="",
            tool_calls=[
                {
                    "id": f"{table}-schema",
                    "name": "get_table_schema",
                    "args": {"tables": [table]},
                }
            ],
        ),
        _tool(
            "get_table_schema",
            {"tables": [table], "schema_text": schema_text},
            f"{table}-schema",
        ),
        AIMessage(
            content="",
            tool_calls=[
                {
                    "id": f"{table}-wiki",
                    "name": "search_knowledge",
                    "args": {"query": question},
                }
            ],
        ),
        _tool(
            "search_knowledge",
            {"page_keys": [page_key], "hit_count": 1},
            f"{table}-wiki",
        ),
        AIMessage(
            content="",
            tool_calls=[
                {
                    "id": f"{table}-sql",
                    "name": "execute_sql_sandbox",
                    "args": {"sql": sql},
                }
            ],
        ),
        _tool(
            "execute_sql_sandbox",
            {"sql": sql, "required": True, "row_count": 1},
            f"{table}-sql",
        ),
        AIMessage(content="done"),
    ]


def test_continue_keeps_prior_schema_tool_message() -> None:
    history = _schema_turn(
        "查项目",
        table="tenant_project",
        sql="SELECT id, name FROM tenant_project LIMIT 10",
    )
    plane = AgentKnowledgePlane(
        schema_outline="<schema_outline>\n- tenant_project: 项目\n</schema_outline>"
    )
    messages, start, _folds = build_continued_messages(
        history=history,
        question="再加上城市",
        knowledge_plane=plane,
        token_budget=100_000,
        keep_turns=3,
    )
    assert isinstance(messages[0], SystemMessage)
    assert "<schema_outline>" in str(messages[0].content)
    assert "<change_baseline>" not in str(messages[0].content)
    assert "<memory_slots>" not in str(messages[0].content)
    names = [getattr(item, "name", "") for item in messages]
    assert "get_table_schema" in names
    assert str(messages[start].content) == "再加上城市"


def test_fold_oldest_turn_level_one_keeps_sql_from() -> None:
    history: list = []
    for index in range(4):
        pad = ("字段注释填充 " * 80) if index == 0 else ""
        history.extend(
            _schema_turn(
                f"问题{index}",
                table=f"table_{index}",
                sql=f"SELECT id, name FROM table_{index} WHERE id > 0",
                schema_pad=pad,
                page_key=f"concepts/p{index}",
            )
        )
    turns = split_turns(history)
    last3: list = []
    for turn in turns[-3:]:
        last3.extend(turn)
    budget = estimate_tokens(last3) + 80
    assert estimate_tokens(history) > budget
    folded, meta = fold_history(history, token_budget=budget, keep_turns=3)
    assert meta
    assert meta[0]["index"] == 0
    assert meta[0]["level"] == 1
    assert isinstance(folded[0], HumanMessage)
    text = str(folded[0].content)
    assert '<turn_fold level="1">' in text
    assert "问题0" in text
    remaining = split_turns(folded[1:])
    assert len(remaining) == 3
    assert any(getattr(item, "tool_calls", None) for turn in remaining for item in turn)


def test_fold_demotes_oldest_to_level_two() -> None:
    huge_labels = "labels=" + "|".join(f"V{i}:标签{i}" for i in range(200))
    history = _schema_turn(
        "第一问",
        table="tenant_project",
        sql="SELECT id, name FROM tenant_project",
        schema_pad=f"name:varchar, 名称, {huge_labels}\n",
        page_key="concepts/" + ("k" * 200),
    )
    last = _schema_turn(
        "第二问",
        table="other_table",
        sql="SELECT id FROM other_table",
    )
    history.extend(last)
    folded, meta = fold_history(history, token_budget=1, keep_turns=1)
    assert meta
    assert meta[0]["level"] == 2
    text = str(folded[0].content)
    assert '<turn_fold level="2">' in text
    assert "第一问" in text
    assert "FROM tenant_project" not in text
    assert any(getattr(item, "tool_calls", None) for item in folded[1:])


def test_knowledge_tools_run_before_budget() -> None:
    plane = AgentKnowledgePlane(knowledge_rounds=0)

    def get_table_schema(tables: list[str] | None = None) -> dict:
        return success_outcome(
            "expanded",
            payload={
                "tables": list(tables or ["tenant_product"]),
                "schema_text": "id:int",
            },
            name="get_table_schema",
        )

    tool = StructuredTool.from_function(
        func=get_table_schema,
        name="get_table_schema",
        description="schema",
    )
    result = execute_tools_node(
        {
            "messages": [
                AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "id": "call-1",
                            "name": "get_table_schema",
                            "args": {"tables": ["tenant_product"]},
                        }
                    ],
                )
            ],
            "bound_tools": [tool],
            "sink": "json",
            "knowledge_plane": plane.to_dump(),
        }
    )
    assert result["tool_stop_reason"] in {"", None}
    assert result["consecutive_tool_failures"] == 0
    tool_message = next(
        item
        for item in deserialize_messages(result["messages"])
        if isinstance(item, ToolMessage)
    )
    payload = tool_result_from_message(tool_message)
    assert payload["ok"] is True
    assert payload.get("signals", {}).get("skipped") is not True
    tables = (payload.get("payload") or payload.get("data") or {}).get("tables") or []
    assert "tenant_product" in tables
    content = str(tool_message.content)
    assert "id:int" in content
    assert "\\n" not in content
    assert not content.lstrip().startswith("{")
    assert route_after_tools_execution(result) == "agent_loop"


def test_knowledge_tools_skip_when_budget_exhausted() -> None:
    plane = AgentKnowledgePlane(knowledge_rounds=8)

    def get_table_schema(tables: list[str] | None = None) -> dict:
        raise AssertionError("knowledge tools must not run after LoopBudget is exhausted")

    tool = StructuredTool.from_function(
        func=get_table_schema,
        name="get_table_schema",
        description="schema",
    )
    result = execute_tools_node(
        {
            "messages": [
                AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "id": "call-1",
                            "name": "get_table_schema",
                            "args": {"tables": ["tenant_product"]},
                        }
                    ],
                )
            ],
            "bound_tools": [tool],
            "sink": "json",
            "knowledge_plane": plane.to_dump(),
        }
    )
    tool_message = next(
        item
        for item in deserialize_messages(result["messages"])
        if isinstance(item, ToolMessage)
    )
    payload = tool_result_from_message(tool_message)
    assert payload["ok"] is True
    assert payload["signals"]["skipped"] is True
    assert (payload.get("payload") or {}).get("reason") == "knowledge_budget"


def test_system_prompt_has_no_slot_or_hard_budget_copy() -> None:
    prompt = build_agent_system_prompt(
        memory_slots={"confirmed_calibers": [{"label": "x"}]},
    )
    assert "<memory_slots>" not in prompt
    assert "<change_baseline>" not in prompt
    assert "硬预算" not in prompt
    assert "不要再调用 get_table_schema" not in prompt
    assert "轮次建议" not in prompt
    assert "按需调用" in prompt
    assert "每轮思考不超过 8 句" in prompt
    assert "同标题再交一次" in prompt
    assert "不同标题则追加" in prompt


def test_stage_copy_shows_working_for_from_send() -> None:
    stages = (_ROOT / "frontend/src/views/chat/answer/AgentStagesView.vue").read_text()
    assert "liveStartedAt" in stages
    assert "blocks.length || isLive" in stages
    assert "Math.max(fromBlocks, fromSend)" not in stages
    assert "working_as" in stages
    assert "thoughtSnippet" in stages
    assert "deliveredDatasetIds" in stages
    assert "processOpen.value = false" in stages
    vue = (_ROOT / "frontend/src/views/chat/answer/MultiStepAnswer.vue").read_text()
    assert "conversationPlaceholderKey" not in vue
    assert "multi-step-loading" not in vue
    assert "timelineItems.length > 0 || _loading || message?.isTyping" in vue
    assert "delivered-dataset-ids" in vue
    assert "qa.run_stage_generate" not in vue
    timeline = (
        _ROOT / "frontend/src/features/conversation/processTimeline.ts"
    ).read_text()
    assert "THOUGHT_SNIPPET_CHARS = 80" in timeline
    assert "truncated?: boolean" in timeline
    for locale in ("en", "zh-CN", "zh-TW", "ko-KR"):
        data = json.loads((_ROOT / "frontend/src/i18n" / f"{locale}.json").read_text())
        working_as = data["chat"]["timeline"]["working_as"]
        assert "{action}" in working_as
        assert "{seconds}" in working_as
