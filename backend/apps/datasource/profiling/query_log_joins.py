"""Mine EQUI_JOIN candidates from historical successful SQL."""

from __future__ import annotations

import re
from collections import Counter
from typing import Any, Iterable

from sqlmodel import Session, select

from apps.chat.models.chat_model import ChatRecord
from apps.datasource.models.datasource import CoreField, CoreTable
from apps.datasource.profiling.models import RelationSource
from common.utils.utils import SQLBotLogUtil

_EQ_JOIN = re.compile(
    r"(?P<lalias>[A-Za-z_][\w$]*)\.(?P<lcol>[A-Za-z_][\w$]*)\s*=\s*"
    r"(?P<ralias>[A-Za-z_][\w$]*)\.(?P<rcol>[A-Za-z_][\w$]*)",
    re.I,
)
_FROM_TABLE = re.compile(
    r"\b(?:FROM|JOIN)\s+"
    r"(?:`?\"?\[?([A-Za-z_][\w$]*)`?\"?\]?\.)?"
    r"`?\"?\[?([A-Za-z_][\w$]*)`?\"?\]?"
    r"(?:\s+(?:AS\s+)?`?\"?\[?([A-Za-z_][\w$]*)`?\"?\]?)?",
    re.I,
)


def _strip_sql_noise(sql: str) -> str:
    text = re.sub(r"/\*.*?\*/", " ", sql, flags=re.S)
    text = re.sub(r"--.*?$", " ", text, flags=re.M)
    return text


def extract_equi_join_pairs(
    sql: str,
) -> list[tuple[str, str, str, str, str, str]]:
    """Return ``(lt, lc, rt, rc, left_db, right_db)`` using alias map.

    ``*_db`` is empty when the SQL did not qualify the table. Best-effort
    regex parse; failures return empty (never invent pairs).
    """
    if not sql or not str(sql).strip():
        return []
    text = _strip_sql_noise(str(sql))
    alias_to_table: dict[str, tuple[str, str]] = {}
    for match in _FROM_TABLE.finditer(text):
        db, table, alias = match.group(1), match.group(2), match.group(3)
        if not table:
            continue
        entry = ((db or "").strip(), table)
        key = (alias or table).lower()
        alias_to_table[key] = entry
        alias_to_table[table.lower()] = entry
        if db:
            alias_to_table[f"{db.lower()}.{table.lower()}"] = entry
    pairs: list[tuple[str, str, str, str, str, str]] = []
    for match in _EQ_JOIN.finditer(text):
        la, lc, ra, rc = (
            match.group("lalias").lower(),
            match.group("lcol"),
            match.group("ralias").lower(),
            match.group("rcol"),
        )
        left = alias_to_table.get(la)
        right = alias_to_table.get(ra)
        if not left or not right:
            continue
        lt, rt = left[1], right[1]
        if lt.lower() == rt.lower() and left[0].lower() == right[0].lower():
            continue
        pairs.append((lt, lc, rt, rc, left[0], right[0]))
    return pairs


def _confidence_from_count(count: int) -> float:
    # Saturates toward ~0.9
    return round(min(0.9, 0.35 + 0.1 * count), 4)


