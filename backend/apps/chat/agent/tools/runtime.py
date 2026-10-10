"""Chat-agent tool dispatch: parallel-safe knowledge tools, serial exclusive tools."""

from __future__ import annotations

import contextvars
from collections.abc import Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from langchain_core.messages import ToolMessage

from apps.chat.agent.audit import tool_close_keys
from apps.chat.agent.budget import budget_from_state, calls_count_as_execution
from apps.chat.agent.close import apply_outcome_to_workspace
from apps.chat.agent.knowledge import (
    cache_from_state,
    load_plane,
    merge_published,
    publish_plane,
    take_working,
)
from apps.chat.agent.mode import resolve_agent_mode
from apps.chat.agent.tools.render import render_tool_message
from apps.chat.agent.workspace import SqlWorkspace
from apps.chat.agent_config.defaults import DEFAULT_PARALLEL_SAFE
from apps.chat.agent_knowledge import KNOWLEDGE_TOOLS
from apps.chat.steps.observability import sanitize_audit_value
from apps.chat.tools.analyze_result import ANALYZE_SQL_TOOLS
from apps.chat.tools.contract import (
    Signals,
    ToolOutcome,
    outcome_payload,
    parse_tool_outcome,
    skipped_outcome,
)
from apps.conversation.messages import deserialize_messages, serialize_messages
from apps.conversation.process_timeline import (
    PREVIEW_ROW_LIMIT,
    attach_process_span,
    attach_running_tool_span,
    complete_page_rows,
    open_process_span,
    preview_rows,
)
from apps.conversation.runtime_context import (
    attach_runtime,
    runtime_value,
    tool_call_scope,
)
from apps.conversation.sink import StreamSink
from apps.conversation.tooling import (
    _tool_call_signature as tool_call_signature,
)
from apps.conversation.tooling import (
    _truncate_for_log as truncate_for_log,
)
from apps.conversation.tooling import (
    last_tool_call_message,
    tool_calls_from_message,
)

_KEEP_TOOL_RESULTS = 8


def _invoke_one(
    tools: Mapping[str, Any],
    call: Mapping[str, Any],
    *,
    skip_knowledge: bool = False,
    skip_probe: bool = False,
    skip_clarify: bool = False,
    defer_clarify: str = "",
) -> dict[str, Any]:
    name = str(call.get("name") or "")
    args = call.get("args") or {}
    call_id = str(call.get("id") or "")
    if skip_knowledge and name in KNOWLEDGE_TOOLS:
        return skipped_outcome(
            "knowledge budget exhausted",
            reason="knowledge_budget",
            name=name,
        )
    if skip_probe and name == "execute_sql_sandbox":
        purpose = str((args if isinstance(args, Mapping) else {}).get("purpose") or "")
        if purpose == "probe":
            return skipped_outcome(
                "probe budget exhausted; deliver or clarify instead",
                reason="probe_budget",
                name=name,
            )
    if skip_clarify and name == "request_clarification":
        return skipped_outcome(
            "clarification budget exhausted",
            reason="clarify_budget",
            name=name,
        )
    if defer_clarify and name == "request_clarification":
        return skipped_outcome(
            defer_clarify,
            reason="explore_first",
            name=name,
        )
    tool = tools.get(name)
    try:
        if tool is None:
            from apps.chat.tools.contract import failure_outcome

            return failure_outcome(f"Unknown tool: {name}", name=name, retryable=False)
        with tool_call_scope(call_id):
            raw = tool.invoke(args)
            return parse_tool_outcome(raw, name=name).as_dict()
    except Exception as exc:
        from apps.chat.tools.contract import failure_outcome

        return failure_outcome(f"{name} failed: {exc}", name=name, retryable=True)


