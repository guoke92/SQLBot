"""Unified Tool-Agent node and runtime loop for SQLBot."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Literal

from langchain_core.messages import AIMessage, SystemMessage

from apps.chat.agent.budget import budget_from_state
from apps.chat.agent.close import close_kind, compute_verdict, has_turn_result
from apps.chat.agent.context_spec import build_context_spec
from apps.chat.agent.delivery import incomplete_query_message
from apps.chat.agent.init import init_agent_turn
from apps.chat.agent.knowledge import cache_from_state
from apps.chat.agent.tokens import count_message_tokens, count_tokens
from apps.chat.agent.workspace import SqlWorkspace
from apps.chat.agent_copy import (
    compact_agent_final_text,
    truncated_display_note,
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
from apps.conversation.runtime_context import runtime_value
from apps.conversation.sink import StreamSink
from apps.conversation.tooling import (
    attach_tool_calls,
    looks_like_tool_markup,
    resolve_message_tool_calls,
    sanitize_messages_for_model,
    tool_calls_from_message,
)
from common.utils.utils import SQLBotLogUtil


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


def _incomplete_query_state(
    state: Mapping[str, Any], messages: Sequence[Any]
) -> dict[str, Any]:
    text = incomplete_query_message(state)
    return {
        **state,
        "messages": serialize_messages(list(messages)),
        "final_text": text,
        "error": text,
        "public_error": text,
        "outcome": failed_outcome(text, kind="empty_response"),
        "open_tool_spans": {},
    }


def agent_loop_node(state: Mapping[str, Any]) -> dict[str, Any]:
    """Autonomous ReAct loop node: streams thought, calls tools, or finalizes."""
    if state.get("turn_message_start") is None and not state.get("error"):
        state = init_agent_turn(state)
        if state.get("error"):
            return dict(state)

    sink = StreamSink.from_state(state)
    messages = deserialize_messages(list(state.get("messages") or []))
    messages = sanitize_messages_for_model(messages)
    if messages:
        from langchain_core.messages import SystemMessage as _SystemMessage

        from apps.chat.agent.prompt import build_agent_system_prompt

        rebuilt = _SystemMessage(
            content=build_agent_system_prompt(
                knowledge_plane=state.get("knowledge_plane"),
                memory_slots=state.get("memory_slots"),
                state=state,
            )
        )
        if isinstance(messages[0], _SystemMessage):
            messages[0] = rebuilt
        else:
            messages = [rebuilt, *messages]
    tools = list(runtime_value(state, "bound_tools") or [])
    budget = budget_from_state(state)
    record_id = state.get("record_id")
    run_id = str(state.get("run_id") or "") or None
    llm = runtime_value(state, "llm")
    stop_reason = budget.stop_reason
    cache_from_state(state)

    spec = build_context_spec(
        state,
        knowledge_plane=state.get("knowledge_plane"),
        memory_slots=state.get("memory_slots"),
        question=str(getattr(messages[-1], "content", "") or "") if messages else "",
    )
    budget.context_tokens.used = count_message_tokens(messages) + count_tokens(
        spec.turn_brief
    )

    finalizing = budget.exhausted or bool(stop_reason)

    model_messages = messages
    if spec.turn_brief:
        model_messages = [
            *model_messages,
            SystemMessage(content=spec.turn_brief),
        ]
    if finalizing:
        reason = stop_reason or budget.render_brief()
        model_messages = [
            *model_messages,
            SystemMessage(
                content=(
                    f"工具调用已关闭（{reason}）。不要再请求任何工具。"
                    "按 §6 停手终答：有本轮交付卡则只写口径旁白；"
                    "否则直接写结论，不要再提出补检索、目录 SQL 或猜测字段。"
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
                text = text.strip() or incomplete_query_message(state)
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
        if has_turn_result(state):
            return _salvage_after_summary_failure(state, messages)
        return {
            **state,
            "error": format_error_message(exc),
            "outcome": failed_outcome(exc),
        }

    if response is None:
        if has_turn_result(state):
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
        return {
            **state,
            "messages": serialize_messages(updated_messages),
            "open_tool_spans": open_tool_spans,
            "loop_budget": budget.model_dump(mode="json"),
        }

    if looks_like_tool_markup(text) or (
        recovered_calls and not str(text or "").strip()
    ):
        return _incomplete_query_state(state, updated_messages)

    kind = close_kind(
        {**state, "final_text": text},
        has_cards=has_turn_result(state),
    )
    if kind == "empty":
        return _incomplete_query_state(state, updated_messages)

    truncated, limit = SqlWorkspace.from_state(state).truncation()
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
        "loop_budget": budget.model_dump(mode="json"),
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
    action = compute_verdict(state, phase="after_loop").action
    if action in {"execute_tools", "finalize_turn", "fail"}:
        return action  # type: ignore[return-value]
    return "fail"


def route_after_tools_execution(
    state: Mapping[str, Any],
) -> Literal["agent_loop", "await_clarification", "finalize_turn", "fail"]:
    action = compute_verdict(state, phase="after_tools").action
    if action in {"agent_loop", "await_clarification", "finalize_turn", "fail"}:
        return action  # type: ignore[return-value]
    return "fail"
