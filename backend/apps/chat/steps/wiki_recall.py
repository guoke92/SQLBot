"""Wiki knowledge passage assembly for the chat runtime (KNOWLEDGE_BACKEND=wiki).

Runtime recall is DB-only:

- bound ``wiki_corpus_binding`` → ``wiki_page`` + ``wiki_chunk_embedding``
- unbound datasource → ``schema_vector`` (physical catalog fallback)

Zero Wiki hits stay on the Wiki path. Directory markdown is an admin import
source only — never scanned at query time.
"""

from __future__ import annotations

import time
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

from apps.chat.steps.recall_request import RecallRequest
from common.core.config import settings
from common.utils.utils import SQLBotLogUtil

_STORE_ERROR: str = ""
_EMBEDDING_BUILT: int = 0  # ensure() 触发构建的次数（遥测：embedding_built）
_DB_STORE: dict[int, Any] = {}
_DB_INDEX: dict[int, Any] = {}
_DB_STAMP: dict[
    int, tuple[int, int, str, str, int, str]
] = {}  # ds_id -> cache stamp (includes runtime status set)


@dataclass(frozen=True)
class WikiRecallResult:
    """一次 wiki 召回的完整产出——运行时各消费面的单一采集点。

    - ``text``：prompt-ready 拼接文本（planner 提示词消费）
    - ``hits``：``[{page_key, title, source, score, vector_score,
      lexical_score, filtered}]`` 结构化命中清单（wiki_hits 遥测 → 执行
      详情展示；vector/lexical 是原始通道信号，score 是 RRF 融合分）
    - ``page_keys``：锚点闭包输入（anchors/field_targets/maps_to 在页上）
    - ``elapsed_ms`` / ``embedding_built``：召回耗时与嵌入构建观测
      （retrieval span 输入——首次全量嵌入构建从此可见）
    """

    text: str = ""
    hits: list[dict[str, Any]] = field(default_factory=list)
    page_keys: list[str] = field(default_factory=list)
    elapsed_ms: int = 0
    embedding_built: bool = False
    # 保留页的完整渲染文本（执行详情"召回内容"展开用；键=page_key）
    passages: dict[str, str] = field(default_factory=dict)
    # 召回各阶段中间量（执行详情"召回过程"卡片：可见页数→通道→页融合→
    # 图扩展；可见页数/chunk 命中数/每通道 top5）
    trace: dict[str, Any] = field(default_factory=dict)
    store_source: str = ""  # db | unbound
    corpus_id: int = 0
    generation: int = 0
    vector_chunks: int = 0
    vector_channel: bool = False


def _hit_projection(
    passages: list[Any], kept_keys: set[str] | None = None
) -> list[dict[str, Any]]:
    """RenderedPassage → 轻量命中清单（观测 + 过滤标注）。"""
    projection: list[dict[str, Any]] = []
    for p in passages:
        page_key = str(getattr(p, "page_key", "") or "")
        if not page_key:
            continue
        projection.append(
            {
                "page_key": page_key,
                "title": str(getattr(p, "title", "") or ""),
                "source": str(getattr(p, "source", "") or ""),
                "score": getattr(p, "score", 0.0),
                "vector_score": round(float(getattr(p, "vector_score", 0.0) or 0.0), 4),
                "lexical_score": round(
                    float(getattr(p, "lexical_score", 0.0) or 0.0), 4
                ),
                "filtered": bool(kept_keys is not None and page_key not in kept_keys),
            }
        )
    return projection


def wiki_backend_active(ds_id: int | None = None) -> bool:
    """wiki 后端判定（单一权威实现，wiki_recall/recall_map/knowledge 共用）。

    ``KNOWLEDGE_BACKEND=wiki`` 且：
    - allowlist 含 ``*`` 或为空 → 全量启用（全面切换形态）；
    - 否则按 ds_id 灰度（ds_id 为 None 视为"无 DS 上下文"→ 跟随后端开关）。"""
    if settings.KNOWLEDGE_BACKEND != "wiki":
        return False
    raw = (settings.KNOWLEDGE_WIKI_DS_ALLOWLIST or "").strip()
    if not raw or raw == "*":
        return True
    ids = {int(item) for item in raw.split(",") if item.strip().isdigit()}
    return ds_id is None or int(ds_id) in ids


def datasource_databases(ds: Any) -> list[str]:
    """解析数据源的物理库名（scope.databases 围栏的运行面一侧）。

    数据源是知识来源、不是使用限制：解析失败/REST 等无库名类型返回
    空列表 = 页面围栏不生效（与"页面未声明 = 不限"同向，行为不回退）。
    ``configuration`` 就在传入对象上（AES 加密 JSON），protocol 的
    schema_namespace 内部解密并按类型取 dbSchema/database/catalog，
    无需额外查询。"""
    if ds is None:
        return []
    try:
        from apps.protocol import get_protocol_for_ds

        return [
            str(name).strip()
            for name in [get_protocol_for_ds(ds).schema_namespace(ds)]
            if str(name).strip()
        ]
    except Exception as exc:  # noqa: BLE001 — 解析失败=不围栏
        SQLBotLogUtil.debug("wiki scope db resolve failed: %s", exc)
        return []


