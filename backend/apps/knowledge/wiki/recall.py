"""Wiki recall: RRF fusion + page aggregation + graph-expansion quota.

Spec: docs/wiki-knowledge/wiki召回接口-v1.md. Pipeline ported from verified
llm-wiki search.rs: oversample → RRF fuse channels → page aggregation →
one-hop wikilink expansion with a dynamic retention quota. Vector channel is
pluggable; when absent the pipeline silently degrades to lexical-only (the
same degradation contract llm-wiki keeps when embeddings fail).
"""

from __future__ import annotations

import math
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from apps.knowledge.wiki.chunker import Chunk, chunk_markdown
from apps.knowledge.wiki.contract import WikiPage, parse_page
from apps.knowledge.wiki.graph import build_graph

_MAX_GRAPH_SEEDS = 20
_MAX_GRAPH_RATIO = 0.30
_MIN_GRAPH_RATIO = 0.15
_RRF_K = 60
_MIN_TOKEN = 2
# 通道权重（页级 RRF）：词法 1.0 / 向量 1.2——业务词→物理键场景向量是强补充
# 信号但噪声高于精确别名命中；eval 达标即停，不做自动调参。
_LEXICAL_WEIGHT = 1.0
_VECTOR_WEIGHT = 1.2
# table 页侧重（P2 schema wiki 化）：business 模式给表页小幅倾斜
_TABLE_PAGE_BONUS = 0.05
# business 模式单页正文摘要上限（剔除围栏后的散文）；0 = 不截断
_DEFAULT_PROSE_CHARS = 400

_CJK_RUN_RE = re.compile(r"[\u4e00-\u9fff]+")
_ASCII_WORD_RE = re.compile(r"[a-zA-Z0-9_]+")


def tokenize(text: str) -> set[str]:
    """CJK bigrams + full CJK runs + ASCII words (llm-wiki's CJK-bigram idea)."""
    tokens: set[str] = set()
    lowered = text.lower()
    for word in _ASCII_WORD_RE.findall(lowered):
        tokens.add(word)
    for run in _CJK_RUN_RE.findall(text):
        tokens.add(run)
        if len(run) > 1:
            tokens.update(run[i : i + 2] for i in range(len(run) - 1))
    return tokens


@dataclass(frozen=True)
class RenderedPassage:
    page_key: str
    title: str
    score: float
    source: Literal["lexical", "graph", "vector"]
    related_to: tuple[str, ...]
    text: str
    # 原始通道信号（过滤决策依据；RRF 融合分 score 不是相似度，
    # 无法表达"相关/无关"——chat 168：0.10 与 0.07 只差两个排名位）
    vector_score: float = 0.0  # 该页最好 chunk 的向量 cosine（无向量=0）
    lexical_score: float = 0.0  # 词法 coverage 通道原始分


class InMemoryWikiStore:
    """Process-local page store: chunks + alias map + adjacency, zero DB."""

    def __init__(self, pages: list[WikiPage]) -> None:
        self.pages: dict[str, WikiPage] = {page.page_key: page for page in pages}
        self.chunks: dict[str, list[Chunk]] = {
            page.page_key: chunk_markdown(page.body) for page in pages
        }
        self.adjacency, self.alias_map = build_graph(self.pages)
        # alias-exact 索引：别名/标题（含枚举值 label）作为查询子串的强命中通道
        self.alias_index: dict[str, str] = {}
        for key, page in self.pages.items():
            for name in page.identity_aliases:
                cleaned = name.strip()
                if len(cleaned) >= _MIN_TOKEN and cleaned not in self.alias_index:
                    self.alias_index[cleaned] = key
        # chunk token cache + document frequency（coverage 的 IDF 加权底座）：
        # 表页字段注释词汇广，任何查询都能蹭到高频 bigram——不降权会淹没
        # 稀有而精准的枚举值/别名命中。键=chunk_id（与 _lexical_channels 的
        # 取用键一致；曾经按 page_key 键导致缓存永不命中、每次全量重 tokenize）。
        self.chunk_tokens: dict[str, set[str]] = {
            f"{key}#{index}": tokenize(chunk.text)
            for key, chunks_ in self.chunks.items()
            for index, chunk in enumerate(chunks_)
        }
        total = max(1, sum(len(v) for v in self.chunk_tokens.values()))
        df: dict[str, int] = {}
        for tokens in self.chunk_tokens.values():
            for tok in tokens:
                df[tok] = df.get(tok, 0) + 1
        self.idf: dict[str, float] = {
            tok: math.log(1.0 + total / count) for tok, count in df.items()
        }

    @classmethod
    def load(cls, contents: list[str]) -> InMemoryWikiStore:
        return cls([parse_page(content) for content in contents])

    @classmethod
    def load_dir(cls, root: Path) -> InMemoryWikiStore:
        """加载页面目录（双面架构接缝：管理面写 git 目录，运行面直接消费）。
        子目录=type 路由（tables/enums/concepts/…），必须 rglob——平面 glob
        在子目录结构下会漏掉全部页面。`_` 前缀文件（_index.md 等）非内容页。"""
        pages = [
            parse_page(p.read_text(), page_key=p.stem)
            for p in sorted(root.rglob("*.md"))
            if not p.name.startswith("_")
        ]
        return cls(pages)

    def _fenced(
        self, page: WikiPage, *, databases: list[str] | tuple[str, ...]
    ) -> bool:
        """围栏：published only + 物理库名交集（scope.databases）。
        页面未声明（空）= 不限——数据源是知识来源，不是使用限制。"""
        if page.status != "published":
            return False
        return not page.databases or bool(
            set(page.databases) & {str(name).strip().lower() for name in databases}
        )


