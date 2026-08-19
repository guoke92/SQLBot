"""Deterministic grouped-aggregation window helpers.

Plan facts describe the SQL; these helpers only add an ordered display window
and a one-row totals wrap. They never reinterpret business meaning.
"""

from __future__ import annotations

from typing import Any

import sqlglot
from sqlglot import exp

from apps.chat.plan_facts import extract_sql_plan_facts

GROUP_COUNT_ALIAS = "__group_count"
_NO_ALIAS_ORDER_DIALECTS = frozenset({"hive"})


def ensure_grouped_metric_order(sql: str, *, dialect: str | None = None) -> str:
    """ORDER BY the first aggregated output when a grouped query has no sort.

    Hive cannot ORDER BY select aliases; leave those plans unchanged.
    """
    text = (sql or "").strip()
    if not text or (dialect or "").casefold() in _NO_ALIAS_ORDER_DIALECTS:
        return sql
    facts = extract_sql_plan_facts(text, dialect=dialect)
    if (
        facts.parser_coverage == "unsupported"
        or not facts.group_fields
        or facts.order_fields
        or facts.aggregation_count < 1
    ):
        return sql
    try:
        parsed = sqlglot.parse_one(text, dialect=dialect)
    except Exception:
        return sql
    if not isinstance(parsed, exp.Select) or parsed.args.get("order"):
        return sql
    metric: exp.Expression | None = None
    for item in parsed.expressions:
        if item.find(exp.AggFunc):
            metric = item
            break
    if metric is None:
        return sql
    alias = metric.alias_or_name
    if not alias:
        return sql
    ordered = parsed.order_by(exp.Ordered(this=exp.to_identifier(alias), desc=True))
    return ordered.sql(dialect=dialect)


def aggregation_totals_sql(sql: str, *, dialect: str | None = None) -> str | None:
    """Wrap a grouped aggregation so metric totals and group count are one row."""
    text = (sql or "").strip()
    if not text:
        return None
    facts = extract_sql_plan_facts(text, dialect=dialect)
    if (
        facts.parser_coverage == "unsupported"
        or not facts.group_fields
        or facts.aggregation_count < 1
    ):
        return None
    try:
        parsed = sqlglot.parse_one(text, dialect=dialect)
    except Exception:
        return None
    if not isinstance(parsed, exp.Select):
        return None
    inner = parsed.copy()
    inner.set("order", None)
    inner.set("limit", None)
    outer_exprs: list[exp.Expression] = [
        exp.Count(this=exp.Star()).as_(GROUP_COUNT_ALIAS)
    ]
    for item in inner.expressions:
        if item.find(exp.AggFunc) is None:
            continue
        alias = item.alias_or_name
        if not alias:
            continue
        outer_exprs.append(exp.Sum(this=exp.column(alias)).as_(alias))
    if len(outer_exprs) == 1:
        return None
    wrapped = (
        exp.Select().select(*outer_exprs).from_(inner.subquery(alias="__agg_groups"))
    )
    return wrapped.sql(dialect=dialect)


def apply_grouped_metric_order(
    plans: list[dict[str, Any]],
    *,
    dialect: str | None,
) -> bool:
    """Rewrite grouped plans in place. Returns True when any SQL changed."""
    changed = False
    for plan in plans:
        sql = str(plan.get("sql") or (plan.get("payload") or {}).get("sql") or "")
        rewritten = ensure_grouped_metric_order(sql, dialect=dialect)
        if not rewritten or rewritten == sql:
            continue
        payload = dict(plan.get("payload") or {})
        payload["sql"] = rewritten
        plan["sql"] = rewritten
        plan["payload"] = payload
        if plan.get("format_statement"):
            plan["format_statement"] = rewritten
        changed = True
    return changed
