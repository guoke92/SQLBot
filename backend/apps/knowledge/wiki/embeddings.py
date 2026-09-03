"""Wiki chunk embeddings with per-page revision cache (Spec C vector channel V2).

对齐 llm-wiki page_embedding.rs 的增量思想：
- 增量粒度 = **chunk 文本指纹**（而非整页内容哈希）：嵌入输入是
  ``heading_path + chunk.text``，缓存键就对这两个东西做哈希——enrich 类
  "改正文但 chunk 文本不变"的编辑（补 wikilink/行数注释/frontmatter）零重嵌；
  新增/修改的 chunk 单独重嵌。每页 revision = 各 chunk 指纹的聚合（有序拼接
  后哈希，保留 chunk 顺序敏感性：顺序变 = 全页重嵌）。
- 缓存 = 单索引文件（embeddings-cache/embeddings-{model}-{dim}.json）内 per-page
  条目 {revision, chunks: {chunk_hash: {cid, vector}}}；整体原子写
  （temp+rename）+ 进程锁双检。
- ensure() 失败 → 进程级 60s 冷却（与 EmbeddingModelCache.embed_query 熔断同模式），
  期间直接 False 不触网——模型挂掉时不再每请求全库重试。
- ensure() 构建统计（build_count/ensured）透出给召回层做 retrieval span 观测。
- 余弦走 numpy 矩阵一次算（3500×1536 ≈ 21MB），替代逐对循环。

Embedding failure returns None/False everywhere — recall silently degrades to
lexical-only（与 llm-wiki 同一降级契约，不变）。
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import threading
import time
from pathlib import Path
from typing import Any

from apps.knowledge.wiki.rec import cosine as _cosine_impl
from apps.knowledge.wiki.recall import InMemoryWikiStore
from common.core.config import settings
from common.utils.utils import SQLBotLogUtil

_CACHE_DIR_NAME = "embeddings-cache"
_BUILD_COOLDOWN_SEC = 60.0
_EMBED_BATCH = 32

_build_lock = threading.Lock()
_build_unavailable_until = 0.0


def chunk_text(page_key: str, chunk: Any) -> str:  # noqa: ARG001 — page_key 预留调用方上下文
    """chunk 的嵌入输入文本（与 embed_documents 消费严格一致——单一真相）。"""
    heading = getattr(chunk, "heading_path", "") or ""
    body = getattr(chunk, "text", "") or ""
    return f"{heading}\n{body}" if heading else body


def chunk_fingerprint(text: str, model_key: str, dimension: int) -> str:
    """单个 chunk 的缓存键：嵌入输入文本哈希（文本变才重嵌）。"""
    material = f"{model_key}:{dimension}:{text}"
    return hashlib.sha256(material.encode()).hexdigest()


def page_revision(
    page_content: str, model_key: str, dimension: int, *, chunks: Any = None
) -> str:
    """页 revision：chunk 级指纹聚合（有 chunks 时），整页哈希兜底。

    chunk 文本不变（enrich 改 frontmatter/无关散文）→ 各指纹不变 → revision
    命中零重嵌；chunk 顺序变化（增删节）→ 拼接串变 → 全页重嵌。向后兼容：
    不传 chunks 退回整页内容哈希（tests 与外部调用点保持可用）。"""
    if chunks is None:
        material = f"{model_key}:{dimension}:{page_content}"
        return hashlib.sha256(material.encode()).hexdigest()
    parts = [
        chunk_fingerprint(chunk_text("", chunk), model_key, dimension)
        for chunk in chunks
    ]
    material = f"{model_key}:{dimension}:" + "|".join(parts)
    return hashlib.sha256(material.encode()).hexdigest()


def _cache_path(cache_dir: Path, model_key: str, dimension: int) -> Path:
    slug = "".join(c if c.isalnum() else "-" for c in model_key)[:40]
    return cache_dir / _CACHE_DIR_NAME / f"embeddings-{slug}-{dimension}.json"


def _load_index(path: Path) -> dict:
    try:
        if path.exists():
            data = json.loads(path.read_text())
            if isinstance(data, dict) and isinstance(data.get("pages"), dict):
                return data
    except (json.JSONDecodeError, OSError):
        pass
    return {}


def _atomic_write(path: Path, data: dict) -> None:
    """temp+rename 原子写；并发下最后写者胜（单 DS 规模可接受）。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as fh:
            json.dump(data, fh)
        os.replace(tmp, path)
    except OSError:
        try:
            os.unlink(tmp)
        except OSError:
            pass


