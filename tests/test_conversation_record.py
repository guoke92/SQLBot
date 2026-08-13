from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, cast

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.conversation.record import persist_snapshot  # noqa: E402


class _Session:
    def __init__(self, *, rowcount: int = 1) -> None:
        self.statements: list[Any] = []
        self.commits = 0
        self.rowcount = rowcount

    def execute(self, statement: Any) -> Any:
        self.statements.append(statement)
        return type("_Result", (), {"rowcount": self.rowcount})()

    def commit(self) -> None:
        self.commits += 1


def test_progressive_snapshot_uses_one_transaction() -> None:
    session = _Session()

    assert persist_snapshot(cast(Any, session), 42, data='{"steps":[]}') is True

    assert len(session.statements) == 1
    assert session.commits == 1


def test_terminal_failure_only_persists_record_at_snapshot_boundary() -> None:
    session = _Session()

    assert persist_snapshot(
        cast(Any, session),
        42,
        data='{"steps":[]}',
        terminal=True,
        error="query failed",
    ) is True

    # Audit spans are closed only by finalize_run / turn terminal boundaries,
    # never by the generic record snapshot primitive.
    assert len(session.statements) == 1
    assert session.commits == 1


def test_late_terminal_writer_is_an_idempotent_noop() -> None:
    session = _Session(rowcount=0)

    assert persist_snapshot(cast(Any, session), 42, terminal=True) is False

    assert len(session.statements) == 1
    assert session.commits == 1


def test_successful_terminal_snapshot_does_not_clear_existing_error() -> None:
    session = _Session()

    assert persist_snapshot(cast(Any, session), 42, terminal=True) is True

    values = {
        getattr(column, "key", str(column))
        for column in session.statements[0]._values
    }
    assert "error" not in values
