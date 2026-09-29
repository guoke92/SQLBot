"""Unified Tool-Agent node and runtime loop for SQLBot."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Literal

from langchain_core.messages import AIMessage, SystemMessage

from apps.chat.agent_copy import (
    compact_agent_final_text,
    truncated_display_note,
    truncation_from_tool_steps,
)
from apps.chat.agent_knowledge import (
    EXECUTION_ROUND_LIMIT,
    tool_calls_advance_round,
)
from apps.chat.steps.stream import consume_llm
from apps.chat.tools.metadata import get_tool_title_key
from apps.conversation.messages import (
    deserialize_messages,
    serialize_messages,
)
from apps.conversation.outcome import (
    failed_outcome,
    format_error_message,
)
from apps.conversation.process_timeline import open_process_span
from apps.conversation.run_service import ConversationRunCancelled
from apps.conversation.runtime_context import attach_runtime, runtime_value
from apps.conversation.sink import StreamSink
from apps.conversation.tooling import (
    attach_tool_calls,
    looks_like_tool_markup,
    resolve_message_tool_calls,
    sanitize_messages_for_model,
    tool_calls_from_message,
    tool_result_from_message,
)
from common.utils.utils import SQLBotLogUtil

_INCOMPLETE_NO_DATA_KEY = "i18n_chat.agent.incomplete_no_data"
_INCOMPLETE_NO_DATA_FALLBACK = (
    "这次没能查出结果。请换个问法试试，或确认数据源表结构已同步。"
)


def _messages_for_audit(messages: Sequence[Any]) -> list[dict[str, Any]]:
    """Full prompt payload for durable thought spans (bounded later by bound_llm_io)."""
    rows: list[dict[str, Any]] = []
    for message in messages:
        row: dict[str, Any] = {
            "type": str(getattr(message, "type", "") or ""),
            "content": str(getattr(message, "content", "") or ""),
        }
        name = getattr(message, "name", None)
        if name:
            row["name"] = str(name)
        tool_call_id = getattr(message, "tool_call_id", None)
        if tool_call_id:
            row["tool_call_id"] = str(tool_call_id)
        tool_calls = getattr(message, "tool_calls", None)
        if tool_calls:
            row["tool_calls"] = tool_calls
        rows.append(row)
    return rows


def _query_requires_data(state: Mapping[str, Any]) -> bool:
    route = state.get("turn_route") or {}
    kind = str(route.get("task_kind") or "query")
    return kind == "query"


def _required_sql_payload(data: Mapping[str, Any] | Any) -> bool:
    if not isinstance(data, Mapping) or not data.get("sql"):
        return False
    return data.get("required") is not False


def _messages_for_current_turn(
    state: Mapping[str, Any], messages: Sequence[Any]
) -> Sequence[Any]:
    """Slice to this turn only — same window as ``persist_turn_from_state``.

    Continued chats preload prior ``execute_sql_sandbox`` ToolMessages in the
    transcript. Completeness checks must not treat those as this turn's result.
    """
    start = state.get("turn_message_start")
    if start is None:
        return messages
    try:
        idx = int(start)
    except (TypeError, ValueError):
        return messages
    if idx <= 0:
        return messages
    if idx >= len(messages):
        return []
    return messages[idx:]


def _agent_has_sql_result(state: Mapping[str, Any], messages: Sequence[Any]) -> bool:
    """True when *this turn* produced a required=true SQL success.

    ``tool_steps`` is already turn-local. Message history may include prior
    turns via ``agent_transcript``; only messages from ``turn_message_start``
    count. Probes (``required=false``) never count.
    """
    for step in state.get("tool_steps") or []:
        if not isinstance(step, Mapping) or not step.get("ok"):
            continue
        data = (step.get("result") or {}).get("data") or {}
        if _required_sql_payload(data):
            return True
    for message in _messages_for_current_turn(state, messages):
        if str(getattr(message, "name", "") or "") != "execute_sql_sandbox":
            continue
        payload = tool_result_from_message(message)
        if not payload or payload.get("ok") is False:
            continue
        data = payload.get("data") if isinstance(payload.get("data"), Mapping) else {}
        if _required_sql_payload(data):
            return True
    return False


def _incomplete_query_state(
    state: Mapping[str, Any], messages: Sequence[Any]
) -> dict[str, Any]:
    text = _incomplete_query_message(state)
    return {
        **state,
        "messages": serialize_messages(list(messages)),
        "final_text": text,
        "error": text,
        "public_error": text,
        "outcome": failed_outcome(text, kind="empty_response"),
        "open_tool_spans": {},
    }


def _incomplete_query_message(state: Mapping[str, Any]) -> str:
    try:
        llm_service = runtime_value(state, "llm_service")
        trans = getattr(llm_service, "trans", None)
        if callable(trans):
            text = str(trans(_INCOMPLETE_NO_DATA_KEY) or "").strip()
            if text and text != _INCOMPLETE_NO_DATA_KEY:
                return text
    except Exception:
        pass
    return _INCOMPLETE_NO_DATA_FALLBACK


def agent_loop_node(state: Mapping[str, Any]) -> dict[str, Any]:
    """Autonomous ReAct loop node: streams thought, calls tools, or finalizes."""
    if state.get("turn_message_start") is None and not state.get("error"):
        from apps.chat.graphs.turn_init import init_agent_turn

        state = init_agent_turn(state)
        if state.get("error"):
            return dict(state)

    sink = StreamSink.from_state(state)
    messages = deserialize_messages(list(state.get("messages") or []))
    messages = sanitize_messages_for_model(messages)
    tools = list(runtime_value(state, "bound_tools") or [])
    rounds = int(state.get("tool_rounds") or 0)
    round_limit = int(state.get("tool_round_limit") or EXECUTION_ROUND_LIMIT)
    record_id = state.get("record_id")
    run_id = str(state.get("run_id") or "") or None
    llm = runtime_value(state, "llm")
    stop_reason = str(state.get("tool_stop_reason") or "")
    if run_id:
        attach_runtime(
            str(run_id),
            knowledge_plane=dict(state.get("knowledge_plane") or {}),
            probe_sql_calls=int(state.get("probe_sql_calls") or 0),
        )

    finalizing = bool(stop_reason) or rounds >= round_limit
    if (
        finalizing
        and _query_requires_data(state)
        and not _agent_has_sql_result(state, messages)
    ):
        return _incomplete_query_state(state, messages)

    model_messages = messages
    if finalizing:
        reason = stop_reason or f"执行类工具已达 {round_limit} 轮预算"
        model_messages = [
            *messages,
            SystemMessage(
                content=(
                    f"工具调用已关闭（{reason}）。不要再请求任何工具。"
                    "若尚无查询结果，直接按 §6 说明本轮未能取得数据，"
                    "不要再提出补检索、目录 SQL 或猜测字段。"
                )
            ),
        ]

    thought_span = None
    response: AIMessage | None = None
    calls: list[dict[str, Any]] = []
    text = ""
    usage: Mapping[str, Any] = {}
    recovered_calls = False

    def _ensure_thought_span():
        nonlocal thought_span
        if thought_span is not None:
            return thought_span
        thought_span = open_process_span(
            kind="thought",
            record_id=record_id,
            sink=sink,
            run_id=run_id,
            graph_node="agent_loop",
            title_key="chat.timeline.thought",
            thought={"source": "scratchpad", "content": ""},
            local_operation=False,
            ai_modal_id=state.get("ai_modal_id"),
            ai_modal_name=state.get("ai_modal_name"),
        )
        return thought_span

    try:
        bound = llm if finalizing or not tools else llm.bind_tools(tools)
        held_content: list[str] = []
        saw_model_reasoning = False

        def _on_chunk(chunk: Mapping[str, Any]) -> None:
            nonlocal saw_model_reasoning
            reasoning = str(chunk.get("reasoning_content") or "")
            content = str(chunk.get("content") or "")
            if reasoning or chunk.get("has_reasoning"):
                saw_model_reasoning = True
                span = _ensure_thought_span()
                if span is not None:
                    span.delta(
                        thought_content=reasoning or None,
                        thought_source="model_reasoning",
                    )
            if not content:
                return
            # Hold plain content until tool calls appear — final answers belong
            # to the answer span, while tool-bound scratchpad is thought.
            if chunk.get("has_tool_calls"):
                span = _ensure_thought_span()
                if span is not None:
                    if held_content:
                        span.delta(
                            thought_content="".join(held_content),
                            thought_source="scratchpad",
                        )
                        held_content.clear()
                    span.delta(
                        thought_content=content,
                        thought_source="scratchpad",
                    )
            else:
                held_content.append(content)

        call = consume_llm(bound, model_messages, on_chunk=_on_chunk)
        response = call.message
        text = call.content
        usage = call.usage or {}
        native_calls = tool_calls_from_message(response) if response is not None else []
        calls, text = (
            resolve_message_tool_calls(response, text)
            if response is not None
            else ([], text)
        )
        recovered_calls = bool(calls) and not native_calls
        if finalizing:
            if recovered_calls or looks_like_tool_markup(call.content):
                text = text.strip() or _incomplete_query_message(state)
            calls = []
        elif recovered_calls and response is not None:
            response = attach_tool_calls(response, calls, text)
        if calls and held_content:
            span = _ensure_thought_span()
            if span is not None:
                span.delta(
                    thought_content="".join(held_content),
                    thought_source="scratchpad",
                    flush=True,
                )
        if thought_span is not None:
            thought_body = str(
                (thought_span.snapshot().get("thought") or {}).get("content") or ""
            ).strip()
            if thought_body or saw_model_reasoning:
                thought_span.set_usage(usage)
                thought_span.set_input(_messages_for_audit(model_messages))
                thought_span.set_output(
                    {"type": "ai", "content": text, "tool_calls": calls}
                )
                thought_span.close(
                    status="completed",
                    summary_key="chat.summary.thought_done",
                )
            else:
                # Final-answer rounds often have no reasoning channel; do not
                # leave an empty "thought" row beside the answer span.
                thought_span.discard()
                thought_span = None
    except ConversationRunCancelled:
        raise
    except Exception as exc:
        SQLBotLogUtil.error(f"agent loop error: {exc}")
        if thought_span is not None:
            thought_span.close(status="failed", summary_key="chat.audit.step_failed")
        if _agent_has_sql_result(state, messages):
            return _salvage_after_summary_failure(state, messages)
        return {
            **state,
            "error": format_error_message(exc),
            "outcome": failed_outcome(exc),
        }

    if response is None:
        if _agent_has_sql_result(state, messages):
            return _salvage_after_summary_failure(state, messages)
        return {
            **state,
            "error": "Model returned an empty response",
            "outcome": failed_outcome(
                "Model returned an empty response", kind="empty_response"
            ),
        }

    updated_messages = [*messages, response]
    parent_id = thought_span.id if thought_span is not None else None
    open_tool_spans: dict[str, int] = {}
    if calls:
        for item in calls:
            c_name = str(item.get("name") or "")
            call_id = str(item.get("id") or "")
            args = item.get("args") or {}
            tool_span = open_process_span(
                kind="tool",
                record_id=record_id,
                sink=sink,
                run_id=run_id,
                parent_id=parent_id,
                graph_node="agent_loop",
                title_key=get_tool_title_key(c_name),
                tool={"call_id": call_id, "name": c_name, "args": args},
                local_operation=True,
            )
            if tool_span is not None and call_id:
                open_tool_spans[call_id] = tool_span.id
        advanced_rounds = rounds + 1 if tool_calls_advance_round(calls) else rounds
        return {
            **state,
            "messages": serialize_messages(updated_messages),
            "tool_rounds": advanced_rounds,
            "open_tool_spans": open_tool_spans,
        }

    if looks_like_tool_markup(text) or (
        recovered_calls and not str(text or "").strip()
    ):
        return _incomplete_query_state(state, updated_messages)

    if _query_requires_data(state) and not _agent_has_sql_result(
        state, updated_messages
    ):
        return _incomplete_query_state(state, updated_messages)

    truncated, limit = truncation_from_tool_steps(state.get("tool_steps"))
    trans = None
    try:
        trans = getattr(runtime_value(state, "llm_service"), "trans", None)
    except Exception:
        trans = None
    text = compact_agent_final_text(
        text,
        truncated=truncated,
        limit=limit,
        truncation_note=truncated_display_note(limit, trans=trans),
    )

    answer_span = open_process_span(
        kind="answer",
        record_id=record_id,
        sink=sink,
        run_id=run_id,
        parent_id=parent_id,
        graph_node="agent_loop",
        title_key="chat.timeline.answer",
        answer={"content": text},
        local_operation=False,
        ai_modal_id=state.get("ai_modal_id"),
        ai_modal_name=state.get("ai_modal_name"),
    )
    if answer_span is not None:
        # When the thought span was discarded (no reasoning channel), keep the
        # full model I/O on the answer span for Execution Details.
        if thought_span is None:
            answer_span.set_input(_messages_for_audit(model_messages))
            answer_span.set_output({"type": "ai", "content": text, "tool_calls": calls})
            if usage:
                answer_span.set_usage(usage)
        answer_span.close(status="completed", summary_key="chat.summary.answer_ready")
    return {
        **state,
        "messages": serialize_messages(updated_messages),
        "final_text": text,
        "open_tool_spans": {},
    }


def _salvage_after_summary_failure(
    state: Mapping[str, Any],
    messages: Sequence[Any],
) -> dict[str, Any]:
    """Keep a successful SQL result even when the closing LLM round fails."""
    return {
        **state,
        "messages": serialize_messages(messages),
        "final_text": str(state.get("final_text") or ""),
        "open_tool_spans": {},
        "analysis_incomplete": True,
    }


def route_after_agent_loop(
    state: Mapping[str, Any],
) -> Literal["execute_tools", "finalize_turn", "fail"]:
    messages = deserialize_messages(list(state.get("messages") or []))
    if state.get("error"):
        if _agent_has_sql_result(state, messages) or state.get("analysis_incomplete"):
            return "finalize_turn"
        return "fail"
    if messages:
        last = messages[-1]
        if isinstance(last, AIMessage) and getattr(last, "tool_calls", None):
            return "execute_tools"
    return "finalize_turn"


def route_after_tools_execution(
    state: Mapping[str, Any],
) -> Literal["agent_loop", "await_clarification", "finalize_turn", "fail"]:
    if state.get("error"):
        return "fail"
    from apps.chat.tools.complete_answer import has_terminal_text_answer

    for step in state.get("tool_steps") or []:
        if isinstance(step, Mapping):
            data = step.get("result", {}).get("data") or {}
            if isinstance(data, Mapping) and data.get("interrupt_required"):
                return "await_clarification"
    if has_terminal_text_answer(state.get("tool_steps")):
        return "finalize_turn"
    return "agent_loop"
