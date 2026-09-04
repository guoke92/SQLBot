"""AST-based incremental SQL patcher using sqlglot."""

from __future__ import annotations

from typing import Any, Mapping
import sqlglot
from sqlglot import exp, parse_one

from apps.chat.tools.base import failure_result, success_result
from apps.conversation.tooling import ToolResult


def patch_and_compile_sql(
    base_sql: str,
    action: str,
    payload: Mapping[str, Any],
    *,
    dialect: str | None = None,
) -> ToolResult:
    """Incrementally patch base_sql using AST operations.
    
    Actions:
    - add_dimension: add field(s) to SELECT and GROUP BY (e.g. payload={'fields': ['dept', 'region']})
    - add_filter: add WHERE predicate (e.g. payload={'condition': "status NOT IN ('CANCELLED')"})
    - replace_filter: replace or update filter condition (e.g. payload={'old_field': 'status', 'new_condition': "status IN ('PAID')"})
    - change_limit: update or remove LIMIT (e.g. payload={'limit': 100})
    - change_order: add or update ORDER BY (e.g. payload={'order': 'total DESC'})
    """
    if not (base_sql or "").strip():
        return failure_result("base_sql cannot be empty for incremental patch")

    try:
        read_dialect = dialect or "mysql"
        tree = parse_one(base_sql, read=read_dialect)
    except Exception as exc:
        return failure_result(
            f"Failed to parse base_sql with AST parser: {exc}. Please provide a full SQL directly."
        )

    try:
        if action == "add_dimension":
            fields = payload.get("fields") or []
            if isinstance(fields, str):
                fields = [fields]
            for f in fields:
                if f and str(f).strip():
                    tree.select(str(f).strip(), copy=False)
                    tree.group_by(str(f).strip(), copy=False)

        elif action == "add_filter":
            condition = str(payload.get("condition") or "").strip()
            if condition:
                tree.where(condition, copy=False)

        elif action == "replace_filter":
            old_field = str(payload.get("old_field") or "").strip()
            new_condition = str(payload.get("new_condition") or "").strip()
            if old_field:
                where_clause = tree.find(exp.Where)
                if where_clause:
                    for node in list(where_clause.find_all(exp.Column)):
                        if node.name.lower() == old_field.lower():
                            parent = node.find_ancestor(exp.Binary, exp.In, exp.Between)
                            if parent:
                                parent.replace(exp.true())
            if new_condition:
                tree.where(new_condition, copy=False)

        elif action == "change_limit":
            limit_val = payload.get("limit")
            if limit_val is not None:
                tree.set("limit", exp.Limit(expression=exp.Literal.number(int(limit_val))))
            else:
                tree.set("limit", None)

        elif action == "change_order":
            order_clause = str(payload.get("order") or "").strip()
            if order_clause:
                tree.set("order", parse_one(f"ORDER BY {order_clause}"))

        else:
            return failure_result(f"Unsupported patch action: {action}")

        patched_sql = tree.sql(dialect=read_dialect)
        return success_result(
            f"Successfully patched SQL with action '{action}'",
            data={"sql": patched_sql, "action": action, "dialect": read_dialect},
        )
    except Exception as exc:
        return failure_result(
            f"Error applying patch '{action}': {exc}. Fall back to generating full SQL."
        )
