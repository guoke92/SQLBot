#!/usr/bin/env python
"""Backfill the v3.1 node store from already-registered KnowledgePackage rows.

P2 migration: packages registered before the decomposer existed (or before
this schema) carry their full source document in
knowledge_package.source_document. Re-decomposing them populates the node
store without re-upload. The legacy revision plane is left untouched so the
current runtime keeps serving it until the recall switch (P3).

Usage:
    backend/venv/bin/python scripts/backfill_compositions.py [--oid 1]
"""

from __future__ import annotations

import argparse
import sys

from sqlmodel import select

from apps.knowledge.db_models import SemanticKnowledgePackage
from apps.knowledge.graph.decompose import decompose_package
from apps.knowledge.semantic.schema import KnowledgePackageV2
from common.core.db import get_session


def backfill(oid: int) -> dict[str, int]:
    stats = {"packages": 0, "skipped": 0, "failed": 0}
    with get_session() as session:
        packages = session.exec(
            select(SemanticKnowledgePackage).where(
                SemanticKnowledgePackage.oid == oid
            )
        ).all()
        for package in packages:
            try:
                model = KnowledgePackageV2.model_validate(
                    package.source_document
                )
                report = decompose_package(
                    session,
                    oid=oid,
                    package=model,
                    package_row_id=int(package.id or 0),
                )
                session.commit()
                plan = report.plan
                stats["packages"] += 1
                print(
                    f"package {package.package_id!r} rev {package.revision}: "
                    f"{plan.stats['node_count']} nodes, "
                    f"{plan.stats['edge_count']} edges, "
                    f"{plan.stats['merge_conflicts']} conflicts"
                )
            except Exception as exc:  # noqa: BLE001 - per-package isolation
                session.rollback()
                stats["failed"] += 1
                print(
                    f"package {package.package_id!r} rev {package.revision} "
                    f"FAILED: {type(exc).__name__}: {exc}"
                )
    return stats


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--oid", type=int, default=1)
    args = parser.parse_args(argv)
    stats = backfill(args.oid)
    print(stats)
    return 0 if stats["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())