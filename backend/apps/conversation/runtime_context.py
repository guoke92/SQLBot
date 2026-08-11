"""Rehydratable runtime objects kept outside checkpointed graph state."""

from __future__ import annotations

import threading
from typing import Any

from apps.chat.models.chat_model import ChatQuestion, ChatRecord
from apps.chat.task.llm import LLMService
from apps.conversation.async_util import run_coro_sync
from apps.conversation.models import ConversationRun
from apps.conversation.session import session_scope
from apps.system.crud.user import get_user_info
from apps.system.models.system_model import AssistantModel
from apps.system.schemas.system_schema import AssistantHeader

_lock = threading.RLock()
_contexts: dict[str, dict[str, Any]] = {}


def attach_runtime(run_id: str, **values: Any) -> None:
    with _lock:
        current = _contexts.setdefault(run_id, {})
        current.update(values)


def detach_runtime(run_id: str) -> None:
    with _lock:
        _contexts.pop(run_id, None)


def _hydrate_chat(run: ConversationRun) -> dict[str, Any]:
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
            regenerate_record_id=record.regenerate_record_id,
        )
        service = run_coro_sync(LLMService.create(session, user, question, assistant))
        service.set_record(ChatRecord(**record.model_dump()))
        return {"llm_service": service}


def _hydrate_config(run: ConversationRun) -> dict[str, Any]:
    from apps.config_assistant.nodes import hydrate_config_runtime

    return hydrate_config_runtime(run)


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
    hydrated = (
        _hydrate_config(detached)
        if detached.graph_key == "config"
        else _hydrate_chat(detached)
    )
    attach_runtime(run_id, **hydrated)
    return hydrated


def runtime_value(state: dict[str, Any] | Any, key: str) -> Any:
    run_id = str(state.get("run_id") or "")
    if not run_id:
        raise RuntimeError("Checkpointed conversation state is missing run_id")
    values = runtime_context(run_id)
    if key not in values:
        raise RuntimeError(f"Runtime value {key!r} is unavailable for run {run_id}")
    return values[key]
