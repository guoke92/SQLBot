"""Wiki subsystem regression tests — v0 contract (docs/wiki页面契约-spec-v0.md).

Fixture corpus = docs/wiki-knowledge/examples/（159 病例场景，双实现共享
fixture 的 Python 侧种子，v0 §7.1）。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.knowledge.wiki.chunker import chunk_markdown  # noqa: E402
from apps.knowledge.wiki.contract import (  # noqa: E402
    Finding,
    PageContractError,
    lint_page,
    parse_page,
)
from apps.knowledge.wiki.recall import InMemoryWikiStore, recall  # noqa: E402

EXAMPLES = _ROOT / "docs" / "wiki-knowledge" / "examples"

# v0 对账底稿（Spec B 的 catalog 基线，测试形态）
CATALOG = {
    "tables": {
        "cust_company_info": {
            "fields": {
                "id": {"family": "number"},
                "cust_build_type": {"family": "string"},
                "identify_style": {"family": "string"},
                "cust_build_status": {"family": "string"},
                "cust_status": {"family": "string"},
                "data_type": {"family": "string"},
                "enable": {"family": "string"},
            },
        },
        "cust_company_detail": {"fields": {"company_id": {"family": "number"}}},
    },
    "dicts": {
        "cust_build_type": ["PC_BUILD", "AGW_BUILD"],
        "identify_style": ["INVITE", "INVITE_AGW", "SELF"],
    },
}


def _corpus(*, scoped: bool = False) -> list[str]:
    pages = [p.read_text() for p in sorted(EXAMPLES.glob("*.md"))]
    if scoped:  # 每页声明物理库名（页面级 scope.databases 围栏）
        return [
            page.replace(
                'contract_version: "0.1"',
                'contract_version: "0.1"\nscope:\n  databases: [lowcode_pplatform]',
            )
            for page in pages
        ]
    return pages


def _load_store() -> InMemoryWikiStore:
    return InMemoryWikiStore.load(_corpus())


# ── 契约解析（v0 语法与身份规则） ─────────────────────────────────────────────


def test_parse_v0_corpus_identity_rules() -> None:
    pages = {p.page_key: p for p in (parse_page(c) for c in _corpus())}
    assert set(pages) == {
        "cust_company_info",
        "cust_build_type",
        "identify_style",
        "平台录入",
        "企业建档流程",
        "有效企业",
    }
    # 物理身份：表/枚举页 slug = 物理名
    table = pages["cust_company_info"]
    assert table.type == "table" and table.anchors == ("cust_company_info",)
    enum_page = pages["cust_build_type"]
    assert enum_page.ground_blocks[0].data["fields"] == [
        "cust_company_info.cust_build_type"
    ]
    # 概念页：CJK slug + 术语桥（maps_to + adjudication，159 病灶的对症结构）
    concept = pages["平台录入"]
    assert concept.maps_to == "cust_build_type.AGW_BUILD"
    assert concept.adjudication == "boundary"
    assert "认证方式" in concept.also_confused_with
    # process 块的 transitions 带初始态
    proc = pages["企业建档流程"]
    transitions = proc.ground_blocks[0].data["stages"][0]["transitions"]
    assert transitions[0]["from"] is None and transitions[0]["to"] == "CREATED"


def test_v0_slug_rules_and_status_enum() -> None:
    ok = "---\ntype: concept\ntitle: t\npage_key: 平台录入\nstatus: published\n---\n- [[x]]\n"
    parse_page(ok)  # CJK 业务 slug 合法
    with pytest.raises(PageContractError):
        parse_page(
            "---\ntype: table\ntitle: t\npage_key: cust-company-info\nstatus: published\n---\n- [[x]]\n"
        )  # 表页必须物理名 snake
    with pytest.raises(PageContractError):
        parse_page(
            "---\ntype: concept\ntitle: t\npage_key: 平台录入\nstatus: draftx\n---\n- [[x]]\n"
        )


def test_unknown_ground_kind_warn_and_ignore() -> None:
    page = parse_page(
        "---\ntype: concept\ntitle: t\npage_key: 概念\nstatus: published\n---\n"
        "- [[x]]\n\n```ground:tensor\nshape: [3]\n```\n"
    )
    assert page.unknown_ground_kinds == ("tensor",)
    assert page.ground_blocks == ()
    codes = {f.code for f in lint_page(page, known_keys={"x"})}
    assert "UNKNOWN_GROUND_KIND" in codes


def test_scenario_ground_kind_is_accepted() -> None:
    page = parse_page(
        "---\ntype: scenario\ntitle: 建档\npage_key: company_build\n"
        "status: draft\n---\n- [[cust_company_info]]\n\n"
        "```ground:scenario\nscenario: company_build\nhubs:\n"
        "- table: cust_company_info\n  window: [id, data_type]\n```\n"
    )
    assert page.unknown_ground_kinds == ()
    assert any(block.kind == "scenario" for block in page.ground_blocks)


def test_scope_databases_parse_and_legacy_finding() -> None:
    """scope.databases 围栏：新形态解析 + 旧 ds_id 形态记 LEGACY_SCOPE 不静默兼容。"""
    new = parse_page(
        "---\ntype: rule\ntitle: t\npage_key: r1\nstatus: published\n"
        "scope:\n  databases: [LowCode_PPlatform]\n---\n- [[x]]\n"
    )
    assert new.databases == ("lowcode_pplatform",)  # fold 小写
    assert not any(f.code == "LEGACY_SCOPE" for f in new.parse_findings)

    legacy = parse_page(
        "---\ntype: rule\ntitle: t\npage_key: r2\nstatus: published\n"
        "scope:\n  datasources: [15]\n---\n- [[x]]\n"
    )
    assert legacy.databases == ()  # 旧值不静默采纳（防 ds_id 变"空=不限"）
    assert any(f.code == "LEGACY_SCOPE" for f in legacy.parse_findings)

    flat = parse_page(
        "---\ntype: rule\ntitle: t\npage_key: r3\nstatus: published\n"
        "datasources: [15]\n---\n- [[x]]\n"
    )
    assert flat.databases == ()
    assert any(f.code == "LEGACY_SCOPE" for f in flat.parse_findings)


# ── Lint 码表（v0 §6 子集） ──────────────────────────────────────────────────


def test_lint_catalog_violations() -> None:
    page = parse_page(
        "---\ntype: table\ntitle: t\npage_key: ghost_table\ndomain: d\nstatus: published\n---\n"
        "- [[x]]\n\n```ground:table\ntable: ghost_table\nfields:\n"
        "  - name: nope\n    data_type: int\n```\n"
    )
    codes = {f.code for f in lint_page(page, known_keys={"x"}, catalog=CATALOG)}
    assert "TABLE_NOT_IN_CATALOG" in codes


def test_lint_field_and_family_and_enum_baseline() -> None:
    page = parse_page(
        "---\ntype: table\ntitle: t\npage_key: cust_company_info\ndomain: d\nstatus: published\n---\n"
        "- [[x]]\n\n```ground:table\ntable: cust_company_info\nfields:\n"
        "  - name: nope\n    data_type: string\n"
        "  - name: cust_build_type\n    data_type: int\n```\n"
    )
    codes = {f.code for f in lint_page(page, known_keys={"x"}, catalog=CATALOG)}
    assert "FIELD_NOT_IN_CATALOG" in codes
    assert "TYPE_FAMILY_MISMATCH" in codes

    enum_page = parse_page(
        "---\ntype: dict\ntitle: e\npage_key: cust_build_type\ndomain: d\nstatus: published\n---\n"
        "- [[x]]\n\n```ground:dict\ndict: cust_build_type\nfields: [cust_company_info.cust_build_type]\n"
        "values:\n  PC_BUILD: {label: 平台录入}\n  GHOST: {label: 幻觉值}\n```\n"
    )
    codes = {f.code for f in lint_page(enum_page, known_keys={"x"}, catalog=CATALOG)}
    assert "DICT_NOT_IN_BASELINE" in codes  # catalog 胜，转 review


def test_lint_relation_tenant_endpoint_and_term_adjudication() -> None:
    page = parse_page(
        "---\ntype: table\ntitle: t\npage_key: cust_company_info\ndomain: d\nstatus: published\n---\n"
        "- [[x]]\n\n```ground:relation\ntype: EQUI_JOIN\nleft: cust_company_info.tenant_id\n"
        "right: cust_company_detail.company_id\ncardinality: many_to_one\n```\n"
    )
    codes = {f.code for f in lint_page(page, known_keys={"x"}, catalog=CATALOG)}
    assert "TENANT_FIELD_AS_ENDPOINT" in codes

    unjudged = parse_page(
        "---\ntype: concept\ntitle: c\npage_key: 概念\nstatus: published\n"
        "field_targets: [cust_company_info.cust_build_type]\n"
        "also_confused_with: [认证方式]\n---\n- [[x]]\n"
    )
    codes = {f.code for f in lint_page(unjudged, known_keys={"x"}, catalog=CATALOG)}
    assert "TERM_UNADJUDICATED" in codes
    assert "CONCEPT_UNANCHORED" not in codes  # 有 field_targets


def test_lint_duplicate_block_ref_target_and_orphan() -> None:
    page = parse_page(
        "---\ntype: dict\ntitle: e\npage_key: cust_build_type\ndomain: d\nstatus: published\n"
        "field_targets: [cust_company_info.nope]\n---\n- [[x]]\n\n"
        "```ground:dict\ndict: cust_build_type\nvalues:\n  PC_BUILD: {label: 平台录入}\n```\n\n"
        "```ground:dict\ndict: cust_build_type\nvalues:\n  PC_BUILD: {label: 平台录入}\n```\n"
    )
    codes = {f.code for f in lint_page(page, known_keys={"x"}, catalog=CATALOG)}
    assert "DUPLICATE_GROUND_BLOCK" in codes
    assert "REF_TARGET_MISSING" in codes

    orphan = parse_page(
        "---\ntype: concept\ntitle: 孤\npage_key: 孤页\nstatus: published\n"
        "field_targets: [cust_company_info.id]\n---\n正文无出链。\n"
    )
    assert "NO_OUTLINKS" in {
        f.code for f in lint_page(orphan, known_keys=set(), catalog=CATALOG)
    }
    assert Finding("x", "y").code == "x"


# ── 切块（v0 围栏原子性） ─────────────────────────────────────────────────────


def test_ground_fence_is_atomic_chunk() -> None:
    content = (_ROOT / "docs/wiki-knowledge/examples/cust_build_type.md").read_text()
    page = parse_page(content)
    chunks = chunk_markdown(page.body)
    anchor_chunks = [c for c in chunks if "```ground:dict" in c.text]
    assert len(anchor_chunks) == 1
    assert "PC_BUILD" in anchor_chunks[0].text


# ── 召回（159 场景） ──────────────────────────────────────────────────────────


def test_recall_159_scene_maps_platform_entry_to_agw_build() -> None:
    store = _load_store()
    query = "提取25年6月之前认证方式是平台录入 建档的企业清单"
    passages = recall(query, store, oid=1, databases=["lowcode_pplatform"], top_k=5)

    keys = [p.page_key for p in passages]
    assert "cust_build_type" in keys  # AGW_BUILD=平台录入 的权威枚举页
    assert "平台录入" in keys  # 术语桥页（CJK slug）
    assert "identify_style" in keys  # 易混淆字段页同时呈给规划器
    build = next(p for p in passages if p.page_key == "cust_build_type")
    assert "PC_BUILD" in build.text and "平台录入" in build.text
    assert "客户录入" in build.text  # PC_BUILD 的源码真值 label（语义反转修正）
    concept = next(p for p in passages if p.page_key == "平台录入")
    assert "cust_build_type.AGW_BUILD" in concept.text or "AGW_BUILD" in concept.text


def test_recall_graph_expansion_injects_neighbor_with_quota() -> None:
    store = _load_store()
    passages = recall(
        "认证方式有哪些", store, oid=1, databases=["lowcode_pplatform"], top_k=3
    )
    graph_hits = [p for p in passages if p.source == "graph"]
    assert graph_hits, "图扩展应注入链路邻居"
    assert all(p.related_to for p in graph_hits)


def test_recall_fencing_and_physical_mode() -> None:
    corpus = _corpus()
    table_src = next(c for c in corpus if "page_key: cust_company_info" in c)
    draft = parse_page(
        table_src.replace("status: published", "status: draft").replace(
            "page_key: cust_company_info", "page_key: draft_ghost"
        )
    )
    store = InMemoryWikiStore([parse_page(c) for c in corpus] + [draft])
    query = "平台录入"
    trace: dict = {}
    passages = recall(
        "cust_company_info",
        store,
        oid=1,
        databases=["lowcode_pplatform"],
        top_k=8,
        trace_out=trace,
    )
    gated_tables = [str(k) for k in (trace.get("gated_table_pages") or [])]
    assert any(p.page_key == "draft_ghost" for p in passages) or any(
        "draft_ghost" in key for key in gated_tables
    )  # draft 暂入召回（表页进候选，不占语义窗）
    retired = parse_page(
        table_src.replace("status: published", "status: retired").replace(
            "page_key: cust_company_info", "page_key: retired_ghost"
        )
    )
    store_retired = InMemoryWikiStore(list(store.pages.values()) + [retired])
    retired_hits = recall(
        "cust_company_info",
        store_retired,
        oid=1,
        databases=["lowcode_pplatform"],
        top_k=8,
    )
    assert all(p.page_key != "retired_ghost" for p in retired_hits)
    # 页面级 scope 声明围栏：声明库名的语料对其他库不可见
    scoped_store = InMemoryWikiStore.load(_corpus(scoped=True))
    assert recall(query, scoped_store, oid=1, databases=["other_db"], top_k=3) == []
    physical = recall(
        query, store, oid=1, databases=["lowcode_pplatform"], top_k=3, mode="physical"
    )
    assert all(p.source == "lexical" for p in physical)  # physical 无图注入


# ── v0 §0.1 零信任：坏 YAML 丢块+警告（页面散文保留），而非杀整页 ────────────────


def test_broken_yaml_drops_block_with_finding_keeps_prose() -> None:
    content = (
        "---\ntype: dict\ntitle: e\npage_key: cust_build_type\ndomain: d\nstatus: published\n---\n"
        "- [[x]]\n\n散文区保留：平台录入=AGW_BUILD 的正文说明不应被连坐丢弃。\n\n"
        "```ground:dict\ndict: cust_build_type\nvalues:\n  PC_BUILD: [未闭合的yaml\n```\n"
    )
    page = parse_page(content)  # 不 raise —— v0 §0.1 丢块+警告
    assert page.ground_blocks == ()  # 坏块被丢弃
    assert "平台录入=AGW_BUILD" in page.body  # 散文保留
    codes = {f.code for f in lint_page(page, known_keys={"x"}, catalog=CATALOG)}
    assert "GROUND_PARSE_FAILED" in codes  # 警告进 REVIEW 队列


def test_unclosed_fence_is_structural_raise() -> None:
    with pytest.raises(PageContractError):
        parse_page(
            "---\ntype: dict\ntitle: e\npage_key: cust_build_type\nstatus: published\n---\n"
            "- [[x]]\n\n```ground:dict\ndict: x\n"
        )


def test_store_load_dir_seam() -> None:
    """双面架构接缝：llm_wiki 管理面写目录，运行面 load_dir 直接消费."""
    store = InMemoryWikiStore.load_dir(EXAMPLES)
    assert store.get_page("cust_build_type") is not None
    assert store.get_page("平台录入") is not None
    passages = recall(
        "提取25年6月之前认证方式是平台录入 建档的企业清单",
        store,
        oid=1,
        databases=["lowcode_pplatform"],
        top_k=4,
    )
    keys = [p.page_key for p in passages]
    assert "cust_build_type" in keys and "平台录入" in keys


# ── P2：向量通道与运行时开关 ─────────────────────────────────────────────────


class _FakeEmbedder:
    """确定性 fake：token hash 投影，"平台录入"查询与含该词 chunk 天然相似。"""

    def __init__(self, dim: int = 32):
        self.dim = dim

    def _vec(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        for ch in text:
            vec[ord(ch) % self.dim] += 1.0
        norm = sum(v * v for v in vec) ** 0.5 or 1.0
        return [v / norm for v in vec]

    def embed_documents(self, texts):
        return [self._vec(t) for t in texts]

    def embed_query(self, text):
        return self._vec(text)


def test_vector_channel_improves_enum_page_ranking(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from apps.ai_model.embedding import EmbeddingModelCache
    from apps.knowledge.wiki.embeddings import vector_channel
    from common.core.config import settings

    # 测试封闭：嵌入走确定性 fake（不触网、不受全局失败熔断污染）
    fake = _FakeEmbedder()
    monkeypatch.setattr(settings, "EMBEDDING_ENABLED", True)
    monkeypatch.setattr(EmbeddingModelCache, "get_model", lambda *a, **k: fake)
    monkeypatch.setattr(EmbeddingModelCache, "get_dimension", lambda *a, **k: fake.dim)
    monkeypatch.setattr(
        EmbeddingModelCache, "embed_query", lambda text, **k: fake.embed_query(text)
    )

    store = _load_store()
    query = "平台录入的企业清单"
    vector_scores = vector_channel(store, query, cache_dir=tmp_path)
    assert vector_scores, "fake embedder 应产出向量分数"

    hybrid = recall(
        query,
        store,
        oid=1,
        databases=["lowcode_pplatform"],
        top_k=5,
        vector_scores=vector_scores,
    )
    # 向量通道接通：两路都跑通，且枚举页仍在窗口（融合不倒退）
    assert "cust_build_type" in {p.page_key for p in hybrid}


def test_recall_embedder_param_degrades_silently(monkeypatch) -> None:
    from apps.knowledge.wiki import embeddings as emb_mod

    monkeypatch.setattr(emb_mod, "_cosine_impl", lambda a, b: 0.0)

    # embedder 抛异常 → 静默降级纯词法（不抛出）
    def broken(_store, _query):
        raise RuntimeError("embedding down")

    hits = recall(
        "平台录入",
        _load_store(),
        oid=1,
        databases=["lowcode_pplatform"],
        top_k=3,
        embedder=broken,
    )
    assert hits  # 降级后仍有词法结果


def test_wiki_recall_step_gated_by_backend(monkeypatch) -> None:
    from apps.chat.steps import wiki_recall as wr
    from common.core.config import settings

    monkeypatch.setattr(settings, "KNOWLEDGE_BACKEND", "unit")
    assert wr.wiki_business_text("q", ds_id=15) is None  # unit 后端 → None

    monkeypatch.setattr(settings, "KNOWLEDGE_BACKEND", "wiki")
    monkeypatch.setattr(settings, "KNOWLEDGE_WIKI_DS_ALLOWLIST", "15")
    monkeypatch.setattr(settings, "KNOWLEDGE_WIKI_EMBEDDING_ENABLED", False)
    store = _load_store()
    monkeypatch.setattr(wr, "_store", lambda ds_id=None: store)
    text = wr.wiki_business_text("平台录入的企业清单", ds_id=15)
    assert text and "cust_build_type" in text  # 段拼装含权威枚举页

    monkeypatch.setattr(settings, "KNOWLEDGE_WIKI_DS_ALLOWLIST", "8")
    assert wr.wiki_business_text("平台录入", ds_id=15) is None
    monkeypatch.setattr(settings, "KNOWLEDGE_BACKEND", "unit")
    assert wr.wiki_business_text("平台录入", ds_id=15) is None


def test_wiki_recall_unbound_skips_directory_fallback(monkeypatch) -> None:
    from apps.chat.steps import wiki_recall as wr
    from common.core.config import settings

    monkeypatch.setattr(settings, "KNOWLEDGE_BACKEND", "wiki")
    monkeypatch.setattr(settings, "KNOWLEDGE_WIKI_DS_ALLOWLIST", "*")
    monkeypatch.setattr(wr, "_db_store", lambda _ds_id: None)
    wr._DB_STORE.clear()
    wr._DB_INDEX.clear()
    wr._DB_STAMP.clear()
    assert wr.wiki_business_text("平台录入", ds_id=15) is None