def _lexical_channels(
    query: str,
    chunks: Mapping[str, list[Chunk]],
    *,
    idf: Mapping[str, float] | None = None,
    chunk_tokens: Mapping[str, set[str]] | None = None,
) -> list[dict[str, float]]:
    """Two lexical channels: exact-run containment + IDF-weighted coverage.

    ``runs`` are the query's ORIGINAL consecutive CJK runs — bigrams belong
    to the coverage channel. Mixing them into the exact channel floods RRF
    with 2-char tie hits that drown true phrase matches. Coverage is
    IDF-weighted: 表页字段注释词汇广，任何查询都能蹭到高频 bigram——
    不降权会淹没枚举值/别名等稀有而精准的命中."""
    query_tokens = tokenize(query)
    runs = sorted(
        (run for run in _CJK_RUN_RE.findall(query) if len(run) >= _MIN_TOKEN),
        key=len,
        reverse=True,
    )
    words = {t for t in query_tokens if _ASCII_WORD_RE.fullmatch(t)}
    denom = sum((idf or {}).get(tok, 1.0) for tok in query_tokens)
    exact: dict[str, float] = {}
    coverage: dict[str, float] = {}
    for key, page_chunks in chunks.items():
        for index, chunk in enumerate(page_chunks):
            cid = f"{key}#{index}"
            lowered = chunk.text.lower()
            best_run = max(
                (len(run) for run in runs if run in lowered or run in chunk.text),
                default=0,
            )
            if best_run:
                exact[cid] = max(exact.get(cid, 0.0), float(best_run))
            c_tokens = (chunk_tokens or {}).get(cid) or tokenize(chunk.text)
            if denom > 0:
                weighted = sum(
                    (idf or {}).get(tok, 1.0) for tok in query_tokens & set(c_tokens)
                )
                if weighted > 0:
                    coverage[cid] = weighted / denom
            if words and any(word in lowered for word in words):
                exact[cid] = max(exact.get(cid, 0.0), 2.0)
    return [exact, coverage]


def _alias_hits(query: str, store: InMemoryWikiStore) -> dict[str, float]:
    """别名/值标签 ⊂ 查询 的页级强命中（确定性，"值⊂文本"哲学的页面版）。

    枚举值 label（如"平台录入"）作为查询子串出现时，其权威页必须进窗口——
    这是 F1（枚举映射）失败模式的正解。RRF 是排名融合，稀疏强信号通道
    在其中与 74 项 coverage 通道等权会被稀释——所以走**页级分数加成**
    而非通道融合。

    别名最短 3 字符：加成幅度（min(2.0, len/4)）比页级 RRF 主分（≈0.02）
    大 25~100 倍，2 字别名（"状态"/"编号"）作为查询子串几乎必中，会把
    无关页无条件顶进窗口挤掉真命中。"""
    scores: dict[str, float] = {}
    for alias, page_key in store.alias_index.items():
        if len(alias) >= 3 and alias in query:
            scores[page_key] = max(scores.get(page_key, 0.0), float(len(alias)))
    return scores


