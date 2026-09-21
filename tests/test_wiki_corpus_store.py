"""Wiki corpus import / bind / remap / mixed recall tests."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.knowledge.wiki.binding_service import (  # noqa: E402
    _remap_for_datasource,
    collect_bind_ids,
    effective_remap_databases,
    suggest_database_remap,
)
from apps.knowledge.wiki.contract import parse_page  # noqa: E402
from apps.knowledge.wiki.corpus_runtime import (  # noqa: E402
    corpus_cache_stamp,
    remap_databases,
)
from apps.knowledge.wiki.chunker import (  # noqa: E402
    _MAX_CHUNK_CHARS,
    chunk_markdown,
)
from apps.knowledge.wiki.corpus_store import (  # noqa: E402
    CorpusImportError,
    parse_directory,
    resolve_pages_dir,
)
from apps.ai_model.embedding import pack_indices_by_tokens  # noqa: E402
from apps.knowledge.wiki.embeddings import WikiEmbeddingIndex  # noqa: E402
from apps.knowledge.wiki.recall import InMemoryWikiStore, recall  # noqa: E402


def _write_page(root: Path, rel: str, body: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


_TABLE_PAGE = """---
page_key: cust_company_info
title: 企业信息
type: table
status: published
oid: 1
scope:
  databases: [lowcode_pplatform]
aliases: [企业]
anchors: [cust_company_info]
sources: [test]
contract_version: "0.1"
---

## 概述
企业主表。

```ground:table
table: cust_company_info
row_semantic: 企业
fields:
  - name: id
    type: bigint
    description: 主键
```
"""

_DRAFT_PAGE = """---
page_key: 平台录入
title: 平台录入
type: concept
status: draft
oid: 1
aliases: [PC端录入]
field_targets: [cust_company_info.cust_build_type]
sources: [test]
contract_version: "0.1"
---

平台录入是 PC_BUILD。
"""

_ENUM_PAGE = """---
page_key: cust_build_type
title: 建档录入方式
type: dict
status: published
oid: 1
scope:
  databases: [lowcode_pplatform]
aliases: [录入方式]
anchors: [cust_company_info.cust_build_type]
sources: [test]
contract_version: "0.1"
---

