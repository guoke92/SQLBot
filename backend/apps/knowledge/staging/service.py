"""Staging quarantine for Conversation knowledge candidates."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlmodel import Session, col, select

from apps.knowledge.db_models import KnowledgeStaging
from apps.knowledge.evidence import append_evidence_event, reproduce_event_key
from apps.knowledge.lineage import append_event, new_lineage_id
from apps.knowledge.natural_key import caliber_natural_key, fragments_equivalent


def list_pending_staging(
    session: Session,
    *,
    oid: int,
    kind: str | None = None,
    limit: int = 100,
) -> list[KnowledgeStaging]:
    stmt = (
        select(KnowledgeStaging)
        .where(KnowledgeStaging.oid == oid)
        .where(KnowledgeStaging.status == "pending")
        .order_by(col(KnowledgeStaging.create_time).desc())
        .limit(limit)
    )
    if kind:
        stmt = stmt.where(KnowledgeStaging.kind == kind)
    return list(session.exec(stmt).all())


def admit_candidate(
    session: Session,
    *,
    oid: int,
    kind: str,
    trigger_id: str,
    payload: dict[str, Any],
    scope: dict[str, Any],
    source_record_id: int | None,
    suggested_trust_tier: str = "admitted",
    quality_snapshot: dict[str, Any] | None = None,
    field_targets: list[Any] | None = None,
    provenance: dict[str, Any] | None = None,
) -> tuple[KnowledgeStaging, str]:
    """Admit a candidate into staging or merge with an existing pending row.

    Returns ``(staging, action)`` where action is ``admitted`` or ``merged``.
    """
    fragment = payload.get("contract_fragment") or payload.get("fragment") or {}
    if not isinstance(fragment, dict):
        fragment = {}
    natural_key = payload.get("natural_key") or caliber_natural_key(
        oid=oid,
        datasource_id=scope.get("ds_id") or scope.get("datasource_id"),
        field_targets=field_targets or payload.get("field_targets") or [],
        fragment=fragment,
    )

    existing_pending = session.exec(
        select(KnowledgeStaging)
        .where(KnowledgeStaging.oid == oid)
        .where(KnowledgeStaging.natural_key == natural_key)
        .where(KnowledgeStaging.status == "pending")
    ).first()
    if existing_pending is not None:
        existing_payload = dict(existing_pending.payload or {})
        existing_frag = (
            existing_payload.get("contract_fragment")
            or existing_payload.get("fragment")
            or {}
        )
        if not isinstance(existing_frag, dict):
            existing_frag = {}
        equivalent = (
            fragments_equivalent(existing_frag, fragment)
            if kind == "caliber"
            else existing_payload == payload
        )
        if equivalent:
            existing_pending.quality_snapshot = {
                **(existing_pending.quality_snapshot or {}),
                **(quality_snapshot or {}),
                "merge_count": int(
                    (existing_pending.quality_snapshot or {}).get("merge_count") or 0
                )
                + 1,
            }
            existing_pending.update_time = datetime.utcnow()
            session.add(existing_pending)
            # Pre-certify reproduce evidence keyed by natural_key; certify
            # backfills asset_id so promotion counting inherits it seamlessly.
            if source_record_id is not None:
                append_evidence_event(
                    session,
                    event_key=reproduce_event_key(natural_key, source_record_id),
                    asset_id=None,
                    asset_kind=kind,
                    natural_key=natural_key,
                    signal_kind="reproduce",
                    record_id=source_record_id,
                    fact={"trigger": trigger_id, "phase": "staging_merge"},
                )
            append_event(
                session,
                lineage_id=existing_pending.lineage_id,
                asset_kind=kind,
                action="merged",
                asset_id=existing_pending.id,
                trigger_id=trigger_id,
                refs={"source_record_id": source_record_id},
                require_evidence=False,
            )
            session.flush()
            return existing_pending, "merged"
        existing_pending.payload = payload
        existing_pending.trigger_id = trigger_id
        existing_pending.source_record_id = source_record_id
        existing_pending.suggested_trust_tier = suggested_trust_tier
        existing_pending.quality_snapshot = {
            **(existing_pending.quality_snapshot or {}),
            **(quality_snapshot or {}),
            "replaced": "pending_fragment_mismatch",
        }
        existing_pending.update_time = datetime.utcnow()
        session.add(existing_pending)
        append_event(
            session,
            lineage_id=existing_pending.lineage_id,
            asset_kind=kind,
            action="merged",
            asset_id=existing_pending.id,
            trigger_id=trigger_id,
            refs={"source_record_id": source_record_id},
            payload={"reason": "pending_fragment_replaced"},
            require_evidence=False,
        )
        session.flush()
        return existing_pending, "merged"

    # Rejection memory: a reviewer already said no to this exact knowledge.
    # Re-admitting it would put the same item back in the triage queue forever.
    # Explicit manual entry is the recovery channel and bypasses suppression.
    if (provenance or {}).get("source_type") != "manual":
        rejected = session.exec(
            select(KnowledgeStaging)
            .where(KnowledgeStaging.oid == oid)
            .where(KnowledgeStaging.natural_key == natural_key)
            .where(KnowledgeStaging.status == "rejected")
            .order_by(col(KnowledgeStaging.update_time).desc())
        ).first()
        if rejected is not None:
            return rejected, "suppressed"

    now = datetime.utcnow()
    lineage_id = new_lineage_id()
    staging = KnowledgeStaging(
        oid=oid,
        kind=kind,
        status="pending",
        natural_key=natural_key,
        scope=scope,
        payload=payload,
        trigger_id=trigger_id,
        source_record_id=source_record_id,
        suggested_trust_tier=suggested_trust_tier,
        quality_snapshot=quality_snapshot,
        lineage_id=lineage_id,
        provenance=provenance,
        create_time=now,
        update_time=now,
    )
    session.add(staging)
    session.flush()
    append_event(
        session,
        lineage_id=lineage_id,
        asset_kind=kind,
        action="captured",
        asset_id=staging.id,
        trigger_id=trigger_id,
        refs={"source_record_id": source_record_id},
        payload={"status": "pending"},
        require_evidence=False,
    )
    append_event(
        session,
        lineage_id=lineage_id,
        asset_kind=kind,
        action="admitted",
        asset_id=staging.id,
        to_tier="admitted",
        trigger_id=trigger_id,
        require_evidence=False,
    )
    return staging, "admitted"
