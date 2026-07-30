from __future__ import annotations

import sys
from pathlib import Path
from types import ModuleType
from types import SimpleNamespace
from typing import Any

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.protocol.sql.cost_validate import explain_cost_too_high  # noqa: E402


class _RejectingSession:
    def __enter__(self) -> _RejectingSession:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def execute(self, _statement: object) -> Any:
        raise RuntimeError("selected column must appear in GROUP BY")


def test_regular_explain_failure_rejects_statement(monkeypatch: Any) -> None:
    db_module = ModuleType("apps.db.db")
    db_module.get_session = lambda _ds: _RejectingSession()  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "apps.db.db", db_module)

    message = explain_cost_too_high(
        SimpleNamespace(type="starrocks"),
        "SELECT company_name, SUM(amount) FROM finance",
    )

    assert message is not None
    assert "SQL EXPLAIN validation failed" in message
    assert "GROUP BY" in message


def test_unsupported_protocol_skips_explain() -> None:
    assert (
        explain_cost_too_high(
            SimpleNamespace(type="api"),
            "SELECT 1",
        )
        is None
    )
