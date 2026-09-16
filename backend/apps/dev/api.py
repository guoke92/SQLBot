"""Mount all /api/v1/dev routes: extract-key (admin JWT), extract (key), qa-admin (admin JWT)."""

from __future__ import annotations

import asyncio
from typing import Any

from fastapi import APIRouter

from apps.dev import extract_api, qa_admin_api
from apps.dev.extract_key import get_key_row, public_key_info, revoke_key, rotate_key
from apps.dev.guards import DevAdmin
from common.core.deps import SessionDep

router = APIRouter(prefix="/dev", tags=["dev"])
router.include_router(extract_api.router)
router.include_router(qa_admin_api.router)


@router.get("/extract-key")
async def get_extract_key(
    session: SessionDep, _admin: DevAdmin
) -> dict[str, Any] | None:
    def inner() -> dict[str, Any] | None:
        return public_key_info(get_key_row(session))

    return await asyncio.to_thread(inner)


@router.post("/extract-key")
async def create_extract_key(
    session: SessionDep, _admin: DevAdmin
) -> dict[str, Any]:
    def inner() -> dict[str, Any]:
        plaintext = rotate_key(session, int(_admin.id))
        info = public_key_info(get_key_row(session)) or {}
        return {**info, "key": plaintext}

    return await asyncio.to_thread(inner)


@router.delete("/extract-key")
async def delete_extract_key(
    session: SessionDep, _admin: DevAdmin
) -> dict[str, bool]:
    await asyncio.to_thread(revoke_key, session)
    return {"ok": True}
