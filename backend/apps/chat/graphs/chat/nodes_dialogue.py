"""Target dialogue-path nodes — architecture stubs.

These are real callables that satisfy LangGraph compilation. Product logic
(Working Set, dialogue LLM, RepairBrief) will be filled in a later PR.
Each node prints a stub marker so test harnesses can verify the path is
traversable without side effects.
"""

from __future__ import annotations

from typing import Any, Dict, Literal

from apps.conversation.state import RunState
from apps.conversation.sink import StreamSink
from common.utils.utils import SQLBotLogUtil


# Re-use ChatState from the sibling module for TypedDict compatibility.
from apps.chat.graphs.chat.state import ChatState


def prepare_turn_node(state: ChatState) -> ChatState:
    """Hydrate turn-level state (record, LLM service). Shared entry."""
    return {**state, "mode": "primary"}


def hydrate_working_set_node(state: ChatState) -> ChatState:
    """Load Working Set context for multi-turn continuity.

    Stub: no-op pass-through. Future impl will hydrate anchor / evidence.
    """
    SQLBotLogUtil.info("[target-stub] hydrate_working_set: no-op")
    return state


def route_turn_node(state: ChatState) -> ChatState:
    """Turn router — pass-through; the router function does the branching.

    This node is a no-op sink; the conditional edge ``route_turn`` reads
    ``state["intent"]`` (set by the caller / TurnRouter LLM) to select the path.
    """
    return state


def route_after_turn(state: ChatState) -> Literal["nlq_new", "explain", "critique", "clarify", "fail"]:
    """Read state.intent and route to the correct path.

    Stub: defaults to ``nlq_new`` when intent is unset.
    """
    intent = str(state.get("intent") or "nlq_new").strip()
    if state.get("error"):
        return "fail"
    # Map intent families → path entry nodes
    if intent.startswith("explain") or intent in ("critique", "clarify"):
        return "explain"
    # All SQL-generating intents go through nlq_new
    return "nlq_new"


def dlg_resolve_anchor_node(state: ChatState) -> ChatState:
    """Validate that a multi-turn anchor exists in the Working Set.

    Stub: pass-through; future impl will set error if anchor is stale/missing.
    """
    SQLBotLogUtil.info("[target-stub] dlg_resolve_anchor: pass-through")
    return state


def dlg_load_evidence_node(state: ChatState) -> ChatState:
    """Load evidence / prior SQL+result context into state.evidence.

    Stub: sets empty evidence block.
    """
    return {**state, "evidence": state.get("evidence") or {}}


def dlg_reason_node(state: ChatState) -> ChatState:
    """Run dialogue LLM to generate diagnosis.

    Stub: writes a placeholder diagnosis structure.
    """
    return {
        **state,
        "diagnosis": state.get("diagnosis") or {"kind": "stub", "detail": "dialogue not yet implemented"},
    }


def dlg_synthesize_node(state: ChatState) -> ChatState:
    """Stream or write the dialogue response to the user.

    Stub: emits a placeholder message via sink.
    """
    sink = StreamSink.from_state(state)
    diagnosis = state.get("diagnosis") or {}
    detail = diagnosis.get("detail", "dialogue response placeholder")
    sink.event({"type": "message", "content": detail})
    sink.text(detail + "\n\n")
    return state


def dlg_maybe_repair_brief_node(state: ChatState) -> ChatState:
    """Optionally write a RepairBrief for the next NLQ turn.

    Stub: no-op pass-through.
    """
    return state


def dlg_complete_node(state: ChatState) -> ChatState:
    """Dialogue path finish — emit finish event."""
    sink = StreamSink.from_state(state)
    sink.event({"type": "finish"})
    return state


def finalize_turn_node(state: ChatState) -> ChatState:
    """Shared tail — emit finish / JSON for paths that haven't already."""
    sink = StreamSink.from_state(state)
    json_result = state.get("json_result") or {}
    if sink.mode == "json":
        sink.json_result(json_result)
    return state
