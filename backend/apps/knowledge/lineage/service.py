"""Append-only knowledge lineage events."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlmodel import Session, select

from apps.knowledge.db_models import KnowledgeLineageEvent

# Actions that must freeze an evidence_snapshot (plan §11.3 / §11.13).
PROMOTION_ACTIONS = frozenset(
    {
        "certified",
        "promoted",
        "published",
        "demoted",
        "schema_invalidated",
        "superseded",
    }
)


def new_lineage_id() -> str:
    return f"lin_{uuid4().hex}"


def new_event_id() -> str:
    return f"evt_{uuid4().hex}"


def append_event(
    session: Session,
    *,
    lineage_id: str,
    asset_kind: str,
    action: str,
    asset_id: int | None = None,
    asset_version: int | None = None,
    actor: dict[str, Any] | None = None,
    from_tier: str | None = None,
    to_tier: str | None = None,
    trigger_id: str | None = None,
    refs: dict[str, Any] | None = None,
    evidence_snapshot: dict[str, Any] | None = None,
    decision: dict[str, Any] | None = None,
    payload: dict[str, Any] | None = None,
    at: datetime | None = None,
    require_evidence: bool | None = None,
) -> KnowledgeLineageEvent:
    """Insert one immutable lineage event.

    For promotion/certify/demote/schema_invalidated actions, ``evidence_snapshot``
    is required unless ``require_evidence`` is explicitly False.
    """
    needs_evidence = (
        require_evidence
        if require_evidence is not None
        else action in PROMOTION_ACTIONS
    )
    if needs_evidence and not evidence_snapshot:
        raise ValueError(
            f"lineage action={action!r} requires a non-empty evidence_snapshot"
        )

    event = KnowledgeLineageEvent(
        event_id=new_event_id(),
        lineage_id=lineage_id,
        asset_kind=asset_kind,
        asset_id=asset_id,
        asset_version=asset_version,
        at=at or datetime.utcnow(),
        actor=actor,
        action=action,
        from_tier=from_tier,
        to_tier=to_tier,
        trigger_id=trigger_id,
        refs=refs,
        evidence_snapshot=evidence_snapshot,
        decision=decision,
        payload=payload,
    )
    session.add(event)
    session.flush()
    return event


def list_lineage_events(
    session: Session,
    *,
    lineage_id: str,
    limit: int = 200,
) -> list[KnowledgeLineageEvent]:
    stmt = (
        select(KnowledgeLineageEvent)
        .where(KnowledgeLineageEvent.lineage_id == lineage_id)
        .order_by(KnowledgeLineageEvent.at.asc())  # type: ignore[attr-defined]
        .limit(limit)
    )
    return list(session.exec(stmt).all())
