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

from apps.chat.answer_payload import build_answer_payload  # noqa: E402
from apps.chat.graphs.nodes import nlq  # noqa: E402
from apps.chat.semantic_intent import IntentContext  # noqa: E402
from apps.chat.steps.clarification import SemanticAssessmentResult  # noqa: E402
from apps.conversation.outcome import RunOutcome  # noqa: E402
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
        "accepted_candidate": None,
        "rejected_candidate": None,
        "active_candidate": {
            "plan_validated": True,
            "contract_satisfied": True,
            "plans": [
                {
                    "sql": "SELECT current",
                    "format_statement": "SELECT current",
                    "brief": "current",
                    "chart_type": "table",
                    "tables": ["t"],
                }
            ],
            "results": [
                {
                    "index": 0,
                    "result": {"fields": ["name"], "data": [{"name": "B"}]},
                }
            ],
            "charts": [{"type": "table"}],
        },
        "entity_bindings": {"resolved": {"org": {"canonical": "A"}}},
        "intent_context": {"status": "ready"},
        "analysis_text": "",
    }


def _candidate(steps: list[dict[str, Any]]) -> nlq.CandidateBatch:
    assessments = nlq._assess_all_steps(steps)
    quality = nlq._build_candidate_quality(
        assessments,
        intent_ready=True,
        plan_validated=True,
        contract_satisfied=True,
    )
    return nlq._candidate_batch(steps, quality=quality)


def test_candidate_quality_does_not_mutate_the_input_outcome() -> None:
    steps = [
        {
            "sql": "SELECT 1",
            "result": {"fields": ["value"], "data": [{"value": 1}]},
        }
    ]
    raw_outcome: RunOutcome = {
        "status": "success",
        "failures": [],
        "successful_steps": 1,
        "total_steps": 1,
    }
    quality = nlq._build_candidate_quality(
        nlq._assess_all_steps(steps),
        intent_ready=True,
        plan_validated=True,
        contract_satisfied=True,
    )

    candidate = nlq._candidate_batch(
        steps,
        quality=quality,
        outcome=raw_outcome,
    )

    assert "quality" not in raw_outcome
    assert candidate["outcome"]["quality"] == quality


def test_ready_intent_is_persisted_before_sql_generation(
    monkeypatch: Any,
) -> None:
    persisted: list[dict[str, Any]] = []
    span: dict[str, Any] = {}

    @contextmanager
    def fake_log_span(**_kwargs: Any) -> Any:
        yield span

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
        lambda *_args, **_kwargs: SemanticAssessmentResult(
            context=ready,
            usage={"total_tokens": 12},
            reasoning="口径完整",
            attempts=[{"attempt": 1, "valid": True}],
        ),
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
    assert span["payload"]["assessment_attempt_count"] == 1
    assert span["payload"]["assessment_attempts"] == [{"attempt": 1, "valid": True}]
    assert span["token_usage"]["total_tokens"] == 12


def test_repair_rejects_current_batch_but_keeps_its_context(
    monkeypatch: Any,
) -> None:
    service = _service()
    meta: dict[str, Any] = {}
    monkeypatch.setattr(
        nlq,
        "validate_result_structure",
        lambda _items, **_kwargs: {
            "valid": False,
            "issues": [
                {
                    "code": "split_multi_metric_grain",
                    "step_index": 0,
                    "params": {},
                }
            ],
        },
    )
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
        meta=meta,
    )

    assert result["decision"] == "repair"
    assert result["accepted_candidate"] is None
    assert [step["sql"] for step in result["rejected_candidate"]["steps"]] == [
        "SELECT current"
    ]
    assert (
        result["rejected_candidate"]["steps"][0]["_entity_bindings"]["resolved"]["org"][
            "canonical"
        ]
        == "A"
    )
    assert "wrong grain" in result["repair_hint"]
    assert [step["sql"] for step in nlq._context_steps(result)] == ["SELECT current"]
    assert meta["used_llm"] is False
    assert meta["path"] == "structural_repair"


def test_successful_batch_is_accepted_without_autonomous_extension() -> None:
    service = _service()
    meta: dict[str, Any] = {}

    result = nlq._decide_next_impl(
        _state(),
        service,
        step_index=0,
        max_steps=2,
        meta=meta,
    )

    assert result["decision"] == "accept"
    assert [step["sql"] for step in result["accepted_candidate"]["steps"]] == [
        "SELECT current"
    ]
    assert result["rejected_candidate"] is None
    assert result["repair_hint"] == ""
    assert meta["path"] == "accepted"
    assert service.llm.messages == []


