"""Scope-aware SQL identifier extraction for catalog validation.

The SQL protocol validates only physical database tables and columns against
AI智能问数 metadata. CTEs and derived tables are query-local relations: their
output aliases must never be mistaken for physical catalog columns.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, cast

import sqlglot
from sqlglot import exp
from sqlglot.optimizer.scope import Scope, traverse_scope

from apps.chat.query_contract import QueryContract


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
    all_qualified_columns: frozenset[str]
    predicate_qualified_columns: frozenset[str]
    projection_qualified_columns: frozenset[str]
    grouping_qualified_columns: frozenset[str]


@dataclass(frozen=True)
class ResultProjection:
    """One public result field and the confirmed requirements in its lineage."""

    output_name: str
    requirement_keys: tuple[str, ...]
    source_columns: tuple[str, ...]


@dataclass(frozen=True)
class ProjectionContractEvidence:
    """Lineage-aware evidence for the statement's public result columns."""

    output_columns: frozenset[str]
    violations: tuple[str, ...]
    result_projections: tuple[ResultProjection, ...]


@dataclass(frozen=True)
class SqlContractValidation:
    """One atomic contract validation report for an executable SQL batch."""

    error: str | None
    per_plan_coverage: tuple[frozenset[str], ...]
    per_plan_projections: tuple[tuple[ResultProjection, ...], ...]


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
    all_qualified: set[str] = set()
    predicate_qualified: set[str] = set()
    projection_qualified: set[str] = set()
    grouping_qualified: set[str] = set()

    def role_for_column(
        column: exp.Column,
        select: exp.Select,
    ) -> str | None:
        def belongs_to_aggregate(node: exp.Expression) -> bool:
            parent = node.parent
            while parent is not None and parent is not select:
                if isinstance(parent, exp.AggFunc):
                    return True
                parent = parent.parent
            return False

        node: exp.Expression | None = column
        while node is not None and node is not select:
            if isinstance(node, (exp.Where, exp.Having, exp.Qualify, exp.Join)):
                return "predicate"
            if isinstance(node, exp.Group):
                return "grouping"
            # ORDER BY at statement level is presentation-only. An ORDER node
            # nested inside GROUP_CONCAT/LISTAGG is part of the projected
            # aggregate and must retain the projection role.
            if isinstance(node, (exp.Order, exp.Limit)) and not belongs_to_aggregate(
                node
            ):
                return None
            node = node.parent
        if node is not select:
            return None
        return "projection"

    def physical_name(
        column: exp.Column,
        scope: Scope,
    ) -> str:
        sources = {
            _norm(alias).casefold(): source for alias, source in scope.sources.items()
        }
        table_ref = _norm(column.table).casefold()
        if table_ref:
            source = sources.get(table_ref)
            if isinstance(source, exp.Table):
                table_name = _norm(source.name).casefold()
                return f"{table_name}.{_norm(column.name).casefold()}"
            return ""
        physical_sources = [
            source for source in sources.values() if isinstance(source, exp.Table)
        ]
        virtual_sources = [
            source for source in sources.values() if not isinstance(source, exp.Table)
        ]
        if len(physical_sources) == 1 and not virtual_sources:
            return (
                f"{_norm(physical_sources[0].name).casefold()}."
                f"{_norm(column.name).casefold()}"
            )
        return ""

    for statement in sqlglot.parse(sql, dialect=dialect):
        if statement is None:
            continue
        for scope in traverse_scope(statement):
            select = scope.expression
            if not isinstance(select, exp.Select):
                continue
            select_aliases = _select_aliases(scope)
            for column in scope.columns:
                if _is_output_alias_reference(column, scope, select_aliases):
                    continue
                name = _norm(column.name).casefold()
                if not name or name == "*":
                    continue
                role = role_for_column(column, select)
                if role is None:
                    continue
                all_columns.add(name)
                qualified = physical_name(column, scope)
                if qualified:
                    all_qualified.add(qualified)
                if role == "predicate":
                    predicate_columns.add(name)
                    if qualified:
                        predicate_qualified.add(qualified)
                elif role == "grouping":
                    grouping_columns.add(name)
                    if qualified:
                        grouping_qualified.add(qualified)
                else:
                    projection_columns.add(name)
                    if qualified:
                        projection_qualified.add(qualified)

    return SqlClauseUsage(
        all_columns=frozenset(all_columns),
        predicate_columns=frozenset(predicate_columns),
        projection_columns=frozenset(projection_columns),
        grouping_columns=frozenset(grouping_columns),
        all_qualified_columns=frozenset(all_qualified),
        predicate_qualified_columns=frozenset(predicate_qualified),
        projection_qualified_columns=frozenset(projection_qualified),
        grouping_qualified_columns=frozenset(grouping_qualified),
    )


