"""Shared helpers for extracting structured JSON from model output."""

from __future__ import annotations

import orjson


def extract_nested_json(text: str) -> str | None:
    """Return the first complete JSON object or array embedded in text.

    Brackets inside JSON strings are ignored, so model output containing SQL,
    regexes, or prose with braces cannot corrupt the nesting state.
    """
    stack: list[str] = []
    start = -1
    in_string = False
    escaped = False

    for index, char in enumerate(text or ""):
        if escaped:
            escaped = False
            continue
        if char == "\\" and in_string:
            escaped = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if char in "{[":
            if not stack:
                start = index
            stack.append(char)
            continue
        if char not in "}]":
            continue
        if not stack:
            continue
        expected = "{" if char == "}" else "["
        if stack[-1] != expected:
            stack.clear()
            start = -1
            continue
        stack.pop()
        if stack or start < 0:
            continue
        candidate = text[start : index + 1]
        try:
            orjson.loads(candidate)
            return candidate
        except orjson.JSONDecodeError:
            start = -1
    return None
