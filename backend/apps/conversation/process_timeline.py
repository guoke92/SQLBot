"""Single process-timeline contract: write to chat_log, project for UI.

ProcessItemV1 is the only shape for inline agent timeline and Execution Details.
Run events carry compact upserts/deltas of the same items; they are not a
second audit truth.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Mapping, Sequence
from datetime import datetime
from typing import Any, Literal
from uuid import uuid4

from sqlalchemy import select, update
from sqlmodel import Session

from apps.chat.models.chat_model import ChatLog, ChatRecord, OperationEnum
from apps.chat.steps.observability import (
    make_span_message,
    parse_audit_envelope,
    project_audit_message,
    sanitize_audit_value,
)
from apps.conversation.models import ResultDataset
from apps.conversation.observability import _end_log, _start_log
from apps.conversation.runtime_context import current_worker_identity
from apps.conversation.session import audit_session, session_scope
from apps.conversation.sink import StreamSink

ProcessKind = Literal["thought", "tool", "artifact", "clarification", "answer"]
ProcessStatus = Literal["running", "completed", "failed", "interrupted"]
ProcessView = Literal["compact", "detail"]

PREVIEW_ROW_LIMIT = 3
# Durable chat_log keeps full LLM prompts up to this serialized-char ceiling.
# Compact SSE upserts omit heavy input/output; Execution Details uses view=detail.
# Thought body is never display-capped: compact/SSE and detail all keep the full text.
LLM_IO_MAX_CHARS = 400_000
_DELTA_FLUSH_CHARS = 96
_DELTA_FLUSH_SEC = 0.5

_KIND_OPERATE: dict[ProcessKind, OperationEnum] = {
    "thought": OperationEnum.AGENT_STEP,
    "tool": OperationEnum.TOOL_CALL,
    "artifact": OperationEnum.TOOL_CALL,
    "clarification": OperationEnum.CLARIFY_INTENT,
    "answer": OperationEnum.ANALYSIS,
}


def bound_llm_io(value: Any, *, max_chars: int = LLM_IO_MAX_CHARS) -> Any:
    """Persist full prompts when possible; hard-cap pathological sizes."""
    sanitized = sanitize_audit_value(value)
    try:
        import orjson

        encoded = orjson.dumps(sanitized).decode()
    except Exception:
        encoded = str(sanitized)
    if len(encoded) <= max_chars:
        return sanitized
    return {
        "truncated": True,
        "truncation_reason": "llm_io_max_chars",
        "max_chars": max_chars,
        "preview": encoded[: max(0, max_chars - 128)],
    }


def project_thought_for_view(
    thought: Mapping[str, Any] | None,
    view: ProcessView = "compact",
) -> dict[str, Any] | None:
    """Pass through the full thought for every view.

    Compact vs detail only differs on whether ``detail`` (model I/O) is attached.
    Display truncation does not shorten generation and hid the real CoT.
    """
    if not thought:
        return None
    _ = view
    return dict(thought)


_KIND_TITLE_KEY: dict[ProcessKind, str] = {
    "thought": "chat.timeline.thought",
    "tool": "chat.timeline.tool.generic",
    "artifact": "chat.timeline.artifact",
    "clarification": "chat.timeline.clarification",
    "answer": "chat.timeline.answer",
}


def tool_title_key(tool_name: str) -> str:
    if tool_name:
        return f"chat.timeline.tool.{tool_name}"
    return "chat.timeline.tool.generic"


def _duration_ms(start: datetime | None, finish: datetime | None) -> int | None:
    if start is None or finish is None:
        return None
    return max(0, int((finish - start).total_seconds() * 1000))


def _as_iso(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def localize_text(
    trans: Callable[..., str] | None,
    key: str | None,
    params: Mapping[str, Any] | None = None,
) -> str:
    if not key:
        return ""
    if trans is None:
        return key
    try:
        text = trans(key, **dict(params or {}))
    except Exception:
        text = key
    return text if text else key


def localize_process_item(
    item: dict[str, Any],
    trans: Callable[..., str] | None,
) -> dict[str, Any]:
    projected = dict(item)
    projected["title"] = localize_text(
        trans, projected.get("title_key"), projected.get("title_params")
    )
    projected["summary"] = localize_text(
        trans, projected.get("summary_key"), projected.get("summary_params")
    )
    return projected


def localize_process_event(
    payload: Mapping[str, Any],
    trans: Callable[..., str] | None,
) -> dict[str, Any]:
    event = dict(payload)
    event_type = str(event.get("type") or "")
    if event_type in {"process_upsert", "process_delta"}:
        nested = dict(event.get("item") or event)
        localized = localize_process_item(nested, trans)
        if "item" in event:
            event["item"] = localized
        else:
            event.update(localized)
    return event


def _compact_item(item: dict[str, Any]) -> dict[str, Any]:
    compact = dict(item)
    compact.pop("detail", None)
    thought = compact.get("thought")
    if isinstance(thought, Mapping):
        projected = project_thought_for_view(thought, "compact")
        if projected is not None:
            compact["thought"] = projected
    return compact


def _emit_process_event(
    sink: StreamSink | None,
    *,
    event_type: str,
    item: Mapping[str, Any],
) -> None:
    if sink is None or sink.mode != "sse":
        return
    payload = {"type": event_type, "item": _compact_item(dict(item))}
    sink.event(payload)


def _process_payload(
    *,
    kind: ProcessKind,
    parent_id: int | None = None,
    tool: Mapping[str, Any] | None = None,
    thought: Mapping[str, Any] | None = None,
    artifact: Mapping[str, Any] | None = None,
    answer: Mapping[str, Any] | None = None,
    meta: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"process_kind": kind}
    if parent_id is not None:
        payload["parent_id"] = parent_id
    if tool:
        payload["tool"] = sanitize_audit_value(dict(tool))
    if thought:
        payload["thought"] = dict(thought)
    if artifact:
        payload["artifact"] = sanitize_audit_value(dict(artifact))
    if answer:
        payload["answer"] = dict(answer)
    if meta:
        payload["meta"] = sanitize_audit_value(dict(meta))
    return payload


def _item_from_log(
    log: ChatLog,
    *,
    attempt_index: int = 0,
    run_terminal: bool = False,
    view: ProcessView = "compact",
) -> dict[str, Any] | None:
    envelope = parse_audit_envelope(log.messages)
    if envelope is None:
        return None
    detail = dict(envelope.get("detail") or {})
    kind = detail.get("process_kind")
    if kind not in _KIND_TITLE_KEY:
        return None
    projection = project_audit_message(
        envelope,
        finish_time=log.finish_time,
        error=bool(log.error),
        run_terminal=run_terminal,
    )
    status_map = {
        "running": "running",
        "success": "completed",
        "degraded": "completed",
        "failed": "failed",
        "interrupted": "interrupted",
    }
    status = status_map.get(str(projection["status"]), "completed")
    item: dict[str, Any] = {
        "id": int(log.id),
        "sequence": int(log.id),
        "run_id": log.run_id,
        "record_id": log.pid,
        "attempt_index": attempt_index,
        "kind": kind,
        "status": status,
        "title_key": projection.get("title_key") or _KIND_TITLE_KEY[kind],
        "title_params": dict(projection.get("title_params") or {}),
        "summary_key": projection.get("summary_key"),
        "summary_params": dict(projection.get("summary_params") or {}),
        "started_at": _as_iso(log.start_time),
        "finished_at": _as_iso(log.finish_time),
        "duration_ms": _duration_ms(log.start_time, log.finish_time),
        "parent_id": detail.get("parent_id"),
    }
    if detail.get("tool"):
        item["tool"] = dict(detail["tool"])
    thought_payload = dict(detail.get("thought") or {})
    reasoning = str(log.reasoning_content or "").strip()
    if reasoning and not str(thought_payload.get("content") or "").strip():
        thought_payload["content"] = log.reasoning_content
    if thought_payload:
        projected = project_thought_for_view(thought_payload, view)
        if projected:
            item["thought"] = projected
    if detail.get("artifact"):
        item["artifact"] = dict(detail["artifact"])
    if detail.get("answer"):
        item["answer"] = dict(detail["answer"])
    if isinstance(detail.get("meta"), Mapping) and detail["meta"]:
        item["meta"] = dict(detail["meta"])
    if view == "detail":
        item["detail"] = {
            "input": projection.get("input"),
            "output": projection.get("output"),
            "model_calls": projection.get("model_calls") or [],
            "token_usage": log.token_usage or {},
            "operate": (
                log.operate.name
                if isinstance(log.operate, OperationEnum)
                else str(log.operate or "")
            ),
        }
    return item


class ProcessSpan:
    """Open / delta / close one ProcessItem, writing chat_log then run events."""

    def __init__(
        self,
        *,
        log: ChatLog,
        kind: ProcessKind,
        sink: StreamSink | None,
        run_id: str | None,
        record_id: int | None,
        attempt_index: int,
        title_key: str,
        title_params: dict[str, Any],
        graph_node: str,
        parent_id: int | None,
        tool: dict[str, Any] | None,
        thought: dict[str, Any] | None,
        artifact: dict[str, Any] | None,
        answer: dict[str, Any] | None,
        meta: dict[str, Any] | None,
        summary_key: str | None,
        summary_params: dict[str, Any],
        local_operation: bool,
        ai_modal_id: int | None,
        ai_modal_name: str | None,
    ) -> None:
        self.id = int(log.id)
        self.kind = kind
        self.sink = sink
        self.run_id = run_id
        self.record_id = record_id
        self.attempt_index = attempt_index
        self._log = log
        self._title_key = title_key
        self._title_params = dict(title_params)
        self._graph_node = graph_node
        self._parent_id = parent_id
        self._tool = dict(tool) if tool else None
        self._thought = dict(thought) if thought else None
        self._artifact = dict(artifact) if artifact else None
        self._answer = dict(answer) if answer else None
        self._meta = dict(meta) if meta else None
        self._summary_key = summary_key
        self._summary_params = dict(summary_params)
        self._local_operation = local_operation
        self._ai_modal_id = ai_modal_id
        self._ai_modal_name = ai_modal_name
        self._input: Any = None
        self._output: Any = None
        self._model_calls: list[Any] = []
        self._token_usage: dict[str, Any] = {}
        self._status: ProcessStatus = "running"
        self._closed = False
        self._last_flush = time.monotonic()
        self._pending_chars = 0

    def snapshot(self, *, status: ProcessStatus | None = None) -> dict[str, Any]:
        item: dict[str, Any] = {
            "id": self.id,
            "sequence": self.id,
            "run_id": self.run_id,
            "record_id": self.record_id,
            "attempt_index": self.attempt_index,
            "kind": self.kind,
            "status": status or self._status,
            "title_key": self._title_key,
            "title_params": dict(self._title_params),
            "summary_key": self._summary_key,
            "summary_params": dict(self._summary_params),
            "started_at": _as_iso(self._log.start_time),
            "finished_at": _as_iso(self._log.finish_time) if self._closed else None,
            "duration_ms": (
                _duration_ms(self._log.start_time, self._log.finish_time)
                if self._closed
                else None
            ),
            "parent_id": self._parent_id,
        }
        if self._tool:
            item["tool"] = dict(self._tool)
        if self._thought:
            item["thought"] = dict(self._thought)
        if self._artifact:
            item["artifact"] = dict(self._artifact)
        if self._answer:
            item["answer"] = dict(self._answer)
        if self._meta:
            item["meta"] = dict(self._meta)
        return item

    def _envelope(
        self,
        *,
        outcome: str | None = None,
        extra_detail: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload = _process_payload(
            kind=self.kind,
            parent_id=self._parent_id,
            tool=self._tool,
            thought=self._thought,
            artifact=self._artifact,
            answer=self._answer,
            meta=self._meta,
        )
        if extra_detail:
            payload.update(dict(extra_detail))
        return make_span_message(
            graph_node=self._graph_node,
            title_key=self._title_key,
            title_params=self._title_params,
            summary_key=self._summary_key,
            summary_params=self._summary_params,
            outcome=outcome,  # type: ignore[arg-type]
            payload=payload,
            input_value=self._input,
            output_value=self._output,
            model_calls=self._model_calls or None,
        )

    def _flush_log(self, *, outcome: str | None = None) -> None:
        try:
            with audit_session() as session:
                session.execute(
                    update(ChatLog)
                    .where(ChatLog.id == self.id, ChatLog.finish_time.is_(None))
                    .values(
                        messages=self._envelope(outcome=outcome),
                        reasoning_content=(
                            (self._thought or {}).get("content")
                            if self.kind == "thought"
                            else None
                        ),
                        token_usage=self._token_usage or {},
                    )
                )
                session.commit()
        except Exception:
            pass
        self._last_flush = time.monotonic()
        self._pending_chars = 0

    def set_input(self, value: Any) -> None:
        self._input = bound_llm_io(value)

    def set_output(self, value: Any) -> None:
        self._output = bound_llm_io(value)

    def set_meta(self, meta: Mapping[str, Any] | None) -> None:
        if not meta:
            return
        current = dict(self._meta or {})
        current.update(dict(meta))
        self._meta = current

    def set_model_calls(self, calls: Sequence[Mapping[str, Any]] | None) -> None:
        self._model_calls = [dict(item) for item in calls or []]

    def set_usage(self, usage: Mapping[str, Any] | None) -> None:
        self._token_usage = dict(usage or {})

    def delta(
        self,
        *,
        thought_content: str | None = None,
        thought_source: str | None = None,
        answer_content: str | None = None,
        summary_key: str | None = None,
        summary_params: Mapping[str, Any] | None = None,
        tool: Mapping[str, Any] | None = None,
        artifact: Mapping[str, Any] | None = None,
        flush: bool = False,
    ) -> None:
        if self._closed:
            return
        added = 0
        if thought_content or thought_source:
            current = dict(self._thought or {"source": "scratchpad", "content": ""})
            if thought_source:
                current["source"] = thought_source
            if thought_content:
                current["content"] = str(current.get("content") or "") + thought_content
                added += len(thought_content)
            self._thought = current
        if answer_content:
            current_answer = dict(self._answer or {"content": ""})
            current_answer["content"] = (
                str(current_answer.get("content") or "") + answer_content
            )
            self._answer = current_answer
            added += len(answer_content)
        if tool:
            merged = dict(self._tool or {})
            merged.update(dict(tool))
            self._tool = merged
        if artifact:
            merged_art = dict(self._artifact or {})
            merged_art.update(dict(artifact))
            self._artifact = merged_art
        if summary_key:
            self._summary_key = summary_key
            self._summary_params = dict(summary_params or {})
        self._pending_chars += added
        _emit_process_event(self.sink, event_type="process_delta", item=self.snapshot())
        elapsed = time.monotonic() - self._last_flush
        if (
            flush
            or self._pending_chars >= _DELTA_FLUSH_CHARS
            or elapsed >= _DELTA_FLUSH_SEC
        ):
            self._flush_log()

    def close(
        self,
        *,
        status: ProcessStatus = "completed",
        summary_key: str | None = None,
        summary_params: Mapping[str, Any] | None = None,
        tool: Mapping[str, Any] | None = None,
        artifact: Mapping[str, Any] | None = None,
        extra_detail: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        if self._closed:
            return self.snapshot()
        if summary_key:
            self._summary_key = summary_key
            self._summary_params = dict(summary_params or {})
        if tool:
            merged = dict(self._tool or {})
            merged.update(dict(tool))
            self._tool = merged
        if artifact:
            merged_art = dict(self._artifact or {})
            merged_art.update(dict(artifact))
            self._artifact = merged_art
        self._status = status
        outcome = "failed" if status in {"failed", "interrupted"} else "success"
        extra = dict(extra_detail or {})
        if status == "interrupted":
            extra["interrupted"] = True
            extra["error_code"] = extra.get("error_code") or "RUN_INTERRUPTED"
        envelope = self._envelope(outcome=outcome, extra_detail=extra)
        try:
            with audit_session() as session:
                _end_log(
                    session=session,
                    log=self._log,
                    full_message=envelope,
                    reasoning_content=(
                        (self._thought or {}).get("content")
                        if self.kind == "thought"
                        else None
                    ),
                    token_usage=self._token_usage or {},
                    error=status in {"failed", "interrupted"},
                )
                row = session.get(ChatLog, self.id)
                if row is not None:
                    self._log = row
        except Exception:
            pass
        self._closed = True
        item = self.snapshot(status=status)
        _emit_process_event(self.sink, event_type="process_upsert", item=item)
        return item

    def discard(self) -> None:
        """Drop an unused span (e.g. empty thought before a final answer)."""
        if self._closed:
            return
        self._closed = True
        try:
            with audit_session() as session:
                row = session.get(ChatLog, self.id)
                if row is not None:
                    session.delete(row)
                    session.commit()
        except Exception:
            pass
        if self.sink is not None and self.sink.mode == "sse":
            self.sink.event({"type": "process_remove", "id": self.id})


def open_process_span(
    *,
    kind: ProcessKind,
    record_id: int | None,
    sink: StreamSink | None = None,
    run_id: str | None = None,
    parent_id: int | None = None,
    graph_node: str = "",
    title_key: str | None = None,
    title_params: Mapping[str, Any] | None = None,
    summary_key: str | None = None,
    summary_params: Mapping[str, Any] | None = None,
    tool: Mapping[str, Any] | None = None,
    thought: Mapping[str, Any] | None = None,
    artifact: Mapping[str, Any] | None = None,
    answer: Mapping[str, Any] | None = None,
    meta: Mapping[str, Any] | None = None,
    local_operation: bool = True,
    ai_modal_id: int | None = None,
    ai_modal_name: str | None = None,
    attempt_index: int = 0,
) -> ProcessSpan | None:
    """Create a running chat_log row and emit process_upsert. None if no record."""
    if not record_id:
        return None
    if run_id is None:
        active_run_id, _token = current_worker_identity()
        run_id = active_run_id
    resolved_title = title_key or (
        tool_title_key(str((tool or {}).get("name") or ""))
        if kind == "tool"
        else _KIND_TITLE_KEY[kind]
    )
    params = dict(title_params or {})
    operate = _KIND_OPERATE[kind]
    payload = _process_payload(
        kind=kind,
        parent_id=parent_id,
        tool=tool,
        thought=thought,
        artifact=artifact,
        answer=answer,
        meta=meta,
    )
    envelope = make_span_message(
        graph_node=graph_node,
        title_key=resolved_title,
        title_params=params,
        summary_key=summary_key or "chat.audit.processing",
        summary_params=dict(summary_params or {}),
        payload=payload,
    )
    with audit_session() as session:
        log = _start_log(
            session=session,
            ai_modal_id=ai_modal_id,
            ai_modal_name=ai_modal_name,
            operate=operate,
            record_id=record_id,
            run_id=run_id,
            full_message=envelope,
            local_operation=local_operation,
        )
    span = ProcessSpan(
        log=log,
        kind=kind,
        sink=sink,
        run_id=run_id,
        record_id=record_id,
        attempt_index=attempt_index,
        title_key=resolved_title,
        title_params=params,
        graph_node=graph_node,
        parent_id=parent_id,
        tool=dict(tool) if tool else None,
        thought=dict(thought) if thought else None,
        artifact=dict(artifact) if artifact else None,
        answer=dict(answer) if answer else None,
        meta=dict(meta) if meta else None,
        summary_key=summary_key or "chat.audit.processing",
        summary_params=dict(summary_params or {}),
        local_operation=local_operation,
        ai_modal_id=ai_modal_id,
        ai_modal_name=ai_modal_name,
    )
    _emit_process_event(sink, event_type="process_upsert", item=span.snapshot())
    return span


def attach_process_span(
    item_id: int,
    *,
    sink: StreamSink | None = None,
    attempt_index: int = 0,
) -> ProcessSpan | None:
    with audit_session() as session:
        log = session.get(ChatLog, item_id)
        if log is None or log.finish_time is not None:
            return None
        envelope = parse_audit_envelope(log.messages) or {}
        detail = dict(envelope.get("detail") or {})
        kind = detail.get("process_kind")
        if kind not in _KIND_TITLE_KEY:
            return None
        return ProcessSpan(
            log=log,
            kind=kind,
            sink=sink,
            run_id=log.run_id,
            record_id=log.pid,
            attempt_index=attempt_index,
            title_key=str(envelope.get("title_key") or _KIND_TITLE_KEY[kind]),
            title_params=dict(envelope.get("title_params") or {}),
            graph_node=str(envelope.get("graph_node") or ""),
            parent_id=detail.get("parent_id"),
            tool=detail.get("tool"),
            thought=detail.get("thought"),
            artifact=detail.get("artifact"),
            answer=detail.get("answer"),
            meta=detail.get("meta")
            if isinstance(detail.get("meta"), Mapping)
            else None,
            summary_key=envelope.get("summary_key"),
            summary_params=dict(envelope.get("summary_params") or {}),
            local_operation=bool(log.local_operation),
            ai_modal_id=log.ai_modal_id,
            ai_modal_name=log.base_modal,
        )


def project_process_timeline(
    session: Session,
    *,
    record_id: int,
    run_id: str | None = None,
    view: ProcessView = "compact",
    trans: Callable[..., str] | None = None,
) -> dict[str, Any]:
    """Read chat_log into ProcessItemV1 list. Same source as Execution Details."""
    from apps.conversation.models import ConversationInterrupt, ConversationRun

    record = session.get(ChatRecord, record_id)
    if record is None:
        raise LookupError(f"ChatRecord {record_id} not found")
    runs = list(
        session.exec(
            select(ConversationRun)
            .where(ConversationRun.chat_record_id == record_id)
            .order_by(ConversationRun.attempt_index)
        ).scalars()
    )
    selected_run_id = run_id or record.active_run_id
    run = next(
        (item for item in runs if item.run_id == selected_run_id),
        runs[-1] if runs and selected_run_id is None else None,
    )
    log_query = select(ChatLog).where(
        ChatLog.pid == record_id,
        ChatLog.operate != OperationEnum.GENERATE_RECOMMENDED_QUESTIONS,
    )
    if run is not None:
        log_query = log_query.where(ChatLog.run_id == run.run_id)
    logs = list(
        session.exec(
            log_query.order_by(ChatLog.start_time.asc(), ChatLog.id.asc())
        ).scalars()
    )
    run_terminal = bool(
        run is not None
        and run.status in {"succeeded", "degraded", "failed", "cancelled"}
    )
    attempt_index = int(run.attempt_index or 0) if run is not None else 0
    items: list[dict[str, Any]] = []
    total_tokens = 0
    for log in logs:
        if isinstance(log.token_usage, dict):
            token_value = log.token_usage.get("total_tokens") or 0
            if isinstance(token_value, int | float):
                total_tokens += int(token_value)
        item = _item_from_log(
            log,
            attempt_index=attempt_index,
            run_terminal=run_terminal,
            view=view,
        )
        if item is None:
            continue
        items.append(item)
    items = [
        localize_process_item(item, trans) for item in fold_clarification_flow(items)
    ]
    # Drop completed thoughts with no body (final-answer rounds without reasoning).
    items = [
        item
        for item in items
        if not (
            item.get("kind") == "thought"
            and item.get("status") != "running"
            and not str((item.get("thought") or {}).get("content") or "").strip()
        )
    ]
    run_interrupts: list[Any] = []
    if run is not None:
        run_interrupts = list(
            session.exec(
                select(ConversationInterrupt).where(
                    ConversationInterrupt.run_id == run.run_id
                )
            ).scalars()
        )
    from apps.chat.curd.chat import _run_duration_breakdown

    elapsed, waiting, processing = _run_duration_breakdown(
        run,
        run_interrupts,
        fallback_start=record.create_time,
        fallback_end=record.finish_time,
    )
    attempts = [
        {
            "run_id": item.run_id,
            "status": item.status,
            "current_node": item.current_node,
            "attempt_index": int(item.attempt_index or 0),
            "started_at": item.started_at,
            "completed_at": item.completed_at,
        }
        for item in runs
    ]
    return {
        "record_id": record_id,
        "run_id": run.run_id if run is not None else None,
        "attempt_index": attempt_index,
        "view": view,
        "items": items,
        "total_tokens": total_tokens,
        "duration": processing,
        "waiting_duration": waiting,
        "elapsed_duration": elapsed,
        "run": (
            {
                "run_id": run.run_id,
                "status": run.status,
                "current_node": run.current_node,
                "started_at": run.started_at,
                "completed_at": run.completed_at,
            }
            if run is not None
            else None
        ),
        "attempts": attempts,
    }


def preview_rows(
    rows: Sequence[Mapping[str, Any]] | None,
    *,
    limit: int = PREVIEW_ROW_LIMIT,
) -> list[dict[str, Any]]:
    return [
        dict(row)
        for row in list(rows or [])[: max(0, limit)]
        if isinstance(row, Mapping)
    ]


def new_dataset_id() -> str:
    return f"ds_{uuid4().hex[:12]}"


def upsert_result_dataset(
    *,
    run_id: str,
    dataset_id: str,
    plan_id: str,
    fields: Sequence[str],
    rows: Sequence[Mapping[str, Any]],
    row_count: int,
    truncated: bool,
    sql: str = "",
    status: str = "succeeded",
    value_labels: Mapping[str, Mapping[str, str]] | None = None,
    limit: int | None = None,
    required: bool = True,
    result_title: str = "",
    chart_type: str = "",
) -> None:
    """Persist the row store without requiring a query_run planning row."""
    if not run_id:
        return
    safe_rows = [dict(item) for item in rows if isinstance(item, Mapping)]
    with session_scope() as session:
        existing = (
            session.exec(
                select(ResultDataset)
                .where(
                    ResultDataset.run_id == run_id,
                    ResultDataset.dataset_id == dataset_id,
                    ResultDataset.plan_id == plan_id,
                )
                .with_for_update()
            )
            .scalars()
            .one_or_none()
        )
        snapshot: dict[str, Any] = {}
        if sql:
            snapshot["sql"] = sql
        if limit is not None:
            snapshot["limit"] = int(limit)
        title = str(result_title or "").strip()
        if title:
            snapshot["result_title"] = title
        chart = str(chart_type or "").strip().lower()
        if chart:
            snapshot["chart_type"] = chart
        if value_labels:
            snapshot["value_labels"] = {
                str(field): {str(raw): str(label) for raw, label in mapping.items()}
                for field, mapping in value_labels.items()
                if isinstance(mapping, Mapping)
            }
        if existing is None:
            session.add(
                ResultDataset(
                    run_id=run_id,
                    dataset_id=dataset_id,
                    plan_id=plan_id,
                    status=status,
                    required=bool(required),
                    fields=[str(item) for item in fields],
                    rows=safe_rows,
                    row_count=row_count,
                    truncated=truncated,
                    schema_snapshot=snapshot,
                )
            )
        else:
            existing.status = status
            existing.required = bool(required)
            existing.fields = [str(item) for item in fields]
            existing.rows = safe_rows
            existing.row_count = row_count
            existing.truncated = truncated
            existing.schema_snapshot = {
                **(existing.schema_snapshot or {}),
                **snapshot,
            }
            existing.error = None
            session.add(existing)
        session.commit()


def _process_span_from_log(
    log: ChatLog,
    *,
    kind: ProcessKind,
    sink: StreamSink | None = None,
    attempt_index: int = 0,
) -> ProcessSpan:
    envelope = parse_audit_envelope(log.messages) or {}
    detail = dict(envelope.get("detail") or {})
    return ProcessSpan(
        log=log,
        kind=kind,
        sink=sink,
        run_id=log.run_id,
        record_id=log.pid,
        attempt_index=attempt_index,
        title_key=str(envelope.get("title_key") or _KIND_TITLE_KEY[kind]),
        title_params=dict(envelope.get("title_params") or {}),
        graph_node=str(envelope.get("graph_node") or ""),
        parent_id=detail.get("parent_id"),
        tool=detail.get("tool") if isinstance(detail.get("tool"), Mapping) else None,
        thought=detail.get("thought")
        if isinstance(detail.get("thought"), Mapping)
        else None,
        artifact=(
            detail.get("artifact")
            if isinstance(detail.get("artifact"), Mapping)
            else None
        ),
        answer=detail.get("answer")
        if isinstance(detail.get("answer"), Mapping)
        else None,
        meta=detail.get("meta") if isinstance(detail.get("meta"), Mapping) else None,
        summary_key=envelope.get("summary_key"),
        summary_params=dict(envelope.get("summary_params") or {}),
        local_operation=bool(log.local_operation),
        ai_modal_id=log.ai_modal_id,
        ai_modal_name=log.base_modal,
    )


def attach_running_tool_span(
    *,
    record_id: int | None,
    call_id: str,
    run_id: str | None = None,
    sink: StreamSink | None = None,
    attempt_index: int = 0,
) -> ProcessSpan | None:
    """Reuse an open tool span for the same call_id; never open a duplicate."""
    if not record_id or not call_id:
        return None
    with audit_session() as session:
        logs = list(
            session.exec(
                select(ChatLog)
                .where(
                    ChatLog.pid == record_id,
                    ChatLog.finish_time.is_(None),
                    ChatLog.operate == OperationEnum.TOOL_CALL,
                )
                .order_by(ChatLog.id.desc())
            ).scalars()
        )
        for log in logs:
            if run_id and log.run_id and log.run_id != run_id:
                continue
            envelope = parse_audit_envelope(log.messages) or {}
            detail = dict(envelope.get("detail") or {})
            if detail.get("process_kind") != "tool":
                continue
            tool = detail.get("tool") if isinstance(detail.get("tool"), Mapping) else {}
            if str(tool.get("call_id") or "") != call_id:
                continue
            return _process_span_from_log(
                log, kind="tool", sink=sink, attempt_index=attempt_index
            )
    return None


def attach_running_clarification_span(
    *,
    record_id: int | None,
    run_id: str | None = None,
    sink: StreamSink | None = None,
    attempt_index: int = 0,
) -> ProcessSpan | None:
    """Reuse the open clarification span across interrupt → resume (one lifecycle)."""
    if not record_id:
        return None
    with audit_session() as session:
        logs = list(
            session.exec(
                select(ChatLog)
                .where(
                    ChatLog.pid == record_id,
                    ChatLog.finish_time.is_(None),
                    ChatLog.operate == OperationEnum.CLARIFY_INTENT,
                )
                .order_by(ChatLog.id.desc())
            ).scalars()
        )
        for log in logs:
            if run_id and log.run_id and log.run_id != run_id:
                continue
            envelope = parse_audit_envelope(log.messages) or {}
            detail = dict(envelope.get("detail") or {})
            if detail.get("process_kind") != "clarification":
                continue
            return _process_span_from_log(
                log, kind="clarification", sink=sink, attempt_index=attempt_index
            )
    return None


def fold_clarification_flow(items: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Collapse request_clarification tool + wait/confirm spans into one card."""

    def _is_clarify_tool(item: Mapping[str, Any]) -> bool:
        tool = item.get("tool") if isinstance(item.get("tool"), Mapping) else {}
        return (
            item.get("kind") == "tool"
            and str(tool.get("name") or "") == "request_clarification"
        )

    def _duration_ms_iso(start: Any, end: Any) -> int | None:
        if not start or not end:
            return None
        try:
            from datetime import datetime

            def _parse(value: Any) -> datetime | None:
                if isinstance(value, datetime):
                    return value
                text = str(value).replace("Z", "+00:00")
                return datetime.fromisoformat(text)

            a = _parse(start)
            b = _parse(end)
            if a is None or b is None:
                return None
            return max(0, int((b - a).total_seconds() * 1000))
        except Exception:
            return None

    def _merge_group(group: list[dict[str, Any]]) -> dict[str, Any]:
        preferred: dict[str, Any] | None = None
        for status in ("completed", "running", "interrupted", "failed"):
            for item in reversed(group):
                if item.get("status") == status and item.get("kind") == "clarification":
                    preferred = dict(item)
                    break
            if preferred is not None:
                break
        if preferred is None:
            for item in reversed(group):
                if item.get("kind") == "clarification":
                    preferred = dict(item)
                    break
        if preferred is None:
            preferred = dict(group[-1])
            preferred["kind"] = "clarification"
            preferred["title_key"] = (
                preferred.get("title_key") or _KIND_TITLE_KEY["clarification"]
            )
        starts = [item.get("started_at") for item in group if item.get("started_at")]
        finishes = [
            item.get("finished_at") for item in group if item.get("finished_at")
        ]
        if starts:
            preferred["started_at"] = starts[0]
        if finishes:
            preferred["finished_at"] = finishes[-1]
        duration = _duration_ms_iso(
            preferred.get("started_at"), preferred.get("finished_at")
        )
        if duration is not None:
            preferred["duration_ms"] = duration
        if preferred.get("status") == "interrupted":
            # Clarification wait is expected; never surface as a crash after fold.
            preferred["status"] = "completed"
            preferred["summary_key"] = "chat.summary.clarification_confirmed"
        if preferred.get("status") == "running":
            preferred["summary_key"] = "chat.summary.clarification_waiting"
        elif preferred.get("status") == "completed" and preferred.get(
            "summary_key"
        ) in {
            None,
            "chat.audit.processing",
            "chat.audit.step_interrupted",
            "chat.summary.tool_ok",
        }:
            preferred["summary_key"] = "chat.summary.clarification_confirmed"
        preferred.pop("tool", None)
        # Prefer interrupt linkage / card payload from any clarification row.
        for item in reversed(group):
            meta = item.get("meta")
            if isinstance(meta, Mapping) and meta.get("interrupt_id"):
                preferred["meta"] = dict(meta)
                break
        return preferred

    out: list[dict[str, Any]] = []
    group: list[dict[str, Any]] = []

    def _flush() -> None:
        nonlocal group
        if group:
            out.append(_merge_group(group))
            group = []

    for raw in items:
        item = dict(raw)
        if _is_clarify_tool(item) or item.get("kind") == "clarification":
            group.append(item)
            continue
        _flush()
        out.append(item)
    _flush()
    return out