# 兼容旧名（内部调用点）
_ds_allowlisted = wiki_backend_active


def _datasource_has_binding(ds_id: int) -> bool:
    """True when this datasource has an enabled wiki corpus binding."""
    try:
        from sqlmodel import Session

        from apps.knowledge.wiki.corpus_runtime import binding_stamp
        from common.core.db import engine

        with Session(engine) as session:
            return binding_stamp(session, ds_id) is not None
    except Exception as exc:  # noqa: BLE001
        SQLBotLogUtil.warning("wiki binding lookup failed ds_id=%s: %s", ds_id, exc)
        return False


def has_wiki_bound_corpus(ds_id: int | None = None) -> bool:
    """Runtime Wiki exists only when the datasource has an enabled DB binding."""
    if ds_id is None or not wiki_backend_active(ds_id):
        return False
    return _datasource_has_binding(int(ds_id))


def _db_store(ds_id: int) -> Any | None:
    """Load draft+published pages for the corpus bound to ``ds_id``. None = no binding."""
    global _STORE_ERROR
    stamp = None
    loaded = None
    try:
        from sqlmodel import Session

        from apps.knowledge.wiki.corpus_runtime import binding_stamp, load_bound_corpus
        from common.core.db import engine

        with Session(engine) as session:
            stamp = binding_stamp(session, ds_id)
            if stamp is None:
                _DB_STORE.pop(ds_id, None)
                _DB_INDEX.pop(ds_id, None)
                _DB_STAMP.pop(ds_id, None)
                return None
            if _DB_STAMP.get(ds_id) == stamp and ds_id in _DB_STORE:
                return _DB_STORE[ds_id]
            loaded = load_bound_corpus(session, ds_id)
    except Exception as exc:  # noqa: BLE001
        SQLBotLogUtil.warning("wiki db store load failed ds_id=%s: %s", ds_id, exc)
        _STORE_ERROR = str(exc)
        return None
    if loaded is None or stamp is None:
        _DB_STORE.pop(ds_id, None)
        _DB_INDEX.pop(ds_id, None)
        _DB_STAMP.pop(ds_id, None)
        return None
    from apps.knowledge.wiki.embeddings import WikiEmbeddingIndex

    store = loaded.store
    store.runtime_meta = {
        "source": "db",
        "corpus_id": loaded.corpus_id,
        "generation": loaded.generation,
        "vector_chunks": len(loaded.vectors),
        "status": loaded.status,
    }
    _DB_STORE[ds_id] = store
    _DB_STAMP[ds_id] = stamp
    _DB_INDEX[ds_id] = (
        WikiEmbeddingIndex.from_vectors(store, loaded.vectors)
        if loaded.vectors
        else None
    )
    SQLBotLogUtil.info(
        "wiki db store loaded: ds_id=%s corpus_id=%s pages=%s vectors=%s gen=%s",
        ds_id,
        loaded.corpus_id,
        len(store.pages),
        len(loaded.vectors),
        loaded.generation,
    )
    return store


def _store(ds_id: int | None = None) -> Any | None:
    """Bound DB corpus only. Unbound datasource → None."""
    if not has_wiki_bound_corpus(ds_id) or ds_id is None:
        return None
    return _db_store(int(ds_id))


def _embedding_index(store: Any, ds_id: int | None = None) -> Any | None:
    """Reuse the DB-backed WikiEmbeddingIndex. Never embed on the request path."""
    if store is None or ds_id is None or not settings.KNOWLEDGE_WIKI_EMBEDDING_ENABLED:
        return None
    if _DB_STORE.get(int(ds_id)) is not store:
        return None
    index = _DB_INDEX.get(int(ds_id))
    if index is None or not index.ensured:
        return None
    return index


def _store_meta(store: Any) -> dict[str, Any]:
    meta = getattr(store, "runtime_meta", None)
    if isinstance(meta, dict):
        return meta
    return {}