def _rrf_chunk_scores(channels: list[dict[str, float]]) -> dict[str, float]:
    scores: dict[str, float] = {}
    for channel in channels:
        ranked = sorted(channel.items(), key=lambda item: -item[1])
        for rank, (cid, _score) in enumerate(ranked):
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (_RRF_K + rank)
    return scores


def _rrf_page_scores(
    page_rankings: list[tuple[dict[str, float], float]],
) -> dict[str, float]:
    """页级 RRF：每个通道给出 {page_key: 分}（或页级排名聚合结果），按分降序
    取页级排名，`score = Σ weight_c / (60 + rank_c)`。向量通道页级排名进 RRF
    （对齐 llm-wiki search.rs apply_rrf_scores），替代此前 chunk 级排名稀释。"""
    scores: dict[str, float] = {}
    for channel, weight in page_rankings:
        ranked = sorted(channel.items(), key=lambda item: -item[1])
        for rank, (page_key, _score) in enumerate(ranked):
            scores[page_key] = scores.get(page_key, 0.0) + weight / (_RRF_K + rank)
    return scores


def _aggregate_pages(chunk_scores: Mapping[str, float]) -> dict[str, float]:
    pages: dict[str, list[float]] = {}
    for cid, score in chunk_scores.items():
        page_key = cid.rsplit("#", 1)[0]
        pages.setdefault(page_key, []).append(score)
    aggregated: dict[str, float] = {}
    for page_key, scores in pages.items():
        ordered = sorted(scores, reverse=True)
        top = ordered[0]
        tail = sum(ordered[1:])
        aggregated[page_key] = top + min(0.3 * tail, 1.0 - top)
    return aggregated


def _graph_quota(limit: int, vector_hits: int) -> int:
    """图扩展份额：向量通道对**最终窗口**的覆盖越高越保守。

    ``vector_hits`` 必须传页级窗口内的向量命中数（≤limit），而不是 chunk
    级超采命中数——后者在向量通道开启时恒为 top_k*3，会把 coverage 锁死
    在 1.0，图扩展被实质禁用（回归：2026-09 走读发现）。"""
    if limit < 2:
        return 0
    coverage = min(vector_hits, limit) / limit
    ratio = _MAX_GRAPH_RATIO - (_MAX_GRAPH_RATIO - _MIN_GRAPH_RATIO) * coverage
    return max(1, min(int(limit * ratio + 0.999), limit - 1))


def _prose_summary(page: WikiPage, *, max_chars: int) -> str:
    """页面正文摘要：剔除 ground 围栏与「关联表」节后的散文（按页封顶）。

    business 模式的核心变化：表结构由 WikiSchemaRenderer 在 schema 段权威
    渲染（含枚举 label 内联/关系行），passage 不再重复字段清单——这里只
    承载 schema 给不了的「业务表述/口径散文」。枚举 values 块保留（翻译
    与澄清的依据）。"""
    lines: list[str] = []
    in_fence = False
    in_relations = False
    for line in page.body.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if stripped == "## 关联表":
            in_relations = True
            continue
        if in_relations and stripped.startswith("## "):
            in_relations = False
        if in_relations:
            continue
        if not stripped:
            continue
        lines.append(line)
    text = "\n".join(lines).strip()
    if len(text) > max_chars:
        text = text[:max_chars].rstrip() + "…"
    return text


def _enum_values_block(page: WikiPage) -> str:
    """ground:enum 的 values 块原样（value: label 逐行，翻译/澄清依据）。"""
    for anchor in page.ground_blocks:
        if anchor.kind != "enum":
            continue
        values = anchor.data.get("values") or {}
        if not values:
            return ""
        lines = ["```ground:enum", f"enum: {anchor.data.get('enum', '')}"]
        for value, meta in values.items():
            label = (
                str((meta or {}).get("label") or value)
                if isinstance(meta, dict)
                else str(meta or value)
            )
            lines.append(f"  {value}: {label}")
        lines.append("```")
        return "\n".join(lines)
    return ""


