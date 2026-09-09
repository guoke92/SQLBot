"""Single display projection for wiki-backed enum value labels.

Query result cells are translated here once — before they enter result_dataset
or TurnAnswer preview — so row-store APIs, Excel export, and the chat table
share one projection. Raw codes stay recoverable via returned value_labels.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


def _sql_alias_columns(sql: str, dialect: str) -> list[dict[str, str]]:
    """Resolve SELECT projections: result alias → physical column (+ table)."""
    projections: list[dict[str, str]] = []
    try:
        import sqlglot
        from sqlglot import exp

        for statement in sqlglot.parse(sql, dialect=dialect):
            if statement is None:
                continue
            table_alias_map: dict[str, str] = {}
            for tbl in statement.find_all(exp.Table):
                t_name = str(tbl.name).strip()
                t_alias = str(tbl.alias).strip() if tbl.alias else ""
                if t_alias:
                    table_alias_map[t_alias] = t_name
                table_alias_map[t_name] = t_name

            for select in statement.find_all(exp.Select):
                for proj in select.expressions:
                    inner = proj.this
                    if not isinstance(inner, exp.Column):
                        continue
                    qualifier = str(inner.table or "").strip()
                    if qualifier and qualifier in table_alias_map:
                        qualifier = table_alias_map[qualifier]
                    projections.append(
                        {
                            "alias": str(proj.alias_or_name or inner.name),
                            "column": str(inner.name),
                            "table": qualifier,
                        }
                    )
    except Exception:
        return []
    return projections


def wiki_table_columns(table: str, *, ds_id: int | None = None) -> set[str]:
    """Column names from the wiki ground:table page; empty when unavailable."""
    try:
        from apps.chat.steps.wiki_recall import _store

        store = _store(ds_id)
        if store is None:
            return set()
        page = store.pages.get(table) or store.pages.get(f"tables/{table}")
        if page is None and hasattr(store, "get_page"):
            page = store.get_page(table)
            if page is not None and getattr(page, "type", "table") not in (
                "table",
                None,
                "",
            ):
                page = store.pages.get(f"tables/{table}")
        if page is None:
            return set()
        for anchor in getattr(page, "ground_blocks", ()) or ():
            if anchor.kind != "table":
                continue
            return {
                str(f.get("name") or "")
                for f in anchor.data.get("fields") or []
                if isinstance(f, dict) and f.get("name")
            }
        return set()
    except Exception:
        return set()


def is_wiki_enum_discovery_sql(
    sql: str,
    enum_carriers: set[str],
    *,
    dialect: str = "mysql",
) -> bool:
    """True when SQL is a DISTINCT dictionary dump over Wiki enum columns.

    Wiki enum pages are the value authority. ``SELECT DISTINCT enum_col …``
    with no WHERE is a live dictionary probe. GROUP BY distribution queries
    (e.g. count by status) remain allowed — they are user analytics, not
    value discovery.
    """
    if not sql.strip() or not enum_carriers:
        return False
    try:
        import sqlglot
        from sqlglot import exp

        statements = [item for item in sqlglot.parse(sql, dialect=dialect) if item]
    except Exception:
        return False
    if len(statements) != 1:
        return False
    select = (
        statements[0]
        if isinstance(statements[0], exp.Select)
        else statements[0].find(exp.Select)
    )
    if select is None or not select.args.get("distinct"):
        return False
    if select.find(exp.Where) is not None:
        return False
    if select.args.get("group") is not None:
        return False

    projected: list[exp.Column] = []
    for proj in select.expressions:
        inner = proj.this if isinstance(proj, exp.Alias) else proj
        if isinstance(inner, exp.Column):
            projected.append(inner)
            continue
        if isinstance(inner, exp.AggFunc):
            continue
        return False
    if not projected:
        return False

    def _is_enum_column(col: exp.Column) -> bool:
        name = str(col.name or "").casefold()
        table = str(col.table or "").casefold()
        if name in enum_carriers:
            return True
        if table and f"{table}.{name}" in enum_carriers:
            return True
        return False

    return all(_is_enum_column(col) for col in projected)


def enum_refs_for_query(
    *,
    sql: str,
    fields: Sequence[str],
    tables: Sequence[str] | None = None,
    dialect: str = "mysql",
    ds_id: int | None = None,
) -> tuple[list[str], dict[str, str]]:
    """Build ``表.列`` refs and result-alias → ref map for enum translation."""
    refs: list[str] = []
    alias_to_ref: dict[str, str] = {}
    table_list = [str(t) for t in (tables or []) if str(t).strip()]
    if not table_list and sql:
        try:
            import sqlglot
            from sqlglot import exp

            for statement in sqlglot.parse(sql, dialect=dialect):
                if statement is None:
                    continue
                for tbl in statement.find_all(exp.Table):
                    t_name = str(tbl.name).strip()
                    if t_name and t_name not in table_list:
                        table_list.append(t_name)
        except Exception:
            pass
    field_list = [str(f) for f in fields]
    if not field_list:
        return refs, alias_to_ref

    projections = _sql_alias_columns(sql, dialect) if sql else []
    alias_map = {p["alias"]: p for p in projections}
    table_columns: dict[str, set[str]] = {
        table: wiki_table_columns(table, ds_id=ds_id) for table in table_list
    }
    known = {col for cols in table_columns.values() for col in cols}

    resolved: list[tuple[str, str, str]] = []
    seen: set[str] = set()
    for field in field_list:
        proj = alias_map.get(field)
        if proj is not None and proj["column"] not in seen:
            seen.add(proj["column"])
            resolved.append((field, proj["column"], proj["table"]))
    if resolved:
        for result_field, column, table_qualifier in resolved:
            candidates = (
                [table_qualifier]
                if table_qualifier and table_qualifier in table_columns
                else [t for t, cols in table_columns.items() if column in cols]
                or list(table_columns)
            )
            for table in candidates:
                if not known or column in (table_columns.get(table) or set()):
                    ref = f"{table}.{column}"
                    if ref not in refs:
                        refs.append(ref)
                    alias_to_ref.setdefault(result_field, ref)
                    break
        return refs, alias_to_ref

    for table in table_list:
        cols = table_columns.get(table) or set()
        for field in field_list:
            if known and field not in cols:
                continue
            ref = f"{table}.{field}"
            if ref not in refs:
                refs.append(ref)
    return refs, alias_to_ref


def apply_wiki_enum_labels(
    *,
    sql: str,
    fields: Sequence[str],
    rows: Sequence[Mapping[str, Any]],
    llm_service: Any = None,
    tables: Sequence[str] | None = None,
    dialect: str | None = None,
    ds_id: int | None = None,
) -> tuple[list[dict[str, Any]], dict[str, dict[str, str]]]:
    """Translate enum cells via wiki maps. Idempotent on already-labeled cells."""
    from apps.chat.steps.wiki_recall import enum_maps_for, translate_enum_cells

    safe_rows = [dict(row) for row in rows if isinstance(row, Mapping)]
    if not safe_rows or not fields:
        return safe_rows, {}

    resolved_dialect = dialect
    if not resolved_dialect and llm_service is not None:
        resolved_dialect = str(
            getattr(getattr(llm_service, "protocol", None), "type_key", None) or "mysql"
        )
    resolved_dialect = resolved_dialect or "mysql"

    resolved_ds = ds_id
    if resolved_ds is None and llm_service is not None:
        ds = getattr(llm_service, "ds", None) or getattr(
            llm_service, "datasource", None
        )
        resolved_ds = getattr(ds, "id", None)

    refs, alias_to_ref = enum_refs_for_query(
        sql=sql,
        fields=fields,
        tables=tables,
        dialect=resolved_dialect,
        ds_id=resolved_ds,
    )
    if not refs:
        return safe_rows, {}
    maps = enum_maps_for(refs, ds_id=resolved_ds)
    if not maps:
        return safe_rows, {}
    return translate_enum_cells(
        [str(item) for item in fields],
        safe_rows,
        maps,
        alias_to_ref=alias_to_ref,
    )
