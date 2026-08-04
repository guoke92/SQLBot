"""Shared normalization for provider-specific model message content."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


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
