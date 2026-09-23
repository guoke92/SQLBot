"""Lightweight feedback CSV/Markdown projected from chat records."""

from __future__ import annotations

import csv
import io
from datetime import datetime
from typing import Any

from sqlmodel import Session, select

from apps.chat.models.chat_model import ChatRecord
from apps.dev.catalog import list_chats
from apps.system.models.system_model import WorkspaceModel
from apps.system.models.user import UserModel

FEEDBACK_CSV_COLUMNS = [
    "chat_id",
    "brief",
    "record_id",
    "user_account",
    "user_name",
    "create_time",
    "question",
    "feedback",
    "feedback_comment",
    "feedback_revision",
    "finish",
    "error",
    "sql",
]


def _iso(value: datetime | None) -> str:
    if value is None:
        return ""
    return value.isoformat()


def _trunc(value: Any, limit: int) -> str:
    text = "" if value is None else str(value)
    if len(text) <= limit:
        return text
    return text[:limit] + "…"


def extract_record_sql(record: ChatRecord) -> str:
    raw = str(getattr(record, "sql", None) or "").strip()
    if raw:
        return raw
    answer = getattr(record, "answer", None)
    if not isinstance(answer, dict):
        return ""
    chunks: list[str] = []
    seen: set[str] = set()
    for key in ("datasets", "source_datasets", "steps"):
        items = answer.get(key) or []
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            sql = str(item.get("sql") or "").strip()
            if sql and sql not in seen:
                seen.add(sql)
                chunks.append(sql)
    return "\n\n".join(chunks)


def load_feedback_rows(
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
    chat_type: str | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    chats = list_chats(
        session,
        oid=oid,
        create_by=create_by,
        q=q,
        feedback=feedback,
        chat_ids=chat_ids,
        datasource=datasource,
        created_from=created_from,
        created_to=created_to,
        chat_type=chat_type,
    )
    ids = [int(item["id"]) for item in chats]
    workspace = session.get(WorkspaceModel, oid)
    if not ids:
        return (
            {
                "oid": oid,
                "workspace_name": workspace.name if workspace is not None else None,
                "chat_count": 0,
                "record_count": 0,
                "feedback_up": 0,
                "feedback_down": 0,
                "feedback_down_with_comment": 0,
            },
            [],
        )

    stmt = (
        select(ChatRecord)
        .where(
            ChatRecord.chat_id.in_(ids),
            ChatRecord.feedback.in_(["up", "down"]),
        )
        .order_by(ChatRecord.chat_id, ChatRecord.create_time, ChatRecord.id)
    )
    if feedback == "up":
        stmt = stmt.where(ChatRecord.feedback == "up")
    elif feedback == "down":
        stmt = stmt.where(ChatRecord.feedback == "down")
    records = list(session.exec(stmt).all())
    user_ids = {int(row.create_by) for row in records if row.create_by is not None}
    users: dict[int, UserModel] = {}
    if user_ids:
        for user in session.exec(
            select(UserModel).where(UserModel.id.in_(list(user_ids)))
        ).all():
            if user.id is not None:
                users[int(user.id)] = user
    chat_by_id = {int(item["id"]): item for item in chats}

    rows: list[dict[str, Any]] = []
    up = down = commented = 0
    for record in records:
        chat = chat_by_id.get(int(record.chat_id or 0), {})
        owner = users.get(int(record.create_by or 0))
        if record.feedback == "up":
            up += 1
        elif record.feedback == "down":
            down += 1
            if record.feedback_comment:
                commented += 1
        rows.append(
            {
                "chat_id": record.chat_id,
                "brief": chat.get("brief") or "",
                "record_id": record.id,
                "user_account": (
                    owner.account if owner is not None else chat.get("user_account")
                )
                or "",
                "user_name": (
                    owner.name if owner is not None else chat.get("user_name")
                )
                or "",
                "create_time": _iso(record.create_time),
                "question": record.question or "",
                "feedback": record.feedback or "",
                "feedback_comment": record.feedback_comment or "",
                "feedback_revision": int(record.feedback_revision or 0),
                "finish": bool(record.finish),
                "error": record.error or "",
                "sql": extract_record_sql(record),
            }
        )
    summary = {
        "oid": oid,
        "workspace_name": workspace.name if workspace is not None else None,
        "chat_count": len(chats),
        "record_count": len(rows),
        "feedback_up": up,
        "feedback_down": down,
        "feedback_down_with_comment": commented,
    }
    return summary, rows


def render_feedback_csv(rows: list[dict[str, Any]]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(
        buffer, fieldnames=FEEDBACK_CSV_COLUMNS, extrasaction="ignore"
    )
    writer.writeheader()
    for row in rows:
        writer.writerow({key: row.get(key, "") for key in FEEDBACK_CSV_COLUMNS})
    return buffer.getvalue()


def render_feedback_markdown(
    summary: dict[str, Any], rows: list[dict[str, Any]]
) -> str:
    lines = [
        f"# Workspace {summary.get('oid')} — {summary.get('workspace_name') or ''}",
        "",
        f"- chats: **{summary.get('chat_count', 0)}**",
        f"- records: **{summary.get('record_count', 0)}**",
        f"- 有帮助: **{summary.get('feedback_up', 0)}**",
        f"- 没帮助: **{summary.get('feedback_down', 0)}**"
        f"  （含描述 {summary.get('feedback_down_with_comment', 0)}）",
        "",
        "## 反馈明细",
    ]
    voted = [row for row in rows if row.get("feedback")]
    if not voted:
        lines.append("（没有有帮助/没帮助反馈）")
    else:
        for row in voted:
            mark = "有帮助" if row.get("feedback") == "up" else "没帮助"
            lines.append("")
            lines.append(
                f"### {mark} chat `{row.get('chat_id')}` / record `{row.get('record_id')}`"
            )
            who = row.get("user_name") or row.get("user_account") or ""
            lines.append(f"- user: `{who}`  time: `{row.get('create_time')}`")
            lines.append(f"- question: {_trunc(row.get('question'), 240)}")
            if row.get("feedback") == "down":
                lines.append(
                    f"- comment: {_trunc(row.get('feedback_comment') or '（无描述）', 800)}"
                )
            if row.get("sql"):
                lines.append(f"- sql: `{_trunc(row.get('sql'), 400)}`")
            if row.get("error"):
                lines.append(f"- error: {_trunc(row.get('error'), 400)}")
    return "\n".join(lines) + "\n"
