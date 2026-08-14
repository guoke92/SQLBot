"""Single user-visible business-audit channel for every conversation graph."""

from __future__ import annotations

import json
import re
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal

import orjson
from sqlalchemy import select, update
from sqlmodel import Session

from apps.chat.models.chat_model import ChatLog, OperationEnum
from apps.conversation.observability import _end_log, _start_log
from apps.conversation.session import session_scope

SPAN_FLAG = "sqlbot_span"
AUDIT_VERSION = 1
AuditPhase = Literal[
    "prepare", "understand", "plan", "execute", "review", "present", "respond"
]
AuditOutcome = Literal["success", "degraded", "failed"]

_SECRET_KEYS = frozenset(
    {
        "access_key",
        "access_token",
        "api_key",
        "authorization",
        "client_secret",
        "credential",
        "credentials",
        "password",
        "private_key",
        "refresh_token",
        "secret",
        "secret_access_key",
        "secret_key",
        "token",
    }
)


def _normalized_key(key: object) -> str:
    text = str(key).strip().replace("-", "_").replace(" ", "_")
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", text).lower()


def sanitize_audit_value(value: Any, *, key: object | None = None) -> Any:
    """Recursively remove credentials before audit data is persisted."""
    normalized = _normalized_key(key or "")
    if normalized in _SECRET_KEYS or normalized.endswith(
        ("_password", "_secret", "_token")
    ):
        return "<redacted>"
    if normalized in {"configuration", "config"} and isinstance(value, str):
        try:
            return sanitize_audit_value(json.loads(value))
        except (TypeError, ValueError):
            return "<redacted>"
    if isinstance(value, Mapping):
        return {
            str(item_key): sanitize_audit_value(item_value, key=item_key)
            for item_key, item_value in value.items()
        }
    if isinstance(value, list | tuple):
        return [sanitize_audit_value(item) for item in value]
    if isinstance(value, datetime | date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, bytes | bytearray):
        return bytes(value).decode(errors="replace")
    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        return sanitize_audit_value(model_dump(mode="json"))
    if isinstance(value, str):
        value = re.sub(
            r"(?i)\b(password|passwd|pwd|api[_-]?key|access[_-]?token)\s*[:=]\s*([^\s,;]+)",
            r"\1=<redacted>",
            value,
        )
        value = re.sub(r"(?<=\s)-p[^\s]+", "-p<redacted>", value)
        value = re.sub(
            r"(https?://[^:/\s]+:)[^@/\s]+@", r"\1<redacted>@", value
        )
        value = re.sub(
            r"(?i)(authorization\s*:\s*(?:bearer|basic)\s+)[^\s]+",
            r"\1<redacted>",
            value,
        )
    if value is None or isinstance(value, bool | int | float):
        return value
    try:
        orjson.dumps(value)
        return value
    except TypeError:
        return str(value)


def serialize_model_messages(messages: Sequence[Any] | None) -> list[dict[str, Any]]:
    """Serialize LangChain or mapping messages without retaining live objects."""
    result: list[dict[str, Any]] = []
    for message in messages or []:
        if isinstance(message, Mapping):
            item = dict(message)
        else:
            item = {
                "type": getattr(message, "type", message.__class__.__name__.lower()),
                "sqlbot_system": getattr(message, "sqlbot_system", False) is True,
                "content": getattr(message, "content", str(message)),
            }
            tool_calls = getattr(message, "tool_calls", None)
            if tool_calls:
                item["tool_calls"] = tool_calls
        result.append(sanitize_audit_value(item))
    return result


def _model_io(messages: Sequence[Any] | None) -> tuple[Any | None, Any | None]:
    """Split one original model exchange into its request and response."""
    serialized = serialize_model_messages(messages)
    if not serialized:
        return None, None
    last_type = str(
        serialized[-1].get("type") or serialized[-1].get("role") or ""
    ).lower()
    if last_type in {"ai", "assistant", "aimessage"} or "assistant" in last_type:
        return serialized[:-1] or None, serialized[-1]
    return serialized, None


