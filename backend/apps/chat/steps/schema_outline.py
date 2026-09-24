"""Compact datasource catalog map for the agent system prompt.

The schema outline is the datasource Repo Map: every visible table as one line
(table comment + catalog positioning + a few representative fields).

Resolution:
1. Bound ``catalog_summary`` is parsed as *supplementary* blurbs and merged
   with CoreTable / wiki table comments. Comments are never dropped.
2. Dynamic catalog fallback (no outline page): ``store.table_index`` then
   ``CoreTable``. AccessScope never crops the map.
"""

from __future__ import annotations

import re
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

_CATALOG_LINE_RE = re.compile(r"^-\s+([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.+?)\s*$")

_OUTLINE_HINT = (
    "当前数据源全库表大纲。这是全局地图，不是已展开的字段定义。"
    "每行是「表注释」；分号后是 catalog 补充定位（与注释不一致时两者都保留）。"
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

    Table comments and catalog positioning are both first-class: merge them,
    never inject catalog_summary verbatim in place of comments.
    """
    catalog_text = _fetch_catalog_summary_from_db(store=store, session=session, ds=ds)
    blurbs = parse_catalog_table_lines(catalog_text or "")

    rows = _rows_from_store(store)
    if session is not None:
        ds_id = int(getattr(ds, "id", 0) or 0)
        if ds_id > 0:
            catalog_rows = _rows_from_catalog(session, ds_id=ds_id)
            rows = _prefer_catalog_comments(rows, catalog_rows)

    merged = merge_outline_rows(rows, blurbs)
    if not merged:
        return ""
    apply_budget = not blurbs
    body = _format_rows(merged, with_fields=True)
    if apply_budget and len(body) > _OUTLINE_CHAR_BUDGET:
        body = _format_rows(merged, with_fields=False)
        if len(body) > _OUTLINE_CHAR_BUDGET:
            body = body[:_OUTLINE_CHAR_BUDGET].rstrip() + "\n…(截断)"
    return f"<schema_outline>\n{_OUTLINE_HINT}\n{body}\n</schema_outline>"


def parse_catalog_table_lines(text: str) -> dict[str, str]:
    """Map physical table name → catalog positioning blurb (rest of the line)."""
    blurbs: dict[str, str] = {}
    for raw in (text or "").splitlines():
        match = _CATALOG_LINE_RE.match(raw.strip())
        if not match:
            continue
        name, blurb = match.group(1), match.group(2).strip()
        if name and blurb:
            blurbs[name] = blurb
    return blurbs


def merge_comment_and_blurb(comment: str, blurb: str) -> str:
    """Keep both official comment and catalog positioning when they differ."""
    title = str(comment or "").strip()
    extra = str(blurb or "").strip()
    if not title:
        return extra
    if not extra:
        return title
    if title == extra:
        return title
    if extra.startswith(title) or title in extra:
        return extra
    if extra in title:
        return title
    return f"{title}; {extra}"


def merge_outline_rows(
    rows: Sequence[tuple[str, str, list[str]]],
    blurbs: dict[str, str],
) -> list[tuple[str, str, list[str]]]:
    """Comment-first rows, plus catalog-only tables, each with merged title."""
    by_name: dict[str, tuple[str, str, list[str]]] = {}
    for name, comment, fields in rows:
        key = str(name or "").strip()
        if not key:
            continue
        title = merge_comment_and_blurb(comment, blurbs.get(key, ""))
        by_name[key] = (key, title or key, list(fields or []))
    for name, blurb in blurbs.items():
        if name in by_name:
            continue
        by_name[name] = (name, blurb or name, [])
    return [by_name[key] for key in sorted(by_name)]


def _prefer_catalog_comments(
    wiki_rows: Sequence[tuple[str, str, list[str]]],
    catalog_rows: Sequence[tuple[str, str, list[str]]],
) -> list[tuple[str, str, list[str]]]:
    """CoreTable comments win; wiki fields fill in when CoreTable has none."""
    wiki = {name: (name, comment, fields) for name, comment, fields in wiki_rows}
    merged: dict[str, tuple[str, str, list[str]]] = dict(wiki)
    for name, comment, fields in catalog_rows:
        prior = merged.get(name)
        if prior is None:
            merged[name] = (name, comment, fields)
            continue
        _pname, prior_comment, prior_fields = prior
        use_comment = comment if comment and comment != name else prior_comment
        use_fields = fields or prior_fields
        merged[name] = (name, use_comment, use_fields)
    return [merged[key] for key in sorted(merged)]


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
    """Read catalog_summary body from bound store or DB."""
    if store is not None:
        getter = getattr(store, "get_page", None)
        if callable(getter):
            page = getter("catalog_summary") or getter("concepts/catalog_summary")
            if page is not None and getattr(page, "body", None):
                return _strip_frontmatter(str(page.body).strip())

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