def mine_query_log_join_candidates(
    session: Session,
    *,
    ds_id: int,
    oid: int,
    min_count: int = 2,
    sql_limit: int = 200,
    upsert: bool = True,
) -> dict[str, Any]:
    """Parse recent successful SQL for the datasource and upsert CANDIDATE joins."""
    from datetime import datetime

    from apps.datasource.profiling.models import (
        FieldRelation,
        RelationKind,
        RelationStatus,
    )

    stmt = (
        select(ChatRecord)
        .where(ChatRecord.datasource == ds_id)
        .order_by(ChatRecord.id.desc())
        .limit(max(1, min(int(sql_limit), 500)))
    )
    records = [r for r in session.exec(stmt).all() if (r.sql or "").strip()]
    counter: Counter[tuple[str, str, str, str]] = Counter()
    parsed = 0
    for rec in records:
        sql = (rec.sql or "").strip()
        if rec.error:
            continue
        if rec.finish is False:
            continue
        pairs = extract_equi_join_pairs(sql)
        if pairs:
            parsed += 1
        for pair in pairs:
            a = (
                pair[4].lower(),
                pair[0].lower(),
                pair[1].lower(),
                pair[5].lower(),
                pair[2].lower(),
                pair[3].lower(),
            )
            b = (
                pair[5].lower(),
                pair[2].lower(),
                pair[3].lower(),
                pair[4].lower(),
                pair[0].lower(),
                pair[1].lower(),
            )
            key = a if a <= b else b
            counter[key] += 1

    from apps.datasource.models.datasource import resolve_catalog_table

    tables = session.exec(
        select(CoreTable).where(CoreTable.ds_id == ds_id, CoreTable.checked == True)  # noqa: E712
    ).all()
    fields = session.exec(
        select(CoreField).where(CoreField.ds_id == ds_id, CoreField.checked == True)  # noqa: E712
    ).all()
    field_index: dict[tuple[int, str], CoreField] = {}
    for f in fields:
        if f.id is None or not f.field_name:
            continue
        field_index[(int(f.table_id), f.field_name.lower())] = f

    upserted = 0
    skipped = 0
    candidates: list[dict[str, Any]] = []
    now = datetime.now()
    for (ldb, lt, lc, rdb, rt, rc), count in counter.items():
        if count < min_count:
            skipped += 1
            continue
        left_table = resolve_catalog_table(
            tables, lt, database_name=ldb or None
        )
        right_table = resolve_catalog_table(
            tables, rt, database_name=rdb or None
        )
        if left_table is None or right_table is None or left_table.id is None or right_table.id is None:
            skipped += 1
            continue
        left_field = field_index.get((int(left_table.id), lc))
        right_field = field_index.get((int(right_table.id), rc))
        if left_field is None or right_field is None or left_field.id is None or right_field.id is None:
            skipped += 1
            continue
        conf = _confidence_from_count(count)
        evidence = {
            "query_log": True,
            "cooccur_count": count,
            "algo": "regex_equi_join_v1",
        }
        item = {
            "source_field_id": int(left_field.id),
            "target_field_id": int(right_field.id),
            "source_table": left_table.table_name,
            "source_field": left_field.field_name,
            "target_table": right_table.table_name,
            "target_field": right_field.field_name,
            "cooccur_count": count,
            "confidence": conf,
        }
        candidates.append(item)
        if not upsert:
            continue
        try:
            existing = session.exec(
                select(FieldRelation).where(
                    FieldRelation.ds_id == ds_id,
                    FieldRelation.source_field_id == int(left_field.id),
                    FieldRelation.target_field_id == int(right_field.id),
                    FieldRelation.kind == RelationKind.EQUI_JOIN.value,
                )
            ).first()
            if existing is not None:
                if existing.status in {
                    RelationStatus.CONFIRMED.value,
                    RelationStatus.REJECTED.value,
                    RelationStatus.DISABLED.value,
                }:
                    skipped += 1
                    continue
                existing.status = RelationStatus.CANDIDATE.value
                existing.confidence = conf
                existing.evidence = evidence
                existing.source = RelationSource.QUERY_LOG.value
                existing.update_time = now
                session.add(existing)
            else:
                session.add(
                    FieldRelation(
                        oid=oid,
                        ds_id=ds_id,
                        source_table_id=int(left_table.id),
                        source_field_id=int(left_field.id),
                        target_table_id=int(right_table.id),
                        target_field_id=int(right_field.id),
                        kind=RelationKind.EQUI_JOIN.value,
                        status=RelationStatus.CANDIDATE.value,
                        source=RelationSource.QUERY_LOG.value,
                        confidence=conf,
                        evidence=evidence,
                        create_time=now,
                        update_time=now,
                    )
                )
            upserted += 1
        except Exception as exc:
            SQLBotLogUtil.warning(f"query_log upsert skipped: {exc}")
            skipped += 1

    if upsert:
        session.commit()
    return {
        "sql_scanned": len(records),
        "sql_with_joins": parsed,
        "pair_buckets": len(counter),
        "candidates": candidates,
        "upserted": upserted,
        "skipped": skipped,
        "min_count": min_count,
    }


def summarize_pairs(pairs: Iterable[tuple[str, str, str, str]]) -> list[str]:
    return [f"{a}.{b}={c}.{d}" for a, b, c, d in pairs]
