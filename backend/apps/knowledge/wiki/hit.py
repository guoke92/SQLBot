"""Single projection for wiki knowledge hits (search tool + prompt).

Structured WikiPage fields are the payload. Body prose is an optional note,
never the only thing the agent sees.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

from apps.knowledge.wiki.contract import WikiPage

_FENCE_RE = re.compile(r"```[\s\S]*?```")
_HEADING_RE = re.compile(r"^#{1,6}\s+", re.M)
_WS_RE = re.compile(r"\s+")
_NOTE_CHARS = 200


def _clip(text: str, limit: int) -> str:
    cleaned = _WS_RE.sub(" ", str(text or "").strip())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1].rstrip() + "…"


def _ground(page: WikiPage, kind: str) -> dict[str, Any]:
    for block in page.ground_blocks:
        if block.kind == kind:
            data = block.data
            return dict(data) if isinstance(data, Mapping) else {}
    return {}


def _role_tables(raw: Any) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    if not isinstance(raw, list):
        return rows
    for item in raw:
        if not isinstance(item, Mapping):
            continue
        table = str(item.get("table") or "").strip()
        if not table:
            continue
        entry = {"table": table}
        role = str(item.get("role") or "").strip()
        if role:
            entry["role"] = role
        rows.append(entry)
    return rows


def _prose_note(body: str) -> str:
    text = _FENCE_RE.sub(" ", str(body or ""))
    text = _HEADING_RE.sub("", text)
    parts = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    if not parts:
        return ""
    return _clip(parts[0], _NOTE_CHARS)


def project_knowledge_hit(page: WikiPage) -> dict[str, Any]:
    """Project a wiki page into the search_knowledge object shape."""
    hit: dict[str, Any] = {
        "type": page.type,
        "page_key": page.page_key,
        "title": page.title,
    }
    if page.maps_to:
        hit["maps_to"] = page.maps_to
    if page.field_targets:
        hit["field_targets"] = list(page.field_targets)
    if page.also_confused_with:
        hit["also_confused_with"] = list(page.also_confused_with)
    if page.adjudication:
        hit["adjudication"] = page.adjudication
    if page.type == "caliber":
        data = _ground(page, "caliber")
        predicate = str(data.get("predicate") or "").strip()
        if predicate:
            hit["predicate"] = _clip(predicate, 400)
        boundary = str(data.get("boundary") or "").strip()
        if boundary:
            hit["boundary"] = _clip(boundary, 240)
    elif page.type == "scenario":
        data = _ground(page, "scenario")
        hubs = _role_tables(data.get("hubs"))
        shared = _role_tables(data.get("shared"))
        if hubs:
            hit["hubs"] = hubs
        if shared:
            hit["shared"] = shared
    note = _prose_note(page.body)
    if note:
        hit["note"] = note
    return hit


def format_knowledge_hit(hit: Mapping[str, Any]) -> str:
    """Render one projected hit. Same fields as ``project_knowledge_hit``."""
    title = str(hit.get("title") or hit.get("page_key") or "")
    kind = str(hit.get("type") or "")
    lines = [f"{kind}: {title}".strip()]
    order = (
        "page_key",
        "maps_to",
        "field_targets",
        "predicate",
        "boundary",
        "also_confused_with",
        "adjudication",
        "hubs",
        "shared",
        "note",
    )
    for key in order:
        value = hit.get(key)
        if value in (None, "", [], ()):
            continue
        lines.append(f"  {key}: {_fmt_value(value)}")
    return "\n".join(lines)


def format_knowledge_hits(hits: Sequence[Mapping[str, Any]]) -> dict[str, str]:
    """store_key/page_key → compact text, for plane wiki_passages."""
    out: dict[str, str] = {}
    for hit in hits:
        key = str(hit.get("store_key") or hit.get("page_key") or "").strip()
        if not key:
            continue
        out[key] = format_knowledge_hit(hit)
    return out


def _fmt_value(value: Any) -> str:
    if isinstance(value, list):
        if value and isinstance(value[0], Mapping):
            parts = []
            for item in value:
                table = str(item.get("table") or "")
                role = str(item.get("role") or "")
                parts.append(f"{table}({role})" if role else table)
            return ", ".join(part for part in parts if part)
        return ", ".join(str(item) for item in value if str(item).strip())
    return str(value).strip()
