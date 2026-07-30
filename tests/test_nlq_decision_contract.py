"""NLQ candidate review, repair, and publication contracts."""

from __future__ import annotations

import sys
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.graphs.nodes import nlq  # noqa: E402
from apps.chat.semantic_intent import IntentContext  # noqa: E402
from apps.conversation.usage import merge_usage, usage_from_response  # noqa: E402


class FakeSummaryModel:
    def __init__(self) -> None:
        self.messages: list[Any] = []

    def invoke(self, messages: list[Any]) -> AIMessage:
        self.messages = messages
        return AIMessage(
            content=(
                "## 结论\n查询完成。\n\n"
                "## SQL 生成依据与解释\n依据已执行查询。\n\n"
                "## 数据解读\n返回了明确数据。\n\n"
                "## 数据质量与局限\n无额外限制。\n\n"
                "## 建议\n继续按需分析。"
            ),
            usage_metadata={
                "input_tokens": 100,
                "output_tokens": 80,
                "total_tokens": 180,
            },
        )


class FakeSummaryRetryModel:
    def __init__(self) -> None:
        self.calls = 0

    def invoke(self, _messages: list[Any]) -> AIMessage:
        self.calls += 1
        if self.calls == 1:
            content = '{"action":"summarize","reason":"ready"}'
        else:
            content = (
                "## 结论\n有明确结果。\n\n"
                "## SQL 生成依据与解释\n依据查询。\n\n"
                "## 数据解读\n已返回记录。\n\n"
                "## 数据质量与局限\n无。\n\n"
                "## 建议\n继续分析。"
            )
        return AIMessage(
            content=content,
            usage_metadata={
                "input_tokens": 10,
                "output_tokens": 5,
                "total_tokens": 15,
            },
        )


def _service(model: Any | None = None) -> SimpleNamespace:
    return SimpleNamespace(
        llm=model or FakeSummaryModel(),
        sql_message=[HumanMessage(content="large mutable SQL history must not leak")],
        chat_question=SimpleNamespace(
            question="compare two metrics",
            ai_modal_id=7,
            ai_modal_name="fake",
        ),
        record=SimpleNamespace(id=99),
    )


def _state() -> dict[str, Any]:
    return {
        "all_steps": [],
        "repair_steps": [],
        "batch_plans": [
            {
                "sql": "SELECT current",
                "format_statement": "SELECT current",
                "brief": "current",
                "chart_type": "table",
                "tables": ["t"],
            }
        ],
        "batch_results": [
            {
                "index": 0,
                "result": {"fields": ["name"], "data": [{"name": "B"}]},
            }
        ],
        "batch_charts": [{"type": "table"}],
        "entity_bindings": {"resolved": {"org": {"canonical": "A"}}},
        "analysis_text": "",
    }


def test_ready_intent_is_persisted_before_sql_generation(
    monkeypatch: Any,
) -> None:
    persisted: list[dict[str, Any]] = []

    @contextmanager
    def fake_log_span(**_kwargs: Any) -> Any:
        yield {}

    @contextmanager
    def fake_session_scope() -> Any:
        yield object()

    class FakeSink:
        def event(self, _payload: dict[str, Any]) -> None:
            return None

    context = IntentContext(
        status="evaluating",
        original_question="汇总签收额和融资额",
    )
    ready = context.model_copy(update={"status": "ready", "summary": "口径完整"})
    service = SimpleNamespace(
        record=SimpleNamespace(id=77, intent_context=None),
        chat_question=SimpleNamespace(
            intent_context=context.model_dump(mode="json"),
            question="汇总签收额和融资额",
            ai_modal_id=1,
            ai_modal_name="fake",
        ),
    )

    monkeypatch.setattr(nlq, "log_span", fake_log_span)
    monkeypatch.setattr(
        nlq,
        "assess_semantic_intent",
        lambda *_args, **_kwargs: (ready, {}, ""),
    )
    monkeypatch.setattr(nlq.StreamSink, "from_state", lambda _state: FakeSink())
    monkeypatch.setattr(nlq, "session_scope", fake_session_scope)
    monkeypatch.setattr(
        nlq,
        "persist_snapshot",
        lambda _session, _record_id, **kwargs: persisted.append(kwargs) or True,
    )

    result = nlq.assess_clarity_node(
        {
            "llm_service": service,
            "intent_context": context.model_dump(mode="json"),
            "entity_bindings": {},
            "time_intent": {},
        }
    )

    assert result["intent_context"]["status"] == "ready"
    assert persisted == [{"intent_context": result["intent_context"]}]


