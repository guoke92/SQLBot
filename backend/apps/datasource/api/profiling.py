"""HTTP API for metadata cognition briefs, scans, and relation confirmation."""

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from sqlmodel import select

from apps.datasource.models.datasource import CoreDatasource, CoreTable
from apps.datasource.profiling.models import (
    FieldRelation,
    MetadataScanRun,
    RelationStatus,
    ScanRunMode,
)
from apps.datasource.profiling.service import (
    ALLOWED_RUN_MODES,
    build_profile_brief,
    decide_field_relation,
    enqueue_manual_refresh,
    get_published_relations,
    schedule_worker_kick,
)
from apps.system.schemas.permission import SqlbotPermission, require_permissions
from common.core.deps import CurrentUser, SessionDep, Trans

router = APIRouter(tags=["MetadataProfiling"], prefix="/datasource/profiling")


class RefreshProfileRequest(BaseModel):
    table_ids: list[int] = Field(default_factory=list)
    run_mode: str = ScanRunMode.FACTS_ONLY.value


class RelationDecisionRequest(BaseModel):
    status: str


class MiningPolicyRequest(BaseModel):
    """preset=lite|standard|deep|custom; capabilities required when custom; inherit for tables."""

    preset: str | None = None
    capabilities: list[str] | None = None
    inherit: bool = False


@router.get("/capabilities")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def list_capabilities(
    session: SessionDep,
    user: CurrentUser,
) -> dict[str, Any]:
    from apps.datasource.profiling.capability_catalog import CAPABILITIES, PRESETS

    _ = session, user
    return {
        "capabilities": [
            {
                "id": spec.id,
                "pipe": spec.pipe,
                "depends_on": list(spec.depends_on),
                "recall_targets": list(spec.recall_targets),
                "tools": list(spec.tools),
                "description": spec.description,
            }
            for spec in CAPABILITIES.values()
        ],
        "presets": {name: sorted(caps) for name, caps in PRESETS.items()},
    }


@router.get("/policy/{ds_id}")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def get_mining_policy(
    session: SessionDep,
    user: CurrentUser,
    ds_id: int,
    table_id: int | None = Query(default=None),
) -> dict[str, Any]:
    from apps.datasource.profiling.policy import policy_to_public_dict
    from apps.datasource.profiling.service import resolve_table_mining_policy

    ds = _require_ds(session, user, ds_id)
    if table_id is None:
        from apps.datasource.profiling.policy import resolve_mining_policy

        policy = resolve_mining_policy(ds_policy=getattr(ds, "mining_policy", None))
        return {
            "ds_id": ds_id,
            "stored": getattr(ds, "mining_policy", None),
            "effective": policy_to_public_dict(policy),
        }
    table = session.get(CoreTable, table_id)
    if table is None or int(table.ds_id) != int(ds.id):
        raise HTTPException(status_code=404, detail="table not found")
    policy = resolve_table_mining_policy(session, ds=ds, table=table)
    return {
        "ds_id": ds_id,
        "table_id": table_id,
        "stored": getattr(table, "mining_policy", None),
        "effective": policy_to_public_dict(policy),
    }


@router.put("/policy/{ds_id}")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def put_mining_policy(
    session: SessionDep,
    user: CurrentUser,
    ds_id: int,
    body: MiningPolicyRequest,
    table_id: int | None = Query(default=None),
) -> dict[str, Any]:
    from apps.datasource.profiling.capability_catalog import expand_capabilities
    from apps.datasource.profiling.policy import policy_to_public_dict, resolve_mining_policy
    from apps.datasource.profiling.service import resolve_table_mining_policy

    ds = _require_ds(session, user, ds_id)
    if body.inherit and table_id is None:
        raise HTTPException(status_code=400, detail="inherit only valid for table policy")
    if body.inherit:
        doc: dict[str, Any] = {"inherit": True}
    else:
        preset = (body.preset or "standard").strip().lower()
        doc = {"preset": preset}
        if body.capabilities is not None:
            try:
                expand_capabilities(body.capabilities)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
            doc["capabilities"] = list(body.capabilities)
        if preset == "custom" and not body.capabilities:
            raise HTTPException(
                status_code=400, detail="custom preset requires capabilities"
            )
    if table_id is None:
        ds.mining_policy = doc
        session.add(ds)
        session.commit()
        session.refresh(ds)
        policy = resolve_mining_policy(ds_policy=ds.mining_policy)
        return {"ds_id": ds_id, "stored": ds.mining_policy, "effective": policy_to_public_dict(policy)}
    table = session.get(CoreTable, table_id)
    if table is None or int(table.ds_id) != int(ds.id):
        raise HTTPException(status_code=404, detail="table not found")
    table.mining_policy = doc
    session.add(table)
    session.commit()
    session.refresh(table)
    policy = resolve_table_mining_policy(session, ds=ds, table=table)
    return {
        "ds_id": ds_id,
        "table_id": table_id,
        "stored": table.mining_policy,
        "effective": policy_to_public_dict(policy),
    }


