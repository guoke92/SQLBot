"""Configurable checks that run before ``execute_sql_sandbox`` hits the warehouse.

Rule kinds are mechanisms (catalog probe, enum discovery, closed-vocabulary
literals). Which kinds are on is agent-config data, merged the same way as
tool overrides and loop bounds. Business filters such as ``enable='Y'`` are
not a rule kind.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from apps.chat.tools.contract import failure_outcome

EXECUTE_SQL_TOOL_NAME = "execute_sql_sandbox"

_FIELD_HEAD = re.compile(r"^([A-Za-z_][\w]*)\s*:")
_ATTR = re.compile(r"(topk|labels|dict)=([^,\n]+)")
_LABEL_PAIR = re.compile(r"([^:|]+):([^|]*)")


def _catalog(sql: str, llm_service: Any) -> dict[str, Any] | None:
    del llm_service
    from apps.chat.tools.execute_sql import is_catalog_probe_sql

    if not is_catalog_probe_sql(sql):
        return None
    return failure_outcome(
        "Catalog probes are not allowed (information_schema / pg_catalog / "
        "SHOW COLUMNS / DESCRIBE). Table structure must come from Wiki or "
        "the schema context already in the prompt.",
        retryable=False,
        name=EXECUTE_SQL_TOOL_NAME,
    )


def _enum_discovery(sql: str, llm_service: Any) -> dict[str, Any] | None:
    from apps.chat.tools.execute_sql import _reject_enum_discovery

    return _reject_enum_discovery(sql, llm_service)


def _closed_columns(schema_by_table: Mapping[str, str]) -> dict[tuple[str, str], set[str]]:
    """Columns whose opened schema publishes a closed code set.

    A column is closed only when the schema line carries ``labels=`` or
    ``dict=``. ``topk=`` alone is a sample, not a vocabulary. Display names
    after the colon in ``labels=`` are not members of the code set.
    """
    found: dict[tuple[str, str], set[str]] = {}
    for table, body in schema_by_table.items():
        table_name = str(table or "").strip()
        if not table_name or not body:
            continue
        for raw_line in str(body).splitlines():
            line = raw_line.strip().lstrip("-").strip()
            head = _FIELD_HEAD.match(line)
            if head is None:
                continue
            attrs = {key: value.strip() for key, value in _ATTR.findall(line)}
            if "labels" not in attrs and "dict" not in attrs:
                continue
            codes: set[str] = set()
            topk = attrs.get("topk") or ""
            if topk:
                codes.update(part.strip() for part in topk.split("|") if part.strip())
            labels = attrs.get("labels") or ""
            for code, _label in _LABEL_PAIR.findall(labels):
                text = code.strip()
                if text:
                    codes.add(text)
            if not codes:
                continue
            found[(table_name.lower(), head.group(1).lower())] = codes
    return found


def _lookup_codes(
    columns: Mapping[tuple[str, str], set[str]],
    *,
    table: str,
    name: str,
) -> set[str] | None:
    field = name.lower()
    if not field:
        return None
    qualified = table.lower()
    if qualified:
        hit = columns.get((qualified, field))
        if hit:
            return hit
    matches = [codes for (tbl, col), codes in columns.items() if col == field]
    if len(matches) == 1:
        return matches[0]
    return None


def _string_literals(node: Any) -> list[str]:
    from sqlglot import exp

    values: list[str] = []
    for literal in node.find_all(exp.Literal):
        if not literal.is_string:
            continue
        text = str(literal.this or "").strip()
        if text:
            values.append(text)
    return values


def _closed_literal(sql: str, llm_service: Any) -> dict[str, Any] | None:
    from apps.chat.agent.knowledge import load_plane

    plane = load_plane()
    columns = _closed_columns(getattr(plane, "schema_by_table", {}) or {})
    if not columns:
        return None
    ds = getattr(llm_service, "ds", None) or getattr(llm_service, "datasource", None)
    dialect_name = getattr(ds, "type", None) or "mysql"
    try:
        import sqlglot
        from sqlglot import exp

        from apps.db.db import get_sqlglot_dialect

        dialect = get_sqlglot_dialect(str(dialect_name))
        tree = sqlglot.parse_one(sql, read=str(dialect or "mysql"))
    except Exception:
        return None
    if tree is None:
        return None

    alias_to_table: dict[str, str] = {}
    for tbl in tree.find_all(exp.Table):
        real = str(tbl.name or "").strip()
        alias = str(tbl.alias or "").strip()
        if real:
            alias_to_table[real.lower()] = real
        if alias and real:
            alias_to_table[alias.lower()] = real

    for predicate in tree.find_all(exp.EQ, exp.NEQ, exp.In, exp.Like):
        column = next(predicate.find_all(exp.Column), None)
        if column is None:
            continue
        qualifier = str(column.table or "").strip().lower()
        table = alias_to_table.get(qualifier, qualifier)
        codes = _lookup_codes(columns, table=table, name=str(column.name or ""))
        if not codes:
            continue
        folded = {item.casefold() for item in codes}
        if isinstance(predicate, (exp.Like, exp.ILike)):
            return failure_outcome(
                f"Column {column.name} has a closed code set. "
                "Filter it with = or IN using a physical code, not LIKE.",
                retryable=True,
                name=EXECUTE_SQL_TOOL_NAME,
            )
        for literal in _string_literals(predicate):
            if literal.casefold() in folded:
                continue
            shown = ", ".join(sorted(codes)[:12])
            return failure_outcome(
                f"Literal {literal!r} is not a physical code of {column.name}. "
                f"Use one of: {shown}.",
                retryable=True,
                name=EXECUTE_SQL_TOOL_NAME,
            )
    return None


_HANDLERS = {
    "catalog_probe": _catalog,
    "enum_discovery": _enum_discovery,
    "closed_literal": _closed_literal,
}


def enforce_sql_rules(sql: str, llm_service: Any) -> dict[str, Any] | None:
    """Return a tool failure for the first enabled rule that rejects ``sql``."""
    from apps.chat.agent_config.loader import load_agent_config_for_run

    config = load_agent_config_for_run()
    for kind, handler in _HANDLERS.items():
        if not config.rule_enabled(kind):
            continue
        failed = handler(sql, llm_service)
        if failed is not None:
            return failed
    return None
