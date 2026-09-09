"""Anchor closure — page metadata → physical tables（方案 v1 §2 锚点闭包）.

被召回语义页引用的物理表必须进规划上下文：从 frontmatter 契约字段
（anchors / field_targets / maps_to）抽取表名，只返回 store 中真实存在的
表页。图扩展负责"发现"（把相关语义页带进召回窗口），本模块负责"落地"
（引用即可见）——纯确定性代码，零 LLM。

不做 ground 块正则重解析：anchors/field_targets/maps_to 是契约字段，
parse_page 已解析归一，这里只消费元数据。
"""

from __future__ import annotations

import re
from typing import Any

# maps_to 形如 "cust_person_info.source = 'AMS'"；取表段
_PHYSICAL_KEY_RE = re.compile(r"\b[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*\b")
# 闭包上限由 RecallBudget.max_tables 决定；此处仅作无 budget 调用的兜底
DEFAULT_CLOSURE_MAX = 4


def _table_of(physical_key: str) -> str:
    return physical_key.partition(".")[0].strip()


def _resolve_page(store: Any, key: str) -> Any | None:
    pages = getattr(store, "pages", {}) or {}
    if key in pages:
        return pages[key]
    getter = getattr(store, "get_page", None)
    if callable(getter):
        return getter(key)
    return None


def _has_table(store: Any, table: str, pages: dict[str, Any]) -> bool:
    checker = getattr(store, "has_table", None)
    if callable(checker):
        return bool(checker(table))
    page = pages.get(table) or pages.get(f"tables/{table}")
    if page is None:
        return False
    actual = getattr(page, "type", None)
    return actual in ("table", None, "")


def anchor_tables(store: Any, page_keys: list[str]) -> list[str]:
    """召回命中页 → 引用的物理表名（去重保序，仅保留 store 中的表页）。"""
    if store is None or not page_keys:
        return []
    pages = getattr(store, "pages", {}) or {}
    tables: list[str] = []
    for key in page_keys:
        page = _resolve_page(store, key)
        if page is None:
            continue
        candidates: list[str] = []
        for anchor in getattr(page, "anchors", ()) or ():
            candidates.append(_table_of(str(anchor)))
        for target in getattr(page, "field_targets", ()) or ():
            candidates.append(_table_of(str(target)))
        maps_to = str(getattr(page, "maps_to", "") or "")
        if maps_to:
            candidates.extend(
                match.group(0).partition(".")[0]
                for match in _PHYSICAL_KEY_RE.finditer(maps_to)
            )
        for table in candidates:
            if table and _has_table(store, table, pages) and table not in tables:
                tables.append(table)
    return tables


def closure_tables(
    store: Any, page_keys: list[str], *, max_tables: int | None = None
) -> tuple[list[str], int]:
    """闭包表 + 截断数（超出上限丢弃的数量，供 anchor_closure_truncated 遥测）。"""
    tables = anchor_tables(store, page_keys)
    cap = DEFAULT_CLOSURE_MAX if max_tables is None else max(1, int(max_tables))
    if len(tables) <= cap:
        return tables, 0
    return tables[:cap], len(tables) - cap


def anchor_tables_missing(store: Any, page_keys: list[str]) -> list[str]:
    """引用了但无表页的表名（SCHEMA_PAGE_MISSING 同族——增量提取信号）。"""
    if store is None or not page_keys:
        return []
    pages = getattr(store, "pages", {}) or {}
    missing: list[str] = []
    for key in page_keys:
        page = _resolve_page(store, key)
        if page is None:
            continue
        for anchor in getattr(page, "anchors", ()) or ():
            table = _table_of(str(anchor))
            if table and not _has_table(store, table, pages) and table not in missing:
                missing.append(table)
    return missing


def anchor_table_attribution(
    store: Any, page_keys: list[str]
) -> dict[str, list[dict[str, str]]]:
    """闭包表 ← 来源归因：每张表由哪个命中页的哪个契约字段拉入。

    执行详情"召回过程"卡片用——表选择可解释（chat 169：用户想知道
    tenant_setting_config 这类表是怎么进来的）。字段三种：anchors /
    field_targets / maps_to。"""
    if store is None or not page_keys:
        return {}
    pages = getattr(store, "pages", {}) or {}
    attribution: dict[str, list[dict[str, str]]] = {}
    for key in page_keys:
        page = _resolve_page(store, key)
        if page is None:
            continue
        candidates: list[tuple[str, str]] = []
        for anchor in getattr(page, "anchors", ()) or ():
            candidates.append((_table_of(str(anchor)), "anchors"))
        for target in getattr(page, "field_targets", ()) or ():
            candidates.append((_table_of(str(target)), "field_targets"))
        maps_to = str(getattr(page, "maps_to", "") or "")
        if maps_to:
            candidates.extend(
                (match.group(0).partition(".")[0], "maps_to")
                for match in _PHYSICAL_KEY_RE.finditer(maps_to)
            )
        for block in getattr(page, "ground_blocks", ()) or ():
            kind = str(getattr(block, "kind", "") or "")
            data = getattr(block, "data", {}) or {}
            if not isinstance(data, dict):
                continue
            if kind == "enum":
                for item in data.get("fields") or []:
                    candidates.append((_table_of(str(item)), "field_targets"))
            elif kind == "table":
                name = str(data.get("table") or getattr(page, "page_key", "") or "")
                if name:
                    candidates.append((name, "anchors"))
        for table, field in candidates:
            if not table or not _has_table(store, table, pages):
                continue
            entry = {"page_key": str(key), "field": field}
            existing = attribution.setdefault(table, [])
            if not any(
                e["page_key"] == entry["page_key"] and e["field"] == entry["field"]
                for e in existing
            ):
                existing.append(entry)
    return attribution
