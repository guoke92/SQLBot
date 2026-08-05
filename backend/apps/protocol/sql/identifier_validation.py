"""SQL catalog extraction and clause-oriented contract verification."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

import sqlglot
from sqlglot import exp
from sqlglot.optimizer.scope import Scope, traverse_scope

from apps.chat.query_contract import (
    ContractRequirement,
    FieldRef,
    GroupRequirement,
    LimitRequirement,
    OrderRequirement,
    OutputRequirement,
    PredicateRequirement,
    ProjectionRequirement,
    QueryContract,
    RelationPair,
    RelationRequirement,
    TimeWindowRequirement,
)


@dataclass(frozen=True)
class PhysicalColumnRef:
    column_name: str
    table_name: str | None = None
    candidate_tables: tuple[str, ...] = ()


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
class SlotVerification:
    slot_id: str
    state: VerificationState
    reason: str = ""


@dataclass(frozen=True)
class SqlContractValidation:
    error: str | None
    status: VerificationOverall
    slots: tuple[SlotVerification, ...]
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
        if isinstance(parent, (exp.Group, exp.Order, exp.Having, exp.Qualify)):
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
            physical_scope_tables: list[str] = []
            has_virtual = False
            for source in sources.values():
                if isinstance(source, exp.Table):
                    table = _norm(source.name)
                    if table:
                        physical_tables.add(table)
                        if table not in physical_scope_tables:
                            physical_scope_tables.append(table)
                else:
                    has_virtual = True
            for column in scope.columns:
                name = _norm(column.name)
                if not name or name == "*" or _is_output_alias(column, scope):
                    continue
                ref: PhysicalColumnRef | None = None
                table_ref = _norm(column.table).casefold()
                if table_ref and isinstance(sources.get(table_ref), exp.Table):
                    table = _norm(sources[table_ref].name)
                    ref = PhysicalColumnRef(name, table_name=table)
                elif physical_scope_tables and not has_virtual:
                    ref = PhysicalColumnRef(
                        name,
                        candidate_tables=tuple(physical_scope_tables),
                    )
                if ref is not None and ref not in seen:
                    refs.append(ref)
                    seen.add(ref)
    return SqlIdentifierUsage(
        physical_tables=frozenset(physical_tables),
        physical_columns=tuple(refs),
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
    while isinstance(current, (exp.Cast, exp.Paren)):
        current = current.this
    if isinstance(current, exp.Literal):
        return str(current.this)
    if isinstance(current, (exp.Boolean, exp.Null)):
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
    return (
        _field_matches(pair.left, left) and _field_matches(pair.right, right)
    ) or (_field_matches(pair.left, right) and _field_matches(pair.right, left))


def _matching_relation_joins(
    requirement: RelationRequirement,
    observed: _ObservedPlan,
) -> list[tuple[set[str], set[str], str]]:
    return [
        join
        for join in observed.joins
        if any(
            _relation_pair_matches(pair, join[0], join[1])
            for pair in requirement.pairs
        )
    ]


def _relation_satisfied(
    requirement: RelationRequirement, observed: _ObservedPlan
) -> bool:
    matched = _matching_relation_joins(requirement, observed)
    for pair in requirement.pairs:
        if not any(
            _relation_pair_matches(pair, left, right)
            for left, right, _kind in matched
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
    if (
        not observed.has_union
        or not kinds
        or not all(kind == "left" for kind in kinds)
    ):
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


def _is_cross_resource_join(left: set[str], right: set[str]) -> bool:
    left_resources = _join_resources(left)
    right_resources = _join_resources(right)
    return any(
        left_resource != right_resource
        for left_resource in left_resources
        for right_resource in right_resources
    )


def _join_matches_contract(
    left: set[str],
    right: set[str],
    relations: list[RelationRequirement],
) -> bool:
    return any(
        _relation_pair_matches(pair, left, right)
        for relation in relations
        for pair in relation.pairs
    )


def _slot_state(
    requirement: ContractRequirement,
    observed: _ObservedPlan,
    contract: QueryContract,
) -> VerificationState:
    if isinstance(requirement, ProjectionRequirement):
        satisfied = (
            observed.has_star
            if requirement.mode == "all"
            else all(
                _field_matches(field, observed.projection_fields)
                for field in requirement.fields
            )
        )
    elif isinstance(requirement, OutputRequirement):
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
    elif isinstance(requirement, RelationRequirement):
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
            else {requirement.output_slot_id.casefold()}
        )
        if requirement.output_slot_id:
            output = contract.by_slot().get(requirement.output_slot_id)
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
    elif isinstance(requirement, LimitRequirement):
        satisfied = observed.limit == requirement.value
    else:
        satisfied = False
    return "satisfied" if satisfied else "violated"


def _project_requirement_lineage(
    observed: _ObservedPlan,
    contract: QueryContract,
) -> tuple[ResultProjection, ...]:
    result: list[ResultProjection] = []
    for projection in observed.projections:
        keys = set(projection.source_columns) | {projection.output_name.casefold()}
        slots: list[str] = []
        for requirement in contract.requirements:
            fields: list[FieldRef] = []
            if isinstance(requirement, OutputRequirement):
                fields = [requirement.field]
            elif isinstance(requirement, GroupRequirement):
                fields = [requirement.field]
            elif isinstance(requirement, ProjectionRequirement):
                fields = requirement.fields
            if any(_field_matches(field, keys) for field in fields):
                slots.append(requirement.slot_id)
        result.append(
            ResultProjection(
                output_name=projection.output_name,
                requirement_keys=tuple(sorted(set(slots))),
                source_columns=projection.source_columns,
            )
        )
    return tuple(result)


def analyze_sql_contract_structure(
    statements: list[str] | tuple[str, ...],
    contract: QueryContract,
    *,
    dialect: str | None,
) -> SqlContractValidation:
    """Compare every generated plan with the same frozen query contract."""
    try:
        observed = [_observe(statement, dialect) for statement in statements]
    except Exception as exc:
        return SqlContractValidation(
            error=f"SQL contract parsing failed: {exc}",
            status="unsupported",
            slots=(),
            per_plan_coverage=(),
            per_plan_projections=(),
        )
    coverages: list[set[str]] = []
    states_by_plan: list[dict[str, VerificationState]] = []
    projections = [_project_requirement_lineage(item, contract) for item in observed]
    for plan in observed:
        states = {
            requirement.slot_id: _slot_state(requirement, plan, contract)
            for requirement in contract.requirements
        }
        states_by_plan.append(states)
        coverages.append(
            {slot_id for slot_id, state in states.items() if state != "violated"}
        )

    violations: list[str] = []
    distributable = {
        requirement.slot_id
        for requirement in contract.requirements
        if isinstance(requirement, (OutputRequirement, ProjectionRequirement))
    }
    universal = {
        requirement.slot_id
        for requirement in contract.requirements
        if requirement.slot_id not in distributable
        and not isinstance(requirement, (OrderRequirement, LimitRequirement))
    }
    global_slots = {
        requirement.slot_id
        for requirement in contract.requirements
        if isinstance(requirement, (OrderRequirement, LimitRequirement))
    }
    if len(observed) > 1 and global_slots:
        violations.append("Global order/limit contract must be implemented by one plan")
    if len(observed) > 1 and not distributable:
        violations.append("Contract has no distributable outputs and must use one plan")
    for index, coverage in enumerate(coverages):
        missing_universal = universal - coverage
        if missing_universal:
            violations.append(
                f"Plan {index + 1} omits universal contract slots: "
                + ", ".join(sorted(missing_universal))
            )
        if len(observed) > 1 and not (coverage & distributable):
            violations.append(f"Plan {index + 1} covers no distributable output slot")
    if distributable:
        output_coverage = [coverage & distributable for coverage in coverages]
        union = set().union(*output_coverage) if output_coverage else set()
        if union != distributable:
            violations.append(
                "Batch does not cover output slots: "
                + ", ".join(sorted(distributable - union))
            )
        for left_index, left in enumerate(output_coverage):
            for right_index, right in enumerate(
                output_coverage[left_index + 1 :], left_index + 1
            ):
                overlap = left & right
                if overlap:
                    violations.append(
                        f"Plans {left_index + 1} and {right_index + 1} overlap output slots: "
                        + ", ".join(sorted(overlap))
                    )
        for requirement in contract.requirements:
            if (
                not isinstance(requirement, OutputRequirement)
                or not requirement.operands
            ):
                continue
            for index, coverage in enumerate(coverages):
                if requirement.slot_id in coverage and not set(
                    requirement.operands
                ).issubset(coverage):
                    violations.append(
                        f"Plan {index + 1} separates derived output "
                        f"{requirement.slot_id} from its operands"
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

    relation_requirements = [
        requirement
        for requirement in contract.requirements
        if isinstance(requirement, RelationRequirement)
    ]
    for index, plan in enumerate(observed):
        unconfirmed_joins = [
            (left, right)
            for left, right, _kind in plan.joins
            if _is_cross_resource_join(left, right)
            and not _join_matches_contract(left, right, relation_requirements)
        ]
        if unconfirmed_joins:
            rendered = [
                f"({'/'.join(sorted(left))})=({'/'.join(sorted(right))})"
                for left, right in unconfirmed_joins
            ]
            violations.append(
                f"Plan {index + 1} adds unconfirmed cross-resource joins: "
                + ", ".join(rendered)
            )

    projection_is_open = any(
        isinstance(requirement, ProjectionRequirement) and requirement.mode == "all"
        for requirement in contract.requirements
    )
    allowed_group_fields = {
        key
        for requirement in contract.requirements
        if isinstance(requirement, GroupRequirement)
        for key in _ref_keys(requirement.field)
    }
    group_slot_ids = {
        requirement.slot_id
        for requirement in contract.requirements
        if isinstance(requirement, GroupRequirement)
    }
    for index, (plan, lineage) in enumerate(zip(observed, projections, strict=True)):
        if not projection_is_open:
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
            if set(projection.requirement_keys) & group_slot_ids
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
    slots = tuple(
        SlotVerification(
            slot_id=requirement.slot_id,
            state=(
                "violated"
                if requirement.slot_id not in all_coverage
                else (
                    "unverified"
                    if all(
                        states.get(requirement.slot_id) != "satisfied"
                        for states in states_by_plan
                    )
                    else "satisfied"
                )
            ),
            reason=(
                f"SQL does not implement {requirement.clause} clause"
                if requirement.slot_id not in all_coverage
                else (
                    f"{requirement.clause} clause is only partially observable"
                    if all(
                        states.get(requirement.slot_id) != "satisfied"
                        for states in states_by_plan
                    )
                    else ""
                )
            ),
        )
        for requirement in contract.requirements
    )
    if violations or any(slot.state == "violated" for slot in slots):
        missing = [slot.slot_id for slot in slots if slot.state == "violated"]
        parts = list(violations)
        if missing:
            parts.append("Missing contract slots: " + ", ".join(missing))
        error = "; ".join(dict.fromkeys(parts))
        status: VerificationOverall = "partial"
    elif any(slot.state == "unverified" for slot in slots):
        error = None
        status = "partial"
    else:
        error = None
        status = "verified"
    return SqlContractValidation(
        error=error,
        status=status,
        slots=slots,
        per_plan_coverage=tuple(frozenset(item) for item in coverages),
        per_plan_projections=tuple(projections),
    )