def _cosine(a: list[float], b: list[float]) -> float:
    return _cosine_impl(a, b)


def _query_top(scores: dict[str, float], top_k: int | None) -> dict[str, float]:
    if not top_k:
        return scores
    ranked = sorted(scores.items(), key=lambda item: -item[1])[:top_k]
    return dict(ranked)


class WikiEmbeddingIndex:
    """Chunk-level vector index over an in-memory wiki store (lazy + incremental)."""

    def __init__(
        self,
        store: InMemoryWikiStore,
        *,
        cache_dir: Path | None = None,
    ) -> None:
        self.store = store
        self.cache_dir = cache_dir or Path(".")
        self._vectors: dict[str, list[float]] | None = None
        self._matrix: Any = None  # 预归一化 numpy 矩阵(chunk 顺序对齐 _vector_ids)
        self._vector_ids: list[str] | None = None
        self._available: bool | None = None
        self.build_count = 0  # 累计 embed_documents 调用次数（遥测）
        self.built_pages = 0  # 累计触发重嵌的页数（遥测）

    @property
    def ensured(self) -> bool:
        """ensure 是否已成功完成（True 后 recall 不再触碰该路径）。"""
        return self._available is True

    # ── ensure：chunk 级指纹 diff → 只嵌未命中 chunk ─────────────────────────

    def ensure(self) -> bool:
        """Build/load chunk vectors. Returns False when embeddings are
        unavailable (disabled/model failure/cooldown) — callers degrade
        gracefully. Incremental: chunks whose fingerprint matches the cache
        are reused verbatim; only new/changed chunk texts hit the embedding
        endpoint (enrich-style page edits that leave chunk texts untouched
        cost zero remote calls)."""
        global _build_unavailable_until
        if self._available is not None:
            return self._available
        if not settings.EMBEDDING_ENABLED:
            self._available = False
            return False
        with _build_lock:
            if time.monotonic() < _build_unavailable_until:
                self._available = False
                return False
            try:
                from apps.ai_model.embedding import EmbeddingModelCache

                model = EmbeddingModelCache.get_model()
                model_key = settings.DEFAULT_EMBEDDING_MODEL
                dimension = EmbeddingModelCache.get_dimension()
            except Exception as exc:
                SQLBotLogUtil.warning("wiki embedding init failed: %s", exc)
                self._available = False
                return False

            cache_path = _cache_path(self.cache_dir, model_key, dimension)
            index = _load_index(cache_path)
            cached_pages: dict[str, dict] = index.get("pages") or {}
            merged: dict[str, list[float]] = {}
            pending: list[tuple[str, int, str]] = []  # (key, chunk_index, text)
            pending_pages: dict[str, dict] = {}  # key → 新页条目（复用未变 chunk）
            for key, chunks in self.store.chunks.items():
                texts = [chunk_text(key, chunk) for chunk in chunks]
                revision = page_revision(
                    self.store.pages[key].body, model_key, dimension, chunks=chunks
                )
                entry = cached_pages.get(key)
                if entry and entry.get("revision") == revision:
                    page_vectors = entry.get("vectors")
                    if page_vectors:
                        # 旧格式（页级 vectors 字段）
                        merged.update(page_vectors)
                    else:
                        # chunk 级格式：向量在 chunks[指纹].vector（chat 168 回归：
                        # 快路径只读 vectors 键，557 个新格式页的向量全部丢失，
                        # 向量通道静默失效）。指纹键重算回 chunk_id。
                        for text in texts:
                            fp = chunk_fingerprint(text, model_key, dimension)
                            cached = (entry.get("chunks") or {}).get(fp)
                            if cached is not None:
                                merged[cached["cid"]] = list(cached["vector"])
                    continue
                # 页 revision 不匹配 → chunk 级 diff：指纹命中的 chunk 复用，
                # 只有指纹变化的 chunk 进嵌入队列
                cached_chunks: dict[str, dict] = (
                    entry.get("chunks") or {} if isinstance(entry, dict) else {}
                )
                page_entry: dict[str, Any] = {"revision": revision, "chunks": {}}
                if isinstance(entry, dict) and entry.get("vectors"):
                    # 旧格式迁移（vectors 无 chunk 指纹）→ 全页重嵌一次
                    pending.extend((key, i, text) for i, text in enumerate(texts))
                else:
                    for i, text in enumerate(texts):
                        fp = chunk_fingerprint(text, model_key, dimension)
                        cached = cached_chunks.get(fp)
                        if cached is not None:
                            merged[cached["cid"]] = list(cached["vector"])
                            page_entry["chunks"][fp] = cached
                        else:
                            pending.append((key, i, text))
                pending_pages[key] = page_entry

            if pending:
                try:
                    for start in range(0, len(pending), _EMBED_BATCH):
                        batch = pending[start : start + _EMBED_BATCH]
                        embeddings = model.embed_documents(
                            [text for _key, _i, text in batch]
                        )
                        self.build_count += 1
                        for (key, chunk_index, _text), vector in zip(
                            batch, embeddings, strict=False
                        ):
                            cid = f"{key}#{chunk_index}"
                            merged[cid] = [float(x) for x in vector]
                    # 重建页条目（含复用 chunk 与新嵌入 chunk 的完整指纹表）
                    for key, page_entry in pending_pages.items():
                        texts = [chunk_text(key, c) for c in self.store.chunks[key]]
                        for i, text in enumerate(texts):
                            fp = chunk_fingerprint(text, model_key, dimension)
                            if fp in page_entry["chunks"]:
                                continue
                            page_entry["chunks"][fp] = {
                                "cid": f"{key}#{i}",
                                "vector": merged[f"{key}#{i}"],
                            }
                        page_entry.pop("vectors", None)
                        index.setdefault("pages", {})[key] = page_entry
                        self.built_pages += 1
                    index["model"] = model_key
                    index["dim"] = dimension
                    _atomic_write(cache_path, index)
                    SQLBotLogUtil.info(
                        "wiki embeddings built: %s chunks across %s pages "
                        "(%s embed calls, cache reused)",
                        len(pending),
                        len(pending_pages),
                        self.build_count,
                    )
                except Exception as exc:
                    SQLBotLogUtil.warning("wiki embedding build failed: %s", exc)
                    _build_unavailable_until = time.monotonic() + _BUILD_COOLDOWN_SEC
                    self._available = False
                    return False

            self._vectors = merged
            self._matrix = None  # 向量集变化 → 矩阵重建
            self._vector_ids = None
            self._available = True
            return True

    # ── query ────────────────────────────────────────────────────────────────

    def query_scores(
        self, query: str, *, top_k: int | None = None
    ) -> dict[str, float] | None:
        """Query → {chunk_id: cosine}（recall 的 vector_scores 形态）。不可用→None。"""
        if not self.ensure():
            return None
        try:
            from apps.ai_model.embedding import EmbeddingModelCache

            query_vector = EmbeddingModelCache.embed_query(query)
        except Exception as exc:
            SQLBotLogUtil.warning("wiki query embedding failed: %s", exc)
            return None
        return self._query_top_matrix(query_vector, top_k)

    def _query_top_matrix(self, query_vector: list[float], top_k: int | None):
        """numpy 预归一化矩阵点积一次算全部余弦;numpy 不可用回退逐 chunk。

        docstring 承诺的"矩阵一次算"落到实处:2000×1536 纯 Python 循环
        ~250ms,矩阵化 ~5ms(实测)。归一化在矩阵构建时做一次,查询侧
        只归一化查询向量。"""
        vectors = self._vectors or {}
        if not vectors:
            return {}
        try:
            import numpy as np

            if self._matrix is None or self._vector_ids is None:
                ids = list(vectors.keys())
                mat = np.asarray([vectors[cid] for cid in ids], dtype=np.float32)
                norms = np.linalg.norm(mat, axis=1, keepdims=True)
                norms[norms == 0.0] = 1.0
                self._matrix = mat / norms
                self._vector_ids = ids
            qv = np.asarray(query_vector, dtype=np.float32)
            qnorm = float(np.linalg.norm(qv))
            if qnorm == 0.0:
                return {}
            qv = qv / qnorm
            scores = self._matrix @ qv
            ranked = sorted(
                zip(self._vector_ids, scores.tolist(), strict=False),
                key=lambda item: -item[1],
            )
            return dict(ranked[:top_k] if top_k else ranked)
        except ImportError:
            scored = {
                cid: _cosine(query_vector, vector) for cid, vector in vectors.items()
            }
            return _query_top(scored, top_k)


def vector_channel(
    store: InMemoryWikiStore, query: str, *, cache_dir: Path | None = None
) -> dict[str, float] | None:
    """Convenience: vector_scores for ``recall(vector_scores=…)`` or None."""
    return WikiEmbeddingIndex(store, cache_dir=cache_dir).query_scores(query)
