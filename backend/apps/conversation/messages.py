"""Shared normalization for provider-specific model message content."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from langchain_core.messages import BaseMessage, messages_from_dict, messages_to_dict


def message_content_text(content: Any) -> str:
    """Extract visible text from string or structured content blocks."""
    if isinstance(content, str):
        return content
    if isinstance(content, Mapping):
        text = content.get("text")
        return text if isinstance(text, str) else ""
    if isinstance(content, Sequence) and not isinstance(content, (str, bytes)):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
                continue
            if isinstance(item, Mapping):
                text = item.get("text")
                if isinstance(text, str):
                    parts.append(text)
        return "".join(parts)
    return str(content or "")


def serialize_messages(messages: Sequence[BaseMessage]) -> list[dict[str, Any]]:
    """Store LangChain messages as plain checkpoint-safe dictionaries."""
    return messages_to_dict(list(messages))


def deserialize_messages(values: Sequence[Any]) -> list[BaseMessage]:
    """Accept canonical dictionaries and tolerate objects in non-durable graphs."""
    objects = [value for value in values if isinstance(value, BaseMessage)]
    if len(objects) == len(values):
        return objects
    dictionaries = [value for value in values if isinstance(value, dict)]
    if len(dictionaries) != len(values):
        raise TypeError("Conversation messages must be serialized message dictionaries")
    return messages_from_dict(dictionaries)
