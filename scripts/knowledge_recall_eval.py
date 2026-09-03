#!/usr/bin/env python
"""Recall evaluation harness: compare the unit and node recall strategies.

Reads tests/eval/knowledge_recall_questions.jsonl (question -> expected node
keys) and runs each strategy against a live backend, reporting seed hit
rate, closure precision and bundle size. Requires a running app + Postgres
(the strategies need pgvector/trigram indexes and published compositions).

Usage:
    backend/venv/bin/python scripts/knowledge_recall_eval.py --ds-id 8 \\
        --questions tests/eval/knowledge_recall_questions.jsonl
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

import yaml


def load_questions(path: pathlib.Path) -> list[dict]:
    questions = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        questions.append(json.loads(line))
    return questions


def evaluate(questions: list[dict], *, strategy: str, ds_id: int) -> dict:
    """Run one strategy over the question set (backend session)."""
    from apps.knowledge.compile import compile_business_data_bundle
    from common.core.config import settings
    from common.core.db import get_session

    settings.KNOWLEDGE_RECALL_STRATEGY = strategy
    seed_hits = 0
    total = 0
    bundle_sizes: list[int] = []
    with get_session() as session:
        for item in questions:
            question = item["question"]
            expected = set(item.get("expected_node_keys") or [])
            bundle = compile_business_data_bundle(
                session,
                stage="generate",
                question=question,
                oid=1,
                ds_id=ds_id,
            )
            total += 1
            reached_keys = _bundle_node_keys(bundle)
            if expected and (expected & reached_keys):
                seed_hits += 1
            size = len(bundle.fields) + len(bundle.concepts) + len(bundle.datasets)
            bundle_sizes.append(size)
    return {
        "strategy": strategy,
        "questions": total,
        "seed_hits": seed_hits,
        "hit_rate": seed_hits / total if total else 0.0,
        "avg_bundle_size": sum(bundle_sizes) / len(bundle_sizes) if bundle_sizes else 0.0,
    }


def _bundle_node_keys(bundle) -> set[str]:
    keys: set[str] = set()
    for dataset in bundle.datasets:
        keys.add(str(dataset.get("name") or ""))
    for field in bundle.fields:
        keys.add(str(field.get("name") or ""))
    for concept in bundle.concepts:
        keys.add(str(concept.get("name") or ""))
    return keys


def _pages_database(pages_dir: pathlib.Path) -> str:
    """评测围栏库名：语料旁 db-catalog.yaml 的顶层 database（与 baseline 同源）。"""
    catalog = pages_dir.parent / "db" / "db-catalog.yaml"
    try:
        data = yaml.safe_load(catalog.read_text()) or {}
    except (OSError, yaml.YAMLError):
        return ""
    return str(data.get("database") or "").strip()


def evaluate_wiki(
    questions: list[dict],
    *,
    pages_dir: pathlib.Path,
    top_k: int = 8,
    use_vector: bool = False,
) -> dict:
    """wiki 策略：直接打 recall 管道（不依赖活后端/Postgres）。

    命中判定：expected_node_keys 与召回 passage 的 page_key/text 物理键相交。
    ``use_vector=True`` 时接真实向量通道（per-page revision 缓存，二次运行零远程）。"""
    from apps.knowledge.wiki.recall import InMemoryWikiStore, recall

    store = InMemoryWikiStore.load_dir(pages_dir)
    _load_known_tables(pages_dir)
    embedder = None
    if use_vector:
        from apps.knowledge.wiki.embeddings import WikiEmbeddingIndex

        index = WikiEmbeddingIndex(store, cache_dir=pages_dir.parent)
        index.ensure()
        oversample = max(top_k * 3, 30)
        embedder = lambda s, q: index.query_scores(q, top_k=oversample)  # noqa: E731
    seed_hits = 0
    total = 0
    sizes: list[int] = []
    for item in questions:
        question = item["question"]
        expected = _expected_keys(item)
        if not expected:
            continue
        passages = recall(
            question,
            store,
            databases=[_pages_database(pages_dir)],
            top_k=top_k,
            embedder=embedder,
        )
        total += 1
        reached: set[str] = set()
        for p in passages:
            reached.add(p.page_key)
            reached.update(_physical_keys(p.text))
            # 表页正文里的裸字段名与页键组合成 table.field 二段键（expected 形态）
            for field in re.findall(r"\bname: ([a-z][a-z0-9_]{2,})\b", p.text):
                reached.add(f"{p.page_key}.{field}")
        if expected & reached:
            seed_hits += 1
        sizes.append(len(passages))
    return {
        "strategy": "wiki",
        "questions": total,
        "seed_hits": seed_hits,
        "hit_rate": seed_hits / total if total else 0.0,
        "avg_passages": sum(sizes) / len(sizes) if sizes else 0.0,
        "pages": len(store.pages),
    }


def _physical_keys(text: str) -> set[str]:
    """从 passage 文本里抽物理键（表名.字段 / 裸表名）供命中判定。

    物理键判定靠 db catalog 的表名清单（--wiki-pages 旁的 db-catalog.yaml
    或显式 --tables），不硬编码业务前缀——换数据集不失效。"""
    keys: set[str] = set()
    for table, field in re.findall(r"\b([a-z][a-z0-9_]{3,})\.([a-z][a-z0-9_]{2,})\b", text):
        keys.add(f"{table}.{field}")
    for bare in re.findall(r"\b([a-z][a-z0-9_]{3,})\b", text):
        if bare in _KNOWN_TABLES:
            keys.add(bare)
    return keys


_KNOWN_TABLES: set[str] = set()


def _load_known_tables(pages_dir: pathlib.Path) -> None:
    catalog = pages_dir.parent / "db" / "db-catalog.yaml"
    if catalog.exists():
        import yaml

        data = yaml.safe_load(catalog.read_text()) or {}
        _KNOWN_TABLES.update(data.get("tables") or {})


def _expected_keys(item: dict) -> set[str]:
    """expected key 归一：剥库名前缀（与 _physical_keys 同形态）+ 保留原文。"""
    normalized: set[str] = set()
    for key in item.get("expected_node_keys") or []:
        normalized.add(key)
        parts = key.split(".")
        if len(parts) >= 3:  # db.table.field / db:table 形态 → 剥首段
            normalized.add(".".join(parts[1:]))
    return normalized


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questions", type=pathlib.Path, required=True)
    parser.add_argument("--ds-id", type=int, required=True)
    parser.add_argument(
        "--strategy",
        default="unit+node",
        help="unit | node | unit+node | wiki（wiki 不需要活后端）",
    )
    parser.add_argument(
        "--wiki-pages",
        type=pathlib.Path,
        default=pathlib.Path("docs/wiki-knowledge/pplatform/wiki-pages"),
        help="wiki 策略的页面目录",
    )
    parser.add_argument(
        "--vector",
        action="store_true",
        help="wiki 策略启用向量通道（per-page revision 缓存）",
    )
    args = parser.parse_args(argv)
    questions = load_questions(args.questions)
    if "wiki" in args.strategy:
        report = evaluate_wiki(
            questions, pages_dir=args.wiki_pages, use_vector=args.vector
        )
        print(json.dumps(report, ensure_ascii=False, indent=2))
    for strategy in ("unit", "node"):
        if strategy not in args.strategy:
            continue
        report = evaluate(questions, strategy=strategy, ds_id=args.ds_id)
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())