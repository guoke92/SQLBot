"""Chat record helpful / unhelpful feedback persistence contract."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi import HTTPException

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.curd.chat import (  # noqa: E402
    FEEDBACK_COMMENT_MAX_LEN,
    normalize_record_feedback,
    submit_record_feedback,
)


def test_down_requires_non_empty_comment() -> None:
    with pytest.raises(HTTPException) as exc:
        normalize_record_feedback("down", "   ")
    assert exc.value.status_code == 400


def test_down_keeps_trimmed_comment() -> None:
    assert normalize_record_feedback("down", "  SQL 不对  ") == ("down", "SQL 不对")


def test_up_clears_comment() -> None:
    assert normalize_record_feedback("up", "should be dropped") == ("up", None)


def test_clear_vote_clears_comment() -> None:
    assert normalize_record_feedback(None, "old") == (None, None)


def test_invalid_vote_rejected() -> None:
    with pytest.raises(HTTPException) as exc:
        normalize_record_feedback("maybe", "x")
    assert exc.value.status_code == 400


def test_comment_max_length() -> None:
    with pytest.raises(HTTPException) as exc:
        normalize_record_feedback("down", "x" * (FEEDBACK_COMMENT_MAX_LEN + 1))
    assert exc.value.status_code == 400


class _FakeResult:
    def __init__(self, record: object | None) -> None:
        self._record = record

    def scalars(self) -> "_FakeResult":
        return self

    def one_or_none(self) -> object | None:
        return self._record


class _FakeRecord:
    def __init__(self, *, user_id: int) -> None:
        self.id = 11
        self.create_by = user_id
        self.feedback = None
        self.feedback_comment = None
        self.feedback_revision = 0


class _FakeSession:
    def __init__(self, record: object | None) -> None:
        self.record = record
        self.committed = False
        self.added: list[object] = []

    def exec(self, _stmt: object) -> _FakeResult:
        return _FakeResult(self.record)

    def add(self, record: object) -> None:
        self.added.append(record)

    def commit(self) -> None:
        self.committed = True


def test_submit_down_persists_vote_and_comment() -> None:
    record = _FakeRecord(user_id=7)
    session = _FakeSession(record)
    result = submit_record_feedback(
        session,
        chat_record_id=11,
        user_id=7,
        feedback="down",
        comment="  口径错了  ",
    )
    assert result == {"feedback": "down", "comment": "口径错了", "revision": 1}
    assert record.feedback == "down"
    assert record.feedback_comment == "口径错了"
    assert session.committed is True


def test_submit_up_clears_previous_comment() -> None:
    record = _FakeRecord(user_id=7)
    record.feedback = "down"
    record.feedback_comment = "old"
    session = _FakeSession(record)
    result = submit_record_feedback(
        session,
        chat_record_id=11,
        user_id=7,
        feedback="up",
        comment="ignored",
    )
    assert result["feedback"] == "up"
    assert result["comment"] is None
    assert record.feedback_comment is None
