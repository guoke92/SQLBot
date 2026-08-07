"""Business caliber CRUD: certify / demote / schema-drift disable."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlmodel import Session, select

from apps.knowledge.db_models import BusinessCaliber, KnowledgeStaging
from apps.knowledge.lineage import append_event
from apps.knowledge.natural_key import caliber_natural_key

_DEMOTE_TIERS = frozenset({"published", "trusted", "admitted"})


def _require_valid_fragment(fragment: dict[str, Any]) -> None:
    """Light shape gate before certify — reuse QueryContract parsers, no new engine."""
    requirements = fragment.get("requirements")
    if not isinstance(requirements, list) or not requirements:
        raise ValueError("contract_fragment.requirements must be a non-empty list")
    from apps.chat.query_contract import parse_requirement

    for index, req in enumerate(requirements):
        if not isinstance(req, dict):
            raise ValueError(
                f"contract_fragment.requirements[{index}] must be an object"
            )
        try:
            parse_requirement(req)
        except Exception as exc:
            raise ValueError(
                f"contract_fragment.requirements[{index}] is not a valid "
                f"contract slot: {exc}"
            ) from exc


def certify_staging_caliber(
    session: Session,
    *,
    staging_id: int,
    actor_user_id: int | None,
    oid: int,
    supersede_existing: bool = True,
) -> BusinessCaliber:
    """One-click certify: staging pending → business_caliber certified.

    ``status=conflict`` rows are rejected (legacy dead-end). Prefer pending rows
    that carry ``conflict_with`` — an existing enabled caliber with the same
    natural_key is superseded in the same transaction.
    """
    staging = session.get(KnowledgeStaging, staging_id)
    if staging is None or staging.oid != oid:
        raise ValueError("staging not found")
    if staging.kind != "caliber":
        raise ValueError("staging kind is not caliber")
    if staging.status == "conflict":
        raise ValueError(
            "conflict staging cannot be certified; resolve or discard first"
        )
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
        select(BusinessCaliber)
        .where(BusinessCaliber.oid == oid)
        .where(BusinessCaliber.natural_key == natural_key)
        .where(BusinessCaliber.enabled.is_(True))  # type: ignore[attr-defined]
        .where(BusinessCaliber.superseded_by.is_(None))  # type: ignore[attr-defined]
    ).first()
    if prior is not None and not supersede_existing:
        raise ValueError("enabled caliber with same natural_key already exists")

    now = datetime.utcnow()
    caliber = BusinessCaliber(
        lineage_id=staging.lineage_id,
        version=(int(prior.version) + 1) if prior is not None else 1,
        oid=oid,
        datasource_id=int(ds_id) if ds_id is not None else None,
        advanced_application_id=(staging.scope or {}).get("assistant_id"),
        label=label,
        summary=str(summary) if summary else None,
        contract_fragment=fragment,
        field_targets=field_targets,
        synonyms=payload.get("synonyms"),
        trust_tier="certified",
        certified=True,
        enabled=True,
        provenance={
            "trigger_id": staging.trigger_id,
            "source_record_id": staging.source_record_id,
            "staging_id": staging.id,
            "supersedes": prior.id if prior else None,
        },
        natural_key=natural_key,
        create_by=actor_user_id,
        certify_by=actor_user_id,
        create_time=now,
        update_time=now,
    )
    session.add(caliber)
    session.flush()

    if prior is not None and prior.id is not None:
        prior.enabled = False
        prior.superseded_by = caliber.id
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
            refs={"related_asset_ids": [caliber.id]},
            evidence_snapshot={
                "reason": "certify_supersede",
                "new_caliber_id": caliber.id,
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
        asset_id=caliber.id,
        asset_version=caliber.version,
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
        asset_id=caliber.id,
        asset_version=caliber.version,
        actor={"user_id": actor_user_id},
        from_tier="published",
        to_tier="certified",
        trigger_id=staging.trigger_id,
        evidence_snapshot=evidence,
    )
    session.flush()
    return caliber


def demote_caliber(
    session: Session,
    *,
    caliber_id: int,
    oid: int,
    actor_user_id: int | None,
    to_tier: str = "published",
    reason: str = "",
) -> BusinessCaliber:
    if to_tier not in _DEMOTE_TIERS:
        raise ValueError(
            f"demote to_tier must be one of {sorted(_DEMOTE_TIERS)}, got {to_tier!r}"
        )
    caliber = session.get(BusinessCaliber, caliber_id)
    if caliber is None or caliber.oid != oid:
        raise ValueError("caliber not found")
    from_tier = caliber.trust_tier
    caliber.trust_tier = to_tier
    caliber.certified = False
    caliber.update_time = datetime.utcnow()
    session.add(caliber)
    append_event(
        session,
        lineage_id=caliber.lineage_id,
        asset_kind="caliber",
        action="demoted",
        asset_id=caliber.id,
        asset_version=caliber.version,
        actor={"user_id": actor_user_id},
        from_tier=from_tier,
        to_tier=to_tier,
        evidence_snapshot={"reason": reason, "E7": True},
        decision={"reason": reason},
    )
    session.flush()
    return caliber


def disable_caliber(
    session: Session,
    *,
    caliber_id: int,
    oid: int,
    actor_user_id: int | None,
    reason: str = "",
) -> BusinessCaliber:
    caliber = session.get(BusinessCaliber, caliber_id)
    if caliber is None or caliber.oid != oid:
        raise ValueError("caliber not found")
    caliber.enabled = False
    caliber.update_time = datetime.utcnow()
    session.add(caliber)
    append_event(
        session,
        lineage_id=caliber.lineage_id,
        asset_kind="caliber",
        action="disabled",
        asset_id=caliber.id,
        asset_version=caliber.version,
        actor={"user_id": actor_user_id},
        evidence_snapshot=None,
        decision={"reason": reason},
        require_evidence=False,
    )
    session.flush()
    return caliber


def disable_for_schema_change(
    session: Session,
    *,
    ds_id: int,
    changed_field_ids: list[int] | None = None,
    changed_table_ids: list[int] | None = None,
    changed_field_names: list[tuple[str, str]] | None = None,
    changed_table_names: list[str] | None = None,
) -> int:
    """L-1: disable calibers whose field_targets hit deleted/renamed fields.

    Matches by field_id/table_id **or** table_name/field_name (V-T1 often
    only stores names).
    """
    changed_field_ids = changed_field_ids or []
    changed_table_ids = changed_table_ids or []
    name_pairs = {
        (t.casefold(), f.casefold())
        for t, f in (changed_field_names or [])
        if t or f
    }
    table_names = {t.casefold() for t in (changed_table_names or []) if t}
    if (
        not changed_field_ids
        and not changed_table_ids
        and not name_pairs
        and not table_names
    ):
        return 0
    stmt = (
        select(BusinessCaliber)
        .where(BusinessCaliber.datasource_id == ds_id)
        .where(BusinessCaliber.enabled.is_(True))  # type: ignore[attr-defined]
    )
    rows = list(session.exec(stmt).all())
    disabled = 0
    field_set = set(changed_field_ids)
    table_set = set(changed_table_ids)
    now = datetime.utcnow()
    for caliber in rows:
        targets = caliber.field_targets or []
        hit = False
        for target in targets:
            if not isinstance(target, dict):
                continue
            fid = target.get("field_id")
            tid = target.get("table_id")
            tname = str(target.get("table_name") or "").casefold()
            fname = str(target.get("field_name") or "").casefold()
            if fid is not None and int(fid) in field_set:
                hit = True
                break
            if tid is not None and int(tid) in table_set:
                hit = True
                break
            if (tname, fname) in name_pairs:
                hit = True
                break
            if tname and tname in table_names:
                hit = True
                break
        if not hit:
            continue
        caliber.enabled = False
        caliber.update_time = now
        session.add(caliber)
        append_event(
            session,
            lineage_id=caliber.lineage_id,
            asset_kind="caliber",
            action="schema_invalidated",
            asset_id=caliber.id,
            asset_version=caliber.version,
            to_tier=caliber.trust_tier,
            evidence_snapshot={
                "changed_field_ids": changed_field_ids,
                "changed_table_ids": changed_table_ids,
                "changed_field_names": [list(p) for p in name_pairs],
                "changed_table_names": list(table_names),
                "ds_id": ds_id,
            },
        )
        disabled += 1
    if disabled:
        session.flush()
    return disabled


def promote_to_trusted(
    session: Session,
    *,
    caliber_id: int,
    oid: int,
    reproduce_count: int,
    policy_n: int,
) -> BusinessCaliber | None:
    """Reproduce N times → trusted; still not Bind-eligible without certify."""
    caliber = session.get(BusinessCaliber, caliber_id)
    if caliber is None or caliber.oid != oid or not caliber.enabled:
        return None
    if caliber.certified or caliber.trust_tier in ("trusted", "certified", "golden"):
        return caliber
    if reproduce_count < policy_n:
        return None
    from_tier = caliber.trust_tier
    caliber.trust_tier = "trusted"
    caliber.update_time = datetime.utcnow()
    session.add(caliber)
    append_event(
        session,
        lineage_id=caliber.lineage_id,
        asset_kind="caliber",
        action="promoted",
        asset_id=caliber.id,
        asset_version=caliber.version,
        from_tier=from_tier,
        to_tier="trusted",
        evidence_snapshot={
            "E1": False,
            "E4": True,
            "reproduce_count": reproduce_count,
            "note": "trusted_still_no_bind",
        },
    )
    session.flush()
    return caliber
