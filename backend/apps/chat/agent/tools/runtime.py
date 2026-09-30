"""Chat-agent tool dispatch: parallel-safe knowledge tools, serial exclusive tools."""

from __future__ import annotations

import contextvars
from collections.abc import Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from langchain_core.messages import ToolMessage

from apps.chat.agent.audit import tool_close_keys
from apps.chat.agent.budget import budget_from_state
from apps.chat.agent.close import delivery_from_state, stamp_delivery
from apps.chat.agent.knowledge import (
    cache_from_state,
    load_plane,
    merge_published,
    publish_plane,
    take_working,
)
from apps.chat.agent.tools.effect import signals_from_result
from apps.chat.agent_config.defaults import DEFAULT_PARALLEL_SAFE
from apps.chat.agent_knowledge import KNOWLEDGE_BUDGET_SKIP, KNOWLEDGE_TOOLS
from apps.chat.steps.observability import sanitize_audit_value
from apps.conversation.messages import deserialize_messages, serialize_messages
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
from apps.conversation.tooling import (
    ToolResult,
    last_tool_call_message,
    normalize_tool_result,
    render_tool_message,
    tool_calls_from_message,
    tool_failure,
    tool_success,
)
from apps.conversation.tooling import (
    _tool_call_signature as tool_call_signature,
)
from apps.conversation.tooling import (
    _truncate_for_log as truncate_for_log,
)


def _tool_message_skipped(message: ToolMessage) -> bool:
    from apps.conversation.tooling import tool_result_from_message

    payload = tool_result_from_message(message)
    data = payload.get("data") if isinstance(payload.get("data"), Mapping) else {}
    return isinstance(data, Mapping) and data.get("skipped") == KNOWLEDGE_BUDGET_SKIP


def _knowledge_skip_result() -> ToolResult:
    return tool_success(
        "knowledge budget exhausted",
        {"skipped": KNOWLEDGE_BUDGET_SKIP},
    )


def _invoke_one(
    tools: Mapping[str, Any],
    call: Mapping[str, Any],
    *,
    skip_knowledge: bool = False,
) -> ToolResult:
    name = str(call.get("name") or "")
    args = call.get("args") or {}
    call_id = str(call.get("id") or "")
    if skip_knowledge and name in KNOWLEDGE_TOOLS:
        return _knowledge_skip_result()
    tool = tools.get(name)
    try:
        if tool is None:
            return tool_failure(f"Unknown tool: {name}", f"Unknown tool: {name}")
        with tool_call_scope(call_id):
            return normalize_tool_result(tool.invoke(args))
    except Exception as exc:
        return tool_failure(f"{name} failed", str(exc))


def _dispatch_results(
    tools: Mapping[str, Any],
    calls: Sequence[Mapping[str, Any]],
    *,
    skip_knowledge: bool = False,
) -> tuple[list[ToolResult], list[dict[str, Any]]]:
    if not calls:
        return [], []
    exclusive = any(
        str(call.get("name") or "") not in DEFAULT_PARALLEL_SAFE for call in calls
    )
    if exclusive or len(calls) == 1:
        results = [
            _invoke_one(tools, call, skip_knowledge=skip_knowledge) for call in calls
        ]
        dump = take_working()
        return results, [dump] if dump else []

    parent_snapshots = [contextvars.copy_context() for _ in calls]
    results: list[ToolResult | None] = [None] * len(calls)
    dumps: list[dict[str, Any] | None] = [None] * len(calls)

    def _run(index: int) -> tuple[int, ToolResult, dict[str, Any] | None]:
        def _inner() -> tuple[ToolResult, dict[str, Any] | None]:
            result = _invoke_one(tools, calls[index], skip_knowledge=skip_knowledge)
            return result, take_working()

        result, dump = parent_snapshots[index].run(_inner)
        return index, result, dump

    workers = min(8, len(calls))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futs = [pool.submit(_run, index) for index in range(len(calls))]
        for fut in as_completed(futs):
            index, result, dump = fut.result()
            results[index] = result
            dumps[index] = dump
    return (
        [
            item if item is not None else tool_failure("empty", "empty")
            for item in results
        ],
        [item for item in dumps if item],
    )


