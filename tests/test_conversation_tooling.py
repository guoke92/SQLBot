from __future__ import annotations

import json
import sys
import types
from pathlib import Path

import pytest

_BACKEND = Path(__file__).resolve().parents[1] / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))
if "apps" not in sys.modules:
    apps_package = types.ModuleType("apps")
    apps_package.__path__ = [str(_BACKEND / "apps")]  # type: ignore[attr-defined]
    sys.modules["apps"] = apps_package
if "apps.conversation" not in sys.modules:
    conversation_package = types.ModuleType("apps.conversation")
    conversation_package.__path__ = [  # type: ignore[attr-defined]
        str(_BACKEND / "apps" / "conversation")
    ]
    sys.modules["apps.conversation"] = conversation_package


from langchain_core.messages import AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import StructuredTool

import sqlbot_xpack  # noqa: F401  # initialize extension imports before app modules
import apps.conversation.agent as agent_module
import apps.conversation.tooling as tooling_module
from apps.chat.steps.observability import sanitize_audit_value
from apps.conversation.agent import agent_node, route_after_agent
from apps.conversation.messages import deserialize_messages, serialize_messages
from apps.conversation.tooling import (
    execute_tools_node,
    normalize_tool_result,
    parse_markup_tool_calls,
    render_tool_message,
    resolve_message_tool_calls,
    strip_markup_tool_calls,
    tool_failure,
    tool_result_from_message,
)


@pytest.fixture(autouse=True)
def _stub_tool_spans(monkeypatch):
    class _Span:
        id = 1

        def set_input(self, *_a, **_k):
            return None

        def set_output(self, *_a, **_k):
            return None

        def set_usage(self, *_a, **_k):
            return None

        def set_model_calls(self, *_a, **_k):
            return None

        def delta(self, *_a, **_k):
            return None

        def close(self, *_a, **_k):
            return {}

        def snapshot(self):
            return {}

    def _open_span(**_kwargs):
        return _Span()

    monkeypatch.setattr(tooling_module, "open_process_span", _open_span)
    monkeypatch.setattr(tooling_module, "attach_process_span", lambda *_a, **_k: _Span())
    monkeypatch.setattr(
        tooling_module, "attach_running_tool_span", lambda **_k: None
    )
    monkeypatch.setattr(agent_module, "open_process_span", _open_span)
    # Node unit tests isolate tool/agent behavior from the durable runtime
    # boundary, which is covered separately by run lifecycle tests.
    direct_runtime_value = lambda state, key: state[key]
    monkeypatch.setattr(tooling_module, "runtime_value", direct_runtime_value)
    monkeypatch.setattr(agent_module, "runtime_value", direct_runtime_value)


def test_redact_value_handles_nested_and_json_configuration() -> None:
    value = {
        "configuration": json.dumps(
            {
                "host": "db.local",
                "password": "secret",
                "api_key": "key",
            }
        ),
        "token": "token",
    }
    assert sanitize_audit_value(value) == {
        "configuration": {
            "host": "db.local",
            "password": "<redacted>",
            "api_key": "<redacted>",
        },
        "token": "<redacted>",
    }


def test_redact_value_normalizes_camel_case_secret_keys() -> None:
    value = {
        "configuration": {
            "apiKey": "api",
            "clientSecret": "client",
            "bearerToken": "bearer",
            "basicPassword": "password",
            "apiKeyHeader": "X-API-Key",
        }
    }
    assert sanitize_audit_value(value) == {
        "configuration": {
            "apiKey": "<redacted>",
            "clientSecret": "<redacted>",
            "bearerToken": "<redacted>",
            "basicPassword": "<redacted>",
            "apiKeyHeader": "X-API-Key",
        }
    }


