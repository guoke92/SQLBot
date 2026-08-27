"""Per-datasource value index for deterministic recall top-up.

Bridges business *values* ("研发二部") to schema locations via
"normalized value ⊂ normalized text" containment — no segmentation, no LLM.
Sources: published dictionary values ∪ active profiling ``top_values``
(low-cardinality gate). Every consumer must apply AccessScope afterwards;
the index itself only knows names.

The index is process-local (see ``CACHE_TYPE=memory`` limitation) and lazily
rebuilt when the generation stamp drifts: dictionary ``published_generation``
aggregate + per-table ``active_profile_generation`` aggregate. Publication
lag across processes is acceptable — stamps make copies self-healing.
"""

from __future__ import annotations

import threading
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from sqlmodel import Session, func, select

from apps.datasource.models.datasource import CoreField, CoreTable
from apps.datasource.profiling.models import FieldProfileSnapshot
from apps.dictionary.matching import normalize_dictionary_value
from apps.dictionary.models import (
    DictionaryFieldConfig,
    DictionaryStatus,
    DictionaryValue,
)
from common.core.config import settings
from common.utils.utils import SQLBotLogUtil

_MIN_VALUE_LENGTH = 2
_MAX_HITS = 20


@dataclass(frozen=True)
class ValueHit:
    """One containment hit: where in the schema a business value lives."""

    table_name: str
    field_name: str
    value: str
    source: str  # "dictionary" | "profile"
    matched_text: str


@dataclass(frozen=True)
class _IndexEntry:
    table_name: str
    field_name: str
    value: str
    normalized_value: str
    source: str


@dataclass(frozen=True)
class _CachedIndex:
    stamp: tuple[int, int, int, int]
    entries: tuple[_IndexEntry, ...]


_INDEX_CACHE: dict[tuple[int, int], _CachedIndex] = {}
_CACHE_LOCK = threading.Lock()


def clear_value_index_cache() -> None:
    """Test hook: drop all process-local index copies."""
    with _CACHE_LOCK:
        _INDEX_CACHE.clear()


def _generation_stamp(
    session: Session, *, oid: int, ds_id: int
) -> tuple[int, int, int, int]:
    """Cheap aggregate stamp; any publish/profile bump invalidates the copy."""
    dict_row = session.exec(
        select(
            func.count(DictionaryFieldConfig.id),
            func.coalesce(func.sum(DictionaryFieldConfig.published_generation), 0),
        ).where(
            DictionaryFieldConfig.oid == oid,
            DictionaryFieldConfig.ds_id == ds_id,
            DictionaryFieldConfig.enabled == True,  # noqa: E712
            DictionaryFieldConfig.status == DictionaryStatus.READY,
        )
    ).one()
    table_row = session.exec(
        select(
            func.count(CoreTable.id),
            func.coalesce(func.sum(CoreTable.active_profile_generation), 0),
        ).where(
            CoreTable.ds_id == ds_id,
            CoreTable.checked == True,  # noqa: E712
        )
    ).one()
    return (int(dict_row[0]), int(dict_row[1]), int(table_row[0]), int(table_row[1]))


def _iter_top_values(raw: Any, *, top_k: int) -> Iterable[str]:
    """Profile ``top_values`` accepts raw scalars or ``{"value": ...}`` dicts."""
    if not isinstance(raw, list):
        return []
    values: list[str] = []
    for item in raw[: max(0, int(top_k))]:
        raw_value = item.get("value") if isinstance(item, dict) else item
        if raw_value is None:
            continue
        text = str(raw_value).strip()
        if text:
            values.append(text)
    return values


