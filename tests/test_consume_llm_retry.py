from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.steps.stream import consume_llm, llm_error_is_retryable  # noqa: E402


class _RateLimit(RuntimeError):
    status_code = 429

    def __str__(self) -> str:
        return "RateLimitError 429 TPM limit"


class _BadRequest(RuntimeError):
    status_code = 400

    def __str__(self) -> str:
        return "invalid_request: context length"


def test_llm_error_is_retryable_for_rate_limit_and_timeout() -> None:
    assert llm_error_is_retryable(_RateLimit())
    timeout = TimeoutError("gateway timeout")
    assert llm_error_is_retryable(timeout)
    assert not llm_error_is_retryable(_BadRequest())
    assert not llm_error_is_retryable(ValueError("invalid_request schema"))


def test_consume_llm_retries_rate_limit_then_succeeds(monkeypatch) -> None:
    monkeypatch.setattr("apps.chat.steps.stream.time.sleep", lambda *_a, **_k: None)
    monkeypatch.setattr("apps.chat.steps.stream.settings.LLM_MAX_RETRIES", 2)
    calls = {"n": 0}

    class _Model:
        def invoke(self, _messages: object) -> SimpleNamespace:
            calls["n"] += 1
            if calls["n"] == 1:
                raise _RateLimit()
            return SimpleNamespace(
                content="ok",
                additional_kwargs={},
                usage_metadata={},
                response_metadata={},
            )

    result = consume_llm(_Model(), [])
    assert calls["n"] == 2
    assert result.content == "ok"


def test_consume_llm_does_not_retry_client_errors(monkeypatch) -> None:
    monkeypatch.setattr("apps.chat.steps.stream.time.sleep", lambda *_a, **_k: None)
    calls = {"n": 0}

    class _Model:
        def invoke(self, _messages: object) -> SimpleNamespace:
            calls["n"] += 1
            raise _BadRequest()

    try:
        consume_llm(_Model(), [])
        raise AssertionError("expected client error")
    except _BadRequest:
        pass
    assert calls["n"] == 1
