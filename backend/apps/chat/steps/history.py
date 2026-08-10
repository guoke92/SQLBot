"""Conversation history helpers for prompt assembly (domain atom)."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from common.core.config import settings


def extract_prompt_messages(payload: object) -> list[dict[str, Any]]:
    """Return only chat messages that are safe to replay to a model.

    ``chat_log.messages`` is also the audit payload for local graph spans.  A
    deterministic SQL compilation therefore stores a mapping rather than an
    LLM message list.  Audit payloads must remain visible in execution details,
    but they are not conversation history and must never block a later turn.
    """
    if not isinstance(payload, list):
        return []

    return [
        message
        for message in payload
        if isinstance(message, dict)
        and message.get("sqlbot_system") is not True
        and message.get("type") in {"human", "ai"}
        and message.get("content") is not None
    ]


def select_prompt_history(
    logs: Sequence[Any], *, record_id: int | None = None
) -> list[dict[str, Any]]:
    """Select one generation log and project it to replayable prompt history."""
    selected = next(
        (
            log
            for log in reversed(logs)
            if record_id is None or getattr(log, "pid", None) == record_id
        ),
        None,
    )
    return extract_prompt_messages(getattr(selected, "messages", None))


def get_last_conversation_rounds(
    messages: object,
    rounds: int = settings.GENERATE_SQL_QUERY_HISTORY_ROUND_COUNT,
) -> list[dict[str, Any]]:
    """Return the last N human-led dialogue rounds, tolerating truncated logs."""
    prompt_messages = extract_prompt_messages(messages)
    if not prompt_messages or rounds <= 0:
        return []

    human_indices = [
        index
        for index, msg in enumerate(prompt_messages)
        if msg.get("type") == "human"
    ]
    if not human_indices:
        return []

    if len(human_indices) <= rounds:
        start_index = human_indices[0]
    else:
        start_index = human_indices[-rounds]

    return prompt_messages[start_index:]
