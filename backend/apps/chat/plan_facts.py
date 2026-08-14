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
    predicates: tuple[str, ...] = ()
    predicate_fields: tuple[str, ...] = ()
    groups: tuple[str, ...] = ()
    group_fields: tuple[str, ...] = ()
    ordering: tuple[str, ...] = ()
    order_fields: tuple[str, ...] = ()
    explicit_limit: int | None = None
    parser_coverage: Literal["full", "partial", "unsupported"] = "unsupported"


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
    predicates: list[str] = []
    predicate_fields: list[str] = []
    groups: list[str] = []
    group_fields: list[str] = []
    ordering: list[str] = []
    order_fields: list[str] = []
    limits: list[int] = []
    for statement in statements:
        resources.extend(
            table.name for table in statement.find_all(exp.Table) if table.name
        )
        fields.extend(
            column.name for column in statement.find_all(exp.Column) if column.name
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
            aggregations.extend(
                type(item).__name__.casefold() for item in select.find_all(exp.AggFunc)
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
        predicates=tuple(dict.fromkeys(predicates)),
        predicate_fields=tuple(dict.fromkeys(predicate_fields)),
        groups=tuple(dict.fromkeys(groups)),
        group_fields=tuple(dict.fromkeys(group_fields)),
        ordering=tuple(dict.fromkeys(ordering)),
        order_fields=tuple(dict.fromkeys(order_fields)),
        explicit_limit=min(limits) if limits else None,
        parser_coverage="full",
    )
