"""Single schema renderer — wiki table pages with live-catalog fallback."""

from __future__ import annotations

import re
from typing import Any

from apps.chat.steps.wiki_schema import WikiSchemaRenderer, filter_schema_relations

_RELATION_LINE_RE = re.compile(
    r"关联:\s*([A-Za-z_][\w.]*)\.[A-Za-z_]\w*\s*→\s*([A-Za-z_][\w.]*)\."
)


def render_schema(
    tables: list[str],
    *,
    store: Any = None,
    live_tables: dict[str, Any] | None = None,
    peer_catalog: list[str] | None = None,
    confirmed_relations: list[str] | None = None,
    project_relations: bool = True,
) -> str:
    """Render physical tables (full fields) in the wiki ``## 注释 (phys)`` format.

    ``project_relations=True`` (NLQ 单次 working set) 按当前 ``tables`` 投影关联。
    Agent 增量召回传 ``False``，把完整紧凑边交给 plane，由累计表集再投影。
    字段级压缩不在此处——``wiki_schema.project_schema`` 是唯一实现，由
    消费面（plane / 预算裁表）在需要时调用。

    ``peer_catalog`` is the full datasource table-name set used to resolve
    naming-convention FKs whose peer is outside the current working set.
    """
    if not tables:
        return ""
    if store is not None:
        renderer = WikiSchemaRenderer.from_store(
            store, live_tables=live_tables, peer_catalog=peer_catalog
        )
        if renderer is None:
            renderer = WikiSchemaRenderer(
                store,
                live_tables=live_tables or {},
                peer_catalog=peer_catalog,
            )
    else:
        renderer = WikiSchemaRenderer(
            None, live_tables=live_tables or {}, peer_catalog=peer_catalog
        )
    text = str(renderer.render(list(tables)) or "")
    if confirmed_relations:
        text = _attach_relation_lines(text, list(tables), confirmed_relations)
    if project_relations:
        text = filter_schema_relations(text, peer_tables=tables)
    return text.strip()


def split_rendered_tables(schema_text: str, tables: list[str]) -> dict[str, str]:
    from apps.chat.agent_knowledge import split_schema_text

    return split_schema_text(schema_text, tables=tables)


def _attach_relation_lines(
    schema_text: str, tables: list[str], lines: list[str]
) -> str:
    from apps.chat.agent_knowledge import split_schema_text

    by_table = split_schema_text(schema_text, tables=tables)
    if not by_table:
        extra = "\n".join(line for line in lines if line.strip())
        return f"{schema_text}\n{extra}".strip()
    for raw in lines:
        line = str(raw).strip()
        if not line:
            continue
        match = _RELATION_LINE_RE.match(line)
        target = ""
        if match:
            left = match.group(1).partition(".")[0]
            if left in by_table:
                target = left
        if not target:
            target = next(iter(by_table))
        body = by_table[target]
        if line not in body:
            by_table[target] = f"{body}\n{line}"
    ordered = [by_table[name] for name in tables if name in by_table]
    leftover = [
        body
        for name, body in by_table.items()
        if name not in tables and not str(name).startswith("_")
    ]
    return "\n".join([*ordered, *leftover]).strip()