@router.get("/brief/{ds_id}")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def get_brief(
    session: SessionDep,
    user: CurrentUser,
    ds_id: int,
    table_id: int | None = Query(default=None),
    include_top_values: bool = Query(default=False),
) -> dict[str, Any]:
    ds = _require_ds(session, user, ds_id)
    table_ids = [table_id] if table_id is not None else None
    return build_profile_brief(
        session,
        ds_id=int(ds.id),
        table_ids=table_ids,
        include_top_values=include_top_values,
    )


@router.get("/runs/{ds_id}")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def list_runs(
    session: SessionDep,
    user: CurrentUser,
    ds_id: int,
    limit: int = Query(default=50, ge=1, le=200),
) -> list[dict[str, Any]]:
    _require_ds(session, user, ds_id)
    rows = session.exec(
        select(MetadataScanRun)
        .where(MetadataScanRun.ds_id == ds_id)
        .order_by(MetadataScanRun.id.desc())
        .limit(limit)
    ).all()
    return [
        {
            "id": r.id,
            "table_id": r.table_id,
            "run_mode": r.run_mode,
            "trigger": r.trigger,
            "status": r.status,
            "attempt": r.attempt,
            "error": r.error,
            "schema_fingerprint": r.schema_fingerprint,
            "create_time": r.create_time,
            "finished_at": r.finished_at,
        }
        for r in rows
    ]


@router.post("/refresh/{ds_id}")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def refresh_profiles(
    session: SessionDep,
    user: CurrentUser,
    ds_id: int,
    body: RefreshProfileRequest,
) -> dict[str, Any]:
    ds = _require_ds(session, user, ds_id)
    mode = (body.run_mode or ScanRunMode.FACTS_ONLY.value).strip()
    if mode not in ALLOWED_RUN_MODES:
        raise HTTPException(status_code=400, detail=f"invalid run_mode {mode}")
    stmt = select(CoreTable).where(CoreTable.ds_id == ds_id, CoreTable.checked == True)  # noqa: E712
    tables = list(session.exec(stmt).all())
    if body.table_ids:
        wanted = {int(tid) for tid in body.table_ids}
        tables = [t for t in tables if t.id is not None and int(t.id) in wanted]
    try:
        runs = enqueue_manual_refresh(
            session, ds=ds, tables=tables, run_mode=mode
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    schedule_worker_kick()
    return {
        "enqueued": len(runs),
        "run_ids": [r.id for r in runs],
        "run_mode": mode,
    }


@router.get("/relations/{ds_id}")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def list_relations(
    session: SessionDep,
    user: CurrentUser,
    ds_id: int,
    status: str | None = Query(default=None),
) -> list[dict[str, Any]]:
    _require_ds(session, user, ds_id)
    statuses = [status] if status else [
        RelationStatus.CANDIDATE.value,
        RelationStatus.CONFIRMED.value,
    ]
    rows = get_published_relations(session, ds_id=ds_id, statuses=statuses)
    return [
        {
            "id": r.id,
            "kind": r.kind,
            "status": r.status,
            "source": r.source,
            "confidence": r.confidence,
            "source_table_id": r.source_table_id,
            "source_field_id": r.source_field_id,
            "target_table_id": r.target_table_id,
            "target_field_id": r.target_field_id,
            "evidence": r.evidence,
        }
        for r in rows
    ]


@router.post("/relations/{relation_id}/decision")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def decide_relation(
    session: SessionDep,
    user: CurrentUser,
    relation_id: int,
    body: RelationDecisionRequest,
    trans: Trans,
) -> dict[str, Any]:
    row = session.get(FieldRelation, relation_id)
    if row is None:
        raise HTTPException(status_code=404, detail="relation not found")
    _require_ds(session, user, int(row.ds_id))
    try:
        updated = decide_field_relation(
            session,
            relation_id=relation_id,
            status=body.status,
            confirmed_by=int(user.id),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"id": updated.id, "status": updated.status}


def _require_ds(session: SessionDep, user: CurrentUser, ds_id: int) -> CoreDatasource:
    ds = session.get(CoreDatasource, ds_id)
    if ds is None or int(ds.oid or 1) != int(getattr(user, "oid", None) or 1):
        raise HTTPException(status_code=404, detail="Datasource not found")
    return ds
