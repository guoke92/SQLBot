"""Protocol plan facts used for validation; never a source of business intent."""

from __future__ import annotations

from typing import Literal

import sqlglot
from pydantic import BaseModel, ConfigDict
from sqlglot import exp


class PlanFacts(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    resources: tuple[str, ...] = ()
    fields: tuple[str, ...] = ()
    outputs: tuple[str, ...] = ()
    output_expressions: tuple[str, ...] = ()
    output_fields: tuple[str, ...] = ()
    aggregations: tuple[str, ...] = ()
    aggregation_count: int = 0
    predicates: tuple[str, ...] = ()
    predicate_fields: tuple[str, ...] = ()
    groups: tuple[str, ...] = ()
    group_fields: tuple[str, ...] = ()
    ordering: tuple[str, ...] = ()
    order_fields: tuple[str, ...] = ()
    joins: tuple[str, ...] = ()
    subquery_count: int = 0
    cte_count: int = 0
    set_operation_count: int = 0
    case_count: int = 0
    window_count: int = 0
    distinct_count: int = 0
    arithmetic_count: int = 0
    explicit_limit: int | None = None
    parser_coverage: Literal["full", "partial", "unsupported"] = "unsupported"


def sqlglot_dialect_for(type_key: str | None) -> str | None:
    """Closest sqlglot dialect for a protocol type key; None if unknown."""
    key = (type_key or "").strip()
    if not key:
        return None
    try:
        from apps.protocol.registry import get_spec

        return get_spec(key).sqlglot_dialect
    except Exception:
        return None


def _cte_aliases(statement: exp.Expression) -> set[str]:
    return {cte.alias for cte in statement.find_all(exp.CTE) if cte.alias}


def _relation_table_name(node: exp.Expression | None) -> str | None:
    if node is None:
        return None
    if isinstance(node, exp.Table):
        return node.name
    if isinstance(node, exp.Alias):
        return _relation_table_name(node.this) or node.alias
    table = node.find(exp.Table)
    return table.name if isinstance(table, exp.Table) else None


def _physical_join_sql(statement: exp.Expression, *, dialect: str | None) -> list[str]:
    """Joins to base tables only. CTE-to-CTE alignment is not a catalog relation."""
    cte_aliases = _cte_aliases(statement)
    joins: list[str] = []
    for join in statement.find_all(exp.Join):
        name = _relation_table_name(join.this)
        if name and name in cte_aliases:
            continue
        joins.append(join.sql(dialect=dialect))
    return joins


def extract_sql_plan_facts(sql: str, *, dialect: str | None = None) -> PlanFacts:
    try:
        statements = [
            item for item in sqlglot.parse(sql, dialect=dialect) if item is not None
        ]
    except Exception:
        return PlanFacts(parser_coverage="unsupported")
    if not statements:
        return PlanFacts(parser_coverage="unsupported")
    resources: list[str] = []
    fields: list[str] = []
    outputs: list[str] = []
    output_expressions: list[str] = []
    output_fields: list[str] = []
    aggregations: list[str] = []
    aggregation_count = 0
    predicates: list[str] = []
    predicate_fields: list[str] = []
    groups: list[str] = []
    group_fields: list[str] = []
    ordering: list[str] = []
    order_fields: list[str] = []
    limits: list[int] = []
    joins: list[str] = []
    subquery_count = 0
    cte_count = 0
    set_operation_count = 0
    case_count = 0
    window_count = 0
    distinct_count = 0
    arithmetic_count = 0
    for statement in statements:
        resources.extend(
            table.name for table in statement.find_all(exp.Table) if table.name
        )
        fields.extend(
            column.name for column in statement.find_all(exp.Column) if column.name
        )
        joins.extend(_physical_join_sql(statement, dialect=dialect))
        subquery_count += sum(1 for _ in statement.find_all(exp.Subquery))
        cte_count += sum(1 for _ in statement.find_all(exp.CTE))
        set_operation_count += sum(
            1 for item in statement.walk() if isinstance(item, exp.SetOperation)
        )
        case_count += sum(1 for _ in statement.find_all(exp.Case))
        window_count += sum(1 for _ in statement.find_all(exp.Window))
        distinct_count += sum(1 for _ in statement.find_all(exp.Distinct))
        arithmetic_count += sum(
            1
            for item in statement.walk()
            if isinstance(item, exp.Add | exp.Sub | exp.Mul | exp.Div | exp.Mod)
        )
        for select in statement.find_all(exp.Select):
            outputs.extend(
                item.alias_or_name or item.sql(dialect=dialect)
                for item in select.expressions
            )
            output_expressions.extend(
                item.sql(dialect=dialect) for item in select.expressions
            )
            for item in select.expressions:
                output_fields.extend(
                    column.name for column in item.find_all(exp.Column) if column.name
                )
            select_aggregations = list(select.find_all(exp.AggFunc))
            aggregation_count += len(select_aggregations)
            aggregations.extend(
                type(item).__name__.casefold() for item in select_aggregations
            )
            where = select.args.get("where")
            if isinstance(where, exp.Expression):
                predicates.append(where.sql(dialect=dialect))
                predicate_fields.extend(
                    column.name for column in where.find_all(exp.Column) if column.name
                )
            group = select.args.get("group")
            if isinstance(group, exp.Group):
                groups.extend(item.sql(dialect=dialect) for item in group.expressions)
                for item in group.expressions:
                    group_fields.extend(
                        column.name
                        for column in item.find_all(exp.Column)
                        if column.name
                    )
            order = select.args.get("order")
            if isinstance(order, exp.Order):
                ordering.extend(item.sql(dialect=dialect) for item in order.expressions)
                for item in order.expressions:
                    order_fields.extend(
                        column.name
                        for column in item.find_all(exp.Column)
                        if column.name
                    )
            limit = select.args.get("limit")
            if isinstance(limit, exp.Limit) and isinstance(
                limit.expression, exp.Literal
            ):
                try:
                    limits.append(int(limit.expression.this))
                except (TypeError, ValueError):
                    pass
    return PlanFacts(
        resources=tuple(dict.fromkeys(resources)),
        fields=tuple(dict.fromkeys(fields)),
        outputs=tuple(dict.fromkeys(outputs)),
        output_expressions=tuple(dict.fromkeys(output_expressions)),
        output_fields=tuple(dict.fromkeys(output_fields)),
        aggregations=tuple(dict.fromkeys(aggregations)),
        aggregation_count=aggregation_count,
        predicates=tuple(dict.fromkeys(predicates)),
        predicate_fields=tuple(dict.fromkeys(predicate_fields)),
        groups=tuple(dict.fromkeys(groups)),
        group_fields=tuple(dict.fromkeys(group_fields)),
        ordering=tuple(dict.fromkeys(ordering)),
        order_fields=tuple(dict.fromkeys(order_fields)),
        joins=tuple(dict.fromkeys(joins)),
        subquery_count=subquery_count,
        cte_count=cte_count,
        set_operation_count=set_operation_count,
        case_count=case_count,
        window_count=window_count,
        distinct_count=distinct_count,
        arithmetic_count=arithmetic_count,
        explicit_limit=min(limits) if limits else None,
        parser_coverage="full",
    )