def _render(  # noqa: PLR0911
    page: WikiPage,
    chunk: Chunk,
    *,
    source_note: str = "",
    mode: Literal["business", "physical"] = "business",
    prose_chars: int | None = None,
) -> str:
    header = f"# {page.title}"
    if page.aliases:
        header += f"\n（别名: {'、'.join(page.aliases)}）"
    # frontmatter 结构锚点随文本下发（concept 页无 ground 块，maps_to 是术语桥本体）
    if page.maps_to:
        header += f"\n（术语锚点: {page.title} → {page.maps_to}）"
    elif page.field_targets:
        header += f"\n（字段锚点: {'、'.join(page.field_targets)}）"
    if page.anchors:
        header += f"\n（表锚点: {'、'.join(page.anchors)}）"
    if source_note:
        header += f"\n（{source_note}）"

    if mode == "business":
        # business 模式：正文摘要 + 枚举 values（去 ground:table 字段清单——
        # schema 段由 WikiSchemaRenderer 权威渲染，重复字段纯耗 token）
        from common.core.config import settings

        effective_prose = (
            prose_chars
            if prose_chars is not None
            else int(getattr(settings, "KNOWLEDGE_WIKI_PROSE_CHARS", 0) or 0)
            or _DEFAULT_PROSE_CHARS
        )
        parts = [header]
        prose = _prose_summary(page, max_chars=effective_prose)
        if prose:
            parts.append(prose)
        enum_block = _enum_values_block(page)
        if enum_block:
            parts.append(enum_block)
        return "\n\n".join(parts)

    body = chunk.text
    has_anchor = "```ground:" in body
    if not has_anchor:
        for candidate in chunk_markdown(page.body):
            if "```ground:" in candidate.text:
                body = f"{body}\n\n{candidate.text}"
                break
    return f"{header}\n\n{body}"


