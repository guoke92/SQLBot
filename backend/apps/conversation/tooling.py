"""Shared tool execution contract for tool-enabled conversation graphs."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from typing import Any, TypedDict, cast

import orjson
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from langchain_core.tools import BaseTool

from apps.chat.models.chat_model import OperationEnum
from apps.chat.steps.observability import log_span, sanitize_audit_value
from apps.conversation.messages import deserialize_messages, serialize_messages
from apps.conversation.outcome import FailureInfo, FailureKind, classify_failure
from apps.conversation.runtime_context import runtime_value

_LOG_RESULT_LIMIT = 4000
class ToolResult(TypedDict):
    ok: bool
    summary: str
    data: Any
    error: str | None
    failure: FailureInfo | None


def tool_success(summary: str, data: Any = None) -> ToolResult:
    return {
        "ok": True,
        "summary": summary,
        "data": data,
        "error": None,
        "failure": None,
    }


def tool_failure(
    summary: str,
    error: str,
    data: Any = None,
    *,
    failure: FailureInfo | None = None,
) -> ToolResult:
    return {
        "ok": False,
        "summary": summary,
        "data": data,
        "error": error,
        "failure": failure or classify_failure(error),
    }


def tool_calls_from_message(message: AIMessage) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []
    for index, call in enumerate(getattr(message, "tool_calls", None) or []):
        if isinstance(call, Mapping):
            call_id = call.get("id")
            name = call.get("name")
            args = call.get("args") or {}
        else:
            call_id = getattr(call, "id", None)
            name = getattr(call, "name", None)
            args = getattr(call, "args", {}) or {}
        calls.append(
            {
                "id": str(call_id or f"tool_call_{index}"),
                "name": str(name or ""),
                "args": dict(args) if isinstance(args, Mapping) else {},
            }
        )
    return calls


def last_tool_call_message(messages: Sequence[BaseMessage]) -> AIMessage | None:
    for message in reversed(messages):
        if isinstance(message, AIMessage) and getattr(message, "tool_calls", None):
            return message
    return None


def normalize_tool_result(raw: Any) -> ToolResult:
    """Validate the single result contract returned by every registered tool."""
    if not isinstance(raw, Mapping):
        raise TypeError("Tool must return a ToolResult mapping")
    required = {"ok", "summary", "data", "error", "failure"}
    actual = set(raw)
    if actual != required:
        raise TypeError(
            "ToolResult fields must be exactly "
            f"{sorted(required)}; missing={sorted(required - actual)}, "
            f"unexpected={sorted(actual - required)}"
        )
    ok = raw["ok"]
    if not isinstance(ok, bool):
        raise TypeError("ToolResult.ok must be a boolean")
    summary = raw["summary"]
    if not isinstance(summary, str) or not summary.strip():
        raise TypeError("ToolResult.summary must be a non-empty string")
    error = raw["error"]
    failure = raw["failure"]
    if ok and error is not None:
        raise TypeError("Successful ToolResult.error must be null")
    if ok and failure is not None:
        raise TypeError("Successful ToolResult.failure must be null")
    if not ok and (not isinstance(error, str) or not error.strip()):
        raise TypeError("Failed ToolResult.error must be a non-empty string")
    if not ok and (
        not isinstance(failure, Mapping)
        or not isinstance(failure.get("kind"), str)
        or not isinstance(failure.get("message"), str)
        or not isinstance(failure.get("retryable"), bool)
    ):
        raise TypeError("Failed ToolResult.failure must be a FailureInfo mapping")
    normalized_failure: FailureInfo | None = None
    if isinstance(failure, Mapping):
        normalized_failure = {
            "kind": cast(FailureKind, failure["kind"]),
            "message": failure["message"],
            "retryable": failure["retryable"],
        }
        if isinstance(failure.get("step_index"), int):
            normalized_failure["step_index"] = failure["step_index"]
    return {
        "ok": ok,
        "summary": summary,
        "data": raw["data"],
        "error": error,
        "failure": normalized_failure,
    }


def serialize_tool_result(result: ToolResult) -> str:
    return orjson.dumps(result).decode()


def _truncate_for_log(value: Any, limit: int = _LOG_RESULT_LIMIT) -> Any:
    text = orjson.dumps(value, default=str).decode()
    if len(text) <= limit:
        return value
    return {"truncated": True, "preview": text[:limit]}


def _tool_call_signature(name: str, args: Mapping[str, Any]) -> str:
    """Hash one call for loop detection without retaining credentials in state."""
    payload = orjson.dumps(
        {"name": name, "args": args},
        option=orjson.OPT_SORT_KEYS,
        default=str,
    )
    return hashlib.sha256(payload).hexdigest()


def execute_tools_node(state: Mapping[str, Any]) -> dict[str, Any]:
    """Execute the latest AI tool calls sequentially with per-call audit spans."""
    messages = deserialize_messages(list(state.get("messages") or []))
    ai_message = last_tool_call_message(messages)
    if ai_message is None:
        return {**state, "error": "Tool execution requested without tool calls"}

    tools = {
        tool.name: tool
        for tool in (runtime_value(state, "bound_tools") or [])
        if isinstance(tool, BaseTool) and tool.name
    }
    record_id = state.get("record_id")
    tool_messages: list[ToolMessage] = []
    # State owns the normalized cross-round outcome; chat_log remains the
    # detailed audit timeline. Preserve earlier rounds so final status cannot
    # be decided from the last tool call alone.
    tool_steps: list[dict[str, Any]] = [
        dict(item)
        for item in (state.get("tool_steps") or [])
        if isinstance(item, Mapping)
    ]
    previous_failure = str(state.get("last_tool_failure_signature") or "")
    consecutive_failures = int(state.get("consecutive_tool_failures") or 0)
    stop_reason = ""

    for call in tool_calls_from_message(ai_message):
        call_id = call["id"]
        name = call["name"]
        args = call["args"]
        safe_args = sanitize_audit_value(args)
        initial = {
            "kind": "tool",
            "tool_call_id": call_id,
            "name": name,
            "args": safe_args,
            "status": "running",
        }

        with log_span(
            operate=OperationEnum.TOOL_CALL,
            record_id=record_id,
            local_operation=True,
            graph_node="execute_tools",
            title_key="chat.log.TOOL_CALL",
            brief=name,
            initial_payload=initial,
        ) as span:
            span.set_input({"tool": name, "arguments": safe_args})
            tool = tools.get(name)
            try:
                if tool is None:
                    result: ToolResult = tool_failure(
                        f"Unknown tool: {name}",
                        f"Unknown tool: {name}",
                    )
                else:
                    result = normalize_tool_result(tool.invoke(args))
            except Exception as exc:
                result = tool_failure(f"{name} failed", str(exc))

            safe_result = sanitize_audit_value(result)
            span.set_output(safe_result)
            model_content = serialize_tool_result(safe_result)
            if not result["ok"]:
                span.mark_failed(str(result.get("error") or result["summary"]))
            span["payload"] = {
                **initial,
                "status": "completed",
                "result": _truncate_for_log(safe_result),
                "ok": result["ok"],
            }
            tool_messages.append(
                ToolMessage(
                    content=model_content,
                    tool_call_id=call_id,
                    name=name or None,
                )
            )
            if result["ok"]:
                tool_steps.append({"result": {"tool": name}})
                previous_failure = ""
                consecutive_failures = 0
            else:
                tool_steps.append(
                    {
                        "error": result["error"],
                        "failure": result["failure"],
                        "tool": name,
                    }
                )
                signature = _tool_call_signature(name, args)
                if signature == previous_failure:
                    consecutive_failures += 1
                else:
                    previous_failure = signature
                    consecutive_failures = 1

                failure = result["failure"] or {}
                if not bool(failure.get("retryable")):
                    stop_reason = (
                        f"{name} failed with a non-retryable "
                        f"{failure.get('kind') or 'execution'} error"
                    )
                elif consecutive_failures >= 2:
                    stop_reason = f"{name} repeated the same failed call"

    return {
        **state,
        "messages": serialize_messages([*messages, *tool_messages]),
        "tool_steps": tool_steps,
        "last_tool_failure_signature": previous_failure,
        "consecutive_tool_failures": consecutive_failures,
        "tool_stop_reason": stop_reason,
    }
