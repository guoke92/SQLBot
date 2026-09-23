"""Tests for independent raw LLM call logging."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

from apps.ai_model.call_log import (
    current_llm_call_refs,
    llm_call_log_scope,
)


def test_llm_call_log_scope_binds_refs() -> None:
    assert current_llm_call_refs() == (None, None)
    with llm_call_log_scope(chat_id=11, chat_record_id=22):
        assert current_llm_call_refs() == (11, 22)
    assert current_llm_call_refs() == (None, None)


def test_begin_llm_call_log_persists_raw_payload() -> None:
    from apps.ai_model import call_log as mod

    captured: dict[str, Any] = {}

    class _FakeSession:
        def add(self, row: Any) -> None:
            captured["row"] = row

        def commit(self) -> None:
            captured["committed"] = True
            captured["row"].id = 99

        def refresh(self, row: Any) -> None:
            return None

        def rollback(self) -> None:
            captured["rolled_back"] = True

        def close(self) -> None:
            captured["closed"] = True

    with (
        llm_call_log_scope(chat_id=7, chat_record_id=8),
        patch.object(mod, "_session_factory", return_value=_FakeSession()),
    ):
        payload = {
            "model": "deepseek-reasoner",
            "reasoning": {"effort": "max", "summary": "auto"},
            "messages": [{"role": "user", "content": "hi"}],
        }
        log_id = mod.begin_llm_call_log(payload)

    assert log_id == 99
    assert captured["committed"] is True
    assert captured["closed"] is True
    row = captured["row"]
    assert row.chat_id == 7
    assert row.chat_record_id == 8
    assert row.request_payload == payload
    assert row.response_content is None


def test_finish_llm_call_log_updates_merged_output() -> None:
    from apps.ai_model import call_log as mod

    executed: dict[str, Any] = {}

    class _FakeSession:
        def execute(self, stmt: Any) -> None:
            executed["stmt"] = stmt

        def commit(self) -> None:
            executed["committed"] = True

        def rollback(self) -> None:
            executed["rolled_back"] = True

        def close(self) -> None:
            executed["closed"] = True

    with patch.object(mod, "_session_factory", return_value=_FakeSession()):
        mod.finish_llm_call_log(
            42,
            response_content="answer",
            reasoning_content="think",
            error=None,
        )

    assert executed["committed"] is True
    assert executed["closed"] is True
    assert executed["stmt"] is not None


def test_finish_llm_call_log_noop_without_id() -> None:
    from apps.ai_model import call_log as mod

    with patch.object(mod, "_session_factory") as factory:
        mod.finish_llm_call_log(None, response_content="x")
    factory.assert_not_called()


def test_begin_llm_call_log_swallows_db_errors() -> None:
    from apps.ai_model import call_log as mod

    class _BoomSession:
        def add(self, row: Any) -> None:
            raise RuntimeError("db down")

        def rollback(self) -> None:
            return None

        def close(self) -> None:
            return None

    with patch.object(mod, "_session_factory", return_value=_BoomSession()):
        assert mod.begin_llm_call_log({"model": "x"}) is None


def test_get_request_payload_begins_log(monkeypatch: Any) -> None:
    from apps.ai_model.openai.llm import BaseChatOpenAI

    calls: list[Any] = []

    def _fake_begin(payload: Any) -> int:
        calls.append(payload)
        return 55

    monkeypatch.setattr(
        "apps.ai_model.openai.llm.begin_llm_call_log", _fake_begin
    )

    llm = BaseChatOpenAI.__new__(BaseChatOpenAI)
    object.__setattr__(llm, "use_responses_api", False)
    object.__setattr__(llm, "max_tokens", None)

    def _super_payload(self: Any, input_: Any, *, stop: Any = None, **kwargs: Any) -> dict:
        return {
            "model": "m",
            "messages": [{"role": "user", "content": "q"}],
            "stream_usage": True,
        }

    monkeypatch.setattr(
        BaseChatOpenAI.__mro__[1],
        "_get_request_payload",
        _super_payload,
        raising=False,
    )
    # Patch via instance unbound call path used inside method
    monkeypatch.setattr(
        "langchain_openai.chat_models.base.ChatOpenAI._get_request_payload",
        lambda self, input_, *, stop=None, **kwargs: {
            "model": "m",
            "messages": [{"role": "user", "content": "q"}],
            "stream_usage": True,
        },
    )

    payload = BaseChatOpenAI._get_request_payload(llm, "q")
    assert calls and calls[0]["model"] == "m"
    assert getattr(llm, "_active_llm_call_log_id") == 55
    assert payload["model"] == "m"