def test_normalize_tool_result_has_one_result_contract() -> None:
    assert normalize_tool_result(
        {
            "ok": True,
            "summary": "done",
            "data": {"id": 1},
            "error": None,
            "failure": None,
        }
    ) == {
        "ok": True,
        "summary": "done",
        "data": {"id": 1},
        "error": None,
        "failure": None,
    }
    with pytest.raises(TypeError):
        normalize_tool_result('{"error":"not found"}')
    with pytest.raises(TypeError):
        normalize_tool_result({"message": "legacy result"})
    with pytest.raises(TypeError):
        normalize_tool_result(
            {
                "ok": True,
                "summary": "done",
                "data": None,
                "error": None,
                "failure": None,
                "message": "legacy",
            }
        )
    with pytest.raises(TypeError):
        normalize_tool_result(
            {
                "ok": True,
                "summary": "done",
                "data": None,
                "error": "inconsistent",
                "failure": None,
            }
        )


def test_tool_failure_preserves_structured_partial_data() -> None:
    result = tool_failure(
        "Updated 1/2 resources",
        "1 resource failed",
        [{"id": 1, "ok": True}, {"id": 2, "ok": False}],
    )
    assert normalize_tool_result(result) == result


def test_execute_tools_appends_one_tool_message_per_call() -> None:
    def echo(value: str) -> dict[str, object]:
        return {
            "ok": True,
            "summary": "echoed",
            "data": {"value": value},
            "error": None,
            "failure": None,
        }

    tool = StructuredTool.from_function(
        func=echo,
        name="echo",
        description="Echo one value",
    )
    ai_message = AIMessage(
        content="",
        tool_calls=[
            {"id": "call-1", "name": "echo", "args": {"value": "a"}},
            {"id": "call-2", "name": "echo", "args": {"value": "b"}},
        ],
    )
    result = execute_tools_node(
        {
            "messages": [ai_message],
            "bound_tools": [tool],
            "sink": "json",
        }
    )
    messages = deserialize_messages(result["messages"])
    tool_messages = [
        message for message in messages if isinstance(message, ToolMessage)
    ]
    assert [message.tool_call_id for message in tool_messages] == ["call-1", "call-2"]
    assert [
        tool_result_from_message(message)["data"]["value"] for message in tool_messages
    ] == [
        "a",
        "b",
    ]
    for message in tool_messages:
        content = str(message.content)
        assert not content.lstrip().startswith("{")
        assert "value: " in content


def test_execute_tools_redacts_results_before_returning_them_to_the_model() -> None:
    def inspect() -> dict[str, object]:
        return {
            "ok": True,
            "summary": "loaded",
            "data": {"host": "db.local", "password": "secret"},
            "error": None,
            "failure": None,
        }

    tool = StructuredTool.from_function(
        func=inspect,
        name="inspect",
        description="Return one configuration",
    )
    result = execute_tools_node(
        {
            "messages": [
                AIMessage(
                    content="",
                    tool_calls=[{"id": "call-1", "name": "inspect", "args": {}}],
                )
            ],
            "bound_tools": [tool],
            "sink": "json",
        }
    )
    tool_message = next(
        message
        for message in deserialize_messages(result["messages"])
        if isinstance(message, ToolMessage)
    )
    assert tool_result_from_message(tool_message)["data"] == {
        "host": "db.local",
        "password": "<redacted>",
    }
    content = str(tool_message.content)
    assert "secret" not in content
    assert "db.local" in content
    assert "<redacted>" in content
    assert not content.lstrip().startswith("{")


def test_route_after_agent_uses_shared_tool_loop() -> None:
    state = {
        "messages": [
            AIMessage(
                content="",
                tool_calls=[{"id": "call-1", "name": "echo", "args": {}}],
            )
        ]
    }
    assert route_after_agent(state) == "execute_tools"


