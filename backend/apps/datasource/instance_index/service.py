"""Enqueue, persist, and query the datasource value index."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, replace
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
_MAX_HITS_UNSCOPED = 12
_MAX_SCOPE_TABLES = 3
_MAX_SCOPE_FIELDS = 3
_FIELD_TOPK = 20
_TYPE_RANK = {"person_alias": 0, "enum_label": 1, "enum_code": 2, "instance": 3}


@dataclass(frozen=True)
class ValueAnchor:
    table_name: str
    field_name: str
    raw_value: str
    val_type: str
    matched_text: str
    extra: dict[str, Any] | None = None


@dataclass(frozen=True)
class LookupScope:
    tables: frozenset[str] = frozenset()
    fields: frozenset[tuple[str, str]] = frozenset()

    def empty(self) -> bool:
        return not self.tables and not self.fields

    def allows(self, table: str, field: str) -> bool:
        if self.empty():
            return True
        if (table, field) in self.fields:
            return True
        return table in self.tables

    def table_names(self) -> set[str]:
        return set(self.tables) | {table for table, _field in self.fields}


def parse_lookup_scope(
    scope: Sequence[str] | None = None, *, hint_table: str = ""
) -> LookupScope:
    """Parse ``table`` or ``table.field`` tokens. Caps: 3 tables, 3 fields."""
    tables: list[str] = []
    fields: list[tuple[str, str]] = []
    items = [str(item).strip() for item in (scope or []) if str(item).strip()]
    hint = str(hint_table or "").strip()
    if hint and hint not in items:
        items.append(hint)
    for item in items:
        if "." in item:
            table, field = item.split(".", 1)
            table, field = table.strip(), field.strip()
            if table and field:
                fields.append((table, field))
        else:
            tables.append(item)
    return LookupScope(
        tables=frozenset(tables[:_MAX_SCOPE_TABLES]),
        fields=frozenset(fields[:_MAX_SCOPE_FIELDS]),
    )


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
    scope: LookupScope | Sequence[str] | None = None,
) -> list[ValueAnchor]:
    """Query surface for ``lookup_values``: LLM-named phrases only, no sentence split.

    Matches either stored value ⊂ phrase (enum labels in a short fragment) or
    phrase ⊂ stored value (「二部」→「研发二部」). Person hits expand to every
    alias of that user inside ``scope``.
    """
    if not settings.VALUE_INDEX_ENABLED:
        return []
    parsed = (
        scope
        if isinstance(scope, LookupScope)
        else parse_lookup_scope(scope, hint_table=hint_table)
    )
    merged: list[ValueAnchor] = []
    seen: set[tuple[str, str, str, str]] = set()
    for raw in phrases:
        text = str(raw or "").strip()
        if not text:
            continue
        for hit in _match_one_phrase(session, ds_id=ds_id, phrase=text, scope=parsed):
            key = (hit.table_name, hit.field_name, hit.raw_value, hit.val_type)
            if key in seen:
                continue
            seen.add(key)
            merged.append(hit)
    cap = _MAX_HITS if not parsed.empty() else _MAX_HITS_UNSCOPED
    ranked = sorted(
        merged,
        key=lambda hit: (
            _TYPE_RANK.get(hit.val_type, 9),
            -len(hit.raw_value),
            hit.table_name,
            hit.field_name,
        ),
    )
    expanded = expand_person_anchored_hits(
        session, ds_id=ds_id, hits=ranked[:cap], scope=parsed
    )
    return attach_person_snapshots(session, ds_id=ds_id, hits=expanded)


def _match_one_phrase(
    session: Session,
    *,
    ds_id: int,
    phrase: str,
    scope: LookupScope,
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
    if not scope.empty():
        names = list(scope.table_names())
        stmt = stmt.where(
            or_(
                CoreValueIndex.val_type == "person_alias",
                CoreValueIndex.table_name.in_(names) if names else literal(False),
            )
        )
    rows = list(session.exec(stmt.limit(500)).all())
    if not scope.empty():
        rows = [
            row
            for row in rows
            if row.val_type == "person_alias"
            or scope.allows(row.table_name, row.field_name)
        ]
    return rank_value_hits(rows, phrase, reverse=True, collapse_per_field=False)


def expand_person_anchored_hits(
    session: Session,
    *,
    ds_id: int,
    hits: Sequence[ValueAnchor],
    scope: LookupScope | None = None,
) -> list[ValueAnchor]:
    """When a person alias hits, match all of that user's aliases in scope."""
    people = [hit for hit in hits if hit.val_type == "person_alias"]
    if not people:
        return list(hits)
    from apps.datasource.instance_index.person_map import (
        extra_instance_hits_for_people,
        synthetic_id_hits_for_people,
    )

    parsed = scope or LookupScope()
    aliases: set[str] = set()
    tables: set[str] = set()
    for hit in people:
        extra = hit.extra or {}
        for item in list(extra.get("aliases") or []) + [
            extra.get("name_zh"),
            extra.get("name_en_raw"),
            extra.get("name_en_fold"),
            extra.get("user_id"),
            extra.get("sso_id"),
            extra.get("wx_id"),
        ]:
            text = str(item or "").strip()
            if text:
                aliases.add(normalize_dictionary_value(text))
        for item in extra.get("anchored_fields") or []:
            if not isinstance(item, dict) or not item.get("table"):
                continue
            table = str(item["table"])
            field = str(item.get("field") or "")
            if parsed.allows(table, field):
                tables.add(table)
    if not aliases:
        return list(hits)
    if parsed.empty():
        tables = tables or {
            str(item.get("table") or "")
            for hit in people
            for item in (hit.extra or {}).get("anchored_fields") or []
            if isinstance(item, dict)
        }
    extra_hits: list[ValueAnchor] = []
    if tables:
        alias_list = [item for item in aliases if item]
        contain = [
            func.strpos(CoreValueIndex.normalized_value, literal(alias)) > 0
            for alias in alias_list[:12]
        ]
        stmt = select(CoreValueIndex).where(
            CoreValueIndex.ds_id == ds_id,
            CoreValueIndex.val_type == "instance",
            CoreValueIndex.table_name.in_(list(tables)),
            or_(
                CoreValueIndex.normalized_value.in_(alias_list),
                *contain,
            ),
        )
        rows = list(session.exec(stmt.limit(500)).all())
        extra_hits.extend(
            extra_instance_hits_for_people(
                people,
                rows,
                scope_tables=set(parsed.tables) if parsed.tables else None,
                scope_fields=set(parsed.fields) if parsed.fields else None,
            )
        )
    extra_hits.extend(synthetic_id_hits_for_people(people, parsed))
    merged = list(hits)
    seen = {
        (hit.table_name, hit.field_name, hit.raw_value, hit.val_type) for hit in hits
    }
    for hit in extra_hits:
        key = (hit.table_name, hit.field_name, hit.raw_value, hit.val_type)
        if key in seen:
            continue
        seen.add(key)
        merged.append(hit)
    cap = _MAX_HITS * 2 if not parsed.empty() else _MAX_HITS
    return merged[:cap]