```ground:dict
dict: cust_company_info.cust_build_type
values:
  PC_BUILD: {label: 平台录入}
  AGW_BUILD: {label: 网关录入}
```
"""


def test_parse_directory_preserves_draft_and_skips_junk(tmp_path: Path) -> None:
    _write_page(tmp_path, "tables/cust_company_info.md", _TABLE_PAGE)
    _write_page(tmp_path, "concepts/平台录入.md", _DRAFT_PAGE)
    _write_page(tmp_path, "_index.md", "# skip")
    _write_page(
        tmp_path,
        ".runs/topic/_note.md",
        '---\npage_key: x\ntitle: x\ntype: rule\nstatus: published\nsources: [t]\ncontract_version: "0.1"\n---\n',
    )
    _write_page(tmp_path, "broken.md", "not a wiki page")

    parsed = parse_directory(tmp_path)
    keys = {page.page_key for _path, page, _body, _sha in parsed.pages}
    assert keys == {"cust_company_info", "平台录入"}
    statuses = {page.page_key: page.status for _path, page, _body, _sha in parsed.pages}
    assert statuses["cust_company_info"] == "published"
    assert statuses["平台录入"] == "draft"
    assert parsed.failed
    assert any("broken.md" in item.path for item in parsed.failed)


def test_parse_directory_rejects_missing_dir(tmp_path: Path) -> None:
    try:
        parse_directory(tmp_path / "missing")
    except CorpusImportError:
        return
    raise AssertionError("expected CorpusImportError")


def test_suggest_and_apply_database_remap() -> None:
    remap = suggest_database_remap(["lowcode_pplatform"], "qa_pplatform")
    assert remap == {"lowcode_pplatform": "qa_pplatform"}
    mapped = remap_databases(("lowcode_pplatform",), remap)
    assert mapped == ("qa_pplatform",)
    same = suggest_database_remap(["qa_pplatform"], "qa_pplatform")
    assert same == {}


def test_db_vectors_mixed_recall_includes_draft() -> None:
    pages = [
        parse_page(_TABLE_PAGE, page_key="cust_company_info"),
        parse_page(_DRAFT_PAGE, page_key="平台录入"),
        parse_page(_ENUM_PAGE, page_key="cust_build_type"),
    ]
    store = InMemoryWikiStore(pages)
    index = WikiEmbeddingIndex.from_vectors(store, {})
    assert index.ensured is False
    hits = recall(
        "平台录入",
        store,
        oid=1,
        databases=["lowcode_pplatform"],
        top_k=5,
        embedder=lambda _s, _q: None,
    )
    keys = [item.page_key for item in hits]
    assert "cust_build_type" in keys
    assert "平台录入" in keys  # draft temporarily admitted


def test_parse_directory_empty_dir(tmp_path: Path) -> None:
    parsed = parse_directory(tmp_path)
    assert parsed.pages == []
    assert parsed.failed == []


def test_resolve_pages_dir_relative_to_repo_root() -> None:
    path = resolve_pages_dir("docs/wiki/v3")
    assert path.is_dir()
    assert path.name == "v3"
    try:
        resolve_pages_dir("   ")
    except CorpusImportError:
        return
    raise AssertionError("expected CorpusImportError for empty pages_dir")


def test_collect_bind_ids_dedupes_legacy_and_list() -> None:
    assert collect_bind_ids(15, [8, 15, 8]) == [8, 15]
    assert collect_bind_ids(15, None) == [15]
    assert collect_bind_ids(None, []) == []
    assert collect_bind_ids(0, [-1, 8]) == [8]


def test_remap_for_datasource_is_per_ds_when_batch_binding() -> None:
    ids = [8, 15]
    by_ds = {"8": {"src": "db_a"}, "15": {"src": "db_b"}}
    assert _remap_for_datasource(
        8, ids=ids, remap_databases={"src": "ignored"}, remaps_by_datasource=by_ds
    ) == {"src": "db_a"}
    assert _remap_for_datasource(
        15, ids=ids, remap_databases={"src": "ignored"}, remaps_by_datasource=by_ds
    ) == {"src": "db_b"}
    assert (
        _remap_for_datasource(
            8, ids=ids, remap_databases={"src": "ignored"}, remaps_by_datasource=None
        )
        is None
    )
    assert _remap_for_datasource(
        8, ids=[8], remap_databases={"src": "legacy"}, remaps_by_datasource=None
    ) == {"src": "legacy"}


def test_empty_remap_from_ui_uses_suggested() -> None:
    suggested = {"lowcode_pplatform": "qa_pplatform"}
    assert effective_remap_databases(None, suggested) == suggested
    assert effective_remap_databases({}, suggested) == suggested
    assert effective_remap_databases({"lowcode_pplatform": "other"}, suggested) == {
        "lowcode_pplatform": "other"
    }


def test_corpus_cache_stamp_invalidates_when_embed_finishes() -> None:
    indexing = corpus_cache_stamp(
        corpus_id=1,
        generation=2,
        remap={},
        status="indexing",
        embedded_chunks=0,
    )
    ready = corpus_cache_stamp(
        corpus_id=1,
        generation=2,
        remap={},
        status="ready",
        embedded_chunks=12,
    )
    assert indexing != ready


def test_bind_signature_does_not_take_pages_dir() -> None:
    import inspect

    from apps.knowledge.wiki.binding_service import bind_corpus

    assert "pages_dir" not in inspect.signature(bind_corpus).parameters


def test_from_vectors_enables_vector_channel() -> None:
    page = parse_page(_ENUM_PAGE, page_key="cust_build_type")
    store = InMemoryWikiStore([page])
    dim = 4
    key = page.store_key
    vectors = {
        f"{key}#{i}": [1.0, 0.0, 0.0, 0.0]
        for i in range(len(store.chunks[key]))
    }
    index = WikiEmbeddingIndex.from_vectors(store, vectors)
    assert index.ensured is True
    # query_scores still needs embed_query; empty-safe: ensure stays true
    assert index.ensure() is True
    assert dim == 4


def test_chunk_markdown_caps_long_line() -> None:
    body = "概述\n\n" + ("字" * 5000)
    chunks = chunk_markdown(body)
    assert chunks
    assert all(len(chunk.text) <= _MAX_CHUNK_CHARS + 20 for chunk in chunks)
    assert len(chunks) >= 2


def test_chunk_markdown_display_zone_not_recalled() -> None:
    body = (
        "# 企业主档\n\n"
        "主档一行一企。\n\n"
        "## 版本演进\n\n"
        "本期不处理审批撤销。\n\n"
        "## 字段\n\n"
        "name 是企业名称。\n"
    )
    chunks = chunk_markdown(body)
    recalled = [chunk.text for chunk in chunks if chunk.recall]
    hidden = [chunk.text for chunk in chunks if not chunk.recall]
    assert any("一行一企" in text for text in recalled)
    assert any("name 是企业名称" in text for text in recalled)
    assert any("本期不处理" in text for text in hidden)
    assert all("本期不处理" not in text for text in recalled)


def test_chunk_markdown_display_fence_not_recalled() -> None:
    body = "口径谓词 enable=Y\n\n```wiki:display\nV1.13 排期说明\n```\n"
    chunks = chunk_markdown(body)
    assert any(chunk.recall and "enable=Y" in chunk.text for chunk in chunks)
    assert any(not chunk.recall and "排期说明" in chunk.text for chunk in chunks)


def test_pack_indices_keeps_request_under_8k() -> None:
    texts = ["字" * 600] * 20
    groups = pack_indices_by_tokens(texts, max_tokens=7000)
    assert len(groups) > 1
    from apps.ai_model.embedding import estimate_embed_tokens

    for group in groups:
        total = sum(estimate_embed_tokens(texts[i]) for i in group)
        assert total <= 7000 or len(group) == 1


_CONCEPT_IDENTIFY = """---
page_key: concept_identify_style
title: 认证方式
type: concept
status: published
oid: 1
aliases: [认证方式]
field_targets: [cust_company_info.identify_style]
sources: [test]
contract_version: "0.1"
---

