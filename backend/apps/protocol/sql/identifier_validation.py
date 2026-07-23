"""Scope-aware SQL identifier extraction for catalog validation.

The SQL protocol validates only physical database tables and columns against
SQLBot metadata. CTEs and derived tables are query-local relations: their
output aliases must never be mistaken for physical catalog columns.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import sqlglot
from sqlglot import exp
from sqlglot.optimizer.scope import Scope, traverse_scope


@dataclass(frozen=True)
class PhysicalColumnRef:
    """One column reference that can be checked against physical metadata."""

    column_name: str
    table_name: str | None = None
    candidate_tables: tuple[str, ...] = ()


@dataclass(frozen=True)
class SqlIdentifierUsage:
    """Physical catalog usage extracted from a SQL statement."""

    physical_tables: frozenset[str]
    physical_columns: tuple[PhysicalColumnRef, ...]


def _norm(name: Any) -> str:
    if not name:
        return ""
    return str(name).replace("`", "").replace('"', "").strip()


def _select_aliases(scope: Scope) -> set[str]:
    expression = scope.expression
    if not isinstance(expression, exp.Select):
        return set()
    aliases: set[str] = set()
    for projection in expression.expressions:
        if projection is None:
            continue
        alias = _norm(projection.alias)
        if alias:
            aliases.add(alias.lower())
    return aliases


def _is_output_alias_reference(
    column: exp.Column,
    scope: Scope,
    select_aliases: set[str],
) -> bool:
    """Return true only for GROUP/ORDER/HAVING references to SELECT aliases."""
    if column.table or _norm(column.name).lower() not in select_aliases:
        return False
    parent = column.parent
    while parent is not None and parent is not scope.expression:
        if isinstance(parent, (exp.Group, exp.Order, exp.Having, exp.Qualify)):
            return True
        parent = parent.parent
    return False


def collect_sql_identifier_usage(sql: str, dialect: str) -> SqlIdentifierUsage:
    """Extract physical relations with lexical SQL scope awareness.

    ``sqlglot.optimizer.scope`` resolves each SELECT independently. A source is
    an ``exp.Table`` only when it is a physical table in that scope; CTE and
    derived-table sources are represented by ``Scope`` and are intentionally
    excluded from physical catalog checks.
    """
    physical_tables: set[str] = set()
    refs: list[PhysicalColumnRef] = []
    seen_refs: set[PhysicalColumnRef] = set()

    for statement in sqlglot.parse(sql, dialect=dialect):
        if statement is None:
            continue
        for scope in traverse_scope(statement):
            sources_by_alias: dict[str, Any] = {}
            physical_scope_tables: list[str] = []
            has_virtual_source = False

            for alias, source in scope.sources.items():
                sources_by_alias[_norm(alias).lower()] = source
                if isinstance(source, exp.Table):
                    table_name = _norm(source.name)
                    if table_name:
                        physical_tables.add(table_name)
                        if table_name not in physical_scope_tables:
                            physical_scope_tables.append(table_name)
                else:
                    # CTE, derived table or nested query scope.
                    has_virtual_source = True

            select_aliases = _select_aliases(scope)

            for column in scope.columns:
                column_name = _norm(column.name)
                if not column_name or column_name == "*":
                    continue
                if _is_output_alias_reference(column, scope, select_aliases):
                    continue

                ref: PhysicalColumnRef | None = None
                table_ref = _norm(column.table)
                if table_ref:
                    source = sources_by_alias.get(table_ref.lower())
                    if isinstance(source, exp.Table):
                        table_name = _norm(source.name)
                        if table_name:
                            ref = PhysicalColumnRef(
                                table_name=table_name,
                                column_name=column_name,
                            )
                    # A Scope source is a CTE/derived-table output. Its inner
                    # physical columns are visited in that source's own scope.
                elif physical_scope_tables and not has_virtual_source:
                    ref = PhysicalColumnRef(
                        column_name=column_name,
                        candidate_tables=tuple(physical_scope_tables),
                    )

                if ref is not None and ref not in seen_refs:
                    seen_refs.add(ref)
                    refs.append(ref)

    return SqlIdentifierUsage(
        physical_tables=frozenset(physical_tables),
        physical_columns=tuple(refs),
    )
