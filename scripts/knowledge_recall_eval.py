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
import sys


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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questions", type=pathlib.Path, required=True)
    parser.add_argument("--ds-id", type=int, required=True)
    args = parser.parse_args(argv)
    questions = load_questions(args.questions)
    for strategy in ("unit", "node"):
        report = evaluate(questions, strategy=strategy, ds_id=args.ds_id)
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())