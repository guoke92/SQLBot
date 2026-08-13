from __future__ import annotations

import sys
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import Mock

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.models.chat_model import ChatRecord  # noqa: E402
from apps.conversation import runtime_context as runtime_context_module  # noqa: E402
from apps.conversation.models import ConversationRun  # noqa: E402


def _record() -> ChatRecord:
    return ChatRecord(
        id=320,
        chat_id=102,
        question="今年累计签收额",
        datasource=10,
    )


def _run(graph_key: str = "chat") -> ConversationRun:
    return ConversationRun(
        run_id="run-1",
        chat_record_id=320,
        graph_key=graph_key,
        user_id=1,
    )


def test_chat_runtime_rehydrates_access_scope_with_llm_service(monkeypatch) -> None:  # noqa: ANN001
    record = _record()
    user = SimpleNamespace(id=1, language="zh-CN")
    service = SimpleNamespace(ds=SimpleNamespace(id=10), set_record=Mock())
    access_scope = object()
    session = Mock()
    session.get.return_value = record

    @contextmanager
    def fake_session_scope():
        yield session

    monkeypatch.setattr(runtime_context_module, "session_scope", fake_session_scope)
    monkeypatch.setattr(runtime_context_module, "get_user_info", lambda **_kwargs: user)
    monkeypatch.setattr(runtime_context_module, "run_coro_sync", lambda value: value)
    monkeypatch.setattr(
        runtime_context_module.LLMService,
        "create",
        lambda *_args, **_kwargs: service,
    )
    monkeypatch.setattr(
        runtime_context_module,
        "_rehydrate_chat_access_scope",
        lambda _session, _service: access_scope,
    )

    values = runtime_context_module._hydrate_chat(_run())

    assert values == {"llm_service": service, "access_scope": access_scope}
    service.set_record.assert_called_once()


def test_non_nlq_runtime_does_not_resolve_access_scope(monkeypatch) -> None:  # noqa: ANN001
    record = _record()
    user = SimpleNamespace(id=1, language="zh-CN")
    service = SimpleNamespace(ds=SimpleNamespace(id=10), set_record=Mock())
    session = Mock()
    session.get.return_value = record

    @contextmanager
    def fake_session_scope():
        yield session

    monkeypatch.setattr(runtime_context_module, "session_scope", fake_session_scope)
    monkeypatch.setattr(runtime_context_module, "get_user_info", lambda **_kwargs: user)
    monkeypatch.setattr(runtime_context_module, "run_coro_sync", lambda value: value)
    monkeypatch.setattr(
        runtime_context_module.LLMService,
        "create",
        lambda *_args, **_kwargs: service,
    )
    resolver = Mock(return_value=object())
    monkeypatch.setattr(
        runtime_context_module,
        "_rehydrate_chat_access_scope",
        resolver,
    )

    values = runtime_context_module._hydrate_chat(_run("analysis"))

    assert values == {"llm_service": service}
    resolver.assert_not_called()


def test_rehydrated_access_scope_reuses_datasource_validation(monkeypatch) -> None:  # noqa: ANN001
    from apps.chat.steps import datasource as datasource_step
    from apps.datasource import access as datasource_access

    session = Mock()
    service = SimpleNamespace(
        ds=SimpleNamespace(id=10),
        current_user=SimpleNamespace(id=1),
    )
    scope = object()
    validate = Mock()
    resolve = Mock(return_value=scope)
    monkeypatch.setattr(datasource_step, "validate_history_ds", validate)
    monkeypatch.setattr(datasource_access, "resolve_access_scope", resolve)

    result = runtime_context_module._rehydrate_chat_access_scope(session, service)

    assert result is scope
    validate.assert_called_once_with(service, session)
    resolve.assert_called_once_with(
        session,
        current_user=service.current_user,
        ds=service.ds,
    )


def test_rehydrated_access_scope_is_explicitly_none_without_datasource() -> None:
    service: Any = SimpleNamespace(ds=None)

    assert runtime_context_module._rehydrate_chat_access_scope(Mock(), service) is None
