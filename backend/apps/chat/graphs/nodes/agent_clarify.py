"""Clarification interrupt node for Unified Agent."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from langchain_core.messages import HumanMessage
from langgraph.types import interrupt

from apps.conversation.messages import deserialize_messages, serialize_messages
from apps.conversation.run_service import create_interrupt
from apps.conversation.session import session_scope
from apps.conversation.sink import StreamSink


def await_agent_clarification_node(state: Mapping[str, Any]) -> dict[str, Any]:
    """Durably interrupt the graph run, publish ClarificationCard, and handle resume."""
    run_id = str(state["run_id"])
    card_payload: dict[str, Any] = {}

    for step in reversed(state.get("tool_steps") or []):
        if isinstance(step, Mapping):
            data = step.get("result", {}).get("data") or {}
            if isinstance(data, Mapping) and data.get("clarification_card"):
                card_payload = data["clarification_card"]
                break

    # Fallback to inspecting messages if tool_steps didn't retain card
    if not card_payload:
        from apps.chat.semantic_planning import ClarificationCard, coerce_clarification_questions
        for m in reversed(list(state.get("messages") or [])):
            if isinstance(m, Mapping) and m.get("type") == "tool":
                import json
                try:
                    c = json.loads(m.get("content", "{}"))
                    if isinstance(c, dict) and c.get("data", {}).get("clarification_card"):
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
    if pending.status == "open":
        StreamSink.from_state(state).awaiting_input(public)

    # Durable interrupt: returns answers upon resume
    answers = interrupt(public)

    # When resumed from interrupt, answers are returned to the node.
    # 1. Update memory slots with confirmed calibers
    raw_slots = dict(state.get("memory_slots") or {})
    confirmed = dict(raw_slots.get("confirmed_calibers") or {})
    if isinstance(answers, list):
        for ans in answers:
            if isinstance(ans, dict):
                q_id = ans.get("question_id") or ans.get("field") or "caliber"
                val = ans.get("option_id") or ans.get("value") or ans.get("text") or str(ans)
                confirmed[str(q_id)] = val
    raw_slots["confirmed_calibers"] = confirmed

    # 2. Inject user clarification answers into agent conversation messages with explicit directive
    messages = deserialize_messages(list(state.get("messages") or []))
    if answers:
        clarify_text = f"用户已确认以下口径选项：{answers}。请严格基于用户已确认的业务口径，结合 Wiki 知识直接完成后续查询，不要重复提出澄清问题。"
    else:
        clarify_text = "用户已确认澄清选项，请直接执行查询。"

    messages.append(HumanMessage(content=clarify_text))

    return {
        **state,
        "messages": serialize_messages(messages),
        "memory_slots": raw_slots,
        "tool_steps": [],  # reset tool steps to avoid re-triggering clarify
    }
