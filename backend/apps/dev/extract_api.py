"""Login-free extract surface for coding agents. Auth is X-SQLBOT-EXTRACT-KEY only."""

from __future__ import annotations

import asyncio
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from apps.dev.catalog import list_chats, list_operators, list_workspaces
from apps.dev.jsonutil import parse_id_list
from apps.dev.pack import build_conversation_pack
from common.core.deps import SessionDep, Trans

router = APIRouter(prefix="/extract", tags=["dev-extract"])


@router.get("/workspaces")
async def extract_workspaces(
    session: SessionDep, trans: Trans
) -> list[dict[str, Any]]:
    def inner() -> list[dict[str, Any]]:
        rows = list_workspaces(session)
        for row in rows:
            name = str(row.get("name") or "")
            if name.startswith("i18n"):
                row["name"] = trans(name)
        return rows

    return await asyncio.to_thread(inner)


@router.get("/operators")
async def extract_operators(
    session: SessionDep, oid: int = Query(...)
) -> list[dict[str, Any]]:
    return await asyncio.to_thread(list_operators, session, oid)


@router.get("/chats")
async def extract_chats(
    session: SessionDep,
    oid: int = Query(...),
    create_by: int | None = None,
    q: str | None = None,
    feedback: str | None = None,
    chat_ids: str | None = None,
) -> list[dict[str, Any]]:
    ids = parse_id_list(chat_ids)
    return await asyncio.to_thread(
        list_chats,
        session,
        oid=oid,
        create_by=create_by,
        q=q,
        feedback=feedback,
        chat_ids=ids or None,
    )


@router.get("/chats/{chat_id}")
async def extract_chat_pack(
    session: SessionDep, trans: Trans, chat_id: int
) -> dict[str, Any]:
    def inner() -> dict[str, Any]:
        try:
            return build_conversation_pack(session, chat_id, trans=trans)
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    return await asyncio.to_thread(inner)
