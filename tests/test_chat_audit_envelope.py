"""Contract tests for the single user-visible conversation audit envelope."""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.steps.observability import (  # noqa: E402
    AuditSpanHandle,
    make_span_message,
    parse_audit_envelope,
    project_audit_message,
    sanitize_audit_value,
    serialize_model_calls,
)


def test_running_envelope_has_no_false_completion_detail() -> None:
    message = make_span_message(
        graph_node="retrieve_context",
        title_key="chat.log.FILTER_TERMS",
        summary_key="chat.audit.processing",
    )

    assert message == {
        "sqlbot_span": True,
        "version": 1,
        "graph_node": "retrieve_context",
        "title_key": "chat.log.FILTER_TERMS",
        "summary_key": "chat.audit.processing",
    }


def test_first_attempt_batch_and_unit_are_not_tagged() -> None:
    hidden = make_span_message(
        step_index=0,
        gen_attempts=0,
        unit_index=0,
    )
    shown = make_span_message(
        step_index=1,
        gen_attempts=2,
        unit_index=3,
    )

    assert "batch_index" not in hidden
    assert "attempt_index" not in hidden
    assert "unit_index" not in hidden
    assert shown["batch_index"] == 1
    assert shown["attempt_index"] == 2
    assert shown["unit_index"] == 3


def test_only_v1_envelope_is_interpreted_semantically() -> None:
    legacy = {"sqlbot_span": True, "payload": {"count": 0}}
    current = make_span_message(outcome="success")

    assert parse_audit_envelope(legacy) is None
    assert parse_audit_envelope(current) == current


def test_audit_sanitizer_covers_nested_model_and_tool_context() -> None:
    value = {
        "authorization": "Bearer abc",
        "nested": {"apiKey": "secret", "safe": "visible"},
        "configuration": '{"user":"demo","password":"pw"}',
        "command": "mysql -h db -udemo -ppw select 1",
        "url": "https://demo:pw@example.invalid/path",
    }

    sanitized = sanitize_audit_value(value)

    assert sanitized["authorization"] == "<redacted>"
    assert sanitized["nested"] == {"apiKey": "<redacted>", "safe": "visible"}
    assert sanitized["configuration"] == {
        "user": "demo",
        "password": "<redacted>",
    }
    assert "-p<redacted>" in sanitized["command"]
    assert sanitized["url"] == "https://demo:<redacted>@example.invalid/path"


def test_execution_projection_uses_one_status_contract() -> None:
    running = make_span_message()
    interrupted = make_span_message(
        outcome="failed",
        payload={"interrupted": True},
    )
    degraded = make_span_message(outcome="degraded")

    assert (
        project_audit_message(
            running,
            finish_time=None,
            error=False,
            run_terminal=False,
        )["status"]
        == "running"
    )
    assert (
        project_audit_message(
            running,
            finish_time=None,
            error=False,
            run_terminal=True,
        )["status"]
        == "interrupted"
    )
    assert (
        project_audit_message(
            interrupted,
            finish_time=None,
            error=True,
            run_terminal=True,
        )["status"]
        == "interrupted"
    )
    assert (
        project_audit_message(
            degraded,
            finish_time=datetime.now(),
            error=False,
            run_terminal=True,
        )["status"]
        == "degraded"
    )


def test_terminal_step_never_keeps_processing_summary() -> None:
    processing = make_span_message(
        summary_key="chat.audit.processing",
        outcome="failed",
    )

    failed = project_audit_message(
        processing,
        finish_time=datetime.now(),
        error=True,
        run_terminal=True,
    )

    assert failed["status"] == "failed"
    assert failed["summary_key"] == "chat.audit.step_failed"


def test_model_exchange_projects_raw_input_and_output() -> None:
    span = AuditSpanHandle()
    span.set_model_context(
        [
            {"role": "system", "content": "instructions"},
            {"role": "user", "content": "question"},
            {"role": "assistant", "content": '{"answer": 1}'},
        ]
    )
    message = make_span_message(
        input_value=span["input"],
        output_value=span["output"],
        outcome="success",
    )
    projection = project_audit_message(
        message,
        finish_time=datetime.now(),
        error=False,
        run_terminal=True,
    )

    assert projection["input"] == [
        {"role": "system", "content": "instructions"},
        {"role": "user", "content": "question"},
    ]
    assert projection["output"] == {
        "role": "assistant",
        "content": '{"answer": 1}',
    }
    assert "model_messages" not in message


