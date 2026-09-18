"""Shared tool execution contract for tool-enabled conversation graphs."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping, Sequence
from typing import Any, TypedDict, cast

import orjson
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage

from apps.chat.agent_knowledge import KNOWLEDGE_TOOLS, AgentKnowledgePlane
from apps.chat.memory_slots import MemorySlots
from apps.chat.steps.observability import sanitize_audit_value
from apps.chat.tools.metadata import get_tool_title_key
from apps.conversation.messages import deserialize_messages, serialize_messages
from apps.conversation.outcome import FailureInfo, FailureKind, classify_failure
from apps.conversation.process_timeline import (
    PREVIEW_ROW_LIMIT,
    attach_process_span,
    attach_running_tool_span,
    open_process_span,
    preview_rows,
)
from apps.conversation.runtime_context import (
    attach_runtime,
    peek_runtime,
    runtime_value,
    tool_call_scope,
)
from apps.conversation.sink import StreamSink

_LOG_RESULT_LIMIT = 4000
_DSML_MARK = r"(?:[|｜]{0,4})"
_DSML_OPEN = rf"<{_DSML_MARK}DSML{_DSML_MARK}"
_DSML_INVOKE_RE = re.compile(
    rf"{_DSML_OPEN}invoke\s+name=\"([^\"]+)\"\s*>(.*?)</{_DSML_MARK}DSML{_DSML_MARK}invoke>",
    re.DOTALL | re.IGNORECASE,
)
_DSML_PARAM_RE = re.compile(
    rf"{_DSML_OPEN}parameter\s+name=\"([^\"]+)\"[^>]*>(.*?)</{_DSML_MARK}DSML{_DSML_MARK}parameter>",
    re.DOTALL | re.IGNORECASE,
)
_DSML_BLOCK_RE = re.compile(
    rf"{_DSML_OPEN}tool_calls\s*>(.*?)</{_DSML_MARK}DSML{_DSML_MARK}tool_calls>",
    re.DOTALL | re.IGNORECASE,
)


def looks_like_tool_markup(text: str) -> bool:
    body = str(text or "")
    if not body.strip():
        return False
    lowered = body.lower()
    return "dsml" in lowered and ("tool_calls" in lowered or "invoke" in lowered)


def parse_markup_tool_calls(text: str) -> list[dict[str, Any]]:
    """Parse vendor DSML / XML tool-call markup leaked into message content."""
    body = str(text or "")
    if not body.strip():
        return []
    calls: list[dict[str, Any]] = []
    for index, match in enumerate(_DSML_INVOKE_RE.finditer(body)):
        name = str(match.group(1) or "").strip()
        inner = match.group(2) or ""
        args: dict[str, Any] = {}
        for param in _DSML_PARAM_RE.finditer(inner):
            key = str(param.group(1) or "").strip()
            if key:
                args[key] = str(param.group(2) or "").strip()
        if name:
            calls.append(
                {
                    "id": f"markup_call_{index}",
                    "name": name,
                    "args": args,
                }
            )
    return calls


def strip_markup_tool_calls(text: str) -> str:
    body = str(text or "")
    if not body:
        return ""
    cleaned = _DSML_BLOCK_RE.sub(" ", body)
    cleaned = _DSML_INVOKE_RE.sub(" ", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def resolve_message_tool_calls(
    message: AIMessage, text: str
) -> tuple[list[dict[str, Any]], str]:
    """Native tool_calls win; otherwise recover DSML markup from content."""
    calls = tool_calls_from_message(message)
    raw = text if text is not None else str(getattr(message, "content", "") or "")
    if calls:
        return calls, strip_markup_tool_calls(raw) if looks_like_tool_markup(
            raw
        ) else raw
    parsed = parse_markup_tool_calls(raw)
    if not parsed:
        if looks_like_tool_markup(raw):
            return [], strip_markup_tool_calls(raw)
        return [], raw
    return parsed, strip_markup_tool_calls(raw)


def attach_tool_calls(
    message: AIMessage, calls: Sequence[Mapping[str, Any]], content: str
) -> AIMessage:
    """Return a copy of ``message`` carrying ``calls`` so routing can execute them."""
    payload = [
        {
            "name": str(item.get("name") or ""),
            "args": dict(item.get("args") or {})
            if isinstance(item.get("args"), Mapping)
            else {},
            "id": str(item.get("id") or f"tool_call_{index}"),
            "type": "tool_call",
        }
        for index, item in enumerate(calls)
    ]
    return AIMessage(
        content=content,
        tool_calls=payload,
        id=getattr(message, "id", None),
        additional_kwargs=dict(getattr(message, "additional_kwargs", None) or {}),
        response_metadata=dict(getattr(message, "response_metadata", None) or {}),
    )


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


def _knowledge_tool_close(
    name: str, result: Mapping[str, Any]
) -> tuple[str, dict[str, Any]]:
    """Knowledge tools report hit counts; other tools keep 执行成功."""
    if not result.get("ok"):
        return "chat.summary.tool_failed", {"tool": name}
    data = result.get("data") if isinstance(result.get("data"), Mapping) else {}
    if name == "get_table_schema":
        count = len(data.get("tables") or data.get("added_tables") or [])
        return "chat.summary.schema_loaded", {"count": count}
    if name == "get_table_relations":
        count = len(data.get("direct") or []) + len(data.get("bridges") or [])
        return "chat.summary.relations_loaded", {"count": count}
    if name == "search_knowledge":
        count = int(data.get("hit_count") or len(data.get("page_keys") or []) or 0)
        return "chat.summary.wiki_prepared", {"count": count}
    if name == "get_dict_values":
        count = len(data.get("values") or [])
        return "chat.summary.dict_loaded", {"count": count}
    return "chat.summary.tool_ok", {"tool": name}


def execute_tools_node(state: Mapping[str, Any]) -> dict[str, Any]:
    """Execute the latest AI tool calls sequentially with per-call audit spans."""
    messages = deserialize_messages(list(state.get("messages") or []))
    ai_message = last_tool_call_message(messages)
    if ai_message is None:
        return {**state, "error": "Tool execution requested without tool calls"}

    bound_tools = state.get("bound_tools")
    if not bound_tools:
        try:
            bound_tools = runtime_value(state, "bound_tools")
        except Exception:
            bound_tools = []
    tools = {
        tool.name: tool
        for tool in (bound_tools or [])
        if hasattr(tool, "name") and tool.name
    }
    sink = StreamSink.from_state(state)
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

        open_ids = dict(state.get("open_tool_spans") or {})
        run_id = str(state.get("run_id") or "") or None
        span = None
        if call_id in open_ids:
            span = attach_process_span(int(open_ids[call_id]), sink=sink)
        if span is None and record_id:
            # Fallback when LangGraph dropped open_tool_spans or state was lost
            span = attach_running_tool_span(
                record_id=int(record_id),
                call_id=call_id,
                run_id=run_id,
                sink=sink,
            )
        if span is None and record_id:
            span = open_process_span(
                kind="tool",
                record_id=record_id,
                sink=sink,
                run_id=run_id,
                graph_node="execute_tools",
                title_key=get_tool_title_key(name),
                tool={"call_id": call_id, "name": name, "args": safe_args},
                local_operation=True,
            )
        if span is not None:
            span.set_input({"tool": name, "arguments": safe_args, **initial})

        tool = tools.get(name)
        try:
            if tool is None:
                result: ToolResult = tool_failure(
                    f"Unknown tool: {name}",
                    f"Unknown tool: {name}",
                )
            else:
                with tool_call_scope(call_id):
                    result = normalize_tool_result(tool.invoke(args))
        except Exception as exc:
            result = tool_failure(f"{name} failed", str(exc))

        safe_result = sanitize_audit_value(result)
        model_content = serialize_tool_result(safe_result)
        if span is not None:
            span.set_output(_truncate_for_log(safe_result))
            summary_key, summary_params = _knowledge_tool_close(name, result)
            span.close(
                status="completed" if result["ok"] else "failed",
                summary_key=summary_key,
                summary_params=summary_params,
                tool={"call_id": call_id, "name": name, "args": safe_args},
            )
            data = result.get("data") if isinstance(result.get("data"), Mapping) else {}
            if result["ok"] and isinstance(data, Mapping) and data.get("dataset_id"):
                art = open_process_span(
                    kind="artifact",
                    record_id=record_id,
                    sink=sink,
                    run_id=str(state.get("run_id") or "") or None,
                    parent_id=span.id,
                    graph_node="execute_tools",
                    title_key="chat.timeline.artifact",
                    artifact={
                        "dataset_id": data.get("dataset_id"),
                        "sql": data.get("sql")
                        or (args.get("sql") if isinstance(args, Mapping) else ""),
                        "fields": list(data.get("fields") or []),
                        "row_count": data.get("row_count") or data.get("total_rows"),
                        "truncated": bool(data.get("truncated")),
                        "limit": data.get("limit"),
                        "preview_rows": preview_rows(
                            data.get("preview_rows") or data.get("sample_rows") or [],
                            limit=PREVIEW_ROW_LIMIT,
                        ),
                    },
                    local_operation=True,
                )
                if art is not None:
                    art.close(
                        status="completed",
                        summary_key="chat.summary.query_rows",
                        summary_params={
                            "count": int(
                                data.get("row_count") or data.get("total_rows") or 0
                            )
                        },
                    )
            if result["ok"] and isinstance(data, Mapping) and name == "compare_results":
                for side, side_data in (
                    ("base", data.get("base")),
                    ("new", data.get("new")),
                ):
                    if not isinstance(side_data, Mapping) or not side_data.get("sql"):
                        continue
                    art = open_process_span(
                        kind="artifact",
                        record_id=record_id,
                        sink=sink,
                        run_id=str(state.get("run_id") or "") or None,
                        parent_id=span.id,
                        graph_node="execute_tools",
                        title_key="chat.timeline.artifact",
                        title_params={"side": side},
                        artifact={
                            "dataset_id": side_data.get("dataset_id")
                            or f"{call_id}_{side}",
                            "sql": side_data.get("sql"),
                            "row_count": side_data.get("row_count"),
                            "preview_rows": preview_rows(
                                side_data.get("sample_rows") or [],
                                limit=PREVIEW_ROW_LIMIT,
                            ),
                        },
                        local_operation=True,
                    )
                    if art is not None:
                        art.close(
                            status="completed", summary_key="chat.summary.tool_ok"
                        )

        tool_messages.append(
            ToolMessage(
                content=model_content,
                tool_call_id=call_id,
                name=name or None,
            )
        )
        if result["ok"]:
            tool_steps.append(
                {
                    "tool": name,
                    "name": name,
                    "result": safe_result,
                    "ok": True,
                }
            )
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

    run_id = str(state.get("run_id") or "")
    snap = peek_runtime(run_id) if run_id else None
    plane = AgentKnowledgePlane.from_dump(
        (snap or {}).get("knowledge_plane") or state.get("knowledge_plane")
    )
    probe_sql_calls = int(
        (snap or {}).get("probe_sql_calls")
        if snap and snap.get("probe_sql_calls") is not None
        else (state.get("probe_sql_calls") or 0)
    )
    if run_id:
        attach_runtime(
            run_id,
            knowledge_plane=plane.to_dump(),
            probe_sql_calls=probe_sql_calls,
        )

    outgoing = [*messages, *tool_messages]
    knowledge_used = any(
        getattr(item, "name", "") in KNOWLEDGE_TOOLS for item in tool_messages
    )
    if knowledge_used:
        plane.knowledge_rounds = int(plane.knowledge_rounds or 0) + 1
        slots = dict(state.get("memory_slots") or {})
        baseline = None
        try:
            baseline = MemorySlots.model_validate(slots).extract_change_baseline()
        except Exception:
            baseline = None
        outgoing = plane.apply_to_system_message(
            outgoing,
            memory_slots=slots,
            change_baseline=baseline,
        )

    return {
        **state,
        "messages": serialize_messages(outgoing),
        "tool_steps": tool_steps,
        "last_tool_failure_signature": previous_failure,
        "consecutive_tool_failures": consecutive_failures,
        "tool_stop_reason": stop_reason,
        "knowledge_plane": plane.to_dump(),
        "probe_sql_calls": probe_sql_calls,
    }
