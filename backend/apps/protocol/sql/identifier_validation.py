"""SQL catalog extraction and clause-oriented contract verification."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

import sqlglot
from sqlglot import exp
from sqlglot.optimizer.scope import Scope, traverse_scope

from apps.chat.query_specification import (
    BusinessRelationRequirement,
    FieldRef,
    GroupRequirement,
    OrderRequirement,
    OutputRequirement,
    PredicateRequirement,
    QuerySpecification,
    RelationPair,
    SpecificationRequirement,
    TimeWindowRequirement,
    requirement_fields,
)


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


@dataclass(frozen=True)
class SqlClauseUsage:
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
    output_name: str
    requirement_keys: tuple[str, ...]
    source_columns: tuple[str, ...]


VerificationState = Literal["satisfied", "violated", "unverified"]
VerificationOverall = Literal["verified", "partial", "unsupported"]


@dataclass(frozen=True)
class RequirementVerification:
    requirement_id: str
    state: VerificationState
    reason: str = ""


@dataclass(frozen=True)
class SqlContractValidation:
    error: str | None
    status: VerificationOverall
    requirements: tuple[RequirementVerification, ...]
    per_plan_coverage: tuple[frozenset[str], ...]
    per_plan_projections: tuple[tuple[ResultProjection, ...], ...]
    warnings: tuple[str, ...] = ()


def _norm(value: Any) -> str:
    return str(value or "").replace("`", "").replace('"', "").strip()


def _column_key(column: exp.Column, scope: Scope) -> set[str]:
    field = _norm(column.name).casefold()
    if not field:
        return set()
    result = {field}
    table_ref = _norm(column.table).casefold()
    sources = {
        _norm(alias).casefold(): source for alias, source in scope.sources.items()
    }
    source: exp.Expression | Scope | None = None
    if table_ref:
        source = sources.get(table_ref)
    elif len(sources) == 1:
        source = next(iter(sources.values()))
    if isinstance(source, exp.Table):
        table = _norm(source.name).casefold()
        if table:
            result.add(f"{table}.{field}")
    return result


def _ref_keys(field: FieldRef) -> set[str]:
    if not field.field:
        return set()
    keys = {field.field.casefold()}
    if field.resource_name:
        keys.add(f"{field.resource_name.casefold()}.{field.field.casefold()}")
    return keys


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
            # (database_name, table_name) — bare allow-list still uses table only.
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
                    table = _norm(source_table.name)
                    database = _norm(source_table.db) or None
                    ref = PhysicalColumnRef(
                        name,
                        table_name=table,
                        database_name=database,
                    )
                elif physical_scope and not has_virtual:
                    ref = PhysicalColumnRef(
                        name,
                        candidate_tables=tuple(t for _db, t in physical_scope),
                        candidate_databases=tuple(db for db, _t in physical_scope),
                    )
                if ref is not None and ref not in seen:
                    refs.append(ref)
                    seen.add(ref)
    return SqlIdentifierUsage(
        physical_tables=frozenset(physical_tables),
        physical_columns=tuple(refs),
    )


#: Engines that evaluate ORDER BY after projection, so it resolves against the
#: SELECT output list instead of the source tables.
_OUTPUT_SCOPED_ORDER_DIALECTS = frozenset({"hive", "spark", "spark2", "databricks"})


def order_by_scope_error(sql: str, dialect: str | None) -> str | None:
    """Report an ORDER BY the engine is certain to refuse.

    On Hive-family engines ``ORDER BY t.col`` raises SemanticException 10004
    even when ``t.col`` is projected, because by then only output names exist.
    The prompt says so and models keep writing the qualified form anyway, at a
    cost of one generation plus one engine round-trip each time, so the
    statement is checked before it is sent.  Rewriting it here is not an
    option: re-emitting the statement through sqlglot drops arguments on
    functions such as ``FROM_UNIXTIME``, which would silently change the
    answer.  Naming the exact replacement is what the raw Java stack trace
    fails to do.
    """
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


def _belongs_to(expression: exp.Expression, container: exp.Expression) -> bool:
    parent = expression.parent
    while parent is not None and parent is not container:
        if isinstance(parent, exp.Select):
            return False
        parent = parent.parent
    return parent is container


def collect_sql_clause_usage(sql: str, dialect: str | None = None) -> SqlClauseUsage:
    all_bare: set[str] = set()
    all_qualified: set[str] = set()
    predicate_bare: set[str] = set()
    predicate_qualified: set[str] = set()
    projection_bare: set[str] = set()
    projection_qualified: set[str] = set()
    grouping_bare: set[str] = set()
    grouping_qualified: set[str] = set()

    def add(
        column: exp.Column, scope: Scope, bare: set[str], qualified: set[str]
    ) -> None:
        keys = _column_key(column, scope)
        bare.update(key for key in keys if "." not in key)
        qualified.update(key for key in keys if "." in key)

    for parsed in sqlglot.parse(sql, dialect=dialect):
        if parsed is None:
            continue
        for scope in traverse_scope(parsed):
            select = scope.expression
            if not isinstance(select, exp.Select):
                continue
            for column in scope.columns:
                if _is_output_alias(column, scope):
                    continue
                add(column, scope, all_bare, all_qualified)
            for projection in select.expressions:
                for column in projection.find_all(exp.Column):
                    if _belongs_to(column, projection):
                        add(column, scope, projection_bare, projection_qualified)
            group = select.args.get("group")
            if isinstance(group, exp.Group):
                for column in group.find_all(exp.Column):
                    add(column, scope, grouping_bare, grouping_qualified)
            predicates = [select.args.get("where"), select.args.get("having")]
            for predicate in predicates:
                if isinstance(predicate, exp.Expression):
                    for column in predicate.find_all(exp.Column):
                        add(column, scope, predicate_bare, predicate_qualified)
    return SqlClauseUsage(
        all_columns=frozenset(all_bare),
        predicate_columns=frozenset(predicate_bare),
        projection_columns=frozenset(projection_bare),
        grouping_columns=frozenset(grouping_bare),
        all_qualified_columns=frozenset(all_qualified),
        predicate_qualified_columns=frozenset(predicate_qualified),
        projection_qualified_columns=frozenset(projection_qualified),
        grouping_qualified_columns=frozenset(grouping_qualified),
    )


@dataclass
class _ObservedPlan:
    usage: SqlClauseUsage
    projections: tuple[ResultProjection, ...]
    projection_fields: set[str]
    projection_aggregations: dict[str, set[str]]
    has_star: bool
    predicates: list[tuple[set[str], str, tuple[str, ...]]]
    joins: list[tuple[set[str], set[str], str]]
    has_union: bool
    group_fields: set[str]
    public_group_fields: set[str]
    group_buckets: dict[str, set[str]]
    order_fields: list[tuple[set[str], str]]
    limit: int | None


def _scope_output_keys(
    scope: Scope,
    output_name: str,
    *,
    visited: set[tuple[int, str]],
) -> set[str]:
    marker = (id(scope), output_name.casefold())
    if marker in visited:
        return set()
    visited.add(marker)
    if isinstance(scope.expression, exp.Union):
        return set().union(
            *(
                _scope_output_keys(child, output_name, visited=visited)
                for child in scope.union_scopes
            )
        )
    if not isinstance(scope.expression, exp.Select):
        return set()
    for projection in scope.expression.expressions:
        if _norm(projection.alias_or_name).casefold() != output_name.casefold():
            continue
        return {
            key
            for column in projection.find_all(exp.Column)
            for key in _lineage_column_keys(column, scope, visited=visited)
        }
    return set()


def _lineage_column_keys(
    column: exp.Column,
    scope: Scope,
    *,
    visited: set[tuple[int, str]] | None = None,
) -> set[str]:
    """Resolve a derived-table output back to its physical source fields."""
    keys = _column_key(column, scope)
    table_ref = _norm(column.table).casefold()
    source = {
        _norm(alias).casefold(): value for alias, value in scope.sources.items()
    }.get(table_ref)
    if isinstance(source, Scope):
        keys.update(
            _scope_output_keys(
                source,
                _norm(column.name),
                visited=visited if visited is not None else set(),
            )
        )
    return keys


def _literal(expression: exp.Expression | None) -> str | None:
    current = expression
    while isinstance(current, exp.Cast | exp.Paren):
        current = current.this
    if isinstance(current, exp.Literal):
        return str(current.this)
    if isinstance(current, exp.Boolean | exp.Null):
        return current.sql().casefold()
    return None


def _agg_name(node: exp.AggFunc) -> str:
    if isinstance(node, exp.Count):
        return "count_distinct" if node.find(exp.Distinct) else "count"
    if isinstance(node, exp.Sum):
        return "sum"
    if isinstance(node, exp.Avg):
        return "avg"
    if isinstance(node, exp.Min):
        return "min"
    if isinstance(node, exp.Max):
        return "max"
    if isinstance(node, exp.GroupConcat):
        return "distinct_concat" if node.find(exp.Distinct) else "group_concat"
    return node.key.casefold()


def _predicate_items(
    expression: exp.Expression, scope: Scope
) -> list[tuple[set[str], str, tuple[str, ...]]]:
    items: list[tuple[set[str], str, tuple[str, ...]]] = []
    operators: tuple[tuple[type[exp.Expression], str], ...] = (
        (exp.EQ, "eq"),
        (exp.NEQ, "ne"),
        (exp.GT, "gt"),
        (exp.GTE, "gte"),
        (exp.LT, "lt"),
        (exp.LTE, "lte"),
        (exp.Like, "like"),
    )
    for node_type, operator in operators:
        for node in expression.find_all(node_type):
            effective_operator = operator
            left, right = node.left, node.right
            if isinstance(left, exp.Column):
                value, column = _literal(right), left
            elif isinstance(right, exp.Column):
                value, column = _literal(left), right
                effective_operator = {
                    "gt": "lt",
                    "gte": "lte",
                    "lt": "gt",
                    "lte": "gte",
                }.get(operator, operator)
            else:
                continue
            if value is not None:
                items.append(
                    (
                        _column_key(column, scope),
                        effective_operator,
                        (value.casefold(),),
                    )
                )
    for negation in expression.find_all(exp.Not):
        node = negation.this
        if isinstance(node, exp.In) and isinstance(node.this, exp.Column):
            values = tuple(
                value.casefold()
                for item in node.expressions
                if (value := _literal(item)) is not None
            )
            if values:
                items.append((_column_key(node.this, scope), "not_in", values))
        elif (
            isinstance(node, exp.Is)
            and isinstance(node.this, exp.Column)
            and isinstance(node.expression, exp.Null)
        ):
            items.append((_column_key(node.this, scope), "is_not_null", ()))
    for node in expression.find_all(exp.In):
        if isinstance(node.parent, exp.Not):
            continue
        if isinstance(node.this, exp.Column):
            values = tuple(
                value.casefold()
                for item in node.expressions
                if (value := _literal(item)) is not None
            )
            if values:
                items.append((_column_key(node.this, scope), "in", values))
    for node in expression.find_all(exp.Is):
        if isinstance(node.parent, exp.Not):
            continue
        if isinstance(node.this, exp.Column) and isinstance(node.expression, exp.Null):
            items.append((_column_key(node.this, scope), "is_null", ()))
    return items


def _observe(statement: str, dialect: str | None) -> _ObservedPlan:
    usage = collect_sql_clause_usage(statement, dialect)
    projections: list[ResultProjection] = []
    projection_fields: set[str] = set()
    projection_aggregations: dict[str, set[str]] = {}
    predicates: list[tuple[set[str], str, tuple[str, ...]]] = []
    joins: list[tuple[set[str], set[str], str]] = []
    group_fields: set[str] = set()
    public_group_fields: set[str] = set()
    group_buckets: dict[str, set[str]] = {}
    order_fields: list[tuple[set[str], str]] = []
    lineage: dict[str, tuple[set[str], set[str]]] = {}
    has_star = False
    has_union = False
    limit: int | None = None
    for parsed in sqlglot.parse(statement, dialect=dialect):
        if parsed is None:
            continue
        has_union = has_union or parsed.find(exp.Union) is not None
        for scope in traverse_scope(parsed):
            select = scope.expression
            if not isinstance(select, exp.Select):
                continue
            is_public = scope.parent is None
            for item in select.expressions:
                keys: set[str] = set()
                aggregations = {_agg_name(node) for node in item.find_all(exp.AggFunc)}
                if item.find(exp.Div):
                    aggregations.add("ratio")
                if item.find(exp.Sub):
                    aggregations.add("difference")
                for column in item.find_all(exp.Column):
                    keys.update(_column_key(column, scope))
                expanded_keys = set(keys)
                expanded_aggregations = set(aggregations)
                for key in list(keys):
                    inherited = lineage.get(key.rsplit(".", 1)[-1])
                    if inherited is not None:
                        expanded_keys.update(inherited[0])
                        expanded_aggregations.update(inherited[1])
                alias = _norm(item.alias_or_name).casefold()
                if alias:
                    expanded_keys.add(alias)
                    lineage[alias] = (expanded_keys, expanded_aggregations)
                if is_public:
                    if isinstance(item, exp.Star) or item.find(exp.Star):
                        has_star = True
                    keys = expanded_keys
                    aggregations = expanded_aggregations
                    projection_fields.update(keys)
                    for key in keys:
                        projection_aggregations.setdefault(key, set()).update(
                            aggregations
                        )
                    projections.append(
                        ResultProjection(
                            output_name=_norm(item.alias_or_name)
                            or item.sql(dialect=dialect),
                            requirement_keys=(),
                            source_columns=tuple(sorted(keys)),
                        )
                    )
            for predicate in (select.args.get("where"), select.args.get("having")):
                if isinstance(predicate, exp.Expression):
                    predicates.extend(_predicate_items(predicate, scope))
            for join in select.args.get("joins") or []:
                kind = str(
                    join.args.get("kind") or join.args.get("side") or "inner"
                ).casefold()
                on = join.args.get("on")
                if isinstance(on, exp.Expression):
                    for equality in on.find_all(exp.EQ):
                        if isinstance(equality.left, exp.Column) and isinstance(
                            equality.right, exp.Column
                        ):
                            joins.append(
                                (
                                    _lineage_column_keys(equality.left, scope),
                                    _lineage_column_keys(equality.right, scope),
                                    kind,
                                )
                            )
            group = select.args.get("group")
            if isinstance(group, exp.Group):
                for group_expression in group.expressions:
                    sql_text = group_expression.sql(dialect=dialect).casefold()
                    if any(
                        token in sql_text
                        for token in ("%y-%m-%d", "'day'", '"day"', "day(")
                    ):
                        bucket = "day"
                    elif any(
                        token in sql_text
                        for token in ("%y-%m", "'month'", '"month"', "month(")
                    ):
                        bucket = "month"
                    elif any(
                        token in sql_text
                        for token in ("%y", "'year'", '"year"', "year(")
                    ):
                        bucket = "year"
                    else:
                        bucket = ""
                    for column in group_expression.find_all(exp.Column):
                        keys = _column_key(column, scope)
                        expanded_group_keys = set(keys)
                        for key in keys:
                            inherited = lineage.get(key.rsplit(".", 1)[-1])
                            if inherited is not None:
                                expanded_group_keys.update(inherited[0])
                        group_fields.update(keys)
                        if is_public:
                            public_group_fields.update(expanded_group_keys)
                        if bucket:
                            for key in keys:
                                group_buckets.setdefault(key, set()).add(bucket)
            order = select.args.get("order")
            if is_public and isinstance(order, exp.Order):
                for ordered in order.expressions:
                    keys = {
                        key
                        for column in ordered.find_all(exp.Column)
                        for key in _column_key(column, scope)
                    }
                    alias = _norm(
                        ordered.this.name
                        if isinstance(ordered.this, exp.Column)
                        else ""
                    ).casefold()
                    if alias:
                        keys.add(alias)
                    order_fields.append(
                        (keys, "desc" if ordered.args.get("desc") else "asc")
                    )
            limit_node = select.args.get("limit")
            if is_public and isinstance(limit_node, exp.Limit):
                raw_limit = _literal(limit_node.expression)
                if raw_limit and raw_limit.isdigit():
                    limit = int(raw_limit)
    return _ObservedPlan(
        usage=usage,
        projections=tuple(projections),
        projection_fields=projection_fields,
        projection_aggregations=projection_aggregations,
        has_star=has_star,
        predicates=predicates,
        joins=joins,
        has_union=has_union,
        group_fields=group_fields,
        public_group_fields=public_group_fields,
        group_buckets=group_buckets,
        order_fields=order_fields,
        limit=limit,
    )


def _field_matches(field: FieldRef, keys: set[str] | frozenset[str]) -> bool:
    if not field.field:
        return False
    normalized = set(keys)
    if field.resource_name:
        return (
            f"{field.resource_name.casefold()}.{field.field.casefold()}" in normalized
        )
    return field.field.casefold() in normalized


def _predicate_satisfied(
    requirement: PredicateRequirement, observed: _ObservedPlan
) -> bool:
    expected = tuple(str(value).casefold() for value in requirement.values)
    for keys, operator, values in observed.predicates:
        if not _field_matches(requirement.field, keys):
            continue
        if requirement.operator == operator and (
            not expected or set(expected) == set(values)
        ):
            return True
    return False


def _time_satisfied(
    requirement: TimeWindowRequirement, observed: _ObservedPlan
) -> bool:
    if requirement.mode == "all":
        return not any(
            any(_field_matches(field, keys) for field in requirement.fields)
            for keys, _operator, _values in observed.predicates
        )
    if requirement.mode == "rolling":
        predicate_keys = set(observed.usage.predicate_columns) | set(
            observed.usage.predicate_qualified_columns
        )
        return all(
            _field_matches(field, predicate_keys) for field in requirement.fields
        )
    assert requirement.start is not None and requirement.end_exclusive is not None
    for field in requirement.fields:
        lower = any(
            _field_matches(field, keys)
            and operator in {"gte", "gt"}
            and requirement.start.casefold() in values
            for keys, operator, values in observed.predicates
        )
        upper = any(
            _field_matches(field, keys)
            and operator in {"lt", "lte"}
            and requirement.end_exclusive.casefold() in values
            for keys, operator, values in observed.predicates
        )
        if not lower or not upper:
            return False
    return True


def _relation_pair_matches(
    pair: RelationPair,
    left: set[str],
    right: set[str],
) -> bool:
    return (_field_matches(pair.left, left) and _field_matches(pair.right, right)) or (
        _field_matches(pair.left, right) and _field_matches(pair.right, left)
    )


def _matching_relation_joins(
    requirement: BusinessRelationRequirement,
    observed: _ObservedPlan,
) -> list[tuple[set[str], set[str], str]]:
    return [
        join
        for join in observed.joins
        if any(
            _relation_pair_matches(pair, join[0], join[1]) for pair in requirement.pairs
        )
    ]


def _relation_satisfied(
    requirement: BusinessRelationRequirement, observed: _ObservedPlan
) -> bool:
    matched = _matching_relation_joins(requirement, observed)
    for pair in requirement.pairs:
        if not any(
            _relation_pair_matches(pair, left, right) for left, right, _kind in matched
        ):
            return False
    kinds = {kind for _left, _right, kind in matched}
    if requirement.population == "intersection":
        return not kinds or all(kind in {"", "inner"} for kind in kinds)
    if requirement.population == "left":
        return any(kind == "left" for kind in kinds)
    if requirement.population == "right":
        return any(kind == "right" for kind in kinds)
    if any(kind in {"full", "outer", "full outer"} for kind in kinds):
        return True
    if not observed.has_union or not kinds or not all(kind == "left" for kind in kinds):
        return False
    return all(
        any(
            {
                pair.left.resource_name.casefold(),
                pair.right.resource_name.casefold(),
            }
            <= _join_resources(side)
            for left, right, _kind in matched
            for side in (left, right)
        )
        for pair in requirement.pairs
    )


def _join_resources(keys: set[str]) -> set[str]:
    return {key.split(".", 1)[0] for key in keys if "." in key}


def _requirement_state(
    requirement: SpecificationRequirement,
    observed: _ObservedPlan,
    contract: QuerySpecification,
) -> VerificationState:
    # semantic_ref intentionally carries an unresolved business concept rather
    # than a fabricated identifier. SQL AST cannot prove its implementation,
    # so it is a disclosed risk, not a contract violation or a repair loop.
    if any(not field.field for field in requirement_fields(requirement)):
        return "unverified"
    if isinstance(requirement, OutputRequirement):
        if not _field_matches(requirement.field, observed.projection_fields):
            satisfied = False
        elif requirement.operation == "value":
            satisfied = True
        elif requirement.operation in {"ratio", "difference"}:
            satisfied = any(
                requirement.operation in operations
                for key, operations in observed.projection_aggregations.items()
                if key in _ref_keys(requirement.field)
            )
        else:
            satisfied = any(
                requirement.operation in aggregations
                for key, aggregations in observed.projection_aggregations.items()
                if key in _ref_keys(requirement.field)
            )
    elif isinstance(requirement, PredicateRequirement):
        satisfied = _predicate_satisfied(requirement, observed)
        if satisfied and requirement.null_policy == "preserve":
            return "unverified"
    elif isinstance(requirement, GroupRequirement):
        satisfied = _field_matches(requirement.field, observed.group_fields)
        if satisfied and requirement.bucket:
            satisfied = any(
                requirement.bucket in buckets
                for key, buckets in observed.group_buckets.items()
                if key in _ref_keys(requirement.field)
            )
    elif isinstance(requirement, BusinessRelationRequirement):
        pairs_present = all(
            any(
                (_field_matches(pair.left, left) and _field_matches(pair.right, right))
                or (
                    _field_matches(pair.left, right)
                    and _field_matches(pair.right, left)
                )
                for left, right, _kind in observed.joins
            )
            for pair in requirement.pairs
        )
        if not pairs_present:
            return "violated"
        satisfied = _relation_satisfied(requirement, observed)
    elif isinstance(requirement, TimeWindowRequirement):
        satisfied = _time_satisfied(requirement, observed)
        if satisfied and requirement.mode == "rolling":
            return "unverified"
    elif isinstance(requirement, OrderRequirement):
        target_keys = (
            _ref_keys(requirement.field)
            if requirement.field is not None
            else {str(requirement.output_requirement_id).casefold()}
        )
        if requirement.output_requirement_id:
            output = contract.by_requirement_id().get(requirement.output_requirement_id)
            if isinstance(output, OutputRequirement):
                target_keys |= _ref_keys(output.field) | {output.label.casefold()}
                target_keys.update(
                    projection.output_name.casefold()
                    for projection in observed.projections
                    if _field_matches(output.field, set(projection.source_columns))
                )
        satisfied = any(
            direction == requirement.direction and bool(keys & target_keys)
            for keys, direction in observed.order_fields
        )
    else:
        satisfied = False
    return "satisfied" if satisfied else "violated"


def _project_requirement_lineage(
    observed: _ObservedPlan,
    contract: QuerySpecification,
) -> tuple[ResultProjection, ...]:
    result: list[ResultProjection] = []
    for projection in observed.projections:
        keys = set(projection.source_columns) | {projection.output_name.casefold()}
        requirement_ids: list[str] = []
        for requirement in contract.requirements:
            fields: list[FieldRef] = []
            if isinstance(requirement, OutputRequirement):
                fields = [requirement.field]
            elif isinstance(requirement, GroupRequirement):
                fields = [requirement.field]
            if any(_field_matches(field, keys) for field in fields):
                requirement_ids.append(requirement.requirement_id)
        result.append(
            ResultProjection(
                output_name=projection.output_name,
                requirement_keys=tuple(sorted(set(requirement_ids))),
                source_columns=projection.source_columns,
            )
        )
    # A semantic_ref deliberately has no physical identifier to compare with
    # the AST. When the number of still-unclaimed public projections matches
    # the unresolved business concepts, bind them positionally for lineage
    # only. The requirement remains ``unverified`` and lowers quality; any
    # additional projection still remains an explicit contract violation.
    semantic_concepts: list[list[str]] = []
    concept_index: dict[str, int] = {}
    for requirement in contract.requirements:
        if not isinstance(requirement, OutputRequirement | GroupRequirement):
            continue
        if requirement.field.field or not requirement.field.semantic_ref:
            continue
        key = requirement.field.semantic_ref.casefold()
        index = concept_index.get(key)
        if index is None:
            concept_index[key] = len(semantic_concepts)
            semantic_concepts.append([requirement.requirement_id])
        else:
            semantic_concepts[index].append(requirement.requirement_id)
    unclaimed = [
        index for index, item in enumerate(result) if not item.requirement_keys
    ]
    if semantic_concepts and len(unclaimed) == len(semantic_concepts):
        for projection_index, requirement_ids in zip(
            unclaimed, semantic_concepts, strict=True
        ):
            projection = result[projection_index]
            result[projection_index] = ResultProjection(
                output_name=projection.output_name,
                requirement_keys=tuple(sorted(requirement_ids)),
                source_columns=projection.source_columns,
            )
    return tuple(result)


def analyze_query_specification_alignment(
    statements: list[str] | tuple[str, ...],
    contract: QuerySpecification,
    *,
    dialect: str | None,
) -> SqlContractValidation:
    """Compare every generated plan with the same active specification revision."""
    try:
        observed = [_observe(statement, dialect) for statement in statements]
    except Exception as exc:
        return SqlContractValidation(
            error=f"SQL contract parsing failed: {exc}",
            status="unsupported",
            requirements=(),
            per_plan_coverage=(),
            per_plan_projections=(),
        )
    coverages: list[set[str]] = []
    states_by_plan: list[dict[str, VerificationState]] = []
    projections = [_project_requirement_lineage(item, contract) for item in observed]
    for plan in observed:
        states = {
            requirement.requirement_id: _requirement_state(requirement, plan, contract)
            for requirement in contract.requirements
        }
        states_by_plan.append(states)
        coverages.append(
            {
                requirement_id
                for requirement_id, state in states.items()
                if state != "violated"
            }
        )

    violations: list[str] = []
    distributable = {
        requirement.requirement_id
        for requirement in contract.requirements
        if isinstance(requirement, OutputRequirement)
    }
    universal = {
        requirement.requirement_id
        for requirement in contract.requirements
        if requirement.requirement_id not in distributable
        and not isinstance(requirement, OrderRequirement)
    }
    global_requirements = {
        requirement.requirement_id
        for requirement in contract.requirements
        if isinstance(requirement, OrderRequirement)
    }
    if contract.limit is not None:
        if len(observed) != 1:
            violations.append(
                "Global limit specification must be implemented by one plan"
            )
        elif observed[0].limit != contract.limit:
            violations.append(
                f"Plan limit {observed[0].limit!r} does not match specification {contract.limit}"
            )
    if len(observed) > 1 and global_requirements:
        violations.append("Global order/limit contract must be implemented by one plan")
    if len(observed) > 1 and not distributable:
        violations.append("Contract has no distributable outputs and must use one plan")
    for index, coverage in enumerate(coverages):
        missing_universal = universal - coverage
        if missing_universal:
            violations.append(
                f"Plan {index + 1} omits universal specification requirements: "
                + ", ".join(sorted(missing_universal))
            )
        if len(observed) > 1 and not (coverage & distributable):
            violations.append(
                f"Plan {index + 1} covers no distributable output requirement"
            )
    if distributable:
        output_coverage = [coverage & distributable for coverage in coverages]
        union = set().union(*output_coverage) if output_coverage else set()
        if union != distributable:
            violations.append(
                "Contract outputs not covered by any plan: "
                + ", ".join(sorted(distributable - union))
            )
        for left_index, left in enumerate(output_coverage):
            for right_index, right in enumerate(
                output_coverage[left_index + 1 :], left_index + 1
            ):
                overlap = left & right
                if overlap:
                    # Two plans emitting the same output duplicates rows once
                    # the batch is merged.
                    violations.append(
                        f"Plans {left_index + 1} and {right_index + 1} "
                        "overlap output requirements: " + ", ".join(sorted(overlap))
                    )
        for requirement in contract.requirements:
            if (
                not isinstance(requirement, OutputRequirement)
                or not requirement.operands
            ):
                continue
            for index, coverage in enumerate(coverages):
                if requirement.requirement_id in coverage and not set(
                    requirement.operands
                ).issubset(coverage):
                    violations.append(
                        f"Plan {index + 1} separates derived output "
                        f"{requirement.requirement_id} from its operands"
                    )

    allowed_predicate_fields = {
        key
        for requirement in contract.requirements
        if isinstance(requirement, PredicateRequirement)
        for key in _ref_keys(requirement.field)
    } | {
        key
        for requirement in contract.requirements
        if isinstance(requirement, TimeWindowRequirement)
        for field in requirement.fields
        for key in _ref_keys(field)
    }
    for index, plan in enumerate(observed):
        extras = {
            key
            for keys, _operator, _values in plan.predicates
            for key in keys
            if "." not in key and key not in allowed_predicate_fields
        }
        if extras:
            violations.append(
                f"Plan {index + 1} adds unconfirmed business predicates: "
                + ", ".join(sorted(extras))
            )

    # Joins are deliberately absent from this list.  Which tables it takes to
    # connect two business entities is a property of the schema, not of the
    # contract: a many-to-many bridge is mandatory yet can never be named by an
    # assessor that only ever saw the question.  The join the user did decide
    # is a business-relation requirement, and ``_requirement_state`` verifies it.

    allowed_group_fields = {
        key
        for requirement in contract.requirements
        if isinstance(requirement, GroupRequirement)
        for key in _ref_keys(requirement.field)
    }
    group_requirement_ids = {
        requirement.requirement_id
        for requirement in contract.requirements
        if isinstance(requirement, GroupRequirement)
    }
    for index, (plan, lineage) in enumerate(zip(observed, projections, strict=True)):
        extra_outputs = [
            projection.output_name
            for projection in lineage
            if not projection.requirement_keys
        ]
        if extra_outputs:
            violations.append(
                f"Plan {index + 1} adds unconfirmed public outputs: "
                + ", ".join(extra_outputs)
            )
        allowed_plan_groups = allowed_group_fields | {
            projection.output_name.casefold()
            for projection in lineage
            if set(projection.requirement_keys) & group_requirement_ids
        }
        extra_groups = {
            key
            for key in plan.public_group_fields
            if "." not in key and key not in allowed_plan_groups
        }
        if extra_groups:
            violations.append(
                f"Plan {index + 1} adds unconfirmed public grouping: "
                + ", ".join(sorted(extra_groups))
            )

    all_coverage = set().union(*coverages) if coverages else set()
    requirements = tuple(
        RequirementVerification(
            requirement_id=requirement.requirement_id,
            state=(
                "violated"
                if requirement.requirement_id not in all_coverage
                else (
                    "unverified"
                    if all(
                        states.get(requirement.requirement_id) != "satisfied"
                        for states in states_by_plan
                    )
                    else "satisfied"
                )
            ),
            reason=(
                f"SQL does not implement {requirement.clause} clause"
                if requirement.requirement_id not in all_coverage
                else (
                    f"{requirement.clause} clause is only partially observable"
                    if all(
                        states.get(requirement.requirement_id) != "satisfied"
                        for states in states_by_plan
                    )
                    else ""
                )
            ),
        )
        for requirement in contract.requirements
    )
    if violations or any(
        requirement.state == "violated" for requirement in requirements
    ):
        missing = [
            requirement.requirement_id
            for requirement in requirements
            if requirement.state == "violated"
        ]
        parts = list(violations)
        if missing:
            parts.append("Missing specification requirements: " + ", ".join(missing))
        error = "; ".join(dict.fromkeys(parts))
        status: VerificationOverall = "partial"
    elif any(requirement.state == "unverified" for requirement in requirements):
        error = None
        status = "partial"
    else:
        error = None
        status = "verified"
    return SqlContractValidation(
        error=error,
        status=status,
        requirements=requirements,
        per_plan_coverage=tuple(frozenset(item) for item in coverages),
        per_plan_projections=tuple(projections),
    )
