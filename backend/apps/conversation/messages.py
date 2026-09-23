"""Shared normalization for provider-specific model message content."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from langchain_core.messages import BaseMessage, messages_from_dict, messages_to_dict


def _is_reasoning_block(block: Mapping[str, Any]) -> bool:
    return str(block.get("type") or "") == "reasoning"


def _looks_like_envelope_text(text: str) -> bool:
    stripped = text.strip()
    if "encrypted_content" not in stripped:
        return False
    return "'type': 'reasoning'" in stripped or '"type": "reasoning"' in stripped


def _text_from_nested(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, Mapping):
        text = value.get("text")
        return text if isinstance(text, str) else ""
    if isinstance(value, Sequence) and not isinstance(value, str | bytes):
        parts: list[str] = []
        for item in value:
            extracted = _text_from_nested(item)
            if extracted:
                parts.append(extracted)
        return "".join(parts)
    return ""


def reasoning_text_from_value(value: Any) -> str:
    """Visible thought text only — never serialized reasoning envelopes."""
    if value is None or isinstance(value, bool):
        return ""
    if isinstance(value, str):
        return "" if _looks_like_envelope_text(value) else value
    if isinstance(value, Mapping):
        return _reasoning_from_block(value)
    if isinstance(value, Sequence) and not isinstance(value, str | bytes):
        parts: list[str] = []
        for item in value:
            extracted = reasoning_text_from_value(item)
            if extracted:
                parts.append(extracted)
        return "".join(parts)
    return ""


def message_content_text(content: Any) -> str:
    """Extract visible text from string or structured content blocks."""
    if isinstance(content, str):
        return content
    if isinstance(content, Mapping):
        if _is_reasoning_block(content) or "encrypted_content" in content:
            return ""
        text = content.get("text")
        return text if isinstance(text, str) else ""
    if isinstance(content, Sequence) and not isinstance(content, str | bytes):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
                continue
            if isinstance(item, Mapping):
                if _is_reasoning_block(item) or "encrypted_content" in item:
                    continue
                text = item.get("text")
                if isinstance(text, str):
                    parts.append(text)
        return "".join(parts)
    return str(content or "")


def message_reasoning_text(content: Any) -> str:
    """Extract thought text from Responses-style reasoning content blocks."""
    if isinstance(content, str):
        return ""
    return reasoning_text_from_value(content)


def _is_reasoning_text_part(value: Any) -> bool:
    return isinstance(value, Mapping) and str(value.get("type") or "") in {
        "reasoning_text",
        "summary_text",
    }


def _is_reasoning_shape(block: Mapping[str, Any]) -> bool:
    if _is_reasoning_block(block) or "encrypted_content" in block or "summary" in block:
        return True
    content = block.get("content")
    if isinstance(content, Sequence) and not isinstance(content, str | bytes):
        return any(_is_reasoning_text_part(item) for item in content)
    return False


def _reasoning_from_block(block: Mapping[str, Any]) -> str:
    if not _is_reasoning_shape(block):
        return ""
    # Prefer DeepSeek ``content[].reasoning_text`` over OpenAI ``summary``.
    for key in ("content", "summary", "text"):
        extracted = _text_from_nested(block.get(key))
        if extracted:
            return extracted
    return ""


# ormsgpack / LangGraph checkpoints reject ints outside signed/unsigned 64-bit.
_MSGPACK_INT_MIN = -(2**63)
_MSGPACK_INT_MAX = 2**64 - 1


def sanitize_for_checkpoint(value: Any) -> Any:
    """Coerce oversized ints to str so LangGraph msgpack checkpoints do not fail.

    SQL ``column_stats.sum`` over snowflake-style IDs can exceed 2^64; when those
    values sit on ToolMessage.artifact and the graph hits ``interrupt()``, the
    checkpointer raises ``Integer exceeds 64-bit range``.
    """
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, int):
        if value > _MSGPACK_INT_MAX or value < _MSGPACK_INT_MIN:
            return str(value)
        return value
    if isinstance(value, Mapping):
        return {k: sanitize_for_checkpoint(v) for k, v in value.items()}
    if isinstance(value, list):
        return [sanitize_for_checkpoint(v) for v in value]
    if isinstance(value, tuple):
        return tuple(sanitize_for_checkpoint(v) for v in value)
    return value


def serialize_messages(messages: Sequence[BaseMessage]) -> list[dict[str, Any]]:
    """Store LangChain messages as plain checkpoint-safe dictionaries."""
    return sanitize_for_checkpoint(messages_to_dict(list(messages)))


def deserialize_messages(values: Sequence[Any]) -> list[BaseMessage]:
    """Accept canonical dictionaries and tolerate objects in non-durable graphs."""
    objects = [value for value in values if isinstance(value, BaseMessage)]
    if len(objects) == len(values):
        return objects
    dictionaries = [value for value in values if isinstance(value, dict)]
    if len(dictionaries) != len(values):
        raise TypeError("Conversation messages must be serialized message dictionaries")
    safe = sanitize_for_checkpoint(dictionaries)
    if not isinstance(safe, list):
        raise TypeError("Conversation messages must be serialized message dictionaries")
    return messages_from_dict(safe)
