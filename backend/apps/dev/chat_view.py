"""Admin chat hydrate: same shape as production get_chat_with_records, no caller owner check."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from fastapi import HTTPException
from sqlmodel import Session

from apps.chat.curd.chat import get_chat_with_records
from apps.chat.models.chat_model import Chat


def get_chat_for_admin(
    session: Session,
    chat_id: int,
    *,
    trans: Any = None,
    with_data: bool = False,
) -> Any:
    chat = session.get(Chat, chat_id)
    if chat is None or chat.create_by is None:
        raise HTTPException(status_code=404, detail=f"Chat with id {chat_id} not found")
    owner = SimpleNamespace(id=int(chat.create_by))
    try:
        return get_chat_with_records(
            session=session,
            chart_id=chat_id,
            current_user=owner,  # type: ignore[arg-type]
            current_assistant=None,
            with_data=with_data,
            trans=trans,
        )
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
