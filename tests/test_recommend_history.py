"""Recommend history sampling and llm_call_log binding."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.ai_model.call_log import current_llm_call_refs  # noqa: E402
from apps.chat.curd.chat import (  # noqa: E402
    _append_unique_questions,
    get_old_questions,
)


def test_append_unique_questions_dedupes_and_excludes() -> None:
    out: list[str] = []
    seen: set[str] = set()
    done = _append_unique_questions(
        [
            "  导出A  ",
            "导出A",
            "/regenerate",
            "",
            "导出B",
            "导出A",
            "导出C",
        ],
        out=out,
        seen=seen,
        exclude="导出B",
        limit=2,
    )
    assert done is True
    assert out == ["导出A", "导出C"]


def test_get_old_questions_prefers_chat_then_fills_datasource() -> None:
    session = MagicMock()

    def _rows(questions: list[str]):
        result = MagicMock()
        result.all.return_value = [(q,) for q in questions]
        return result

    # First execute = current chat; second = datasource fill.
    session.execute.side_effect = [
        _rows(["导出A", "导出A", "当前问题", "导出B"]),
        _rows(["导出B", "导出C", "导出A", "导出D"]),
    ]

    questions = get_old_questions(
        session,
        datasource=15,
        chat_id=330,
        exclude_question="当前问题",
        limit=3,
    )
    assert questions == ["导出A", "导出B", "导出C"]
    assert session.execute.call_count == 2


def test_get_old_questions_skips_datasource_when_chat_fills_limit() -> None:
    session = MagicMock()
    result = MagicMock()
    result.all.return_value = [("q1",), ("q2",), ("q3",)]
    session.execute.return_value = result

    questions = get_old_questions(
        session, datasource=15, chat_id=1, exclude_question=None, limit=2
    )
    assert questions == ["q1", "q2"]
    assert session.execute.call_count == 1


def test_recommend_binds_llm_call_log_scope(monkeypatch) -> None:
    from apps.chat.steps import recommend as mod

    bound: list[tuple[int | None, int | None]] = []

    def _fake_process_stream(*_a, **_k):
        bound.append(current_llm_call_refs())
        return iter([])

    class _Span:
        def __enter__(self):
            bound.append(current_llm_call_refs())
            return self

        def __exit__(self, *args):
            return False

        def set_model_context(self, *_a, **_k):
            return None

        def set_usage(self, *_a, **_k):
            return None

        def set_summary(self, *_a, **_k):
            return None

        def __setitem__(self, key, value):
            return None

    monkeypatch.setattr(mod, "process_stream", _fake_process_stream)
    monkeypatch.setattr(mod, "log_span", lambda **_k: _Span())
    monkeypatch.setattr(mod, "get_old_questions", lambda *_a, **_k: [])
    monkeypatch.setattr(
        mod,
        "save_recommend_question_answer",
        lambda **_k: SimpleNamespace(id=808, recommended_question="[]"),
    )

    llm_service = SimpleNamespace(
        articles_number=4,
        record=SimpleNamespace(
            id=808,
            chat_id=330,
            datasource=15,
            question="当前问题",
            active_run_id=None,
        ),
        chat_question=SimpleNamespace(
            ai_modal_id=1,
            ai_modal_name="m",
            db_schema="",
            guess_sys_question=lambda _n: "sys",
            guess_user_question=lambda _old: "user",
        ),
        llm=SimpleNamespace(stream=lambda _messages: iter([])),
    )

    list(mod.generate_recommend_questions(llm_service, MagicMock()))
    assert bound
    assert all(item == (330, 808) for item in bound)
    assert current_llm_call_refs() == (None, None)