def test_repair_rejects_current_batch_but_keeps_its_context(
    monkeypatch: Any,
) -> None:
    service = _service()
    meta: dict[str, Any] = {}
    monkeypatch.setattr(nlq, "_quality_requires_repair", lambda _items: True)
    monkeypatch.setattr(nlq, "outcome_allows_retry", lambda _outcome: True)
    monkeypatch.setattr(
        nlq,
        "_repair_instruction",
        lambda _assessments, _question: "wrong grain",
    )

    result = nlq._decide_next_impl(
        _state(),
        service,
        step_index=0,
        max_steps=2,
        finish_v=3,
        meta=meta,
    )

    assert result["decision"] == "repair"
    assert result["all_steps"] == []
    assert [step["sql"] for step in result["repair_steps"]] == ["SELECT current"]
    assert (
        result["repair_steps"][0]["_entity_bindings"]["resolved"]["org"]["canonical"]
        == "A"
    )
    assert "wrong grain" in result["repair_hint"]
    assert [step["sql"] for step in nlq._context_steps(result)] == ["SELECT current"]
    assert meta["used_llm"] is False
    assert meta["path"] == "auto_repair"


def test_successful_batch_is_accepted_without_autonomous_extension() -> None:
    service = _service()
    meta: dict[str, Any] = {}

    result = nlq._decide_next_impl(
        _state(),
        service,
        step_index=0,
        max_steps=2,
        finish_v=3,
        meta=meta,
    )

    assert result["decision"] == "complete"
    assert [step["sql"] for step in result["all_steps"]] == ["SELECT current"]
    assert result["repair_steps"] == []
    assert result["repair_hint"] == ""
    assert meta["path"] == "llm_summary"
    assert len(service.llm.messages) == 2
    assert isinstance(service.llm.messages[1], HumanMessage)
    assert all(
        "large mutable SQL history must not leak" not in str(message.content)
        for message in service.llm.messages
    )


def test_failed_candidate_is_not_published_as_an_answer() -> None:
    service = _service()
    state = _state()
    state["batch_results"] = [
        {
            "index": 0,
            "error": "permission denied",
            "failure": {
                "kind": "permission",
                "message": "permission denied",
                "retryable": False,
            },
        }
    ]

    result = nlq._decide_next_impl(
        state,
        service,
        step_index=0,
        max_steps=2,
        finish_v=3,
        meta={},
    )

    assert result["decision"] == "complete"
    assert result["all_steps"] == []
    assert [step["sql"] for step in result["repair_steps"]] == ["SELECT current"]
    assert result["outcome"]["status"] == "failed"


def test_usage_from_response_supports_provider_response_metadata() -> None:
    response = SimpleNamespace(
        usage_metadata=None,
        response_metadata={
            "token_usage": {
                "prompt_tokens": 11,
                "completion_tokens": 5,
                "total_tokens": 16,
            }
        },
    )

    assert usage_from_response(response) == {
        "input_tokens": 11,
        "output_tokens": 5,
        "total_tokens": 16,
    }
    assert merge_usage(
        usage_from_response(response),
        {"input_tokens": 2, "output_tokens": 3, "total_tokens": 5},
    ) == {
        "input_tokens": 13,
        "output_tokens": 8,
        "total_tokens": 21,
    }


def test_router_only_sends_repair_back_to_generation() -> None:
    base = {"step_index": 1, "max_steps": 2}

    assert (
        nlq.route_after_decision({**base, "decision": "repair"}) == "generate_queries"
    )
    assert nlq.route_after_decision({**base, "decision": "complete"}) == "complete"


def test_terminal_round_uses_plain_markdown_summary() -> None:
    service = _service()
    meta: dict[str, Any] = {}

    result = nlq._decide_next_impl(
        _state(),
        service,
        step_index=1,
        max_steps=2,
        finish_v=3,
        meta=meta,
    )

    assert result["decision"] == "complete"
    assert result["repair_steps"] == []
    assert "## 数据质量与局限" in result["analysis_text"]
    assert "未能生成完整文字总结" not in result["analysis_text"]
    assert meta["path"] == "llm_summary"
    assert "不要输出 JSON" in str(service.llm.messages[1].content)


def test_missing_summary_text_is_retried_as_plain_markdown() -> None:
    service = _service(FakeSummaryRetryModel())
    meta: dict[str, Any] = {}

    result = nlq._decide_next_impl(
        _state(),
        service,
        step_index=0,
        max_steps=2,
        finish_v=3,
        meta=meta,
    )

    assert result["decision"] == "complete"
    assert "## 结论" in result["analysis_text"]
    assert "未能生成完整文字总结" not in result["analysis_text"]
    assert service.llm.calls == 2
    assert meta["summary_retried"] is True
    assert meta["token_usage"]["total_tokens"] == 30


def test_display_truncation_is_a_limitation_not_a_repair_failure() -> None:
    step = {
        "sql": "SELECT value FROM t ORDER BY value DESC",
        "brief": "ordered values",
        "result": {
            "fields": ["value"],
            "fields_info": [{"name": "value", "is_numeric": True}],
            "data": [{"value": index} for index in range(1000)],
            "row_count": 1000,
            "limit": 1000,
            "truncated": True,
            "truncation_reason": "query_limit",
        },
        "chart": {"type": "table"},
    }

    assessment = nlq._assess_step_quality(step, 0)

    assert assessment["row_count"] == 1000
    assert assessment["severity"] is False
    assert assessment["issues"] == []
    assert assessment["limitations"]
    assert nlq._quality_requires_repair([assessment]) is False
    assert nlq._result_quality([step]) == {
        "status": "partial",
        "truncated": True,
        "returned_rows": 1000,
    }


