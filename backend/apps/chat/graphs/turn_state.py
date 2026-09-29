"""Canonical checkpoint state for the production chat agent graph."""

from __future__ import annotations

import traceback
from collections.abc import Mapping
from typing import Any, Literal, cast

from apps.chat.task.llm import LLMService
from apps.conversation.outcome import (
    RunOutcome,
    failed_outcome,
    format_error_message,
    public_error_message,
)
from apps.conversation.run_service import ConversationRunCancelled
from apps.conversation.runtime_context import runtime_value
from apps.conversation.state import RunState


class ChatTurnState(RunState, total=False):
    """JSON-only graph state for graphs/current/chat.yaml."""

    turn_route: dict[str, Any]
    referenced_turns: list[dict[str, Any]]
    prior_user_evidence: list[dict[str, Any]]
    source_datasets: list[dict[str, Any]]
    data_strategy: Literal[
        "direct_query", "existing_results", "derived_query", "unavailable"
    ]
    business_now: str
    timezone: str
    context_fingerprint: str
    terminal_answer: dict[str, Any]
    json_result: dict[str, Any]
    knowledge_plane: dict[str, Any]
    probe_sql_calls: int
    memory_slots: dict[str, Any]
    bound_tools: list[Any]
    final_text: str
    turn_message_start: int
    agent_transcript_saved: bool
    tool_rounds: int
    tool_round_limit: int
    tool_stop_reason: str
    last_tool_failure_signature: str
    consecutive_tool_failures: int
    analysis_incomplete: bool
    ai_modal_id: Any
    ai_modal_name: str
    reference_record_ids: list[int]
    route_hint: str
    execution_mode: Literal["verified", "unverified", "agent"]


def llm_service(state: Mapping[str, Any]) -> LLMService:
    return cast(LLMService, runtime_value(state, "llm_service"))


def fail_turn_state(
    state: Mapping[str, Any], _record_id: int | None, exc: BaseException
) -> dict[str, Any]:
    if isinstance(exc, ConversationRunCancelled):
        raise exc
    traceback.print_exc()
    error_msg = format_error_message(exc)
    return {
        **dict(state),
        "error": error_msg,
        "public_error": public_error_message(exc),
        "outcome": failed_outcome(exc),
    }