def test_model_calls_keep_every_retry_as_an_independent_exchange() -> None:
    calls = serialize_model_calls(
        [
            {
                "attempt": 1,
                "status": "invalid",
                "elapsed_ms": 1200,
                "usage": {"total_tokens": 10},
                "messages": [
                    {"role": "user", "content": "request"},
                    {"role": "assistant", "content": '{"invalid":true}'},
                ],
                "error": "validation failed",
            },
            {
                "attempt": 2,
                "status": "success",
                "elapsed_ms": 800,
                "usage": {"total_tokens": 12},
                "messages": [
                    {"role": "user", "content": "repair"},
                    {"role": "assistant", "content": '{"answer":1}'},
                ],
            },
        ]
    )
    message = make_span_message(model_calls=calls, outcome="failed")
    projection = project_audit_message(
        message,
        finish_time=datetime.now(),
        error=True,
        run_terminal=True,
    )

    assert [item["attempt"] for item in projection["model_calls"]] == [1, 2]
    assert projection["model_calls"][0]["input"] == [
        {"role": "user", "content": "request"}
    ]
    assert projection["model_calls"][1]["output"]["content"] == '{"answer":1}'


def test_model_output_is_the_exact_sanitized_response() -> None:
    response = {
        "decision": "ready",
        "intent": {"internal": "not shown"},
        "evidence_bindings": [{"internal": "not shown"}],
        "candidates": [{"payload": {"sql": "SELECT 1"}}],
        "summary": "简单查询",
    }
    calls = serialize_model_calls(
        [
            {
                "attempt": 1,
                "messages": [
                    {"role": "user", "content": "query"},
                    {
                        "role": "assistant",
                        "content": json.dumps(response, ensure_ascii=False),
                    },
                ],
            }
        ]
    )

    assert "internal" in calls[0]["output"]["content"]

    message = make_span_message(output_value=calls[0]["output"], outcome="success")
    projection = project_audit_message(
        message,
        finish_time=datetime.now(),
        error=False,
        run_terminal=True,
    )
    assert projection["output"] == calls[0]["output"]
    assert "display_output" not in projection


def test_legacy_aggregate_log_does_not_fabricate_model_calls() -> None:
    first_response = {
        "role": "assistant",
        "content": '{"decision":"ready","candidates":[]}',
    }
    final_response = {
        "role": "assistant",
        "content": '{"decision":"ready","candidates":[{"payload":{"sql":"SELECT 1"}}]}',
    }
    message = make_span_message(
        input_value=[
            {"role": "system", "content": "system"},
            {"role": "user", "content": "query"},
            first_response,
            {"role": "user", "content": "repair"},
        ],
        output_value=final_response,
        payload={
            "attempts": [
                {"attempt": 1, "error": "invalid intent"},
                {"attempt": 2, "decision": "ready"},
            ]
        },
        outcome="failed",
    )

    projection = project_audit_message(
        message,
        finish_time=datetime.now(),
        error=True,
        run_terminal=True,
    )

    assert projection["model_calls"] == []
    assert projection["output"] == final_response


def test_audit_handle_can_keep_request_and_failed_response() -> None:
    span = AuditSpanHandle()
    span.set_input_messages([{"role": "user", "content": "request"}])
    span.set_output_message({"role": "assistant", "content": '{"invalid": true}'})
    span["reasoning_content"] = "reasoning"

    message = make_span_message(
        input_value=span["input"],
        output_value=span["output"],
        outcome="failed",
    )

    assert message["input"] == [{"role": "user", "content": "request"}]
    assert message["output"] == {
        "role": "assistant",
        "content": '{"invalid": true}',
    }


def test_serialized_messages_keep_raw_newlines() -> None:
    from langchain_core.messages import SystemMessage

    from apps.chat.steps.observability import serialize_model_messages

    serialized = serialize_model_messages([SystemMessage(content="line one\nline two")])
    assert serialized[0]["content"] == "line one\nline two"
