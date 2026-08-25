#!/usr/bin/env python
"""Publish decomposed compositions: bind to a datasource, approve, pin + index.

Populates the v3.1 node runtime store (bindings + deployments + node index)
without switching the active recall strategy. The legacy unit plane keeps
serving until KNOWLEDGE_RECALL_STRATEGY=node is explicitly enabled (P3 A/B).

Usage:
    backend/venv/bin/python scripts/backfill_composition_publish.py [--oid 1] [--ds 15] [--dry-run]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT / "backend") not in sys.path:
    sys.path.insert(0, str(_ROOT / "backend"))

from sqlmodel import Session, select

from apps.knowledge.graph.governance import (
    bind_and_validate_composition,
    publish_composition,
)
from apps.knowledge.graph.models import UnitComposition
from common.core.db import engine


def backfill(oid: int, ds_id: int, dry_run: bool) -> dict[str, int]:
    stats = {"total": 0, "bound": 0, "published": 0, "blocked": 0, "failed": 0}
    with Session(engine) as session:
        compositions = session.exec(
            select(UnitComposition).where(UnitComposition.oid == oid)
        ).all()
        stats["total"] = len(compositions)
        for composition in compositions:
            cid = int(composition.id or 0)
            try:
                binding = bind_and_validate_composition(
                    session, oid=oid, composition_id=cid, datasource_id=ds_id
                )
                status = str(composition.validation_status or "NOT_RUN")
                if status == "FAIL":
                    stats["blocked"] += 1
                    issues = (binding.validation_result or {}).get("issues") or []
                    errors = [i for i in issues if i.get("severity") == "error"]
                    print(
                        f"  {composition.unit_key!r}: FAIL -> skipped ("
                        f"{len(errors)} errors: "
                        + "; ".join(str(e.get("code")) for e in errors[:3]) + ")"
                    )
                    continue
                stats["bound"] += 1
                if dry_run:
                    print(f"  {composition.unit_key!r}: {status} (dry-run, not published)")
                    continue
                composition.lifecycle_status = "APPROVED"
                session.add(composition)
                session.commit()
                publish_composition(session, oid=oid, composition_id=cid)
                stats["published"] += 1
                print(f"  {composition.unit_key!r}: published ({status})")
            except Exception as exc:  # noqa: BLE001 - per-composition isolation
                session.rollback()
                stats["failed"] += 1
                print(f"  {composition.unit_key!r} FAILED: {type(exc).__name__}: {exc}")
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--oid", type=int, default=1)
    parser.add_argument("--ds", type=int, default=15, help="datasource id to bind against")
    parser.add_argument("--dry-run", action="store_true", help="bind + validate only, no publish")
    args = parser.parse_args()
    stats = backfill(args.oid, args.ds, args.dry_run)
    print(
        f"done: total={stats['total']} bound={stats['bound']} "
        f"published={stats['published']} blocked={stats['blocked']} failed={stats['failed']}"
    )


if __name__ == "__main__":
    main()