def _recall_passages(
    query: str,
    *,
    ds_id: int | None,
    databases: list[str] | None = None,
    mode: str,
    top_k: int | None = None,
    trace_out: dict[str, Any] | None = None,
) -> tuple[Any | None, list[Any] | None]:
    """recall 的公共执行体（store + RenderedPassage 列表）。

    ``databases`` = 当前数据源的物理库名（scope.databases 围栏输入）；
    ``ds_id`` 仅用于 allowlist 灰度判定。
    ``trace_out`` 透传给 recall 填充各阶段中间量（召回过程可观测）。"""
    if not _ds_allowlisted(ds_id):
        SQLBotLogUtil.info("wiki recall skipped: backend inactive ds_id=%s", ds_id)
        return None, None
    store = _store(ds_id)
    if store is None:
        SQLBotLogUtil.info(
            "wiki recall skipped: no bound corpus ds_id=%s mode=%s",
            ds_id,
            mode,
        )
        return None, None
    try:
        from apps.knowledge.recall_kernel.conflicts import (
            conflict_page_keys,
            conflicts_to_evidence,
            detect_caliber_conflicts,
        )
        from apps.knowledge.wiki.recall import recall

        effective_top_k = top_k or int(settings.KNOWLEDGE_WIKI_RECALL_TOP_K)
        index = _embedding_index(store, ds_id)
        embedder = None
        if index is not None:
            # 向量超采到全量 chunk（chat 168 回归：30 窗口把大表页的全部
            # chunk 挤出候选，页级聚合拿不到向量分 → 相关性过滤误杀主表）。
            # 矩阵点积全量 ~600ms/3672 chunk，一次查询无页级损失。
            embedder = lambda store_, query_: index.query_scores(query_)  # noqa: E731
        pin_keys: list[str] = []
        if mode == "business":
            conflicts = detect_caliber_conflicts(store, query)
            pin_keys = conflict_page_keys(conflicts)
            if trace_out is not None:
                trace_out["caliber_conflicts"] = conflicts_to_evidence(conflicts)
                trace_out["conflict_page_keys"] = list(pin_keys)
        passages = recall(
            query,
            store,
            oid=1,
            databases=databases or [],
            top_k=effective_top_k,
            mode=mode,
            embedder=embedder,
            trace_out=trace_out,
            pin_keys=pin_keys,
        )
        return store, passages
    except Exception as exc:
        SQLBotLogUtil.warning("wiki %s recall failed (degraded): %s", mode, exc)
        return store, None


def _recall_result(
    query: str,
    *,
    ds_id: int | None,
    databases: list[str] | None = None,
    mode: str,
    top_k: int | None = None,
) -> WikiRecallResult | None:
    """recall 的统一包装：text/hits/page_keys/耗时/嵌入标记一次采集。

    各消费面（planner 提示词 / wiki_hits 遥测 / 锚点闭包 / retrieval span）
    都从这一个结构取数——杜绝同一召回结果的多处重复解析。
    business 模式质量门已在 recall() 前置：过门语义页进 prompt，表页只作
    TableCandidate。physical 模式不过滤。

    有运行面 store 但零命中返回空结果（可观测）；无 Wiki runtime 返回 None。
    """
    started = time.monotonic()
    built_before = _EMBEDDING_BUILT
    trace: dict[str, Any] = {}
    store, passages = _recall_passages(
        query,
        ds_id=ds_id,
        databases=databases,
        mode=mode,
        top_k=top_k,
        trace_out=trace,
    )
    if store is None:
        return None
    meta = _store_meta(store)
    vector_channel = bool(_embedding_index(store, ds_id))
    elapsed_ms = int((time.monotonic() - started) * 1000)
    if not passages:
        SQLBotLogUtil.info(
            "wiki recall empty ds_id=%s source=%s corpus_id=%s gen=%s "
            "pages=%s vectors=%s vector_channel=%s mode=%s query_chars=%s elapsed_ms=%s",
            ds_id,
            meta.get("source") or "db",
            meta.get("corpus_id"),
            meta.get("generation"),
            len(getattr(store, "pages", {}) or {}),
            meta.get("vector_chunks"),
            vector_channel,
            mode,
            len(query or ""),
            elapsed_ms,
        )
        return WikiRecallResult(
            elapsed_ms=elapsed_ms,
            embedding_built=_EMBEDDING_BUILT > built_before,
            trace=trace,
            store_source=str(meta.get("source") or "db"),
            corpus_id=int(meta.get("corpus_id") or 0),
            generation=int(meta.get("generation") or 0),
            vector_chunks=int(meta.get("vector_chunks") or 0),
            vector_channel=vector_channel,
        )
    kept = list(passages)
    kept_keys = {str(p.page_key) for p in kept}
    text = "\n\n".join(p.text for p in kept)
    hits = _hit_projection(
        passages, kept_keys=kept_keys if mode == "business" else None
    )
    SQLBotLogUtil.info(
        "wiki recall ds_id=%s source=%s corpus_id=%s gen=%s pages=%s vectors=%s "
        "vector_channel=%s mode=%s query_chars=%s hits=%s kept=%s filtered=%s elapsed_ms=%s",
        ds_id,
        meta.get("source") or "db",
        meta.get("corpus_id"),
        meta.get("generation"),
        len(getattr(store, "pages", {}) or {}),
        meta.get("vector_chunks"),
        vector_channel,
        mode,
        len(query or ""),
        len(hits),
        len(kept),
        sum(1 for h in hits if h.get("filtered")),
        elapsed_ms,
    )
    return WikiRecallResult(
        text=text if text.strip() else "",
        hits=hits,
        page_keys=[str(getattr(p, "store_key", None) or p.page_key) for p in kept],
        elapsed_ms=elapsed_ms,
        embedding_built=_EMBEDDING_BUILT > built_before,
        passages={str(p.page_key): str(p.text or "") for p in kept},
        trace=trace,
        store_source=str(meta.get("source") or "db"),
        corpus_id=int(meta.get("corpus_id") or 0),
        generation=int(meta.get("generation") or 0),
        vector_chunks=int(meta.get("vector_chunks") or 0),
        vector_channel=vector_channel,
    )


