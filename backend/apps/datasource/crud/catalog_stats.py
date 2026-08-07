"""Catalog cost stats keyed by ``(database_name, table_name)``."""

from __future__ import annotations

import datetime
import json
from typing import Any, Dict, List, Optional, Sequence, Tuple

from sqlalchemy import text
from sqlmodel import Session

from apps.db.db import get_session
from apps.datasource.models.datasource import CoreDatasource, CoreTable
from apps.datasource.utils.utils import aes_decrypt
from common.utils.utils import SQLBotLogUtil, equals_ignore_case
from apps.datasource.models.datasource import DatasourceConf

TableKey = Tuple[str, str]


def _key(database_name: str | None, table_name: str) -> TableKey:
    return ((database_name or "").strip(), (table_name or "").strip())


def _mysql_stats(
    ds: CoreDatasource, tables: Sequence[CoreTable]
) -> Dict[TableKey, Dict[str, Any]]:
    conf = DatasourceConf(**json.loads(aes_decrypt(ds.configuration)))
    default_db = conf.database
    out: Dict[TableKey, Dict[str, Any]] = {}
    if not tables:
        return out

    by_schema: Dict[str, list[str]] = {}
    for table in tables:
        schema = (table.database_name or default_db or "").strip()
        if not schema or not table.table_name:
            continue
        by_schema.setdefault(schema, []).append(table.table_name)

    try:
        with get_session(ds) as session:
            for schema, table_names in by_schema.items():
                placeholders = ", ".join([f":t{i}" for i in range(len(table_names))])
                params: Dict[str, Any] = {"schema": schema}
                for i, n in enumerate(table_names):
                    params[f"t{i}"] = n
                row_sql = text(
                    f"""
                    SELECT TABLE_NAME, TABLE_ROWS, DATA_LENGTH + INDEX_LENGTH AS BYTES
                    FROM information_schema.TABLES
                    WHERE TABLE_SCHEMA = :schema AND TABLE_NAME IN ({placeholders})
                    """
                )
                for r in session.execute(row_sql, params):
                    name = r[0]
                    key = _key(schema if schema != default_db else (tables[0].database_name or ""), name)
                    # Prefer explicit database_name from matching CoreTable when present.
                    matched = next(
                        (
                            t
                            for t in tables
                            if t.table_name == name
                            and (t.database_name or default_db) == schema
                        ),
                        None,
                    )
                    if matched is not None:
                        key = _key(matched.database_name, name)
                    out.setdefault(key, {})
                    out[key]["approx_rows"] = int(r[1] or 0)
                    out[key]["data_bytes"] = int(r[2] or 0)

                idx_sql = text(
                    f"""
                    SELECT TABLE_NAME, INDEX_NAME, GROUP_CONCAT(
                        COLUMN_NAME ORDER BY SEQ_IN_INDEX SEPARATOR ','
                    ) AS cols, NON_UNIQUE
                    FROM information_schema.STATISTICS
                    WHERE TABLE_SCHEMA = :schema AND TABLE_NAME IN ({placeholders})
                    GROUP BY TABLE_NAME, INDEX_NAME, NON_UNIQUE
                    ORDER BY TABLE_NAME, INDEX_NAME
                    """
                )
                by_table: Dict[str, List[str]] = {}
                for r in session.execute(idx_sql, params):
                    tname, iname, cols, non_unique = r[0], r[1], r[2] or "", r[3]
                    kind = "UNIQUE" if non_unique == 0 else "INDEX"
                    if iname == "PRIMARY":
                        kind = "PRIMARY"
                    by_table.setdefault(tname, []).append(f"{kind} {iname}({cols})")
                for tname, parts in by_table.items():
                    matched = next(
                        (
                            t
                            for t in tables
                            if t.table_name == tname
                            and (t.database_name or default_db) == schema
                        ),
                        None,
                    )
                    key = (
                        _key(matched.database_name, tname)
                        if matched is not None
                        else _key(schema, tname)
                    )
                    out.setdefault(key, {})
                    summary = "; ".join(parts[:24])
                    if len(parts) > 24:
                        summary += f"; …(+{len(parts)-24})"
                    out[key]["index_summary"] = summary
    except Exception as exc:
        SQLBotLogUtil.warning(f"mysql catalog stats failed ds={getattr(ds,'id',None)}: {exc}")
    return out


