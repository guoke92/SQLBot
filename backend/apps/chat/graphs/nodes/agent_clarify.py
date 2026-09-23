"""Clarification interrupt node for Unified Agent."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from langchain_core.messages import HumanMessage
from langgraph.types import interrupt

from apps.chat.agent_knowledge import AgentKnowledgePlane
from apps.chat.caliber_surface import render_caliber_lines
from apps.conversation.messages import deserialize_messages, serialize_messages
from apps.conversation.process_timeline import ensure_clarification_span
from apps.conversation.run_service import create_interrupt
from apps.conversation.session import session_scope
from apps.conversation.sink import StreamSink


def await_agent_clarification_node(state: Mapping[str, Any]) -> dict[str, Any]:
    """Durably interrupt the graph run, publish ClarificationCard, and handle resume."""
    run_id = str(state["run_id"])
    record_id = state.get("record_id")
    card_payload: dict[str, Any] = {}

    for step in reversed(state.get("tool_steps") or []):
        if isinstance(step, Mapping):
            data = step.get("result", {}).get("data") or {}
            if isinstance(data, Mapping) and data.get("clarification_card"):
                card_payload = data["clarification_card"]
                break

    # Fallback to inspecting messages if tool_steps didn't retain card
    if not card_payload:
        for m in reversed(list(state.get("messages") or [])):
            if isinstance(m, Mapping) and m.get("type") == "tool":
                try:
                    c = json.loads(m.get("content", "{}"))
                    if isinstance(c, dict) and c.get("data", {}).get(
                        "clarification_card"
                    ):
                        card_payload = c["data"]["clarification_card"]
                        break
                except Exception:
                    pass

    with session_scope() as session:
        pending = create_interrupt(session, run_id=run_id, payload=card_payload)

    public = {
        "interrupt_id": pending.interrupt_id,
        "version": pending.version,
        **card_payload,
    }
    sink = StreamSink.from_state(state)
    # One interrupt_id ↔ one process span for the whole pause (open → resume).
    clarify_span = ensure_clarification_span(
        record_id=int(record_id) if record_id is not None else None,
        run_id=run_id,
        interrupt_id=str(pending.interrupt_id),
        version=int(pending.version),
        clarification_card=card_payload,
        sink=sink,
        ai_modal_id=state.get("ai_modal_id"),
        ai_modal_name=state.get("ai_modal_name"),
    )

    if pending.status == "open":
        sink.awaiting_input(public)

    # Durable interrupt: returns answers upon resume
    answers = interrupt(public)
    if clarify_span is not None:
        clarify_span.set_output(
            {"answers": answers, "interrupt_id": pending.interrupt_id}
        )
        clarify_span.close(
            status="completed",
            summary_key="chat.summary.clarification_confirmed",
        )

    # Build question & option lookup map from card_payload
    # {question_id: {"question": "...", "options": {opt_id: opt_dict}}}
    questions_map: dict[str, dict[str, Any]] = {}
    for q in card_payload.get("questions") or []:
        if isinstance(q, dict):
            qid = str(q.get("question_id") or q.get("field") or "")
            opts_by_id = {}
            for opt in q.get("options") or []:
                if isinstance(opt, dict):
                    opt_id = str(opt.get("option_id") or opt.get("id") or "")
                    opts_by_id[opt_id] = opt
            questions_map[qid] = {
                "question": q.get("question") or q.get("prompt") or "",
                "options": opts_by_id,
            }

    # 1. Update memory slots with confirmed calibers; the resume message reuses
    #    the single caliber renderer (render_caliber_lines) instead of ad-hoc text.
    raw_slots = dict(state.get("memory_slots") or {})
    confirmed = dict(raw_slots.get("confirmed_calibers") or {})
    newly_confirmed: list[dict[str, Any]] = []

    if isinstance(answers, list):
        for ans in answers:
            if not isinstance(ans, dict):
                continue
            qid = str(ans.get("question_id") or ans.get("field") or "")
            opt_id = str(
                ans.get("option_id") or ans.get("value") or ans.get("text") or ""
            )

            q_info = questions_map.get(qid) or {}
            opt_obj = q_info.get("options", {}).get(opt_id) if q_info else None
            q_text = str(q_info.get("question") or "").strip()

            if opt_obj:
                label = str(opt_obj.get("label") or opt_id).strip()
                meaning = str(
                    opt_obj.get("meaning") or opt_obj.get("description") or label
                ).strip()
                fields = opt_obj.get("fields") or []
                confirmed[qid] = {
                    "question": q_text,
                    "label": label,
                    "meaning": meaning,
                    "fields": fields,
                    "option_id": opt_id,
                }
            else:
                val = opt_id or str(ans)
                confirmed[qid] = {
                    "question": q_text or qid,
                    "label": val,
                    "meaning": val,
                    "option_id": opt_id,
                }
            newly_confirmed.append(confirmed[qid])

    raw_slots["confirmed_calibers"] = confirmed

    # 2. Inject the user's answers as a structured, Chinese resume directive.
    messages = deserialize_messages(list(state.get("messages") or []))
    lines = render_caliber_lines(newly_confirmed)
    if lines:
        clarify_text = (
            "用户已完成澄清，确认口径如下（括号内为绑定的物理字段）：\n"
            + "\n".join(lines)
            + "\n\n按已确认口径继续：不要再询问已确认的项；"
            "若还有其它未确认的冲突条件，合并到一次澄清；否则直接落口径写 SQL 并执行。"
        )
    elif answers:
        clarify_text = f"用户已确认澄清选项：{answers}。按确认结果继续，不要重复澄清。"
    else:
        clarify_text = "用户已确认澄清选项。按确认结果继续查询。"

    messages.append(HumanMessage(content=clarify_text))

    plane = AgentKnowledgePlane.from_dump(state.get("knowledge_plane"))
    plane.drop_resolved_conflicts(confirmed)
    messages = plane.apply_to_system_message(messages)

    return {
        **state,
        "messages": serialize_messages(messages),
        "memory_slots": raw_slots,
        "knowledge_plane": plane.to_dump(),
        "tool_steps": [],  # reset tool steps to avoid re-triggering clarify
        "tool_rounds": 0,
        "tool_stop_reason": "",
    }