def wiki_business_text(
    question: str,
    *,
    ds_id: int | None,
    databases: list[str] | None = None,
    top_k: int | None = None,
) -> str | None:
    """Recall → one prompt-ready text block（或 None=本层不产出，零影响）。"""
    result = wiki_business_recall(
        question, ds_id=ds_id, databases=databases, top_k=top_k
    )
    if result is None:
        return None
    return result.text or None


def wiki_recall(
    question: str,
    *,
    ds_id: int | None,
    databases: list[str] | None = None,
    top_k: int | None = None,
) -> WikiRecallResult | None:
    """Wiki 召回（结构化结果：text/hits/page_keys/观测）。

    消费方需要命中页元数据（闭包的 anchors/field_targets/maps_to、
    遥测的 hits、span 的耗时）。
    ``databases`` = 当前数据源物理库名（scope.databases 围栏）。"""
    if not _ds_allowlisted(ds_id):
        return None
    return _recall_result(
        question, ds_id=ds_id, databases=databases, mode="business", top_k=top_k
    )


# 保持兼容别名
wiki_business_recall = wiki_recall


def _strong_alias_hit(concept: str, store: Any) -> bool:
    """强命中判定：概念与某页别名/标题互为包含（中文业务词≥2 字）。

    "卫星遥感" vs 别名"问卷星"——无包含关系，不算命中（弱重叠不 bounce）；
    "平台录入" vs 别名"平台录入"——精确，命中。"""
    text = (concept or "").strip()
    if len(text) < 2:
        return False
    for alias in store.alias_index:
        if len(alias) >= 2 and (alias in text or text in alias):
            return True
    for page in store.pages.values():
        title = (page.title or "").strip()
        if len(title) >= 2 and (title in text or text in title):
            return True
    return False


def wiki_physical_text(
    concept: str,
    *,
    ds_id: int | None,
    databases: list[str] | None = None,
    top_k: int = 3,
) -> str | None:
    """门禁缺口检索（plan_gate missing_concepts 反弹上下文）——physical 模式：
    窗口小、无图扩展注入，与扩表机制互补不替代。向量通道同源复用。

    质量门：只有**强命中**（概念词作为别名/标题精确出现在某页，即 alias⊂concept
    或 concept⊂alias）才算"wiki 有此概念的证据"——coverage 通道对任意词都有弱
    重叠，无质量门会让每个 negative 都 bounce（verified_negative 永远不成立）。"""
    result = wiki_physical_recall(
        concept, ds_id=ds_id, databases=databases, top_k=top_k
    )
    if result is None:
        return None
    return result.text or None


def wiki_physical_recall(
    concept: str,
    *,
    ds_id: int | None,
    databases: list[str] | None = None,
    top_k: int = 3,
) -> WikiRecallResult | None:
    """physical 召回（强命中质量门），结构化结果（text/hits/page_keys）。"""
    store = _store(ds_id)
    if store is None:
        return None
    if not _strong_alias_hit(concept, store):
        return None
    return _recall_result(
        concept, ds_id=ds_id, databases=databases, mode="physical", top_k=top_k
    )


def wiki_enum_carriers(*, ds_id: int | None) -> set[str]:
    """Physical enum columns published on Wiki enum pages.

    Returns lowercased ``table.column`` and bare ``column`` names so SQL
    probes can be matched against the same enum pages used for display.
    """
    if not wiki_backend_active(ds_id) or ds_id is None:
        return set()
    store = _store(int(ds_id))
    if store is None:
        return set()
    names: set[str] = set()
    for page in getattr(store, "pages", {}).values():
        if str(getattr(page, "type", "") or "") != "dict":
            continue
        for block in getattr(page, "ground_blocks", ()) or ():
            if getattr(block, "kind", "") != "dict":
                continue
            data = getattr(block, "data", {}) or {}
            for item in data.get("fields") or []:
                ref = str(item or "").strip()
                if not ref:
                    continue
                names.add(ref.casefold())
                names.add(ref.rsplit(".", 1)[-1].casefold())
    return names


def enum_maps_for(
    field_refs: list[str], *, ds_id: int | None
) -> dict[str, dict[str, str]]:
    """查询结果枚举翻译映射（P3）：``{表.列: {VALUE: label}}``。

    输入 = 查询引用的物理字段（plan_facts 提取）；映射来自权威枚举页的
    ground:dict（强证据归并后的 value→label）。仅返回命中字段的映射，
    wiki 后端关闭或无枚举绑定时返回空 dict（零行为变化）。
    解析直接消费 parse_page 产出的 ``GroundAnchor.data``（与
    WikiSchemaRenderer._enum_label_map 单一真相），不再正则重解析。"""
    if not wiki_backend_active(ds_id):
        return {}
    store = _store(ds_id)
    if store is None or not field_refs:
        return {}
    try:
        wanted = {str(r).strip() for r in field_refs if r}
        maps: dict[str, dict[str, str]] = {}
        for page in store.pages.values():
            if page.type != "dict":
                continue
            for anchor in page.ground_blocks or ():
                if anchor.kind != "dict":
                    continue
                carriers = {str(c).strip() for c in anchor.data.get("fields") or []}
                hit = carriers & wanted
                if not hit:
                    continue
                values = {
                    str(v): str((meta or {}).get("label") or v).strip()
                    for v, meta in (anchor.data.get("values") or {}).items()
                }
                for ref in hit:
                    maps[ref] = values
        return maps
    except Exception as exc:  # noqa: BLE001 — 翻译失败=原样展示
        SQLBotLogUtil.warning("enum map build degraded: %s", exc)
        return {}


