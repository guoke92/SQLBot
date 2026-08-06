"""Deterministic SQL for the narrow single-table filter contract subset.

Complex shapes stay on the LLM path.  Compilation either returns a batch that
has already passed ``validate_plan``, or ``None`` so the caller falls back.
"""

from __future__ import annotations

from typing import Any

from apps.chat.planning import BatchParseResult, batch_from_compiled_sql
from apps.chat.query_contract import (
    LimitRequirement,
    OrderRequirement,
    PredicateRequirement,
    ProjectionRequirement,
    QueryContract,
    requirement_fields,
)
from apps.protocol.base import CAP_SQL_DIALECT

_ALLOWED_CLAUSES = frozenset({"projection", "predicate", "order", "limit"})
_OPERATOR_SQL = {
    "eq": "=",
    "ne": "<>",
    "gt": ">",
    "gte": ">=",
    "lt": "<",
    "lte": "<=",
    "like": "LIKE",
    "in": "IN",
    "not_in": "NOT IN",
    "is_null": "IS NULL",
    "is_not_null": "IS NOT NULL",
}


def try_compile_simple_batch(
    contract: QueryContract | None,
    llm_service: Any,
    *,
    question: str = "",
    intent_context: Any = None,
    default_limit: int | None = None,
) -> BatchParseResult | None:
    """Compile a single-table filter contract, or return ``None`` for LLM."""
    protocol = getattr(llm_service, "protocol", None)
    supports = getattr(protocol, "supports", None)
    if not callable(supports) or not supports(CAP_SQL_DIALECT):
        return None
    if contract is None:
        return None
    compiled = _compile_simple_sql(
        contract,
        protocol,
        getattr(llm_service, "ds", None),
        default_limit=default_limit,
    )
    if compiled is None:
        return None
    sql, resource = compiled
    return batch_from_compiled_sql(
        sql,
        llm_service,
        query_contract=contract,
        question=question,
        intent_context=intent_context,
        resources=[resource],
    )


def _compile_simple_sql(
    contract: QueryContract,
    protocol: Any,
    ds: Any,
    *,
    default_limit: int | None,
) -> tuple[str, str] | None:
    shape = _simple_filter_shape(contract)
    if shape is None:
        return None
    projection, predicates, orders, limit_value, resource = shape
    try:
        quote = protocol._quote_identifier
        schema = str(protocol.schema_namespace(ds) or "").strip()
    except AttributeError:
        return None

    table_sql = quote(resource)
    if schema:
        table_sql = f"{quote(schema)}.{table_sql}"

    if projection.mode == "all":
        select_sql = "*"
        select_names: frozenset[str] | None = None
    else:
        select_parts = [quote(field.field) for field in projection.fields]
        select_names = frozenset(field.field.casefold() for field in projection.fields)
        select_sql = ", ".join(select_parts)

    where_parts: list[str] = []
    for predicate in predicates:
        rendered = _render_predicate(predicate, quote)
        if rendered is None:
            return None
        where_parts.append(rendered)

    order_parts: list[str] = []
    for order in orders:
        column = _order_column(order, projection)
        if column is None:
            return None
        if select_names is not None and column.casefold() not in select_names:
            return None
        order_parts.append(f"{quote(column)} {order.direction.upper()}")

    limit = limit_value if limit_value is not None else default_limit

    pieces = [f"SELECT {select_sql} FROM {table_sql}"]
    if where_parts:
        pieces.append("WHERE " + " AND ".join(where_parts))
    if order_parts:
        pieces.append("ORDER BY " + ", ".join(order_parts))
    if limit is not None and int(limit) > 0:
        pieces.append(f"LIMIT {int(limit)}")
    return " ".join(pieces), resource


def _simple_filter_shape(
    contract: QueryContract,
) -> (
    tuple[
        ProjectionRequirement,
        list[PredicateRequirement],
        list[OrderRequirement],
        int | None,
        str,
    ]
    | None
):
    if any(
        requirement.clause not in _ALLOWED_CLAUSES
        for requirement in contract.requirements
    ):
        return None

    projection: ProjectionRequirement | None = None
    predicates: list[PredicateRequirement] = []
    orders: list[OrderRequirement] = []
    limit_value: int | None = None
    resources: dict[str, str] = {}

    for requirement in contract.requirements:
        for field in requirement_fields(requirement):
            name = field.resource_name
            if name:
                resources.setdefault(name.casefold(), name)

        if isinstance(requirement, ProjectionRequirement):
            if projection is not None:
                return None
            projection = requirement
        elif isinstance(requirement, PredicateRequirement):
            if requirement.operator not in _OPERATOR_SQL:
                return None
            predicates.append(requirement)
        elif isinstance(requirement, OrderRequirement):
            orders.append(requirement)
        elif isinstance(requirement, LimitRequirement):
            if limit_value is not None:
                return None
            limit_value = int(requirement.value)
        else:
            return None

    if projection is None or len(resources) != 1:
        return None
    return projection, predicates, orders, limit_value, next(iter(resources.values()))


def _order_column(
    order: OrderRequirement, projection: ProjectionRequirement
) -> str | None:
    if order.field is not None:
        return order.field.field
    if not order.output_slot_id:
        return None
    if order.output_slot_id != projection.slot_id:
        return None
    if projection.mode != "listed" or len(projection.fields) != 1:
        return None
    return projection.fields[0].field


def _render_predicate(predicate: PredicateRequirement, quote: Any) -> str | None:
    column = quote(predicate.field.field)
    operator = predicate.operator
    sql_op = _OPERATOR_SQL.get(operator)
    if sql_op is None:
        return None
    if operator in {"is_null", "is_not_null"}:
        return f"{column} {sql_op}"
    if operator in {"in", "not_in"}:
        if not predicate.values:
            return None
        values = ", ".join(_sql_literal(value) for value in predicate.values)
        return f"{column} {sql_op} ({values})"
    if len(predicate.values) != 1:
        return None
    return f"{column} {sql_op} {_sql_literal(predicate.values[0])}"


def _sql_literal(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    text = str(value)
    return "'" + text.replace("'", "''") + "'"
