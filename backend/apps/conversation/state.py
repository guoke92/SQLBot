"""Shared run-state keys for graph scenarios.

Scenario graphs may extend these fields via their own TypedDict; common keys
live here so sinks / runtime / record helpers share one vocabulary.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, TypedDict

from apps.conversation.outcome import RunOutcome
from apps.conversation.sink import SinkMode

RunMode = Literal["primary", "follow_up", "side"]


class RunState(TypedDict, total=False):
    """Minimal shared state every graph may read/write.

    Scenario-specific objects (e.g. llm step library handle) may appear as extra
    keys on the concrete graph state; ``extras`` remains for free-form payload.
    """

    graph_key: str
    run_id: str
    mode: RunMode
    sink: SinkMode
    chat_id: int
    record_id: int
    base_record_id: Optional[int]
    user_id: int
    oid: int
    question: str
    messages: List[Dict[str, Any]]
    full_text: str
    error: str
    public_error: str
    outcome: RunOutcome
    tool_steps: List[Dict[str, Any]]
    # call_id → open ChatLog id; LangGraph drops undeclared keys across nodes
    open_tool_spans: Dict[str, int]
    extras: Dict[str, Any]