def list_field_topk(
    session: Session,
    *,
    ds_id: int,
    table_name: str,
    field_name: str,
    limit: int = _FIELD_TOPK,
    proto: Any | None = None,
    ds: Any | None = None,
    database_name: str | None = None,
) -> list[ValueAnchor]:
    """Indexed instance samples for one field (column-topk mode)."""
    if not settings.VALUE_INDEX_ENABLED:
        return []
    stmt = select(CoreValueIndex).where(
        CoreValueIndex.ds_id == ds_id,
        CoreValueIndex.table_name == table_name,
        CoreValueIndex.field_name == field_name,
        CoreValueIndex.val_type == "instance",
    )
    rows = list(session.exec(stmt.limit(500)).all())

    def _count(row: CoreValueIndex) -> int:
        extra = row.extra if isinstance(row.extra, dict) else {}
        try:
            return int(extra.get("count") or 0)
        except (TypeError, ValueError):
            return 0

    ranked = sorted(rows, key=_count, reverse=True)
    out: list[ValueAnchor] = []
    seen: set[str] = set()
    for row in ranked:
        raw = str(row.raw_value or "").strip()
        if not raw or raw in seen:
            continue
        seen.add(raw)
        extra = row.extra if isinstance(row.extra, dict) else None
        out.append(
            ValueAnchor(
                table_name=row.table_name,
                field_name=row.field_name,
                raw_value=raw,
                val_type=row.val_type,
                matched_text=str(row.normalized_value or raw),
                extra=extra,
            )
        )
        if len(out) >= max(1, int(limit)):
            break
    if out:
        return attach_person_snapshots(session, ds_id=ds_id, hits=out)
    return _profile_field_topk(
        proto=proto,
        ds=ds,
        table_name=table_name,
        field_name=field_name,
        database_name=database_name,
        limit=limit,
        session=session,
        ds_id=ds_id,
    )


