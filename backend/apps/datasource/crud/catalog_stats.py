"""Refresh per-table catalog cost stats (row estimates, size, indexes).

Stats live on ``CoreTable`` and are consumed by ``SqlProtocol.validate_plan``
and NLQ boundary probes. Keep discovery here — do not re-query information_schema
ad hoc inside graph nodes.
"""

from __future__ import annotations

import datetime
import json
from typing import Any, Dict, List, Optional, Sequence

from sqlalchemy import text
from sqlmodel import Session

from apps.db.db import get_session
from apps.datasource.models.datasource import CoreDatasource, CoreTable
from apps.datasource.utils.utils import aes_decrypt
from apps.db.constant import DB
from common.utils.utils import SQLBotLogUtil, equals_ignore_case
from apps.datasource.models.datasource import DatasourceConf


def _mysql_stats(ds: CoreDatasource, table_names: Sequence[str]) -> Dict[str, Dict[str, Any]]:
    """Return {table_name: {approx_rows, data_bytes, index_summary}} for MySQL-family."""
    conf = DatasourceConf(**json.loads(aes_decrypt(ds.configuration)))
    db_name = conf.database
    out: Dict[str, Dict[str, Any]] = {}
    if not table_names:
        return out
    # information_schema is cheap enough for checked tables only
    placeholders = ", ".join([f":t{i}" for i in range(len(table_names))])
    params: Dict[str, Any] = {"schema": db_name}
    for i, n in enumerate(table_names):
        params[f"t{i}"] = n
    try:
        with get_session(ds) as session:
            row_sql = text(
                f"""
                SELECT TABLE_NAME, TABLE_ROWS, DATA_LENGTH + INDEX_LENGTH AS BYTES
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = :schema AND TABLE_NAME IN ({placeholders})
                """
            )
            for r in session.execute(row_sql, params):
                name = r[0]
                out.setdefault(name, {})
                # TABLE_ROWS is approximate for InnoDB
                out[name]["approx_rows"] = int(r[1] or 0)
                out[name]["data_bytes"] = int(r[2] or 0)

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
                out.setdefault(tname, {})
                # Cap stored text
                summary = "; ".join(parts[:24])
                if len(parts) > 24:
                    summary += f"; …(+{len(parts)-24})"
                out[tname]["index_summary"] = summary
    except Exception as exc:
        SQLBotLogUtil.warning(f"mysql catalog stats failed ds={getattr(ds,'id',None)}: {exc}")
    return out


def _pg_stats(ds: CoreDatasource, table_names: Sequence[str]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    if not table_names:
        return out
    conf = DatasourceConf(**json.loads(aes_decrypt(ds.configuration)))
    schema = conf.dbSchema or "public"
    try:
        with get_session(ds) as session:
            for name in table_names:
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
                        out[name] = {
                            "approx_rows": max(int(row[0] or 0), 0),
                            "data_bytes": int(row[1] or 0),
                        }
                    iq = text(
                        """
                        SELECT indexrelid::regclass::text, pg_get_indexdef(indexrelid)
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
                        out.setdefault(name, {})["index_summary"] = "; ".join(parts)
                except Exception as ie:
                    SQLBotLogUtil.warning(f"pg stats table={name}: {ie}")
    except Exception as exc:
        SQLBotLogUtil.warning(f"pg catalog stats failed: {exc}")
    return out


def fetch_table_stats_map(
    ds: CoreDatasource, table_names: Sequence[str]
) -> Dict[str, Dict[str, Any]]:
    names = [n for n in table_names if n]
    if not names:
        return {}
    t = (ds.type or "").lower()
    if equals_ignore_case(t, "doris", "starrocks"):
        conf = DatasourceConf(**json.loads(aes_decrypt(ds.configuration)))
        catalog = (getattr(conf, "catalog", None) or "").strip()
        if catalog:
            # External catalog table stats are unreliable / unavailable via information_schema.
            SQLBotLogUtil.info(
                f"skip catalog stats for external catalog ds={getattr(ds, 'id', None)} catalog={catalog}"
            )
            return {}
        # Internal tables: reuse mysql-family path only when SQLAlchemy session works.
        # StarRocks/Doris are py_driver — skip rather than fail via get_session.
        SQLBotLogUtil.info(
            f"skip catalog stats for py_driver ds type={t} id={getattr(ds, 'id', None)}"
        )
        return {}
    if equals_ignore_case(t, "mysql", "mariadb"):
        return _mysql_stats(ds, names)
    if equals_ignore_case(t, "pg", "postgresql", "kingbase", "redshift"):
        return _pg_stats(ds, names)
    # Other engines: skip quietly
    return {}


def refresh_table_stats(
    session: Session, ds: CoreDatasource, tables: Sequence[CoreTable]
) -> None:
    """Persist stats onto the given CoreTable rows (already attached to session)."""
    if not tables:
        return
    names = [t.table_name for t in tables if t.table_name]
    stats_map = fetch_table_stats_map(ds, names)
    if not stats_map:
        return
    now = datetime.datetime.now()
    for t in tables:
        s = stats_map.get(t.table_name) or {}
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
    session: Session, ds_id: int, table_names: Sequence[str]
) -> Dict[str, Dict[str, Any]]:
    """Read stored stats for validate_plan (no remote round-trip)."""
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
    out: Dict[str, Dict[str, Any]] = {}
    for t in rows:
        out[t.table_name] = {
            "approx_rows": t.approx_rows,
            "data_bytes": t.data_bytes,
            "index_summary": t.index_summary or "",
            "stats_updated_at": t.stats_updated_at,
        }
    return out