def test_agent_audit_payload_redacts_tool_credentials(monkeypatch) -> None:
    opened: list[dict] = []

    class _Span:
        id = 1

        def set_input(self, *_a, **_k):
            return None

        def set_output(self, value):
            opened.append({"output": value})

        def set_usage(self, *_a, **_k):
            return None

        def set_model_calls(self, *_a, **_k):
            return None

        def delta(self, *_a, **_k):
            return None

        def close(self, *_a, **_k):
            return {}

    def _open(**kwargs):
        opened.append(kwargs)
        return _Span()

    class FakeModel:
        def bind_tools(self, _tools):
            return self

        def invoke(self, _messages):
            return AIMessage(
                content="",
                tool_calls=[
                    {
                        "id": "call-1",
                        "name": "create_datasource",
                        "args": {
                            "configuration": {
                                "host": "db.local",
                                "password": "secret",
                            }
                        },
                    }
                ],
            )

    monkeypatch.setattr(agent_module, "open_process_span", _open)
    result = agent_node(
        {
            "llm": FakeModel(),
            "messages": [],
            "bound_tools": [],
            "sink": "json",
            "tool_round_limit": 2,
        }
    )
    thought_out = next(item for item in opened if "output" in item)["output"]
    calls = thought_out["tool_calls"]
    assert calls[0]["args"]["configuration"] == {
        "host": "db.local",
        "password": "<redacted>",
    }
    tool_open = next(item for item in opened if item.get("kind") == "tool")
    assert tool_open["tool"]["args"]["configuration"] == {
        "host": "db.local",
        "password": "<redacted>",
    }
    assert result["tool_rounds"] == 1


def test_agent_rejects_empty_terminal_response(monkeypatch) -> None:
    class FakeModel:
        def invoke(self, _messages):
            return AIMessage(content="")

    result = agent_node(
        {
            "llm": FakeModel(),
            "messages": [],
            "bound_tools": [],
            "sink": "json",
        }
    )
    assert result["error"] == "Model returned an empty response"
    assert result["outcome"]["status"] == "failed"


def test_agent_requires_tool_grounding_before_config_completion(monkeypatch) -> None:
    class FakeModel:
        def bind_tools(self, _tools):
            return self

        def invoke(self, _messages):
            return AIMessage(content="The relationship was saved.")

    result = agent_node(
        {
            "llm": FakeModel(),
            "messages": [],
            "bound_tools": [object()],
            "sink": "json",
            "tool_free_completion_marker": "[[NO_SYSTEM_ACTION]]",
        }
    )
    assert result["final_text"] == ""
    assert result["tool_grounding_retry"] is True
    assert isinstance(deserialize_messages(result["messages"])[-1], SystemMessage)
    assert route_after_agent(result) == "agent"


def test_agent_accepts_explicit_tool_free_guidance(monkeypatch) -> None:
    class FakeModel:
        def bind_tools(self, _tools):
            return self

        def invoke(self, _messages):
            return AIMessage(
                content="[[NO_SYSTEM_ACTION]] A table relationship joins fields."
            )

    result = agent_node(
        {
            "llm": FakeModel(),
            "messages": [],
            "bound_tools": [object()],
            "sink": "json",
            "tool_free_completion_marker": "[[NO_SYSTEM_ACTION]]",
        }
    )
    assert result["final_text"] == "A table relationship joins fields."
    assert result["tool_grounding_retry"] is False
    assert route_after_agent(result) == "finish"


def test_agent_fails_repeated_ungrounded_config_completion(monkeypatch) -> None:
    class FakeModel:
        def bind_tools(self, _tools):
            return self

        def invoke(self, _messages):
            return AIMessage(content="The relationship was saved.")

    result = agent_node(
        {
            "llm": FakeModel(),
            "messages": [],
            "bound_tools": [object()],
            "sink": "json",
            "tool_free_completion_marker": "[[NO_SYSTEM_ACTION]]",
            "tool_grounding_retry": True,
        }
    )
    assert result["outcome"]["status"] == "failed"
    assert "No system tool was executed" in result["error"]
    assert route_after_agent(result) == "fail"


