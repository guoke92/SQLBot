"""Read-only MySQL DSN parsing. No Spring profile / Druid decrypt."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any
from urllib.parse import unquote, urlparse

_DSN_ENV = "WIKI_EXTRACT_DSN"


@dataclass(frozen=True)
class MysqlTarget:
    host: str
    port: int
    user: str
    password: str
    database: str

    def masked(self) -> str:
        return f"mysql://{self.user}@{self.host}:{self.port}/{self.database}"


def parse_dsn(dsn: str, *, database: str = "") -> MysqlTarget:
    text = (dsn or "").strip()
    if not text:
        raise ValueError("empty DSN")
    parsed = urlparse(text)
    if parsed.scheme not in {"mysql", "mysql+pymysql"}:
        raise ValueError(f"unsupported DSN scheme {parsed.scheme!r}; expected mysql://")
    db = database.strip() or (parsed.path or "/").lstrip("/").split("/")[0]
    if not db:
        raise ValueError("DSN is missing a database name")
    return MysqlTarget(
        host=parsed.hostname or "127.0.0.1",
        port=int(parsed.port or 3306),
        user=unquote(parsed.username or ""),
        password=unquote(parsed.password or ""),
        database=db,
    )


def resolve_dsn(*, db_url: str = "", database: str = "") -> MysqlTarget:
    raw = (db_url or "").strip() or os.environ.get(_DSN_ENV, "").strip()
    if not raw:
        raise ValueError(
            f"pass --db-url or set {_DSN_ENV} (mysql://user:pass@host:port/db)"
        )
    return parse_dsn(raw, database=database)


def connect(target: MysqlTarget) -> Any:
    import pymysql
    from pymysql.cursors import DictCursor

    conn = pymysql.connect(
        host=target.host,
        port=target.port,
        user=target.user,
        password=target.password,
        database=target.database,
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=True,
    )
    try:
        with conn.cursor() as cur:
            cur.execute("SET SESSION TRANSACTION READ ONLY")
    except Exception:
        pass
    return conn
