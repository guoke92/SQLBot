"""Shared worker-thread DB sessions for conversation graphs.

Graphs must not each re-declare ``scoped_session(sessionmaker(...))``.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy.orm import scoped_session, sessionmaker
from sqlmodel import Session

from common.core.db import engine

# One factory for all conversation graph workers (thread-local via scoped_session).
session_factory = scoped_session(sessionmaker(bind=engine, class_=Session))


@contextmanager
def session_scope() -> Iterator[Session]:
    """Yield a Session bound to the current worker thread; always remove on exit."""
    session = session_factory()
    try:
        yield session
    finally:
        session_factory.remove()
