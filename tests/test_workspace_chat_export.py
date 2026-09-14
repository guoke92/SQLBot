"""Workspace chat/feedback export helpers."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import pytest

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.curd.workspace_export import (  # noqa: E402
    resolve_export_oid,
    serialize_record_for_export,
)


def test_admin_can_export_any_oid() -> None:
    admin = SimpleNamespace(oid=1, isAdmin=True)
    assert resolve_export_oid(admin, 9) == 9
    assert resolve_export_oid(admin, None) == 1


def test_ws_admin_cannot_export_other_oid() -> None:
    user = SimpleNamespace(oid=3, isAdmin=False)
    assert resolve_export_oid(user, None) == 3
    assert resolve_export_oid(user, 3) == 3
    with pytest.raises(PermissionError):
        resolve_export_oid(user, 9)


def test_serialize_record_keeps_feedback_and_optional_sql() -> None:
    record = SimpleNamespace(
        id=692,
        chat_id=274,
        create_by=7,
        create_time=datetime(2026, 9, 11, 15, 24, 37),
        finish_time=None,
        question="查询多租户联系人超过五个的企业信息",
        finish=True,
        error=None,
        feedback="down",
        feedback_comment="test",
        feedback_revision=3,
        sql="SELECT 1",
    )
    with_sql = serialize_record_for_export(record, include_sql=True)
    assert with_sql["feedback"] == "down"
    assert with_sql["feedback_comment"] == "test"
    assert with_sql["sql"] == "SELECT 1"
    without_sql = serialize_record_for_export(record, include_sql=False)
    assert "sql" not in without_sql