def test_terminal_structural_rejection_has_unreliable_empty_quality(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(
        nlq,
        "validate_result_structure",
        lambda _items, **_kwargs: {
            "valid": False,
            "issues": [
                {
                    "code": "split_multi_metric_grain",
                    "step_index": 0,
                    "params": {},
                }
            ],
        },
    )

    result = nlq._decide_next_impl(
        _state(),
        _service(),
        step_index=0,
        max_steps=1,
        meta={},
    )

    assert result["accepted_candidate"] is None
    assert result["outcome"]["status"] == "failed"
    assert result["outcome"]["quality"]["score"] == 0
    assert result["outcome"]["quality"]["grade"] == "unreliable"
    assert result["outcome"]["failures"][0]["kind"] == "validation"


def test_failed_candidate_is_not_published_as_an_answer() -> None:
    service = _service()
    state = _state()
    state["active_candidate"]["results"] = [
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
        meta={},
    )

    assert result["decision"] == "complete"
    assert result["accepted_candidate"] is None
    assert result["rejected_candidate"] is not None
    assert result["outcome"]["status"] == "failed"


def test_successful_repair_replaces_rejected_candidate() -> None:
    service = _service()
    state = _state()
    state["rejected_candidate"] = _candidate(
        [
            {
                "sql": "SELECT rejected",
                "brief": "rejected",
                "result": {"fields": ["name"], "data": [{"name": "old"}]},
                "chart": {"type": "table"},
            }
        ]
    )
    state["active_candidate"]["plans"][0]["sql"] = "SELECT repaired"
    state["active_candidate"]["plans"][0]["format_statement"] = "SELECT repaired"

    result = nlq._decide_next_impl(
        state,
        service,
        step_index=1,
        max_steps=2,
        meta={},
    )

    assert [step["sql"] for step in result["accepted_candidate"]["steps"]] == [
        "SELECT repaired"
    ]
    assert result["rejected_candidate"] is None


def test_failed_repair_never_publishes_rejected_candidate() -> None:
    service = _service()
    state = _state()
    state["rejected_candidate"] = _candidate(
        [
            {
                "sql": "SELECT previous",
                "brief": "previous",
                "result": {"fields": ["name"], "data": [{"name": "old"}]},
                "chart": {"type": "table"},
            }
        ]
    )
    state["active_candidate"]["results"] = [
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
        step_index=1,
        max_steps=2,
        meta={},
    )

    assert result["accepted_candidate"] is None
    assert result["outcome"]["status"] == "failed"
    assert [step["sql"] for step in result["rejected_candidate"]["steps"]] == [
        "SELECT current"
    ]


def test_partial_batch_is_never_used_as_a_repair_fallback() -> None:
    service = _service()
    state = _state()
    state["active_candidate"]["plans"].append(
        {
            "sql": "SELECT broken",
            "format_statement": "SELECT broken",
            "brief": "broken",
            "chart_type": "table",
            "tables": ["t"],
        }
    )
    state["active_candidate"]["results"].append(
        {
            "index": 1,
            "error": "unknown column",
            "failure": {
                "kind": "unknown_identifier",
                "message": "unknown column",
                "retryable": True,
            },
        }
    )
    repairing = nlq._decide_next_impl(
        state,
        service,
        step_index=0,
        max_steps=2,
        meta={},
    )
    assert repairing["decision"] == "repair"
    assert repairing["rejected_candidate"]["outcome"]["successful_steps"] == 1
    assert repairing["rejected_candidate"]["outcome"]["total_steps"] == 2

    repairing["active_candidate"] = {
        "plans": state["active_candidate"]["plans"][:1],
        "results": [
            {
                "index": 0,
                "error": "permission denied",
                "failure": {
                    "kind": "permission",
                    "message": "permission denied",
                    "retryable": False,
                },
            }
        ],
        "charts": [],
    }
    terminal = nlq._decide_next_impl(
        repairing,
        service,
        step_index=1,
        max_steps=2,
        meta={},
    )

    assert terminal["accepted_candidate"] is None
    assert terminal["outcome"]["status"] == "failed"


def test_quality_score_does_not_replace_a_structurally_valid_candidate() -> None:
    service = _service()
    state = _state()
    state["rejected_candidate"] = _candidate(
        [
            {
                "sql": "SELECT previous",
                "brief": "previous",
                "result": {"fields": ["name"], "data": [{"name": "old"}]},
                "chart": {"type": "table"},
            }
        ]
    )
    state["active_candidate"]["plans"][0]["sql"] = "SELECT empty_repair"
    state["active_candidate"]["plans"][0]["format_statement"] = "SELECT empty_repair"
    state["active_candidate"]["results"][0]["result"] = {
        "fields": ["name"],
        "data": [],
    }

    result = nlq._decide_next_impl(
        state,
        service,
        step_index=1,
        max_steps=2,
        meta={},
    )

    assert [step["sql"] for step in result["accepted_candidate"]["steps"]] == [
        "SELECT empty_repair"
    ]
    assert result["outcome"]["quality"]["score"] == 95
    assert result["outcome"]["quality"]["grade"] == "excellent"
    assert [item["code"] for item in result["outcome"]["quality"]["observations"]] == [
        "empty_result"
    ]


def test_repair_instruction_uses_structural_validation_issues() -> None:
    instruction = nlq._repair_instruction(
        [
            {
                "index": 0,
                "row_count": 10,
                "structural_issues": [
                    {
                        "code": "split_multi_metric_grain",
                        "step_index": 0,
                        "params": {},
                    }
                ],
            }
        ],
        "汇总指标",
    )

    assert "多指标结果被稀疏维度拆成互斥行" in instruction
    assert "共同业务粒度" in instruction


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
    assert nlq.route_after_decision({**base, "decision": "accept"}) == "generate_charts"
    assert nlq.route_after_decision({**base, "decision": "complete"}) == "complete"


def test_query_data_uses_the_same_decision_gate_before_completion() -> None:
    state = {"finish_step": nlq.ChatFinishStep.QUERY_DATA}

    assert nlq.route_after_execute(state) == "decide_next"
    assert nlq.route_after_decision({**state, "decision": "accept"}) == "complete"
    assert (
        nlq.route_after_decision(
            {**state, "decision": "repair", "step_index": 1, "max_steps": 2}
        )
        == "generate_queries"
    )


def test_chart_failure_falls_back_to_table_without_rejecting_data(
    monkeypatch: Any,
) -> None:
    class FakeSink:
        def event(self, _payload: dict[str, Any]) -> None:
            return None

    @contextmanager
    def fake_session_scope() -> Any:
        yield object()

    def fake_generate_chart(*_args: Any, **_kwargs: Any) -> Any:
        yield {"content": "not-json", "reasoning_content": ""}

    service = SimpleNamespace(
        out_ds_instance=None,
        chart_message=[],
        current_logs={},
        chat_question=SimpleNamespace(sql=""),
        record=SimpleNamespace(id=99),
    )
    state = {
        "llm_service": service,
        "accepted_candidate": {
            "plans": [
                {
                    "sql": "SELECT category, amount FROM sales",
                    "format_statement": "SELECT category, amount FROM sales",
                    "brief": "销售额",
                    "chart_type": "bar",
                }
            ],
            "results": [
                {
                    "index": 0,
                    "plan": {
                        "sql": "SELECT category, amount FROM sales",
                        "brief": "销售额",
                        "chart_type": "bar",
                    },
                    "result": {
                        "fields": ["category", "amount"],
                        "data": [{"category": "A", "amount": 10}],
                    },
                }
            ],
            "steps": [
                {
                    "sql": "SELECT category, amount FROM sales",
                    "brief": "销售额",
                    "result": {
                        "fields": ["category", "amount"],
                        "data": [{"category": "A", "amount": 10}],
                    },
                }
            ],
            "outcome": {
                "status": "success",
                "failures": [],
                "successful_steps": 1,
                "total_steps": 1,
            },
        },
    }
    monkeypatch.setattr(nlq.StreamSink, "from_state", lambda _state: FakeSink())
    monkeypatch.setattr(nlq, "session_scope", fake_session_scope)
    monkeypatch.setattr(nlq, "generate_chart", fake_generate_chart)

    result = nlq.generate_charts_node(state)

    assert result.get("error") is None
    assert result["accepted_candidate"]["charts"][0]["type"] == "table"
    assert result["accepted_candidate"]["outcome"]["status"] == "success"


def test_terminal_round_uses_plain_markdown_summary(monkeypatch: Any) -> None:
    @contextmanager
    def fake_log_span(**_kwargs: Any) -> Any:
        yield {}

    monkeypatch.setattr(nlq, "log_span", fake_log_span)
    service = _service()
    meta: dict[str, Any] = {}

    accepted = nlq._decide_next_impl(
        _state(),
        service,
        step_index=1,
        max_steps=2,
        meta=meta,
    )
    accepted["llm_service"] = service
    result = nlq.summarize_answer_node(accepted)

    assert accepted["decision"] == "accept"
    assert accepted["rejected_candidate"] is None
    assert "## 数据质量与局限" in result["analysis_text"]
    assert "未能生成完整文字总结" not in result["analysis_text"]
    assert meta["path"] == "accepted"
    assert "不要输出 JSON" in str(service.llm.messages[1].content)


def test_missing_summary_text_uses_deterministic_fallback(monkeypatch: Any) -> None:
    @contextmanager
    def fake_log_span(**_kwargs: Any) -> Any:
        yield {}

    monkeypatch.setattr(nlq, "log_span", fake_log_span)
    service = _service(FakeSummaryRetryModel())
    accepted = nlq._decide_next_impl(
        _state(),
        service,
        step_index=0,
        max_steps=2,
        meta={},
    )
    accepted["llm_service"] = service
    result = nlq.summarize_answer_node(accepted)

    assert "## 结论" in result["analysis_text"]
    assert "总结模型未返回可用正文" in result["analysis_text"]
    assert service.llm.calls == 1


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
    assert assessment["limitations"]
    assert nlq.validate_result_structure([assessment])["valid"] is True
    assessments = nlq._assess_all_steps([step])
    report = nlq._build_candidate_quality(
        assessments,
        intent_ready=True,
        plan_validated=True,
        contract_satisfied=True,
    )
    assert report["score"] == 95
    assert report["grade"] == "excellent"
    assert report["coverage"] == {
        "returned_rows": 1000,
        "truncated": True,
        "step_count": 1,
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

    assessments = nlq._assess_all_steps([step])
    assessment = assessments[0]
    quality = nlq._build_candidate_quality(
        assessments,
        intent_ready=True,
        plan_validated=True,
        contract_satisfied=True,
    )

    assert assessment["limitations"]
    assert {observation["code"] for observation in quality["observations"]} == {
        "dimension_null_severe",
        "metric_all_zero",
        "truncated_result",
    }
    assert nlq.validate_result_structure([assessment])["valid"] is True


def test_candidate_quality_attributes_structure_failure_to_the_affected_step() -> None:
    assessments = [
        {
            "index": 0,
            "execution_status": "success",
            "row_count": 1,
            "truncated": False,
            "null_rates": {},
            "metrics": {},
            "structural_issues": [],
        },
        {
            "index": 1,
            "execution_status": "success",
            "row_count": 1,
            "truncated": False,
            "null_rates": {},
            "metrics": {},
            "structural_issues": [{"code": "split_multi_metric_grain"}],
        },
    ]

    quality = nlq._build_candidate_quality(
        assessments,
        intent_ready=True,
        plan_validated=True,
        contract_satisfied=True,
    )

    semantic_dimension = next(
        item
        for item in quality["dimensions"]
        if item["code"] == "sql_semantic_correctness"
    )
    assert semantic_dimension["score"] == 40
    assert {detail.get("step_index") for detail in semantic_dimension["details"]} == {2}


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


def test_snapshot_persists_one_run_level_quality_report() -> None:
    step = {
        "sql": "SELECT amount FROM t",
        "brief": "amount",
        "result": {
            "fields": ["amount"],
            "fields_info": [{"name": "amount", "is_numeric": True}],
            "data": [{"amount": 10}],
        },
        "chart": {"type": "table"},
    }
    assessments = nlq._assess_all_steps([step])
    quality = nlq._build_candidate_quality(
        assessments,
        intent_ready=True,
        plan_validated=True,
        contract_satisfied=True,
    )

    payload = build_answer_payload(
        [step],
        "done",
        {
            "status": "success",
            "failures": [],
            "successful_steps": 1,
            "total_steps": 1,
            "quality": quality,
        },
    )

    assert "quality" not in payload["steps"][0]
    assert payload["outcome"]["quality"]["score"] == 95


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
            "accepted_candidate": {
                "steps": [
                    {
                        "sql": "SELECT 1",
                        "brief": "one",
                        "result": {"fields": ["v"], "data": [{"v": 1}]},
                        "chart": {"type": "table"},
                    }
                ]
            },
            "analysis_text": "查询完成",
            "return_img": False,
        }
    )

    assert order == ["persist", "analysis", "finish"]
    assert result["outcome"]["status"] == "success"


def test_fail_node_persists_canonical_empty_answer_before_emitting(
    monkeypatch: Any,
) -> None:
    calls: list[dict[str, Any]] = []
    service = SimpleNamespace(record=SimpleNamespace(id=99))

    def persist(
        _service: Any, steps: list[dict[str, Any]], _analysis: str, **values: Any
    ) -> None:
        calls.append({"steps": steps, **values})

    monkeypatch.setattr(nlq, "_persist_record_snapshot", persist)
    monkeypatch.setattr(nlq, "fail_turn_node", lambda state: dict(state))

    result = nlq.fail_node(
        {
            "llm_service": service,
            "record_id": 99,
            "error": "plan validation failed",
        }
    )

    assert calls[0]["steps"] == []
    assert calls[0]["finish"] is True
    assert calls[0]["outcome"]["status"] == "failed"
    assert calls[0]["outcome"]["quality"]["grade"] == "unreliable"
    assert result["outcome"]["status"] == "failed"


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