def test_truncated_sample_quality_signals_do_not_trigger_repair() -> None:
    step = {
        "sql": "SELECT supplier_level, amount FROM t",
        "brief": "supplier metrics",
        "result": {
            "fields": ["supplier_level", "amount"],
            "fields_info": [
                {"name": "supplier_level", "is_numeric": False},
                {"name": "amount", "is_numeric": True},
            ],
            "data": [{"supplier_level": None, "amount": 0} for _index in range(1000)],
            "row_count": 1000,
            "limit": 1000,
            "truncated": True,
            "truncation_reason": "query_limit",
        },
        "chart": {"type": "table"},
    }

    assessment = nlq._assess_step_quality(step, 0)

    assert assessment["severity"] is False
    assert assessment["issues"] == []
    assert any(
        "不能据此判断全量 join 质量" in item for item in assessment["limitations"]
    )
    assert any("展示样本中指标列" in item for item in assessment["limitations"])


def test_nlq_snapshot_projects_through_shared_persistence_boundary(
    monkeypatch: Any,
) -> None:
    session = object()
    calls: list[dict[str, Any]] = []

    @contextmanager
    def fake_session_scope() -> Any:
        yield session

    def fake_persist(current_session: Any, record_id: int, **values: Any) -> bool:
        calls.append(
            {
                "session": current_session,
                "record_id": record_id,
                **values,
            }
        )
        return True

    monkeypatch.setattr(nlq, "session_scope", fake_session_scope)
    monkeypatch.setattr(nlq, "persist_snapshot", fake_persist)
    service = SimpleNamespace(record=SimpleNamespace(id=99))

    nlq._persist_record_snapshot(
        service,
        [
            {
                "sql": "SELECT 1",
                "brief": "one",
                "result": {"fields": ["v"], "data": [{"v": 1}]},
                "chart": {"type": "table"},
            }
        ],
        "done",
        finish=True,
        outcome={
            "status": "success",
            "failures": [],
            "successful_steps": 1,
            "total_steps": 1,
        },
    )

    assert len(calls) == 1
    assert calls[0]["session"] is session
    assert calls[0]["record_id"] == 99
    assert calls[0]["sql"] == "SELECT 1"
    assert calls[0]["terminal"] is True
    assert calls[0]["error"] is None


def test_complete_commits_snapshot_before_publishing_analysis(
    monkeypatch: Any,
) -> None:
    order: list[str] = []

    class FakeSink:
        mode = "sse"

        def event(self, payload: dict[str, Any]) -> None:
            order.append(str(payload["type"]))

        def json_result(self, _payload: dict[str, Any]) -> None:
            return None

    @contextmanager
    def fake_log_span(**_kwargs: Any) -> Any:
        yield {}

    service = SimpleNamespace(
        record=SimpleNamespace(id=99, chat_id=8),
        chat_question=SimpleNamespace(ai_modal_id=7, ai_modal_name="fake"),
    )
    monkeypatch.setattr(nlq.StreamSink, "from_state", lambda _state: FakeSink())
    monkeypatch.setattr(nlq, "log_span", fake_log_span)
    monkeypatch.setattr(
        nlq,
        "_persist_record_snapshot",
        lambda *_args, **_kwargs: order.append("persist"),
    )

    result = nlq.complete_node(
        {
            "llm_service": service,
            "all_steps": [
                {
                    "sql": "SELECT 1",
                    "brief": "one",
                    "result": {"fields": ["v"], "data": [{"v": 1}]},
                    "chart": {"type": "table"},
                }
            ],
            "analysis_text": "查询完成",
            "return_img": False,
        }
    )

    assert order == ["persist", "analysis", "finish"]
    assert result["outcome"]["status"] == "success"


def test_nlq_snapshot_scalar_projection_uses_first_accepted_step(
    monkeypatch: Any,
) -> None:
    calls: list[dict[str, Any]] = []

    @contextmanager
    def fake_session_scope() -> Any:
        yield object()

    monkeypatch.setattr(nlq, "session_scope", fake_session_scope)
    monkeypatch.setattr(
        nlq,
        "persist_snapshot",
        lambda _session, _record_id, **values: calls.append(values) or True,
    )
    service = SimpleNamespace(record=SimpleNamespace(id=99))
    nlq._persist_record_snapshot(
        service,
        [
            {"sql": "SELECT first", "chart": {"type": "table"}},
            {"sql": "SELECT second", "chart": {"type": "bar"}},
        ],
        finish=True,
        outcome={
            "status": "success",
            "failures": [],
            "successful_steps": 2,
            "total_steps": 2,
        },
    )

    assert calls[0]["sql"] == "SELECT first"
    assert '"table"' in calls[0]["chart"]