def _identifier_parts(identifier: Any) -> tuple[str | None, str]:
    normalized = (
        str(identifier or "")
        .replace("`", "")
        .replace('"', "")
        .replace("[", "")
        .replace("]", "")
        .strip()
        .casefold()
    )
    if "." not in normalized:
        return None, normalized
    table, column = normalized.rsplit(".", 1)
    return table or None, column


def _normalized_identifier(identifier: Any) -> str:
    return _identifier_parts(identifier)[1]


def _allowed_contract_columns(
    role: str,
    usage: SqlClauseUsage,
    output_columns: frozenset[str],
) -> frozenset[str]:
    if role in {"filter", "join"}:
        return usage.predicate_columns
    if role == "group":
        return output_columns | usage.grouping_columns
    if role in {"measure", "attribute"}:
        return output_columns
    return usage.all_columns


def _allowed_qualified_contract_columns(
    role: str,
    usage: SqlClauseUsage,
) -> frozenset[str]:
    if role in {"filter", "join"}:
        return usage.predicate_qualified_columns
    if role == "group":
        return usage.projection_qualified_columns | usage.grouping_qualified_columns
    if role in {"measure", "attribute"}:
        return usage.projection_qualified_columns
    return usage.all_qualified_columns


def _identifier_is_covered(
    identifier: str,
    *,
    allowed: frozenset[str],
    qualified_allowed: frozenset[str],
) -> bool:
    table, column = _identifier_parts(identifier)
    if not column or column not in allowed:
        return False
    return table is None or f"{table}.{column}" in qualified_allowed


def _output_selects(expression: exp.Expression) -> list[exp.Select]:
    """Return only SELECTs that define the statement's public result shape."""
    if isinstance(expression, exp.Subquery):
        return _output_selects(expression.this)
    if isinstance(expression, exp.Select):
        return [expression]
    if isinstance(expression, exp.SetOperation):
        return [
            *_output_selects(expression.this),
            *_output_selects(expression.expression),
        ]
    return []


def _direct_sources(select: exp.Select) -> dict[str, exp.Expression]:
    sources: dict[str, exp.Expression] = {}
    from_clause = select.args.get("from_")
    relations = [from_clause.this] if from_clause is not None else []
    relations.extend(join.this for join in select.args.get("joins") or [])
    for relation in relations:
        if relation is None:
            continue
        alias = _norm(relation.alias_or_name).casefold()
        if alias:
            sources[alias] = relation
    return sources


def _cte_sources(expression: exp.Expression) -> dict[str, exp.Expression]:
    return {
        _norm(cte.alias_or_name).casefold(): cte.this
        for cte in expression.find_all(exp.CTE)
        if _norm(cte.alias_or_name)
    }


def _source_query(
    relation: exp.Expression,
    ctes: Mapping[str, exp.Expression],
) -> exp.Expression | None:
    if isinstance(relation, exp.Subquery):
        return relation.this
    if isinstance(relation, exp.Table):
        return ctes.get(_norm(relation.name).casefold())
    return None


def _named_projection(select: exp.Select, name: str) -> exp.Expression | None:
    normalized = _normalized_identifier(name)
    for projection in select.expressions:
        if _normalized_identifier(projection.alias_or_name) == normalized:
            return projection
    return None


