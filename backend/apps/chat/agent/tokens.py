"""CJK-aware token estimate for context budget and folding."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from apps.conversation.messages import message_content_text


def count_tokens(value: Any) -> int:
    """Approximate tokens without a vendor tokenizer.

    CJK characters count as one token; ASCII is ~4 chars/token.
    """
    if value is None:
        return 0
    if not isinstance(value, str):
        try:
            import orjson

            text = orjson.dumps(value, default=str).decode()
        except Exception:
            text = str(value)
    else:
        text = value
    if not text:
        return 0
    cjk = 0
    other = 0
    for char in text:
        code = ord(char)
        if (
            0x3400 <= code <= 0x9FFF
            or 0xF900 <= code <= 0xFAFF
            or 0x20000 <= code <= 0x2CEAF
        ):
            cjk += 1
        else:
            other += 1
    return max(1, cjk + (other + 3) // 4)


def count_message_tokens(messages: Sequence[Any]) -> int:
    total = 0
    for message in messages:
        total += count_tokens(
            message_content_text(getattr(message, "content", "") or "")
        )
        for call in getattr(message, "tool_calls", None) or []:
            total += count_tokens(call)
        name = getattr(message, "name", None)
        if name:
            total += count_tokens(str(name))
    return max(1, total) if messages else 0