def translate_enum_cells(
    fields: list[str],
    rows: list[dict],
    enum_maps: dict[str, dict[str, str]],
    *,
    alias_to_ref: dict[str, str] | None = None,
) -> tuple[list[dict], dict[str, dict[str, str]]]:
    """结果单元格枚举值→描述翻译（纯函数，datasets 组装与 replay 双调）。

    翻译直接改 rows 单元格（前端 S2 无 formatter 钩子，这是唯一路径）：
    ``INVITE_AGW → 邀请认证-内管录入``（只显示 label，chat 168）。原始值
    保留在返回的 value_labels（{列: {原始值: label}}，仅命中子集）。

    ``fields`` = 结果列名（可能是 SQL 中文别名）。enum_maps 的键是
    ``表.物理列``。结果列与物理列的对应按优先级取：
    1. ``alias_to_ref``（SQL 别名回解的精确映射，audit 层传入）——别名
       直接挂回自己的物理列映射；
    2. 结果列名直命中物理列（无别名场景，旧路径）；
    3. 插入序兜底（sqlglot 解析失败/无 SQL 时）——单枚举列场景正确，
       多枚举列可能错挂，所以仅作最终回退。"""
    value_labels: dict[str, dict[str, str]] = {}
    if not enum_maps or not rows:
        return rows, value_labels
    # 物理列 → 候选映射（多表同名列合并，值集取并）
    by_column: dict[str, dict[str, str]] = {}
    for ref, mapping in enum_maps.items():
        column = ref.partition(".")[2]
        merged = dict(by_column.get(column) or {})
        merged.update(mapping)
        by_column[column] = merged
    # 结果列 → 值映射：先走精确别名回解，再直命中，最后插入序兜底
    field_maps: dict[str, dict[str, str]] = {}
    for result_field in fields or []:
        exact_ref = (alias_to_ref or {}).get(result_field)
        if exact_ref and exact_ref in enum_maps:
            field_maps[result_field] = enum_maps[exact_ref]
            continue
        direct = by_column.get(result_field)
        if direct is not None:
            field_maps[result_field] = direct
            continue
        for column, mapping in by_column.items():
            if column != result_field and result_field in rows[0] and column in rows[0]:
                continue  # 两列都真实存在于行 → 不是别名，勿乱挂
            field_maps.setdefault(result_field, mapping)
            break
    translated = []
    for row in rows:
        new_row = dict(row)
        for result_field, mapping in field_maps.items():
            if result_field not in new_row:
                continue
            raw = new_row[result_field]
            raw_str = str(raw) if raw is not None else None
            if raw_str is None or raw_str not in mapping:
                continue
            label = mapping[raw_str]
            if label and label != raw_str:
                new_row[result_field] = label
                value_labels.setdefault(result_field, {})[raw_str] = label
        translated.append(new_row)
    return translated, value_labels


def store_error() -> str:
    return _STORE_ERROR


def wiki_context_observability(res: WikiRecallResult | None) -> dict[str, Any]:
    """Telemetry copied onto every Wiki consumer (prepare_wiki / search_wiki)."""
    if res is None:
        return {
            "store_source": "unbound",
            "corpus_id": 0,
            "generation": 0,
            "vector_chunks": 0,
            "vector_channel": False,
            "wiki_trace": {},
            "hits": [],
            "elapsed_ms": 0,
            "embedding_built": False,
        }
    return {
        "store_source": str(res.store_source or "") or "db",
        "corpus_id": int(res.corpus_id or 0),
        "generation": int(res.generation or 0),
        "vector_chunks": int(res.vector_chunks or 0),
        "vector_channel": bool(res.vector_channel),
        "wiki_trace": dict(res.trace or {}),
        "hits": list(res.hits or [])[:12],
        "elapsed_ms": int(res.elapsed_ms or 0),
        "embedding_built": bool(res.embedding_built),
    }


def schema_ready_from_payload(payload: dict[str, Any] | None) -> bool:
    """True when recall produced at least one physical table with field rows."""
    from apps.chat.agent_knowledge import recall_schema_is_ready

    return recall_schema_is_ready(payload)


