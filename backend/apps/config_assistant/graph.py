"""Config-assistant LangGraph — tool-calling primary scenario.

Control flow::

    prepare → agent ⇄ run_tools → finish
                     ↘ (error) → fail

SSE types (single contract, no dual map)::

    id / tool-call / tool-result / message / finish / error

Process truth source is ChatLog (TOOL_CALL / CONFIG_AGENT), same channel as
NLQ ExecutionDetails. Final assistant answer is plain text on sql_answer only.

Invoked only via ``submit_graph("config", state)``.
"""

from __future__ import annotations

import traceback
from typing import Any, Dict, List, Literal, Sequence

import orjson
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode
from sqlalchemy import and_, select

from apps.chat.curd.chat import end_log, save_question, save_sql_answer, start_log
from apps.chat.models.chat_model import Chat, ChatQuestion, ChatRecord, OperationEnum
from apps.config_assistant.prompt import SYSTEM_PROMPT
from apps.config_assistant.tools import build_tools
from apps.conversation.async_util import run_coro_sync
from apps.conversation.llm import get_chat_model, get_default_chat_config
from apps.conversation.record import finish as record_finish
from apps.conversation.record import save_error as record_save_error
from apps.conversation.registry import register_graph
from apps.conversation.session import session_scope
from apps.conversation.sink import StreamSink
from apps.conversation.state import RunState
from common.error import SingleMessageError
from common.utils.utils import SQLBotLogUtil


# Soft upper bound on agent↔tool rounds per user turn.
_MAX_TOOL_ROUNDS = 8
# How many prior finished Q/A pairs to hydrate into the agent context.
_HISTORY_TURNS = 8
# Cap each tool result body stored on ChatLog / returned in audits.
_TOOL_RESULT_LOG_LIMIT = 4000


class ConfigState(RunState, total=False):
    """Primary config-assistant run state.

    Bound tools live under ``bound_tools`` — never ``tools`` — so the LangGraph
    node id ``run_tools`` (and any future ``tools`` rename) cannot collide with a
    state channel (LangGraph forbids node names that match channel keys).
    """

    current_user: Any
    question: str
    record: ChatRecord
    messages: List[BaseMessage]
    bound_tools: List[Any]
    llm: Any
    tool_rounds: int
    error: str
    final_text: str
    ai_modal_id: int | None
    ai_modal_name: str | None


def _error_message(exc: BaseException) -> str:
    if isinstance(exc, SingleMessageError):
        return str(exc)
    return orjson.dumps(
        {"message": str(exc), "traceback": traceback.format_exc(limit=1)}
    ).decode()


def _tool_calls_payload(message: AIMessage) -> List[Dict[str, Any]]:
    calls: List[Dict[str, Any]] = []
    for tc in getattr(message, "tool_calls", None) or []:
        if isinstance(tc, dict):
            calls.append(
                {
                    "id": tc.get("id"),
                    "name": tc.get("name"),
                    "args": tc.get("args") or {},
                }
            )
        else:
            calls.append(
                {
                    "id": getattr(tc, "id", None),
                    "name": getattr(tc, "name", None),
                    "args": getattr(tc, "args", {}) or {},
                }
            )
    return calls


def _assistant_text_for_history(sql_answer: str | None) -> str:
    """Prefer plain assistant prose when older rows still have a tool-trace prefix."""
    raw = (sql_answer or "").strip()
    if not raw:
        return ""
    if "**tool-call**" not in raw and "**tool-result" not in raw:
        return raw
    parts = [p.strip() for p in raw.split("\n\n") if p.strip()]
    for p in reversed(parts):
        if not p.startswith("**tool-"):
            return p
    return raw


def _load_history_messages(session: Any, chat_id: int, limit: int = _HISTORY_TURNS) -> List[BaseMessage]:
    """Hydrate prior finished config turns as Human/AI pairs (no analysis/predict)."""
    stmt = (
        select(ChatRecord)
        .where(
            and_(
                ChatRecord.chat_id == chat_id,
                ChatRecord.analysis_record_id.is_(None),
                ChatRecord.predict_record_id.is_(None),
                ChatRecord.finish.is_(True),
            )
        )
        .order_by(ChatRecord.create_time.desc())
        .limit(limit)
    )
    rows = list(session.execute(stmt).scalars().all())
    rows.reverse()
    out: List[BaseMessage] = []
    for r in rows:
        if r.first_chat:
            continue
        q = (r.question or "").strip()
        a = _assistant_text_for_history(r.sql_answer)
        if not q and not a:
            continue
        if q:
            out.append(HumanMessage(content=q))
        if a:
            out.append(AIMessage(content=a))
    return out


