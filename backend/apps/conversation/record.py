"""Single persistence boundary for conversation record lifecycle."""

from __future__ import annotations

import datetime
from typing import Any

from sqlalchemy import and_, update
from sqlmodel import Session

from apps.chat.models.chat_model import ChatLog, ChatRecord


def persist_snapshot(
    session: Session,
    record_id: int,
    *,
    data: str | None = None,
    sql: str | None = None,
    chart: str | None = None,
    re_exec: str | None = None,
    analysis: str | None = None,
    sql_answer: str | None = None,
    intent_context: dict[str, Any] | None = None,
    terminal: bool = False,
    error: str | None = None,
) -> bool:
    """Persist one progressive or terminal snapshot in a single transaction.

    Updates apply only while the record is unfinished, so the first terminal
    writer wins and later success/failure callbacks cannot overwrite it.
    """
    if not record_id:
        raise ValueError("Record id cannot be None")

    values: dict[str, object] = {}
    for field, value in (
        ("data", data),
        ("sql", sql),
        ("chart", chart),
        ("re_exec", re_exec),
        ("analysis", analysis),
        ("sql_answer", sql_answer),
        ("intent_context", intent_context),
    ):
        if value is not None:
            values[field] = value

    finish_time: datetime.datetime | None = None
    if terminal:
        finish_time = datetime.datetime.now()
        values.update(
            {
                "finish": True,
                "finish_time": finish_time,
            }
        )
        if error is not None:
            values["error"] = error

    applied = False
    if values:
        result = session.execute(
            update(ChatRecord)
            .where(
                and_(
                    ChatRecord.id == record_id,
                    ChatRecord.finish.is_not(True),
                )
            )
            .values(**values)
        )
        applied = bool(getattr(result, "rowcount", 0))

    if applied and terminal and error is not None and finish_time is not None:
        session.execute(
            update(ChatLog)
            .where(
                and_(
                    ChatLog.pid == record_id,
                    ChatLog.finish_time.is_(None),
                )
            )
            .values(finish_time=finish_time, error=True)
        )

    session.commit()
    return applied
