"""Enqueue, persist, and query the datasource value index."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from sqlalchemy import func, literal, or_
from sqlmodel import Session, select

from apps.datasource.models.datasource import CoreDatasource, CoreTable
from apps.datasource.models.value_index import CoreValueIndex
from apps.dictionary.matching import normalize_dictionary_value
from common.core.config import settings
from common.utils.utils import SQLBotLogUtil

_MIN_VALUE_LENGTH = 2
_MAX_HITS = 20
_TYPE_RANK = {"enum_label": 0, "enum_code": 1, "instance": 2}


@dataclass(frozen=True)
class ValueAnchor:
    table_name: str
    field_name: str
    raw_value: str
    val_type: str
    matched_text: str
    extra: dict[str, Any] | None = None


def list_field_values(
    session: Session,
    *,
    ds_id: int,
    table_name: str,
    field_name: str,
    val_types: Sequence[str] | None = None,
) -> list[dict[str, str]]:
    """Return value→label rows for one field from core_value_index."""
    if not settings.VALUE_INDEX_ENABLED:
        return []
    stmt = select(CoreValueIndex).where(
        CoreValueIndex.ds_id == ds_id,
        CoreValueIndex.table_name == table_name,
        CoreValueIndex.field_name == field_name,
    )
    if val_types:
        stmt = stmt.where(CoreValueIndex.val_type.in_(list(val_types)))
    rows = session.exec(stmt).all()
    labels: dict[str, str] = {}
    codes: list[str] = []
    for row in rows:
        extra = row.extra if isinstance(row.extra, dict) else {}
        if row.val_type == "enum_label":
            code = str(extra.get("code") or row.raw_value)
            labels[code] = row.raw_value
            if code not in codes:
                codes.append(code)
        elif row.val_type == "enum_code":
            if row.raw_value not in codes:
                codes.append(row.raw_value)
        elif row.val_type == "instance":
            if row.raw_value not in codes:
                codes.append(row.raw_value)
    return [{"value": code, "label": labels.get(code, "")} for code in codes]


def match_phrases(
    session: Session,
    *,
    ds_id: int,
    phrases: Sequence[str],
    hint_table: str = "",
) -> list[ValueAnchor]:
    """Query surface for ``lookup_values``: LLM-named phrases only, no sentence split.

    Matches either stored value ⊂ phrase (enum labels in a short fragment) or
    phrase ⊂ stored value (「二部」→「研发二部」).
    """
    if not settings.VALUE_INDEX_ENABLED:
        return []
    table_hint = str(hint_table or "").strip()
    merged: list[ValueAnchor] = []
    seen: set[tuple[str, str, str, str]] = set()
    for raw in phrases:
        text = str(raw or "").strip()
        if not text:
            continue
        for hit in _match_one_phrase(
            session, ds_id=ds_id, phrase=text, hint_table=table_hint
        ):
            key = (hit.table_name, hit.field_name, hit.raw_value, hit.val_type)
            if key in seen:
                continue
            seen.add(key)
            merged.append(hit)
    ranked = sorted(
        merged,
        key=lambda hit: (
            _TYPE_RANK.get(hit.val_type, 9),
            -len(hit.raw_value),
            hit.table_name,
            hit.field_name,
        ),
    )
    return ranked[:_MAX_HITS]


def _match_one_phrase(
    session: Session,
    *,
    ds_id: int,
    phrase: str,
    hint_table: str,
) -> list[ValueAnchor]:
    normalized = normalize_dictionary_value(phrase)
    if len(normalized) < _MIN_VALUE_LENGTH:
        return []
    stmt = select(CoreValueIndex).where(
        CoreValueIndex.ds_id == ds_id,
        func.char_length(CoreValueIndex.normalized_value) >= _MIN_VALUE_LENGTH,
        or_(
            func.strpos(literal(normalized), CoreValueIndex.normalized_value) > 0,
            func.strpos(CoreValueIndex.normalized_value, literal(normalized)) > 0,
        ),
    )
    if hint_table:
        stmt = stmt.where(CoreValueIndex.table_name == hint_table)
    rows = list(session.exec(stmt.limit(500)).all())
    return rank_value_hits(rows, phrase, reverse=True)


def rank_value_hits(
    rows: Sequence[CoreValueIndex],
    question: str,
    *,
    allowed_tables: frozenset[str] | set[str] | None = None,
    reverse: bool = False,
) -> list[ValueAnchor]:
    """Containment match: stored value ⊂ query, optionally query ⊂ stored value."""
    normalized = normalize_dictionary_value(question or "")
    if len(normalized) < _MIN_VALUE_LENGTH:
        return []
    best: dict[tuple[str, str], ValueAnchor] = {}
    for row in rows:
        value = str(row.normalized_value or "")
        if len(value) < _MIN_VALUE_LENGTH:
            continue
        if value.isdigit() and len(value) < 4:
            continue
        if allowed_tables is not None and row.table_name not in allowed_tables:
            continue
        if value in normalized:
            matched = value
        elif reverse and normalized in value:
            matched = value
        else:
            continue
        extra = row.extra if isinstance(row.extra, dict) else None
        candidate = ValueAnchor(
            table_name=row.table_name,
            field_name=row.field_name,
            raw_value=row.raw_value,
            val_type=row.val_type,
            matched_text=matched,
            extra=extra,
        )
        key = (row.table_name, row.field_name)
        current = best.get(key)
        if current is None:
            best[key] = candidate
            continue
        better_type = _TYPE_RANK.get(candidate.val_type, 9) < _TYPE_RANK.get(
            current.val_type, 9
        )
        longer = len(candidate.matched_text) > len(current.matched_text)
        if longer or (
            len(candidate.matched_text) == len(current.matched_text) and better_type
        ):
            best[key] = candidate

    # Suppress hits whose matched_text is wholly contained within another longer hit's matched_text
    candidates = list(best.values())
    longer_spans = {c.matched_text for c in candidates}
    pruned: list[ValueAnchor] = []
    for c in candidates:
        if any(
            c.matched_text != other and c.matched_text in other
            for other in longer_spans
        ):
            continue
        pruned.append(c)

    ranked = sorted(
        pruned,
        key=lambda hit: (
            _TYPE_RANK.get(hit.val_type, 9),
            -len(hit.matched_text),
            hit.table_name,
            hit.field_name,
        ),
    )
    return ranked[:_MAX_HITS]


def match_question_values(
    session: Session,
    *,
    ds_id: int,
    question: str,
    allowed_tables: frozenset[str] | set[str] | None = None,
) -> list[ValueAnchor]:
    if not settings.VALUE_INDEX_ENABLED:
        return []
    normalized = normalize_dictionary_value(question or "")
    if len(normalized) < _MIN_VALUE_LENGTH:
        return []
    stmt = select(CoreValueIndex).where(
        CoreValueIndex.ds_id == ds_id,
        func.char_length(CoreValueIndex.normalized_value) >= _MIN_VALUE_LENGTH,
        func.strpos(literal(normalized), CoreValueIndex.normalized_value) > 0,
    )
    if allowed_tables is not None:
        names = list(allowed_tables)
        if not names:
            return []
        stmt = stmt.where(CoreValueIndex.table_name.in_(names))
    rows = list(session.exec(stmt.limit(500)).all())
    return rank_value_hits(rows, question, allowed_tables=allowed_tables)


def render_value_grounding(hits: Sequence[ValueAnchor]) -> str:
    if not hits:
        return ""
    lines: list[str] = []
    for hit in hits:
        extra = hit.extra or {}
        code = str(extra.get("code") or "")
        if hit.val_type == "enum_label" and code:
            detail = f"枚举值 {code}"
        elif hit.val_type == "enum_code":
            detail = "枚举码"
        else:
            detail = "业务实例"
        lines.append(
            f'候选: "{hit.raw_value}" → {hit.table_name}.{hit.field_name}（{detail}）'
        )
    return "\n".join(lines)


def extract_datasource(
    session: Session,
    *,
    ds_id: int,
    table_ids: Sequence[int] | None = None,
) -> int:
    from apps.datasource.instance_index.extractor import (
        extract_table,
        select_extract_scope,
    )
    from apps.knowledge.wiki.corpus_runtime import load_bound_corpus

    ds = session.get(CoreDatasource, ds_id)
    if ds is None:
        return 0
    query = select(CoreTable).where(CoreTable.ds_id == ds_id)
    if table_ids:
        query = query.where(CoreTable.id.in_([int(i) for i in table_ids]))
    tables = select_extract_scope(list(session.exec(query).all()))
    store = None
    try:
        loaded = load_bound_corpus(session, ds_id)
        store = loaded.store if loaded is not None else None
    except Exception as exc:
        SQLBotLogUtil.warning("value-index wiki load failed ds=%s: %s", ds_id, exc)
    total = 0
    for idx, table in enumerate(tables, 1):
        try:
            total += extract_table(session, ds=ds, table=table, store=store)
            if idx % 10 == 0:
                session.commit()
                SQLBotLogUtil.info(
                    "value-index progress ds=%s [%s/%s tables]", ds_id, idx, len(tables)
                )
        except Exception as exc:
            SQLBotLogUtil.warning(
                "value-index extract table %s failed: %s",
                getattr(table, "table_name", table.id),
                exc,
            )
    session.commit()
    SQLBotLogUtil.info(
        "value-index extracted ds=%s tables=%s rows=%s", ds_id, len(tables), total
    )
    return total


def enqueue_value_index_extract(
    ds_id: int, table_ids: Sequence[int] | None = None
) -> None:
    """Fire-and-forget extract on the shared embedding thread pool."""
    if not settings.VALUE_INDEX_ENABLED:
        return
    from common.utils.embedding_threads import executor, session_maker

    ids = [int(i) for i in (table_ids or []) if i is not None]

    def _run() -> None:
        session = session_maker()
        try:
            extract_datasource(session, ds_id=int(ds_id), table_ids=ids or None)
        except Exception as exc:
            SQLBotLogUtil.warning(
                "value-index background extract ds=%s failed: %s", ds_id, exc
            )
            try:
                session.rollback()
            except Exception:
                pass
        finally:
            session.close()

    executor.submit(_run)
