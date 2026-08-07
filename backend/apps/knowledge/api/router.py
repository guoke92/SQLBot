"""Knowledge Conversation plane admin APIs (staging / certify / lineage)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import select

from apps.knowledge.assets.caliber import (
    certify_staging_caliber,
    demote_caliber,
    disable_caliber,
)
from apps.knowledge.db_models import BusinessCaliber, KnowledgeStaging
from apps.knowledge.lineage import list_lineage_events
from apps.knowledge.staging.service import admit_candidate, list_pending_staging
from apps.system.schemas.permission import SqlbotPermission, require_permissions
from common.audit.models.log_model import OperationModules, OperationType
from common.audit.schemas.logger_decorator import LogConfig, system_log
from common.core.deps import CurrentUser, SessionDep

router = APIRouter(tags=["Knowledge"], prefix="/knowledge")


class StagingOut(BaseModel):
    id: int
    kind: str
    status: str
    natural_key: str
    trigger_id: str
    lineage_id: str
    source_record_id: int | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    scope: dict[str, Any] = Field(default_factory=dict)


class CaliberOut(BaseModel):
    id: int
    lineage_id: str
    label: str
    trust_tier: str
    certified: bool
    enabled: bool
    natural_key: str
    summary: str | None = None


class LineageEventOut(BaseModel):
    event_id: str
    action: str
    at: str
    from_tier: str | None = None
    to_tier: str | None = None
    evidence_snapshot: dict[str, Any] | None = None
    actor: dict[str, Any] | None = None


class SaveCaliberIn(BaseModel):
    """V-T3 explicit save — still lands in staging for certify."""

    label: str
    contract_fragment: dict[str, Any]
    field_targets: list[dict[str, Any]] = Field(default_factory=list)
    ds_id: int
    summary: str | None = None
    source_record_id: int | None = None


class DemoteIn(BaseModel):
    to_tier: str = "published"
    reason: str = ""


@router.get("/staging", response_model=list[StagingOut])
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def get_staging(
    session: SessionDep,
    user: CurrentUser,
    kind: str | None = None,
) -> list[StagingOut]:
    rows = list_pending_staging(session, oid=int(user.oid or 1), kind=kind)
    # Also surface conflicts for the ops queue
    conflicts = list(
        session.exec(
            select(KnowledgeStaging)
            .where(KnowledgeStaging.oid == int(user.oid or 1))
            .where(KnowledgeStaging.status == "conflict")
        ).all()
    )
    seen = {r.id for r in rows}
    for row in conflicts:
        if row.id not in seen:
            rows.append(row)
    return [
        StagingOut(
            id=int(r.id),
            kind=r.kind,
            status=r.status,
            natural_key=r.natural_key,
            trigger_id=r.trigger_id,
            lineage_id=r.lineage_id,
            source_record_id=r.source_record_id,
            payload=dict(r.payload or {}),
            scope=dict(r.scope or {}),
        )
        for r in rows
        if r.id is not None
    ]


@router.post("/staging/{staging_id}/certify", response_model=CaliberOut)
@system_log(
    LogConfig(
        operation_type=OperationType.CREATE_OR_UPDATE,
        module=OperationModules.DATASOURCE,
        resource_id_expr="staging_id",
    )
)
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def certify_staging(
    session: SessionDep,
    user: CurrentUser,
    staging_id: int,
) -> CaliberOut:
    try:
        caliber = certify_staging_caliber(
            session,
            staging_id=staging_id,
            actor_user_id=int(user.id) if user.id is not None else None,
            oid=int(user.oid or 1),
        )
        session.commit()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    assert caliber.id is not None
    return CaliberOut(
        id=int(caliber.id),
        lineage_id=caliber.lineage_id,
        label=caliber.label,
        trust_tier=caliber.trust_tier,
        certified=caliber.certified,
        enabled=caliber.enabled,
        natural_key=caliber.natural_key,
        summary=caliber.summary,
    )


@router.post("/caliber/save", response_model=StagingOut)
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def save_caliber(
    session: SessionDep,
    user: CurrentUser,
    body: SaveCaliberIn,
) -> StagingOut:
    """V-T3: explicit save → staging pending (not auto Bind)."""
    from apps.datasource.models.datasource import CoreDatasource

    oid = int(user.oid or 1)
    ds = session.get(CoreDatasource, body.ds_id)
    if ds is None or int(ds.oid or 0) != oid:
        raise HTTPException(status_code=400, detail="datasource not found in workspace")
    staging = admit_candidate(
        session,
        oid=oid,
        kind="caliber",
        trigger_id="V-T3",
        payload={
            "label": body.label,
            "summary": body.summary,
            "contract_fragment": body.contract_fragment,
            "field_targets": body.field_targets,
        },
        scope={"ds_id": body.ds_id},
        source_record_id=body.source_record_id,
        suggested_trust_tier="admitted",
        field_targets=body.field_targets,
    )
    session.commit()
    assert staging.id is not None
    return StagingOut(
        id=int(staging.id),
        kind=staging.kind,
        status=staging.status,
        natural_key=staging.natural_key,
        trigger_id=staging.trigger_id,
        lineage_id=staging.lineage_id,
        source_record_id=staging.source_record_id,
        payload=dict(staging.payload or {}),
        scope=dict(staging.scope or {}),
    )


@router.post("/caliber/{caliber_id}/demote", response_model=CaliberOut)
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def demote(
    session: SessionDep,
    user: CurrentUser,
    caliber_id: int,
    body: DemoteIn,
) -> CaliberOut:
    try:
        caliber = demote_caliber(
            session,
            caliber_id=caliber_id,
            oid=int(user.oid or 1),
            actor_user_id=int(user.id) if user.id is not None else None,
            to_tier=body.to_tier,
            reason=body.reason,
        )
        session.commit()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    assert caliber.id is not None
    return CaliberOut(
        id=int(caliber.id),
        lineage_id=caliber.lineage_id,
        label=caliber.label,
        trust_tier=caliber.trust_tier,
        certified=caliber.certified,
        enabled=caliber.enabled,
        natural_key=caliber.natural_key,
        summary=caliber.summary,
    )


@router.post("/caliber/{caliber_id}/disable", response_model=CaliberOut)
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def disable(
    session: SessionDep,
    user: CurrentUser,
    caliber_id: int,
) -> CaliberOut:
    try:
        caliber = disable_caliber(
            session,
            caliber_id=caliber_id,
            oid=int(user.oid or 1),
            actor_user_id=int(user.id) if user.id is not None else None,
        )
        session.commit()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    assert caliber.id is not None
    return CaliberOut(
        id=int(caliber.id),
        lineage_id=caliber.lineage_id,
        label=caliber.label,
        trust_tier=caliber.trust_tier,
        certified=caliber.certified,
        enabled=caliber.enabled,
        natural_key=caliber.natural_key,
        summary=caliber.summary,
    )


class PromoteTrustedIn(BaseModel):
    reproduce_count: int
    policy_n: int | None = None


@router.post("/caliber/{caliber_id}/promote-trusted", response_model=CaliberOut)
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def promote_trusted(
    session: SessionDep,
    user: CurrentUser,
    caliber_id: int,
    body: PromoteTrustedIn,
) -> CaliberOut:
    # Client-supplied reproduce_count is not trustworthy; server ledger is not
    # wired yet. Do not accept promotions through this path.
    del session, user, caliber_id, body
    raise HTTPException(
        status_code=400,
        detail=(
            "reproduce promotion requires a server-side ledger; "
            "use certify for Bind eligibility"
        ),
    )


@router.get("/assets/{kind}/{asset_id}/lineage", response_model=list[LineageEventOut])
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def get_lineage(
    session: SessionDep,
    user: CurrentUser,
    kind: str,
    asset_id: int,
) -> list[LineageEventOut]:
    oid = int(user.oid or 1)
    lineage_id: str | None = None
    if kind == "caliber":
        caliber = session.get(BusinessCaliber, asset_id)
        if caliber is None or int(caliber.oid) != oid:
            raise HTTPException(status_code=404, detail="asset not found")
        lineage_id = caliber.lineage_id
    elif kind == "staging":
        staging = session.get(KnowledgeStaging, asset_id)
        if staging is None or int(staging.oid) != oid:
            raise HTTPException(status_code=404, detail="asset not found")
        lineage_id = staging.lineage_id
    else:
        raise HTTPException(status_code=404, detail="asset not found")
    events = list_lineage_events(session, lineage_id=lineage_id)
    return [
        LineageEventOut(
            event_id=e.event_id,
            action=e.action,
            at=e.at.isoformat() if e.at else "",
            from_tier=e.from_tier,
            to_tier=e.to_tier,
            evidence_snapshot=e.evidence_snapshot,
            actor=e.actor,
        )
        for e in events
    ]