def make_span_message(
    *,
    phase: AuditPhase = "plan",
    graph_node: str = "",
    step_index: int | None = None,
    gen_attempts: int | None = None,
    unit_index: int | None = None,
    brief: str = "",
    title_key: str = "",
    title_params: dict[str, Any] | None = None,
    summary_key: str | None = None,
    summary_params: dict[str, Any] | None = None,
    outcome: AuditOutcome | None = None,
    payload: dict[str, Any] | None = None,
    input_value: Any | None = None,
    output_value: Any | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the only persisted, versioned audit envelope."""
    message: dict[str, Any] = {
        SPAN_FLAG: True,
        "version": AUDIT_VERSION,
        "phase": phase,
    }
    if graph_node:
        message["graph_node"] = graph_node
    if title_key:
        message["title_key"] = title_key
    if title_params:
        message["title_params"] = sanitize_audit_value(title_params)
    if summary_key:
        message["summary_key"] = summary_key
    if summary_params:
        message["summary_params"] = sanitize_audit_value(summary_params)
    if step_index is not None:
        message["batch_index"] = int(step_index)
    if gen_attempts is not None:
        message["attempt_index"] = int(gen_attempts)
    if unit_index is not None:
        message["unit_index"] = int(unit_index)
    if brief:
        message["brief"] = brief
    if outcome:
        message["outcome"] = outcome
    if payload:
        message["detail"] = sanitize_audit_value(payload)
    if input_value is not None:
        message["input"] = sanitize_audit_value(input_value)
    if output_value is not None:
        message["output"] = sanitize_audit_value(output_value)
    for item_key, item_value in (extra or {}).items():
        if item_key not in message and item_value is not None:
            message[item_key] = sanitize_audit_value(item_value, key=item_key)
    return message


def parse_audit_envelope(value: Any) -> dict[str, Any] | None:
    """Parse V1 only; unversioned history has one generic raw fallback."""
    if (
        not isinstance(value, dict)
        or value.get(SPAN_FLAG) is not True
        or int(value.get("version") or 0) != AUDIT_VERSION
    ):
        return None
    return dict(value)


def project_audit_message(
    value: Any,
    *,
    finish_time: datetime | None,
    error: bool,
    run_terminal: bool,
) -> dict[str, Any]:
    """Project persisted audit data into the shared ExecutionStep fields."""
    message = value
    if isinstance(message, str | bytes | bytearray):
        try:
            message = orjson.loads(message)
        except Exception:
            pass
    envelope = parse_audit_envelope(message)
    interrupted = bool((envelope or {}).get("detail", {}).get("interrupted"))
    if interrupted:
        status = "interrupted"
    elif finish_time is None:
        status = "interrupted" if run_terminal else "running"
    elif error or (envelope or {}).get("outcome") == "failed":
        status = "failed"
    elif (envelope or {}).get("outcome") == "degraded":
        status = "degraded"
    else:
        status = "success"
    summary_key = (envelope or {}).get("summary_key")
    summary_params = dict((envelope or {}).get("summary_params") or {})
    if summary_key == "chat.audit.processing" and status != "running":
        summary_key = {
            "failed": "chat.audit.step_failed",
            "interrupted": "chat.audit.step_interrupted",
            "degraded": "chat.audit.step_degraded",
        }.get(status)
        summary_params = {}
    input_value = (envelope or {}).get("input")
    output_value = (envelope or {}).get("output")
    if input_value is None and output_value is None and (envelope or {}).get(
        "model_messages"
    ):
        input_value, output_value = _model_io(
            (envelope or {}).get("model_messages")
        )
    return {
        "status": status,
        "phase": str((envelope or {}).get("phase") or "plan"),
        "graph_node": (envelope or {}).get("graph_node"),
        "title_key": (envelope or {}).get("title_key"),
        "title_params": dict((envelope or {}).get("title_params") or {}),
        "summary_key": summary_key,
        "summary_params": summary_params,
        "batch_index": (envelope or {}).get("batch_index"),
        "attempt_index": (envelope or {}).get("attempt_index"),
        "unit_index": (envelope or {}).get("unit_index"),
        "detail": dict((envelope or {}).get("detail") or {}),
        "input": input_value,
        "output": output_value,
        "message": message if envelope is None else None,
    }


def close_open_audit_spans(session: Session, record_id: int) -> int:
    """Truthfully close spans abandoned by a crash/recovery boundary."""
    rows = list(
        session.exec(
            select(ChatLog).where(
                ChatLog.pid == record_id,
                ChatLog.finish_time.is_(None),
                ChatLog.operate != OperationEnum.GENERATE_RECOMMENDED_QUESTIONS,
            )
        )
        .scalars()
        .all()
    )
    now = datetime.now()
    for row in rows:
        envelope = parse_audit_envelope(row.messages) or make_span_message()
        detail = dict(envelope.get("detail") or {})
        detail.update({"interrupted": True, "error_code": "RUN_INTERRUPTED"})
        envelope["detail"] = detail
        envelope["outcome"] = "failed"
        session.execute(
            update(ChatLog)
            .where(ChatLog.id == row.id)
            .values(messages=envelope, finish_time=now, error=True)
        )
    return len(rows)


class AuditSpanHandle(dict[str, Any]):
    """Small typed-behaviour handle used by domain steps."""

    def set_summary(self, key: str, **params: Any) -> None:
        self["summary_key"] = key
        self["summary_params"] = params

    def set_detail(self, detail: Mapping[str, Any]) -> None:
        self["payload"] = dict(detail)

    def set_model_context(self, messages: Sequence[Any]) -> None:
        input_value, output_value = _model_io(messages)
        self["input"] = input_value
        self["output"] = output_value

    def set_input_messages(self, messages: Sequence[Any]) -> None:
        self["input"] = serialize_model_messages(messages) or None

    def set_output_message(self, message: Any) -> None:
        serialized = serialize_model_messages([message])
        self["output"] = serialized[0] if serialized else None

    def set_input(self, value: Any) -> None:
        self["input"] = sanitize_audit_value(value)

    def set_output(self, value: Any) -> None:
        self["output"] = sanitize_audit_value(value)

    def set_usage(self, usage: Mapping[str, Any] | None) -> None:
        self["token_usage"] = dict(usage or {})

    def mark_degraded(self, reason: str = "") -> None:
        self["outcome"] = "degraded"
        if reason:
            self.setdefault("payload", {})["degraded_reason"] = reason

    def mark_failed(self, reason: str = "") -> None:
        self["error"] = True
        self["outcome"] = "failed"
        if reason:
            self.setdefault("payload", {})["error"] = reason

    def persist_progress(self) -> None:
        """Persist the current input/output snapshot without closing the span."""
        persist = self.get("_persist_progress")
        if callable(persist):
            try:
                persist()
            except Exception:
                # Observability must never become a business-path dependency.
                pass


@contextmanager
def log_span(
    *,
    operate: OperationEnum,
    record_id: int | None,
    run_id: str | None = None,
    ai_modal_id: int | None = None,
    ai_modal_name: str | None = None,
    local_operation: bool = True,
    phase: AuditPhase = "plan",
    graph_node: str = "",
    step_index: int | None = None,
    gen_attempts: int | None = None,
    unit_index: int | None = None,
    brief: str = "",
    title_key: str = "",
    title_params: dict[str, Any] | None = None,
    initial_summary_key: str = "chat.audit.processing",
    initial_summary_params: dict[str, Any] | None = None,
    initial_payload: dict[str, Any] | None = None,
) -> Iterator[AuditSpanHandle]:
    """Create, update and reliably close one business audit span."""
    span = AuditSpanHandle(
        payload=dict(initial_payload or {}),
        error=False,
        outcome=None,
        token_usage=None,
        reasoning_content=None,
        input=None,
        output=None,
        summary_key=initial_summary_key,
        summary_params=dict(initial_summary_params or {}),
        local_operation=local_operation,
        log=None,
    )
    if not record_id:
        yield span
        return

    if run_id is None:
        from apps.conversation.runtime_context import current_worker_identity

        active_run_id, _worker_token = current_worker_identity()
        run_id = active_run_id

    common = {
        "phase": phase,
        "graph_node": graph_node,
        "step_index": step_index,
        "gen_attempts": gen_attempts,
        "unit_index": unit_index,
        "brief": brief,
        "title_key": title_key,
        "title_params": title_params,
    }
    log: ChatLog | None = None
    try:
        with session_scope() as session:
            log = _start_log(
                session=session,
                ai_modal_id=ai_modal_id,
                ai_modal_name=ai_modal_name,
                operate=operate,
                record_id=record_id,
                run_id=run_id,
                full_message=make_span_message(
                    **common,
                    summary_key=initial_summary_key,
                    summary_params=initial_summary_params,
                ),
                local_operation=local_operation,
            )
            span["log"] = log

            def persist_progress() -> None:
                if log is None:
                    return
                progress_message = make_span_message(
                    **common,
                    summary_key=span.get("summary_key"),
                    summary_params=span.get("summary_params"),
                    payload=span.get("payload") or None,
                    input_value=span.get("input"),
                    output_value=span.get("output"),
                )
                with session_scope() as progress_session:
                    progress_session.execute(
                        update(ChatLog)
                        .where(ChatLog.id == log.id, ChatLog.finish_time.is_(None))
                        .values(
                            messages=progress_message,
                            reasoning_content=(
                                span.get("reasoning_content") or None
                            ),
                            token_usage=span.get("token_usage") or {},
                        )
                    )
                    progress_session.commit()

            span["_persist_progress"] = persist_progress
    except Exception:
        log = None

    try:
        yield span
    except Exception as exc:
        if span.get("output") is None:
            span.set_output(
                {
                    "status": "failed",
                    "error_type": exc.__class__.__name__,
                    "message": str(exc),
                }
            )
        span.mark_failed(str(exc))
        raise
    finally:
        if log is not None:
            try:
                outcome: AuditOutcome = (
                    "failed"
                    if span.get("error")
                    else "degraded"
                    if span.get("outcome") == "degraded"
                    else "success"
                )
                final_message = make_span_message(
                    **common,
                    summary_key=span.get("summary_key"),
                    summary_params=span.get("summary_params"),
                    outcome=outcome,
                    payload=span.get("payload") or None,
                    input_value=span.get("input"),
                    output_value=span.get("output"),
                )
                with session_scope() as session:
                    final_local = bool(span.get("local_operation", local_operation))
                    if final_local != local_operation:
                        session.execute(
                            update(ChatLog)
                            .where(ChatLog.id == log.id)
                            .values(local_operation=final_local)
                        )
                    _end_log(
                        session=session,
                        log=log,
                        full_message=final_message,
                        reasoning_content=span.get("reasoning_content"),
                        token_usage=span.get("token_usage") or {},
                        error=outcome == "failed",
                    )
            except Exception:
                pass
