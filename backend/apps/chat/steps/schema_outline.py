"""Compact datasource catalog map for the agent system prompt.

Aider/Cursor keep a repo map in context so the model can choose files
itself. The schema outline is the same idea for a datasource: every visible
table as one line (name, comment, a few representative fields), cheap enough
to stay resident (~800 tokens for a typical 20–80 table catalog).
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from sqlmodel import Session, select

from apps.datasource.models.datasource import CoreField, CoreTable

_OUTLINE_FIELD_MAX = 8
_OUTLINE_CHAR_BUDGET = 4500
_SKIP_FIELD_NAMES = frozenset(
    {
        "id",
        "enable",
        "is_deleted",
        "deleted",
        "create_time",
        "created_at",
        "update_time",
        "updated_at",
        "create_by",
        "update_by",
        "created_by",
        "updated_by",
    }
)


def render_schema_outline(
    *,
    ds: Any = None,
    access_scope: Any = None,
    store: Any = None,
    session: Session | None = None,
) -> str:
    """Render ``<schema_outline>`` or empty when the catalog cannot be listed."""
    allowed = _allowed_names(access_scope)
    rows = _rows_from_store(store, allowed=allowed)
    if not rows and session is not None:
        ds_id = int(getattr(ds, "id", 0) or 0)
        if ds_id > 0:
            rows = _rows_from_catalog(session, ds_id=ds_id, allowed=allowed)
    if not rows:
        return ""
    body = _format_rows(rows, with_fields=True)
    if len(body) > _OUTLINE_CHAR_BUDGET:
        body = _format_rows(rows, with_fields=False)
        if len(body) > _OUTLINE_CHAR_BUDGET:
            body = body[:_OUTLINE_CHAR_BUDGET].rstrip() + "\n…(截断)"
    return (
        "<schema_outline>\n"
        f"当前数据源全库表大纲（{len(rows)} 张表）。这是全局地图，不是已展开的字段定义。"
        "写 SQL 前用 get_table_schema 展开需要的表；跨表 JOIN 用 get_table_relations；"
        "业务口径/专有名词用 search_knowledge；字段枚举用 get_dict_values。\n"
        f"{body}\n"
        "</schema_outline>"
    )


def _allowed_names(access_scope: Any) -> frozenset[str] | None:
    if access_scope is None:
        return None
    names = getattr(access_scope, "resource_names", None)
    if names is None:
        return None
    return frozenset(str(name) for name in names if str(name).strip())


def _rows_from_store(
    store: Any, *, allowed: frozenset[str] | None
) -> list[tuple[str, str, list[str]]]:
    index = getattr(store, "table_index", None) or {}
    get_page = getattr(store, "get_page", None)
    if not index or not callable(get_page):
        return []
    rows: list[tuple[str, str, list[str]]] = []
    for page_key, store_key in index.items():
        page = get_page(store_key) or get_page(page_key)
        name = _table_name(page, page_key)
        if not name:
            continue
        if allowed is not None and name not in allowed:
            continue
        comment = str(getattr(page, "title", "") or "").strip() or name
        fields = _rep_fields_from_page(page)
        rows.append((name, comment, fields))
    rows.sort(key=lambda item: item[0])
    return rows


def _rows_from_catalog(
    session: Session, *, ds_id: int, allowed: frozenset[str] | None
) -> list[tuple[str, str, list[str]]]:
    tables = list(
        session.exec(
            select(CoreTable)
            .where(
                CoreTable.ds_id == ds_id,
                CoreTable.checked == True,  # noqa: E712
            )
            .order_by(CoreTable.table_name.asc())
        ).all()
    )
    if allowed is not None:
        tables = [table for table in tables if table.table_name in allowed]
    if not tables:
        return []
    fields = list(
        session.exec(
            select(CoreField).where(
                CoreField.ds_id == ds_id,
                CoreField.checked == True,  # noqa: E712
                CoreField.table_id.in_([int(table.id) for table in tables if table.id]),
            )
        ).all()
    )
    by_table: dict[int, list[CoreField]] = {}
    for field in fields:
        by_table.setdefault(int(field.table_id), []).append(field)
    rows: list[tuple[str, str, list[str]]] = []
    for table in tables:
        name = str(table.table_name or "").strip()
        if not name:
            continue
        comment = str(table.custom_comment or table.table_comment or "").strip() or name
        ordered = sorted(
            by_table.get(int(table.id or 0), []),
            key=lambda item: int(item.field_index or 0),
        )
        labels: list[str] = []
        for field in ordered:
            field_name = str(field.field_name or "").strip()
            if not field_name or field_name.casefold() in _SKIP_FIELD_NAMES:
                continue
            label = str(field.custom_comment or field.field_comment or "").strip()
            labels.append(label or field_name)
            if len(labels) >= _OUTLINE_FIELD_MAX:
                break
        rows.append((name, comment, labels))
    return rows


def _table_name(page: Any, fallback: str) -> str:
    if page is not None:
        for block in getattr(page, "ground_blocks", ()) or ():
            if getattr(block, "kind", "") == "table":
                name = str(
                    (getattr(block, "data", {}) or {}).get("table") or ""
                ).strip()
                if name:
                    return name
        key = str(getattr(page, "page_key", "") or "")
        if key:
            return key.rsplit("/", 1)[-1]
    return str(fallback or "").rsplit("/", 1)[-1]


def _rep_fields_from_page(page: Any) -> list[str]:
    labels: list[str] = []
    for block in getattr(page, "ground_blocks", ()) or ():
        if getattr(block, "kind", "") != "table":
            continue
        for entry in (getattr(block, "data", {}) or {}).get("fields") or []:
            if not isinstance(entry, dict):
                continue
            name = str(entry.get("name") or "").strip()
            if not name or name.casefold() in _SKIP_FIELD_NAMES:
                continue
            label = str(entry.get("desc") or entry.get("comment") or "").strip()
            labels.append(label or name)
            if len(labels) >= _OUTLINE_FIELD_MAX:
                return labels
    return labels


def _format_rows(
    rows: Sequence[tuple[str, str, list[str]]], *, with_fields: bool
) -> str:
    lines: list[str] = []
    for name, comment, fields in rows:
        title = comment if comment and comment != name else ""
        head = f"- {name}: {title}" if title else f"- {name}"
        if with_fields and fields:
            head = f"{head} ({', '.join(fields)})"
        lines.append(head.rstrip())
    return "\n".join(lines)
