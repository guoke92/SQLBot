"""Reusable model/tool loop nodes for tool-enabled conversation graphs."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal

from langchain_core.messages import AIMessage, SystemMessage

from apps.chat.models.chat_model import OperationEnum
from apps.chat.steps.observability import log_span
from apps.conversation.outcome import failed_outcome, format_error_message
from apps.conversation.sink import StreamSink
from apps.conversation.tooling import redact_value, tool_calls_from_message
from apps.conversation.usage import usage_from_response
from common.utils.utils import SQLBotLogUtil


def agent_node(state: Mapping[str, Any]) -> dict[str, Any]:
    """Run one model turn and expose only auditable tool-selection metadata."""
    sink = StreamSink.from_state(state)
    messages = list(state.get("messages") or [])
    tools = list(state.get("bound_tools") or [])
    rounds = int(state.get("tool_rounds") or 0)
    round_limit = int(state.get("tool_round_limit") or 8)
    record_id = state.get("record_id")
    llm = state["llm"]
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

    try:
        with log_span(
            operate=OperationEnum.AGENT_STEP,
            record_id=record_id,
            ai_modal_id=state.get("ai_modal_id"),
            ai_modal_name=state.get("ai_modal_name"),
            local_operation=False,
            graph_node="agent",
            brief="finalize" if finalizing else f"round {rounds + 1}",
            initial_payload={
                "kind": "agent",
                "round": rounds + 1,
                "finalizing": finalizing,
            },
        ) as span:
            bound = llm if finalizing or not tools else llm.bind_tools(tools)
            response: AIMessage = bound.invoke(model_messages)
            calls = tool_calls_from_message(response)
            safe_calls = redact_value(calls)
            text = (
                response.content
                if isinstance(response.content, str)
                else str(response.content or "")
            )
            span["payload"] = {
                "kind": "agent",
                "round": rounds + 1,
                "finalizing": finalizing,
                "grounding_retry": grounding_retry,
                "tool_calls": safe_calls,
                "content": "" if calls else text[:500],
                "ok": not (finalizing and calls),
            }
            span["token_usage"] = usage_from_response(response)
    except Exception as exc:
        SQLBotLogUtil.error(f"tool agent invoke failed: {exc}")
        error = format_error_message(exc)
        return {**state, "error": error, "outcome": failed_outcome(exc)}

    updated_messages = [*messages, response]
    if calls:
        if finalizing:
            error = stop_reason or f"Tool agent reached the round limit ({round_limit})"
            return {
                **state,
                "messages": updated_messages,
                "error": error,
                "outcome": failed_outcome(error, kind="limit_reached"),
            }
        next_round = rounds + 1
        return {
            **state,
            "messages": updated_messages,
            "tool_rounds": next_round,
            "tool_grounding_retry": False,
        }

    if not text.strip():
        error = "Model returned an empty response"
        return {
            **state,
            "messages": updated_messages,
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
                    "messages": updated_messages,
                    "error": error,
                    "outcome": failed_outcome(error, kind="empty_response"),
                }
        elif not grounding_retry:
            return {
                **state,
                "messages": [
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
                ],
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
                "messages": updated_messages,
                "error": error,
                "outcome": failed_outcome(error, kind="validation"),
                "tool_grounding_retry": False,
            }

    sink.event({"type": "message", "content": text})
    return {
        **state,
        "messages": updated_messages,
        "final_text": text,
        "tool_stop_reason": "",
        "tool_grounding_retry": False,
    }


def route_after_agent(
    state: Mapping[str, Any],
) -> Literal["agent", "execute_tools", "finish", "fail"]:
    if state.get("error"):
        return "fail"
    if state.get("tool_grounding_retry"):
        return "agent"
    messages = state.get("messages") or []
    if messages:
        last = messages[-1]
        if isinstance(last, AIMessage) and getattr(last, "tool_calls", None):
            return "execute_tools"
    return "finish"


def route_after_tools(state: Mapping[str, Any]) -> Literal["agent", "fail"]:
    return "fail" if state.get("error") else "agent"
