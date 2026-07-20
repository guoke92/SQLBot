"""Record lifecycle hooks for graph runs (thin, delegates to chat CRUD).

Graphs finish / error-persist only through these helpers — not by re-wrapping
``finish_record`` / ``save_error_message`` in every node.
"""

from __future__ import annotations

from sqlmodel import Session

from apps.chat.curd.chat import finish_record, save_error_message


def finish(session: Session, record_id: int):
    return finish_record(session=session, record_id=record_id)


def save_error(session: Session, record_id: int, message: str):
    return save_error_message(session=session, record_id=record_id, message=message)
