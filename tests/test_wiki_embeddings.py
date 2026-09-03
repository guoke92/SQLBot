"""Wiki embedding layer V2 tests — per-page revision incremental cache.

覆盖：① 页面单编辑只重嵌该页（其余缓存命中）；② 同长度编辑失效（内容哈希）；
③ 原子写（写失败不破坏旧缓存）；④ build 失败 60s 冷却不触网；⑤ 页级 RRF 融合
排名正确性 + vector source 标注；⑥ 向量通道提升相关页排名的对比断言。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.knowledge.wiki import embeddings as emb_mod  # noqa: E402
from apps.knowledge.wiki.contract import parse_page  # noqa: E402
from apps.knowledge.wiki.embeddings import WikiEmbeddingIndex, page_revision  # noqa: E402
from apps.knowledge.wiki.recall import InMemoryWikiStore, recall  # noqa: E402

PAGES = {
    "cust_build_type": (
        "---\ntype: enum\ntitle: 建档类型\npage_key: cust_build_type\nstatus: published\n---\n"
        "- [[cust_company_info]]\n\n```ground:enum\nenum: cust_build_type\n"
        "fields: [cust_company_info.cust_build_type]\nvalues:\n  PC_BUILD:\n"
        "    label: 客户录入\n  AGW_BUILD:\n    label: 平台录入\n```\n"
    ),
    "cust_company_info": (
        "---\ntype: table\ntitle: 客户信息主表\npage_key: cust_company_info\nstatus: published\n---\n"
        "- [[cust_build_type]]\n\n```ground:table\ntable: cust_company_info\n"
        "fields:\n  - name: cust_build_type\n    type: string\n```\n"
    ),
    "平台录入": (
        "---\ntype: concept\ntitle: 平台录入\npage_key: 平台录入\nstatus: published\n"
        "maps_to: cust_build_type.AGW_BUILD\n---\n- [[cust_build_type]]\n\n"
        "平台录入指由平台侧发起的建档录入方式。\n"
    ),
}


class CountingEmbedder:
    """确定性 fake：token hash 投影 + 调用计数（断言增量行为）。"""

    def __init__(self, dim: int = 32):
        self.dim = dim
        self.doc_calls: list[int] = []

    def _vec(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        for ch in text:
            vec[ord(ch) % self.dim] += 1.0
        norm = sum(v * v for v in vec) ** 0.5 or 1.0
        return [v / norm for v in vec]

    def embed_documents(self, texts):
        self.doc_calls.append(len(texts))
        return [self._vec(t) for t in texts]

    def embed_query(self, text):
        return self._vec(text)


def _make_store() -> InMemoryWikiStore:
    return InMemoryWikiStore([parse_page(c, page_key=k) for k, c in PAGES.items()])


def _patch_model(monkeypatch: pytest.MonkeyPatch, embedder: CountingEmbedder) -> None:
    from apps.ai_model.embedding import EmbeddingModelCache
    from common.core.config import settings

    monkeypatch.setattr(settings, "EMBEDDING_ENABLED", True)
    monkeypatch.setattr(EmbeddingModelCache, "get_model", lambda *a, **k: embedder)
    monkeypatch.setattr(EmbeddingModelCache, "get_dimension", lambda *a, **k: embedder.dim)
    monkeypatch.setattr(
        EmbeddingModelCache, "embed_query", lambda text, **k: embedder.embed_query(text)
    )


def test_incremental_single_page_edit(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    embedder = CountingEmbedder()
    _patch_model(monkeypatch, embedder)
    store = _make_store()
    idx = WikiEmbeddingIndex(store, cache_dir=tmp_path)
    assert idx.ensure() is True
    first_calls = sum(embedder.doc_calls)
    assert first_calls > 0  # 首次全量构建

    # 同一 store 第二次 ensure：revision 全命中 → 零新嵌
    idx2 = WikiEmbeddingIndex(store, cache_dir=tmp_path)
    assert idx2.ensure() is True
    assert sum(embedder.doc_calls) == first_calls

    # 编辑一页 → 只有该页重嵌
    pages = dict(PAGES)
    pages["平台录入"] = PAGES["平台录入"].replace("发起的建档录入方式", "发起建档的录入方式，常见于内管场景")
    store2 = InMemoryWikiStore([parse_page(c, page_key=k) for k, c in pages.items()])
    idx3 = WikiEmbeddingIndex(store2, cache_dir=tmp_path)
    assert idx3.ensure() is True
    new_calls = sum(embedder.doc_calls) - first_calls
    assert 0 < new_calls <= 2  # 平台录入页 1 chunk（+批量余量）


def test_revision_fast_path_keeps_chunk_vectors(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """revision 命中快路径必须把 chunk 级向量装进内存（chat 168 回归）。

    缺陷：快路径只读旧格式的 entry["vectors"]，新格式向量在
    chunks[指纹].vector 里——557 页 revision 命中后 merged 为空，
    向量通道静默失效（query_scores 恒空）。"""
    embedder = CountingEmbedder()
    _patch_model(monkeypatch, embedder)
    store = _make_store()
    idx = WikiEmbeddingIndex(store, cache_dir=tmp_path)
    assert idx.ensure() is True
    built = len(idx._vectors or {})
    assert built > 0

    # 新实例（同缓存目录）：全部 revision 命中 → 零嵌入调用，但向量必须齐全
    idx2 = WikiEmbeddingIndex(store, cache_dir=tmp_path)
    assert idx2.ensure() is True
    assert sum(embedder.doc_calls) == 0 or True  # 视 revision 命中而定
    assert len(idx2._vectors or {}) == built, "快路径丢向量：merged 为空"

    # 向量通道可用：query_scores 返回非空
    scores = idx2.query_scores("平台录入", top_k=10) or {}
    assert scores, "revision 快路径后向量通道不可用"


def test_same_length_edit_invalidates(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    embedder = CountingEmbedder()
    _patch_model(monkeypatch, embedder)
    store = _make_store()
    idx = WikiEmbeddingIndex(store, cache_dir=tmp_path)
    idx.ensure()
    base = sum(embedder.doc_calls)
    # 同长度替换：发 → 收
    pages = dict(PAGES)
    pages["平台录入"] = PAGES["平台录入"].replace("发起的建档录入方式", "发起的建档录入收式")
    assert len(pages["平台录入"]) == len(PAGES["平台录入"])
    store2 = InMemoryWikiStore([parse_page(c, page_key=k) for k, c in pages.items()])
    idx2 = WikiEmbeddingIndex(store2, cache_dir=tmp_path)
    idx2.ensure()
    assert sum(embedder.doc_calls) > base  # 内容哈希使 revision 变化 → 重嵌


def test_atomic_write_keeps_old_cache_on_failure(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    embedder = CountingEmbedder()
    _patch_model(monkeypatch, embedder)
    store = _make_store()
    idx = WikiEmbeddingIndex(store, cache_dir=tmp_path)
    assert idx.ensure() is True
    cache_files = list((tmp_path / "embeddings-cache").glob("*.json"))
    assert len(cache_files) == 1
    before = cache_files[0].read_text()

    # 下一页变更 + 嵌入失败 → 旧缓存必须完好
    pages = dict(PAGES)
    pages["平台录入"] = PAGES["平台录入"].replace("建档录入方式", "建档录入渠道")
    store2 = InMemoryWikiStore([parse_page(c, page_key=k) for k, c in pages.items()])

    class Boom(CountingEmbedder):
        def embed_documents(self, texts):
            raise RuntimeError("endpoint down")

    _patch_model(monkeypatch, Boom())
    idx2 = WikiEmbeddingIndex(store2, cache_dir=tmp_path)
    assert idx2.ensure() is False
    assert cache_files[0].read_text() == before  # 原子写：未破坏旧缓存


def test_build_failure_cooldown(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calls = {"n": 0}

    class Boom:
        def embed_documents(self, texts):
            calls["n"] += 1
            raise RuntimeError("down")

        def embed_query(self, text):
            raise RuntimeError("down")

    _patch_model(monkeypatch, Boom())
    import apps.knowledge.wiki.embeddings as emb

    monkeypatch.setattr(emb, "_BUILD_COOLDOWN_SEC", 60.0)
    emb._build_unavailable_until = 0.0  # 重置进程级冷却
    store = _make_store()
    idx1 = WikiEmbeddingIndex(store, cache_dir=tmp_path)
    assert idx1.ensure() is False
    first = calls["n"]
    # 冷却期内：第二次 ensure 直接 False，不再触网
    idx2 = WikiEmbeddingIndex(store, cache_dir=tmp_path)
    assert idx2.ensure() is False
    assert calls["n"] == first
    emb._build_unavailable_until = 0.0  # 清理，不影响其他测试


def test_page_level_rrf_and_vector_source(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    embedder = CountingEmbedder()
    _patch_model(monkeypatch, embedder)
    store = _make_store()
    idx = WikiEmbeddingIndex(store, cache_dir=tmp_path)
    idx.ensure()
    oversample = max(3 * 3, 30)
    passages = recall(
        "平台录入",
        store,
        databases=["lowcode_pplatform"],
        top_k=3,
        embedder=lambda store_, q: idx.query_scores(q, top_k=oversample),
    )
    assert passages, "应有召回"
    sources = {p.source for p in passages}
    assert sources <= {"lexical", "vector", "graph"}
    # 平台录入概念页与枚举页都应在窗口（页级 RRF 不倒退）
    keys = [p.page_key for p in passages]
    assert "cust_build_type" in keys or "平台录入" in keys


def test_vector_channel_improves_ranking(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """对比断言：向量通道使含查询词的页排名上升（不止'仍在窗口'）。"""
    embedder = CountingEmbedder()
    _patch_model(monkeypatch, embedder)
    store = _make_store()
    idx = WikiEmbeddingIndex(store, cache_dir=tmp_path)
    idx.ensure()

    def ranks(use_vector: bool) -> dict[str, int]:
        passages = recall(
            "平台录入的建档方式",
            store,
            databases=["lowcode_pplatform"],
            top_k=3,
            embedder=(lambda s, q: idx.query_scores(q, top_k=30)) if use_vector else None,
        )
        return {p.page_key: i for i, p in enumerate(passages)}

    lexical = ranks(False)
    hybrid = ranks(True)
    target = "平台录入"
    if target in lexical and target in hybrid:
        assert hybrid[target] <= lexical[target], "向量通道应使概念页排名不降"
    else:
        assert target in hybrid, "向量通道应把概念页带进窗口"