def load_result_datasets(session: Session, run_id: str) -> list[ResultDataset]:
    return list(
        session.exec(
            select(ResultDataset)
            .where(ResultDataset.run_id == run_id)
            .order_by(ResultDataset.create_time)
        ).scalars()
    )


def load_dataset_rows(
    session: Session,
    *,
    record_id: int,
    dataset_id: str,
    offset: int = 0,
    limit: int = 1000,
    user_id: int | None = None,
) -> dict[str, Any]:
    from apps.chat.plan_policy import ROW_LIMIT_MAX

    record = session.get(ChatRecord, record_id)
    if record is None:
        raise LookupError(f"ChatRecord {record_id} not found")
    if user_id is not None and int(record.create_by) != int(user_id):
        raise PermissionError("ChatRecord not owned by the current user")
    run_id = record.active_run_id
    if not run_id:
        raise LookupError("No active run for this record")
    row = (
        session.exec(
            select(ResultDataset).where(
                ResultDataset.run_id == run_id,
                ResultDataset.dataset_id == dataset_id,
            )
        )
        .scalars()
        .first()
    )
    if row is None:
        raise LookupError(f"dataset {dataset_id} not found")
    start = max(0, offset)
    end = start + max(1, min(int(limit), ROW_LIMIT_MAX))
    all_rows = list(row.rows or [])
    snapshot = row.schema_snapshot if isinstance(row.schema_snapshot, Mapping) else {}
    value_labels = (
        snapshot.get("value_labels") if isinstance(snapshot, Mapping) else None
    )
    payload: dict[str, Any] = {
        "dataset_id": row.dataset_id,
        "fields": list(row.fields or []),
        "rows": all_rows[start:end],
        "row_count": int(row.row_count or len(all_rows)),
        "truncated": bool(row.truncated),
        "offset": start,
        "limit": end - start,
    }
    if isinstance(value_labels, Mapping) and value_labels:
        payload["value_labels"] = value_labels
    return payload
