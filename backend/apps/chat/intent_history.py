"""Persistence queries for semantic-intent conversation history."""

from __future__ import annotations

import orjson
from sqlalchemy import select
from sqlmodel import Session

from apps.chat.answer_payload import is_answer_payload
from apps.chat.models.chat_model import ChatRecord
from apps.chat.semantic_intent import is_current_intent_payload


def _has_reusable_outcome(record: ChatRecord) -> bool:
    context = record.intent_context
    if (
        not is_current_intent_payload(context)
        or context.get("status") != "ready"
    ):
        return False
    if not (context.get("contract") or {}).get("requirements"):
        return False
    try:
        payload = orjson.loads(record.data or "")
    except (TypeError, ValueError):
        return False
    if not is_answer_payload(payload):
        return False
    outcome = payload.get("outcome") or {}
    return outcome.get("status") in {"success", "degraded"}


def latest_reusable_intent_record(
    session: Session,
    *,
    chat_id: int,
    user_id: int,
) -> ChatRecord | None:
    """Return the latest completed answer whose intent can be refined."""
    statement = (
        select(ChatRecord)
        .where(
            ChatRecord.chat_id == chat_id,
            ChatRecord.create_by == user_id,
            ChatRecord.finish.is_(True),
            ChatRecord.sql.is_not(None),
            ChatRecord.data.is_not(None),
            ChatRecord.error.is_(None),
        )
        .order_by(ChatRecord.id.desc())
    )
    for record in session.execute(statement).scalars():
        if _has_reusable_outcome(record):
            return record
    return None
