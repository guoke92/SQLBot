"""Thin Catalog ↔ Conversation linkage helpers (L-2 / L-3 / L-4)."""

from __future__ import annotations

import time
from typing import Any

from sqlmodel import Session

from apps.knowledge.capture.snapshot import TurnSnapshot

# In-process throttle: avoid mining full query-log on every successful turn.
_L3_COOLDOWN_SECONDS = 600
_l3_last_mine: dict[int, float] = {}


def maybe_stage_entity_for_dictionary(
    session: Session,
    *,
    snapshot: TurnSnapshot,
    entity_bindings: dict[str, Any] | None,
) -> int:
    """L-2: clarified entity selections → knowledge_staging kind=entity.

    Does not publish dictionary values; ops / refresh still required for NLQ.
    """
    if not entity_bindings or snapshot.ds_id is None:
        return 0
    resolved = entity_bindings.get("resolved") or {}
    if not resolved:
        return 0
    from apps.knowledge.staging.service import admit_candidate

    count = 0
    for phrase, binding in resolved.items():
        if not isinstance(binding, dict):
            continue
        canonical = binding.get("canonical") or binding.get("value")
        if not canonical:
            continue
        targets = binding.get("targets") or binding.get("fields") or []
        import hashlib

        nk = hashlib.sha256(
            f"entity:{snapshot.oid}:{snapshot.ds_id}:{phrase}:{canonical}".encode()
        ).hexdigest()
        admit_candidate(
            session,
            oid=snapshot.oid,
            kind="entity",
            trigger_id="V-T1",
            payload={
                "phrase": phrase,
                "canonical": canonical,
                "targets": targets,
                "source": "chat",
                "natural_key": nk,
            },
            scope={"ds_id": snapshot.ds_id},
            source_record_id=snapshot.record_id,
            suggested_trust_tier="admitted",
        )
        count += 1
    return count


def maybe_trigger_query_log_joins(
    session: Session,
    *,
    snapshot: TurnSnapshot,
    force: bool = False,
) -> int:
    """L-3: successful SQL → reuse Catalog mine_query_log_joins (throttled)."""
    if snapshot.outcome not in ("success", "accepted", "completed", "ok"):
        return 0
    if snapshot.ds_id is None or not snapshot.sql_list:
        return 0
    ds_id = int(snapshot.ds_id)
    now = time.monotonic()
    last = _l3_last_mine.get(ds_id, 0.0)
    if not force and (now - last) < _L3_COOLDOWN_SECONDS:
        return 0
    try:
        from apps.datasource.profiling.query_log_joins import (
            mine_query_log_join_candidates,
        )
    except ImportError:
        return 0
    try:
        result = mine_query_log_join_candidates(
            session,
            oid=snapshot.oid,
            ds_id=ds_id,
        )
        _l3_last_mine[ds_id] = now
        if isinstance(result, dict):
            return int(result.get("upserted") or result.get("count") or 0)
        return int(result or 0)
    except Exception:  # noqa: BLE001
        return 0