def _projection_lineage(
    select: exp.Select,
    projection: exp.Expression,
    ctes: Mapping[str, exp.Expression],
    *,
    visited: set[tuple[int, str]] | None = None,
) -> tuple[exp.Expression, ...]:
    """Resolve a public projection through CTE/derived-table output aliases."""
    lineage: list[exp.Expression] = [projection]
    expression = projection.this if isinstance(projection, exp.Alias) else projection
    sources = _direct_sources(select)
    seen = visited or set()
    columns = (
        [expression]
        if isinstance(expression, exp.Column)
        else list(expression.find_all(exp.Column))
    )
    for column in columns:
        table_alias = _norm(column.table).casefold()
        if table_alias:
            relation = sources.get(table_alias)
        elif len(sources) == 1:
            relation = next(iter(sources.values()))
        else:
            continue
        source_query = _source_query(relation, ctes) if relation is not None else None
        if source_query is None:
            continue

        marker = (id(source_query), _normalized_identifier(column.name))
        if marker in seen:
            continue
        seen.add(marker)
        for source_select in _output_selects(source_query):
            source_projection = _named_projection(source_select, column.name)
            if source_projection is not None:
                lineage.extend(
                    _projection_lineage(
                        source_select,
                        source_projection,
                        ctes,
                        visited=seen,
                    )
                )
    return tuple(lineage)


def _aggregation_name(aggregate: exp.AggFunc) -> str:
    if isinstance(aggregate, exp.Count) and isinstance(aggregate.this, exp.Distinct):
        return "count_distinct"
    if isinstance(aggregate, exp.GroupConcat):
        return (
            "distinct_concat"
            if isinstance(aggregate.this, (exp.Distinct, exp.Order))
            and (
                isinstance(aggregate.this, exp.Distinct)
                or isinstance(aggregate.this.this, exp.Distinct)
            )
            else "group_concat"
        )
    return aggregate.key.casefold()


