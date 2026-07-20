"""Parameterized stream sink for graph nodes (one place for SSE / MCP / JSON).

Sink is a *render strategy*, not a second event-type system:
- ``sse``      — FE contract ``data:{json}\\n\\n`` via ``emit``
- ``markdown`` — MCP streaming text
- ``json``     — MCP non-stream; final object only

Nodes emit domain payloads through StreamSink; they must not branch on
``in_chat`` / ``stream`` ad hoc, and must not hand-build SSE frames.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, Iterator, Literal, Mapping, Optional

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

    def __init__(self, mode: SinkMode = "sse") -> None:
        if mode not in ("sse", "markdown", "json"):
            raise ValueError(f"unsupported sink mode: {mode!r}")
        self.mode: SinkMode = mode

    @classmethod
    def from_state(cls, state: Mapping[str, Any]) -> "StreamSink":
        mode = state.get("sink")
        if mode in ("sse", "markdown", "json"):
            return cls(mode)
        return cls(
            resolve_sink(
                in_chat=bool(state.get("in_chat", True)),
                stream=bool(state.get("stream", True)),
            )
        )

    # ---- low-level -------------------------------------------------------

    def _raw(self, chunk: Any) -> None:
        get_stream_writer()(chunk)

    # ---- domain writes ---------------------------------------------------

    def event(self, payload: Mapping[str, Any]) -> None:
        """Emit a typed FE event (only active in ``sse`` mode)."""
        if self.mode == "sse":
            self._raw(emit(dict(payload)))

    def text(self, content: str) -> None:
        """Write plain markdown/text (only active in ``markdown`` mode)."""
        if self.mode == "markdown" and content:
            self._raw(content)

    def json_result(self, payload: Mapping[str, Any]) -> None:
        """Write final JSON payload (only active in ``json`` mode)."""
        if self.mode == "json":
            self._raw(dict(payload))

    def record_header(self, *, record_id: int, question: Optional[str], prefix: str) -> None:
        """MCP preface lines; no-op for sse; for json only stamps record_id externally."""
        if self.mode == "markdown":
            self._raw(f"> {prefix}{record_id}\n")
            self._raw(f"> {(question or '')}\n\n")

    def token(
        self,
        *,
        content: Optional[str] = None,
        reasoning_content: Optional[str] = None,
        event_type: str,
    ) -> None:
        """Stream one LLM token chunk."""
        if self.mode == "sse":
            self.event(
                {
                    "type": event_type,
                    "content": content,
                    "reasoning_content": reasoning_content,
                }
            )
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
            self._raw({"success": False, "message": message})

    def error_chunks(self, message: str) -> Iterator[Any]:
        """Outside graph nodes (submit_graph top-level) — yield same shapes."""
        if self.mode == "sse":
            yield emit({"content": message, "type": "error"})
        elif self.mode == "markdown":
            yield "&#x274c; **ERROR:**\n"
            yield f"> {message}\n"
        else:
            yield {"success": False, "message": message}


def sink_error_chunks(ctx: Mapping[str, Any], message: str) -> Iterable[Any]:
    """Helper used by ``submit_graph`` when a graph raises before/around nodes."""
    return StreamSink.from_state(ctx).error_chunks(message)
