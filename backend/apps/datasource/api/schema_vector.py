"""Schema-vector admin: status snapshot + manual sync trigger."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from apps.datasource.embedding.schema_index import (
    get_schema_vector_job,
    list_schema_vector_status,
    start_schema_vector_sync,
)
from apps.system.schemas.permission import SqlbotPermission, require_permissions
from apps.system.schemas.system_schema import UserInfoDTO
from common.core.deps import CurrentUser, SessionDep

router = APIRouter(tags=["SchemaVector"], prefix="/datasource/schema-vector")


class SyncSchemaVectorBody(BaseModel):
    ds_id: int | None = Field(default=None, description="Optional datasource id; omit for all")


def _oid(user: UserInfoDTO) -> int:
    return int(getattr(user, "oid", 1) or 1)


@router.get("/status")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def schema_vector_status(
    session: SessionDep,
    current_user: CurrentUser,
    ds_id: int | None = Query(default=None),
) -> dict[str, Any]:
    rows = list_schema_vector_status(session, oid=_oid(current_user), ds_id=ds_id)
    return {"job": get_schema_vector_job(), "items": rows}


@router.get("/job")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def schema_vector_job() -> dict[str, Any]:
    return get_schema_vector_job()


@router.post("/sync")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def sync_schema_vector(
    current_user: CurrentUser, body: SyncSchemaVectorBody | None = None
) -> dict[str, Any]:
    _ = current_user
    ds_id = body.ds_id if body is not None else None
    scoped = [int(ds_id)] if ds_id is not None else None
    result = start_schema_vector_sync(scoped)
    if not result.get("accepted"):
        raise HTTPException(status_code=409, detail="schema vector sync already running")
    return result
