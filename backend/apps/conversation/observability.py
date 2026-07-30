"""Persistence primitives for the shared conversation audit channel."""

from __future__ import annotations

import datetime
from typing import Any

from sqlalchemy import update
from sqlmodel import Session

from apps.chat.models.chat_model import ChatLog, OperationEnum, TypeEnum


def start_log(
    session: Session,
    ai_modal_id: int | None = None,
    ai_modal_name: str | None = None,
    operate: OperationEnum | None = None,
    record_id: int | None = None,
    full_message: list[dict[str, Any]] | dict[str, Any] | None = None,
    local_operation: bool = False,
) -> ChatLog:
    log = ChatLog(
        type=TypeEnum.CHAT,
        operate=operate,
        pid=record_id,
        ai_modal_id=ai_modal_id,
        base_modal=ai_modal_name,
        messages=full_message,
        start_time=datetime.datetime.now(),
        local_operation=local_operation,
    )
    result = ChatLog(**log.model_dump())
    session.add(log)
    session.flush()
    session.refresh(log)
    result.id = log.id
    session.commit()
    return result


def end_log(
    session: Session,
    log: ChatLog,
    full_message: list[dict[str, Any]] | dict[str, Any] | str,
    reasoning_content: str | None = None,
    token_usage: dict[str, Any] | None = None,
) -> ChatLog:
    log.messages = full_message
    log.token_usage = token_usage or {}
    log.finish_time = datetime.datetime.now()
    log.reasoning_content = (
        reasoning_content if reasoning_content and reasoning_content.strip() else None
    )
    session.execute(
        update(ChatLog)
        .where(ChatLog.id == log.id)
        .values(
            messages=log.messages,
            token_usage=log.token_usage,
            finish_time=log.finish_time,
            reasoning_content=log.reasoning_content,
        )
    )
    session.commit()
    return log


def trigger_log_error(session: Session, log: ChatLog) -> ChatLog:
    log.error = True
    session.execute(update(ChatLog).where(ChatLog.id == log.id).values(error=True))
    session.commit()
    return log