def _profile_field_topk(
    *,
    proto: Any | None,
    ds: Any | None,
    table_name: str,
    field_name: str,
    database_name: str | None,
    limit: int,
    session: Session,
    ds_id: int,
) -> list[ValueAnchor]:
    if proto is None or ds is None:
        return []
    try:
        result = proto.profile_field(
            ds,
            resource=table_name,
            field=field_name,
            database_name=database_name,
            top_k=max(1, int(limit)),
        )
    except Exception as exc:
        SQLBotLogUtil.warning(
            "lookup_values profile %s.%s failed: %s", table_name, field_name, exc
        )
        return []
    if result is None or not getattr(result, "supported", True):
        return []
    from apps.datasource.instance_index.cells import instance_cell_entries

    out: list[ValueAnchor] = []
    seen: set[str] = set()
    for item in list(getattr(result, "top_values", None) or []):
        if isinstance(item, dict):
            value = str(item.get("value") or "").strip()
            count = int(item.get("count") or 0)
        else:
            value = str(item or "").strip()
            count = 0
        if not value:
            continue
        for cell, extra in instance_cell_entries(value, count=count):
            if cell in seen:
                continue
            seen.add(cell)
            out.append(
                ValueAnchor(
                    table_name=table_name,
                    field_name=field_name,
                    raw_value=cell,
                    val_type="instance",
                    matched_text=cell,
                    extra=extra,
                )
            )
            if len(out) >= max(1, int(limit)):
                return attach_person_snapshots(session, ds_id=ds_id, hits=out)
    return attach_person_snapshots(session, ds_id=ds_id, hits=out)


def attach_person_snapshots(
    session: Session, *, ds_id: int, hits: Sequence[ValueAnchor]
) -> list[ValueAnchor]:
    """Copy person combo extra onto id-like instance hits."""
    need: list[str] = []
    for hit in hits:
        extra = hit.extra or {}
        if extra.get("aliases") or extra.get("name_zh") or extra.get("user_id"):
            continue
        raw = str(hit.raw_value or "").strip()
        if raw:
            need.append(normalize_dictionary_value(raw))
    if not need:
        return list(hits)
    stmt = select(CoreValueIndex).where(
        CoreValueIndex.ds_id == ds_id,
        CoreValueIndex.val_type == "person_alias",
        CoreValueIndex.normalized_value.in_(list(set(need))),
    )
    rows = list(session.exec(stmt.limit(200)).all())
    by_norm: dict[str, dict[str, Any]] = {}
    for row in rows:
        extra = row.extra if isinstance(row.extra, dict) else {}
        if extra:
            by_norm[str(row.normalized_value or "")] = extra
    out: list[ValueAnchor] = []
    for hit in hits:
        extra = dict(hit.extra or {})
        if extra.get("aliases") or extra.get("name_zh") or extra.get("user_id"):
            out.append(hit)
            continue
        snap = by_norm.get(normalize_dictionary_value(hit.raw_value))
        if not snap:
            out.append(hit)
            continue
        merged = dict(snap)
        merged.update(extra)
        for keep in (
            "person_key",
            "user_id",
            "wx_id",
            "name_zh",
            "name_en_fold",
            "name_en_raw",
            "aliases",
            "anchored_fields",
        ):
            if snap.get(keep) is not None:
                merged[keep] = snap[keep]
        out.append(replace(hit, extra=merged))
    return out