认证方式存于 identify_style。
"""

_ENUM_IDENTIFY = """---
page_key: identify_style
title: identify_style
type: dict
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
aliases: [认证方式]
anchors: [cust_company_info.identify_style]
sources: [test]
contract_version: "0.1"
---

```ground:dict
dict: identify_style
fields: [cust_company_info.identify_style]
values:
  INVITE_AGW: {label: 邀请认证-内管录入}
```
"""

_CONCEPT_CUST_STATUS = """---
page_key: concept_cust_status
title: 客户状态
type: concept
status: published
oid: 1
field_targets: [cust_company_info.cust_status]
sources: [test]
contract_version: "0.1"
---

客户状态。
"""

_ENUM_CUST_STATUS = """---
page_key: cust_status
title: cust_status
type: dict
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: [test]
contract_version: "0.1"
---

```ground:dict
dict: cust_status
fields: [cust_company_info.cust_status]
values:
  EFFECT: {label: 生效}
```
"""


def test_parse_page_frontmatter_page_key_wins_over_filename_stem() -> None:
    page = parse_page(_CONCEPT_IDENTIFY, page_key="identify_style")
    assert page.page_key == "concept_identify_style"
    assert page.type == "concept"
    stamped = parse_page(
        _CONCEPT_IDENTIFY, page_key="stamped_concept", override_page_key=True
    )
    assert stamped.page_key == "stamped_concept"


def test_parse_directory_keeps_concept_and_enum_with_same_filename_stem(
    tmp_path: Path,
) -> None:
    _write_page(tmp_path, "concepts/identify_style.md", _CONCEPT_IDENTIFY)
    _write_page(tmp_path, "dicts/identify_style.md", _ENUM_IDENTIFY)
    _write_page(tmp_path, "concepts/cust_status.md", _CONCEPT_CUST_STATUS)
    _write_page(tmp_path, "dicts/cust_status.md", _ENUM_CUST_STATUS)

    parsed = parse_directory(tmp_path)
    keys = {page.page_key: page.type for _path, page, _body, _sha in parsed.pages}
    assert keys == {
        "concept_identify_style": "concept",
        "identify_style": "dict",
        "concept_cust_status": "concept",
        "cust_status": "dict",
    }
    assert not parsed.failed
    belongs = {(page.belong, page.page_key) for _path, page, _body, _sha in parsed.pages}
    assert ("concepts", "concept_identify_style") in belongs
    assert ("dicts", "identify_style") in belongs


def test_parse_page_normalizes_illegal_prefixed_page_key() -> None:
    raw = """---