def _projection_contract_evidence(
    statement: str,
    contract: QueryContract,
    *,
    dialect: str | None,
) -> ProjectionContractEvidence:
    """Collect public output lineage and validate confirmed projection semantics.

    A dimension/grain is not implemented when it is synthesized as NULL or
    collapsed through MIN/MAX without an explicitly confirmed calculation.
    These are structural errors and belong before execution, not in summary.
    """
    grain_preserving: dict[str, str] = {}
    confirmed_aggregations: dict[str, list[tuple[str, str]]] = {}
    requirement_columns: dict[str, set[str]] = {}
    for requirement in contract.requirements:
        projectable_columns: set[str] = set()
        for binding in requirement.bindings:
            normalized = _normalized_identifier(binding.identifier)
            if normalized and binding.role in {"group", "measure", "attribute"}:
                projectable_columns.add(normalized)
            if (
                normalized
                and binding.role in {"group", "attribute"}
                and binding.aggregation == "none"
            ):
                grain_preserving[normalized] = requirement.label or str(
                    binding.identifier
                )
            if (
                normalized
                and binding.role in {"measure", "attribute"}
                and binding.aggregation != "none"
            ):
                confirmed_aggregations.setdefault(normalized, []).append(
                    (
                        requirement.label or str(binding.identifier),
                        binding.aggregation,
                    )
                )
        if projectable_columns:
            requirement_columns[requirement.key] = projectable_columns

    output_columns: set[str] = set()
    violations: list[str] = []
    result_projections: dict[str, dict[str, set[str] | str]] = {}
    # Only validate aggregations for measures actually projected by this
    # statement. Batch-level coverage below is responsible for proving that
    # complementary statements collectively implement every requirement.
    actual_aggregations: dict[str, set[str]] = {}
    for parsed in sqlglot.parse(statement, dialect=dialect):
        if parsed is None:
            continue
        ctes = _cte_sources(parsed)
        for select in _output_selects(parsed):
            for projection in select.expressions:
                alias = _normalized_identifier(projection.alias_or_name)
                lineage = _projection_lineage(select, projection, ctes)
                columns = {
                    _normalized_identifier(column.name)
                    for item in lineage
                    for column in item.find_all(exp.Column)
                }
                output_columns.update(columns)
                output_name = _norm(projection.alias_or_name).strip() or projection.sql(
                    dialect=dialect
                )
                normalized_output = _normalized_identifier(output_name)
                if normalized_output:
                    footprint = {normalized_output, *columns}
                    projection_requirements = {
                        key
                        for key, required_columns in requirement_columns.items()
                        if footprint & required_columns
                    }
                    current = result_projections.setdefault(
                        normalized_output,
                        {
                            "output_name": output_name,
                            "requirement_keys": set(),
                            "source_columns": set(),
                        },
                    )
                    cast(set[str], current["requirement_keys"]).update(
                        projection_requirements
                    )
                    cast(set[str], current["source_columns"]).update(columns)
                affected = set(grain_preserving) & ({alias} | columns)
                aggregate_affected = set(confirmed_aggregations) & (columns)
                if not affected and not aggregate_affected:
                    continue

                has_null = any(
                    isinstance(
                        item.this if isinstance(item, exp.Alias) else item,
                        exp.Null,
                    )
                    or (
                        isinstance(
                            item.this if isinstance(item, exp.Alias) else item,
                            exp.Cast,
                        )
                        and isinstance(
                            (item.this if isinstance(item, exp.Alias) else item).this,
                            exp.Null,
                        )
                    )
                    for item in lineage
                )
                if has_null:
                    for identifier in affected:
                        violations.append(
                            f"{grain_preserving[identifier]} ({identifier}) "
                            "is projected as NULL"
                        )
                    continue

                aggregations = {
                    _aggregation_name(aggregate)
                    for item in lineage
                    for aggregate in item.find_all(exp.AggFunc)
                }
                for identifier in aggregate_affected:
                    actual_aggregations.setdefault(identifier, set()).update(
                        aggregations
                    )
                if aggregations:
                    for identifier in affected:
                        allowed = {
                            aggregation
                            for _label, aggregation in confirmed_aggregations.get(
                                identifier,
                                [],
                            )
                        }
                        disallowed = aggregations - allowed
                        if not disallowed:
                            continue
                        violations.append(
                            f"{grain_preserving[identifier]} ({identifier}) "
                            "is collapsed with "
                            f"{'/'.join(sorted(disallowed)).upper()} instead of "
                            "preserving its confirmed business grain"
                        )
    for identifier, actual in actual_aggregations.items():
        requirements = confirmed_aggregations[identifier]
        for label, expected in requirements:
            if expected in actual:
                continue
            actual_text = "/".join(sorted(actual)).upper() or "NO AGGREGATION"
            violations.append(
                f"{label} ({identifier}) requires {expected.upper()} "
                f"but uses {actual_text}"
            )
    return ProjectionContractEvidence(
        output_columns=frozenset(output_columns),
        violations=tuple(dict.fromkeys(violations)),
        result_projections=tuple(
            ResultProjection(
                output_name=str(value["output_name"]),
                requirement_keys=tuple(
                    sorted(cast(set[str], value["requirement_keys"]))
                ),
                source_columns=tuple(sorted(cast(set[str], value["source_columns"]))),
            )
            for value in result_projections.values()
        ),
    )


def _column_contract_keys(column: exp.Column, scope: Scope) -> set[str]:
    """Return bare and, when provable, physical table-qualified identities."""
    name = _norm(column.name).casefold()
    if not name:
        return set()
    keys = {name}
    sources = {
        _norm(alias).casefold(): source for alias, source in scope.sources.items()
    }
    table_ref = _norm(column.table).casefold()
    source: exp.Expression | Scope | None = None
    if table_ref:
        source = sources.get(table_ref)
    elif len(sources) == 1:
        source = next(iter(sources.values()))
    if isinstance(source, exp.Table):
        table_name = _norm(source.name).casefold()
        if table_name:
            keys.add(f"{table_name}.{name}")
    return keys