def _truncate(text: str, limit: int = _TOOL_RESULT_LOG_LIMIT) -> str:
    if text is None:
        return ""
    if len(text) <= limit:
        return text
    return text[:limit] + "…(truncated)"


def _usage_from_response(response: Any) -> dict[str, Any]:
    """Normalize token usage from an AIMessage (invoke-path)."""
    usage = getattr(response, "usage_metadata", None) or {}
    if isinstance(usage, dict) and usage:
        return {
            "input_tokens": usage.get("input_tokens"),
            "output_tokens": usage.get("output_tokens"),
            "total_tokens": usage.get("total_tokens"),
        }
    meta = getattr(response, "response_metadata", None) or {}
    if isinstance(meta, dict):
        token_usage = meta.get("token_usage") or meta.get("usage") or {}
        if isinstance(token_usage, dict) and token_usage:
            total = (
                token_usage.get("total_tokens")
                or token_usage.get("total_token_count")
            )
            return {
                "input_tokens": token_usage.get("prompt_tokens")
                or token_usage.get("input_tokens"),
                "output_tokens": token_usage.get("completion_tokens")
                or token_usage.get("output_tokens"),
                "total_tokens": total,
            }
    return {}


def _tool_args_by_call_id(ai_message: AIMessage | None) -> dict[str, dict[str, Any]]:
    """Map tool_call_id → {name, args} from the preceding AIMessage."""
    out: dict[str, dict[str, Any]] = {}
    if ai_message is None:
        return out
    for tc in getattr(ai_message, "tool_calls", None) or []:
        if isinstance(tc, dict):
            call_id = tc.get("id")
            if call_id:
                out[str(call_id)] = {
                    "name": tc.get("name"),
                    "args": tc.get("args") or {},
                }
        else:
            call_id = getattr(tc, "id", None)
            if call_id:
                out[str(call_id)] = {
                    "name": getattr(tc, "name", None),
                    "args": getattr(tc, "args", {}) or {},
                }
    return out


def _find_last_ai_with_tools(messages: Sequence[BaseMessage]) -> AIMessage | None:
    for m in reversed(list(messages)):
        if isinstance(m, AIMessage) and getattr(m, "tool_calls", None):
            return m
    return None


def prepare_node(state: ConfigState) -> ConfigState:
    """Persist the question record, build tools + LLM, seed messages (+history)."""
    user = state["current_user"]
    chat_id = state["chat_id"]
    question = state.get("question") or ""
    if not str(question).strip():
        raise SingleMessageError("Question cannot be Empty")

    config = run_coro_sync(get_default_chat_config())

    with session_scope() as session:
        chat = session.get(Chat, chat_id)
        if not chat:
            raise SingleMessageError(f"Chat with id {chat_id} not found")
        if (chat.chat_type or "chat") != "config":
            raise SingleMessageError(
                f"Chat {chat_id} is chat_type={chat.chat_type!r}, expected config"
            )
        history = _load_history_messages(session, chat_id)
        cq = ChatQuestion(chat_id=chat_id, question=question)
        cq.ai_modal_id = config.model_id
        cq.ai_modal_name = config.model_name
        record = save_question(session=session, current_user=user, question=cq)

    llm = get_chat_model(config)
    bound_tools = build_tools(user)
    messages: List[BaseMessage] = [SystemMessage(content=SYSTEM_PROMPT)]
    messages.extend(history)
    messages.append(HumanMessage(content=question))

    sink = StreamSink.from_state(state)
    sink.event({"type": "id", "id": record.id})

    return {
        **state,
        "record": record,
        "record_id": record.id,
        "graph_key": "config",
        "mode": "primary",
        "messages": messages,
        "bound_tools": bound_tools,
        "llm": llm,
        "tool_rounds": 0,
        "final_text": "",
        "ai_modal_id": config.model_id,
        "ai_modal_name": config.model_name,
        "user_id": getattr(user, "id", None),
        "oid": getattr(user, "oid", None),
    }