def wiki_span_fields(payload: dict[str, Any] | None) -> dict[str, Any]:
    """Process-span output shared by prepare_wiki and search_wiki."""
    data = payload or {}
    knowledge = str(data.get("knowledge_text") or "")
    schema = str(data.get("schema_text") or "")
    return {
        "backend": data.get("backend"),
        "hit_count": int(data.get("hit_count") or 0),
        "page_keys": list(data.get("page_keys") or [])[:20],
        "tables": list(data.get("tables") or [])[:20],
        "knowledge_chars": len(knowledge),
        "schema_chars": int(data.get("schema_chars") or len(schema)),
        "schema_ready": bool(data.get("schema_ready")),
        "store_source": data.get("store_source"),
        "corpus_id": data.get("corpus_id"),
        "generation": data.get("generation"),
        "vector_chunks": data.get("vector_chunks"),
        "vector_channel": bool(data.get("vector_channel")),
        "elapsed_ms": data.get("elapsed_ms"),
        "wiki_trace": data.get("wiki_trace") or {},
        "hits": list(data.get("hits") or [])[:12],
        "recall_status": data.get("recall_status"),
        "focus": str(data.get("focus") or "all"),
        "gate_rejected": list(data.get("gate_rejected") or [])[:20],
        "table_evidence": data.get("table_evidence") or {},
        "budget_cut": list(data.get("budget_cut") or [])[:20],
        "caliber_conflicts": list(data.get("caliber_conflicts") or [])[:4],
        # Prompt composition (what the model actually sees) — the direct
        # evidence when two environments answer the same question differently.
        "retrieval_query": str(data.get("query") or "")[:400],
        "pinned_tables": list(data.get("pinned_tables") or [])[:20],
        "pinned_pages": list(data.get("pinned_pages") or [])[:20],
        "evidence_fields": {
            str(table): list(names)[:40]
            for table, names in dict(data.get("evidence_fields") or {}).items()
        },
        "projection": dict(data.get("projection") or {}),
        **({"error": data.get("error")} if data.get("error") else {}),
    }


def _empty_wiki_payload(**extra: Any) -> dict[str, Any]:
    payload = {
        "knowledge_text": "",
        "tables": [],
        "schema_text": "",
        "backend": "none",
        "page_keys": [],
        "hit_count": 0,
        "schema_ready": False,
        "schema_chars": 0,
        **wiki_context_observability(None),
    }
    payload.update(extra)
    return payload


# ── Unified Wiki Context Retrieval Service ─────────────────────────────────


