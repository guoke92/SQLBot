"""Accepted-result projection for a turn.

One delivery slot is one user-facing result card. Same slot: later success
replaces earlier. Distinct slots all stay. Probes and failures never publish.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

_UNTITLED_SLOT = ("untitled",)


def _normalize_title(raw: Any) -> str:
    return " ".join(str(raw or "").split())


def _attr(item: Any, name: str, default: Any = None) -> Any:
    if isinstance(item, Mapping):
        return item[name] if name in item else default
    return getattr(item, name, default)


def _snapshot(item: Any) -> Mapping[str, Any]:
    raw = _attr(item, "schema_snapshot")
    return raw if isinstance(raw, Mapping) else {}


def _field_names(item: Any) -> tuple[str, ...]:
    raw = _attr(item, "fields") or []
    names = [str(field).strip() for field in raw if str(field).strip()]
    return tuple(sorted(names))


def delivery_slot_key(item: Any) -> tuple[str, ...]:
    """Stable slot id: titled card, else field set, else a shared untitled slot."""
    title = _normalize_title(_snapshot(item).get("result_title"))
    if title:
        return ("title", title)
    fields = _field_names(item)
    if fields:
        return ("fields", *fields)
    return _UNTITLED_SLOT


def select_delivery_datasets(datasets: Sequence[Any]) -> list[Any]:
    """Keep the last successful required dataset per slot, in first-seen order."""
    chosen: dict[tuple[str, ...], Any] = {}
    order: list[tuple[str, ...]] = []
    for item in datasets:
        if str(_attr(item, "status") or "succeeded") == "failed":
            continue
        if _attr(item, "required", True) is False:
            continue
        key = delivery_slot_key(item)
        if key not in chosen:
            order.append(key)
        chosen[key] = item
    return [chosen[key] for key in order]
