"""Wiki knowledge passage assembly for the chat runtime (KNOWLEDGE_BACKEND=wiki).

One call per retrieve_context: recall the wiki (lexical + vector + graph) and
render the passages into one prompt-ready text block. Failures are absorbed —
the wiki layer must never break the chat path (degrades to no block, planner
runs exactly as before).

Store invalidation: the process-local store rebuilds when the configured
directory list changes OR any page file's mtime changes — page edits take
effect without a process restart. Rebuild is parse+index only (milliseconds
for hundreds of pages); embeddings stay on their own fingerprint cache.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from common.core.config import settings
from common.utils.utils import SQLBotLogUtil

_STORE: Any = None
_STORE_DIRS: tuple[Path, ...] = ()
_STORE_STAMP: tuple[int, ...] = ()
_STORE_ERROR: str = ""
_STORE_INDEX: Any = None  # WikiEmbeddingIndex —— 随 store 同生命周期缓存（V2）
_STAMP_CHECKED_AT: float | None = None  # 上次 mtime 探测时刻（单调钟）
_EMBEDDING_BUILT: int = 0  # ensure() 触发构建的次数（遥测：embedding_built）


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


# ── 相关性过滤（chat 168：RRF 分不是相似度，无法表达"相关/无关"）──────────
# 向量 cosine 绝对下限：与表召回 EMBEDDING_TABLE_SIMILARITY 同数量级；
# 词法 coverage 下限：稀疏通道，弱命中页只有同时向量也弱才丢弃。
# graph 邻居（图扩展份额）不再进 prompt 段——它们的价值是锚点闭包（表
# 并入 schema），正文对规划是噪音（chat 168：0.0008 分邻居页占 prompt）。
WIKI_MIN_VECTOR_SCORE = 0.28
WIKI_MIN_LEXICAL_SCORE = 0.30


def _relevance_keep(passage: Any, *, source: str) -> bool:
    """business 模式的相关性下限（physical 不滤——物理修复靠全量锚点）。"""
    if source == "graph":
        return False
    vector_score = float(getattr(passage, "vector_score", 0.0) or 0.0)
    lexical_score = float(getattr(passage, "lexical_score", 0.0) or 0.0)
    if vector_score >= WIKI_MIN_VECTOR_SCORE:
        return True
    return lexical_score >= WIKI_MIN_LEXICAL_SCORE


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


def _dirs_stamp(dirs: tuple[Path, ...]) -> tuple[int, ...]:
    """(mtime_ns, size) per page file, sorted — cheap freshness probe."""
    stamp: list[tuple[int, int]] = []
    for directory in dirs:
        for path in sorted(directory.rglob("*.md")):
            if path.name.startswith("_"):
                continue
            try:
                stat = path.stat()
                stamp.append((stat.st_mtime_ns, stat.st_size))
            except OSError:
                continue
    return tuple(sorted(stamp))


_STAMP_INTERVAL_SEC = 5.0  # mtime 探测降频：热路径多次 _store() 共享一次探测


def _store() -> Any | None:
    """Lazy process-local store over ``KNOWLEDGE_WIKI_PAGES_DIRS``（冒号分隔，
    子目录=type 路由）。目录串或任一页面 mtime/size 变化即重建。
    WikiEmbeddingIndex 随同一生命周期缓存（_STORE_INDEX）：嵌入 ensure() 一次
    进程内生效，页面编辑经 mtime stamp 失效连带重建——避免每请求重 ensure。
    语料根目录作为 ``_pages_root`` 附在 store 上（db catalog 推导用）。

    热路径上一次请求会有 3+ 个 ``_store()`` 调用点（recall 短路/表列集/
    枚举映射），全目录 stat 每次约 10ms——mtime 探测按
    ``_STAMP_INTERVAL_SEC`` 降频共享，页面编辑最迟一个间隔后生效。"""
    global _STORE
    global _STORE_DIRS
    global _STORE_STAMP
    global _STORE_ERROR
    global _STORE_INDEX
    global _STAMP_CHECKED_AT
    dirs = tuple(
        Path(d) for d in settings.knowledge_wiki_pages_dirs_abs.split(":") if d.strip()
    )
    if not dirs:
        return None
    now = time.monotonic()
    if _STORE is not None and _STORE_DIRS == dirs:
        if (
            _STAMP_CHECKED_AT is not None
            and now - _STAMP_CHECKED_AT < _STAMP_INTERVAL_SEC
        ):
            return _STORE  # 探测窗口内共享上次结果
        stamp = _dirs_stamp(dirs)
        _STAMP_CHECKED_AT = now
        if _STORE_STAMP == stamp:
            return _STORE
    else:
        stamp = _dirs_stamp(dirs)
        _STAMP_CHECKED_AT = now
    try:
        from apps.knowledge.wiki.contract import parse_page
        from apps.knowledge.wiki.recall import InMemoryWikiStore

        pages = []
        for directory in dirs:
            for path in sorted(directory.rglob("*.md")):
                if path.name.startswith("_"):
                    continue
                pages.append(parse_page(path.read_text(), page_key=path.stem))
        _STORE = InMemoryWikiStore(pages)
        _STORE._pages_root = dirs[0] if dirs else None  # schema 渲染推导 db catalog 用
        _STORE_DIRS = dirs
        _STORE_STAMP = stamp
        _STORE_INDEX = None  # 新 store → 旧 index 向量键失效，强制重建
        _STORE_ERROR = ""
        SQLBotLogUtil.info("wiki store loaded: %s pages from %s", len(pages), dirs)
        return _STORE
    except Exception as exc:
        _STORE_ERROR = str(exc)
        SQLBotLogUtil.warning("wiki store load failed: %s", exc)
        return None


def _embedding_index(store: Any) -> Any | None:
    """进程内复用 WikiEmbeddingIndex（store 生命周期一致）。不可用/关闭 → None。

    ensure 的构建计数经模块级 _EMBEDDING_BUILT 透出（遥测采集点）。"""
    global _STORE_INDEX, _EMBEDDING_BUILT
    if not settings.KNOWLEDGE_WIKI_EMBEDDING_ENABLED:
        return None
    if _STORE_INDEX is None and _STORE is not None:
        from apps.knowledge.wiki.embeddings import WikiEmbeddingIndex

        _STORE_INDEX = WikiEmbeddingIndex(
            store, cache_dir=_STORE_DIRS[0].parent if _STORE_DIRS else None
        )
    if _STORE_INDEX is not None and not _STORE_INDEX.ensured:
        before = _STORE_INDEX.build_count
        if _STORE_INDEX.ensure():
            _EMBEDDING_BUILT += _STORE_INDEX.build_count - before
    return _STORE_INDEX


def _recall_passages(
    query: str,
    *,
    ds_id: int | None,
    databases: list[str] | None = None,
    mode: str,
    top_k: int | None = None,
    trace_out: dict[str, Any] | None = None,
) -> list[Any] | None:
    """recall 的公共执行体（返回 RenderedPassage 列表；不可用/失败 = None）。

    ``databases`` = 当前数据源的物理库名（scope.databases 围栏输入）；
    ``ds_id`` 仅用于 allowlist 灰度判定。
    ``trace_out`` 透传给 recall 填充各阶段中间量（召回过程可观测）。"""
    if not _ds_allowlisted(ds_id):
        return None
    store = _store()
    if store is None:
        return None
    try:
        from apps.knowledge.wiki.recall import recall

        effective_top_k = top_k or int(settings.KNOWLEDGE_WIKI_RECALL_TOP_K)
        index = _embedding_index(store)
        embedder = None
        if index is not None:
            # 向量超采到全量 chunk（chat 168 回归：30 窗口把大表页的全部
            # chunk 挤出候选，页级聚合拿不到向量分 → 相关性过滤误杀主表）。
            # 矩阵点积全量 ~600ms/3672 chunk，一次查询无页级损失。
            embedder = lambda store_, query_: index.query_scores(query_)  # noqa: E731
        return recall(
            query,
            store,
            oid=1,
            databases=databases or [],
            top_k=effective_top_k,
            mode=mode,
            embedder=embedder,
            trace_out=trace_out,
        )
    except Exception as exc:
        SQLBotLogUtil.warning("wiki %s recall failed (degraded): %s", mode, exc)
        return None


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
    business 模式做相关性下限过滤：向量 cosine < WIKI_MIN_VECTOR_SCORE 且
    词法 coverage < WIKI_MIN_LEXICAL_SCORE 的页不进 prompt（hits 里保留
    并标 filtered=true，执行详情可见被滤原因）；graph 邻居正文不进 prompt
    （其锚点仍通过 page_keys 参与闭包）。physical 模式不过滤。"""
    started = time.monotonic()
    built_before = _EMBEDDING_BUILT
    trace: dict[str, Any] = {}
    passages = _recall_passages(
        query,
        ds_id=ds_id,
        databases=databases,
        mode=mode,
        top_k=top_k,
        trace_out=trace,
    )
    if not passages:
        return None
    if mode == "business":
        kept = [p for p in passages if _relevance_keep(p, source=str(p.source))]
    else:
        kept = passages
    kept_keys = {str(p.page_key) for p in kept}
    text = "\n\n".join(p.text for p in kept)
    if not text.strip():
        # 全被滤掉 → 召回视为无产出（与 passages 空同形）
        return None
    return WikiRecallResult(
        text=text,
        hits=_hit_projection(
            passages, kept_keys=kept_keys if mode == "business" else None
        ),
        page_keys=[str(p.page_key) for p in passages],
        elapsed_ms=int((time.monotonic() - started) * 1000),
        embedding_built=_EMBEDDING_BUILT > built_before,
        # 完整渲染文本按序保留（执行详情展开视图；不进 prompt 的页不含）
        passages={str(p.page_key): str(p.text or "") for p in kept},
        trace=trace,
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
    store = _store()
    if store is None:
        return None
    if not _strong_alias_hit(concept, store):
        return None
    return _recall_result(
        concept, ds_id=ds_id, databases=databases, mode="physical", top_k=top_k
    )


def enum_maps_for(
    field_refs: list[str], *, ds_id: int | None
) -> dict[str, dict[str, str]]:
    """查询结果枚举翻译映射（P3）：``{表.列: {VALUE: label}}``。

    输入 = 查询引用的物理字段（plan_facts 提取）；映射来自权威枚举页的
    ground:enum（强证据归并后的 value→label）。仅返回命中字段的映射，
    wiki 后端关闭或无枚举绑定时返回空 dict（零行为变化）。
    解析直接消费 parse_page 产出的 ``GroundAnchor.data``（与
    WikiSchemaRenderer._enum_label_map 单一真相），不再正则重解析。"""
    if not wiki_backend_active(ds_id):
        return {}
    store = _store()
    if store is None or not field_refs:
        return {}
    try:
        wanted = {str(r).strip() for r in field_refs if r}
        maps: dict[str, dict[str, str]] = {}
        for page in store.pages.values():
            if page.type != "enum":
                continue
            for anchor in page.ground_blocks or ():
                if anchor.kind != "enum":
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


# ── Unified Wiki Context Retrieval Service ─────────────────────────────────

def retrieve_wiki_context(
    llm_service: Any,
    query: str,
    *,
    access_scope: Any = None,
    top_k: int = 5,
) -> dict[str, Any]:
    """Unified service for retrieving Wiki knowledge and authoritative schema.

    Single entrypoint for both initialization (prepare_turn) and runtime tools (search_wiki):
    1. If Wiki is active for datasource: recalls wiki knowledge + anchor closure schema.
    2. Fallback only if Wiki is inactive: transparently retrieves schema without exposing
       schema tool to LLM.
    """
    clean_query = str(query or "").strip()
    if not clean_query:
        return {
            "knowledge_text": "",
            "tables": [],
            "schema_text": "",
            "backend": "none",
            "page_keys": [],
            "hit_count": 0,
        }
    ds = getattr(llm_service, "ds", None)
    ds_id = getattr(ds, "id", None)

    # 1. Wiki Active Branch (Primary SSOT)
    if wiki_backend_active(ds_id):
        try:
            databases = datasource_databases(ds)
            res = wiki_recall(clean_query, ds_id=ds_id, databases=databases, top_k=top_k)
            wiki_text = (res.text if res else "") or ""
            tables: list[str] = []

            store = _store()
            if store is not None and res and getattr(res, "page_keys", None):
                from apps.knowledge.wiki.anchors import closure_tables
                from apps.chat.steps.wiki_schema import WikiSchemaRenderer

                closure, _ = closure_tables(store, res.page_keys)
                if closure:
                    tables = list(closure)
                    renderer = WikiSchemaRenderer.from_store(store)
                    if renderer:
                        raw_schema = renderer.render(tables)
                        compact_lines = [
                            line for line in raw_schema.splitlines()
                            if line.startswith("## ") or "topk=" in line or any(
                                k in line for k in ["Id", "时间", "状态", "名称", "类型", "方式", "来源", "编码", "金额", "部门", "日期"]
                            )
                        ]
                        header = "\n\n### 【权威表结构与字段定义（已完整提供，严禁重复查表结构）】：\n"
                        wiki_text += header + "\n".join(compact_lines)

            return {
                "knowledge_text": wiki_text,
                "tables": tables,
                "schema_text": "",
                "backend": "wiki",
                "page_keys": list(getattr(res, "page_keys", None) or []) if res else [],
                "hit_count": len(getattr(res, "hits", None) or []) if res else 0,
            }
        except Exception as exc:
            SQLBotLogUtil.warning(f"retrieve_wiki_context failed in wiki branch: {exc}")

    # 2. Transparent Fallback (Only when Wiki is inactive or unconfigured for datasource)
    try:
        from apps.chat.steps.schema import match_table_schema
        from apps.conversation.session import session_scope

        schema_text = ""
        matched_tables: list[str] = []
        with session_scope() as session:
            # Temporarily set retrieval_question to user query if needed
            orig_q = getattr(llm_service, "retrieval_question", None)
            setattr(llm_service, "retrieval_question", clean_query)
            try:
                matched_tables = list(
                    match_table_schema(
                        llm_service,
                        session,
                        access_scope=access_scope,
                        table_limit=4,
                        audit=False,
                    ) or []
                )
                schema_text = str(getattr(llm_service.chat_question, "db_schema", "") or "")
            finally:
                if orig_q is not None:
                    setattr(llm_service, "retrieval_question", orig_q)

        return {
            "knowledge_text": "",
            "tables": matched_tables,
            "schema_text": schema_text,
            "backend": "schema_fallback",
            "page_keys": [],
            "hit_count": len(matched_tables),
        }
    except Exception as exc:
        SQLBotLogUtil.warning(f"retrieve_wiki_context failed in fallback branch: {exc}")
        return {
            "knowledge_text": "",
            "tables": [],
            "schema_text": "",
            "backend": "error",
            "page_keys": [],
            "hit_count": 0,
        }
