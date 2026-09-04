"""Unified Tool-Agent node and runtime loop for SQLBot."""

from __future__ import annotations

import time
from collections.abc import Mapping
from typing import Any, Literal

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from apps.chat.memory_slots import MemorySlots
from apps.chat.models.chat_model import ChatFinishStep, OperationEnum
from apps.chat.steps.observability import log_span, sanitize_audit_value
from apps.chat.task.agent_prompt import build_agent_system_prompt
from apps.chat.tools.registry import build_agent_tools
from apps.conversation.messages import (
    deserialize_messages,
    message_content_text,
    serialize_messages,
)
from apps.conversation.outcome import failed_outcome, format_error_message, running_outcome
from apps.conversation.runtime_context import attach_runtime, runtime_value
from apps.conversation.sink import StreamSink
from apps.conversation.tooling import tool_calls_from_message
from apps.conversation.usage import usage_from_response
from apps.datasource.access import resolve_access_scope
from apps.conversation.session import session_scope
from common.utils.utils import SQLBotLogUtil


def prepare_agent_turn_node(state: Mapping[str, Any]) -> dict[str, Any]:
    """Prepare messages, bound tools, memory slots, and runtime context."""
    from apps.chat.graphs.nodes.nlq.state import _llm_service
    from apps.chat.graphs.nodes.nlq.context import prepare_record_node
    
    # 1. Run the base prepare_record_node to initialize chat_record and emit SSE events (type: id, question)
    base_state = prepare_record_node(dict(state))
    if base_state.get("error"):
        return base_state

    llm_service = _llm_service(base_state)
    run_id = str(base_state["run_id"])
    record_id = base_state.get("record_id")
    question_text = str(getattr(llm_service.chat_question, "question", "") or "")

    # 2. Resolve access_scope defensively (ensuring datasource is selected if needed)
    access_scope = None
    try:
        if not getattr(llm_service, "ds", None):
            with session_scope() as session:
                from apps.datasource.crud.datasource import get_ds
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
        SQLBotLogUtil.warning(f"Failed to resolve access_scope in prepare_agent_turn: {exc}")

    # 3. Rehydrate or init memory slots
    raw_slots = base_state.get("memory_slots") or {}
    memory_slots = MemorySlots.model_validate(raw_slots) if raw_slots else MemorySlots()

    referenced = base_state.get("referenced_turns") or []
    if referenced and not memory_slots.active_baseline_sql:
        latest = referenced[-1]
        for ds in latest.get("datasets") or []:
            if ds.get("sql"):
                memory_slots.active_baseline_sql = ds["sql"]
                memory_slots.active_dataset_outline = {
                    "fields": ds.get("fields") or [],
                    "row_count": ds.get("row_count"),
                }
                break

    # 4. Retrieve Wiki knowledge (Single Source of Truth) or Fallback Schema
    from apps.chat.steps.wiki_recall import (
        datasource_databases,
        wiki_backend_active,
        wiki_business_recall,
    )
    from apps.chat.steps.schema import match_table_schema

    ds_id = getattr(getattr(llm_service, "ds", None), "id", None)
    wiki_text = ""
    schema_summary = ""

    if wiki_backend_active(ds_id):
        try:
            from apps.chat.steps.wiki_recall import _store
            from apps.knowledge.wiki.anchors import closure_tables
            from apps.chat.steps.wiki_schema import WikiSchemaRenderer

            databases = datasource_databases(getattr(llm_service, "ds", None))
            wiki_res = wiki_business_recall(question_text, ds_id=ds_id, databases=databases)
            if wiki_res and wiki_res.text:
                wiki_text = wiki_res.text
                store = _store()
                if store is not None and getattr(wiki_res, "page_keys", None):
                    closure, _ = closure_tables(store, wiki_res.page_keys)
                    if closure:
                        renderer = WikiSchemaRenderer.from_store(store)
                        if renderer:
                            raw_schema = renderer.render(list(closure))
                            lines = raw_schema.splitlines()
                            compact_lines = []
                            for line in lines:
                                if line.startswith("## ") or "topk=" in line or any(k in line for k in ["Id", "时间", "状态", "名称", "类型", "方式", "来源", "编码", "金额", "部门", "日期"]):
                                    compact_lines.append(line)
                            header = "\n\n### 【权威表结构与字段定义（已在初始化完整注入，严禁重复检索结构）】：\n"
                            wiki_text += header + "\n".join(compact_lines)
        except Exception as exc:
            SQLBotLogUtil.warning(f"Failed to recall Wiki knowledge in prepare_agent_turn: {exc}")

    # Fallback to physical schema only when Wiki is inactive or returned no knowledge
    if not wiki_text:
        try:
            with session_scope() as session:
                match_table_schema(
                    llm_service,
                    session,
                    access_scope=access_scope,
                    table_limit=4,
                    audit=False,
                )
                schema_summary = str(getattr(llm_service.chat_question, "db_schema", "") or "")
        except Exception as exc:
            SQLBotLogUtil.warning(f"Failed to retrieve fallback schema in prepare_agent_turn: {exc}")

    # 5. Build and bind tools
    tools = build_agent_tools(llm_service, access_scope=access_scope)
    attach_runtime(
        run_id,
        llm=llm_service.llm,
        bound_tools=tools,
        access_scope=access_scope,
        llm_service=llm_service,
    )

    # 6. Assemble initial messages
    system_text = build_agent_system_prompt(
        memory_slots=memory_slots.model_dump(),
        change_baseline=memory_slots.extract_change_baseline(),
        wiki_knowledge=wiki_text,
        schema_summary=schema_summary,
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
    llm = runtime_value(state, "llm")

    finalizing = rounds >= round_limit
    model_messages = messages
    if finalizing:
        model_messages = [
            *messages,
            SystemMessage(
                content=(
                    f"Tool calling budget reached ({round_limit} rounds). "
                    "Do not request further tool calls. Provide a truthful summary of data obtained so far."
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
            graph_node="agent_loop",
            title_key="chat.log.AGENT_STEP",
            brief="finalize" if finalizing else f"round {rounds + 1}",
        ) as span:
            bound = llm if finalizing or not tools else llm.bind_tools(tools)
            
            response: AIMessage = bound.invoke(model_messages)
            calls = tool_calls_from_message(response)
            safe_calls = sanitize_audit_value(calls)
            text = message_content_text(response.content)

            # Stream reasoning content or thought if model supports it
            rc = (
                getattr(response, "additional_kwargs", {}).get("reasoning_content")
                or getattr(response, "reasoning_content", "")
            )
            # If model produced thought in content prior to tool call
            thought_text = rc or (text if calls else "")
            if rc:
                span["reasoning_content"] = rc
                sink.token(content="", reasoning_content=rc, event_type="analysis-reasoning")
            elif thought_text and calls:
                sink.event({"type": "agent-thought", "content": thought_text})

            span["payload"] = {
                "round": rounds + 1,
                "tool_calls": safe_calls,
                "content": "" if calls else text[:500],
            }
            span["token_usage"] = usage_from_response(response)
            span.set_model_context([*model_messages, response])
    except Exception as exc:
        SQLBotLogUtil.error(f"agent loop error: {exc}")
        return {**state, "error": format_error_message(exc), "outcome": failed_outcome(exc)}

    updated_messages = [*messages, response]
    tool_name_map = {
        "execute_sql_sandbox": "执行查询 (execute_sql_sandbox)",
        "patch_and_compile_sql": "增量补丁 (patch_and_compile_sql)",
        "compare_results": "数据对比 (compare_results)",
        "search_schema": "结构检索 (search_schema)",
        "search_wiki": "查阅知识 (search_wiki)",
        "request_clarification": "请求澄清 (request_clarification)",
    }
    if calls:
        for c in calls:
            c_name = c['name']
            c_label = tool_name_map.get(c_name, f"工具调用 ({c_name})")
            sink.event({
                "type": "agent-tool-call",
                "tool": c_name,
                "displayName": c_label,
                "args": c.get('args', {}),
            })
        # Advance budget by count of tool calls (so parallel calls consume budget proportionally)
        advanced_rounds = rounds + max(1, len(calls))
        return {
            **state,
            "messages": serialize_messages(updated_messages),
            "tool_rounds": advanced_rounds,
        }

    # Final answer text reached
    sink.event({"type": "analysis", "content": text})
    return {
        **state,
        "messages": serialize_messages(updated_messages),
        "final_text": text,
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