def person_display_name(hit: ValueAnchor) -> str | None:
    extra = hit.extra or {}
    label = str(extra.get("name_zh") or extra.get("name_en_raw") or "").strip()
    if not label:
        return None
    raw = str(hit.raw_value or "").strip()
    user_id = str(extra.get("user_id") or extra.get("sso_id") or "").strip()
    wx_id = str(extra.get("wx_id") or "").strip()
    role = ""
    for item in extra.get("anchored_fields") or []:
        if not isinstance(item, dict):
            continue
        if str(item.get("table") or "") != hit.table_name:
            continue
        if str(item.get("field") or "") != hit.field_name:
            continue
        role = str(item.get("value_role") or "")
        break
    if role in {"id", "wx"} or (user_id and raw == user_id) or (wx_id and raw == wx_id):
        return label
    return None


def annotate_lookup_candidate(
    hit: ValueAnchor, *, phrases: Sequence[str] = ()
) -> dict[str, Any]:
    from apps.datasource.instance_index.cells import infer_match_hint

    extra = dict(hit.extra or {})
    hint = infer_match_hint(hit.raw_value, extra)
    raw = str(hit.raw_value or "")
    for phrase in phrases:
        text = str(phrase or "").strip()
        if text and text != raw and (text in raw or raw in text):
            hint = "contains"
            break
    display = person_display_name(hit)
    person = None
    if extra.get("aliases") or extra.get("user_id") or extra.get("person_key"):
        person = {
            "user_id": extra.get("user_id"),
            "wx_id": extra.get("wx_id"),
            "name_zh": extra.get("name_zh"),
            "name_en_raw": extra.get("name_en_raw"),
            "aliases": list(extra.get("aliases") or []),
        }
    return {
        "table": hit.table_name,
        "field": hit.field_name,
        "full_value": hit.raw_value,
        "val_type": hit.val_type,
        "matched": hit.matched_text,
        "match_hint": hint,
        "display_name": display,
        "person": person,
        "extra": extra,
    }


def rank_value_hits(
    rows: Sequence[CoreValueIndex],
    question: str,
    *,
    allowed_tables: frozenset[str] | set[str] | None = None,
    reverse: bool = False,
    collapse_per_field: bool = True,
) -> list[ValueAnchor]:
    """Containment match: stored value ⊂ query, optionally query ⊂ stored value."""
    normalized = normalize_dictionary_value(question or "")
    if len(normalized) < _MIN_VALUE_LENGTH:
        return []
    matched_hits: list[ValueAnchor] = []
    seen_raw: set[tuple[str, str, str, str]] = set()
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
        key = (row.table_name, row.field_name, row.raw_value, row.val_type)
        if key in seen_raw:
            continue
        seen_raw.add(key)
        matched_hits.append(candidate)

    if collapse_per_field:
        best: dict[tuple[str, str], ValueAnchor] = {}
        for candidate in matched_hits:
            key = (candidate.table_name, candidate.field_name)
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
        matched_hits = pruned

    ranked = sorted(
        matched_hits,
        key=lambda hit: (
            _TYPE_RANK.get(hit.val_type, 9),
            -len(hit.matched_text),
            hit.table_name,
            hit.field_name,
        ),
    )
    cap = 200 if not collapse_per_field else _MAX_HITS
    return ranked[:cap]


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
        elif hit.val_type == "person_alias":
            detail = "人设映射"
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
        rebuild_person_index,
        select_extract_scope,
    )
    from apps.knowledge.wiki.corpus_runtime import load_bound_corpus
    from apps.protocol import get_protocol_for_ds

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
    proto = get_protocol_for_ds(ds)
    total = 0
    for idx, table in enumerate(tables, 1):
        try:
            total += extract_table(
                session, ds=ds, table=table, store=store, proto=proto
            )
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
    try:
        from apps.datasource.instance_index.person_map import person_source_table_names

        all_tables = list(
            session.exec(select(CoreTable).where(CoreTable.ds_id == ds_id)).all()
        )
        person_tables = select_extract_scope(all_tables)
        seen = {str(item.table_name or "") for item in person_tables}
        by_name = {str(item.table_name or ""): item for item in all_tables}
        for name in person_source_table_names():
            extra = by_name.get(name)
            if extra is not None and name not in seen:
                person_tables.append(extra)
                seen.add(name)
        total += rebuild_person_index(session, ds=ds, tables=person_tables, proto=proto)
    except Exception as exc:
        SQLBotLogUtil.warning("value-index person map ds=%s failed: %s", ds_id, exc)
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
