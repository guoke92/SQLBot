"""SQL catalog extraction and dialect-specific structural checks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import sqlglot
from sqlglot import exp
from sqlglot.optimizer.scope import Scope, traverse_scope


@dataclass(frozen=True)
class PhysicalColumnRef:
    column_name: str
    table_name: str | None = None
    database_name: str | None = None
    candidate_tables: tuple[str, ...] = ()
    #: Parallel to ``candidate_tables`` (empty string when the SQL omits db).
    candidate_databases: tuple[str, ...] = ()


@dataclass(frozen=True)
class SqlIdentifierUsage:
    physical_tables: frozenset[str]
    physical_columns: tuple[PhysicalColumnRef, ...]


def _norm(value: Any) -> str:
    return str(value or "").replace("`", "").replace('"', "").strip()


def _select_aliases(scope: Scope) -> set[str]:
    if not isinstance(scope.expression, exp.Select):
        return set()
    return {
        _norm(item.alias).casefold()
        for item in scope.expression.expressions
        if item is not None and _norm(item.alias)
    }


def _is_output_alias(column: exp.Column, scope: Scope) -> bool:
    if column.table or _norm(column.name).casefold() not in _select_aliases(scope):
        return False
    parent = column.parent
    while parent is not None and parent is not scope.expression:
        if isinstance(parent, exp.Group | exp.Order | exp.Having | exp.Qualify):
            return True
        parent = parent.parent
    return False


def collect_sql_identifier_usage(sql: str, dialect: str) -> SqlIdentifierUsage:
    physical_tables: set[str] = set()
    refs: list[PhysicalColumnRef] = []
    seen: set[PhysicalColumnRef] = set()
    for statement in sqlglot.parse(sql, dialect=dialect):
        if statement is None:
            continue
        for scope in traverse_scope(statement):
            sources = {
                _norm(alias).casefold(): source
                for alias, source in scope.sources.items()
            }
            physical_scope: list[tuple[str, str]] = []
            has_virtual = False
            for source in sources.values():
                if isinstance(source, exp.Table):
                    table = _norm(source.name)
                    database = _norm(source.db)
                    if table:
                        physical_tables.add(table)
                        pair = (database, table)
                        if pair not in physical_scope:
                            physical_scope.append(pair)
                else:
                    has_virtual = True
            for column in scope.columns:
                name = _norm(column.name)
                if not name or name == "*" or _is_output_alias(column, scope):
                    continue
                ref: PhysicalColumnRef | None = None
                table_ref = _norm(column.table).casefold()
                if table_ref and isinstance(sources.get(table_ref), exp.Table):
                    source_table = sources[table_ref]
                    ref = PhysicalColumnRef(
                        name,
                        table_name=_norm(source_table.name),
                        database_name=_norm(source_table.db) or None,
                    )
                elif physical_scope and not has_virtual:
                    ref = PhysicalColumnRef(
                        name,
                        candidate_tables=tuple(table for _db, table in physical_scope),
                        candidate_databases=tuple(db for db, _table in physical_scope),
                    )
                if ref is not None and ref not in seen:
                    refs.append(ref)
                    seen.add(ref)
    return SqlIdentifierUsage(
        physical_tables=frozenset(physical_tables),
        physical_columns=tuple(refs),
    )


_OUTPUT_SCOPED_ORDER_DIALECTS = frozenset({"hive", "spark", "spark2", "databricks"})


def order_by_scope_error(sql: str, dialect: str | None) -> str | None:
    """Report qualified ORDER BY references an engine is certain to refuse."""
    if not sql or dialect not in _OUTPUT_SCOPED_ORDER_DIALECTS:
        return None
    try:
        statements = sqlglot.parse(sql, dialect=dialect)
    except Exception:
        return None
    fixes: dict[str, str] = {}
    for statement in statements:
        if statement is None:
            continue
        for select in statement.find_all(exp.Select):
            order = select.args.get("order")
            if order is None:
                continue
            outputs = {
                _norm(projection.alias_or_name).casefold()
                for projection in select.expressions
            }
            for column in order.find_all(exp.Column):
                if not _norm(column.table):
                    continue
                name = _norm(column.name)
                fixes.setdefault(
                    column.sql(dialect=dialect),
                    f"use `{name}`"
                    if name.casefold() in outputs
                    else f"`{name}` is not in the SELECT output; "
                    "project it or drop it from ORDER BY",
                )
    if not fixes:
        return None
    return (
        "ORDER BY on this engine can only reference SELECT output names, "
        "never table-qualified columns: "
        + "; ".join(f"{column} -> {fix}" for column, fix in fixes.items())
    )
