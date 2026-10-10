"""Rehydratable runtime objects kept outside checkpointed graph state."""

from __future__ import annotations

import threading
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any

from apps.chat.models.chat_model import ChatQuestion, ChatRecord
from apps.chat.task.llm import LLMService
from apps.conversation.async_util import run_coro_sync
from apps.conversation.graph_hooks import try_hydrate
from apps.conversation.models import ConversationRun
from apps.conversation.session import session_scope
from apps.system.crud.user import get_user_info
from apps.system.models.system_model import AssistantModel
from apps.system.schemas.system_schema import AssistantHeader

_lock = threading.RLock()
_contexts: dict[str, dict[str, Any]] = {}
_worker_run_id: ContextVar[str | None] = ContextVar(
    "conversation_worker_run_id", default=None
)
_worker_token: ContextVar[str | None] = ContextVar(
    "conversation_worker_token", default=None
)
_current_tool_call_id: ContextVar[str | None] = ContextVar(
    "conversation_tool_call_id", default=None
)


@contextmanager
def worker_scope(
    run_id: str,
    token: str,
    *,
    chat_id: int | None = None,
    chat_record_id: int | None = None,
) -> Iterator[None]:
    """Bind one claimed worker to this execution context.

    The token is intentionally context-local rather than stored in the shared
    runtime cache. A recovered worker may replace the database owner while an
    old thread is still unwinding; context-local fencing prevents that stale
    thread from borrowing the new owner's token.
    """
    from apps.ai_model.call_log import llm_call_log_scope

    run_handle = _worker_run_id.set(run_id)
    token_handle = _worker_token.set(token)
    try:
        with llm_call_log_scope(chat_id=chat_id, chat_record_id=chat_record_id):
            yield
    finally:
        _worker_token.reset(token_handle)
        _worker_run_id.reset(run_handle)


def current_worker_identity() -> tuple[str | None, str | None]:
    return _worker_run_id.get(), _worker_token.get()


def current_tool_call_id() -> str | None:
    return _current_tool_call_id.get()


@contextmanager
def tool_call_scope(call_id: str) -> Iterator[None]:
    handle = _current_tool_call_id.set(call_id)
    try:
        yield
    finally:
        _current_tool_call_id.reset(handle)


def attach_runtime(run_id: str, **values: Any) -> None:
    with _lock:
        current = _contexts.setdefault(run_id, {})
        current.update(values)


def peek_runtime(run_id: str) -> dict[str, Any] | None:
    """Return the in-memory runtime bag without hydrating from the database."""
    with _lock:
        cached = _contexts.get(run_id)
        return dict(cached) if cached is not None else None


def detach_runtime(run_id: str) -> None:
    with _lock:
        _contexts.pop(run_id, None)


def _rebuild_llm_service(run: ConversationRun) -> dict[str, Any]:
    """Host-owned resume of LLMService. Product extras come from graph hydrate hooks."""
    with session_scope() as session:
        record = session.get(ChatRecord, run.chat_record_id)
        if record is None:
            raise LookupError(f"Chat record {run.chat_record_id} not found")
        user = run_coro_sync(get_user_info(session=session, user_id=run.user_id))
        if user is None:
            raise LookupError(f"User {run.user_id} not found")
        assistant = None
        if run.assistant_id is not None:
            model = session.get(AssistantModel, run.assistant_id)
            if model is None:
                raise LookupError(f"Assistant {run.assistant_id} not found")
            assistant = AssistantHeader.model_validate(model.model_dump())
        question = ChatQuestion(
            chat_id=record.chat_id,
            question=record.question or "",
        )
        snap = run.route_snapshot if isinstance(run.route_snapshot, dict) else {}
        reasoning_effort = snap.get("reasoning_effort")
        service = run_coro_sync(
            LLMService.create(
                session,
                user,
                question,
                assistant,
                reasoning_effort=reasoning_effort,
            )
        )
        service.set_record(ChatRecord(**record.model_dump()))
        return {"llm_service": service}


def _hydrate_run(run: ConversationRun) -> dict[str, Any]:
    """Rebuild runtime via graph-key hooks. Host never imports product tools."""
    if run.graph_key in {"config", "wiki_maintain"}:
        extras = try_hydrate(run.graph_key, run, None)
        if not extras:
            raise RuntimeError("config hydrate hook is not registered")
        return extras
    values = _rebuild_llm_service(run)
    extras = try_hydrate(run.graph_key, run, values["llm_service"])
    if extras:
        values.update(extras)
    return values


def runtime_context(run_id: str) -> dict[str, Any]:
    with _lock:
        cached = _contexts.get(run_id)
        if cached is not None:
            return cached
    with session_scope() as session:
        run = session.get(ConversationRun, run_id)
        if run is None:
            raise LookupError(f"Conversation run {run_id} not found")
        detached = ConversationRun(**run.model_dump())
    hydrated = _hydrate_run(detached)
    attach_runtime(run_id, **hydrated)
    from apps.conversation.lifecycle_log import log_lifecycle

    log_lifecycle(
        "runtime_rehydrated",
        run_id=detached.run_id,
        record_id=detached.chat_record_id,
        graph_key=detached.graph_key,
        status=detached.status,
        count=len(hydrated),
    )
    return hydrated


def runtime_value(state: dict[str, Any] | Any, key: str) -> Any:
    run_id = str(state.get("run_id") or "")
    if not run_id:
        raise RuntimeError("Checkpointed conversation state is missing run_id")
    values = runtime_context(run_id)
    if key not in values:
        raise RuntimeError(f"Runtime value {key!r} is unavailable for run {run_id}")
    return values[key]
