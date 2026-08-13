"""Rule staging certification using the shared knowledge lifecycle."""

from __future__ import annotations

from datetime import datetime

from sqlmodel import Session, select

from apps.knowledge.db_models import KnowledgeAsset, KnowledgeStaging
from apps.knowledge.lineage import append_event


def certify_staging_rule(
    session: Session,
    *,
    staging_id: int,
    actor_user_id: int | None,
    oid: int,
) -> KnowledgeAsset:
    staging = session.get(KnowledgeStaging, staging_id)
    if staging is None or staging.oid != oid:
        raise ValueError("staging not found")
    if staging.kind != "rule":
        raise ValueError("staging kind is not rule")
    if staging.status != "pending":
        raise ValueError(f"staging status={staging.status} cannot be certified")
    payload = dict(staging.payload or {})
    label = str(payload.get("label") or "").strip()
    content = str(payload.get("content") or "").strip()
    if not label or not content:
        raise ValueError("rule certify requires label and content")
    natural_key = staging.natural_key
    prior = session.exec(
        select(KnowledgeAsset)
        .where(KnowledgeAsset.oid == oid)
        .where(KnowledgeAsset.natural_key == natural_key)
        .where(KnowledgeAsset.enabled.is_(True))  # type: ignore[attr-defined]
        .where(KnowledgeAsset.superseded_by.is_(None))  # type: ignore[attr-defined]
    ).first()
    now = datetime.utcnow()
    asset = KnowledgeAsset(
        kind="rule",
        natural_key=natural_key,
        lineage_id=staging.lineage_id,
        version=(int(prior.version) + 1) if prior is not None else 1,
        oid=oid,
        datasource_id=(staging.scope or {}).get("datasource_id"),
        assistant_id=(staging.scope or {}).get("assistant_id"),
        label=label[:255],
        summary=None,
        payload={"content": content},
        trust_tier="certified",
        certified=True,
        enabled=True,
        valid_from=now,
        provenance={
            "trigger_id": staging.trigger_id,
            "staging_id": staging.id,
            "supersedes": prior.id if prior else None,
            **dict(staging.provenance or {}),
        },
        create_by=actor_user_id,
        certify_by=actor_user_id,
        certify_at=now,
        create_time=now,
        update_time=now,
    )
    session.add(asset)
    session.flush()
    if prior is not None:
        prior.enabled = False
        prior.superseded_by = asset.id
        prior.valid_to = now
        prior.update_time = now
        session.add(prior)
    staging.status = "promoted"
    staging.update_time = now
    session.add(staging)
    append_event(
        session,
        lineage_id=staging.lineage_id,
        asset_kind="rule",
        action="certified",
        asset_id=asset.id,
        asset_version=asset.version,
        actor={"user_id": actor_user_id},
        from_tier="admitted",
        to_tier="certified",
        trigger_id=staging.trigger_id,
        evidence_snapshot={
            "staging_id": staging.id,
            "source": dict(staging.provenance or {}),
        },
    )
    session.flush()
    return asset