def recall(
    query: str,
    store: InMemoryWikiStore,
    *,
    databases: list[str] | None = None,
    oid: int = 1,  # noqa: ARG001 — V0 no-op, multi-tenant deferred to phase 2
    top_k: int = 8,
    mode: Literal["business", "physical"] = "business",
    vector_scores: Mapping[str, float] | None = None,
    embedder: Any = None,
    trace_out: dict[str, Any] | None = None,
) -> list[RenderedPassage]:
    """Recall rendered passages (Spec C). Deterministic; no LLM.

    ``vector_scores`` 显式注入；或传 ``embedder``（WikiEmbeddingIndex 工厂）
    由内部生成向量通道——嵌入不可用时静默降级纯词法。
    ``trace_out`` 非空时填充各阶段中间量（召回过程可观测：可见页数 →
    各通道 chunk 命中 → 页融合 top → 图扩展份额），供执行详情展示。"""
    names = [str(name) for name in (databases or []) if str(name).strip()]
    visible = {
        key: page
        for key, page in store.pages.items()
        if store._fenced(page, databases=names)
    }
    if not visible or not query.strip():
        return []

    visible_chunks = {key: store.chunks[key] for key in visible}
    if vector_scores is None and embedder is not None:
        try:
            vector_scores = embedder(store, query)
        except Exception:  # noqa: BLE001 — 嵌入失败静默降级纯词法
            vector_scores = None
    if vector_scores:
        # AccessScope 围栏对向量通道同样生效：过滤后仅保留可见页的 chunk 分。
        vector_scores = {
            cid: score
            for cid, score in vector_scores.items()
            if cid.rsplit("#", 1)[0] in visible
        }
        if not vector_scores:
            vector_scores = None
    channels = _lexical_channels(
        query,
        visible_chunks,
        idf=store.idf,
        chunk_tokens=store.chunk_tokens,
    )
    if vector_scores:
        channels.append(dict(vector_scores))
    chunk_scores = _rrf_chunk_scores(channels)
    page_scores = _aggregate_pages(chunk_scores)
    # 词法-only 窗口（不含向量通道）——source 标注的"边际贡献"基线：
    # 最终窗口里有、词法窗口里没有的页 = 向量通道带进来的。
    lexical_only_scores = _aggregate_pages(_rrf_chunk_scores(channels[:2]))
    lexical_window = {
        pk
        for pk, _s in sorted(
            lexical_only_scores.items(), key=lambda item: (-item[1], item[0])
        )[:top_k]
    }
    # 向量页级排名进 RRF（对齐 llm-wiki）：向量超采 chunk → 页面聚合 → 页级
    # 排名单独一份，带权重融合；页在向量排名中的位置用于 source 标注。
    vector_page_scores: dict[str, float] = {}
    if vector_scores:
        vector_page_scores = _aggregate_pages(vector_scores)
    if vector_page_scores:
        lexical_page_scores = {
            k: v for k, v in page_scores.items() if k not in vector_page_scores
        }
        fused = _rrf_page_scores(
            [
                (page_scores, _LEXICAL_WEIGHT),
                (vector_page_scores, _VECTOR_WEIGHT),
            ]
        )
        page_scores = {
            **fused,
            **{k: v for k, v in lexical_page_scores.items() if k not in fused},
        }
    # alias-exact 页级加成：枚举值 label/别名作为查询子串 = 精确语义锚点，
    # 强度按命中长度（封顶 2.0），叠在 RRF 聚合分之上。
    for page_key, alias_score in _alias_hits(query, store).items():
        if page_key in visible:
            page_scores[page_key] = page_scores.get(page_key, 0.0) + min(
                2.0, alias_score / 4.0
            )
    # table 页侧重加成（P2）：table 页是 schema 权威承载（phys/topk/dict 齐备），
    # business 模式下让 working-set 相关的表页更容易进窗口——与 alias 加成同
    # 机制，幅度小（0.05/RRF 份额）只做同分近似时的倾斜。
    if mode == "business":
        for page_key in visible:
            if visible[page_key].type == "table":
                page_scores[page_key] = (
                    page_scores.get(page_key, 0.0) + _TABLE_PAGE_BONUS
                )
    ranked = sorted(page_scores.items(), key=lambda item: (-item[1], item[0]))[:top_k]

    passages: list[RenderedPassage] = []
    direct_keys: set[str] = set()
    seed_ranks: dict[str, int] = {}
    for rank, (page_key, score) in enumerate(ranked):
        direct_keys.add(page_key)
        seed_ranks[page_key] = rank
        page = visible[page_key]
        page_chunk_ids = [cid for cid in chunk_scores if cid.startswith(f"{page_key}#")]
        # 表页加成可把零词法命中的表页推进窗口（schema 权威呈现职责）——
        # 该页可能没有任何 chunk 分，回退首 chunk。
        best_cid = (
            max(page_chunk_ids, key=lambda cid: chunk_scores[cid])
            if page_chunk_ids
            else f"{page_key}#0"
        )
        best_index = int(best_cid.rsplit("#", 1)[1])
        # source 标注（边际贡献口径）：词法-only 窗口外的页 = 向量通道带进来的。
        source = "lexical" if page_key in lexical_window else "vector"
        # 原始通道信号（绝对阈值过滤用）：向量 cosine 取该页最好 chunk；
        # 词法取 coverage 通道（channels[1]，exact 命中是稀疏强信号单独透出无意义）
        page_vector = 0.0
        if vector_scores:
            page_vector = max(
                (
                    float(s)
                    for cid, s in vector_scores.items()
                    if cid.startswith(f"{page_key}#")
                ),
                default=0.0,
            )
        lexical_raw = 0.0
        if len(channels) >= 2:
            lexical_raw = max(
                (
                    float(s)
                    for cid, s in channels[1].items()
                    if cid.startswith(f"{page_key}#")
                ),
                default=0.0,
            )
        passages.append(
            RenderedPassage(
                page_key=page_key,
                title=page.title,
                score=round(score, 6),
                source=source,
                related_to=(),
                text=_render(page, visible_chunks[page_key][best_index], mode=mode),
                vector_score=round(page_vector, 6),
                lexical_score=round(lexical_raw, 6),
            )
        )

    if mode == "physical" or not store.adjacency:
        _fill_trace(
            trace_out,
            visible=visible,
            channels=channels,
            vector_scores=vector_scores,
            page_scores=page_scores,
            ranked=ranked,
            quota=0,
            neighbors=[],
            mode=mode,
        )
        return passages

    # 页级口径: 最终窗口(direct hits)中有多少页是向量通道带进来的
    vector_hits = sum(1 for p in passages if p.source == "vector")
    quota = _graph_quota(top_k, vector_hits)
    neighbor_scores: dict[str, float] = {}
    neighbor_seeds: dict[str, set[str]] = {}
    for seed_key in sorted(seed_ranks, key=seed_ranks.get):  # type: ignore[arg-type]
        for neighbor in store.adjacency.get(seed_key, ()):
            if neighbor in direct_keys or neighbor not in visible:
                continue
            neighbor_scores[neighbor] = neighbor_scores.get(neighbor, 0.0) + 1.0 / (
                _RRF_K + seed_ranks[seed_key]
            )
            neighbor_seeds.setdefault(neighbor, set()).add(seed_key)
    ordered_neighbors = sorted(
        neighbor_scores.items(), key=lambda item: (-item[1], item[0])
    )
    for page_key, nscore in ordered_neighbors[:quota]:
        page = visible[page_key]
        seeds = tuple(
            sorted(neighbor_seeds[page_key], key=lambda s: seed_ranks.get(s, 999))
        )
        # 邻居页被注入是为了它的锚点块（关系/枚举/口径）——取首个含 ground
        # 围栏的 chunk；无锚点块才回退首块（散文导语）。
        neighbor_chunks = store.chunks[page_key]
        anchor_chunk = next(
            (c for c in neighbor_chunks if "```ground:" in c.text), neighbor_chunks[0]
        )
        passages.append(
            RenderedPassage(
                page_key=page_key,
                title=page.title,
                score=round(nscore / (_RRF_K + 1), 6),
                source="graph",
                related_to=seeds,
                text=_render(
                    page,
                    anchor_chunk,
                    source_note=f"图近邻: {'、'.join(seeds)}",
                    mode=mode,
                ),
            )
        )
    _fill_trace(
        trace_out,
        visible=visible,
        channels=channels,
        vector_scores=vector_scores,
        page_scores=page_scores,
        ranked=ranked,
        quota=quota,
        neighbors=[(k, round(v, 4)) for k, v in ordered_neighbors[: quota + 2]],
        mode=mode,
    )
    return passages


