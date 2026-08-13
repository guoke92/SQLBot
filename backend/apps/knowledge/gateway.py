"""Knowledge domain gateway — sole external interface.

Three contracts:
  submit_candidate  — producers → domain (write)
  emit_signal       — external facts → governance (signal)
  compile_knowledge_for_turn — domain → consumers (read, re-exported)
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field
from sqlmodel import Session, select

from apps.knowledge.compile.compile import compile_knowledge_for_turn  # noqa: F401
from apps.knowledge.db_models import (
    KnowledgeAsset,
    KnowledgeSchemaRef,
    KnowledgeStaging,
)
from apps.knowledge.evidence import (
    append_evidence_event,
    apply_event_key,
    feedback_event_key,
    reproduce_event_key,
    usage_event_key,
)
from apps.knowledge.lineage import append_event
from apps.knowledge.natural_key import caliber_natural_key, predicate_looks_ephemeral
from apps.knowledge.staging.service import admit_candidate


class KnowledgeScope(BaseModel):
    oid: int
    datasource_id: int | None = None
    assistant_id: int | None = None


class KnowledgeCandidate(BaseModel):
    kind: str
    payload: dict[str, Any]
    scope: KnowledgeScope
    provenance: dict[str, Any]
    suggested_tier: str = "admitted"
    evidence_hints: dict[str, Any] = Field(default_factory=dict)


class CandidateReceipt(BaseModel):
    staging_id: int | None = None
    action: str
    natural_key: str
    lineage_id: str
    detail: str = ""


class KnowledgeSignal(BaseModel):
    kind: str
    refs: dict[str, Any] = Field(default_factory=dict)
    fact: dict[str, Any] = Field(default_factory=dict)


def _validate_provenance(
    candidate: KnowledgeCandidate,
    *,
    source_record_id: int | None,
    actor_user_id: int | None,
) -> str | None:
    prov = candidate.provenance
    source_type = prov.get("source_type", "")
    if source_type == "chat" and not prov.get("record_id") and not source_record_id:
        return "chat provenance requires record_id"
    if source_type == "manual" and not actor_user_id:
        return "manual provenance requires actor_user_id"
    if source_type == "mining" and not prov.get("scan_run_id"):
        return "mining provenance requires scan_run_id"
    if source_type == "package" and not prov.get("package_id"):
        return "package provenance requires package_id"
    return None


def _scrub_ephemeral(candidate: KnowledgeCandidate) -> KnowledgeCandidate | None:
    """Drop ephemeral predicate requirements; None when nothing survives."""
    if candidate.kind != "caliber":
        return candidate
    fragment = candidate.payload.get("contract_fragment") or {}
    if not isinstance(fragment, dict):
        return candidate
    reqs = fragment.get("requirements") or []
    if not isinstance(reqs, list) or not reqs:
        return candidate
    non_ephemeral = [
        r
        for r in reqs
        if not isinstance(r, dict)
        or r.get("clause") != "predicate"
        or not predicate_looks_ephemeral(r)
    ]
    if not non_ephemeral:
        return None
    if len(non_ephemeral) == len(reqs):
        return candidate
    fragment = {**fragment, "requirements": non_ephemeral}
    return candidate.model_copy(
        update={"payload": {**candidate.payload, "contract_fragment": fragment}}
    )


def submit_candidate(
    session: Session,
    candidate: KnowledgeCandidate,
    *,
    source_record_id: int | None = None,
    actor_user_id: int | None = None,
) -> CandidateReceipt:
    error = _validate_provenance(
        candidate, source_record_id=source_record_id, actor_user_id=actor_user_id
    )
    if error is not None:
        return CandidateReceipt(
            action="rejected", natural_key="", lineage_id="", detail=error
        )

    scrubbed = _scrub_ephemeral(candidate)
    if scrubbed is None:
        return CandidateReceipt(
            action="rejected",
            natural_key="",
            lineage_id="",
            detail="all predicate requirements are ephemeral",
        )
    candidate = scrubbed

    scope = candidate.scope
    prov = candidate.provenance
    fragment = (
        candidate.payload.get("contract_fragment")
        or candidate.payload.get("fragment")
        or {}
    )
    if not isinstance(fragment, dict):
        fragment = {}
    natural_key = caliber_natural_key(
        oid=scope.oid,
        datasource_id=scope.datasource_id,
        field_targets=candidate.payload.get("field_targets") or [],
        fragment=fragment,
    )

    existing_asset = session.exec(
        select(KnowledgeAsset)
        .where(KnowledgeAsset.oid == scope.oid)
        .where(KnowledgeAsset.natural_key == natural_key)
        .where(KnowledgeAsset.enabled.is_(True))  # type: ignore[attr-defined]
        .where(KnowledgeAsset.valid_to.is_(None))  # type: ignore[attr-defined]
    ).first()
    if existing_asset is not None:
        if source_record_id is None:
            return CandidateReceipt(
                action="existing",
                natural_key=natural_key,
                lineage_id=existing_asset.lineage_id,
                detail=f"asset {existing_asset.id} already exists",
            )
        append_evidence_event(
            session,
            event_key=reproduce_event_key(natural_key, source_record_id),
            asset_id=existing_asset.id,
            asset_kind=candidate.kind,
            natural_key=natural_key,
            signal_kind="reproduce",
            record_id=source_record_id,
            fact={
                "source_record_id": source_record_id,
                "trigger": prov.get("trigger_id") or prov.get("source_type"),
            },
        )
        session.flush()
        return CandidateReceipt(
            action="merged_evidence",
            natural_key=natural_key,
            lineage_id=existing_asset.lineage_id,
            detail=f"evidence merged into asset {existing_asset.id}",
        )

    staging, action = admit_candidate(
        session,
        oid=scope.oid,
        kind=candidate.kind,
        trigger_id=str(prov.get("trigger_id") or prov.get("source_type") or "gateway"),
        payload={**candidate.payload, "natural_key": natural_key},
        scope=scope.model_dump(mode="json"),
        source_record_id=source_record_id,
        suggested_trust_tier=candidate.suggested_tier,
        provenance=prov,
    )
    return CandidateReceipt(
        staging_id=staging.id,
        action=action,
        natural_key=staging.natural_key,
        lineage_id=staging.lineage_id,
    )


def emit_signal(session: Session, signal: KnowledgeSignal) -> int:
    now = datetime.utcnow()
    record_id = signal.fact.get("record_id")
    if signal.kind == "apply_outcome" and record_id is not None:
        asset_id = signal.refs.get("asset_id")
        if asset_id is None:
            return 0
        action = str(signal.fact.get("apply_action") or "apply")
        append_evidence_event(
            session,
            event_key=apply_event_key(
                int(record_id),
                str(signal.refs.get("asset_kind") or "caliber"),
                int(asset_id),
                action,
            ),
            asset_id=int(asset_id),
            asset_kind=str(signal.refs.get("asset_kind") or "caliber"),
            signal_kind="apply_outcome",
            record_id=int(record_id),
            fact=signal.fact,
        )
        session.flush()
        return 1
    if signal.kind in {"turn_feedback", "user_feedback"} and record_id is not None:
        revision = int(signal.fact.get("revision") or 0)
        append_evidence_event(
            session,
            event_key=feedback_event_key(int(record_id), revision),
            asset_id=None,
            asset_kind="turn",
            signal_kind="turn_feedback",
            record_id=int(record_id),
            fact=signal.fact,
        )
        session.flush()
        return 1
    if signal.kind == "usage" and record_id is not None:
        asset_id = signal.refs.get("asset_id")
        if asset_id is None:
            return 0
        usage_kind = str(signal.fact.get("usage_kind") or "usage")
        append_evidence_event(
            session,
            event_key=usage_event_key(
                int(record_id),
                str(signal.refs.get("asset_kind") or "caliber"),
                int(asset_id),
                usage_kind,
            ),
            asset_id=int(asset_id),
            asset_kind=str(signal.refs.get("asset_kind") or "caliber"),
            signal_kind="usage",
            record_id=int(record_id),
            fact=signal.fact,
        )
        session.flush()
        return 1

    if signal.kind == "schema_drift":
        return _handle_schema_drift(session, signal, now)

    return 0


def _handle_schema_drift(
    session: Session, signal: KnowledgeSignal, now: datetime
) -> int:
    ds_id = signal.refs.get("ds_id")
    if ds_id is None:
        return 0
    field_set = {
        int(f) for f in (signal.refs.get("changed_field_ids") or []) if f is not None
    }
    table_set = {
        int(t) for t in (signal.refs.get("changed_table_ids") or []) if t is not None
    }
    name_pairs = {
        (str(t).casefold(), str(f).casefold())
        for t, f in (signal.refs.get("changed_field_names") or [])
        if t or f
    }
    t_names = {
        str(t).casefold() for t in (signal.refs.get("changed_table_names") or []) if t
    }
    if not field_set and not table_set and not name_pairs and not t_names:
        return 0

    refs = list(
        session.exec(
            select(KnowledgeSchemaRef).where(
                KnowledgeSchemaRef.datasource_id == int(ds_id)
            )
        ).all()
    )
    affected_asset_ids: set[int] = set()
    for ref in refs:
        if ref.field_id is not None and int(ref.field_id) in field_set:
            affected_asset_ids.add(int(ref.asset_id))
        elif ref.table_id is not None and int(ref.table_id) in table_set:
            affected_asset_ids.add(int(ref.asset_id))
        elif (
            ref.table_name.casefold(),
            (ref.field_name or "").casefold(),
        ) in name_pairs:
            affected_asset_ids.add(int(ref.asset_id))
        elif ref.table_name.casefold() in t_names:
            affected_asset_ids.add(int(ref.asset_id))

    disabled = 0
    for asset_id in affected_asset_ids:
        asset = session.get(KnowledgeAsset, asset_id)
        if asset is None or not asset.enabled:
            continue
        asset.enabled = False
        asset.valid_to = now
        asset.update_time = now
        session.add(asset)
        append_event(
            session,
            lineage_id=asset.lineage_id,
            asset_kind=asset.kind,
            action="schema_invalidated",
            asset_id=asset.id,
            asset_version=asset.version,
            evidence_snapshot={
                "ds_id": ds_id,
                "changed_field_ids": sorted(field_set),
                "changed_table_ids": sorted(table_set),
            },
        )
        disabled += 1
    if disabled:
        session.flush()
    return disabled


def reject_staging(
    session: Session,
    *,
    staging_id: int,
    oid: int,
    actor_user_id: int | None,
    reason: str,
) -> KnowledgeStaging:
    staging = session.get(KnowledgeStaging, staging_id)
    if staging is None or staging.oid != oid:
        raise ValueError("staging not found")
    staging.status = "rejected"
    staging.reject_reason = reason
    staging.update_time = datetime.utcnow()
    session.add(staging)
    append_event(
        session,
        lineage_id=staging.lineage_id,
        asset_kind=staging.kind,
        action="rejected",
        asset_id=staging.id,
        actor={"user_id": actor_user_id},
        evidence_snapshot={"reason": reason},
        require_evidence=True,
    )
    session.flush()
    return staging
