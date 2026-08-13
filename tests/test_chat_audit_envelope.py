"""Contract tests for the single user-visible conversation audit envelope."""

from __future__ import annotations

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
)


def test_running_envelope_has_no_false_completion_detail() -> None:
    message = make_span_message(
        phase="understand",
        graph_node="retrieve_context",
        title_key="chat.log.FILTER_TERMS",
        summary_key="chat.audit.processing",
    )

    assert message == {
        "sqlbot_span": True,
        "version": 1,
        "phase": "understand",
        "graph_node": "retrieve_context",
        "title_key": "chat.log.FILTER_TERMS",
        "summary_key": "chat.audit.processing",
    }


def test_only_v1_envelope_is_interpreted_semantically() -> None:
    legacy = {"sqlbot_span": True, "phase": "plan", "payload": {"count": 0}}
    current = make_span_message(phase="plan", outcome="success")

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
    running = make_span_message(phase="execute")
    interrupted = make_span_message(
        phase="execute",
        outcome="failed",
        payload={"interrupted": True},
    )
    degraded = make_span_message(phase="respond", outcome="degraded")

    assert project_audit_message(
        running,
        finish_time=None,
        error=False,
        run_terminal=False,
    )["status"] == "running"
    assert project_audit_message(
        running,
        finish_time=None,
        error=False,
        run_terminal=True,
    )["status"] == "interrupted"
    assert project_audit_message(
        interrupted,
        finish_time=None,
        error=True,
        run_terminal=True,
    )["status"] == "interrupted"
    assert project_audit_message(
        degraded,
        finish_time=datetime.now(),
        error=False,
        run_terminal=True,
    )["status"] == "degraded"


def test_terminal_step_never_keeps_processing_summary() -> None:
    processing = make_span_message(
        phase="understand",
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


def test_audit_handle_can_keep_request_and_failed_response() -> None:
    span = AuditSpanHandle()
    span.set_input_messages([{"role": "user", "content": "request"}])
    span.set_output_message(
        {"role": "assistant", "content": '{"invalid": true}'}
    )
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

    serialized = serialize_model_messages(
        [SystemMessage(content="line one\nline two")]
    )
    assert serialized[0]["content"] == "line one\nline two"
