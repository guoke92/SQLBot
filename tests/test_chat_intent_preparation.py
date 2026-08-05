"""Conversation intent preparation regression tests."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import orjson

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.intent_history import latest_reusable_intent_record  # noqa: E402
from apps.chat.models.chat_model import ChatRecord  # noqa: E402


class _ScalarResult:
    def __init__(self, records: list[ChatRecord]):
        self.records = records

    def __iter__(self):
        return iter(self.records)


class _OrmResult:
    """Model SQLAlchemy's Row-vs-scalar distinction used by Session.execute."""

    def __init__(self, records: list[ChatRecord]):
        self.records = records

    def first(self) -> SimpleNamespace:
        # Calling first() directly would reproduce the production regression:
        # a Row-like object does not expose ChatRecord.intent_context.
        return SimpleNamespace(id=self.records[0].id)

    def scalars(self) -> _ScalarResult:
        return _ScalarResult(self.records)


class _Session:
    def __init__(self, records: list[ChatRecord]):
        self.records = records

    def execute(self, _statement: object) -> _OrmResult:
        return _OrmResult(self.records)


def _answer_payload(status: str) -> str:
    return orjson.dumps(
        {
            "steps": [],
            "analysis": "",
            "outcome": {
                "status": status,
                "failures": [],
                "successful_steps": 1 if status in {"success", "degraded"} else 0,
                "total_steps": 1,
            },
        }
    ).decode()


def _intent_context() -> dict:
    requirement = {
        "slot_id": "slot_total",
        "clause": "output",
        "label": "总数",
        "source": "user",
        "evidence_refs": ["question"],
        "field": {"resource": "", "field": "id"},
        "operation": "count",
        "operands": [],
    }
    return {
        "version": 2,
        "status": "ready",
        "contract": {"version": 2, "requirements": [requirement]},
    }


def test_latest_intent_history_query_returns_latest_reusable_orm_scalar() -> None:
    previous = ChatRecord(
        id=289,
        chat_id=88,
        create_by=1,
        finish=True,
        sql="SELECT 1",
        data=_answer_payload("success"),
        intent_context=_intent_context(),
    )
    failed = ChatRecord(
        id=290,
        chat_id=88,
        create_by=1,
        finish=True,
        sql="SELECT broken",
        data=_answer_payload("failed"),
        intent_context=_intent_context(),
    )
    result = latest_reusable_intent_record(
        _Session([failed, previous]),  # type: ignore[arg-type]
        chat_id=88,
        user_id=1,
    )

    assert result is previous