def _build_entries(
    session: Session, *, oid: int, ds_id: int
) -> tuple[_IndexEntry, ...]:
    entries: list[_IndexEntry] = []

    dictionary_rows = session.exec(
        select(DictionaryValue, CoreTable, CoreField)
        .join(
            DictionaryFieldConfig,
            DictionaryFieldConfig.id == DictionaryValue.config_id,
        )
        .join(CoreTable, CoreTable.id == DictionaryFieldConfig.table_id)
        .join(CoreField, CoreField.id == DictionaryFieldConfig.field_id)
        .where(
            DictionaryFieldConfig.oid == oid,
            DictionaryFieldConfig.ds_id == ds_id,
            DictionaryFieldConfig.enabled == True,  # noqa: E712
            DictionaryFieldConfig.status == DictionaryStatus.READY,
            DictionaryFieldConfig.published_generation > 0,
            DictionaryValue.generation == DictionaryFieldConfig.published_generation,
        )
    ).all()
    for value, table, field in dictionary_rows:
        normalized = normalize_dictionary_value(
            value.normalized_value or value.value or ""
        )
        if len(normalized) < _MIN_VALUE_LENGTH:
            continue
        entries.append(
            _IndexEntry(
                table_name=table.table_name,
                field_name=field.field_name,
                value=str(value.value or ""),
                normalized_value=normalized,
                source="dictionary",
            )
        )

    if settings.RECALL_VALUE_INDEX_TOP_K > 0:
        max_ratio = float(settings.RECALL_VALUE_INDEX_MAX_DISTINCT_RATIO)
        profile_rows = session.exec(
            select(FieldProfileSnapshot, CoreTable, CoreField)
            .join(CoreTable, CoreTable.id == FieldProfileSnapshot.table_id)
            .join(CoreField, CoreField.id == FieldProfileSnapshot.field_id)
            .where(
                FieldProfileSnapshot.ds_id == ds_id,
                FieldProfileSnapshot.window_code == "ALL",
                FieldProfileSnapshot.status == "READY",
                CoreTable.active_profile_generation > 0,
                FieldProfileSnapshot.generation == CoreTable.active_profile_generation,
                FieldProfileSnapshot.top_values != None,  # noqa: E711
            )
        ).all()
        for snapshot, table, field in profile_rows:
            ratio = snapshot.distinct_ratio
            if ratio is not None and float(ratio) > max_ratio:
                continue
            for raw in _iter_top_values(
                snapshot.top_values, top_k=int(settings.RECALL_VALUE_INDEX_TOP_K)
            ):
                normalized = normalize_dictionary_value(raw)
                if len(normalized) < _MIN_VALUE_LENGTH:
                    continue
                entries.append(
                    _IndexEntry(
                        table_name=table.table_name,
                        field_name=field.field_name,
                        value=raw,
                        normalized_value=normalized,
                        source="profile",
                    )
                )

    deduped: dict[tuple[str, str, str], _IndexEntry] = {}
    for entry in entries:
        deduped.setdefault(
            (entry.table_name, entry.field_name, entry.normalized_value), entry
        )
    return tuple(deduped.values())


def _get_index(session: Session, *, oid: int, ds_id: int) -> tuple[_IndexEntry, ...]:
    stamp = _generation_stamp(session, oid=oid, ds_id=ds_id)
    key = (oid, ds_id)
    with _CACHE_LOCK:
        cached = _INDEX_CACHE.get(key)
        if cached is not None and cached.stamp == stamp:
            return cached.entries
    entries = _build_entries(session, oid=oid, ds_id=ds_id)
    with _CACHE_LOCK:
        _INDEX_CACHE[key] = _CachedIndex(stamp=stamp, entries=entries)
    SQLBotLogUtil.info(
        "value index built for ds %s: %s entrie(s) (stamp=%s)",
        ds_id,
        len(entries),
        stamp,
    )
    return entries


def match_values(
    session: Session,
    text: str,
    *,
    oid: int,
    ds_id: int,
    allowed_tables: frozenset[str] | set[str] | None = None,
) -> list[ValueHit]:
    """Containment-match one text (question / clarify answer) against the index.

    ``allowed_tables`` is the AccessScope table-name fence; None skips the
    check (callers that already project resources). Hits are deduplicated per
    (table, field) keeping the longest matched value.
    """
    if not settings.RECALL_VALUE_INDEX_ENABLED:
        return []
    normalized_text = normalize_dictionary_value(text or "")
    if len(normalized_text) < _MIN_VALUE_LENGTH:
        return []

    best: dict[tuple[str, str], ValueHit] = {}
    for entry in _get_index(session, oid=oid, ds_id=ds_id):
        if entry.normalized_value not in normalized_text:
            continue
        if allowed_tables is not None and entry.table_name not in allowed_tables:
            continue
        key = (entry.table_name, entry.field_name)
        candidate = ValueHit(
            table_name=entry.table_name,
            field_name=entry.field_name,
            value=entry.value,
            source=entry.source,
            matched_text=entry.normalized_value,
        )
        current = best.get(key)
        if current is None or len(candidate.matched_text) > len(current.matched_text):
            best[key] = candidate
    ranked = sorted(
        best.values(),
        key=lambda hit: (-len(hit.matched_text), hit.table_name, hit.field_name),
    )
    return ranked[:_MAX_HITS]