def _literal_value(expression: exp.Expression | None) -> str | None:
    current = expression
    while isinstance(current, (exp.Cast, exp.Paren)):
        current = current.this
    if isinstance(current, exp.Literal):
        return str(current.this).strip()
    return None


def _predicate_expressions(select: exp.Select) -> list[exp.Expression]:
    predicates = [
        select.args.get("where"),
        select.args.get("having"),
        select.args.get("qualify"),
    ]
    predicates.extend(join.args.get("on") for join in select.args.get("joins") or [])
    return [item for item in predicates if isinstance(item, exp.Expression)]


def _belongs_to_select(
    expression: exp.Expression,
    select: exp.Select,
) -> bool:
    parent = expression.parent
    while parent is not None and not isinstance(parent, exp.Select):
        parent = parent.parent
    return parent is select


def _entity_predicate_bindings(
    statement: str,
    *,
    dialect: str | None,
) -> set[tuple[str, str]]:
    """Collect exact column/value bindings from predicate expressions."""
    bindings: set[tuple[str, str]] = set()
    for parsed in sqlglot.parse(statement, dialect=dialect):
        if parsed is None:
            continue
        for scope in traverse_scope(parsed):
            select = scope.expression
            if not isinstance(select, exp.Select):
                continue
            for predicate in _predicate_expressions(select):
                for equality in predicate.find_all(exp.EQ):
                    if not _belongs_to_select(equality, select):
                        continue
                    left = equality.left
                    right = equality.right
                    if isinstance(left, exp.Column):
                        value = _literal_value(right)
                        column = left
                    elif isinstance(right, exp.Column):
                        value = _literal_value(left)
                        column = right
                    else:
                        continue
                    if value is not None:
                        bindings.update(
                            (key, value.casefold())
                            for key in _column_contract_keys(column, scope)
                        )
                for membership in predicate.find_all(exp.In):
                    if not _belongs_to_select(membership, select):
                        continue
                    column = membership.this
                    if not isinstance(column, exp.Column):
                        continue
                    keys = _column_contract_keys(column, scope)
                    for expression in membership.expressions:
                        value = _literal_value(expression)
                        if value is not None:
                            bindings.update((key, value.casefold()) for key in keys)
    return bindings


def _time_boundary_columns(
    statement: str,
    *,
    boundary: str,
    lower: bool,
    dialect: str | None,
) -> dict[int, set[str]]:
    """Return boundary columns grouped by their lexical SELECT scope."""
    columns_by_scope: dict[int, set[str]] = {}
    scope_index = 0
    for parsed in sqlglot.parse(statement, dialect=dialect):
        if parsed is None:
            continue
        for scope in traverse_scope(parsed):
            select = scope.expression
            if not isinstance(select, exp.Select):
                continue
            current_index = scope_index
            scope_index += 1
            columns = _boundary_columns_in_scope(
                scope,
                boundary=boundary,
                lower=lower,
            )
            if columns:
                columns_by_scope[current_index] = columns
    return columns_by_scope


def _boundary_columns_in_scope(
    scope: Scope,
    *,
    boundary: str,
    lower: bool,
) -> set[str]:
    select = scope.expression
    if not isinstance(select, exp.Select):
        return set()
    columns: set[str] = set()
    direct_type = exp.GTE if lower else exp.LT
    reverse_type = exp.LTE if lower else exp.GT
    for predicate in _predicate_expressions(select):
        for comparison in predicate.find_all(direct_type, reverse_type):
            if not _belongs_to_select(comparison, select):
                continue
            if isinstance(comparison, direct_type):
                column_expression = comparison.left
                literal_expression = comparison.right
            else:
                column_expression = comparison.right
                literal_expression = comparison.left
            if _literal_value(literal_expression) != boundary:
                continue
            candidate_columns = list(column_expression.find_all(exp.Column))
            if isinstance(column_expression, exp.Column):
                candidate_columns.insert(0, column_expression)
            for column in candidate_columns:
                columns.update(_column_contract_keys(column, scope))
    return columns


