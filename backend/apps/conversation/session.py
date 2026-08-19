"""Shared worker-thread DB sessions for conversation graphs.

Graphs must not each re-declare ``scoped_session(sessionmaker(...))``.
Audit writes use a separate short-lived Session so committing ``chat_log``
cannot expire or close the worker session.
"""

from __future__ import annotations

import threading
from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy.orm import scoped_session, sessionmaker
from sqlmodel import Session

from common.core.db import engine

# One factory for all conversation graph workers (thread-local via scoped_session).
session_factory = scoped_session(sessionmaker(bind=engine, class_=Session))
_audit_factory = sessionmaker(bind=engine, class_=Session)
_scope_state = threading.local()


@contextmanager
def session_scope() -> Iterator[Session]:
    """Yield the worker Session for this thread.

    Nested scopes reuse the same Session. Only the outermost exit removes it.
    """
    depth = getattr(_scope_state, "depth", 0)
    session = session_factory()
    _scope_state.depth = depth + 1
    try:
        yield session
    finally:
        _scope_state.depth = depth
        if depth == 0:
            session_factory.remove()


@contextmanager
def audit_session() -> Iterator[Session]:
    """Short-lived Session for ChatLog writes, independent of the worker scope."""
    session = _audit_factory()
    try:
        yield session
    finally:
        session.close()