def test_agent_finalizes_without_tools_at_round_limit(monkeypatch) -> None:
    class FakeModel:
        bind_calls = 0

        def bind_tools(self, _tools):
            self.bind_calls += 1
            return self

        def invoke(self, messages):
            assert isinstance(messages[-1], SystemMessage)
            return AIMessage(content="The operation failed; verify the credentials.")

    model = FakeModel()
    result = agent_node(
        {
            "llm": model,
            "messages": [],
            "bound_tools": [object()],
            "sink": "json",
            "tool_rounds": 2,
            "tool_round_limit": 2,
        }
    )
    assert model.bind_calls == 0
    assert result["final_text"] == "The operation failed; verify the credentials."
    assert "error" not in result


def test_execute_tools_stops_after_repeated_equivalent_failure() -> None:
    def invalid(value: str) -> dict[str, object]:
        return tool_failure("invalid input", f"validation failed for {value}")

    tool = StructuredTool.from_function(
        func=invalid,
        name="invalid",
        description="Always reject input",
    )

    def call_message() -> AIMessage:
        return AIMessage(
            content="",
            tool_calls=[{"id": "call-1", "name": "invalid", "args": {"value": "same"}}],
        )

    first = execute_tools_node(
        {
            "messages": [call_message()],
            "bound_tools": [tool],
            "sink": "json",
        }
    )
    assert first["consecutive_tool_failures"] == 1
    assert first["tool_stop_reason"] == ""

    second = execute_tools_node(
        {
            **first,
            "messages": serialize_messages(
                [*deserialize_messages(first["messages"]), call_message()]
            ),
        }
    )
    assert second["consecutive_tool_failures"] == 2
    assert second["tool_stop_reason"] == "invalid repeated the same failed call"
    assert len(second["tool_steps"]) == 2


def test_execute_tools_stops_after_non_retryable_failure() -> None:
    def disconnected() -> dict[str, object]:
        return tool_failure("connection failed", "Connection refused")

    tool = StructuredTool.from_function(
        func=disconnected,
        name="disconnected",
        description="Always fail connection",
    )
    result = execute_tools_node(
        {
            "messages": [
                AIMessage(
                    content="",
                    tool_calls=[{"id": "call-1", "name": "disconnected", "args": {}}],
                )
            ],
            "bound_tools": [tool],
            "sink": "json",
        }
    )
    assert result["tool_stop_reason"] == (
        "disconnected failed with a non-retryable connection error"
    )


def test_execute_tools_attaches_running_span_by_call_id_when_state_empty(
    monkeypatch,
) -> None:
    """Defense: reuse DB-open tool span even if open_tool_spans was dropped."""
    attached: list[dict] = []
    opened: list[dict] = []

    class _Span:
        id = 3700

        def set_input(self, *_a, **_k):
            return None

        def set_output(self, *_a, **_k):
            return None

        def close(self, *_a, **_k):
            return {}

    def _attach_running(**kwargs):
        attached.append(kwargs)
        return _Span()

    def _open(**kwargs):
        opened.append(kwargs)
        return _Span()

    monkeypatch.setattr(tooling_module, "attach_running_tool_span", _attach_running)
    monkeypatch.setattr(tooling_module, "open_process_span", _open)
    monkeypatch.setattr(tooling_module, "attach_process_span", lambda *_a, **_k: None)

    def echo(value: str) -> dict[str, object]:
        return {
            "ok": True,
            "summary": "echoed",
            "data": {"value": value},
            "error": None,
            "failure": None,
        }

    tool = StructuredTool.from_function(func=echo, name="echo", description="Echo")
    result = execute_tools_node(
        {
            "messages": [
                AIMessage(
                    content="",
                    tool_calls=[
                        {"id": "call-dup", "name": "echo", "args": {"value": "x"}}
                    ],
                )
            ],
            "bound_tools": [tool],
            "sink": "json",
            "record_id": 530,
            "run_id": "run-dup",
        }
    )
    assert attached and attached[0]["call_id"] == "call-dup"
    assert opened == []
    messages = deserialize_messages(result["messages"])
    assert any(
        isinstance(m, ToolMessage) and m.tool_call_id == "call-dup" for m in messages
    )


