"""Single write path for AgentKnowledgePlane (checkpoint is the durable copy).

Tools stage a working copy; the tool runtime publishes once after the batch
joins. The process bag is a cache of the checkpoint, not a second writer.
"""

from __future__ import annotations

from collections.abc import Mapping
from contextvars import ContextVar
from typing import Any

from apps.chat.agent_knowledge import AgentKnowledgePlane
from apps.conversation.runtime_context import (
    attach_runtime,
    current_worker_identity,
    peek_runtime,
)

_working: ContextVar[dict[str, Any] | None] = ContextVar(
    "agent_knowledge_working", default=None
)


def load_plane(state: Mapping[str, Any] | None = None) -> AgentKnowledgePlane:
    working = _working.get()
    if working:
        return AgentKnowledgePlane.from_dump(working)
    run_id, _token = current_worker_identity()
    snap: dict[str, Any] = {}
    if run_id:
        snap = peek_runtime(run_id) or {}
    raw = snap.get("knowledge_plane")
    if not raw and state is not None:
        raw = state.get("knowledge_plane")
    return AgentKnowledgePlane.from_dump(raw if isinstance(raw, Mapping) else None)


def stage_plane(plane: AgentKnowledgePlane) -> AgentKnowledgePlane:
    """Record a working copy for this tool call. Does not touch the run bag."""
    dump = plane.to_dump()
    _working.set(dump)
    return plane


def take_working() -> dict[str, Any] | None:
    dump = _working.get()
    _working.set(None)
    return dict(dump) if dump else None


def publish_plane(plane: AgentKnowledgePlane) -> AgentKnowledgePlane:
    """Sole attach_runtime writer for knowledge_plane."""
    run_id, _token = current_worker_identity()
    dump = plane.to_dump()
    if run_id:
        attach_runtime(run_id, knowledge_plane=dump)
    _working.set(None)
    return plane


def merge_published(*dumps: Mapping[str, Any] | None) -> AgentKnowledgePlane:
    acc: dict[str, Any] = {}
    for dump in dumps:
        if not dump:
            continue
        acc = _merge_dumps(acc, dict(dump)) if acc else dict(dump)
    return AgentKnowledgePlane.from_dump(acc or None)


def cache_from_state(state: Mapping[str, Any]) -> None:
    """Refresh the process cache from checkpoint at node entry. Not a second writer."""
    run_id, _token = current_worker_identity()
    if not run_id:
        run_id = str(state.get("run_id") or "")
    if not run_id:
        return
    dump = dict(state.get("knowledge_plane") or {})
    attach_runtime(
        run_id,
        knowledge_plane=dump,
        probe_sql_calls=int(state.get("probe_sql_calls") or 0),
        tool_steps=list(state.get("tool_steps") or []),
        messages=list(state.get("messages") or []),
        turn_message_start=state.get("turn_message_start"),
        turn_delivery=dict(state.get("turn_delivery") or {}),
    )
    _working.set(None)


def _merge_dumps(base: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    out.update(incoming)
    out["excluded"] = list(
        dict.fromkeys(
            [*(base.get("excluded") or []), *(incoming.get("excluded") or [])]
        )
    )
    for key in ("tables", "page_keys"):
        merged_list = list(
            dict.fromkeys([*(base.get(key) or []), *(incoming.get(key) or [])])
        )
        if key == "tables":
            blocked = {str(item) for item in out.get("excluded") or []}
            merged_list = [item for item in merged_list if str(item) not in blocked]
        out[key] = merged_list
    for key in ("schema_by_table", "keep_fields"):
        merged = dict(base.get(key) or {})
        merged.update(incoming.get(key) or {})
        out[key] = merged
    outline = str(incoming.get("schema_outline") or "").strip()
    if outline:
        out["schema_outline"] = outline
    elif base.get("schema_outline"):
        out["schema_outline"] = base["schema_outline"]
    out["knowledge_rounds"] = max(
        int(base.get("knowledge_rounds") or 0),
        int(incoming.get("knowledge_rounds") or 0),
    )
    return out
