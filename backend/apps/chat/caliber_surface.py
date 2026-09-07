"""Single projection for user-visible calibers vs undeclared assumptions.

Confirmed clarification answers are not assumptions. Assumptions are only
system-chosen constraints the user did not explicitly confirm.

All read/write shaping of these two surfaces should go through this module so
memory slots, TurnAnswer, and UI stay aligned.
"""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping, Sequence
from typing import Any


def _caliber_item(payload: Mapping[str, Any], *, source: str) -> dict[str, Any] | None:
    question = str(payload.get("question") or "").strip()
    meaning = str(
        payload.get("meaning") or payload.get("label") or payload.get("value") or ""
    ).strip()
    label = str(payload.get("label") or meaning).strip()
    if not meaning and not question:
        return None
    return {
        "question": question,
        "label": label or meaning,
        "meaning": meaning or label,
        "value": meaning or label,
        "source": source,
    }


def _slot_entry(payload: Mapping[str, Any]) -> dict[str, Any] | None:
    item = _caliber_item(payload, source="clarification")
    if item is None:
        return None
    return {
        "question": item["question"],
        "label": item["label"],
        "meaning": item["meaning"],
    }


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


def project_caliber_surface(memory_slots: Mapping[str, Any]) -> dict[str, list[dict[str, Any]]]:
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
