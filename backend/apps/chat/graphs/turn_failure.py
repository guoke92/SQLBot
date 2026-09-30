"""Terminal failure node for the production chat agent graph."""

from __future__ import annotations

import traceback
from collections.abc import Mapping
from typing import Any, Literal, cast

from apps.chat.curd.chat import rename_chat
from apps.chat.graphs.turn_snapshot import record_snapshot_values
from apps.chat.models.chat_model import RenameChat
from apps.chat.result_quality import build_overall_quality
from apps.conversation.outcome import (
    RunOutcome,
    failed_outcome,
)
from apps.conversation.run_service import finalize_run
from apps.conversation.session import session_scope
from apps.conversation.sink import StreamSink
from common.utils.utils import SQLBotLogUtil


def _generation_question(llm_service: Any) -> str:
    projected = str(getattr(llm_service, "generation_question", "") or "").strip()
    if projected:
        return projected
    question = getattr(llm_service, "chat_question", None)
    return str(
        getattr(question, "generation_question", "")
        or getattr(question, "question", "")
        or ""
    ).strip()


def update_chat_brief(llm_service: Any, sink: StreamSink, title: str) -> None:
    """Write sidebar title once per chat."""
    if not getattr(llm_service, "change_title", False):
        return
    title = (title or "").replace(chr(10), " ").replace(chr(13), " ").strip()[:20]
    if not title:
        title = _generation_question(llm_service)[:20]
    if not title or not llm_service.record or not llm_service.record.chat_id:
        return
    try:
        with session_scope() as session:
            rename_chat(
                session,
                RenameChat(
                    id=llm_service.record.chat_id,
                    brief=title,
                    brief_generate=True,
                ),
            )
        sink.event({"type": "brief", "brief": title})
        llm_service.change_title = False
    except Exception:
        traceback.print_exc()


def persist_query_terminal_failure(
    state: Mapping[str, Any],
    *,
    error_summary: str,
    public_error: str | None,
    current_node: str | None = None,
    failure_code: str | None = None,
    failure_retryable: bool = True,
    outcome: RunOutcome | None = None,
) -> RunOutcome:
    """Persist one canonical failed query answer at a terminal boundary."""
    terminal_outcome = outcome or failed_outcome(error_summary)
    if "quality" not in terminal_outcome:
        terminal_outcome["quality"] = build_overall_quality([])
    route = (
        state.get("turn_route") if isinstance(state.get("turn_route"), Mapping) else {}
    )
    snapshot_kind = str(route.get("task_kind") or "query")
    try:
        with session_scope() as session:
            finalize_run(
                session,
                run_id=str(state["run_id"]),
                status="failed",
                current_node=current_node,
                result_quality=terminal_outcome.get("quality"),
                record_snapshot=record_snapshot_values(
                    [],
                    "",
                    finish=True,
                    outcome=terminal_outcome,
                    public_error=public_error,
                    failure_code=failure_code,
                    failure_retryable=failure_retryable,
                    execution_mode=cast(
                        Literal["verified", "unverified", "agent"],
                        state.get("execution_mode") or "agent",
                    ),
                    kind=snapshot_kind,
                ),
                error_summary=error_summary,
                error_visibility="public" if public_error is not None else "sanitize",
            )
    except Exception as exc:
        SQLBotLogUtil.error(f"persist query failure snapshot failed: {exc}")
    return terminal_outcome


def fail_node(state: Mapping[str, Any]) -> dict[str, Any]:
    """Delegate to the product-agent delivery fail node (single salvage predicate)."""
    from apps.chat.agent.delivery import fail_node as _fail

    return _fail(state)
