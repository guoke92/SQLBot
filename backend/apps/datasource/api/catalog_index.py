"""Catalog maintenance: value-index extract + default wiki generation."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from apps.datasource.catalog_index import (
    get_catalog_index_job,
    list_catalog_index_status,
    start_default_wiki,
    start_value_index_extract,
)
from apps.system.schemas.permission import SqlbotPermission, require_permissions
from apps.system.schemas.system_schema import UserInfoDTO
from common.core.deps import CurrentUser, SessionDep

router = APIRouter(tags=["CatalogIndex"], prefix="/datasource/catalog-index")


class CatalogIndexBody(BaseModel):
    ds_id: int | None = Field(
        default=None, description="Datasource id; omit extract-all"
    )


def _oid(user: UserInfoDTO) -> int:
    return int(getattr(user, "oid", 1) or 1)


@router.get("/status")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def catalog_index_status(
    session: SessionDep,
    current_user: CurrentUser,
    ds_id: int | None = Query(default=None),
) -> dict[str, Any]:
    rows = list_catalog_index_status(session, oid=_oid(current_user), ds_id=ds_id)
    return {"job": get_catalog_index_job(), "items": rows}


@router.get("/job")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def catalog_index_job() -> dict[str, Any]:
    return get_catalog_index_job()


@router.post("/extract-values")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def extract_values(
    current_user: CurrentUser, body: CatalogIndexBody | None = None
) -> dict[str, Any]:
    _ = current_user
    ds_id = body.ds_id if body is not None else None
    scoped = [int(ds_id)] if ds_id is not None else None
    result = start_value_index_extract(scoped, oid=_oid(current_user))
    if not result.get("accepted"):
        raise HTTPException(status_code=409, detail="catalog index job already running")
    return result


@router.post("/generate-wiki")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def generate_wiki(
    current_user: CurrentUser, body: CatalogIndexBody
) -> dict[str, Any]:
    if body.ds_id is None:
        raise HTTPException(status_code=400, detail="ds_id is required")
    result = start_default_wiki(int(body.ds_id), oid=_oid(current_user))
    if not result.get("accepted"):
        raise HTTPException(status_code=409, detail="catalog index job already running")
    return result
