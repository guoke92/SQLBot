"""Split multi-value instance cells while keeping the original string."""

from __future__ import annotations

import json
import re
from collections.abc import Sequence
from typing import Any

from apps.datasource.instance_index.nomination import is_opaque_token

_SEP_RE = re.compile(r"[,，、;；|]+")


def tokenize_cell(raw: str) -> list[str]:
    """Atomic tokens inside a cell. Empty input → empty list."""
    text = str(raw or "").strip()
    if not text:
        return []
    parsed = _parse_json_list(text)
    if parsed is not None:
        return [item for item in parsed if item]
    parts = [part.strip() for part in _SEP_RE.split(text) if part.strip()]
    if len(parts) >= 2:
        return parts
    return [text]


def infer_match_hint(raw: str, extra: dict[str, Any] | None = None) -> str:
    """eq for a scalar cell; contains for JSON / delimited / token-of-raw."""
    payload = extra if isinstance(extra, dict) else {}
    if payload.get("raw_cell") or payload.get("token_of"):
        return "contains"
    text = str(raw or "").strip()
    if text.startswith("["):
        return "contains"
    if _SEP_RE.search(text):
        return "contains"
    return "eq"


def infer_field_shape(values: Sequence[str]) -> str:
    kinds: set[str] = set()
    for item in values:
        text = str(item or "").strip()
        if not text:
            continue
        if text.startswith("["):
            kinds.add("json_array")
        elif _SEP_RE.search(text):
            kinds.add("multi_sep")
        else:
            kinds.add("scalar")
    if not kinds:
        return "scalar"
    if len(kinds) > 1:
        return "mixed"
    return next(iter(kinds))


def instance_cell_entries(
    raw: str, *, count: int = 0
) -> list[tuple[str, dict[str, Any] | None]]:
    """Index the original cell and any split tokens.

    Extra marks ``raw_cell`` on the original multi-value string and
    ``token_of`` on each atomic token so UI/agent can tell them apart.
    """
    text = str(raw or "").strip()
    if not text:
        return []
    tokens = tokenize_cell(text)
    multi = bool(tokens) and not (len(tokens) == 1 and tokens[0] == text)
    entries: list[tuple[str, dict[str, Any] | None]] = []
    if not is_opaque_token(text):
        extra: dict[str, Any] = {}
        if count:
            extra["count"] = count
        if multi:
            extra["raw_cell"] = True
        entries.append((text, extra or None))
    if multi:
        for token in tokens:
            if not token or token == text or is_opaque_token(token):
                continue
            extra = {"token_of": text}
            if count:
                extra["count"] = count
            entries.append((token, extra))
    return entries


def _parse_json_list(text: str) -> list[str] | None:
    stripped = text.strip()
    if not stripped.startswith("["):
        return None
    try:
        loaded = json.loads(stripped)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(loaded, list):
        return None
    out: list[str] = []
    for item in loaded:
        if item is None:
            continue
        if isinstance(item, str | int | float):
            value = str(item).strip()
            if value:
                out.append(value)
        else:
            return None
    return out
