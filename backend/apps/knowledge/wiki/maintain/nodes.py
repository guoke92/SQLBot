"""Wiki maintenance graph: propose, accept, then materialize a draft."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.types import interrupt
from sqlmodel import Session

from apps.chat.curd.chat import save_question
from apps.chat.models.chat_model import Chat, ChatQuestion, ChatRecord
from apps.chat.semantic_planning import ClarificationCard
from apps.conversation.graph_hooks import register_hydrate
from apps.conversation.llm import (
    get_chat_model,
    get_default_chat_config,
    resolve_chat_llm_config,
)
from apps.conversation.messages import deserialize_messages, serialize_messages
from apps.conversation.models import ConversationRun
from apps.conversation.outcome import running_outcome
from apps.conversation.run_service import create_interrupt, create_run
from apps.conversation.runtime_context import attach_runtime, runtime_value
from apps.conversation.session import session_scope
from apps.conversation.sink import StreamSink
from apps.conversation.state import RunState
from apps.conversation.turn import load_text_history
from apps.knowledge.wiki.maintain.prompt import (
    TOOL_FREE_COMPLETION_MARKER,
    render_system,
)
from apps.knowledge.wiki.maintain.tools import build_tools
from apps.knowledge.wiki.writer import apply_proposed, proposed_patches, reject_proposed
from common.error import SingleMessageError

_MAX_TOOL_ROUNDS = 8
_HISTORY_TURNS = 8


class WikiMaintainState(RunState, total=False):
    tool_rounds: int
    tool_round_limit: int
    tool_steps: list[dict[str, Any]]
    last_tool_failure_signature: str
    consecutive_tool_failures: int
    tool_stop_reason: str
    tool_grounding_retry: bool
    tool_free_completion_marker: str
    final_text: str
    accept_decision: str
    ai_modal_id: int | None
    ai_modal_name: str | None


def wiki_focus(chat: Chat) -> dict[str, Any]:
    raw = chat.agent_transcript if isinstance(chat.agent_transcript, dict) else {}
    focus = raw.get("wiki") if isinstance(raw.get("wiki"), dict) else {}
    return {
        "corpus_key": str(focus.get("corpus_key") or ""),
        "belong": str(focus.get("belong") or ""),
        "page_key": str(focus.get("page_key") or ""),
        "source_id": focus.get("source_id"),
        "origin": str(focus.get("origin") or "maintain"),
        "source_ref": str(focus.get("source_ref") or ""),
    }


async def initialize_wiki_state(
    session: Session,
    *,
    user: Any,
    chat_id: int,
    question: str,
    base_state: dict[str, Any],
    reasoning_effort: str | None = None,
) -> WikiMaintainState:
    question = question.strip()
    if not question:
        raise SingleMessageError("Question cannot be Empty")
    chat = session.get(Chat, chat_id)
    if chat is None or chat.create_by != getattr(user, "id", None):
        raise SingleMessageError(f"Chat with id {chat_id} not found")
    if int(chat.oid or 1) != int(getattr(user, "oid", None) or 1):
        raise SingleMessageError(f"Chat with id {chat_id} not found")
    if (chat.chat_type or "chat").strip() != "wiki":
        raise SingleMessageError(f"Chat {chat_id} is not a wiki maintenance chat")
    focus = wiki_focus(chat)
    if not focus["corpus_key"]:
        raise SingleMessageError("Wiki chat is missing a corpus")

    model_config = await resolve_chat_llm_config(session, user, None, reasoning_effort)
    history = load_text_history(session, chat_id, limit=_HISTORY_TURNS)
    messages: list[BaseMessage] = [SystemMessage(content=render_system(focus))]
    messages.extend(history)
    messages.append(HumanMessage(content=question))
    chat_question = ChatQuestion(chat_id=chat_id, question=question)
    chat_question.ai_modal_id = model_config.model_id
    chat_question.ai_modal_name = model_config.model_name
    record = save_question(
        session=session, current_user=user, question=chat_question, commit=False
    )
    run = create_run(
        session,
        record=record,
        graph_key="wiki_maintain",
        user_id=int(user.id),
        oid=int(getattr(user, "oid", None) or 1),
        reasoning_effort=reasoning_effort,
    )
    attach_runtime(
        run.run_id,
        current_user=user,
        bound_tools=build_tools(user),
        llm=get_chat_model(model_config),
    )
    return {
        **base_state,
        "run_id": run.run_id,
        "chat_id": chat_id,
        "question": question,
        "record_id": record.id,
        "graph_key": "wiki_maintain",
        "mode": "primary",
        "messages": serialize_messages(messages),
        "tool_rounds": 0,
        "tool_round_limit": _MAX_TOOL_ROUNDS,
        "tool_steps": [],
        "last_tool_failure_signature": "",
        "consecutive_tool_failures": 0,
        "tool_stop_reason": "",
        "tool_grounding_retry": False,
        "tool_free_completion_marker": TOOL_FREE_COMPLETION_MARKER,
        "final_text": "",
        "accept_decision": "",
        "ai_modal_id": model_config.model_id,
        "ai_modal_name": model_config.model_name,
        "user_id": getattr(user, "id", None),
        "oid": getattr(user, "oid", None),
        "outcome": running_outcome(),
    }


def prepare_node(state: WikiMaintainState) -> WikiMaintainState:
    record_id = state.get("record_id")
    if not record_id or not state.get("messages"):
        raise RuntimeError("Wiki turn was not initialized before graph submission")
    runtime_value(state, "llm")
    StreamSink.from_state(state).event({"type": "id", "id": record_id})
    return state


def await_accept_node(state: Mapping[str, Any]) -> dict[str, Any]:
    """Pause until the user accepts or rejects the proposals. The model cannot skip this."""
    run_id = str(state.get("run_id") or "")
    with session_scope() as session:
        pending = proposed_patches(session, run_id)
        summary = (
            "、".join(f"{item.op} {item.claim_path}" for item in pending[:6])
            or "没有待确认的补丁"
        )
        card = ClarificationCard.model_validate(
            {
                "questions": [
                    {
                        "question_id": "wiki_patch_accept",
                        "question": "是否把这些补丁写入 Wiki 草稿？",
                        "why": summary,
                        "options": [
                            {
                                "option_id": "accept",
                                "label": "接受",
                                "meaning": "接受补丁",
                                "field": "accept",
                            },
                            {
                                "option_id": "reject",
                                "label": "拒绝",
                                "meaning": "拒绝补丁",
                                "field": "reject",
                            },
                        ],
                    }
                ]
            }
        ).model_dump(mode="json")
        stored = create_interrupt(session, run_id=run_id, payload=card)
    public = {
        "interrupt_id": stored.interrupt_id,
        "version": stored.version,
        **card,
    }
    sink = StreamSink.from_state(state)
    if stored.status == "open":
        sink.awaiting_input(public)
    answers = interrupt(public)
    decision, reason = _decision(answers)
    if decision == "accept":
        return {**state, "accept_decision": "accept"}
    messages = deserialize_messages(list(state.get("messages") or []))
    messages.append(
        HumanMessage(
            content=f"用户拒绝了这批补丁。理由：{reason}。请修改提案，或说明为什么不能改。"
        )
    )
    with session_scope() as session:
        reject_proposed(session, run_id=run_id)
        session.commit()
    return {
        **state,
        "messages": serialize_messages(messages),
        "accept_decision": "rejected",
        "tool_stop_reason": "",
    }


def apply_patches_node(state: Mapping[str, Any]) -> dict[str, Any]:
    run_id = str(state.get("run_id") or "")
    actor = str(state.get("user_id") or "")
    try:
        with session_scope() as session:
            applied = apply_proposed(session, run_id=run_id, actor=actor)
            corpus_ids = {
                int(item.corpus_id) for item in applied if item.status == "applied"
            }
            session.commit()
        for corpus_id in corpus_ids:
            from apps.knowledge.wiki.embeddings_sync import schedule_embed_sync

            schedule_embed_sync(corpus_id)
    except Exception as exc:
        return {**state, "error": str(exc), "accept_decision": "failed"}
    return {
        **state,
        "accept_decision": "applied",
        "tool_stop_reason": "the user accepted the wiki patches and they were written into the draft",
    }


def route_after_wiki_agent(
    state: Mapping[str, Any],
) -> Literal["agent", "execute_tools", "await_accept", "finish", "fail"]:
    if state.get("error"):
        return "fail"
    if state.get("tool_grounding_retry"):
        return "agent"
    from langchain_core.messages import AIMessage

    messages = deserialize_messages(list(state.get("messages") or []))
    if messages:
        last = messages[-1]
        if isinstance(last, AIMessage) and getattr(last, "tool_calls", None):
            return "execute_tools"
    run_id = str(state.get("run_id") or "")
    with session_scope() as session:
        if proposed_patches(session, run_id):
            return "await_accept"
    return "finish"


def route_after_apply(state: Mapping[str, Any]) -> Literal["agent", "fail"]:
    return "fail" if state.get("error") else "agent"


def route_after_accept(state: Mapping[str, Any]) -> Literal["apply", "agent", "fail"]:
    if state.get("error"):
        return "fail"
    if state.get("accept_decision") == "accept":
        return "apply"
    return "agent"


def hydrate_wiki_runtime(run: ConversationRun) -> dict[str, Any]:
    from apps.conversation.async_util import run_coro_sync
    from apps.system.crud.user import get_user_info

    with session_scope() as session:
        user = run_coro_sync(get_user_info(session=session, user_id=run.user_id))
        if user is None:
            raise LookupError(f"User {run.user_id} not found")
        model_config = run_coro_sync(get_default_chat_config())
        snap = run.route_snapshot if isinstance(run.route_snapshot, dict) else {}
        effort = snap.get("reasoning_effort")
        if effort is not None:
            from apps.ai_model.model_factory import with_reasoning_effort

            model_config = with_reasoning_effort(model_config, effort)
        return {
            "current_user": user,
            "bound_tools": build_tools(user),
            "llm": get_chat_model(model_config),
        }


def recover_wiki_state(run: ConversationRun) -> WikiMaintainState:
    runtime = hydrate_wiki_runtime(run)
    with session_scope() as session:
        record = session.get(ChatRecord, run.chat_record_id)
        chat = session.get(Chat, int(record.chat_id)) if record is not None else None
        if record is None or chat is None:
            raise LookupError(f"Chat record {run.chat_record_id} not found")
        history = load_text_history(session, int(record.chat_id), limit=_HISTORY_TURNS)
        focus = wiki_focus(chat)
    messages: list[BaseMessage] = [SystemMessage(content=render_system(focus))]
    messages.extend(history)
    messages.append(HumanMessage(content=record.question or ""))
    attach_runtime(run.run_id, **runtime)
    return {
        "run_id": run.run_id,
        "chat_id": int(record.chat_id),
        "question": record.question or "",
        "record_id": run.chat_record_id,
        "graph_key": "wiki_maintain",
        "sink": "sse",
        "mode": "primary",
        "messages": serialize_messages(messages),
        "tool_rounds": 0,
        "tool_round_limit": _MAX_TOOL_ROUNDS,
        "tool_steps": [],
        "tool_free_completion_marker": TOOL_FREE_COMPLETION_MARKER,
        "final_text": "",
        "accept_decision": "",
        "user_id": run.user_id,
        "oid": run.oid,
        "outcome": running_outcome(),
    }


def _hydrate_hook(run: ConversationRun, _service: Any = None) -> dict[str, Any]:
    return hydrate_wiki_runtime(run)


def _decision(answers: Any) -> tuple[str, str]:
    reason = "用户拒绝了这批补丁"
    if not isinstance(answers, list):
        return "reject", reason
    for item in answers:
        if not isinstance(item, dict):
            continue
        if str(item.get("option_id") or "") == "accept":
            return "accept", ""
        text = str(item.get("text") or "").strip()
        if text:
            reason = text
    return "reject", reason


register_hydrate("wiki_maintain", _hydrate_hook)
