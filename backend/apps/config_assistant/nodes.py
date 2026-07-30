"""Config-assistant scene preparation.

The model/tool loop and terminal lifecycle are shared conversation nodes; this
module only validates the config scene and provides its prompt and tool catalog.
"""

from __future__ import annotations

from typing import Any

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from sqlmodel import Session

from apps.chat.curd.chat import save_question
from apps.chat.models.chat_model import Chat, ChatQuestion, ChatRecord
from apps.config_assistant.prompt import SYSTEM_PROMPT, TOOL_FREE_COMPLETION_MARKER
from apps.config_assistant.tools import build_tools
from apps.conversation.llm import get_chat_model, get_default_chat_config
from apps.conversation.outcome import running_outcome
from apps.conversation.sink import StreamSink
from apps.conversation.state import RunState
from apps.conversation.turn import load_text_history
from common.error import SingleMessageError

_MAX_TOOL_ROUNDS = 8
_HISTORY_TURNS = 8


class ConfigState(RunState, total=False):
    current_user: Any
    record: ChatRecord
    bound_tools: list[Any]
    llm: Any
    tool_rounds: int
    tool_round_limit: int
    tool_steps: list[dict[str, Any]]
    last_tool_failure_signature: str
    consecutive_tool_failures: int
    tool_stop_reason: str
    tool_grounding_retry: bool
    tool_free_completion_marker: str
    final_text: str
    ai_modal_id: int | None
    ai_modal_name: str | None


async def initialize_config_state(
    session: Session,
    *,
    user: Any,
    chat_id: int,
    question: str,
    base_state: dict[str, Any],
) -> ConfigState:
    """Validate and materialize a config turn before submitting its graph."""
    question = question.strip()
    if not question:
        raise SingleMessageError("Question cannot be Empty")

    chat = session.get(Chat, chat_id)
    if chat is None:
        raise SingleMessageError(f"Chat with id {chat_id} not found")
    if chat.create_by != getattr(user, "id", None):
        raise SingleMessageError(f"Chat with id {chat_id} not found")
    user_oid = int(getattr(user, "oid", None) or 1)
    if int(chat.oid or 1) != user_oid:
        raise SingleMessageError(f"Chat with id {chat_id} not found")
    if (chat.chat_type or "chat").strip() != "config":
        raise SingleMessageError(
            f"Chat {chat_id} is chat_type={chat.chat_type!r}, expected config"
        )

    model_config = await get_default_chat_config()
    bound_tools = build_tools(user)
    llm = get_chat_model(model_config)
    history = load_text_history(session, chat_id, limit=_HISTORY_TURNS)
    messages: list[BaseMessage] = [SystemMessage(content=SYSTEM_PROMPT)]
    messages.extend(history)
    messages.append(HumanMessage(content=question))

    chat_question = ChatQuestion(chat_id=chat_id, question=question)
    chat_question.ai_modal_id = model_config.model_id
    chat_question.ai_modal_name = model_config.model_name
    record = save_question(
        session=session,
        current_user=user,
        question=chat_question,
    )
    return {
        **base_state,
        "current_user": user,
        "chat_id": chat_id,
        "question": question,
        "record": record,
        "record_id": record.id,
        "graph_key": "config",
        "mode": "primary",
        "messages": messages,
        "bound_tools": bound_tools,
        "llm": llm,
        "tool_rounds": 0,
        "tool_round_limit": _MAX_TOOL_ROUNDS,
        "tool_steps": [],
        "last_tool_failure_signature": "",
        "consecutive_tool_failures": 0,
        "tool_stop_reason": "",
        "tool_grounding_retry": False,
        "tool_free_completion_marker": TOOL_FREE_COMPLETION_MARKER,
        "final_text": "",
        "ai_modal_id": model_config.model_id,
        "ai_modal_name": model_config.model_name,
        "user_id": getattr(user, "id", None),
        "oid": getattr(user, "oid", None),
        "outcome": running_outcome(),
    }


def prepare_node(state: ConfigState) -> ConfigState:
    """Announce the already initialized turn before entering the shared agent."""
    record_id = state.get("record_id")
    if not record_id or not state.get("messages") or state.get("llm") is None:
        raise RuntimeError("Config turn was not initialized before graph submission")
    StreamSink.from_state(state).event({"type": "id", "id": record_id})
    return state