def _dispatch_results(
    tools: Mapping[str, Any],
    calls: Sequence[Mapping[str, Any]],
    *,
    skip_knowledge: bool = False,
    skip_probe: bool = False,
    skip_clarify: bool = False,
    defer_clarify: str = "",
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not calls:
        return [], []
    exclusive = any(
        str(call.get("name") or "") not in DEFAULT_PARALLEL_SAFE for call in calls
    )
    kwargs = {
        "skip_knowledge": skip_knowledge,
        "skip_probe": skip_probe,
        "skip_clarify": skip_clarify,
        "defer_clarify": defer_clarify,
    }
    if exclusive or len(calls) == 1:
        results = [_invoke_one(tools, call, **kwargs) for call in calls]
        dump = take_working()
        return results, [dump] if dump else []

    parent_snapshots = [contextvars.copy_context() for _ in calls]
    results: list[dict[str, Any] | None] = [None] * len(calls)
    dumps: list[dict[str, Any] | None] = [None] * len(calls)

    def _run(index: int) -> tuple[int, dict[str, Any], dict[str, Any] | None]:
        def _inner() -> tuple[dict[str, Any], dict[str, Any] | None]:
            result = _invoke_one(tools, calls[index], **kwargs)
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
    from apps.chat.tools.contract import failure_outcome

    return (
        [
            item if item is not None else failure_outcome("empty", name="unknown")
            for item in results
        ],
        [item for item in dumps if item],
    )


def _artifact_preview_rows(data: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Show every row of a small complete page; keep the 3-row card sample otherwise."""
    full = complete_page_rows(data)
    if full is not None and not data.get("truncated"):
        return full
    return preview_rows(
        data.get("preview_rows") or data.get("sample_rows") or [],
        limit=PREVIEW_ROW_LIMIT,
    )


def _record_artifact(
    *,
    outcome: ToolOutcome,
    args: Mapping[str, Any],
    record_id: Any,
    run_id: str | None,
    sink: StreamSink,
    parent_id: int | None,
) -> None:
    if not outcome.ok:
        return
    data = outcome_payload(outcome.as_dict())
    if outcome.signals.dataset_id or data.get("dataset_id"):
        art = open_process_span(
            kind="artifact",
            record_id=record_id,
            sink=sink,
            run_id=run_id,
            parent_id=parent_id,
            graph_node="execute_tools",
            title_key="chat.timeline.artifact",
            artifact={
                "dataset_id": outcome.signals.dataset_id or data.get("dataset_id"),
                "sql": data.get("sql")
                or (args.get("sql") if isinstance(args, Mapping) else ""),
                "fields": list(data.get("fields") or []),
                "row_count": data.get("row_count") or data.get("total_rows"),
                "truncated": bool(data.get("truncated")),
                "limit": data.get("limit"),
                "preview_rows": _artifact_preview_rows(data),
                "rev": outcome.signals.sql_rev,
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


def _clear_old_tool_results(
    messages: Sequence[Any], *, turn_start: int | None
) -> list[Any]:
    """Keep recent tool observations and all failures; pointer-replace the rest."""
    start = int(turn_start or 0)
    keepable: list[int] = []
    for index, message in enumerate(messages):
        if index < start or not isinstance(message, ToolMessage):
            continue
        failed = str(getattr(message, "status", "") or "") == "error"
        if failed:
            continue
        keepable.append(index)
    drop = (
        set(keepable[:-_KEEP_TOOL_RESULTS])
        if len(keepable) > _KEEP_TOOL_RESULTS
        else set()
    )
    if not drop:
        return list(messages)
    out: list[Any] = []
    for index, message in enumerate(messages):
        if index not in drop:
            out.append(message)
            continue
        name = str(getattr(message, "name", "") or "tool")
        out.append(
            ToolMessage(
                content=f"[已清除 · {name} · 见 working_set / sql_workspace]",
                tool_call_id=str(getattr(message, "tool_call_id", "") or ""),
                name=name or None,
                artifact=getattr(message, "artifact", None),
                status=getattr(message, "status", None) or "success",
            )
        )
    return out


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
    workspace = SqlWorkspace.from_state(state)
    batch = Signals()

    calls = tool_calls_from_message(ai_message)
    try:
        from apps.chat.agent_config import load_agent_config_for_run

        budget = budget_from_state(state, config=load_agent_config_for_run())
    except Exception:
        budget = budget_from_state(state)

    if budget.tool_calls.exhausted:
        stop_reason = "tool call budget exhausted"
        budget.stop_reason = stop_reason
        return {
            **state,
            "tool_stop_reason": stop_reason,
            "loop_budget": budget.model_dump(mode="json"),
            "batch_signals": Signals().model_dump(mode="json"),
        }

    results, plane_dumps = _dispatch_results(
        tools,
        calls,
        skip_knowledge=budget.knowledge_exhausted,
        skip_probe=budget.probe_exhausted,
        skip_clarify=budget.clarify_exhausted,
        defer_clarify=resolve_agent_mode(state).defer_clarification(state),
    )

    ds = None
    try:
        service = runtime_value(state, "llm_service")
        ds = getattr(service, "ds", None) or getattr(service, "datasource", None)
    except Exception:
        ds = None
    ds_id = getattr(ds, "id", None)
    dialect = getattr(ds, "type", None) if ds is not None else None

    for call, raw in zip(calls, results, strict=True):
        call_id = str(call.get("id") or "")
        name = str(call.get("name") or "")
        args = call.get("args") or {}
        safe_args = sanitize_audit_value(args)
        outcome = parse_tool_outcome(raw, name=name)
        workspace, outcome = apply_outcome_to_workspace(
            workspace,
            name=name,
            args=args if isinstance(args, Mapping) else {},
            outcome=outcome,
            ds_id=int(ds_id) if ds_id is not None else None,
            dialect=str(dialect) if dialect else None,
        )
        if outcome.signals.interrupt:
            batch = batch.model_copy(update={"interrupt": True})
        if outcome.signals.terminal:
            batch = batch.model_copy(update={"terminal": True})
        if (
            outcome.signals.purpose == "probe"
            and not outcome.signals.skipped
            and name not in ANALYZE_SQL_TOOLS
        ):
            budget.probe_calls.used += 1
        budget.tool_calls.used += 1

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

        dumped = outcome.as_dict()
        safe_result = sanitize_audit_value(dumped)
        model_content = render_tool_message(name, safe_result)
        if run_id:
            attach_runtime(
                run_id,
                sql_workspace=workspace.model_dump(mode="json"),
                loop_budget=budget.model_dump(mode="json"),
            )
        if span is not None:
            span.set_output(truncate_for_log(safe_result))
            if outcome.signals.interrupt:
                payload = outcome_payload(dumped)
                meta: dict[str, Any] = {"interrupt_required": True}
                card = payload.get("clarification_card")
                if card:
                    meta["clarification_card"] = card
                span.set_meta(meta)
            summary_key, summary_params = tool_close_keys(name, dumped)
            span.close(
                status="completed" if outcome.ok else "failed",
                summary_key=summary_key,
                summary_params=summary_params,
                tool={"call_id": call_id, "name": name, "args": safe_args},
            )
            _record_artifact(
                outcome=outcome,
                args=args if isinstance(args, Mapping) else {},
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
                status="success" if outcome.ok else "error",
            )
        )
        step: dict[str, Any] = {
            "tool": name,
            "name": name,
            "ok": outcome.ok,
            "outcome": dumped,
            "signals": outcome.signals.model_dump(mode="json"),
        }
        if outcome.ok:
            step["result"] = dumped
            tool_steps.append(step)
            previous_failure = ""
            consecutive_failures = 0
        else:
            step["error"] = outcome.error
            step["failure"] = outcome.failure
            tool_steps.append(step)
            signature = tool_call_signature(
                name, args if isinstance(args, Mapping) else {}
            )
            if signature == previous_failure:
                consecutive_failures += 1
            else:
                previous_failure = signature
                consecutive_failures = 1
            failure = outcome.failure or {}
            if not bool(failure.get("retryable")):
                stop_reason = (
                    f"{name} failed with a non-retryable "
                    f"{failure.get('kind') or 'execution'} error"
                )
            elif consecutive_failures >= 2:
                stop_reason = f"{name} repeated the same failed call"

    outgoing = [*messages, *tool_messages]
    outgoing = _clear_old_tool_results(
        outgoing, turn_start=state.get("turn_message_start")
    )
    knowledge_used = any(
        str(call.get("name") or "") in KNOWLEDGE_TOOLS
        and not parse_tool_outcome(
            raw, name=str(call.get("name") or "")
        ).signals.skipped
        for call, raw in zip(calls, results, strict=True)
    )
    plane = merge_published(load_plane(state).to_dump(), *plane_dumps)
    if knowledge_used:
        plane.knowledge_rounds = int(plane.knowledge_rounds or 0) + 1
        budget.knowledge_rounds.used = plane.knowledge_rounds
    if calls_count_as_execution(calls):
        budget.exec_rounds.used += 1
    if plane_dumps or knowledge_used:
        publish_plane(plane)
    if stop_reason:
        budget.stop_reason = stop_reason

    return {
        **state,
        "messages": serialize_messages(outgoing),
        "tool_steps": tool_steps,
        "last_tool_failure_signature": previous_failure,
        "consecutive_tool_failures": consecutive_failures,
        "tool_stop_reason": stop_reason,
        "knowledge_plane": plane.to_dump(),
        "sql_workspace": workspace.model_dump(mode="json"),
        "loop_budget": budget.model_dump(mode="json"),
        "batch_signals": batch.model_dump(mode="json"),
        "tool_rounds": budget.exec_rounds.used,
    }
