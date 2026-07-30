"""Scope-aware SQL identifier extraction for catalog validation.

The SQL protocol validates only physical database tables and columns against
AI智能问数 metadata. CTEs and derived tables are query-local relations: their
output aliases must never be mistaken for physical catalog columns.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
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


@dataclass(frozen=True)
class SqlClauseUsage:
    """Column names grouped by their semantic SQL role."""

    all_columns: frozenset[str]
    predicate_columns: frozenset[str]
    projection_columns: frozenset[str]
    grouping_columns: frozenset[str]


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


def collect_sql_clause_usage(sql: str, dialect: str | None = None) -> SqlClauseUsage:
    """Collect column names from the clauses relevant to an intent contract.

    This deliberately models only stable business roles: selected metrics and
    dimensions, grouping dimensions, and filtering/join predicates. Physical
    catalog validation remains the responsibility of
    :func:`collect_sql_identifier_usage`.
    """

    all_columns: set[str] = set()
    predicate_columns: set[str] = set()
    projection_columns: set[str] = set()
    grouping_columns: set[str] = set()

    def add_columns(target: set[str], expression: exp.Expression | None) -> None:
        if expression is None:
            return
        for column in expression.find_all(exp.Column):
            name = _norm(column.name).casefold()
            if name and name != "*":
                target.add(name)
                all_columns.add(name)

    for statement in sqlglot.parse(sql, dialect=dialect):
        if statement is None:
            continue
        for select in statement.find_all(exp.Select):
            for projection in select.expressions:
                add_columns(projection_columns, projection)
            add_columns(grouping_columns, select.args.get("group"))
            add_columns(predicate_columns, select.args.get("where"))
            add_columns(predicate_columns, select.args.get("having"))
            add_columns(predicate_columns, select.args.get("qualify"))
            for join in select.args.get("joins") or []:
                add_columns(predicate_columns, join.args.get("on"))

    return SqlClauseUsage(
        all_columns=frozenset(all_columns),
        predicate_columns=frozenset(predicate_columns),
        projection_columns=frozenset(projection_columns),
        grouping_columns=frozenset(grouping_columns),
    )


def _normalized_identifier(identifier: Any) -> str:
    return str(identifier or "").strip().strip("`\"'[]").rsplit(".", 1)[-1].casefold()


def _allowed_contract_columns(kind: str, usage: SqlClauseUsage) -> frozenset[str]:
    if kind in {"scope", "filter", "entity", "relation"}:
        return usage.predicate_columns
    if kind in {"dimension", "grain"}:
        return usage.projection_columns | usage.grouping_columns
    if kind == "time":
        return (
            usage.predicate_columns | usage.projection_columns | usage.grouping_columns
        )
    if kind in {"metric", "calculation"}:
        return usage.projection_columns
    return usage.all_columns


def validate_sql_contract_structure(
    statements: Sequence[str],
    decisions: Sequence[Mapping[str, Any]],
    *,
    dialect: str | None,
) -> str | None:
    """Validate resolved contract identifiers against their SQL clause roles."""
    coverages: list[set[str]] = []
    usages: list[SqlClauseUsage] = []
    violations_by_plan: list[list[str]] = []
    for statement in statements:
        try:
            usage = collect_sql_clause_usage(statement, dialect)
        except Exception as exc:
            return f"SQL contract parsing failed: {exc}"
        usages.append(usage)

        covered: set[str] = set()
        violations: list[str] = []
        for decision in decisions:
            if not decision.get("locked"):
                continue
            identifiers = [
                str(item or "").strip().strip("`\"'[]")
                for item in decision.get("required_identifiers") or []
                if str(item or "").strip().strip("`\"'[]")
            ]
            if not identifiers:
                continue
            allowed = _allowed_contract_columns(str(decision.get("kind") or ""), usage)
            if all(
                _normalized_identifier(identifier) in allowed
                for identifier in identifiers
            ):
                key = str(decision.get("key") or "").strip()
                if key:
                    covered.add(key)
            else:
                label = str(decision.get("label") or decision.get("key") or "").strip()
                missing = [
                    identifier
                    for identifier in identifiers
                    if _normalized_identifier(identifier) not in allowed
                ]
                violations.append(
                    f"{label}: {', '.join(missing)}" if label else ", ".join(missing)
                )
        coverages.append(covered)
        violations_by_plan.append(violations)

    required_keys = {
        str(decision.get("key") or "").strip()
        for decision in decisions
        if decision.get("locked")
        and decision.get("required_identifiers")
        and str(decision.get("key") or "").strip()
    }
    covered_keys = set().union(*coverages) if coverages else set()
    if required_keys - covered_keys:
        missing: list[str] = []
        for plan_violations in violations_by_plan:
            missing.extend(plan_violations)
        return (
            "Generated SQL does not implement required contract identifier(s) "
            "in the correct clause: " + ", ".join(dict.fromkeys(missing))
        )

    signatures = [
        (
            frozenset(coverage),
            usage.projection_columns,
            usage.grouping_columns,
            usage.predicate_columns,
        )
        for coverage, usage in zip(coverages, usages, strict=True)
        if coverage
    ]
    if len(signatures) != len(set(signatures)):
        return (
            "Generated SQL batch contains competing plans for the same semantic "
            "contract. Return one authoritative plan or complementary plans."
        )
    return None
