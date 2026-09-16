"""INFORMATION_SCHEMA introspection + optional low-cardinality profile."""

from __future__ import annotations

import datetime as dt
import re
from typing import Any

from tools.wiki_extract.connect import MysqlTarget

_PII_COLUMNS = re.compile(
    r"password|secret|token|private_key|id_card|mobile|phone|salt",
    re.I,
)
_PROFILE_TYPES = frozenset(
    {"varchar", "char", "int", "tinyint", "smallint", "bigint", "enum"}
)


def _base_type(mysql_type: str) -> str:
    return (mysql_type or "").split("(")[0].strip().lower()


def introspect(
    conn: Any,
    target: MysqlTarget,
    *,
    tables: set[str] | None = None,
    skip_profile: bool = False,
    max_distinct: int = 32,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return (catalog, profile) dicts ready to dump as YAML."""
    schema = target.database
    table_rows = _fetch_tables(conn, schema, tables)
    columns = _fetch_columns(conn, schema, tables)
    primaries = _fetch_primaries(conn, schema, tables)
    indexes = _fetch_indexes(conn, schema, tables)

    catalog_tables: dict[str, Any] = {}
    for name, meta in table_rows.items():
        catalog_tables[name] = {
            "engine": meta["engine"],
            "comment": meta["comment"],
            "rows_estimate": meta["rows_estimate"],
            "columns": columns.get(name, {}),
            "primary_key": primaries.get(name, []),
            "indexes": indexes.get(name, []),
        }

    stamp = dt.date.today().isoformat()
    catalog = {
        "schema_version": "1.0",
        "generated_at": stamp,
        "source": "tools.wiki_extract.introspect",
        "host": target.host,
        "port": target.port,
        "database": schema,
        "tables": catalog_tables,
    }
    profile_tables: dict[str, Any] = {}
    if not skip_profile:
        for tname, tmeta in catalog_tables.items():
            stats = _profile_table(
                conn,
                schema,
                tname,
                tmeta,
                max_distinct=max_distinct,
            )
            profile_tables[tname] = {
                "rows_estimate": tmeta["rows_estimate"],
                "column_stats": stats,
            }
    profile = {
        "schema_version": "1.0",
        "generated_at": stamp,
        "source": "tools.wiki_extract.introspect",
        "database": schema,
        "tables": profile_tables,
    }
    return catalog, profile


def _fetch_tables(
    conn: Any, schema: str, tables: set[str] | None
) -> dict[str, dict[str, Any]]:
    sql = (
        "SELECT TABLE_NAME AS name, ENGINE AS engine, TABLE_COMMENT AS comment, "
        "TABLE_ROWS AS rows_estimate FROM information_schema.TABLES "
        "WHERE TABLE_SCHEMA = %s AND TABLE_TYPE = 'BASE TABLE'"
    )
    out: dict[str, dict[str, Any]] = {}
    with conn.cursor() as cur:
        cur.execute(sql, (schema,))
        for row in cur.fetchall():
            name = str(row["name"])
            if tables and name not in tables:
                continue
            out[name] = {
                "engine": row.get("engine") or "InnoDB",
                "comment": (row.get("comment") or "").strip(),
                "rows_estimate": int(row.get("rows_estimate") or 0),
            }
    return out


def _fetch_columns(
    conn: Any, schema: str, tables: set[str] | None
) -> dict[str, dict[str, Any]]:
    sql = (
        "SELECT TABLE_NAME AS t, COLUMN_NAME AS name, COLUMN_TYPE AS type, "
        "IS_NULLABLE AS nullable, COLUMN_DEFAULT AS default_value, "
        "COLUMN_KEY AS col_key, EXTRA AS extra, COLUMN_COMMENT AS comment, "
        "ORDINAL_POSITION AS pos FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA = %s ORDER BY TABLE_NAME, ORDINAL_POSITION"
    )
    out: dict[str, dict[str, Any]] = {}
    with conn.cursor() as cur:
        cur.execute(sql, (schema,))
        for row in cur.fetchall():
            tname = str(row["t"])
            if tables and tname not in tables:
                continue
            out.setdefault(tname, {})
            out[tname][str(row["name"])] = {
                "type": str(row["type"] or ""),
                "nullable": str(row["nullable"] or "YES").upper() == "YES",
                "default": row.get("default_value"),
                "key": str(row["col_key"] or ""),
                "extra": str(row["extra"] or ""),
                "comment": (row.get("comment") or "").strip(),
                "pos": int(row["pos"] or 0),
            }
    return out


def _fetch_primaries(
    conn: Any, schema: str, tables: set[str] | None
) -> dict[str, list[str]]:
    sql = (
        "SELECT TABLE_NAME AS t, COLUMN_NAME AS name, ORDINAL_POSITION AS pos "
        "FROM information_schema.KEY_COLUMN_USAGE "
        "WHERE TABLE_SCHEMA = %s AND CONSTRAINT_NAME = 'PRIMARY' "
        "ORDER BY TABLE_NAME, ORDINAL_POSITION"
    )
    out: dict[str, list[str]] = {}
    with conn.cursor() as cur:
        cur.execute(sql, (schema,))
        for row in cur.fetchall():
            tname = str(row["t"])
            if tables and tname not in tables:
                continue
            out.setdefault(tname, []).append(str(row["name"]))
    return out


def _fetch_indexes(
    conn: Any, schema: str, tables: set[str] | None
) -> dict[str, list[dict[str, Any]]]:
    sql = (
        "SELECT TABLE_NAME AS t, INDEX_NAME AS name, NON_UNIQUE AS non_unique, "
        "COLUMN_NAME AS col, SEQ_IN_INDEX AS seq FROM information_schema.STATISTICS "
        "WHERE TABLE_SCHEMA = %s ORDER BY TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX"
    )
    grouped: dict[tuple[str, str], dict[str, Any]] = {}
    with conn.cursor() as cur:
        cur.execute(sql, (schema,))
        for row in cur.fetchall():
            tname = str(row["t"])
            if tables and tname not in tables:
                continue
            key = (tname, str(row["name"]))
            item = grouped.setdefault(
                key,
                {
                    "name": str(row["name"]),
                    "unique": int(row["non_unique"] or 0) == 0,
                    "columns": [],
                },
            )
            item["columns"].append(str(row["col"]))
    out: dict[str, list[dict[str, Any]]] = {}
    for (tname, _), item in grouped.items():
        out.setdefault(tname, []).append(item)
    return out


def _profile_table(
    conn: Any,
    schema: str,
    tname: str,
    tmeta: dict[str, Any],
    *,
    max_distinct: int,
) -> dict[str, Any]:
    if int(tmeta.get("rows_estimate") or 0) <= 0:
        return {}
    pk = set(tmeta.get("primary_key") or [])
    stats: dict[str, Any] = {}
    for cname, cinfo in tmeta.get("columns", {}).items():
        if cname in pk or _PII_COLUMNS.search(cname):
            continue
        if _base_type(str(cinfo.get("type") or "")) not in _PROFILE_TYPES:
            continue
        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"SELECT COUNT(DISTINCT `{cname}`) AS n FROM `{schema}`.`{tname}`"
                )
                n_distinct = int((cur.fetchone() or {}).get("n") or 0)
                if n_distinct <= 0 or n_distinct > max_distinct:
                    continue
                cur.execute(
                    f"SELECT `{cname}` AS v, COUNT(*) AS c FROM `{schema}`.`{tname}` "
                    f"WHERE `{cname}` IS NOT NULL GROUP BY 1 ORDER BY 2 DESC "
                    f"LIMIT %s",
                    (max_distinct,),
                )
                values = {str(row["v"]): int(row["c"]) for row in cur.fetchall()}
            stats[cname] = {"distinct": n_distinct, "values": values}
        except Exception:
            continue
    return stats


def is_pii_column(name: str) -> bool:
    return bool(_PII_COLUMNS.search(name))