def _fill_trace(
    trace_out: dict[str, Any] | None,
    *,
    visible: dict[str, Any],
    channels: list[dict[str, float]],
    vector_scores: Mapping[str, float] | None,
    page_scores: dict[str, float],
    ranked: list[tuple[str, float]],
    quota: int,
    neighbors: list[tuple[str, float]],
    mode: str,
) -> None:
    """召回各阶段中间量 → trace_out（执行详情"召回过程"卡片的数据源）。

    只读已有计算结果，零额外查询；每通道只留 top5 页（chunk 数给全量）。
    """
    if trace_out is None:
        return

    def _channel_top(channel: dict[str, float]) -> list[dict[str, Any]]:
        pages: dict[str, float] = {}
        for cid, score in channel.items():
            pk = cid.rsplit("#", 1)[0]
            pages[pk] = max(pages.get(pk, 0.0), float(score))
        return [
            {"page_key": pk, "score": round(s, 4)}
            for pk, s in sorted(pages.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
        ]

    trace_out["mode"] = mode
    trace_out["visible_pages"] = len(visible)
    trace_out["channels"] = {
        "lexical_exact": {
            "chunks": len(channels[0]) if len(channels) > 0 else 0,
            "top": _channel_top(channels[0]) if len(channels) > 0 else [],
        },
        "lexical_coverage": {
            "chunks": len(channels[1]) if len(channels) > 1 else 0,
            "top": _channel_top(channels[1]) if len(channels) > 1 else [],
        },
        "vector": {
            "chunks": len(vector_scores or {}),
            "top": _channel_top(dict(vector_scores or {})),
        },
    }
    trace_out["page_fusion"] = [
        {"page_key": pk, "score": round(s, 4)}
        for pk, s in sorted(page_scores.items(), key=lambda kv: (-kv[1], kv[0]))[:top_5]
    ]
    trace_out["window"] = [{"page_key": pk, "score": round(s, 4)} for pk, s in ranked]
    trace_out["graph_quota"] = quota
    trace_out["graph_neighbors"] = [{"page_key": pk, "score": s} for pk, s in neighbors]


top_5 = 5  # trace 里每通道/融合只留 top5（可读性优先，完整清单在 hits）
