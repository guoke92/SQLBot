"""SQL generation attempt isolation tests."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from langchain_core.messages import AIMessageChunk, SystemMessage

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.models.chat_model import OperationEnum  # noqa: E402
from apps.chat.steps import sql as sql_step  # noqa: E402


class FakeModel:
    def __init__(self) -> None:
        self.calls: list[list[Any]] = []

    def stream(self, messages: list[Any]) -> Any:
        self.calls.append(list(messages))
        yield AIMessageChunk(
            content='{"success":true,"sql":"SELECT 1"}',
            usage_metadata={
                "input_tokens": 10,
                "output_tokens": 5,
                "total_tokens": 15,
            },
        )


def test_generate_sql_keeps_base_messages_immutable_between_attempts(
    monkeypatch: Any,
) -> None:
    model = FakeModel()
    base_messages = [SystemMessage(content="stable schema and rules")]
    record = SimpleNamespace(id=19)
    service = SimpleNamespace(
        sql_message=base_messages,
        protocol=SimpleNamespace(
            build_user_prompt=lambda *_args, **_kwargs: "current question"
        ),
        chat_question=SimpleNamespace(
            ai_modal_id=7,
            ai_modal_name="fake",
        ),
        change_title=False,
        current_logs={},
        record=record,
        llm=model,
    )
    logs: list[dict[str, Any]] = []

    monkeypatch.setattr(
        sql_step,
        "start_log",
        lambda **_kwargs: SimpleNamespace(id=1),
    )
    monkeypatch.setattr(
        sql_step,
        "end_log",
        lambda **kwargs: logs.append(kwargs) or kwargs["log"],
    )
    monkeypatch.setattr(sql_step, "persist_snapshot", lambda **_kwargs: True)

    first = list(sql_step.generate_sql(service, object(), gen_attempts=0))
    second = list(sql_step.generate_sql(service, object(), gen_attempts=1))

    assert first == second
    assert service.sql_message == base_messages
    assert [len(call) for call in model.calls] == [2, 2]
    assert all(call[0] is base_messages[0] for call in model.calls)
    assert all(call[1].content == "current question" for call in model.calls)
    assert len(logs) == 2
    assert service.current_logs[OperationEnum.GENERATE_QUERY].id == 1