def agent_node(state: ConfigState) -> ConfigState:
    """One LLM turn with tools bound; stream tool-call / message events.

    Each round writes one CONFIG_AGENT ChatLog for ExecutionDetails (and tokens).
    """
    sink = StreamSink.from_state(state)
    bound_tools = state.get("bound_tools") or []
    llm = state["llm"]
    messages = list(state.get("messages") or [])
    rounds = int(state.get("tool_rounds") or 0)
    record_id = state.get("record_id")
    ai_modal_id = state.get("ai_modal_id")
    ai_modal_name = state.get("ai_modal_name")

    log = None
    if record_id:
        with session_scope() as session:
            log = start_log(
                session=session,
                ai_modal_id=ai_modal_id,
                ai_modal_name=ai_modal_name,
                operate=OperationEnum.CONFIG_AGENT,
                record_id=record_id,
                full_message={"kind": "agent", "round": rounds + 1},
                local_operation=False,
            )

    try:
        bound = llm.bind_tools(bound_tools) if bound_tools else llm
        response: AIMessage = bound.invoke(messages)
    except Exception as e:
        SQLBotLogUtil.error(f"config agent invoke failed: {e}")
        error_msg = _error_message(e)
        if log is not None and record_id:
            with session_scope() as session:
                end_log(
                    session=session,
                    log=log,
                    full_message={
                        "kind": "agent",
                        "round": rounds + 1,
                        "error": error_msg,
                        "ok": False,
                    },
                )
                record_save_error(session, record_id, error_msg)
        elif record_id:
            with session_scope() as session:
                record_save_error(session, record_id, error_msg)
        return {**state, "error": error_msg}

    messages.append(response)
    tool_calls = _tool_calls_payload(response)
    text = response.content if isinstance(response.content, str) else str(response.content or "")
    usage = _usage_from_response(response)

    if log is not None:
        preview = text if len(text) <= 500 else text[:500] + "…"
        with session_scope() as session:
            end_log(
                session=session,
                log=log,
                full_message={
                    "kind": "agent",
                    "round": rounds + 1,
                    "tool_calls": tool_calls,
                    "content": preview,
                    "ok": True,
                },
                token_usage=usage or None,
            )

    if tool_calls:
        payload = orjson.dumps(tool_calls).decode()
        sink.event(
            {
                "type": "tool-call",
                "content": payload,
                "tool_calls": tool_calls,
            }
        )
        return {
            **state,
            "messages": messages,
            "tool_rounds": rounds + 1,
        }

    if text:
        sink.event({"type": "message", "content": text})
    return {
        **state,
        "messages": messages,
        "final_text": text,
        "tool_rounds": rounds,
    }