def _record_artifact(
    *,
    name: str,
    result: Mapping[str, Any],
    args: Mapping[str, Any],
    call_id: str,
    record_id: Any,
    run_id: str | None,
    sink: StreamSink,
    parent_id: int | None,
) -> None:
    data = result.get("data") if isinstance(result.get("data"), Mapping) else {}
    if not result.get("ok") or not isinstance(data, Mapping):
        return
    if data.get("dataset_id"):
        art = open_process_span(
            kind="artifact",
            record_id=record_id,
            sink=sink,
            run_id=run_id,
            parent_id=parent_id,
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
                    "count": int(data.get("row_count") or data.get("total_rows") or 0)
                },
            )
    if name != "compare_results":
        return
    for side, side_data in (("base", data.get("base")), ("new", data.get("new"))):
        if not isinstance(side_data, Mapping) or not side_data.get("sql"):
            continue
        art = open_process_span(
            kind="artifact",
            record_id=record_id,
            sink=sink,
            run_id=run_id,
            parent_id=parent_id,
            graph_node="execute_tools",
            title_key="chat.timeline.artifact",
            title_params={"side": side},
            artifact={
                "dataset_id": side_data.get("dataset_id") or f"{call_id}_{side}",
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
            art.close(status="completed", summary_key="chat.summary.tool_ok")


def execute_tools_node(state: Mapping[str, Any]) -> dict[str, Any]:
    """Execute the latest AI tool calls; knowledge tools may run in parallel."""
    cache_from_state(state)
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
    tool_steps: list[dict[str, Any]] = [
        dict(item)
        for item in (state.get("tool_steps") or [])
        if isinstance(item, Mapping)
    ]
    previous_failure = str(state.get("last_tool_failure_signature") or "")
    consecutive_failures = int(state.get("consecutive_tool_failures") or 0)
    stop_reason = ""
    open_ids = dict(state.get("open_tool_spans") or {})
    run_id = str(state.get("run_id") or "") or None
    delivery = delivery_from_state(state)

    calls = tool_calls_from_message(ai_message)
    try:
        from apps.chat.agent_config import load_agent_config_for_run

        budget = budget_from_state(state, config=load_agent_config_for_run())
    except Exception:
        budget = budget_from_state(state)
    skip_knowledge = budget.knowledge_exhausted
    results, plane_dumps = _dispatch_results(
        tools, calls, skip_knowledge=skip_knowledge
    )

    for call, result in zip(calls, results, strict=True):
        call_id = str(call.get("id") or "")
        name = str(call.get("name") or "")
        args = call.get("args") or {}
        safe_args = sanitize_audit_value(args)
        initial = {
            "kind": "tool",
            "tool_call_id": call_id,
            "name": name,
            "args": safe_args,
            "status": "running",
        }

        span = None
        if call_id in open_ids:
            span = attach_process_span(int(open_ids[call_id]), sink=sink)
        if span is None and record_id:
            span = attach_running_tool_span(
                record_id=int(record_id),
                call_id=call_id,
                run_id=run_id,
                sink=sink,
            )
        if span is None and record_id:
            from apps.chat.tools.metadata import get_tool_title_key

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

        safe_result = sanitize_audit_value(result)
        model_content = render_tool_message(name, safe_result)
        signals = signals_from_result(
            name, safe_result if isinstance(safe_result, Mapping) else {}
        )
        delivery = stamp_delivery(delivery, result=safe_result, signals=signals)
        if run_id:
            attach_runtime(run_id, turn_delivery=delivery.model_dump())
        if span is not None:
            span.set_output(truncate_for_log(safe_result))
            if signals.interrupt:
                data = (
                    safe_result.get("data")
                    if isinstance(safe_result.get("data"), Mapping)
                    else {}
                )
                meta: dict[str, Any] = {"interrupt_required": True}
                card = (
                    data.get("clarification_card")
                    if isinstance(data, Mapping)
                    else None
                )
                if card:
                    meta["clarification_card"] = card
                span.set_meta(meta)
            summary_key, summary_params = tool_close_keys(name, result)
            span.close(
                status="completed" if result["ok"] else "failed",
                summary_key=summary_key,
                summary_params=summary_params,
                tool={"call_id": call_id, "name": name, "args": safe_args},
            )
            _record_artifact(
                name=name,
                result=result,
                args=args if isinstance(args, Mapping) else {},
                call_id=call_id,
                record_id=record_id,
                run_id=run_id,
                sink=sink,
                parent_id=span.id,
            )

        tool_messages.append(
            ToolMessage(
                content=model_content,
                tool_call_id=call_id,
                name=name or None,
                artifact=safe_result,
                status="success" if result["ok"] else "error",
            )
        )
        if result["ok"]:
            tool_steps.append(
                {
                    "tool": name,
                    "name": name,
                    "result": safe_result,
                    "ok": True,
                    "signals": signals.model_dump(),
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
                    "signals": signals.model_dump(),
                }
            )
            signature = tool_call_signature(
                name, args if isinstance(args, Mapping) else {}
            )
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

    snap = peek_runtime(run_id) if run_id else None
    probe_sql_calls = int(
        (snap or {}).get("probe_sql_calls")
        if snap and snap.get("probe_sql_calls") is not None
        else (state.get("probe_sql_calls") or 0)
    )
    outgoing = [*messages, *tool_messages]
    knowledge_used = any(
        getattr(item, "name", "") in KNOWLEDGE_TOOLS and not _tool_message_skipped(item)
        for item in tool_messages
    )
    plane = merge_published(load_plane(state).to_dump(), *plane_dumps)
    if knowledge_used:
        plane.knowledge_rounds = int(plane.knowledge_rounds or 0) + 1
    if plane_dumps or knowledge_used:
        publish_plane(plane)

    return {
        **state,
        "messages": serialize_messages(outgoing),
        "tool_steps": tool_steps,
        "last_tool_failure_signature": previous_failure,
        "consecutive_tool_failures": consecutive_failures,
        "tool_stop_reason": stop_reason,
        "knowledge_plane": plane.to_dump(),
        "probe_sql_calls": probe_sql_calls,
        "turn_delivery": delivery.model_dump(),
    }