page_key: caliber/approval_in_progress
title: 审批中
type: caliber
status: published
sources: [test]
contract_version: "0.1"
---

口径正文。
"""
    page = parse_page(raw)
    assert page.page_key == "approval_in_progress"
    assert page.belong == "calibers"


def test_parse_page_belong_mismatch_raises() -> None:
    raw = """---
page_key: pay_status
title: 缴费状态
type: concept
belong: concepts
status: published
sources: [test]
contract_version: "0.1"
---

概念。
"""
    try:
        parse_page(raw, belong="dicts")
    except Exception as exc:
        assert "不一致" in str(exc)
        return
    raise AssertionError("expected PageContractError")


def test_same_page_key_different_belong_coexist(tmp_path: Path) -> None:
    concept = """---
page_key: pay_status
title: 缴费状态
type: concept
status: published
sources: [test]
contract_version: "0.1"
---

概念页。
"""
    enum = """---
page_key: pay_status
title: pay_status
type: dict
status: draft
sources: [test]
contract_version: "0.1"
---

```ground:dict
dict: pay_status
fields: [ca_fee_company.pay_status]
values:
  PAID: {label: 已缴}
```
"""
    _write_page(tmp_path, "concepts/pay_status.md", concept)
    _write_page(tmp_path, "dicts/pay_status.md", enum)
    parsed = parse_directory(tmp_path)
    assert not parsed.failed
    assert len(parsed.pages) == 2
    store = InMemoryWikiStore([page for _p, page, _b, _s in parsed.pages])
    assert "concepts/pay_status" in store.pages
    assert "dicts/pay_status" in store.pages
    from apps.knowledge.wiki.graph import build_graph, fold_key

    _adj, alias_map = build_graph(store.pages)
    assert alias_map[fold_key("dicts/pay_status")] == "dicts/pay_status"
    assert fold_key("pay_status") not in alias_map


def test_normalize_script_dedupes_identical_body_and_rewrites_links(
    tmp_path: Path,
) -> None:
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "normalize_wiki_corpus",
        _ROOT / ".tmp" / "scripts" / "normalize_wiki_corpus.py",
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    body = "同一段正文用于去重。\n"
    keep = f"""---
page_key: shared_rule
title: 规则
type: rule
status: published
sources: [test]
contract_version: "0.1"
---

{body}"""
    dup = f"""---
page_key: shared_rule
title: 口径拷贝
type: caliber
status: published
sources: [test]
contract_version: "0.1"
---

{body}"""
    other = """---
page_key: other
title: 其它
type: concept
status: published
related: [shared_rule]
sources: [test]
contract_version: "0.1"
---

见 [[shared_rule]]。
"""
    _write_page(tmp_path, "rules/shared_rule.md", keep)
    _write_page(tmp_path, "calibers/shared_rule.md", dup)
    _write_page(tmp_path, "concepts/other.md", other)
    stats = mod.normalize_tree(tmp_path, dry_run=False)
    assert stats["deleted"] == 1
    assert (tmp_path / "calibers" / "shared_rule.md").exists()
    assert not (tmp_path / "rules" / "shared_rule.md").exists()
    text = (tmp_path / "concepts" / "other.md").read_text()
    assert "[[calibers/shared_rule]]" in text
    assert "related: [calibers/shared_rule]" in text