def run_tools_node(state: ConfigState) -> ConfigState:
    """Execute tool calls via ToolNode; emit tool-result events.

    Each tool invocation writes its own TOOL_CALL ChatLog row (never a single-slot
    override map: multi-tool parallels must not collapse into one log).

    Node name must not collide with ConfigState channels (never name a node
    after a state key such as the former ``tools`` field).
    """
    sink = StreamSink.from_state(state)
    bound_tools = state.get("bound_tools") or []
    messages = list(state.get("messages") or [])
    record_id = state.get("record_id")
    prev_messages = list(messages)
    ai_with_tools = _find_last_ai_with_tools(prev_messages)
    args_map = _tool_args_by_call_id(ai_with_tools)

    try:
        node = ToolNode(bound_tools)
        result = node.invoke({"messages": messages})
        new_messages: Sequence[BaseMessage] = result.get("messages") or []
    except Exception as e:
        SQLBotLogUtil.error(f"config tools failed: {e}")
        error_msg = _error_message(e)
        with session_scope() as session:
            if record_id:
                # One summary TOOL_CALL so the failure still appears in ExecutionDetails.
                log = start_log(
                    session=session,
                    operate=OperationEnum.TOOL_CALL,
                    record_id=record_id,
                    full_message={"name": "(batch)", "args": {}, "ok": False},
                    local_operation=True,
                )
                end_log(
                    session=session,
                    log=log,
                    full_message={
                        "name": "(batch)",
                        "args": {},
                        "result": error_msg,
                        "ok": False,
                    },
                )
                record_save_error(session, record_id, error_msg)
        return {**state, "error": error_msg}

    tool_msgs = [m for m in new_messages if isinstance(m, ToolMessage)]
    if not tool_msgs:
        prev_len = len(messages)
        added = list(new_messages[prev_len:]) if len(new_messages) > prev_len else []
        tool_msgs = [m for m in added if isinstance(m, ToolMessage)] or list(added)
        messages = list(new_messages) if len(new_messages) >= prev_len else messages + tool_msgs
    else:
        messages = messages + tool_msgs

    for tm in tool_msgs:
        content = tm.content if isinstance(tm.content, str) else str(tm.content)
        name = getattr(tm, "name", None)
        call_id = getattr(tm, "tool_call_id", None)
        call_meta = args_map.get(str(call_id or ""), {})
        if not name:
            name = call_meta.get("name")
        args = call_meta.get("args") or {}
        body = _truncate(content)
        # Heuristic: tool helpers return {"error": ...} for soft failures.
        ok = True
        try:
            parsed = orjson.loads(content) if isinstance(content, str) else None
            if isinstance(parsed, dict) and parsed.get("error"):
                ok = False
        except Exception:
            pass

        sink.event(
            {
                "type": "tool-result",
                "tool_call_id": call_id,
                "name": name,
                "content": content,
            }
        )

        if record_id:
            payload = {
                "name": name,
                "args": args,
                "result": body,
                "ok": ok,
                "tool_call_id": call_id,
            }
            with session_scope() as session:
                log = start_log(
                    session=session,
                    operate=OperationEnum.TOOL_CALL,
                    record_id=record_id,
                    full_message={"name": name, "args": args},
                    local_operation=True,
                )
                end_log(session=session, log=log, full_message=payload)

    return {**state, "messages": messages}


def finish_node(state: ConfigState) -> ConfigState:
    sink = StreamSink.from_state(state)
    record_id = state.get("record_id")
    final_text = state.get("final_text") or ""

    # Process audited via ChatLog; sql_answer is pure assistant prose only.
    answer = final_text

    if record_id:
        with session_scope() as session:
            if answer:
                save_sql_answer(session=session, record_id=record_id, answer=answer)
            record_finish(session, record_id)
    if sink.mode == "markdown" and final_text:
        sink.text(final_text)
    if sink.mode == "json":
        sink.json_result(
            {
                "success": True,
                "record_id": record_id,
                "content": final_text,
            }
        )
    sink.event({"type": "finish", "id": record_id})
    return state


def fail_node(state: ConfigState) -> ConfigState:
    sink = StreamSink.from_state(state)
    error_msg = state.get("error") or "unknown error"
    sink.error(error_msg)
    return state


def _route_after_agent(state: ConfigState) -> Literal["run_tools", "finish", "fail"]:
    if state.get("error"):
        return "fail"
    messages = state.get("messages") or []
    if not messages:
        return "finish"
    last = messages[-1]
    if isinstance(last, AIMessage) and getattr(last, "tool_calls", None):
        rounds = int(state.get("tool_rounds") or 0)
        if rounds > _MAX_TOOL_ROUNDS:
            # Hard stop: do not loop forever if the model keeps calling tools.
            return "finish"
        return "run_tools"
    return "finish"


def _route_after_tools(state: ConfigState) -> Literal["agent", "fail"]:
    if state.get("error"):
        return "fail"
    return "agent"


def build_config_graph(_ctx: Any = None, **_kwargs: Any):
    g = StateGraph(ConfigState)
    g.add_node("prepare", prepare_node)
    g.add_node("agent", agent_node)
    g.add_node("run_tools", run_tools_node)
    g.add_node("finish", finish_node)
    g.add_node("fail", fail_node)

    g.add_edge(START, "prepare")
    g.add_edge("prepare", "agent")
    g.add_conditional_edges(
        "agent",
        _route_after_agent,
        {"run_tools": "run_tools", "finish": "finish", "fail": "fail"},
    )
    g.add_conditional_edges(
        "run_tools",
        _route_after_tools,
        {"agent": "agent", "fail": "fail"},
    )
    g.add_edge("finish", END)
    g.add_edge("fail", END)
    return g.compile()


register_graph("config", build_config_graph)
