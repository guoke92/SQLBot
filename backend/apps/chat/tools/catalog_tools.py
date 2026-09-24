"""Orthogonal catalog tools: schema, relations, knowledge, dictionary values.

Each tool has one job. The model chooses what to open; these functions do not
rank tables, hop the FK graph, or inject peripheral wiki pages.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

from apps.chat.agent_knowledge import (
    AgentKnowledgePlane,
    MergeDelta,
)
from apps.chat.steps.wiki_schema import (
    RELATION_PEER_MISSING,
    field_enum_rows,
    lookup_dict_page,
    schema_fields_by_table,
    table_field_enum,
)
from apps.chat.tools.base import failure_result, success_result
from apps.conversation.runtime_context import (
    attach_runtime,
    current_worker_identity,
    peek_runtime,
)
from apps.conversation.tooling import ToolResult
from common.utils.utils import SQLBotLogUtil

MAX_TABLES_PER_CALL = 3
KNOWLEDGE_PAGE_TYPES = frozenset({"concept", "caliber", "metric", "scenario"})
KNOWLEDGE_BELONGS = frozenset({"concepts", "calibers", "metrics", "scenarios"})
KNOWLEDGE_TOP_K = 6
_RELATION_LINE_RE = re.compile(
    r"^关联:\s*"
    r"(?P<left_table>[A-Za-z_][\w]*)\.(?P<left_col>[A-Za-z_]\w*)"
    r"\s*→\s*"
    r"(?P<right_table>[A-Za-z_][\w]*)\.(?P<right_col>[A-Za-z_]\w*)"
    r"(?:\s*\((?P<peer>[^)]+)\))?"
    r"(?:\s*\[(?P<tag>[^\]]+)\])?"
)


_RELATION_TRUST_LABELS = frozenset(
    {"suggested", "confirmed", "candidate", "inferred", "disputed", "likely"}
)


def _trust_from_tag(tag: str) -> str:
    text = str(tag or "").strip().lower()
    if text in _RELATION_TRUST_LABELS:
        return text
    for label in _RELATION_TRUST_LABELS:
        if label in text:
            return label
    return ""


def _split_field_ref(ref: str) -> tuple[str, str]:
    table, _, col = str(ref or "").strip().partition(".")
    return table.strip(), col.strip()


def relation_edges_from_store(
    store: Any, tables: Sequence[str]
) -> list[dict[str, Any]]:
    """Read ``ground:relation`` blocks from named table pages, including trust."""
    wanted = [str(name).strip() for name in tables if str(name).strip()]
    if store is None or not wanted:
        return []
    edges: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str, str]] = set()
    for name in wanted:
        page = _store_page(store, name, belong="tables")
        if page is None:
            continue
        for block in getattr(page, "ground_blocks", ()) or ():
            if getattr(block, "kind", "") != "relation":
                continue
            data = getattr(block, "data", {}) or {}
            if not isinstance(data, Mapping):
                continue
            left_t, left_c = _split_field_ref(str(data.get("left") or ""))
            right_t, right_c = _split_field_ref(str(data.get("right") or ""))
            if not left_t or not right_t:
                continue
            key = (left_t, left_c, right_t, right_c)
            if key in seen:
                continue
            seen.add(key)
            trust = str(data.get("trust") or "").strip()
            tag = str(data.get("source") or data.get("evidence") or "").strip()
            line = f"{left_t}.{left_c} → {right_t}.{right_c}"
            if trust:
                line = f"{line} [{trust}]"
            edges.append(
                {
                    "left_table": left_t,
                    "left_col": left_c,
                    "right_table": right_t,
                    "right_col": right_c,
                    "trust": trust,
                    "tag": tag,
                    "line": line,
                }
            )
    return edges


def _merge_relation_edges(
    primary: Sequence[Mapping[str, Any]], extra: Sequence[Mapping[str, Any]]
) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str, str]] = set()
    for edge in (*primary, *extra):
        key = (
            str(edge.get("left_table") or ""),
            str(edge.get("left_col") or ""),
            str(edge.get("right_table") or ""),
            str(edge.get("right_col") or ""),
        )
        if not key[0] or not key[2] or key in seen:
            continue
        seen.add(key)
        merged.append(dict(edge))
    return merged


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
                "trust": _trust_from_tag(tag),
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
    edges: Sequence[Mapping[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
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
        page_key = str(
            getattr(passage, "page_key", "") or getattr(page, "page_key", "") or ""
        )
        if "catalog_summary" in page_key or "catalog_summary" in store_key:
            continue
        belong = str(
            getattr(passage, "belong", "") or getattr(page, "belong", "") or ""
        )
        if page_type not in KNOWLEDGE_PAGE_TYPES and belong not in KNOWLEDGE_BELONGS:
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


def _infer_table_for_field(plane: AgentKnowledgePlane, field_name: str) -> str:
    wanted = str(field_name or "").strip()
    if not wanted:
        return ""
    hits: list[str] = []
    for table_name, body in plane.schema_by_table.items():
        for item in schema_fields_by_table(body).get(table_name) or []:
            if item.name == wanted:
                hits.append(table_name)
                break
    return hits[0] if len(hits) == 1 else ""


def resolve_dict_key(
    *,
    store: Any,
    plane: AgentKnowledgePlane,
    dict_name: str = "",
    table: str = "",
    field: str = "",
) -> str:
    named = str(dict_name or "").strip().rsplit("/", 1)[-1]
    table_name = str(table or "").strip()
    field_name = str(field or "").strip() or named
    if not table_name and field_name:
        table_name = _infer_table_for_field(plane, field_name)
    spec = table_field_enum(store, table_name, field_name) if table_name else None
    if spec is not None and spec.dict_key:
        return spec.dict_key
    if table_name and field_name:
        body = plane.schema_by_table.get(table_name) or ""
        if body:
            for item in schema_fields_by_table(body).get(table_name) or []:
                if item.name == field_name and item.enum:
                    return str(item.enum)
    if named:
        page = lookup_dict_page(
            store, named, table=table_name, opened_tables=plane.tables
        )
        if page is not None:
            return str(getattr(page, "page_key", "") or named).rsplit("/", 1)[-1]
        return named
    if table_name and field_name:
        return f"{table_name}__{field_name}"
    return ""


def _fence_tables(
    tables: Sequence[str],
    access_scope: Any = None,  # noqa: ARG001
) -> tuple[list[str], list[str]]:
    """Keep requested names. Runtime table set is the bound wiki, not ACL."""
    names = list(
        dict.fromkeys(str(name).strip() for name in tables if str(name).strip())
    )
    return names, []


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
    requested, _fenced = _fence_tables(tables, access_scope)
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
        notes.append(f"本对话已展开、未重复拉取：{already}。")
    if missing:
        notes.append(f"未找到表：{missing}。请对照 schema_outline 中的物理表名。")
    if not shown and not missing:
        notes.append("这些表已在先前 ToolMessage 中返回，不要重复调用。")
    summary = (
        f"已展开表 {delta.added_tables or already}。"
        + (" " + " ".join(notes) if notes else "")
        + " 不要再为同一张表调用本工具。"
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
    requested, _fenced = _fence_tables(tables, access_scope)
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
    edges = _merge_relation_edges(
        relation_edges_from_store(store, requested),
        parse_relation_edges(raw),
    )
    grouped = classify_relations(requested, edges)
    save_plane(plane)
    direct_lines = [item["line"] for item in grouped["direct"] if item.get("line")]
    bridge_notes = [str(item.get("note") or "") for item in grouped["bridges"]]
    if direct_lines:
        summary = "已知直接关联（trust 仅供参考，不阻止 JOIN）：\n" + "\n".join(
            direct_lines
        )
    elif bridge_notes:
        summary = "无直接外键，候选桥接（仍可按业务需要 JOIN）：\n" + "\n".join(
            bridge_notes
        )
    else:
        summary = (
            f"未找到 {requested} 之间的已知关联边。"
            "关联信息仅供参考，仍可按业务需要 JOIN。"
        )
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
    from apps.knowledge.wiki.hit import (
        format_knowledge_hits,
        project_knowledge_hit,
    )

    hits: list[dict[str, Any]] = []
    seen: set[str] = set()
    for passage in kept:
        page_key = str(getattr(passage, "page_key", "") or "")
        store_key = str(getattr(passage, "store_key", "") or page_key)
        page = _store_page(store, store_key) or _store_page(store, page_key)
        if page is None:
            continue
        ident = str(getattr(page, "store_key", "") or page.page_key)
        if ident in seen:
            continue
        seen.add(ident)
        hit = project_knowledge_hit(page)
        hit["store_key"] = ident
        hits.append(hit)
    page_keys = [
        str(item.get("store_key") or item.get("page_key") or "")
        for item in hits
        if item.get("store_key") or item.get("page_key")
    ]
    plane.knowledge_searches = int(plane.knowledge_searches or 0) + 1
    for key in page_keys:
        if key and key not in plane.page_keys:
            plane.page_keys.append(key)
    save_plane(plane)
    if not hits:
        return success_result(
            (
                "未命中业务口径/概念/场景页。字段含义若已在表注释中写明，直接写 SQL；"
                "名实仍冲突则 request_clarification，不要换近义词再搜。"
            ),
            data={"page_keys": [], "hits": [], "hit_count": 0},
        )
    rendered = "\n".join(format_knowledge_hits(hits).values())
    return success_result(
        (
            f"已命中 {len(hits)} 条业务知识（概念/口径/指标/场景对象）。"
            "用 maps_to / field_targets / adjudication / hubs 按 §2 裁决；"
            "对象正文如下，不要再 search_knowledge。"
            "表结构请用 get_table_schema，不要假设本工具带回了 DDL。\n"
            f"{rendered}"
        ),
        data={
            "page_keys": page_keys,
            "hits": hits,
            "hit_count": len(hits),
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
    store, _live, _databases = _catalog_sources(llm_service)
    named = str(dict_name or "").strip().rsplit("/", 1)[-1]
    table_name = str(table or "").strip()
    field_name = str(field or "").strip() or named
    if not table_name and field_name:
        table_name = _infer_table_for_field(plane, field_name)
    if not named and not (table_name and field_name):
        return failure_result(
            "get_dict_values 需要 dict_name，或同时提供 table 与 field。"
            "连续/明文列（金额、时间、名称）不要调用本工具。",
            retryable=True,
        )

    spec = (
        table_field_enum(store, table_name, field_name)
        if table_name and field_name
        else None
    )
    values = field_enum_rows(spec) if spec is not None else []
    key = (
        (spec.dict_key if spec is not None else "")
        or named
        or (f"{table_name}__{field_name}" if table_name and field_name else "")
    )
    page = None
    if not values:
        key = resolve_dict_key(
            store=store,
            plane=plane,
            dict_name=named or key,
            table=table_name,
            field=field_name,
        )
        page = lookup_dict_page(
            store, key, table=table_name, opened_tables=plane.tables
        )
        if page is None:
            page = _store_page(store, key, belong="dicts")
        values = dict_values_from_page(page) if page is not None else []
    if not values:
        values = _value_index_enum_values(llm_service, table_name, field_name or named)
    if not values:
        return success_result(
            (
                f"未找到字典 {key or named} 的取值表。"
                "若字段注释或 labels= 已写明 0:待审核 这类映射，直接使用，不要再查。"
            ),
            data={
                "dict": key or named,
                "values": [],
                "table": table_name,
                "field": field_name,
            },
        )
    lines = [
        f"{item['value']}: {item['label']}" if item.get("label") else str(item["value"])
        for item in values
    ]
    return success_result(
        f"字典 {key} 取值：\n" + "\n".join(lines),
        data={
            "dict": key,
            "values": values,
            "table": table_name,
            "field": field_name,
        },
    )


def lookup_values(
    llm_service: Any,
    phrases: Sequence[str] | None = None,
    *,
    scope: Sequence[str] | None = None,
    hint_table: str = "",
    access_scope: Any = None,  # noqa: ARG001 — bound wiki / value index, not ACL
) -> ToolResult:
    """Reverse-lookup phrases or sample a field (no phrases + table.field scope)."""
    from apps.datasource.instance_index.service import parse_lookup_scope

    plane = load_plane()
    cleaned: list[str] = []
    skipped: list[str] = []
    store, _live, _databases = _catalog_sources(llm_service)
    closed = _closed_lookup_vocab(store, plane)
    for raw in phrases or ():
        text = str(raw or "").strip()
        if not text:
            continue
        reason = _lookup_skip_reason(text, closed=closed)
        if reason:
            skipped.append(f"{text}（{reason}）")
            continue
        cleaned.append(text)
    parsed = parse_lookup_scope(scope, hint_table=str(hint_table or "").strip())
    if not cleaned and not parsed.fields:
        extra = f" 已跳过：{'、'.join(skipped)}。" if skipped else ""
        return failure_result(
            (
                "lookup_values 需要开放实例短语，或无短语时提供字段级 scope"
                "（如 tenant_project_approval.solution_manager_name）。"
                "日期、纯数字、封闭枚举码和「平台录入」这类概念/字典叫法请用 "
                "search_knowledge 或 schema labels。"
                f"{extra}"
            ),
            retryable=True,
        )
    ds = getattr(llm_service, "ds", None)
    ds_id = getattr(ds, "id", None)
    if ds_id is None:
        return failure_result(
            "当前对话没有绑定数据源，无法反查实例值。", retryable=False
        )
    try:
        from apps.conversation.session import session_scope
        from apps.datasource.instance_index.service import (
            annotate_lookup_candidate,
            list_field_topk,
            match_phrases,
        )
        from apps.protocol import get_protocol_for_ds

        proto = None
        try:
            proto = get_protocol_for_ds(ds)
        except Exception:
            proto = None
        with session_scope() as session:
            if cleaned:
                hits = match_phrases(
                    session,
                    ds_id=int(ds_id),
                    phrases=cleaned,
                    scope=parsed,
                )
            else:
                hits = []
                for table_name, field_name in parsed.fields:
                    hits.extend(
                        list_field_topk(
                            session,
                            ds_id=int(ds_id),
                            table_name=table_name,
                            field_name=field_name,
                            proto=proto,
                            ds=ds,
                        )
                    )
    except Exception as exc:
        SQLBotLogUtil.warning("lookup_values failed: %s", exc)
        return failure_result(f"实例值反查失败：{exc}", retryable=True)

    candidates = [annotate_lookup_candidate(hit, phrases=cleaned) for hit in hits]
    mode = "phrases" if cleaned else "field_topk"
    if not candidates:
        return success_result(
            "值索引未命中这些短语。不要把短语直接当 WHERE；改用 schema labels 或 search_knowledge。",
            data={
                "phrases": cleaned,
                "scope": list(scope or []),
                "mode": mode,
                "candidates": [],
            },
        )
    lines = []
    for item in candidates:
        hint = item.get("match_hint") or "eq"
        display = item.get("display_name")
        tail = f" match={hint}"
        if display:
            tail += f" display={display}"
        lines.append(
            f"{item['full_value']} → {item['table']}.{item['field']}（{item['val_type']}）{tail}"
        )
    notice = "候选证据，不是落点；必须再过 §2 才能写入 WHERE。"
    if any(item.get("match_hint") == "contains" for item in candidates):
        notice += " match_hint=contains 时 WHERE 禁止等值，用 LIKE 或 IN(aliases)。"
    return success_result(
        notice + "\n" + "\n".join(lines),
        data={
            "phrases": cleaned,
            "scope": list(scope or []),
            "mode": mode,
            "candidates": candidates,
        },
    )


_DATE_PHRASE_RE = re.compile(
    r"^(?:\d{4}[-/.年]\d{1,2}(?:[-/.月]\d{1,2})?|\d{1,2}月|\d+年)$"
)
_CLOSED_PAGE_TYPES = frozenset({"concept", "caliber", "metric", "dict", "scenario"})


def _lookup_skip_reason(text: str, *, closed: set[str]) -> str:
    stripped = text.strip()
    if not stripped:
        return "empty"
    if stripped.isdigit():
        return "纯数字"
    if _DATE_PHRASE_RE.match(stripped):
        return "日期"
    from apps.dictionary.matching import normalize_dictionary_value

    token = normalize_dictionary_value(stripped)
    if token and token in closed:
        return "封闭枚举或概念别名"
    return ""


def _closed_lookup_vocab(store: Any, plane: AgentKnowledgePlane) -> set[str]:
    """Concept/dict titles, aliases, and schema labels — not open instances."""
    from apps.dictionary.matching import normalize_dictionary_value

    vocab: set[str] = set()

    def _add(raw: str) -> None:
        token = normalize_dictionary_value(raw)
        if len(token) >= 2:
            vocab.add(token)

    for body in plane.schema_by_table.values():
        for fields in schema_fields_by_table(body).values():
            for item in fields:
                labels = str(getattr(item, "labels", "") or "")
                for part in re.split(r"[,，;；|/]", labels):
                    left, sep, right = part.partition(":")
                    if sep:
                        _add(left)
                        _add(right)
                    else:
                        _add(part)
    pages = getattr(store, "pages", None)
    if isinstance(pages, Mapping):
        for page in pages.values():
            page_type = str(getattr(page, "type", "") or "")
            if page_type not in _CLOSED_PAGE_TYPES:
                continue
            _add(str(getattr(page, "title", "") or ""))
            _add(str(getattr(page, "page_key", "") or ""))
            for alias in getattr(page, "aliases", ()) or ():
                _add(str(alias))
            if page_type != "dict":
                continue
            for block in getattr(page, "ground_blocks", ()) or ():
                if getattr(block, "kind", "") != "dict":
                    continue
                data = getattr(block, "data", {}) or {}
                values = data.get("values") if isinstance(data, Mapping) else None
                if not isinstance(values, Mapping):
                    continue
                for code, meta in values.items():
                    _add(str(code))
                    if isinstance(meta, Mapping):
                        _add(str(meta.get("label") or ""))
                    elif meta is not None:
                        _add(str(meta))
    return vocab


def _value_index_enum_values(
    llm_service: Any, table: str, field: str
) -> list[dict[str, str]]:
    return _value_index_field_values(llm_service, table, field)


def _value_index_field_values(
    llm_service: Any, table: str, field: str
) -> list[dict[str, str]]:
    table_name = str(table or "").strip()
    field_name = str(field or "").strip()
    ds = getattr(llm_service, "ds", None)
    ds_id = getattr(ds, "id", None)
    if ds_id is None or not table_name or not field_name:
        return []
    try:
        from apps.conversation.session import session_scope
        from apps.datasource.instance_index.service import list_field_values

        with session_scope() as session:
            return list_field_values(
                session,
                ds_id=int(ds_id),
                table_name=table_name,
                field_name=field_name,
                val_types=("enum_code", "enum_label"),
            )
    except Exception as exc:
        SQLBotLogUtil.warning("get_dict_values value-index fallback failed: %s", exc)
        return []
