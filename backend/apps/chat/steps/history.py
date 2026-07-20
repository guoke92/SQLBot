"""Conversation history helpers for prompt assembly (domain atom)."""

from __future__ import annotations

from typing import Any, List

from common.core.config import settings


def get_last_conversation_rounds(
    messages: List[dict[str, Any]] | None,
    rounds: int = settings.GENERATE_SQL_QUERY_HISTORY_ROUND_COUNT,
) -> List[dict[str, Any]]:
    """Return the last N human-led dialogue rounds, tolerating truncated logs."""
    if not messages or rounds <= 0:
        return []

    human_indices = [
        index for index, msg in enumerate(messages) if msg.get("type") == "human"
    ]
    if not human_indices:
        return []

    if len(human_indices) <= rounds:
        start_index = human_indices[0]
    else:
        start_index = human_indices[-rounds]

    return messages[start_index:]
