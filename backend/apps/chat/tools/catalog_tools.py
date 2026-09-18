"""Orthogonal catalog tools: schema, relations, knowledge, dictionary values.

Each tool has one job. The model chooses what to open; these functions do not
rank tables, hop the FK graph, or inject peripheral wiki pages.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

from apps.chat.agent_knowledge import (
    KNOWLEDGE_ROUND_LIMIT,
    KNOWLEDGE_SEARCH_LIMIT,
    AgentKnowledgePlane,
    MergeDelta,
)
from apps.chat.steps.wiki_schema import RELATION_PEER_MISSING, schema_fields_by_table
from apps.chat.tools.base import failure_result, success_result
from apps.conversation.runtime_context import (
    attach_runtime,
    current_worker_identity,
    peek_runtime,
)
from apps.conversation.tooling import ToolResult
from common.utils.utils import SQLBotLogUtil

MAX_TABLES_PER_CALL = 3
KNOWLEDGE_PAGE_TYPES = frozenset({"concept", "caliber", "metric"})
KNOWLEDGE_TOP_K = 6
_RELATION_LINE_RE = re.compile(
    r"^关联:\s*"
    r"(?P<left_table>[A-Za-z_][\w]*)\.(?P<left_col>[A-Za-z_]\w*)"
    r"\s*→\s*"
    r"(?P<right_table>[A-Za-z_][\w]*)\.(?P<right_col>[A-Za-z_]\w*)"
    r"(?:\s*\((?P<peer>[^)]+)\))?"
    r"(?:\s*\[(?P<tag>[^\]]+)\])?"
)


def _store_page(store: Any, slug: str, *, belong: str | None = None) -> Any | None:
    if store is None:
        return None
    getter = getattr(store, "get_page", None)
    if not callable(getter):
        return None
    if belong:
        page = getter(f"{belong}/{slug}")
        if page is not None:
            return page
    return getter(slug)


def load_plane() -> AgentKnowledgePlane:
    run_id, _token = current_worker_identity()
    if not run_id:
        return AgentKnowledgePlane()
    snap = peek_runtime(run_id) or {}
    return AgentKnowledgePlane.from_dump(snap.get("knowledge_plane"))


def save_plane(plane: AgentKnowledgePlane) -> None:
    run_id, _token = current_worker_identity()
    if not run_id:
        return
    attach_runtime(run_id, knowledge_plane=plane.to_dump())


def knowledge_budget_result(plane: AgentKnowledgePlane) -> ToolResult | None:
    if int(plane.knowledge_rounds or 0) < KNOWLEDGE_ROUND_LIMIT:
        return None
    return failure_result(
        (
            f"信息收集已达 {KNOWLEDGE_ROUND_LIMIT} 轮上限。"
            "请基于当前 schema_catalog / wiki_knowledge 编写 SQL，"
            "或 request_clarification / complete_without_sql。"
            "不要再调用 get_table_schema / get_table_relations / "
            "search_knowledge / get_dict_values。"
        ),
        retryable=False,
    )


def strip_relation_lines(schema_text: str) -> str:
    """Drop compact JOIN rows so get_table_schema stays field-only."""
    lines = [
        line
        for line in str(schema_text or "").splitlines()
        if not line.startswith("关联:") and RELATION_PEER_MISSING not in line
    ]
    return "\n".join(lines).strip()


def parse_relation_edges(schema_text: str) -> list[dict[str, str]]:
    edges: list[dict[str, str]] = []
    seen: set[tuple[str, str, str, str]] = set()
    for raw in str(schema_text or "").splitlines():
        match = _RELATION_LINE_RE.match(raw.strip())
        if not match:
            continue
        left = str(match.group("left_table") or "")
        left_col = str(match.group("left_col") or "")
        right = str(match.group("right_table") or "")
        right_col = str(match.group("right_col") or "")
        key = (left, left_col, right, right_col)
        if not left or not right or key in seen:
            continue
        seen.add(key)
        tag = str(match.group("tag") or "")
        edges.append(
            {
                "left_table": left,
                "left_col": left_col,
                "right_table": right,
                "right_col": right_col,
                "tag": tag,
                "line": raw.strip().replace(RELATION_PEER_MISSING, "").strip(),
            }
        )
    return edges


def render_tables_schema(
    tables: Sequence[str],
    *,
    store: Any,
    live_tables: Mapping[str, Any] | None = None,
) -> str:
    from apps.knowledge.recall_kernel.render import render_schema

    names = [str(name).strip() for name in tables if str(name).strip()]
    if not names:
        return ""
    text = render_schema(
        names,
        store=store,
        live_tables=dict(live_tables or {}),
        project_relations=False,
    )
    return strip_relation_lines(text)


def classify_relations(
    requested: Sequence[str],
    edges: Sequence[Mapping[str, str]],
) -> dict[str, list[dict[str, str]]]:
    wanted = {str(name).strip() for name in requested if str(name).strip()}
    direct: list[dict[str, str]] = []
    adjacent: list[dict[str, str]] = []
    neighbors: dict[str, set[str]] = {name: set() for name in wanted}
    for edge in edges:
        left = str(edge.get("left_table") or "")
        right = str(edge.get("right_table") or "")
        if left in wanted and right in wanted:
            direct.append(dict(edge))
            continue
        if left in wanted or right in wanted:
            adjacent.append(dict(edge))
            if left in wanted:
                neighbors.setdefault(left, set()).add(right)
            if right in wanted:
                neighbors.setdefault(right, set()).add(left)
    bridges: list[dict[str, Any]] = []
    names = list(wanted)
    if not direct and len(names) >= 2:
        seen_bridge: set[str] = set()
        for i, left in enumerate(names):
            for right in names[i + 1 :]:
                common = neighbors.get(left, set()) & neighbors.get(right, set())
                for peer in sorted(common):
                    if peer in seen_bridge:
                        continue
                    seen_bridge.add(peer)
                    bridges.append(
                        {
                            "via": peer,
                            "between": [left, right],
                            "note": f"{left} 与 {right} 可通过 {peer} 连接；需要时再 get_table_schema 展开该桥接表",
                        }
                    )
    return {"direct": direct, "bridges": bridges, "adjacent": adjacent[:8]}


def filter_knowledge_passages(
    passages: Sequence[Any],
    store: Any,
    *,
    limit: int = KNOWLEDGE_TOP_K,
) -> list[Any]:
    kept: list[Any] = []
    for passage in passages:
        store_key = str(
            getattr(passage, "store_key", "") or getattr(passage, "page_key", "")
        )
        page = None
        getter = getattr(store, "get_page", None)
        if callable(getter):
            page = getter(store_key) or getter(getattr(passage, "page_key", ""))
        page_type = str(getattr(page, "type", "") or "")
        belong = str(
            getattr(passage, "belong", "") or getattr(page, "belong", "") or ""
        )
        if page_type not in KNOWLEDGE_PAGE_TYPES and belong not in {
            "concepts",
            "calibers",
            "metrics",
        }:
            continue
        kept.append(passage)
        if len(kept) >= limit:
            break
    return kept


def dict_values_from_page(page: Any) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for anchor in getattr(page, "ground_blocks", ()) or ():
        if getattr(anchor, "kind", "") != "dict":
            continue
        values = (getattr(anchor, "data", {}) or {}).get("values") or {}
        if not isinstance(values, Mapping):
            continue
        for value, meta in values.items():
            label = ""
            if isinstance(meta, Mapping):
                label = str(meta.get("label") or "")
            elif meta is not None:
                label = str(meta)
            rows.append({"value": str(value), "label": label})
        break
    return rows


def resolve_dict_key(
    *,
    store: Any,
    plane: AgentKnowledgePlane,
    dict_name: str = "",
    table: str = "",
    field: str = "",
) -> str:
    named = str(dict_name or "").strip()
    if named:
        return named.rsplit("/", 1)[-1]
    table_name = str(table or "").strip()
    field_name = str(field or "").strip()
    if not table_name or not field_name:
        return ""
    body = plane.schema_by_table.get(table_name) or ""
    if body:
        for item in schema_fields_by_table(body).get(table_name) or []:
            if item.name == field_name and item.enum:
                return str(item.enum)
    page = _store_page(store, table_name, belong="tables")
    if page is None:
        return ""
    for block in getattr(page, "ground_blocks", ()) or ():
        if getattr(block, "kind", "") != "table":
            continue
        for entry in (getattr(block, "data", {}) or {}).get("fields") or []:
            if not isinstance(entry, Mapping):
                continue
            if str(entry.get("name") or "") == field_name:
                return str(entry.get("dict") or "").strip()
    return ""


def _fence_tables(
    tables: Sequence[str], access_scope: Any
) -> tuple[list[str], list[str]]:
    names = list(
        dict.fromkeys(str(name).strip() for name in tables if str(name).strip())
    )
    if access_scope is None:
        return names, []
    allowed = set(getattr(access_scope, "resource_names", ()) or ())
    if not allowed:
        return names, []
    visible = [name for name in names if name in allowed]
    blocked = [name for name in names if name not in allowed]
    return visible, blocked


def _catalog_sources(llm_service: Any) -> tuple[Any, dict[str, Any], list[str]]:
    from apps.chat.graphs.nodes.nlq.topup import _live_tables_projection
    from apps.chat.steps.wiki_recall import _store, datasource_databases

    ds = getattr(llm_service, "ds", None)
    ds_id = getattr(ds, "id", None)
    store = _store(int(ds_id)) if ds_id is not None else None
    live = _live_tables_projection(llm_service) if ds is not None else {}
    databases = datasource_databases(ds) if ds is not None else []
    return store, live, databases


def get_table_schema(
    llm_service: Any,
    tables: Sequence[str],
    *,
    access_scope: Any = None,
) -> ToolResult:
    """Expand full field definitions for at most three named tables."""
    plane = load_plane()
    blocked_budget = knowledge_budget_result(plane)
    if blocked_budget is not None:
        return blocked_budget
    requested, fenced = _fence_tables(tables, access_scope)
    if len(requested) > MAX_TABLES_PER_CALL:
        requested = requested[:MAX_TABLES_PER_CALL]
        truncated = True
    else:
        truncated = False
    if not requested:
        return failure_result("get_table_schema 需要至少一张可见表名", retryable=True)

    already = [name for name in requested if name in plane.tables]
    needed = [name for name in requested if name not in plane.tables]
    store, live, _databases = _catalog_sources(llm_service)
    schema_text = ""
    missing: list[str] = []
    if needed:
        schema_text = render_tables_schema(needed, store=store, live_tables=live)
        if schema_text:
            delta = plane.merge_recall(
                {
                    "query": " ".join(needed),
                    "schema_text": schema_text,
                    "tables": needed,
                    "backend": "catalog",
                }
            )
        else:
            delta = MergeDelta(unchanged=True, schema_ready=plane.schema_ready)
            missing = list(needed)
        present = set(schema_fields_by_table(schema_text))
        missing = [name for name in needed if name not in present]
    else:
        delta = MergeDelta(unchanged=True, schema_ready=plane.schema_ready)

    catalog = plane.schema_catalog_text()
    chat_q = getattr(llm_service, "chat_question", None)
    if chat_q is not None and catalog:
        chat_q.db_schema = catalog
    save_plane(plane)

    shown = strip_relation_lines(
        "\n".join(
            plane.schema_by_table[name]
            for name in requested
            if plane.schema_by_table.get(name)
        )
    )
    notes: list[str] = []
    if truncated:
        notes.append(
            f"单次最多展开 {MAX_TABLES_PER_CALL} 张表，已截取前 {MAX_TABLES_PER_CALL} 张。"
        )
    if already:
        notes.append(f"已在 schema_catalog 中、未重复拉取：{already}。")
    if missing:
        notes.append(f"未找到表：{missing}。请对照 schema_outline 中的物理表名。")
    if fenced:
        notes.append(f"无权限的表已忽略：{fenced}。")
    if not shown and not missing:
        notes.append("这些表已在系统提示的 schema_catalog 中，不要重复调用。")
    summary = (
        f"已展开表 {delta.added_tables or already}。"
        + (" " + " ".join(notes) if notes else "")
        + " 全文已写入系统提示 schema_catalog；不要再为同一张表调用本工具。"
    )
    return success_result(
        summary.strip(),
        data={
            "tables": [name for name in requested if name in plane.tables],
            "added_tables": list(delta.added_tables),
            "already": already,
            "missing": missing,
            "schema_text": shown,
            "schema_ready": plane.schema_ready,
        },
    )


def get_table_relations(
    llm_service: Any,
    tables: Sequence[str],
    *,
    access_scope: Any = None,
) -> ToolResult:
    """Return known JOIN edges among the named tables. No field definitions."""
    plane = load_plane()
    blocked_budget = knowledge_budget_result(plane)
    if blocked_budget is not None:
        return blocked_budget
    requested, fenced = _fence_tables(tables, access_scope)
    if len(requested) < 2:
        return failure_result(
            "get_table_relations 仅用于跨表 JOIN：请传入至少两张表。"
            "单表查询不要调用本工具。",
            retryable=True,
        )
    store, live, _databases = _catalog_sources(llm_service)
    from apps.knowledge.recall_kernel.render import render_schema

    raw = render_schema(
        requested,
        store=store,
        live_tables=live,
        project_relations=False,
    )
    grouped = classify_relations(requested, parse_relation_edges(raw))
    save_plane(plane)
    direct_lines = [item["line"] for item in grouped["direct"] if item.get("line")]
    bridge_notes = [str(item.get("note") or "") for item in grouped["bridges"]]
    if direct_lines:
        summary = "已知直接关联：\n" + "\n".join(direct_lines)
    elif bridge_notes:
        summary = "无直接外键，候选桥接：\n" + "\n".join(bridge_notes)
    else:
        summary = (
            f"未找到 {requested} 之间的已知关联边。"
            "不要为此再扩大检索；若业务上不应 JOIN，按单表或澄清处理。"
        )
    if fenced:
        summary += f" 无权限的表已忽略：{fenced}。"
    return success_result(
        summary,
        data={
            "tables": requested,
            "direct": grouped["direct"],
            "bridges": grouped["bridges"],
            "adjacent": grouped["adjacent"],
        },
    )


def search_knowledge(
    llm_service: Any,
    query: str,
    *,
    access_scope: Any = None,  # noqa: ARG001 — fenced by corpus binding / databases
) -> ToolResult:
    """Retrieve concept/caliber/metric prose. Never selects tables or rules."""
    plane = load_plane()
    blocked_budget = knowledge_budget_result(plane)
    if blocked_budget is not None:
        return blocked_budget
    if int(plane.knowledge_searches or 0) >= KNOWLEDGE_SEARCH_LIMIT:
        return failure_result(
            (
                "search_knowledge 本对话限 1 次，禁止换近义词再搜。"
                "请基于已返回的口径写 SQL，或 request_clarification。"
            ),
            retryable=False,
        )
    clean = str(query or "").strip()
    if not clean:
        return failure_result("search_knowledge 需要非空 query", retryable=True)

    store, _live, databases = _catalog_sources(llm_service)
    if store is None:
        return failure_result(
            "当前数据源没有绑定 Wiki 知识库，无法检索业务口径。请对照 schema_outline 与已展开表结构写 SQL。",
            retryable=False,
        )
    from apps.knowledge.wiki.recall import recall

    try:
        passages = recall(
            clean, store, databases=databases, top_k=KNOWLEDGE_TOP_K, mode="business"
        )
    except Exception as exc:
        SQLBotLogUtil.warning("search_knowledge recall failed: %s", exc)
        return failure_result(f"知识检索失败：{exc}", retryable=True)

    kept = filter_knowledge_passages(passages, store)
    wiki_passages = {
        str(item.store_key or item.page_key): str(item.text or "").strip()
        for item in kept
        if str(item.text or "").strip()
    }
    page_keys = list(wiki_passages)
    plane.knowledge_searches = int(plane.knowledge_searches or 0) + 1
    if wiki_passages:
        plane.merge_recall(
            {
                "query": clean,
                "page_keys": page_keys,
                "wiki_passages": wiki_passages,
                "backend": "wiki",
            }
        )
    save_plane(plane)
    if not wiki_passages:
        return success_result(
            (
                "未命中业务口径/概念页。字段含义若已在表注释中写明，直接写 SQL；"
                "名实仍冲突则 request_clarification，不要换近义词再搜。"
            ),
            data={"page_keys": [], "passages": {}, "hit_count": 0},
        )
    body = "\n\n".join(wiki_passages[key] for key in page_keys)
    return success_result(
        (
            f"已命中 {len(page_keys)} 条业务知识（概念/口径/指标）。"
            "全文已写入系统提示 wiki_knowledge；不要再 search_knowledge。"
            "表结构请用 get_table_schema，不要假设本工具带回了 DDL。"
        ),
        data={
            "page_keys": page_keys,
            "passages": wiki_passages,
            "hit_count": len(page_keys),
            "text": body,
        },
    )


def get_dict_values(
    llm_service: Any,
    *,
    dict_name: str = "",
    table: str = "",
    field: str = "",
    access_scope: Any = None,  # noqa: ARG001
) -> ToolResult:
    """Look up one dictionary's value→label map. No other wiki pages."""
    plane = load_plane()
    blocked_budget = knowledge_budget_result(plane)
    if blocked_budget is not None:
        return blocked_budget
    store, _live, _databases = _catalog_sources(llm_service)
    key = resolve_dict_key(
        store=store,
        plane=plane,
        dict_name=dict_name,
        table=table,
        field=field,
    )
    if not key:
        return failure_result(
            "get_dict_values 需要 dict_name，或同时提供 table 与 field。"
            "连续/明文列（金额、时间、名称）不要调用本工具。",
            retryable=True,
        )
    page = _store_page(store, key, belong="dicts")
    values = dict_values_from_page(page) if page is not None else []
    if not values:
        return success_result(
            (
                f"未找到字典 {key} 的取值表。"
                "若字段注释或 labels= 已写明 0:待审核 这类映射，直接使用，不要再查。"
            ),
            data={"dict": key, "values": [], "table": table, "field": field},
        )
    lines = [f"{item['value']}: {item['label']}" for item in values]
    if page is not None:
        text = str(getattr(page, "body", "") or "")
        store_key = str(getattr(page, "store_key", "") or f"dicts/{key}")
        if text.strip():
            plane.merge_recall(
                {
                    "query": key,
                    "page_keys": [store_key],
                    "wiki_passages": {store_key: text.strip()},
                    "backend": "wiki",
                }
            )
            save_plane(plane)
    return success_result(
        f"字典 {key} 取值：\n" + "\n".join(lines),
        data={
            "dict": key,
            "values": values,
            "table": str(table or ""),
            "field": str(field or ""),
        },
    )
