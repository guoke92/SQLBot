"""Workspace-scoped chat + feedback export (admin / ws_admin)."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any

from sqlmodel import Session, select

from apps.chat.models.chat_model import Chat, ChatRecord
from apps.system.models.system_model import WorkspaceModel
from apps.system.models.user import UserModel


def resolve_export_oid(current_user: Any, oid: int | None) -> int:
    """Admin may pick any workspace; ws_admin is limited to the current oid."""
    current = int(getattr(current_user, "oid", 1) or 1)
    if oid is None:
        return current
    target = int(oid)
    if bool(getattr(current_user, "isAdmin", False)):
        return target
    if target != current:
        raise PermissionError("ws_admin can only export the current workspace")
    return target


def _iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.isoformat()


def serialize_record_for_export(
    record: ChatRecord, *, include_sql: bool = True
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "id": record.id,
        "chat_id": record.chat_id,
        "create_by": record.create_by,
        "create_time": _iso(record.create_time),
        "finish_time": _iso(record.finish_time),
        "question": record.question,
        "finish": bool(record.finish),
        "error": record.error,
        "feedback": record.feedback,
        "feedback_comment": record.feedback_comment,
        "feedback_revision": int(record.feedback_revision or 0),
    }
    if include_sql:
        row["sql"] = record.sql
    return row


def build_workspace_chat_export(
    session: Session,
    *,
    oid: int,
    feedback_only: bool = False,
    include_sql: bool = True,
) -> dict[str, Any]:
    workspace = session.get(WorkspaceModel, oid)
    chats = session.exec(
        select(Chat).where(Chat.oid == oid).order_by(Chat.create_time.desc(), Chat.id)
    ).all()
    chat_ids = [int(chat.id) for chat in chats if chat.id is not None]
    records: list[ChatRecord] = []
    if chat_ids:
        stmt = (
            select(ChatRecord)
            .where(ChatRecord.chat_id.in_(chat_ids))
            .order_by(ChatRecord.create_time, ChatRecord.id)
        )
        if feedback_only:
            stmt = stmt.where(ChatRecord.feedback.is_not(None))
        records = list(session.exec(stmt).all())

    user_ids = {
        int(uid)
        for uid in [*(chat.create_by for chat in chats), *(rec.create_by for rec in records)]
        if uid is not None
    }
    users: dict[int, dict[str, Any]] = {}
    if user_ids:
        for row in session.exec(
            select(UserModel.id, UserModel.account, UserModel.name).where(
                UserModel.id.in_(list(user_ids))
            )
        ).all():
            users[int(row[0])] = {"id": int(row[0]), "account": row[1], "name": row[2]}

    by_chat: dict[int, list[dict[str, Any]]] = defaultdict(list)
    up = down = commented = 0
    for record in records:
        item = serialize_record_for_export(record, include_sql=include_sql)
        owner = users.get(int(record.create_by or 0))
        item["user_account"] = (owner or {}).get("account")
        item["user_name"] = (owner or {}).get("name")
        by_chat[int(record.chat_id)].append(item)
        if record.feedback == "up":
            up += 1
        elif record.feedback == "down":
            down += 1
            if record.feedback_comment:
                commented += 1

    chat_rows: list[dict[str, Any]] = []
    for chat in chats:
        cid = int(chat.id or 0)
        recs = by_chat.get(cid, [])
        if feedback_only and not recs:
            continue
        owner = users.get(int(chat.create_by or 0))
        chat_rows.append(
            {
                "id": cid,
                "brief": chat.brief,
                "chat_type": chat.chat_type,
                "datasource": chat.datasource,
                "engine_type": chat.engine_type,
                "create_by": chat.create_by,
                "user_account": (owner or {}).get("account"),
                "user_name": (owner or {}).get("name"),
                "create_time": _iso(chat.create_time),
                "record_count": len(recs),
                "records": recs,
            }
        )

    return {
        "oid": oid,
        "workspace_name": workspace.name if workspace is not None else None,
        "feedback_only": feedback_only,
        "include_sql": include_sql,
        "summary": {
            "chat_count": len(chat_rows),
            "record_count": len(records),
            "feedback_up": up,
            "feedback_down": down,
            "feedback_down_with_comment": commented,
        },
        "chats": chat_rows,
    }
