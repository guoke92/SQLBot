"""Platform-admin live view of this environment's conversations. JWT + isAdmin."""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from apps.chat.models.chat_model import ChatRecord
from apps.conversation.process_timeline import (
    load_dataset_rows,
    project_process_timeline,
)
from apps.dev.batch_export import load_feedback_rows, render_feedback_csv
from apps.dev.catalog import (
    list_chats,
    list_datasources,
    list_operators,
    list_workspaces,
)
from apps.dev.chat_view import get_chat_for_admin
from apps.dev.guards import DevAdmin
from apps.dev.jsonutil import parse_id_list
from apps.dev.qa_export import build_qa_chats_workbook
from common.core.deps import SessionDep, Trans

router = APIRouter(prefix="/qa-admin", tags=["dev-qa-admin"])


def _parse_dt(raw: str | None) -> datetime | None:
    if not raw or not str(raw).strip():
        return None
    text = str(raw).strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        try:
            parsed = datetime.strptime(text[:19], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None
    if parsed.tzinfo is not None:
        return parsed.replace(tzinfo=None)
    return parsed


@router.get("/workspaces")
async def qa_workspaces(
    session: SessionDep, _admin: DevAdmin, trans: Trans
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
async def qa_operators(
    session: SessionDep, _admin: DevAdmin, oid: int = Query(...)
) -> list[dict[str, Any]]:
    return await asyncio.to_thread(list_operators, session, oid)


@router.get("/datasources")
async def qa_datasources(
    session: SessionDep, _admin: DevAdmin, oid: int = Query(...)
) -> list[dict[str, Any]]:
    return await asyncio.to_thread(list_datasources, session, oid)


@router.get("/chats")
async def qa_chats(
    session: SessionDep,
    _admin: DevAdmin,
    oid: int = Query(...),
    create_by: int | None = None,
    q: str | None = None,
    feedback: str | None = None,
    chat_ids: str | None = None,
    datasource: int | None = None,
    created_from: str | None = None,
    created_to: str | None = None,
    chat_type: str | None = Query(
        default="chat",
        description="chat | config | all; default chat excludes config assistant",
    ),
) -> list[dict[str, Any]]:
    ids = parse_id_list(chat_ids)
    resolved_type = None if (chat_type or "").strip().lower() in {"", "all"} else chat_type
    return await asyncio.to_thread(
        list_chats,
        session,
        oid=oid,
        create_by=create_by,
        q=q,
        feedback=feedback,
        chat_ids=ids or None,
        datasource=datasource,
        created_from=_parse_dt(created_from),
        created_to=_parse_dt(created_to),
        chat_type=resolved_type,
    )


@router.get("/chats/{chat_id}")
async def qa_chat_detail(
    session: SessionDep, _admin: DevAdmin, trans: Trans, chat_id: int
) -> Any:
    def inner() -> Any:
        return get_chat_for_admin(session, chat_id, trans=trans)

    return await asyncio.to_thread(inner)


@router.get("/records/{record_id}/timeline")
async def qa_record_timeline(
    session: SessionDep,
    _admin: DevAdmin,
    trans: Trans,
    record_id: int,
    view: str = "compact",
    run_id: str | None = None,
) -> Any:
    record = session.get(ChatRecord, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Turn not found")
    resolved_view = "detail" if view == "detail" else "compact"

    def inner() -> Any:
        return project_process_timeline(
            session,
            record_id=record_id,
            run_id=run_id,
            view=resolved_view,  # type: ignore[arg-type]
            trans=trans,
        )

    return await asyncio.to_thread(inner)


@router.get("/records/{record_id}/datasets/{dataset_id}/rows")
async def qa_record_dataset_rows(
    session: SessionDep,
    _admin: DevAdmin,
    record_id: int,
    dataset_id: str,
    offset: int = 0,
    limit: int = 1000,
) -> dict[str, Any]:
    try:
        return load_dataset_rows(
            session,
            record_id=record_id,
            dataset_id=dataset_id,
            offset=offset,
            limit=limit,
            user_id=None,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/feedback.csv")
async def qa_feedback_csv(
    session: SessionDep,
    _admin: DevAdmin,
    oid: int = Query(...),
    create_by: int | None = None,
    q: str | None = None,
    feedback: str | None = None,
    chat_ids: str | None = None,
    datasource: int | None = None,
    created_from: str | None = None,
    created_to: str | None = None,
    chat_type: str | None = Query(default="chat"),
) -> Response:
    resolved_type = None if (chat_type or "").strip().lower() in {"", "all"} else chat_type

    def inner() -> str:
        _summary, rows = load_feedback_rows(
            session,
            oid=oid,
            create_by=create_by,
            q=q,
            feedback=feedback,
            chat_ids=parse_id_list(chat_ids) or None,
            datasource=datasource,
            created_from=_parse_dt(created_from),
            created_to=_parse_dt(created_to),
            chat_type=resolved_type,
        )
        return render_feedback_csv(rows)

    body = await asyncio.to_thread(inner)
    return Response(
        content=body.encode("utf-8-sig"),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="workspace-{oid}-feedback.csv"'
        },
    )


@router.get("/feedback.xlsx")
async def qa_feedback_xlsx(
    session: SessionDep,
    _admin: DevAdmin,
    oid: int = Query(...),
    create_by: int | None = None,
    q: str | None = None,
    feedback: str | None = None,
    chat_ids: str | None = None,
    datasource: int | None = None,
    created_from: str | None = None,
    created_to: str | None = None,
    chat_type: str | None = Query(default="chat"),
) -> Response:
    """Export chats as review Excel (same columns/rules as exports/export_qa_chats.py)."""
    resolved_type = None if (chat_type or "").strip().lower() in {"", "all"} else chat_type

    def inner() -> bytes:
        body, _stats = build_qa_chats_workbook(
            session,
            oid=oid,
            create_by=create_by,
            q=q,
            feedback=feedback,
            chat_ids=parse_id_list(chat_ids) or None,
            datasource=datasource,
            created_from=_parse_dt(created_from),
            created_to=_parse_dt(created_to),
            chat_type=resolved_type,
        )
        return body

    body = await asyncio.to_thread(inner)
    return Response(
        content=body,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="workspace-{oid}-qa-chats.xlsx"'
        },
    )
