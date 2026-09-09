"""Unified Tool-Agent node and runtime loop for SQLBot."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Literal

import orjson
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from sqlalchemy import select

from apps.chat.agent_copy import (
    compact_agent_final_text,
    truncated_display_note,
    truncation_from_tool_steps,
)
from apps.chat.agent_knowledge import AgentKnowledgePlane
from apps.chat.memory_slots import (
    MemorySlots,
    answer_has_executable_sql,
    hydrate_memory_slots_from_referenced_turns,
)
from apps.chat.steps.stream import consume_llm
from apps.chat.task.agent_prompt import build_agent_system_prompt
from apps.chat.tools.metadata import get_tool_title_key
from apps.chat.tools.registry import build_agent_tools
from apps.chat.turn_contracts import TurnRoute
from apps.conversation.messages import (
    deserialize_messages,
    serialize_messages,
)
from apps.conversation.outcome import (
    failed_outcome,
    format_error_message,
    running_outcome,
)
from apps.conversation.process_timeline import open_process_span
from apps.conversation.runtime_context import attach_runtime, runtime_value
from apps.conversation.session import session_scope
from apps.conversation.sink import StreamSink
from apps.conversation.tooling import (
    attach_tool_calls,
    looks_like_tool_markup,
    resolve_message_tool_calls,
    tool_calls_from_message,
)
from apps.datasource.access import resolve_access_scope
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


def _agent_has_sql_result(state: Mapping[str, Any], messages: Sequence[Any]) -> bool:
    """True only when a required=true SQL dataset succeeded. Probes do not count."""
    for step in state.get("tool_steps") or []:
        if not isinstance(step, Mapping) or not step.get("ok"):
            continue
        data = (step.get("result") or {}).get("data") or {}
        if _required_sql_payload(data):
            return True
    for message in messages:
        if str(getattr(message, "name", "") or "") != "execute_sql_sandbox":
            continue
        raw = getattr(message, "content", "") or ""
        payload: Any = raw
        if isinstance(raw, str):
            try:
                payload = orjson.loads(raw)
            except Exception:
                payload = {}
        if not isinstance(payload, Mapping) or payload.get("ok") is False:
            continue
        data = payload.get("data") if isinstance(payload.get("data"), Mapping) else {}
        if _required_sql_payload(data):
            return True
    return False


def _clarify_only_tool_calls(calls: Sequence[Mapping[str, Any]]) -> bool:
    return bool(calls) and all(
        str(item.get("name") or "") == "request_clarification" for item in calls
    )


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


def resolve_continue_reference_ids(
    *,
    chat_id: int | None,
    user_id: int | None,
    exclude_record_id: int | None = None,
    explicit_ids: Sequence[int] | None = None,
) -> list[int]:
    """Prefer explicit refs; otherwise attach the latest succeeded query in-chat."""
    explicit = [int(item) for item in (explicit_ids or []) if int(item) > 0]
    if explicit:
        return explicit[:3]
    if chat_id is None or user_id is None:
        return []
    from apps.chat.models.chat_model import ChatRecord

    with session_scope() as session:
        rows = (
            session.exec(
                select(ChatRecord)
                .where(
                    ChatRecord.chat_id == int(chat_id),
                    ChatRecord.create_by == int(user_id),
                    ChatRecord.question.is_not(None),
                )
                .order_by(ChatRecord.id.desc())
                .limit(20)
            )
            .scalars()
            .all()
        )
        for row in rows:
            if exclude_record_id is not None and int(row.id) == int(exclude_record_id):
                continue
            answer = row.answer if isinstance(row.answer, dict) else None
            if answer_has_executable_sql(answer):
                return [int(row.id)]
    return []


def _ensure_agent_turn_route(
    state: Mapping[str, Any],
    *,
    reference_record_ids: Sequence[int],
    task_kind: str = "query",
) -> dict[str, Any]:
    """Build a valid TurnRoute for assemble_turn_context (refs alone are not enough)."""
    refs = tuple(int(item) for item in reference_record_ids[:3] if int(item) > 0)
    existing = (
        state.get("turn_route") if isinstance(state.get("turn_route"), dict) else {}
    )
    kind = str(
        existing.get("task_kind") or state.get("route_hint") or task_kind or "query"
    )
    if kind not in {"query", "analysis", "prediction", "unsupported"}:
        kind = "query"
    if kind == "analysis" and not refs:
        kind = "query"
    relation: Literal["independent", "continue", "revise"] = (
        "continue" if refs else "independent"
    )
    return TurnRoute(
        task_kind=kind,  # type: ignore[arg-type]
        relation=relation,
        reference_record_ids=refs,
        source="deterministic",
        confidence=0.9 if refs else 1.0,
    ).model_dump(mode="json")


def prepare_agent_turn_node(state: Mapping[str, Any]) -> dict[str, Any]:
    """Prepare messages, bound tools, memory slots, and runtime context."""
    from apps.chat.graphs.nodes.nlq.context import (
        assemble_turn_context_node,
        prepare_record_node,
    )
    from apps.chat.graphs.nodes.nlq.state import _llm_service
    from apps.chat.models.chat_model import ChatRecord

    base_state = prepare_record_node(dict(state))
    if base_state.get("error"):
        return base_state

    llm_service = _llm_service(base_state)
    run_id = str(base_state["run_id"])
    record_id = base_state.get("record_id")
    question_text = str(getattr(llm_service.chat_question, "question", "") or "")
    chat_id = base_state.get("chat_id") or getattr(
        getattr(llm_service, "record", None), "chat_id", None
    )
    user_id = getattr(getattr(llm_service, "current_user", None), "id", None)

    ref_ids = resolve_continue_reference_ids(
        chat_id=int(chat_id) if chat_id is not None else None,
        user_id=int(user_id) if user_id is not None else None,
        exclude_record_id=int(record_id) if record_id is not None else None,
        explicit_ids=base_state.get("reference_record_ids") or [],
    )
    turn_route = _ensure_agent_turn_route(base_state, reference_record_ids=ref_ids)
    base_state["reference_record_ids"] = list(
        turn_route.get("reference_record_ids") or []
    )
    base_state["turn_route"] = turn_route

    if base_state["reference_record_ids"]:
        ctx_state = assemble_turn_context_node(base_state)
        if not ctx_state.get("error"):
            base_state.update(ctx_state)
            # Persist continue linkage for audit / next turns.
            try:
                with session_scope() as session:
                    record = (
                        session.get(ChatRecord, int(record_id))
                        if record_id is not None
                        else None
                    )
                    if record is not None:
                        record.relation = str(turn_route.get("relation") or "continue")
                        record.reference_record_ids = list(
                            base_state["reference_record_ids"]
                        )
                        session.add(record)
                        session.commit()
            except Exception as exc:
                SQLBotLogUtil.warning(
                    f"Failed to persist continue refs on record {record_id}: {exc}"
                )
        else:
            SQLBotLogUtil.warning(
                f"assemble_turn_context failed for agent turn {record_id}: "
                f"{ctx_state.get('error')}"
            )

    access_scope = None
    try:
        if not getattr(llm_service, "ds", None):
            with session_scope() as session:
                from apps.datasource.models.datasource import CoreDatasource

                chat_obj = session.get(ChatRecord, record_id) if record_id else None
                ds_id = getattr(chat_obj, "datasource", None) if chat_obj else None
                if not ds_id and getattr(llm_service, "record", None):
                    ds_id = getattr(llm_service.record, "datasource", None)
                if ds_id:
                    ds = session.get(CoreDatasource, ds_id)
                    if ds:
                        llm_service.ds = ds

        if getattr(llm_service, "ds", None):
            with session_scope() as session:
                access_scope = resolve_access_scope(
                    session,
                    current_user=llm_service.current_user,
                    ds=llm_service.ds,
                )
    except Exception as exc:
        SQLBotLogUtil.warning(
            f"Failed to resolve access_scope in prepare_agent_turn: {exc}"
        )

    raw_slots = base_state.get("memory_slots") or {}
    memory_slots = MemorySlots.model_validate(raw_slots) if raw_slots else MemorySlots()
    referenced = list(base_state.get("referenced_turns") or [])
    # Prefer full answer calibers from the referenced ChatRecord when outline lacks them.
    if referenced:
        try:
            with session_scope() as session:
                latest_id = referenced[-1].get("record_id")
                prior = session.get(ChatRecord, int(latest_id)) if latest_id else None
                answer = (
                    prior.answer
                    if prior is not None and isinstance(prior.answer, dict)
                    else {}
                )
                patch: dict[str, Any] = {}
                if answer.get("assumptions") and "assumptions" not in referenced[-1]:
                    patch["assumptions"] = list(answer.get("assumptions") or [])
                if (
                    answer.get("confirmed_calibers")
                    and "confirmed_calibers" not in referenced[-1]
                ):
                    patch["confirmed_calibers"] = list(
                        answer.get("confirmed_calibers") or []
                    )
                if patch:
                    referenced[-1] = {**referenced[-1], **patch}
        except Exception as exc:
            SQLBotLogUtil.warning(f"Failed to load prior calibers: {exc}")
    memory_slots = hydrate_memory_slots_from_referenced_turns(memory_slots, referenced)

    from apps.chat.steps.wiki_recall import retrieve_wiki_context, wiki_span_fields

    wiki_ctx: dict[str, Any] = {}
    plane = AgentKnowledgePlane.from_dump(base_state.get("knowledge_plane"))
    sink = StreamSink.from_state(base_state)
    wiki_span = open_process_span(
        kind="tool",
        record_id=record_id,
        sink=sink,
        run_id=run_id,
        graph_node="prepare_agent_turn",
        title_key="chat.timeline.tool.prepare_wiki",
        tool={
            "call_id": f"prepare-wiki-{record_id or run_id}",
            "name": "prepare_wiki",
            "args": {"query": question_text[:240]},
        },
        summary_key="chat.audit.processing",
        local_operation=True,
    )
    try:
        wiki_ctx = retrieve_wiki_context(
            llm_service,
            question_text,
            access_scope=access_scope,
            top_k=5,
        )
        plane.merge_recall(wiki_ctx)
        recalled_schema = "\n".join(
            plane.schema_by_table[name]
            for name in plane.tables
            if plane.schema_by_table.get(name)
        )
        if recalled_schema:
            llm_service.chat_question.db_schema = recalled_schema
        page_keys = list(plane.page_keys)
        hit_count = int(wiki_ctx.get("hit_count") or len(page_keys) or 0)
        if wiki_span is not None:
            wiki_span.set_input(
                {
                    "query": question_text,
                    "top_k": 5,
                    "backend": wiki_ctx.get("backend"),
                    "store_source": wiki_ctx.get("store_source"),
                    "corpus_id": wiki_ctx.get("corpus_id"),
                }
            )
            wiki_span.set_output(wiki_span_fields(wiki_ctx))
            wiki_span.close(
                status="completed",
                summary_key="chat.summary.wiki_prepared",
                summary_params={"count": hit_count},
            )
    except Exception as exc:
        SQLBotLogUtil.warning(
            f"Failed to retrieve context in prepare_agent_turn: {exc}"
        )
        if wiki_span is not None:
            wiki_span.close(status="failed", summary_key="chat.audit.step_failed")

    tools = build_agent_tools(llm_service, access_scope=access_scope)
    attach_runtime(
        run_id,
        llm=llm_service.llm,
        bound_tools=tools,
        access_scope=access_scope,
        llm_service=llm_service,
        knowledge_plane=plane.to_dump(),
        probe_sql_calls=0,
    )

    system_text = build_agent_system_prompt(
        memory_slots=memory_slots.model_dump(),
        change_baseline=memory_slots.extract_change_baseline(),
        knowledge_plane=plane,
    )
    initial_messages = [
        SystemMessage(content=system_text),
        HumanMessage(content=question_text),
    ]

    return {
        **base_state,
        "messages": serialize_messages(initial_messages),
        "tool_rounds": 0,
        "tool_round_limit": 5,
        "knowledge_plane": plane.to_dump(),
        "probe_sql_calls": 0,
        "memory_slots": memory_slots.model_dump(),
        "outcome": running_outcome(),
    }


def agent_loop_node(state: Mapping[str, Any]) -> dict[str, Any]:
    """Autonomous ReAct loop node: streams thought, calls tools, or finalizes."""
    sink = StreamSink.from_state(state)
    messages = deserialize_messages(list(state.get("messages") or []))
    tools = list(runtime_value(state, "bound_tools") or [])
    rounds = int(state.get("tool_rounds") or 0)
    round_limit = int(state.get("tool_round_limit") or 5)
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
        reason = stop_reason or (f"Tool calling budget reached ({round_limit} rounds)")
        model_messages = [
            *messages,
            SystemMessage(
                content=(
                    f"Tool execution is now closed because {reason}. "
                    "Do not request further tool calls. If no query result is available, "
                    "do not propose another search, catalog SQL, or guessed columns."
                )
            ),
        ]

    thought_span = None
    response: AIMessage | None = None
    calls: list[dict[str, Any]] = []
    text = ""
    usage: Mapping[str, Any] = {}
    recovered_markup = False

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

        def _on_chunk(chunk: Mapping[str, Any]) -> None:
            reasoning = str(chunk.get("reasoning_content") or "")
            content = str(chunk.get("content") or "")
            if reasoning:
                span = _ensure_thought_span()
                if span is not None:
                    span.delta(
                        thought_content=reasoning,
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
        recovered_markup = bool(calls) and not native_calls
        if finalizing:
            if recovered_markup or looks_like_tool_markup(call.content):
                text = text.strip() or _incomplete_query_message(state)
            calls = []
        elif recovered_markup and response is not None:
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
            if thought_body:
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
    except Exception as exc:
        SQLBotLogUtil.error(f"agent loop error: {exc}")
        if thought_span is not None:
            thought_span.close(status="failed", summary_key="chat.audit.step_failed")
        return {
            **state,
            "error": format_error_message(exc),
            "outcome": failed_outcome(exc),
        }

    if response is None:
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
        advanced_rounds = rounds if _clarify_only_tool_calls(calls) else rounds + 1
        return {
            **state,
            "messages": serialize_messages(updated_messages),
            "tool_rounds": advanced_rounds,
            "open_tool_spans": open_tool_spans,
        }

    if looks_like_tool_markup(text) or (
        recovered_markup and not str(text or "").strip()
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


def route_after_agent_loop(
    state: Mapping[str, Any],
) -> Literal["execute_tools", "finalize_turn", "fail"]:
    if state.get("error"):
        return "fail"
    messages = deserialize_messages(list(state.get("messages") or []))
    if messages:
        last = messages[-1]
        if isinstance(last, AIMessage) and getattr(last, "tool_calls", None):
            return "execute_tools"
    return "finalize_turn"


def route_after_tools_execution(
    state: Mapping[str, Any],
) -> Literal["agent_loop", "await_clarification", "fail"]:
    if state.get("error"):
        return "fail"
    for step in state.get("tool_steps") or []:
        if isinstance(step, Mapping):
            data = step.get("result", {}).get("data") or {}
            if isinstance(data, Mapping) and data.get("interrupt_required"):
                return "await_clarification"
    return "agent_loop"
