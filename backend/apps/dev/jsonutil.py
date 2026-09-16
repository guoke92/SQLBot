"""JSON-safe conversion for conversation packs stored as JSONB."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import UUID


def jsonable(value: Any) -> Any:
    if value is None or isinstance(value, bool | int | float | str):
        return value
    if isinstance(value, datetime | date):
        return value.isoformat()
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, bytes | bytearray):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, list | tuple | set):
        return [jsonable(item) for item in value]
    dump = getattr(value, "model_dump", None)
    if callable(dump):
        return jsonable(dump(mode="json"))
    return str(value)


def parse_id_list(raw: str | None) -> list[int]:
    if not raw or not str(raw).strip():
        return []
    out: list[int] = []
    seen: set[int] = set()
    for part in str(raw).split(","):
        text = part.strip()
        if not text:
            continue
        try:
            value = int(text)
        except ValueError:
            continue
        if value in seen:
            continue
        seen.add(value)
        out.append(value)
    return out
