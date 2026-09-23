"""Independent raw LLM call capture (request body + merged response/thinking).

Not part of chat_log / process-timeline audit. Persistence failures never
affect the LLM call itself.
"""

from __future__ import annotations

import datetime
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any

from sqlalchemy import BigInteger, Column, DateTime, Identity, Text, update
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import sessionmaker
from sqlmodel import Field, Session, SQLModel

from common.core.db import engine
from common.utils.utils import SQLBotLogUtil

_chat_id: ContextVar[int | None] = ContextVar("llm_call_log_chat_id", default=None)
_chat_record_id: ContextVar[int | None] = ContextVar(
    "llm_call_log_chat_record_id", default=None
)
_session_factory = sessionmaker(bind=engine, class_=Session)


class LlmCallLog(SQLModel, table=True):
    __tablename__ = "llm_call_log"

    id: int | None = Field(
        default=None,
        sa_column=Column(BigInteger, Identity(always=True), primary_key=True),
    )
    chat_id: int | None = Field(
        default=None, sa_column=Column(BigInteger, nullable=True, index=True)
    )
    chat_record_id: int | None = Field(
        default=None, sa_column=Column(BigInteger, nullable=True, index=True)
    )
    request_payload: Any = Field(sa_column=Column(JSONB, nullable=False))
    response_content: str | None = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    reasoning_content: str | None = Field(
        default=None, sa_column=Column(Text, nullable=True)
    )
    error: str | None = Field(default=None, sa_column=Column(Text, nullable=True))
    start_time: datetime.datetime = Field(
        sa_column=Column(DateTime(timezone=False), nullable=False)
    )
    finish_time: datetime.datetime | None = Field(
        default=None, sa_column=Column(DateTime(timezone=False), nullable=True)
    )


@contextmanager
def llm_call_log_scope(
    *,
    chat_id: int | None = None,
    chat_record_id: int | None = None,
) -> Iterator[None]:
    """Bind chat/record ids for LLM calls in this context."""
    chat_token = _chat_id.set(chat_id)
    record_token = _chat_record_id.set(chat_record_id)
    try:
        yield
    finally:
        _chat_record_id.reset(record_token)
        _chat_id.reset(chat_token)


def current_llm_call_refs() -> tuple[int | None, int | None]:
    return _chat_id.get(), _chat_record_id.get()


def _jsonable(value: Any) -> Any:
    """Best-effort JSON coercion for JSONB; no business-field rewriting."""
    try:
        import orjson

        return orjson.loads(orjson.dumps(value, default=str))
    except Exception:
        return {"_unserializable": str(value)}


def begin_llm_call_log(request_payload: Any) -> int | None:
    """Insert one row with the raw request body before the provider call."""
    chat_id, chat_record_id = current_llm_call_refs()
    session = _session_factory()
    try:
        row = LlmCallLog(
            chat_id=chat_id,
            chat_record_id=chat_record_id,
            request_payload=_jsonable(request_payload),
            start_time=datetime.datetime.now(),
        )
        session.add(row)
        session.commit()
        session.refresh(row)
        return int(row.id) if row.id is not None else None
    except Exception as exc:  # noqa: BLE001
        session.rollback()
        SQLBotLogUtil.warning("llm_call_log begin failed: %s", exc)
        return None
    finally:
        session.close()


def finish_llm_call_log(
    log_id: int | None,
    *,
    response_content: str | None = None,
    reasoning_content: str | None = None,
    error: str | None = None,
) -> None:
    """Fill merged response / thinking (or error) on the pending row."""
    if log_id is None:
        return
    session = _session_factory()
    try:
        session.execute(
            update(LlmCallLog)
            .where(LlmCallLog.id == log_id)
            .values(
                response_content=response_content,
                reasoning_content=reasoning_content,
                error=error,
                finish_time=datetime.datetime.now(),
            )
        )
        session.commit()
    except Exception as exc:  # noqa: BLE001
        session.rollback()
        SQLBotLogUtil.warning("llm_call_log finish failed: %s", exc)
    finally:
        session.close()
