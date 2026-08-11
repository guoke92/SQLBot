"""Process-wide PostgreSQL checkpointer used by every conversation graph."""

from __future__ import annotations

import threading
from typing import Any

from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool

from common.core.config import settings

_lock = threading.Lock()
_pool: ConnectionPool[Any] | None = None
_saver: PostgresSaver | None = None


def _conninfo() -> str:
    return str(settings.SQLALCHEMY_DATABASE_URI).replace(
        "postgresql+psycopg://", "postgresql://", 1
    )


def get_checkpointer() -> PostgresSaver:
    global _pool, _saver
    with _lock:
        if _saver is None:
            _pool = ConnectionPool(
                conninfo=_conninfo(),
                min_size=1,
                max_size=max(2, min(int(settings.PG_POOL_SIZE), 10)),
                kwargs={"autocommit": True, "prepare_threshold": 0},
                open=True,
            )
            _saver = PostgresSaver(_pool)
            _saver.setup()
        return _saver


def close_checkpointer() -> None:
    global _pool, _saver
    with _lock:
        pool = _pool
        _pool = None
        _saver = None
    if pool is not None:
        pool.close()
