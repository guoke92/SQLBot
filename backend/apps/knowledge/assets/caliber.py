"""Knowledge asset CRUD: certify / demote / schema-drift disable."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlmodel import Session, select

from apps.knowledge.db_models import (
    KnowledgeAsset,
    KnowledgeEvidence,
    KnowledgeSchemaRef,
    KnowledgeStaging,
)
from apps.knowledge.lineage import append_event
from apps.knowledge.natural_key import caliber_natural_key

_DEMOTE_TIERS = frozenset({"published", "trusted", "admitted"})


def _require_valid_fragment(fragment: dict[str, Any]) -> None:
    from apps.chat.intent_defaults import parse_intent_default_fragment

    try:
        parse_intent_default_fragment(fragment)
    except Exception as exc:
        raise ValueError(f"contract_fragment is invalid: {exc}") from exc


def certify_staging_caliber(
    session: Session,
    *,
    staging_id: int,
    actor_user_id: int | None,
    oid: int,
    supersede_existing: bool = True,
) -> KnowledgeAsset:
    staging = session.get(KnowledgeStaging, staging_id)
    if staging is None or staging.oid != oid:
        raise ValueError("staging not found")
    if staging.kind != "caliber":
        raise ValueError("staging kind is not caliber")
    if staging.status != "pending":
        raise ValueError(f"staging status={staging.status} cannot be certified")

    payload = dict(staging.payload or {})
    fragment = payload.get("contract_fragment") or payload.get("fragment") or {}
    if not isinstance(fragment, dict) or not fragment:
        raise ValueError("caliber certify requires contract_fragment")
    _require_valid_fragment(fragment)
    field_targets = list(payload.get("field_targets") or [])
    label = str(payload.get("label") or payload.get("summary") or "caliber")[:255]
    summary = payload.get("summary")
    ds_id = (staging.scope or {}).get("ds_id") or (staging.scope or {}).get(
        "datasource_id"
    )
    natural_key = staging.natural_key or caliber_natural_key(
        oid=oid,
        datasource_id=int(ds_id) if ds_id is not None else None,
        field_targets=field_targets,
        fragment=fragment,
    )

    prior = session.exec(
        select(KnowledgeAsset)
        .where(KnowledgeAsset.oid == oid)
        .where(KnowledgeAsset.natural_key == natural_key)
        .where(KnowledgeAsset.enabled.is_(True))  # type: ignore[attr-defined]
        .where(KnowledgeAsset.superseded_by.is_(None))  # type: ignore[attr-defined]
    ).first()
    if prior is not None and not supersede_existing:
        raise ValueError("enabled asset with same natural_key already exists")

    now = datetime.utcnow()
    asset = KnowledgeAsset(
        kind="caliber",
        lineage_id=staging.lineage_id,
        version=(int(prior.version) + 1) if prior is not None else 1,
        oid=oid,
        datasource_id=int(ds_id) if ds_id is not None else None,
        assistant_id=(staging.scope or {}).get("assistant_id"),
        label=label,
        summary=str(summary) if summary else None,
        payload=payload,
        trust_tier="certified",
        certified=True,
        enabled=True,
        valid_from=now,
        certify_at=now,
        provenance={
            "trigger_id": staging.trigger_id,
            "source_record_id": staging.source_record_id,
            "staging_id": staging.id,
            "supersedes": prior.id if prior else None,
            "staging_quality": dict(staging.quality_snapshot or {}),
        },
        natural_key=natural_key,
        create_by=actor_user_id,
        certify_by=actor_user_id,
        create_time=now,
        update_time=now,
    )
    session.add(asset)
    session.flush()

    # Adopt pre-certify reproduce evidence recorded against the natural key.
    orphan_evidence = session.exec(
        select(KnowledgeEvidence)
        .where(KnowledgeEvidence.natural_key == natural_key)
        .where(KnowledgeEvidence.asset_id.is_(None))  # type: ignore[attr-defined]
        .where(KnowledgeEvidence.asset_kind == "caliber")
    ).all()
    for evidence_row in orphan_evidence:
        evidence_row.asset_id = asset.id
        session.add(evidence_row)

    for target in field_targets:
        if not isinstance(target, dict):
            continue
        ref = KnowledgeSchemaRef(
            asset_id=int(asset.id),  # type: ignore[arg-type]
            asset_kind="caliber",
            datasource_id=int(ds_id) if ds_id is not None else 0,
            table_name=str(target.get("table_name") or ""),
            field_name=target.get("field_name"),
            table_id=target.get("table_id"),
            field_id=target.get("field_id"),
        )
        session.add(ref)

    if prior is not None and prior.id is not None:
        prior.enabled = False
        prior.superseded_by = asset.id
        prior.valid_to = now
        prior.update_time = now
        session.add(prior)
        append_event(
            session,
            lineage_id=prior.lineage_id,
            asset_kind="caliber",
            action="superseded",
            asset_id=prior.id,
            asset_version=prior.version,
            actor={"user_id": actor_user_id},
            refs={"related_asset_ids": [asset.id]},
            evidence_snapshot={
                "reason": "certify_supersede",
                "new_asset_id": asset.id,
            },
            require_evidence=True,
        )

    staging.status = "promoted"
    staging.update_time = now
    session.add(staging)

    evidence = {
        "E8": True,
        "actor_user_id": actor_user_id,
        "contract_fragment": fragment,
        "source_record_id": staging.source_record_id,
        "staging_id": staging.id,
        "prior": ["captured", "admitted"],
    }
    append_event(
        session,
        lineage_id=staging.lineage_id,
        asset_kind="caliber",
        action="published",
        asset_id=asset.id,
        asset_version=asset.version,
        actor={"user_id": actor_user_id},
        from_tier="admitted",
        to_tier="published",
        trigger_id=staging.trigger_id,
        evidence_snapshot=evidence,
    )
    append_event(
        session,
        lineage_id=staging.lineage_id,
        asset_kind="caliber",
        action="certified",
        asset_id=asset.id,
        asset_version=asset.version,
        actor={"user_id": actor_user_id},
        from_tier="published",
        to_tier="certified",
        trigger_id=staging.trigger_id,
        evidence_snapshot=evidence,
    )
    session.flush()
    return asset


def demote_caliber(
    session: Session,
    *,
    caliber_id: int,
    oid: int,
    actor_user_id: int | None,
    to_tier: str = "published",
    reason: str = "",
) -> KnowledgeAsset:
    if to_tier not in _DEMOTE_TIERS:
        raise ValueError(
            f"demote to_tier must be one of {sorted(_DEMOTE_TIERS)}, got {to_tier!r}"
        )
    asset = session.get(KnowledgeAsset, caliber_id)
    if asset is None or asset.oid != oid:
        raise ValueError("caliber not found")
    from_tier = asset.trust_tier
    asset.trust_tier = to_tier
    asset.certified = False
    asset.update_time = datetime.utcnow()
    session.add(asset)
    append_event(
        session,
        lineage_id=asset.lineage_id,
        asset_kind="caliber",
        action="demoted",
        asset_id=asset.id,
        asset_version=asset.version,
        actor={"user_id": actor_user_id},
        from_tier=from_tier,
        to_tier=to_tier,
        evidence_snapshot={"reason": reason, "E7": True},
        decision={"reason": reason},
    )
    session.flush()
    return asset


def disable_caliber(
    session: Session,
    *,
    caliber_id: int,
    oid: int,
    actor_user_id: int | None,
    reason: str = "",
) -> KnowledgeAsset:
    asset = session.get(KnowledgeAsset, caliber_id)
    if asset is None or asset.oid != oid:
        raise ValueError("caliber not found")
    now = datetime.utcnow()
    asset.enabled = False
    asset.valid_to = now
    asset.update_time = now
    session.add(asset)
    append_event(
        session,
        lineage_id=asset.lineage_id,
        asset_kind="caliber",
        action="disabled",
        asset_id=asset.id,
        asset_version=asset.version,
        actor={"user_id": actor_user_id},
        evidence_snapshot=None,
        decision={"reason": reason},
        require_evidence=False,
    )
    session.flush()
    return asset


def promote_to_trusted(
    session: Session,
    *,
    caliber_id: int,
    oid: int,
    policy_n: int,
    positive_feedback_n: int = 2,
    actor_user_id: int | None = None,
) -> KnowledgeAsset:
    """Promote a caliber to trusted when server-side evidence meets *policy_n*.

    Raises ValueError with a reviewer-facing detail when the asset is missing,
    disabled, or the distinct-record evidence count is below the policy floor.
    Already-trusted/certified assets are returned unchanged (idempotent).
    """
    asset = session.get(KnowledgeAsset, caliber_id)
    if asset is None or asset.oid != oid or not asset.enabled:
        raise ValueError("caliber not found")
    if asset.certified or asset.trust_tier in ("trusted", "certified"):
        return asset

    from apps.knowledge.evidence_policy import summarize_asset_evidence

    summary = summarize_asset_evidence(
        session, asset_id=caliber_id, asset_kind="caliber"
    )
    if not summary.promotion_ready(
        reproduce_threshold=policy_n,
        positive_feedback_threshold=positive_feedback_n,
    ):
        raise ValueError(
            "insufficient or conflicting evidence: "
            f"reproductions={summary.reproduce_count}/{policy_n}, "
            f"positive_feedback={summary.positive_feedback_count}/{positive_feedback_n}, "
            f"negative_feedback={summary.negative_feedback_count}"
        )
    from_tier = asset.trust_tier
    asset.trust_tier = "trusted"
    asset.update_time = datetime.utcnow()
    session.add(asset)
    append_event(
        session,
        lineage_id=asset.lineage_id,
        asset_kind="caliber",
        action="promoted",
        asset_id=asset.id,
        asset_version=asset.version,
        actor={"user_id": actor_user_id} if actor_user_id is not None else None,
        from_tier=from_tier,
        to_tier="trusted",
        evidence_snapshot={
            "E1": False,
            "E4": True,
            "reproduce_count": summary.reproduce_count,
            "successful_apply_count": summary.successful_apply_count,
            "positive_feedback_count": summary.positive_feedback_count,
            "negative_feedback_count": summary.negative_feedback_count,
            "note": "trusted_still_no_bind",
        },
    )
    session.flush()
    return asset