def _schema_fallback_context(
    llm_service: Any,
    query: str,
    *,
    access_scope: Any = None,
    pin_tables: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Schema-vector recall when this datasource has no Wiki runtime.

    ``schema_vector`` is the sole fallback store (filled by sync). Renders local
    catalog text only — never pulls live sample rows from the business datasource.
    """
    from apps.datasource.embedding.schema_index import (
        recall_schema_context,
        schedule_schema_vector_sync,
    )
    from apps.knowledge.recall_kernel.types import RecallBudget

    ds_id = getattr(getattr(llm_service, "ds", None), "id", None)
    schedule_schema_vector_sync(ds_id)
    budget = RecallBudget.from_settings()
    chat_question = getattr(llm_service, "chat_question", None)
    orig_q = ""
    wrote_q = False
    if chat_question is not None and hasattr(chat_question, "retrieval_question"):
        orig_q = str(getattr(chat_question, "retrieval_question", "") or "")
        chat_question.retrieval_question = str(query or "").strip()
        wrote_q = True
    try:
        return recall_schema_context(
            llm_service,
            query,
            access_scope=access_scope,
            table_limit=budget.max_tables,
            total_limit=budget.max_tables_total,
            pinned_tables=[
                str(name).strip() for name in (pin_tables or ()) if str(name).strip()
            ],
        )
    finally:
        if wrote_q and chat_question is not None:
            chat_question.retrieval_question = orig_q


def _decorate_schema_fallback(payload: dict[str, Any]) -> dict[str, Any]:
    fallback = dict(payload)
    fallback.setdefault("store_source", str(fallback.get("backend") or "schema_vector"))
    fallback.setdefault("corpus_id", 0)
    fallback.setdefault("generation", 0)
    fallback.setdefault("vector_chunks", 0)
    fallback.setdefault("vector_channel", False)
    fallback.setdefault("wiki_trace", {})
    fallback.setdefault("hits", [])
    fallback.setdefault("elapsed_ms", 0)
    fallback.setdefault("embedding_built", False)
    fallback.setdefault("gate_rejected", [])
    evidence = dict(fallback.get("table_evidence") or {})
    tables = [str(name) for name in (fallback.get("tables") or []) if str(name)]
    # Preserve non-empty evidence from recall; fill missing keys with the
    # backend tag so mid-turn search policy does not strip structural peers.
    fallback["table_evidence"] = {
        name: list(evidence.get(name) or ["schema_vector"]) for name in tables
    }
    fallback.setdefault("budget_cut", [])
    fallback.setdefault("caliber_conflicts", [])
    fallback.setdefault("query", str(fallback.get("query") or ""))
    fallback["schema_chars"] = len(str(fallback.get("schema_text") or ""))
    fallback["schema_ready"] = schema_ready_from_payload(fallback)
    return fallback


def _attach_pinned_passages(
    store: Any,
    *,
    keys: Sequence[str],
    databases: list[str],
    page_keys: list[str],
    wiki_passages: dict[str, str],
    source_note: str,
) -> list[str]:
    """Render ``keys`` outside the ranked window and append them (dedup by key).

    One mechanism for both prior-turn rehydration and enum auto-pin; returns
    the keys actually attached.
    """
    from apps.knowledge.wiki.recall import render_page_passage

    attached: list[str] = []
    for raw in keys:
        key = str(raw or "").strip()
        if not key or key in page_keys or key in wiki_passages:
            continue
        try:
            passage = render_page_passage(
                store, key, databases=databases, source_note=source_note
            )
        except Exception as exc:  # noqa: BLE001 — a bad pin must not fail recall
            SQLBotLogUtil.warning("pinned passage %s skipped: %s", key, exc)
            continue
        if passage is None or not passage.text:
            continue
        store_key = str(passage.store_key or passage.page_key or key)
        if store_key in wiki_passages:
            continue
        page_keys.append(store_key)
        wiki_passages[store_key] = passage.text
        attached.append(store_key)
    return attached


def _catalog_query(request: RecallRequest) -> str:
    return str(request.question or request.query or "").strip()


def _bind_recall_pages(
    store: Any,
    page_keys: list[str],
    tables: list[str],
    *,
    named_query: str,
    pin_pages: Sequence[str],
) -> list[str]:
    from apps.chat.steps.wiki_focus import (
        is_peripheral_page,
        page_binds_to_tables,
        page_named_in_query,
    )

    pin_set = {str(key) for key in pin_pages if str(key)}
    kept: list[str] = []
    for raw in page_keys:
        key = str(raw or "").strip()
        if not key or key in kept:
            continue
        if key in pin_set or page_named_in_query(key, named_query):
            kept.append(key)
            continue
        if not tables:
            if not is_peripheral_page(key):
                kept.append(key)
            continue
        if page_binds_to_tables(key, tables, store):
            kept.append(key)
    return kept


def _wiki_payload_from_recall(
    *,
    request: RecallRequest,
    ds: Any,
    ds_id: int | None,
    top_k: int,
) -> dict[str, Any]:
    from apps.chat.steps.wiki_focus import (
        is_peripheral_page,
        named_wiki_keys,
    )
    from apps.chat.steps.wiki_schema import (
        collect_schema_evidence,
        enum_pins_for,
        merge_field_sets,
        project_schema,
    )
    from apps.knowledge.recall_kernel.render import render_schema
    from apps.knowledge.recall_kernel.tables import resolve_wiki_tables
    from apps.knowledge.recall_kernel.types import (
        RecallBudget,
        RecallBundle,
        TableCandidate,
    )

    rrf_query = str(request.query or "").strip()
    catalog_query = _catalog_query(request) or rrf_query
    named_query = rrf_query or catalog_query
    budget = RecallBudget.from_settings()
    databases = datasource_databases(ds)
    res = (
        wiki_recall(rrf_query, ds_id=ds_id, databases=databases, top_k=top_k)
        if rrf_query
        else None
    )
    store = _store(ds_id)
    trace = dict(getattr(res, "trace", None) or {})
    candidates: list[TableCandidate] = []
    budget_cut: list[str] = []
    page_keys = list(getattr(res, "page_keys", None) or []) if res else []
    raw_passages = dict(getattr(res, "passages", None) or {})
    wiki_passages: dict[str, str] = {}
    for store_key in page_keys:
        slug = store_key.rsplit("/", 1)[-1]
        text = str(raw_passages.get(store_key) or raw_passages.get(slug) or "").strip()
        if text:
            wiki_passages[store_key] = text
    pin_pages = list(dict.fromkeys([*request.pin_pages, *named_wiki_keys(named_query)]))
    pinned_pages: list[str] = []
    if store is not None:
        # 上轮知识面复水 / 点名页：按 key 从 store 重渲。
        pinned_pages.extend(
            _attach_pinned_passages(
                store,
                keys=pin_pages,
                databases=databases,
                page_keys=page_keys,
                wiki_passages=wiki_passages,
                source_note="上轮已用",
            )
        )
    if store is not None and (res is not None or request.pin_tables or pin_pages):
        extra_keys = [
            key
            for key in (
                list(trace.get("closure_extra_keys") or [])
                + [str(item) for item in (trace.get("conflict_page_keys") or [])]
            )
            if not is_peripheral_page(str(key))
        ]
        attribution_keys = [key for key in page_keys if not is_peripheral_page(key)]
        rrf_candidates, budget_cut = resolve_wiki_tables(
            store,
            page_keys=attribution_keys if rrf_query else [],
            extra_keys=extra_keys if rrf_query else [],
            table_pages=(
                list(trace.get("gated_table_pages") or []) if rrf_query else []
            ),
            scores={
                str(key): float(score)
                for key, score in dict(trace.get("page_scores") or {}).items()
            },
            budget=budget,
            query=named_query,
            pinned_tables=request.pin_tables,
        )
        candidates = rrf_candidates
    table_names = [item.name for item in candidates]
    schema_text = ""
    evidence_fields: dict[str, set[str]] = {}
    projection_stats: dict[str, Any] = {}
    if table_names:
        evidence_fields = merge_field_sets(
            collect_schema_evidence(store, page_keys=page_keys, tables=table_names),
            request.required_fields,
        )
        schema_text = render_schema(table_names, store=store, project_relations=False)
        if store is not None:
            pinned_pages.extend(
                _attach_pinned_passages(
                    store,
                    keys=enum_pins_for(
                        schema_text,
                        queries=[catalog_query or named_query],
                        keep_fields=evidence_fields,
                        present_pages=wiki_passages.keys(),
                    ),
                    databases=databases,
                    page_keys=page_keys,
                    wiki_passages=wiki_passages,
                    source_note="字段枚举",
                )
            )
        projection_stats = project_schema(
            schema_text,
            budget_chars=budget.schema_chars,
            queries=[catalog_query or named_query],
            keep_fields=evidence_fields,
            present_pages=wiki_passages.keys(),
        ).as_stats()
    page_keys = _bind_recall_pages(
        store,
        page_keys,
        table_names,
        named_query=named_query,
        pin_pages=pin_pages,
    )
    wiki_passages = {
        key: text for key, text in wiki_passages.items() if key in set(page_keys)
    }
    wiki_text = "\n\n".join(
        part
        for part in [*(wiki_passages.get(key) or "" for key in page_keys)]
        if part.strip()
    )
    if not wiki_text and res is not None and page_keys:
        wiki_text = str(getattr(res, "text", "") or "")
    bundle = RecallBundle(
        backend="wiki",
        tables=tuple(candidates),
        schema_text=schema_text,
        budget=budget,
        trace=trace,
        knowledge_text=wiki_text,
        page_keys=tuple(page_keys),
        hits=tuple(getattr(res, "hits", None) or []) if res else (),
        store_source="db",
        corpus_id=int(getattr(res, "corpus_id", 0) or 0) if res else 0,
        generation=int(getattr(res, "generation", 0) or 0) if res else 0,
        vector_chunks=int(getattr(res, "vector_chunks", 0) or 0) if res else 0,
        vector_channel=bool(getattr(res, "vector_channel", False)) if res else False,
        elapsed_ms=int(getattr(res, "elapsed_ms", 0) or 0) if res else 0,
        embedding_built=bool(getattr(res, "embedding_built", False)) if res else False,
        schema_chars=int(projection_stats.get("chars") or len(schema_text)),
        hit_count=len(getattr(res, "hits", None) or []) if res else 0,
        gate_rejected=tuple(str(k) for k in (trace.get("gate_rejected") or [])),
        budget_cut=tuple(budget_cut),
        caliber_conflicts=tuple(
            dict(item)
            for item in (trace.get("caliber_conflicts") or [])
            if isinstance(item, dict)
        ),
        evidence_fields={
            table: tuple(sorted(names)) for table, names in evidence_fields.items()
        },
        pinned_tables=tuple(request.pin_tables),
        pinned_pages=tuple(pinned_pages),
        query=rrf_query,
        projection=projection_stats,
    )
    payload = bundle.to_agent_payload()
    if wiki_passages:
        payload["wiki_passages"] = wiki_passages
    payload["schema_ready"] = schema_ready_from_payload(payload)
    payload["focus"] = str(getattr(request, "focus", "all") or "all")
    payload["question"] = catalog_query
    payload["pinned_tables"] = list(request.pin_tables)
    return payload


def retrieve_wiki_context(
    llm_service: Any,
    query: str | RecallRequest,
    *,
    access_scope: Any = None,
    top_k: int | None = None,
) -> dict[str, Any]:
    """Wiki (bound DB corpus) or schema_vector — never mixed.

    1. Datasource has an enabled wiki_corpus_binding: recall Wiki knowledge
       + anchor-closure schema. Zero hits stay on this path.
    2. Datasource has no Wiki binding: ``schema_vector`` catalog recall.

    ``query`` may be a plain string (search_wiki) or a ``RecallRequest``.
    Empty ``query`` with pins is pin-only rehydrate: restore those keys from
    the store and skip vector recall.
    """
    from apps.knowledge.recall_kernel.types import RecallBudget

    request = RecallRequest.coerce(query)
    clean_query = request.query
    if not clean_query and not request.is_continuation:
        return _empty_wiki_payload()
    ds = getattr(llm_service, "ds", None)
    ds_id = getattr(ds, "id", None)
    budget = RecallBudget.from_settings()
    effective_top_k = int(top_k) if top_k is not None else budget.passages

    if has_wiki_bound_corpus(ds_id):
        try:
            return _wiki_payload_from_recall(
                request=request,
                ds=ds,
                ds_id=ds_id,
                top_k=effective_top_k,
            )
        except Exception as exc:
            SQLBotLogUtil.warning(
                "retrieve_wiki_context wiki path failed ds_id=%s: %s",
                ds_id,
                exc,
            )
            return _empty_wiki_payload(backend="wiki", store_source="db")

    if not clean_query and not request.pin_tables:
        return _empty_wiki_payload(backend="schema_vector")

    try:
        return _decorate_schema_fallback(
            _schema_fallback_context(
                llm_service,
                clean_query,
                access_scope=access_scope,
                pin_tables=request.pin_tables,
            )
        )
    except Exception as exc:
        SQLBotLogUtil.warning(
            "retrieve_wiki_context failed in fallback branch: %s",
            exc,
            exc_info=True,
        )
        return _empty_wiki_payload(backend="error", error=str(exc))
