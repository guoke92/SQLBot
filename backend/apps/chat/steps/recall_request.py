"""RecallRequest — the single input contract for turn-scoped knowledge recall.

单轮：请求 = 用户问题。
多轮（continue / revise）：跟进短句（「加上城市维度」）本身召不回任何有用页面，
上一轮的知识面必须**显式带回来**——这里把「上轮问题 + 本轮问题」拼成检索词，
把基线 SQL 引用的表/列 pin 成工作集与字段投影的必留项，把上轮 page_keys 作为
待复水（rehydrate）的页面。召回内核只认这个对象，不再散落地读 memory_slots。
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from common.utils.utils import SQLBotLogUtil

_MAX_PRIOR_QUESTIONS = 2
_MAX_PIN_PAGES = 12


@dataclass(frozen=True)
class RecallRequest:
    """What one turn asks the recall kernel for."""

    query: str
    question: str = ""
    pin_tables: tuple[str, ...] = ()
    pin_pages: tuple[str, ...] = ()
    required_fields: Mapping[str, tuple[str, ...]] = field(default_factory=dict)

    @classmethod
    def simple(cls, query: str) -> RecallRequest:
        text = str(query or "").strip()
        return cls(query=text, question=text)

    @classmethod
    def coerce(cls, value: RecallRequest | str | None) -> RecallRequest:
        if isinstance(value, RecallRequest):
            return value
        return cls.simple(str(value or ""))

    @property
    def is_continuation(self) -> bool:
        return bool(self.pin_tables or self.pin_pages)

    def as_span_fields(self) -> dict[str, Any]:
        return {
            "retrieval_query": self.query,
            "pin_tables": list(self.pin_tables),
            "pin_pages": list(self.pin_pages)[:20],
            "required_fields": {
                table: list(names) for table, names in self.required_fields.items()
            },
        }


def sql_references(
    sql: str, *, dialect: str | None = None
) -> tuple[list[str], dict[str, set[str]]]:
    """Physical tables and per-table columns referenced by ``sql``.

    Aliases are resolved; unqualified columns are attributed to every table in
    the statement (over-inclusion only widens the keep set, never narrows it).
    Parse failures degrade to ``([], {})`` — the turn still recalls normally.
    """
    text = str(sql or "").strip()
    if not text:
        return [], {}
    try:
        import sqlglot
        from sqlglot import exp

        tree = sqlglot.parse_one(text, read=dialect or None)
    except Exception as exc:  # noqa: BLE001 — baseline SQL may be dialect-odd
        SQLBotLogUtil.warning("sql_references parse degraded: %s", exc)
        return [], {}

    tables: list[str] = []
    alias_to_table: dict[str, str] = {}
    for node in tree.find_all(exp.Table):
        name = str(node.name or "").strip()
        if not name:
            continue
        if name not in tables:
            tables.append(name)
        alias = str(node.alias or "").strip()
        if alias:
            alias_to_table[alias.casefold()] = name
        alias_to_table.setdefault(name.casefold(), name)

    columns: dict[str, set[str]] = {name: set() for name in tables}
    for node in tree.find_all(exp.Column):
        col = str(node.name or "").strip()
        if not col or col == "*":
            continue
        qualifier = str(node.table or "").strip().casefold()
        owner = alias_to_table.get(qualifier) if qualifier else None
        targets = [owner] if owner else tables
        for table in targets:
            columns.setdefault(table, set()).add(col)
    return tables, columns


def build_recall_request(
    question: str,
    *,
    baseline_sql: str = "",
    prior_questions: Sequence[str] = (),
    prior_page_keys: Sequence[str] = (),
    prior_tables: Sequence[str] = (),
    dialect: str | None = None,
) -> RecallRequest:
    """Compose the recall request for a turn.

    ``baseline_sql`` / ``prior_*`` come from the referenced turn (memory slots).
    Empty → a plain single-turn request.
    """
    text = str(question or "").strip()
    tables, columns = sql_references(baseline_sql, dialect=dialect)
    pin_tables = list(dict.fromkeys([*tables, *(str(t) for t in prior_tables if t)]))
    pin_pages = [str(key) for key in prior_page_keys if str(key).strip()][
        :_MAX_PIN_PAGES
    ]
    if not pin_tables and not pin_pages:
        return RecallRequest.simple(text)

    priors = [str(q).strip() for q in prior_questions if str(q).strip()][
        -_MAX_PRIOR_QUESTIONS:
    ]
    retrieval = "\n".join([*priors, text]) if priors else text
    return RecallRequest(
        query=retrieval,
        question=text,
        pin_tables=tuple(pin_tables),
        pin_pages=tuple(pin_pages),
        required_fields={
            table: tuple(sorted(names)) for table, names in columns.items() if names
        },
    )