def _pg_stats(
    ds: CoreDatasource, tables: Sequence[CoreTable]
) -> Dict[TableKey, Dict[str, Any]]:
    out: Dict[TableKey, Dict[str, Any]] = {}
    if not tables:
        return out
    conf = DatasourceConf(**json.loads(aes_decrypt(ds.configuration)))
    schema = conf.dbSchema or "public"
    try:
        with get_session(ds) as session:
            for table in tables:
                name = table.table_name
                if not name:
                    continue
                key = _key(table.database_name, name)
                try:
                    q = text(
                        """
                        SELECT c.reltuples::bigint AS est_rows,
                               pg_total_relation_size(c.oid) AS bytes
                        FROM pg_class c
                        JOIN pg_namespace n ON n.oid = c.relnamespace
                        WHERE n.nspname = :schema AND c.relname = :name AND c.relkind = 'r'
                        """
                    )
                    row = session.execute(q, {"schema": schema, "name": name}).first()
                    if row:
                        out[key] = {
                            "approx_rows": max(int(row[0] or 0), 0),
                            "data_bytes": int(row[1] or 0),
                        }
                    iq = text(
                        """
                        SELECT indexrelid::regclass::text
                        FROM pg_index
                        JOIN pg_class c ON c.oid = indrelid
                        JOIN pg_namespace n ON n.oid = c.relnamespace
                        WHERE n.nspname = :schema AND c.relname = :name
                        LIMIT 24
                        """
                    )
                    parts = []
                    for r in session.execute(iq, {"schema": schema, "name": name}):
                        parts.append(str(r[0]))
                    if parts:
                        out.setdefault(key, {})["index_summary"] = "; ".join(parts)
                except Exception as ie:
                    SQLBotLogUtil.warning(f"pg stats table={name}: {ie}")
    except Exception as exc:
        SQLBotLogUtil.warning(f"pg catalog stats failed: {exc}")
    return out


def fetch_table_stats_map(
    ds: CoreDatasource, table_names: Sequence[str]
) -> Dict[str, Dict[str, Any]]:
    """Legacy name-only map for callers that only have table names."""
    tables = [
        CoreTable(table_name=n, database_name=None) for n in table_names if n
    ]
    keyed = fetch_table_stats_keyed(ds, tables)
    return {key[1]: value for key, value in keyed.items()}


def fetch_table_stats_keyed(
    ds: CoreDatasource, tables: Sequence[CoreTable]
) -> Dict[TableKey, Dict[str, Any]]:
    if not tables:
        return {}
    t = (ds.type or "").lower()
    if equals_ignore_case(t, "doris", "starrocks"):
        conf = DatasourceConf(**json.loads(aes_decrypt(ds.configuration)))
        catalog = (getattr(conf, "catalog", None) or "").strip()
        if catalog:
            # External catalog stats are not reliably available via information_schema.
            SQLBotLogUtil.info(
                f"skip catalog stats for external catalog ds={getattr(ds, 'id', None)} catalog={catalog}"
            )
            return {}
        # Internal SR/Doris: MySQL-compatible information_schema.
        return _mysql_stats(ds, tables)
    if equals_ignore_case(t, "mysql", "mariadb"):
        return _mysql_stats(ds, tables)
    if equals_ignore_case(t, "pg", "postgresql", "kingbase", "redshift", "excel"):
        return _pg_stats(ds, tables)
    return {}


def refresh_table_stats(
    session: Session, ds: CoreDatasource, tables: Sequence[CoreTable]
) -> None:
    """Persist stats onto the given CoreTable rows (already attached to session)."""
    if not tables:
        return
    stats_map = fetch_table_stats_keyed(ds, tables)
    if not stats_map:
        return
    now = datetime.datetime.now()
    for t in tables:
        s = stats_map.get(_key(t.database_name, t.table_name)) or {}
        if not s:
            # Fallback for legacy name-only maps
            s = stats_map.get(_key("", t.table_name)) or {}
        if not s:
            continue
        if "approx_rows" in s:
            t.approx_rows = s["approx_rows"]
        if "data_bytes" in s:
            t.data_bytes = s["data_bytes"]
        if "index_summary" in s:
            t.index_summary = s["index_summary"]
        t.stats_updated_at = now
        session.add(t)
    try:
        session.commit()
    except Exception as exc:
        session.rollback()
        SQLBotLogUtil.warning(f"refresh_table_stats commit failed: {exc}")


def load_table_stats_for_ds(
    session: Session,
    ds_id: int,
    table_names: Sequence[str],
    *,
    database_names: Sequence[str | None] | None = None,
) -> Dict[str, Dict[str, Any]]:
    """Read stored stats for validate_plan (no remote round-trip).

    Returns a name-keyed map for backward compatibility. When duplicate
    table names exist across databases, the first match wins unless
    ``database_names`` is aligned 1:1 with ``table_names``.
    """
    from sqlmodel import select
    from sqlalchemy import and_

    names = list(table_names)
    if not names:
        return {}
    rows = session.exec(
        select(CoreTable).where(
            and_(CoreTable.ds_id == ds_id, CoreTable.table_name.in_(names))
        )
    ).all()
    by_pair = {
        _key(t.database_name, t.table_name): t for t in rows if t.table_name
    }
    out: Dict[str, Dict[str, Any]] = {}
    if database_names is not None and len(database_names) == len(names):
        for db_name, name in zip(database_names, names, strict=True):
            t = by_pair.get(_key(db_name, name))
            if t is None:
                continue
            out[name] = {
                "approx_rows": t.approx_rows,
                "data_bytes": t.data_bytes,
                "index_summary": t.index_summary or "",
                "stats_updated_at": t.stats_updated_at,
                "database_name": t.database_name or "",
            }
        return out
    for t in rows:
        if t.table_name in out:
            continue
        out[t.table_name] = {
            "approx_rows": t.approx_rows,
            "data_bytes": t.data_bytes,
            "index_summary": t.index_summary or "",
            "stats_updated_at": t.stats_updated_at,
            "database_name": t.database_name or "",
        }
    return out