def _branch_source_scopes(scope: Scope) -> list[Scope]:
    """Return one set-operation branch and the CTE/derived scopes it reads."""
    found: list[Scope] = []
    seen: set[int] = set()

    def visit(current: Scope) -> None:
        marker = id(current)
        if marker in seen:
            return
        seen.add(marker)
        found.append(current)
        if isinstance(current.expression, exp.SetOperation):
            for child in current.union_scopes:
                visit(child)
            return
        if not isinstance(current.expression, exp.Select):
            return
        for alias in _direct_sources(current.expression):
            source = current.sources.get(alias)
            if isinstance(source, Scope):
                visit(source)

    visit(scope)
    return found


def _scope_has_time_pair(scope: Scope, *, start: str, end: str) -> bool:
    lower = _boundary_columns_in_scope(scope, boundary=start, lower=True)
    upper = _boundary_columns_in_scope(scope, boundary=end, lower=False)
    return bool(lower and upper and not lower.isdisjoint(upper))


def _set_operation_time_error(
    statement: str,
    *,
    start: str,
    end: str,
    dialect: str | None,
) -> str | None:
    """Require every UNION/INTERSECT/EXCEPT branch to inherit a time pair."""
    for parsed in sqlglot.parse(statement, dialect=dialect):
        if parsed is None:
            continue
        for scope in traverse_scope(parsed):
            if not isinstance(scope.expression, exp.SetOperation):
                continue
            ancestor = scope.parent
            inherited = False
            while ancestor is not None:
                if _scope_has_time_pair(ancestor, start=start, end=end):
                    inherited = True
                    break
                ancestor = ancestor.parent
            if inherited:
                continue
            for branch in scope.union_scopes:
                if any(
                    _scope_has_time_pair(source, start=start, end=end)
                    for source in _branch_source_scopes(branch)
                ):
                    continue
                return (
                    "Generated SQL omits the explicit half-open time range "
                    f"[{start}, {end}) from a set-operation branch"
                )
    return None


def _predicate_contract_error(
    statement: str,
    contract: QueryContract,
    *,
    dialect: str | None,
) -> str | None:
    entity_requirements = [
        requirement
        for requirement in contract.requirements
        if requirement.expected_values
    ]
    if entity_requirements:
        bindings = _entity_predicate_bindings(statement, dialect=dialect)
        missing: list[str] = []
        for requirement in entity_requirements:
            identifiers = {
                ".".join(part for part in _identifier_parts(binding.identifier) if part)
                for binding in requirement.bindings_for("filter")
            }
            for value in requirement.expected_values:
                if not any(
                    (identifier, value.casefold()) in bindings
                    for identifier in identifiers
                ):
                    missing.append(f"{requirement.label or requirement.key}: {value}")
        if missing:
            return (
                "Generated SQL does not bind confirmed entity value(s) to the "
                "required filter field(s): " + ", ".join(missing)
            )

    time_intent = contract.time_intent or {}
    if time_intent.get("scope") != "explicit":
        return None
    start = str(time_intent.get("start") or "").strip()
    end = str(time_intent.get("end_exclusive") or "").strip()
    if not start or not end:
        return "Explicit time contract requires start and end_exclusive"
    lower_by_scope = _time_boundary_columns(
        statement,
        boundary=start,
        lower=True,
        dialect=dialect,
    )
    upper_by_scope = _time_boundary_columns(
        statement,
        boundary=end,
        lower=False,
        dialect=dialect,
    )
    if not lower_by_scope or not upper_by_scope:
        return (
            "Generated SQL does not implement the explicit half-open time "
            f"range [{start}, {end})"
        )
    for scope_index in set(lower_by_scope) | set(upper_by_scope):
        lower_columns = lower_by_scope.get(scope_index, set())
        upper_columns = upper_by_scope.get(scope_index, set())
        if not lower_columns or not upper_columns:
            return (
                "Generated SQL applies only one explicit time boundary in a "
                "query branch"
            )
        if lower_columns.isdisjoint(upper_columns):
            return "Generated SQL applies explicit time boundaries to different columns"
    return _set_operation_time_error(
        statement,
        start=start,
        end=end,
        dialect=dialect,
    )


