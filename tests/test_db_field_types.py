"""Database cursor field type classification tests."""

from __future__ import annotations

import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))
os.environ["UPLOAD_DIR"] = "/tmp/sqlbot-test-file"

from common.core.config import settings  # noqa: E402

settings.UPLOAD_DIR = os.environ["UPLOAD_DIR"]

import pymssql  # noqa: E402
import sqlbot_xpack  # noqa: E402, F401

from apps.db.db import _fetch_query_rows, build_fields_info_from_cursor  # noqa: E402


class _Cursor:
    def __init__(self, description: list[tuple[object, ...]]) -> None:
        self.description = description


class _Rows:
    def __init__(self, rows: list[int]) -> None:
        self.rows = rows
        self.fetchmany_sizes: list[int] = []

    def fetchmany(self, size: int) -> list[int]:
        self.fetchmany_sizes.append(size)
        return self.rows[:size]

    def fetchall(self) -> list[int]:
        raise AssertionError("bounded execution must not call fetchall")


def _column(name: str, type_code: object) -> tuple[object, ...]:
    return (name, type_code, None, None, None, None, None)


def test_mysql_sqlalchemy_cursor_uses_mysql_type_codes() -> None:
    cursor = _Cursor(
        [
            _column("CompanyName", 253),
            _column("SignAmt", 246),
            _column("SupplierLevel", 3),
        ]
    )

    assert build_fields_info_from_cursor(cursor, False, "mysql") == [
        {"name": "companyname", "is_numeric": False},
        {"name": "signamt", "is_numeric": True},
        {"name": "supplierlevel", "is_numeric": True},
    ]


def test_mysql_compatible_datasources_share_driver_type_mapping() -> None:
    cursor = _Cursor([_column("Amount", 246)])

    for datasource_type in ("doris", "starrocks", "mariadb"):
        assert build_fields_info_from_cursor(cursor, True, datasource_type) == [
            {"name": "Amount", "is_numeric": True}
        ]


def test_postgresql_compatible_datasources_share_oid_mapping() -> None:
    cursor = _Cursor(
        [
            _column("amount", 1700),
            _column("label", 1043),
        ]
    )

    for datasource_type in ("pg", "postgresql", "redshift", "kingbase", "excel"):
        assert build_fields_info_from_cursor(cursor, True, datasource_type) == [
            {"name": "amount", "is_numeric": True},
            {"name": "label", "is_numeric": False},
        ]


def test_dbapi_type_objects_are_classified_by_their_driver() -> None:
    cursor = _Cursor(
        [
            _column("amount", pymssql.DECIMAL),
            _column("created_at", pymssql.DATETIME),
        ]
    )

    assert build_fields_info_from_cursor(cursor, True, "sqlServer") == [
        {"name": "amount", "is_numeric": True},
        {"name": "created_at", "is_numeric": False},
    ]


def test_bounded_query_fetches_one_sentinel_without_counting_total() -> None:
    source = _Rows(list(range(5000)))

    rows, truncated, limit = _fetch_query_rows(source, 1000)

    assert rows == list(range(1000))
    assert truncated is True
    assert limit == 1000
    assert source.fetchmany_sizes == [1001]
