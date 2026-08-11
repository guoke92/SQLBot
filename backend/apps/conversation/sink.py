"""Parameterized stream sink for graph nodes (one place for SSE / MCP / JSON).

Sink is a *render strategy*, not a second event-type system:
- ``sse``      — FE contract ``data:{json}\\n\\n`` via ``emit``
- ``markdown`` — MCP streaming text
- ``json``     — MCP non-stream; final object only

Nodes emit domain payloads through StreamSink; they must not branch on
``in_chat`` / ``stream`` ad hoc, and must not hand-build SSE frames.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping
from typing import Any, Literal

import orjson
from langgraph.config import get_stream_writer

from apps.conversation.events import emit

SinkMode = Literal["sse", "markdown", "json"]


def resolve_sink(*, in_chat: bool = True, stream: bool = True) -> SinkMode:
    """Map historic ``in_chat`` / ``stream`` flags to the single sink mode."""
    if in_chat:
        return "sse"
    return "markdown" if stream else "json"


class StreamSink:
    """Write domain events to LangGraph custom stream under one render mode."""

    def __init__(self, mode: SinkMode = "sse", *, run_id: str | None = None) -> None:
        if mode not in ("sse", "markdown", "json"):
            raise ValueError(f"unsupported sink mode: {mode!r}")
        self.mode: SinkMode = mode
        self.run_id = run_id
        self._token_buffers: dict[str, dict[str, Any]] = {}

    @classmethod
    def from_state(cls, state: Mapping[str, Any]) -> StreamSink:
        mode = state.get("sink")
        if mode in ("sse", "markdown", "json"):
            return cls(mode, run_id=str(state.get("run_id") or "") or None)
        return cls(
            resolve_sink(
                in_chat=bool(state.get("in_chat", True)),
                stream=bool(state.get("stream", True)),
            ),
            run_id=str(state.get("run_id") or "") or None,
        )

    # ---- low-level -------------------------------------------------------

    def _raw(self, chunk: Any) -> None:
        get_stream_writer()(chunk)

    # ---- domain writes ---------------------------------------------------

    def _emit_event(self, payload: Mapping[str, Any]) -> None:
        event = dict(payload)
        if self.run_id:
            from apps.conversation.run_service import append_run_event
            from apps.conversation.session import session_scope

            with session_scope() as session:
                cursor = append_run_event(
                    session,
                    run_id=self.run_id,
                    payload=event,
                )
            if cursor:
                event["cursor"] = cursor
                event["run_id"] = self.run_id
        self._raw(emit(event))

    def flush_tokens(self) -> None:
        """Persist buffered token deltas as coarse-grained run events."""
        pending = list(self._token_buffers.values())
        self._token_buffers.clear()
        for event in pending:
            self._emit_event(event)

    def event(self, payload: Mapping[str, Any]) -> None:
        """Emit a typed FE event (only active in ``sse`` mode)."""
        if self.mode == "sse":
            self.flush_tokens()
            self._emit_event(payload)

    def awaiting_input(self, payload: Mapping[str, Any]) -> None:
        """Render one durable interrupt for every supported transport.

        Interactive web clients receive the normal event. MCP streaming and
        JSON clients receive an actionable representation instead of an empty
        response that is later mistaken for a failed query.
        """
        interrupt_payload = {
            "status": "awaiting_input",
            "run_id": self.run_id,
            "interrupt": dict(payload),
        }
        if self.mode == "sse":
            self.event({"type": "clarification", **dict(payload)})
        elif self.mode == "markdown":
            rendered = orjson.dumps(
                interrupt_payload, option=orjson.OPT_INDENT_2, default=str
            ).decode()
            self._raw(
                "需要补充业务口径后才能继续查询。请使用返回的 run_id 和 "
                "interrupt 信息恢复本次运行。\n\n```json\n"
                f"{rendered}\n```\n"
            )
        else:
            self.json_result({"success": True, **interrupt_payload})

    def text(self, content: str) -> None:
        """Write plain markdown/text (only active in ``markdown`` mode)."""
        if self.mode == "markdown" and content:
            self._raw(content)

    def json_result(self, payload: Mapping[str, Any]) -> None:
        """Write final JSON payload (only active in ``json`` mode)."""
        if self.mode == "json":
            self._raw(dict(payload))

    def record_header(self, *, record_id: int, question: str | None, prefix: str) -> None:
        """MCP preface lines; no-op for sse; for json only stamps record_id externally."""
        if self.mode == "markdown":
            self._raw(f"> {prefix}{record_id}\n")
            self._raw(f"> {(question or '')}\n\n")

    def token(
        self,
        *,
        content: str | None = None,
        reasoning_content: str | None = None,
        event_type: str,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        """Stream one LLM token chunk."""
        if self.mode == "sse":
            metadata = dict(metadata or {})
            buffer_key = event_type + ":" + repr(sorted(metadata.items()))
            current = self._token_buffers.setdefault(
                buffer_key,
                {
                    "type": event_type,
                    **metadata,
                    "content": "",
                    "reasoning_content": "",
                },
            )
            current["content"] += content or ""
            current["reasoning_content"] += reasoning_content or ""
            if len(current["content"]) + len(current["reasoning_content"]) >= 512:
                event = self._token_buffers.pop(buffer_key)
                self._emit_event(event)
        elif self.mode == "markdown":
            self.text(content or "")

    def error(self, message: str) -> None:
        """Write a terminal error under the active sink mode (in-node)."""
        if self.mode == "sse":
            self.event({"content": message, "type": "error"})
        elif self.mode == "markdown":
            self._raw("&#x274c; **ERROR:**\n")
            self._raw(f"> {message}\n")
        else:
            self._raw(
                {
                    "success": False,
                    "status": "failed",
                    "message": message,
                }
            )

    def error_chunks(self, message: str) -> Iterator[Any]:
        """Outside graph nodes (submit_graph top-level) — yield same shapes."""
        if self.mode == "sse":
            yield emit({"content": message, "type": "error"})
        elif self.mode == "markdown":
            yield "&#x274c; **ERROR:**\n"
            yield f"> {message}\n"
        else:
            yield {
                "success": False,
                "status": "failed",
                "message": message,
            }


def sink_error_chunks(ctx: Mapping[str, Any], message: str) -> Iterable[Any]:
    """Helper used by ``submit_graph`` when a graph raises before/around nodes."""
    return StreamSink.from_state(ctx).error_chunks(message)