_CHAT212_DSML = """<｜｜DSML｜｜tool_calls>
<｜｜DSML｜｜invoke name="get_table_schema">
<｜｜DSML｜｜parameter name="tables" string="true">["d_task"]</｜｜DSML｜｜parameter>
</｜｜DSML｜｜invoke>
<｜｜DSML｜｜invoke name="search_knowledge">
<｜｜DSML｜｜parameter name="query" string="true">部门维度表 组织 系统编码</｜｜DSML｜｜parameter>
</｜｜DSML｜｜invoke>
</｜｜DSML｜｜tool_calls>"""


def test_parse_dsml_markup_recovers_search_wiki_calls() -> None:
    calls = parse_markup_tool_calls(_CHAT212_DSML)
    assert [item["name"] for item in calls] == ["get_table_schema", "search_knowledge"]
    assert calls[1]["args"]["query"] == "部门维度表 组织 系统编码"
    assert "DSML" not in strip_markup_tool_calls(_CHAT212_DSML)
    message = AIMessage(content=_CHAT212_DSML)
    recovered, remainder = resolve_message_tool_calls(message, _CHAT212_DSML)
    assert len(recovered) == 2
    assert not remainder
    native = AIMessage(
        content="ok",
        tool_calls=[{"id": "c1", "name": "execute_sql_sandbox", "args": {"sql": "SELECT 1"}}],
    )
    native_calls, native_text = resolve_message_tool_calls(native, "ok")
    assert native_calls[0]["name"] == "execute_sql_sandbox"
    assert native_text == "ok"


def test_render_tool_message_schema_uses_real_newlines() -> None:
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
            "data": {
                "tables": ["tenant_product"],
                "added_tables": ["tenant_product"],
                "already": [],
                "missing": [],
                "schema_text": schema,
                "schema_ready": True,
            },
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


def test_render_tool_message_keeps_knowledge_summary_only() -> None:
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
            "data": {
                "page_keys": ["concepts/product-cate"],
                "hits": [{"title": "产品类型", "type": "concept"}],
                "hit_count": 1,
            },
            "error": None,
            "failure": None,
        },
    )
    assert text == summary
    assert "hit_count" not in text


def test_render_tool_message_sql_drops_orchestration_fields() -> None:
    text = render_tool_message(
        "execute_sql_sandbox",
        {
            "ok": True,
            "summary": "Query executed successfully, returned 1 rows.",
            "data": {
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
                "required": True,
            },
            "error": None,
            "failure": None,
        },
    )
    assert "SELECT 1 AS a" in text
    assert "a=1" in text
    assert "column_stats" not in text
    assert "dataset_id" not in text
    assert '"ok"' not in text


def test_render_tool_message_failure_is_one_line() -> None:
    text = render_tool_message(
        "get_table_schema",
        {
            "ok": False,
            "summary": "get_table_schema 需要至少一张可见表名",
            "data": None,
            "error": "get_table_schema 需要至少一张可见表名",
            "failure": {
                "kind": "execution",
                "message": "get_table_schema 需要至少一张可见表名",
                "retryable": True,
            },
        },
    )
    assert text == "失败：get_table_schema 需要至少一张可见表名"
    assert "retryable" not in text


def test_tool_result_from_message_reads_artifact_and_legacy_json() -> None:
    structured = {
        "ok": True,
        "summary": "ok",
        "data": {"sql": "SELECT 1", "required": True},
        "error": None,
        "failure": None,
    }
    current = ToolMessage(
        content="Query executed successfully, returned 1 rows.\nsql:\nSELECT 1",
        tool_call_id="c1",
        name="execute_sql_sandbox",
        artifact=structured,
    )
    assert tool_result_from_message(current)["data"]["sql"] == "SELECT 1"
    legacy = ToolMessage(
        content=json.dumps(structured),
        tool_call_id="c2",
        name="execute_sql_sandbox",
    )
    assert tool_result_from_message(legacy)["data"]["sql"] == "SELECT 1"


