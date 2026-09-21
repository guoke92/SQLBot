"""Compact datasource catalog map for the agent system prompt.

The schema outline is the datasource Repo Map: every visible table as one line
(name, comment, a few representative fields), cheap enough to stay resident.

Resolution priority (system-wide):
1. Bound corpus outline (DB wiki page ``catalog_summary``): inject the bound
   page body as-is. Never crop by AccessScope; never rebuild from CoreTable
   when a bound outline exists.
2. Dynamic catalog fallback (only if the bound wiki has no outline page):
   ``store.table_index`` then ``CoreTable``. Still no permission crop.
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

_OUTLINE_HINT = (
    "当前数据源全库表大纲。这是全局地图，不是已展开的字段定义。"
    "写 SQL 前用 get_table_schema 展开需要的表；跨表 JOIN 用 get_table_relations；"
    "业务口径/专有名词用 search_knowledge；实例值反查用 lookup_values；"
    "已知字段的残差码表用 get_dict_values。"
)


def render_schema_outline(
    *,
    ds: Any = None,
    access_scope: Any = None,  # noqa: ARG001 — runtime knowledge is bound wiki, not ACL
    store: Any = None,
    session: Session | None = None,
) -> str:
    """Render ``<schema_outline>`` or empty when the catalog cannot be listed.

    Bound ``catalog_summary`` is injected verbatim. AccessScope never crops
    knowledge. CoreTable assembly is a last-resort fallback when the bound
    wiki has no outline page.
    """
    db_summary = _fetch_catalog_summary_from_db(store=store, session=session, ds=ds)
    if db_summary:
        return f"<schema_outline>\n{_OUTLINE_HINT}\n{db_summary}\n</schema_outline>"

    rows = _rows_from_store(store)
    if not rows and session is not None:
        ds_id = int(getattr(ds, "id", 0) or 0)
        if ds_id > 0:
            rows = _rows_from_catalog(session, ds_id=ds_id)
    if not rows:
        return ""
    body = _format_rows(rows, with_fields=True)
    if len(body) > _OUTLINE_CHAR_BUDGET:
        body = _format_rows(rows, with_fields=False)
        if len(body) > _OUTLINE_CHAR_BUDGET:
            body = body[:_OUTLINE_CHAR_BUDGET].rstrip() + "\n…(截断)"
    return f"<schema_outline>\n{_OUTLINE_HINT}\n{body}\n</schema_outline>"


def _strip_frontmatter(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("---"):
        end = cleaned.find("\n---\n", 3)
        if end != -1:
            return cleaned[end + 5 :].strip()
    return cleaned


def _fetch_catalog_summary_from_db(
    *,
    store: Any = None,
    session: Session | None = None,
    ds: Any = None,
) -> str | None:
    """Read catalog_summary body strictly from DB (via bound store or query)."""
    # Prefer in-memory store already hydrated from DB wiki_page rows
    if store is not None:
        getter = getattr(store, "get_page", None)
        if callable(getter):
            page = getter("catalog_summary") or getter("concepts/catalog_summary")
            if page is not None and getattr(page, "body", None):
                return str(page.body).strip()

    # Query DB directly via datasource binding
    ds_id = int(getattr(ds, "id", 0) or 0)
    if session is not None and ds_id > 0:
        try:
            from apps.knowledge.db_models import WikiCorpusBinding, WikiPageRow

            stmt = (
                select(WikiPageRow.body_md)
                .join(
                    WikiCorpusBinding,
                    WikiCorpusBinding.corpus_id == WikiPageRow.corpus_id,
                )
                .where(
                    WikiCorpusBinding.datasource_id == ds_id,
                    WikiCorpusBinding.enabled == True,  # noqa: E712
                    WikiPageRow.page_key == "catalog_summary",
                    WikiPageRow.page_disabled == False,  # noqa: E712
                )
            )
            raw = session.exec(stmt).first()
            if raw:
                return _strip_frontmatter(str(raw))
        except Exception as exc:
            from common.utils.utils import SQLBotLogUtil

            SQLBotLogUtil.warning("Failed to query catalog_summary from DB: %s", exc)
    return None


def _rows_from_store(store: Any) -> list[tuple[str, str, list[str]]]:
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
        comment = str(getattr(page, "title", "") or "").strip() or name
        fields = _rep_fields_from_page(page)
        rows.append((name, comment, fields))
    rows.sort(key=lambda item: item[0])
    return rows


def _rows_from_catalog(
    session: Session, *, ds_id: int
) -> list[tuple[str, str, list[str]]]:
    tables = list(
        session.exec(
            select(CoreTable)
            .where(CoreTable.ds_id == ds_id)
            .order_by(CoreTable.table_name.asc())
        ).all()
    )
    checked = [table for table in tables if bool(getattr(table, "checked", True))]
    tables = checked if checked else tables
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
