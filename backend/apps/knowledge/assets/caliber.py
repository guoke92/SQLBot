"""Knowledge asset CRUD: certify / demote / schema-drift disable."""

from __future__ import annotations

from datetime import datetime

from sqlmodel import Session

from apps.knowledge.db_models import KnowledgeAsset
from apps.knowledge.lineage import append_event

_DEMOTE_TIERS = frozenset({"published", "trusted", "admitted"})


def certify_staging_caliber(
    session: Session,
    *,
    staging_id: int,
    actor_user_id: int | None,
    oid: int,
    supersede_existing: bool = True,
) -> KnowledgeAsset:
    del session, staging_id, actor_user_id, oid, supersede_existing
    raise ValueError(
        "runtime knowledge must be published from a 2.0 knowledge unit; "
        "staging is evidence only"
    )


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
