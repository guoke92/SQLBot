"""Shared text-turn history and terminal lifecycle nodes."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from sqlalchemy import and_, select

from apps.chat.models.chat_model import ChatRecord
from apps.conversation.outcome import (
    failed_outcome,
    outcome_from_steps,
    outcome_is_success,
    successful_outcome,
)
from apps.conversation.record import persist_snapshot
from apps.conversation.run_service import finalize_run
from apps.conversation.session import session_scope
from apps.conversation.sink import StreamSink


def load_text_history(
    session: Any,
    chat_id: int,
    *,
    limit: int = 8,
) -> list[BaseMessage]:
    """Load compact completed question/answer pairs for a text conversation."""
    rows = list(
        session.execute(
            select(ChatRecord)
            .where(
                and_(
                    ChatRecord.chat_id == chat_id,
                    ChatRecord.analysis_record_id.is_(None),
                    ChatRecord.predict_record_id.is_(None),
                    ChatRecord.finish.is_(True),
                    ChatRecord.error.is_(None),
                )
            )
            .order_by(ChatRecord.create_time.desc())
            .limit(limit)
        )
        .scalars()
        .all()
    )
    rows.reverse()
    messages: list[BaseMessage] = []
    for row in rows:
        if row.first_chat:
            continue
        question = (row.question or "").strip()
        answer = (row.sql_answer or "").strip()
        if not question or not answer:
            continue
        messages.append(HumanMessage(content=question))
        messages.append(AIMessage(content=answer))
    return messages


def finish_text_node(state: Mapping[str, Any]) -> dict[str, Any]:
    """Persist one plain-text assistant answer and close its chat record."""
    sink = StreamSink.from_state(state)
    record_id = state.get("record_id")
    final_text = str(state.get("final_text") or "")
    tool_steps = list(state.get("tool_steps") or [])
    outcome = outcome_from_steps(tool_steps) if tool_steps else successful_outcome()
    success = outcome_is_success(outcome)
    run_status: Literal["succeeded", "degraded", "failed"] = (
        "succeeded"
        if outcome["status"] == "success"
        else "degraded"
        if outcome["status"] == "degraded"
        else "failed"
    )
    failure_message = next(
        (
            str(item.get("message"))
            for item in reversed(outcome.get("failures") or [])
            if item.get("message")
        ),
        "Configuration operation failed",
    )
    if record_id:
        with session_scope() as session:
            if state.get("run_id"):
                finalize_run(
                    session,
                    run_id=str(state["run_id"]),
                    status=run_status,
                    current_node="finish",
                    record_snapshot={
                        "sql_answer": final_text or None,
                        "terminal": True,
                        "error": None if success else failure_message,
                    },
                    error_summary=None if success else failure_message,
                )
            else:
                persist_snapshot(
                    session,
                    record_id,
                    sql_answer=final_text or None,
                    terminal=True,
                    error=None if success else failure_message,
                )

    if sink.mode == "markdown" and final_text:
        sink.text(final_text)
    if sink.mode == "json":
        sink.json_result(
            {
                "success": success,
                "status": outcome["status"],
                "record_id": record_id,
                "content": final_text,
                **({"message": failure_message} if not success else {}),
            }
        )
    if success:
        sink.event({"type": "finish", "id": record_id})
    else:
        sink.error(failure_message)
    return {**state, "outcome": outcome}


def persist_turn_failure(record_id: int, error: str) -> None:
    """Persist one terminal error through the idempotent lifecycle boundary."""
    with session_scope() as session:
        persist_snapshot(session, record_id, terminal=True, error=error)


def fail_node(state: Mapping[str, Any]) -> dict[str, Any]:
    """Emit and persist the shared terminal failure behavior."""
    sink = StreamSink.from_state(state)
    error = str(state.get("error") or "unknown error")
    record_id = state.get("record_id")
    if record_id and state.get("run_id"):
        with session_scope() as session:
            finalize_run(
                session,
                run_id=str(state["run_id"]),
                status="failed",
                current_node="fail",
                record_snapshot={"terminal": True, "error": error},
                error_summary=error,
            )
    elif record_id:
        persist_turn_failure(int(record_id), error)
    sink.error(error)
    current = state.get("outcome")
    if not current or current.get("status") == "running":
        current = failed_outcome(error)
    return {
        **state,
        "outcome": current,
    }
