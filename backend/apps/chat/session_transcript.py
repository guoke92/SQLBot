"""Chat-scoped agent transcript load/append. Folding is applied at read time."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from sqlalchemy.orm import Session

from apps.chat.turn_fold import (
    DEFAULT_KEEP_TURNS,
    DEFAULT_TOKEN_BUDGET,
    estimate_tokens,
    fold_history,
)
from apps.conversation.messages import deserialize_messages, serialize_messages
from common.utils.utils import SQLBotLogUtil


def _token_budget() -> int:
    try:
        from common.core.config import settings

        return int(
            getattr(settings, "AGENT_TRANSCRIPT_TOKEN_BUDGET", DEFAULT_TOKEN_BUDGET)
            or DEFAULT_TOKEN_BUDGET
        )
    except Exception:
        return DEFAULT_TOKEN_BUDGET


def _keep_turns() -> int:
    try:
        from common.core.config import settings

        return int(
            getattr(settings, "AGENT_TRANSCRIPT_KEEP_TURNS", DEFAULT_KEEP_TURNS)
            or DEFAULT_KEEP_TURNS
        )
    except Exception:
        return DEFAULT_KEEP_TURNS


def empty_transcript() -> dict[str, Any]:
    return {"messages": [], "folds": []}


def load_agent_transcript(session: Session, chat_id: int) -> list[BaseMessage]:
    from apps.chat.models.chat_model import Chat

    chat = session.get(Chat, int(chat_id))
    if chat is None:
        return []
    raw = getattr(chat, "agent_transcript", None)
    if not isinstance(raw, Mapping):
        return []
    stored = raw.get("messages") or []
    if not stored:
        return []
    try:
        from apps.conversation.messages import sanitize_for_checkpoint

        return deserialize_messages(sanitize_for_checkpoint(list(stored)))
    except Exception as exc:
        SQLBotLogUtil.warning(
            f"agent_transcript deserialize failed chat={chat_id}: {exc}"
        )
        return []


def append_agent_transcript(
    session: Session, chat_id: int, messages: Sequence[BaseMessage]
) -> dict[str, Any]:
    from apps.chat.models.chat_model import Chat

    chunk = [message for message in messages if not isinstance(message, SystemMessage)]
    if not chunk:
        return empty_transcript()
    chat = session.get(Chat, int(chat_id))
    if chat is None:
        return empty_transcript()
    raw = (
        dict(chat.agent_transcript or {})
        if isinstance(chat.agent_transcript, Mapping)
        else {}
    )
    existing = list(raw.get("messages") or [])
    existing.extend(serialize_messages(chunk))
    payload = {
        "messages": existing,
        "folds": list(raw.get("folds") or []),
    }
    chat.agent_transcript = payload
    session.add(chat)
    return payload


def persist_turn_from_state(state: Mapping[str, Any]) -> bool:
    """Append this turn's raw messages onto chat.agent_transcript.

    Returns True when this turn is already persisted or was just written.
    """
    if state.get("agent_transcript_saved"):
        return True
    chat_id = state.get("chat_id")
    start = state.get("turn_message_start")
    if chat_id is None or start is None:
        return False
    messages = deserialize_messages(list(state.get("messages") or []))
    chunk = [
        item for item in messages[int(start) :] if not isinstance(item, SystemMessage)
    ]
    if not chunk:
        return False
    from apps.conversation.session import session_scope

    with session_scope() as session:
        append_agent_transcript(session, int(chat_id), chunk)
        session.commit()
    return True


def save_fold_meta(
    session: Session, chat_id: int, folds: Sequence[Mapping[str, Any]]
) -> None:
    from apps.chat.models.chat_model import Chat

    chat = session.get(Chat, int(chat_id))
    if chat is None:
        return
    raw = (
        dict(chat.agent_transcript or {})
        if isinstance(chat.agent_transcript, Mapping)
        else {}
    )
    raw["messages"] = list(raw.get("messages") or [])
    raw["folds"] = [dict(item) for item in folds]
    chat.agent_transcript = raw
    session.add(chat)


def build_continued_messages(
    *,
    history: Sequence[BaseMessage],
    question: str,
    knowledge_plane: Any = None,
    token_budget: int | None = None,
    keep_turns: int | None = None,
) -> tuple[list[BaseMessage], int, list[dict[str, Any]]]:
    """Stable System + folded history + current Human. Returns start index of this turn."""
    from apps.chat.task.agent_prompt import build_agent_system_prompt

    system = SystemMessage(
        content=build_agent_system_prompt(knowledge_plane=knowledge_plane)
    )
    human = HumanMessage(content=question)
    budget = int(token_budget if token_budget is not None else _token_budget())
    keep = int(keep_turns if keep_turns is not None else _keep_turns())
    folded, folds = fold_history(
        list(history),
        token_budget=budget,
        keep_turns=keep,
        extra_tokens=estimate_tokens([system, human]),
    )
    messages = [system, *folded, human]
    from apps.conversation.tooling import sanitize_messages_for_model

    # History may contain invalid_tool_calls / unanswered tool_calls from a
    # failed turn. Responses API rejects those as orphan function_call items.
    return sanitize_messages_for_model(messages), len(messages) - 1, folds
