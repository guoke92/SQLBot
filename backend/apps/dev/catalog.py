"""Workspace / operator / chat indexes for extract and qa-admin."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import and_, case, func
from sqlmodel import Session, select

from apps.chat.models.chat_model import Chat, ChatRecord
from apps.datasource.models.datasource import CoreDatasource
from apps.dev.jsonutil import jsonable
from apps.system.models.system_model import UserWsModel, WorkspaceModel
from apps.system.models.user import UserModel


def _as_int_ids(values: list[Any]) -> list[int]:
    out: list[int] = []
    seen: set[int] = set()
    for value in values:
        if value is None:
            continue
        if isinstance(value, tuple):
            value = value[0]
        if value is None:
            continue
        parsed = int(value)
        if parsed in seen:
            continue
        seen.add(parsed)
        out.append(parsed)
    return out


def list_workspaces(session: Session) -> list[dict[str, Any]]:
    rows = session.exec(
        select(WorkspaceModel.id, WorkspaceModel.name, WorkspaceModel.create_time).order_by(
            WorkspaceModel.name, WorkspaceModel.create_time
        )
    ).all()
    result: list[dict[str, Any]] = []
    seen: set[int] = set()
    for workspace_id, name, create_time in rows:
        if workspace_id is None:
            continue
        oid = int(workspace_id)
        seen.add(oid)
        result.append({"id": str(oid), "name": name, "create_time": create_time})
    chat_oids = _as_int_ids(list(session.exec(select(Chat.oid).distinct()).all()))
    for oid in chat_oids:
        if oid in seen:
            continue
        result.append({"id": str(oid), "name": f"#{oid}", "create_time": 0})
    return result


def list_operators(session: Session, oid: int) -> list[dict[str, Any]]:
    member_ids = _as_int_ids(
        list(session.exec(select(UserWsModel.uid).where(UserWsModel.oid == oid)).all())
    )
    chat_user_ids = _as_int_ids(
        list(session.exec(select(Chat.create_by).where(Chat.oid == oid).distinct()).all())
    )
    user_ids = sorted(set(member_ids) | set(chat_user_ids))
    if not user_ids:
        return []
    users = session.exec(
        select(UserModel).where(UserModel.id.in_(user_ids)).order_by(UserModel.account)
    ).all()
    return [
        {"id": str(int(user.id)), "account": user.account, "name": user.name}
        for user in users
        if user.id is not None
    ]


def list_datasources(session: Session, oid: int) -> list[dict[str, Any]]:
    chat_ds_ids = _as_int_ids(
        list(session.exec(select(Chat.datasource).where(Chat.oid == oid).distinct()).all())
    )
    workspace_ds_ids = _as_int_ids(
        list(
            session.exec(
                select(CoreDatasource.id).where(CoreDatasource.oid == oid)
            ).all()
        )
    )
    ds_ids = sorted(set(chat_ds_ids) | set(workspace_ds_ids))
    if not ds_ids:
        return []
    rows = session.exec(
        select(CoreDatasource).where(CoreDatasource.id.in_(ds_ids)).order_by(CoreDatasource.name)
    ).all()
    seen: set[int] = set()
    result: list[dict[str, Any]] = []
    for ds in rows:
        if ds.id is None:
            continue
        seen.add(int(ds.id))
        result.append({"id": str(int(ds.id)), "name": ds.name})
    for ds_id in ds_ids:
        if ds_id in seen:
            continue
        result.append({"id": str(ds_id), "name": f"#{ds_id}"})
    return result


def list_chats(
    session: Session,
    *,
    oid: int,
    create_by: int | None = None,
    q: str | None = None,
    feedback: str | None = None,
    chat_ids: list[int] | None = None,
    datasource: int | None = None,
    created_from: datetime | None = None,
    created_to: datetime | None = None,
) -> list[dict[str, Any]]:
    stats = (
        select(
            ChatRecord.chat_id.label("chat_id"),
            func.count(ChatRecord.id).label("record_count"),
            func.max(ChatRecord.create_time).label("last_time"),
            func.coalesce(
                func.sum(case((ChatRecord.feedback == "up", 1), else_=0)), 0
            ).label("feedback_up"),
            func.coalesce(
                func.sum(case((ChatRecord.feedback == "down", 1), else_=0)), 0
            ).label("feedback_down"),
            func.coalesce(
                func.sum(
                    case(
                        (
                            and_(
                                ChatRecord.error.is_not(None),
                                func.length(func.coalesce(ChatRecord.error, "")) > 0,
                            ),
                            1,
                        ),
                        else_=0,
                    )
                ),
                0,
            ).label("error_count"),
        )
        .group_by(ChatRecord.chat_id)
        .subquery()
    )
    stmt = (
        select(
            Chat,
            UserModel,
            stats.c.record_count,
            stats.c.last_time,
            stats.c.feedback_up,
            stats.c.feedback_down,
            stats.c.error_count,
            CoreDatasource.name,
        )
        .join(stats, stats.c.chat_id == Chat.id, isouter=True)
        .join(UserModel, UserModel.id == Chat.create_by, isouter=True)
        .join(CoreDatasource, CoreDatasource.id == Chat.datasource, isouter=True)
        .where(Chat.oid == oid)
        .order_by(Chat.create_time.desc(), Chat.id.desc())
    )
    if create_by is not None:
        stmt = stmt.where(Chat.create_by == create_by)
    if datasource is not None:
        stmt = stmt.where(Chat.datasource == datasource)
    if created_from is not None:
        stmt = stmt.where(Chat.create_time >= created_from)
    if created_to is not None:
        stmt = stmt.where(Chat.create_time <= created_to)
    if chat_ids:
        stmt = stmt.where(Chat.id.in_(chat_ids))
    if q and q.strip():
        pattern = f"%{q.strip()}%"
        stmt = stmt.where(Chat.brief.ilike(pattern))
    if feedback == "up":
        stmt = stmt.where(func.coalesce(stats.c.feedback_up, 0) > 0)
    elif feedback == "down":
        stmt = stmt.where(func.coalesce(stats.c.feedback_down, 0) > 0)
    elif feedback in {"any", "voted"}:
        stmt = stmt.where(
            (func.coalesce(stats.c.feedback_up, 0) + func.coalesce(stats.c.feedback_down, 0)) > 0
        )
    elif feedback == "none":
        stmt = stmt.where(
            (func.coalesce(stats.c.feedback_up, 0) + func.coalesce(stats.c.feedback_down, 0)) == 0
        )
    elif feedback == "error":
        stmt = stmt.where(stats.c.error_count > 0)

    rows: list[dict[str, Any]] = []
    for (
        chat,
        user,
        record_count,
        last_time,
        feedback_up,
        feedback_down,
        error_count,
        datasource_name,
    ) in session.execute(stmt).all():
        if chat.id is None:
            continue
        rows.append(
            jsonable(
                {
                    "id": str(int(chat.id)),
                    "brief": chat.brief,
                    "chat_type": chat.chat_type,
                    "datasource": (
                        str(int(chat.datasource)) if chat.datasource is not None else None
                    ),
                    "datasource_name": datasource_name,
                    "engine_type": chat.engine_type,
                    "create_by": str(int(chat.create_by)) if chat.create_by is not None else None,
                    "user_account": user.account if user is not None else None,
                    "user_name": user.name if user is not None else None,
                    "create_time": chat.create_time,
                    "last_time": last_time or chat.create_time,
                    "record_count": int(record_count or 0),
                    "feedback_up": int(feedback_up or 0),
                    "feedback_down": int(feedback_down or 0),
                    "has_error": int(error_count or 0) > 0,
                }
            )
        )
    return rows