def test_recover_invalid_tool_calls_parses_trailing_junk_json() -> None:
    from apps.conversation.tooling import (
        attach_tool_calls,
        recover_invalid_tool_calls,
        resolve_message_tool_calls,
    )

    # Trailing `]}` mirrors DeepSeek Responses invalid_tool_call args.
    args = (
        '{"questions":[{"question":"q1","question_id":"q1","options":'
        '[{"label":"A","option_id":"a"}]}],"question":"q2","question_id":"q2"}]}'
    )
    message = AIMessage(
        content="clarify",
        tool_calls=[],
        invalid_tool_calls=[
            {
                "id": "call_orphan",
                "name": "request_clarification",
                "args": args,
                "type": "invalid_tool_call",
                "error": "Extra data",
            }
        ],
        additional_kwargs={
            "__openai_function_call_ids__": {"call_orphan": "fc-1"},
        },
    )
    recovered = recover_invalid_tool_calls(message)
    assert len(recovered) == 1
    assert recovered[0]["name"] == "request_clarification"
    calls, _text = resolve_message_tool_calls(message, "clarify")
    assert calls[0]["id"] == "call_orphan"
    attached = attach_tool_calls(message, calls, "clarify")
    assert attached.tool_calls
    assert not attached.invalid_tool_calls


def test_sanitize_messages_for_model_drops_orphan_invalid_tool_calls() -> None:
    from apps.conversation.tooling import sanitize_messages_for_model
    from langchain_openai.chat_models.base import _construct_responses_api_input

    answered = AIMessage(
        content="",
        tool_calls=[
            {"id": "call_ok", "name": "get_table_schema", "args": {"tables": ["t"]}, "type": "tool_call"}
        ],
    )
    orphan = AIMessage(
        content="intend clarify",
        tool_calls=[],
        invalid_tool_calls=[
            {
                "id": "call_orphan",
                "name": "request_clarification",
                "args": '{"questions":[]}',
                "type": "invalid_tool_call",
            }
        ],
        additional_kwargs={
            "__openai_function_call_ids__": {"call_orphan": "fc-orphan"},
        },
    )
    messages = [
        SystemMessage(content="sys"),
        answered,
        ToolMessage(content="ok", tool_call_id="call_ok", name="get_table_schema"),
        orphan,
    ]
    sanitized = sanitize_messages_for_model(messages)
    last = sanitized[-1]
    assert isinstance(last, AIMessage)
    assert not last.invalid_tool_calls
    assert not last.tool_calls
    assert "__openai_function_call_ids__" not in (last.additional_kwargs or {})

    items = _construct_responses_api_input(sanitized)
    call_ids = [
        item.get("call_id")
        for item in items
        if isinstance(item, dict) and item.get("type") == "function_call"
    ]
    assert "call_orphan" not in call_ids
    assert "call_ok" in call_ids


def test_request_clarification_input_repairs_leaked_options() -> None:
    from apps.chat.tools.registry import RequestClarificationInput

    payload = {
        "questions": [
            {
                "question": "判定规则？",
                "question_id": "q1",
                "options": [
                    {"label": "任一为空", "option_id": "any", "table": "t", "field": "f"},
                    {"label": "全部为空", "option_id": "all", "table": "t", "field": "f"},
                ],
            },
            {
                "label": "仅启用",
                "option_id": "active",
                "description": "只看启用",
                "fields": [{"table": "c", "name": "enable", "value": "Y"}],
            },
            {
                "label": "全部",
                "option_id": "all_records",
                "description": "含停用",
                "table": "c",
                "field": "enable",
            },
        ],
        "question": "统计范围？",
        "question_id": "q2",
    }
    parsed = RequestClarificationInput.model_validate(payload)
    assert len(parsed.questions) == 2
    assert parsed.questions[1].question_id == "q2"
    assert len(parsed.questions[1].options) == 2

