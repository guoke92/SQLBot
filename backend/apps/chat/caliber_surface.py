"""Single projection for user-visible calibers vs undeclared assumptions.

Confirmed clarification answers are not assumptions. Assumptions are only
system-chosen constraints the user did not explicitly confirm.

All read/write shaping of these two surfaces should go through this module so
memory slots, TurnAnswer, and UI stay aligned.
"""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping, Sequence
from typing import Any


def _caliber_fields(payload: Mapping[str, Any]) -> list[dict[str, str]]:
    """Physical binding of a caliber (``[{table, field}]``) — kept end to end.

    Clarification options historically used ``name``; memory slots use ``field``.
    Accept either so bindings survive round-trips.
    """
    out: list[dict[str, str]] = []
    for raw in payload.get("fields") or []:
        if isinstance(raw, Mapping):
            table = str(raw.get("table") or "").strip()
            field = str(raw.get("field") or raw.get("name") or "").strip()
        else:
            table, _, field = str(raw or "").strip().rpartition(".")
        if field and {"table": table, "field": field} not in out:
            out.append({"table": table, "field": field})
    return out


def _caliber_item(payload: Mapping[str, Any], *, source: str) -> dict[str, Any] | None:
    question = str(payload.get("question") or "").strip()
    meaning = str(
        payload.get("meaning") or payload.get("label") or ""
    ).strip()
    label = str(payload.get("label") or meaning).strip()
    value = str(payload.get("value") or "").strip()
    if not meaning and not question and not value and not label:
        return None
    item = {
        "question": question,
        "label": label or meaning or value,
        "meaning": meaning or label or value,
        "value": value or meaning or label,
        "source": source,
    }
    fields = _caliber_fields(payload)
    if fields:
        item["fields"] = fields
    return item


def _slot_entry(payload: Mapping[str, Any]) -> dict[str, Any] | None:
    item = _caliber_item(payload, source="clarification")
    if item is None:
        return None
    entry = {
        "question": item["question"],
        "label": item["label"],
        "meaning": item["meaning"],
        "value": item["value"],
    }
    if item.get("fields"):
        entry["fields"] = item["fields"]
    return entry


def render_caliber_lines(
    items: Sequence[Mapping[str, Any]] | Mapping[str, Any],
) -> list[str]:
    """Compact prompt lines for confirmed calibers / assumptions.

    ``- 「question」→ label：meaning（table.field, …）`` — one line per item;
    the single rendering used by the system prompt (no raw JSON dumps).
    """
    values = list(items.values()) if isinstance(items, Mapping) else list(items)
    lines: list[str] = []
    for raw in values:
        if not isinstance(raw, Mapping):
            if raw not in (None, ""):
                lines.append(f"- {raw}")
            continue
        question = str(raw.get("question") or "").strip()
        label = str(raw.get("label") or raw.get("value") or "").strip()
        meaning = str(raw.get("meaning") or "").strip()
        body = label
        if meaning and meaning != label:
            body = f"{label}：{meaning}" if label else meaning
        binding = "、".join(
            f"{f['table']}.{f['field']}" if f["table"] else f["field"]
            for f in _caliber_fields(raw)
        )
        head = f"「{question}」→ " if question else ""
        tail = f"（{binding}）" if binding else ""
        text = f"{head}{body}{tail}".strip()
        if text:
            lines.append(f"- {text}")
    return lines


def is_confirmed_source(source: Any) -> bool:
    return str(source or "") in {"clarification", "confirmed"}


def project_confirmed_calibers(memory_slots: Mapping[str, Any]) -> list[dict[str, Any]]:
    """User-confirmed calibers from clarification (and equivalent sources)."""
    items: list[dict[str, Any]] = []
    confirmed = memory_slots.get("confirmed_calibers")
    if isinstance(confirmed, Mapping):
        for _key, value in confirmed.items():
            if isinstance(value, Mapping):
                item = _caliber_item(value, source="clarification")
            elif value not in (None, ""):
                item = _caliber_item({"label": str(value)}, source="clarification")
            else:
                item = None
            if item is not None:
                items.append(item)

    # Clarification-sourced rows that may still sit in the assumptions slot.
    declared = memory_slots.get("assumptions")
    if isinstance(declared, list):
        for raw in declared:
            if not isinstance(raw, Mapping):
                continue
            if not is_confirmed_source(raw.get("source")):
                continue
            item = _caliber_item(raw, source="clarification")
            if item is not None:
                items.append(item)
    return _dedupe_calibers(items)


def project_query_assumptions(memory_slots: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Undeclared system choices only — never confirmed clarification answers."""
    items: list[dict[str, Any]] = []
    declared = memory_slots.get("assumptions")
    if isinstance(declared, list):
        for raw in declared:
            if not isinstance(raw, Mapping) or not raw:
                continue
            source = str(raw.get("source") or "declared")
            if is_confirmed_source(source):
                continue
            item = _caliber_item(raw, source=source or "declared")
            if item is not None:
                items.append(item)
    return _dedupe_calibers(items)


def project_caliber_surface(
    memory_slots: Mapping[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    return {
        "confirmed_calibers": project_confirmed_calibers(memory_slots),
        "assumptions": project_query_assumptions(memory_slots),
    }


def ingest_confirmed_calibers(
    target: MutableMapping[str, Any],
    raw_confirmed: Any,
) -> None:
    """Merge answer/outline confirmed calibers into memory_slots.confirmed_calibers."""
    if isinstance(raw_confirmed, Mapping) and raw_confirmed:
        for key, value in raw_confirmed.items():
            if isinstance(value, Mapping):
                entry = _slot_entry(value)
                if entry is not None:
                    target[str(key)] = entry
            elif value not in (None, ""):
                entry = _slot_entry({"label": str(value)})
                if entry is not None:
                    target[str(key)] = entry
        return

    if not isinstance(raw_confirmed, list):
        return
    for item in raw_confirmed:
        if not isinstance(item, Mapping):
            continue
        entry = _slot_entry(item)
        if entry is None:
            continue
        key = str(entry.get("question") or entry.get("label") or "")[:120]
        if key:
            target[key] = entry


def lift_confirmed_from_assumptions(
    target: MutableMapping[str, Any],
    assumptions: Sequence[Mapping[str, Any]] | None,
) -> list[dict[str, Any]]:
    """Move clarification-sourced assumption rows into confirmed; return undeclared only."""
    undeclared: list[dict[str, Any]] = []
    for raw in assumptions or []:
        if not isinstance(raw, Mapping):
            continue
        if is_confirmed_source(raw.get("source")):
            entry = _slot_entry(raw)
            if entry is None:
                continue
            key = str(entry.get("question") or entry.get("label") or "")[:120]
            if key and key not in target:
                target[key] = entry
            continue
        undeclared.append(dict(raw))
    return undeclared


def _dedupe_calibers(items: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    out: list[dict[str, Any]] = []
    for item in items:
        key = (str(item.get("question") or ""), str(item.get("value") or ""))
        if key in seen:
            continue
        seen.add(key)
        out.append(dict(item))
    return out