def analyze_sql_contract_structure(
    statements: Sequence[str],
    contract: QueryContract,
    *,
    dialect: str | None,
) -> SqlContractValidation:
    """Validate one batch and return its reusable coverage/projection facts."""
    coverages: list[set[str]] = []
    usages: list[SqlClauseUsage] = []
    projection_evidences: list[ProjectionContractEvidence] = []
    violations_by_plan: list[list[str]] = []

    def report(error: str | None) -> SqlContractValidation:
        return SqlContractValidation(
            error=error,
            per_plan_coverage=tuple(frozenset(items) for items in coverages),
            per_plan_projections=tuple(
                evidence.result_projections for evidence in projection_evidences
            ),
        )

    for statement in statements:
        try:
            usage = collect_sql_clause_usage(statement, dialect)
        except Exception as exc:
            return report(f"SQL contract parsing failed: {exc}")
        predicate_error = _predicate_contract_error(
            statement,
            contract,
            dialect=dialect,
        )
        if predicate_error:
            return report(predicate_error)
        projection_evidence = _projection_contract_evidence(
            statement,
            contract,
            dialect=dialect,
        )
        if projection_evidence.violations:
            return report(
                "Generated SQL violates confirmed dimension/grain semantics: "
                + "; ".join(projection_evidence.violations)
            )
        usages.append(usage)
        projection_evidences.append(projection_evidence)

        covered: set[str] = set()
        violations: list[str] = []
        for requirement in contract.requirements:
            bindings = [
                binding
                for binding in requirement.bindings
                if str(binding.identifier or "").strip().strip("`\"'[]")
            ]
            if not bindings:
                continue
            binding_matches = [
                _identifier_is_covered(
                    binding.identifier,
                    allowed=_allowed_contract_columns(
                        binding.role,
                        usage,
                        projection_evidence.output_columns,
                    ),
                    qualified_allowed=_allowed_qualified_contract_columns(
                        binding.role,
                        usage,
                    ),
                )
                for binding in bindings
            ]
            covered_requirement = (
                any(binding_matches)
                if requirement.match_any_identifier
                else all(binding_matches)
            )
            if covered_requirement:
                key = requirement.key
                if key:
                    covered.add(key)
            else:
                label = requirement.label or requirement.key
                missing = [
                    f"{binding.identifier}<{binding.role}>"
                    for binding, matched in zip(
                        bindings,
                        binding_matches,
                        strict=True,
                    )
                    if not matched
                ]
                violations.append(
                    f"{label}: {', '.join(missing)}" if label else ", ".join(missing)
                )
        coverages.append(covered)
        violations_by_plan.append(violations)

    required_keys = {
        requirement.key
        for requirement in contract.requirements
        if requirement.bindings and requirement.key
    }
    covered_keys = set().union(*coverages) if coverages else set()
    if required_keys - covered_keys:
        missing: list[str] = []
        for plan_violations in violations_by_plan:
            missing.extend(plan_violations)
        return report(
            "Generated SQL does not implement required contract identifier(s) "
            "in the correct clause: " + ", ".join(dict.fromkeys(missing))
        )

    signatures = [
        (
            frozenset(coverage),
            projection_evidence.output_columns,
            usage.grouping_columns,
            usage.predicate_columns,
        )
        for coverage, usage, projection_evidence in zip(
            coverages,
            usages,
            projection_evidences,
            strict=True,
        )
        if coverage
    ]
    if len(signatures) != len(set(signatures)):
        return report(
            "Generated SQL batch contains competing plans for the same semantic "
            "contract. Return one authoritative plan or complementary plans."
        )
    return report(None)
