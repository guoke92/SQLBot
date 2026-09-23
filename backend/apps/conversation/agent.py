"""Reusable model/tool loop nodes for tool-enabled conversation graphs."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal

from langchain_core.messages import AIMessage, SystemMessage

from apps.ai_model.runtime import normalize_message_parts
from apps.chat.steps.observability import sanitize_audit_value
from apps.chat.tools.metadata import get_tool_title_key
from apps.conversation.messages import (
    deserialize_messages,
    message_content_text,
    serialize_messages,
)
from apps.conversation.outcome import failed_outcome, format_error_message
from apps.conversation.process_timeline import open_process_span
from apps.conversation.runtime_context import runtime_value
from apps.conversation.sink import StreamSink
from apps.conversation.tooling import (
    attach_tool_calls,
    looks_like_tool_markup,
    resolve_message_tool_calls,
    tool_calls_from_message,
)
from apps.conversation.usage import usage_from_response
from common.utils.utils import SQLBotLogUtil


def agent_node(state: Mapping[str, Any]) -> dict[str, Any]:
    """Run one model turn and expose only auditable tool-selection metadata."""
    sink = StreamSink.from_state(state)
    messages = deserialize_messages(list(state.get("messages") or []))
    tools = list(runtime_value(state, "bound_tools") or [])
    rounds = int(state.get("tool_rounds") or 0)
    round_limit = int(state.get("tool_round_limit") or 8)
    record_id = state.get("record_id")
    run_id = str(state.get("run_id") or "") or None
    llm = runtime_value(state, "llm")
    stop_reason = str(state.get("tool_stop_reason") or "")
    grounding_retry = bool(state.get("tool_grounding_retry"))
    grounding_marker = str(state.get("tool_free_completion_marker") or "").strip()
    has_tool_evidence = bool(state.get("tool_steps"))
    finalizing = bool(stop_reason) or rounds >= round_limit
    model_messages = messages
    if finalizing:
        reason = stop_reason or f"the tool round limit ({round_limit}) was reached"
        model_messages = [
            *messages,
            SystemMessage(
                content=(
                    f"Tool execution is now closed because {reason}. "
                    "Do not request another tool call. Give the user a concise, "
                    "truthful summary of what succeeded, what failed, and the safe "
                    "next action. Never claim a failed operation succeeded."
                )
            ),
        ]

    thought_span = open_process_span(
        kind="thought",
        record_id=record_id,
        sink=sink,
        run_id=run_id,
        graph_node="agent",
        title_key="chat.timeline.thought",
        thought={"source": "scratchpad", "content": ""},
        local_operation=False,
        ai_modal_id=state.get("ai_modal_id"),
        ai_modal_name=state.get("ai_modal_name"),
    )
    try:
        bound = llm if finalizing or not tools else llm.bind_tools(tools)
        response: AIMessage = bound.invoke(model_messages)
        text = message_content_text(response.content)
        native_calls = tool_calls_from_message(response)
        calls, text = resolve_message_tool_calls(response, text)
        if calls and not native_calls and not finalizing:
            response = attach_tool_calls(response, calls, text)
        if finalizing and (
            calls or looks_like_tool_markup(message_content_text(response.content))
        ):
            calls = []
            text = text.strip()
        safe_calls = sanitize_audit_value(calls)
        rc = normalize_message_parts(response).reasoning
        thought_text = str(rc or (text if calls else "") or "")
        if thought_span is not None:
            if thought_text:
                thought_span.delta(
                    thought_content=thought_text,
                    thought_source="model_reasoning" if rc else "scratchpad",
                    flush=True,
                )
            thought_span.set_usage(usage_from_response(response) or {})
            thought_span.set_output(
                {
                    "kind": "agent",
                    "round": rounds + 1,
                    "finalizing": finalizing,
                    "grounding_retry": grounding_retry,
                    "tool_calls": safe_calls,
                    "content": "" if calls else text[:500],
                    "ok": not (finalizing and calls),
                }
            )
            thought_span.close(
                status="completed",
                summary_key="chat.summary.thought_done",
            )
    except Exception as exc:
        SQLBotLogUtil.error(f"tool agent invoke failed: {exc}")
        if thought_span is not None:
            thought_span.close(status="failed", summary_key="chat.audit.step_failed")
        error = format_error_message(exc)
        return {**state, "error": error, "outcome": failed_outcome(exc)}

    updated_messages = [*messages, response]
    parent_id = thought_span.id if thought_span is not None else None
    if calls:
        if finalizing:
            error = stop_reason or f"Tool agent reached the round limit ({round_limit})"
            return {
                **state,
                "messages": serialize_messages(updated_messages),
                "error": error,
                "outcome": failed_outcome(error, kind="limit_reached"),
            }
        open_tool_spans: dict[str, int] = {}
        for call in calls:
            call_id = str(call.get("id") or "")
            name = str(call.get("name") or "")
            safe_args = sanitize_audit_value(call.get("args") or {})
            tool_span = open_process_span(
                kind="tool",
                record_id=record_id,
                sink=sink,
                run_id=run_id,
                parent_id=parent_id,
                graph_node="agent",
                title_key=get_tool_title_key(name),
                tool={"call_id": call_id, "name": name, "args": safe_args},
                local_operation=True,
            )
            if tool_span is not None and call_id:
                open_tool_spans[call_id] = tool_span.id
        return {
            **state,
            "messages": serialize_messages(updated_messages),
            "tool_rounds": rounds + 1,
            "tool_grounding_retry": False,
            "open_tool_spans": open_tool_spans,
        }

    if not text.strip():
        error = "Model returned an empty response"
        return {
            **state,
            "messages": serialize_messages(updated_messages),
            "error": error,
            "outcome": failed_outcome(error, kind="empty_response"),
        }

    if grounding_marker and not has_tool_evidence and not finalizing:
        stripped = text.lstrip()
        if stripped.startswith(grounding_marker):
            text = stripped[len(grounding_marker) :].lstrip()
            if not text:
                error = "Model returned an empty tool-free response"
                return {
                    **state,
                    "messages": serialize_messages(updated_messages),
                    "error": error,
                    "outcome": failed_outcome(error, kind="empty_response"),
                }
        elif not grounding_retry:
            return {
                **state,
                "messages": serialize_messages(
                    [
                        *updated_messages,
                        SystemMessage(
                            content=(
                                "No system tool was executed in this turn, so the prior "
                                "answer cannot claim that current configuration was "
                                "inspected or changed. Re-evaluate the user's request now: "
                                "call the required tool, or, only for general guidance "
                                f"that needs no system state, answer with {grounding_marker} "
                                "as the exact prefix."
                            )
                        ),
                    ]
                ),
                "final_text": "",
                "tool_grounding_retry": True,
            }
        else:
            error = (
                "No system tool was executed and the model did not identify the "
                "response as general guidance"
            )
            return {
                **state,
                "messages": serialize_messages(updated_messages),
                "error": error,
                "outcome": failed_outcome(error, kind="validation"),
                "tool_grounding_retry": False,
            }

    answer_span = open_process_span(
        kind="answer",
        record_id=record_id,
        sink=sink,
        run_id=run_id,
        parent_id=parent_id,
        graph_node="agent",
        title_key="chat.timeline.answer",
        answer={"content": text},
        local_operation=False,
        ai_modal_id=state.get("ai_modal_id"),
        ai_modal_name=state.get("ai_modal_name"),
    )
    if answer_span is not None:
        answer_span.close(status="completed", summary_key="chat.summary.answer_ready")
    sink.event({"type": "message", "content": text})
    return {
        **state,
        "messages": serialize_messages(updated_messages),
        "final_text": text,
        "tool_stop_reason": "",
        "tool_grounding_retry": False,
        "open_tool_spans": {},
    }


def route_after_agent(
    state: Mapping[str, Any],
) -> Literal["agent", "execute_tools", "finish", "fail"]:
    if state.get("error"):
        return "fail"
    if state.get("tool_grounding_retry"):
        return "agent"
    messages = deserialize_messages(list(state.get("messages") or []))
    if messages:
        last = messages[-1]
        if isinstance(last, AIMessage) and getattr(last, "tool_calls", None):
            return "execute_tools"
    return "finish"


def route_after_tools(state: Mapping[str, Any]) -> Literal["agent", "fail"]:
    return "fail" if state.get("error") else "agent"
