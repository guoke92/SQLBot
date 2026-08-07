"""Staging quarantine for Conversation knowledge candidates."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlmodel import Session, col, select

from apps.knowledge.db_models import BusinessCaliber, KnowledgeStaging
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
) -> KnowledgeStaging:
    """Admit a candidate into staging (pending) or merge/supersede-hint.

    Staging is never recalled by Compile. Differing material against an enabled
    caliber stays ``pending`` with ``conflict_with`` so certify can supersede.
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
        existing_frag = (existing_pending.payload or {}).get(
            "contract_fragment"
        ) or (existing_pending.payload or {}).get("fragment") or {}
        if not isinstance(existing_frag, dict):
            existing_frag = {}
        if fragments_equivalent(existing_frag, fragment):
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
            return existing_pending
        # Same natural_key but non-equivalent fragment (legacy keys): keep one
        # pending row certifiable — newer payload wins; no status=conflict dead-end.
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
        return existing_pending

    existing_caliber = session.exec(
        select(BusinessCaliber)
        .where(BusinessCaliber.oid == oid)
        .where(BusinessCaliber.natural_key == natural_key)
        .where(BusinessCaliber.enabled.is_(True))  # type: ignore[attr-defined]
        .where(BusinessCaliber.superseded_by.is_(None))  # type: ignore[attr-defined]
    ).first()
    now = datetime.utcnow()
    lineage_id = new_lineage_id()
    status = "pending"
    conflict_with: list[int] | None = None
    if existing_caliber is not None:
        existing_frag = existing_caliber.contract_fragment or {}
        if fragments_equivalent(existing_frag, fragment):
            staging = KnowledgeStaging(
                oid=oid,
                kind=kind,
                status="promoted",
                natural_key=natural_key,
                scope=scope,
                payload=payload,
                trigger_id=trigger_id,
                source_record_id=source_record_id,
                suggested_trust_tier=suggested_trust_tier,
                quality_snapshot={
                    **(quality_snapshot or {}),
                    "skipped": "equivalent_caliber",
                },
                lineage_id=existing_caliber.lineage_id,
                create_time=now,
                update_time=now,
            )
            session.add(staging)
            append_event(
                session,
                lineage_id=existing_caliber.lineage_id,
                asset_kind=kind,
                action="merged",
                asset_id=existing_caliber.id,
                trigger_id=trigger_id,
                refs={"source_record_id": source_record_id},
                require_evidence=False,
            )
            session.flush()
            return staging
        # Same key, different material: stay pending so certify can supersede.
        # Do not use status=conflict — that dead-ends the supersede path.
        status = "pending"
        conflict_with = [int(existing_caliber.id)] if existing_caliber.id else None

    staging = KnowledgeStaging(
        oid=oid,
        kind=kind,
        status=status,
        natural_key=natural_key,
        scope=scope,
        payload=payload,
        trigger_id=trigger_id,
        source_record_id=source_record_id,
        suggested_trust_tier=suggested_trust_tier,
        quality_snapshot=quality_snapshot,
        conflict_with=conflict_with,
        lineage_id=lineage_id,
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
        payload={"status": status},
        require_evidence=False,
    )
    if status == "pending":
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
    return staging
