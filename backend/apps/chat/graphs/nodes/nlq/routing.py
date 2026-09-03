"""Turn routing node + every graph edge router (route_after_*)."""

from __future__ import annotations

import time
from typing import Any, Literal, cast

import orjson
from langchain_core.messages import HumanMessage, SystemMessage
from sqlalchemy import select

# ── Constants ────────────────────────────────────────────────────────────────
from apps.chat.graphs.nodes.nlq.state import (
    _MAX_STEPS,
    NlqState,
    _fail,
    _finish_step_value,
    _llm_service,
)
from apps.chat.models.chat_model import (
    ChatFinishStep,
    ChatRecord,
    OperationEnum,
)
from apps.chat.plan_policy import (
    MAX_PLAN_REGEN,
)
from apps.chat.steps.observability import log_span
from apps.chat.steps.recall_topup import topup_enabled_for  # noqa: F401
from apps.chat.steps.stream import consume_llm
from apps.chat.turn_contracts import TurnRoute
from apps.chat.turn_router import route_turn
from apps.conversation.messages import message_content_text
from apps.conversation.outcome import (
    successful_outcome,
)
from apps.conversation.run_service import (
    finalize_run,
    require_active_run,
)

# monkeypatch-surface imports: tests setattr these names on submodules
from apps.conversation.runtime import submit_query  # noqa: F401
from apps.conversation.runtime_context import attach_runtime  # noqa: F401
from apps.conversation.session import session_scope
from apps.conversation.sink import StreamSink
from common.utils.json_utils import extract_nested_json
from common.utils.utils import SQLBotLogUtil


def turn_router_node(state: NlqState) -> NlqState:
    """Classify flow/context only; never infer SQL or business clauses."""
    try:
        llm_service = _llm_service(state)
        with session_scope() as session:
            run = require_active_run(session, str(state["run_id"]))
            record = session.get(ChatRecord, run.chat_record_id)
            if record is None:
                raise LookupError("Conversation turn not found")
            references = tuple(
                int(item)
                for item in (
                    state.get("reference_record_ids")
                    or record.reference_record_ids
                    or []
                )
            )
            persisted_hint = (
                record.turn_kind
                if record.turn_kind in {"analysis", "prediction", "unsupported"}
                else None
            )
            history = list(
                session.exec(
                    select(ChatRecord)
                    .where(
                        ChatRecord.chat_id == record.chat_id,
                        ChatRecord.id != record.id,
                        ChatRecord.first_chat.is_(False),
                        ChatRecord.answer.is_not(None),
                    )
                    .order_by(ChatRecord.create_time.desc())
                    .limit(6)
                ).scalars()
            )
            history.reverse()
            history_payload = [
                {
                    "record_id": int(item.id),
                    "question": str(item.question or "")[:300],
                    "kind": str(item.turn_kind or "query"),
                    "status": str((item.answer or {}).get("status") or ""),
                    "summary": str((item.answer or {}).get("content") or "")[:500],
                    "has_datasets": bool((item.answer or {}).get("datasets")),
                }
                for item in history
            ]
            question_text = str(record.question or "")
            record_id = int(record.id)
            session.commit()

        route_call_holder: dict[str, Any] = {}

        def model_router(message: str) -> dict[str, Any]:
            system = (
                "你是对话流程路由器，只返回 JSON。不得解释业务指标、字段或 SQL。"
                "这是简单分类任务：不要推理，直接给出结论。"
                "task_kind 只能是 query/analysis/prediction/unsupported；relation 只能是 "
                "independent/continue/revise。continue/revise 必须从候选历史选择 1~3 个 "
                "reference_record_ids；新问题必须 independent。"
            )
            human = orjson.dumps(
                {"current_message": message, "recent_turns": history_payload}
            ).decode()
            router_messages = [
                SystemMessage(content=system),
                HumanMessage(content=human),
            ]
            started = time.monotonic()
            try:
                call = consume_llm(
                    llm_service.llm.bind(temperature=0),
                    router_messages,
                )
            except Exception as exc:
                route_call_holder["audit_call"] = {
                    "purpose": "turn_router",
                    "model_name": str(llm_service.chat_question.ai_modal_name or ""),
                    "attempt": 1,
                    "status": "failed",
                    "elapsed_ms": round((time.monotonic() - started) * 1000),
                    "usage": {},
                    "input": router_messages,
                    "output": None,
                    "reasoning": "",
                    "error": str(exc),
                }
                raise
            route_call_holder["audit_call"] = {
                "purpose": "turn_router",
                "model_name": str(llm_service.chat_question.ai_modal_name or ""),
                "attempt": 1,
                "status": "success",
                "elapsed_ms": round((time.monotonic() - started) * 1000),
                "usage": dict(call.usage or {}),
                "input": router_messages,
                "output": call.message,
                "reasoning": call.reasoning,
                "error": "",
            }
            raw = call.content or message_content_text(
                getattr(call.message, "content", "")
            )
            # Observability: keep the raw model output so a validation failure
            # (swallowed by route_turn's fallback) stays diagnosable.
            route_call_holder["raw_text"] = str(raw)[:1000]
            nested = extract_nested_json(raw)
            if not nested:
                raise ValueError("Turn router response is not JSON")
            result = orjson.loads(nested)
            if not isinstance(result, dict):
                raise ValueError("Turn router response must be an object")
            result["source"] = "model"
            result.setdefault("confidence", 0.7)
            route_call_holder["call"] = call
            route_call_holder["raw_payload"] = result
            return result

        with log_span(
            operate=OperationEnum.TURN_ROUTE,
            record_id=record_id,
            ai_modal_id=llm_service.chat_question.ai_modal_id,
            ai_modal_name=llm_service.chat_question.ai_modal_name,
            graph_node="turn_router",
            title_key="chat.log.TURN_ROUTE",
            brief="识别当前消息与历史关系",
        ) as span:
            route = (
                TurnRoute.model_validate(state["preset_route"])
                if state.get("preset_route")
                else route_turn(
                    question_text,
                    reference_record_ids=references,
                    candidate_record_ids=tuple(
                        int(item["record_id"]) for item in history_payload
                    ),
                    route_hint=state.get("route_hint") or persisted_hint,
                    has_history=bool(history_payload),
                    model_router=model_router,
                )
            )
            if route.source == "model":
                allowed_references = {
                    int(item["record_id"]) for item in history_payload
                }
                if not set(route.reference_record_ids).issubset(allowed_references):
                    # A router may select only the compact candidate set it
                    # received. Hallucinated IDs must never broaden context —
                    # re-route through the ladder (conservative rescue keeps
                    # anaphoric messages attached to the latest turn instead
                    # of degrading them to independent).
                    route = route_turn(
                        question_text,
                        reference_record_ids=references,
                        candidate_record_ids=tuple(
                            int(item["record_id"]) for item in history_payload
                        ),
                        has_history=bool(history_payload),
                    )
                    route_call_holder["hallucinated_references"] = True
            audit_call = route_call_holder.get("audit_call")
            if audit_call is not None:
                span.set_model_calls([audit_call])
            route_call = route_call_holder.get("call")
            if route_call is not None:
                span.set_usage(route_call.usage)
                span.set_model_context(
                    [
                        SystemMessage(content="Turn Router"),
                        HumanMessage(content=question_text),
                        route_call.message,
                    ]
                )
            span.set_input(
                {
                    "message": question_text,
                    "candidate_record_ids": [
                        item["record_id"] for item in history_payload
                    ],
                    "route_hint": state.get("route_hint") or persisted_hint,
                }
            )
            span.set_output(route.model_dump(mode="json"))
            if route.source == "fallback" or route_call_holder.get(
                "hallucinated_references"
            ):
                # Diagnosability: what the model actually said before the
                # fallback/repair path replaced it.
                span.set_detail(
                    {
                        "router_raw_payload": route_call_holder.get("raw_payload"),
                        "router_raw_text": route_call_holder.get("raw_text"),
                        "hallucinated_references": bool(
                            route_call_holder.get("hallucinated_references")
                        ),
                    }
                )
            span.set_summary("chat.audit.turn_routed")

        with session_scope() as session:
            run = require_active_run(session, str(state["run_id"]))
            record = session.get(ChatRecord, run.chat_record_id)
            if record is None:
                raise LookupError("Conversation turn not found")
            run.route_snapshot = route.model_dump(mode="json")
            record.turn_kind = route.task_kind
            record.relation = route.relation
            record.reference_record_ids = list(route.reference_record_ids)
            session.add(run)
            session.add(record)
            session.commit()
        return {**state, "turn_route": route.model_dump(mode="json")}
    except Exception as exc:
        return _fail(state, state.get("record_id"), exc)


def unsupported_turn_node(state: NlqState) -> NlqState:
    content = "我可以帮助查询、分析或预测已配置数据源中的数据，请描述数据问题。"
    sink = StreamSink.from_state(state)
    with session_scope() as session:
        finalize_run(
            session,
            run_id=str(state["run_id"]),
            status="succeeded",
            current_node="unsupported",
            record_snapshot={
                "answer": {
                    "kind": "unsupported",
                    "content": content,
                    "source_record_ids": [],
                    "assumptions": [],
                },
                "sql_answer": content,
                "terminal": True,
            },
        )
    sink.text(content)
    sink.event({"type": "finish", "id": state.get("record_id")})
    return {**state, "outcome": successful_outcome()}


def route_after_context(
    state: NlqState,
) -> Literal[
    "unsupported",
    "ensure_datasource",
    "analysis_agent",
    "prediction_agent",
    "unavailable",
    "fail",
]:
    if state.get("error"):
        return "fail"
    route = state.get("turn_route") or {}
    if route.get("task_kind") == "unsupported":
        return "unsupported"
    strategy = state.get("data_strategy")
    if strategy == "existing_results":
        return (
            "analysis_agent"
            if route.get("task_kind") == "analysis"
            else "prediction_agent"
        )
    if strategy in {"direct_query", "derived_query"}:
        return "ensure_datasource"
    return "unavailable"


def route_after_turn_router(
    state: NlqState,
) -> Literal["unsupported", "assemble_context", "fail"]:
    if state.get("error"):
        return "fail"
    route = state.get("turn_route") or {}
    return (
        "unsupported" if route.get("task_kind") == "unsupported" else "assemble_context"
    )


def route_after_plan_gate(
    state: NlqState,
) -> Literal[
    "await_clarification",
    "unsupported",
    "review_query",
    "generate_queries",
    "plan_query",
    "fail",
]:
    if state.get("error"):
        return "fail"
    override = str(state.get("plan_gate_route") or "")
    if override:
        return cast(Literal["plan_query"], override)
    return route_after_planning(state)


def route_after_planning(
    state: NlqState,
) -> Literal[
    "await_clarification", "unsupported", "review_query", "generate_queries", "fail"
]:
    if state.get("error"):
        return "fail"
    if state.get("planning_decision") == "clarify":
        return "await_clarification"
    if state.get("planning_decision") == "unsupported":
        return "unsupported"
    if state.get("planning_decision") != "ready":
        return "fail"
    if (state.get("repair_hint") or "").strip():
        return "generate_queries"
    return "review_query"


def route_after_review(
    state: NlqState,
) -> Literal["await_clarification", "generate_queries", "fail"]:
    if state.get("error"):
        return "fail"
    if state.get("planning_decision") == "clarify":
        return "await_clarification"
    if state.get("planning_decision") == "ready":
        return "generate_queries"
    return "fail"


def route_after_queries(
    state: NlqState,
) -> Literal[
    "await_clarification", "generate_queries", "execute_queries", "complete", "fail"
]:
    """Execute when plans exist; else plan-regen within MAX_PLAN_REGEN, else fail."""
    if state.get("error"):
        return "fail"
    if state.get("planning_decision") == "clarify":
        return "await_clarification"

    plans = (state.get("active_candidate") or {}).get("plans") or []
    if plans:
        if _finish_step_value(state) <= int(ChatFinishStep.GENERATE_QUERY.value):
            return "complete"
        return "execute_queries"

    attempts = int(state.get("gen_attempts") or 0)
    repair = (state.get("repair_hint") or "").strip()
    if repair and attempts < MAX_PLAN_REGEN:
        SQLBotLogUtil.info(
            f"route_after_queries: plan regen attempts={attempts}/{MAX_PLAN_REGEN}"
        )
        return "generate_queries"
    return "fail"


def route_after_execute(
    state: NlqState,
) -> Literal["decide_next", "fail"]:
    if state.get("error"):
        return "fail"
    return "decide_next"


def route_after_decision(
    state: NlqState,
) -> Literal[
    "generate_queries",
    "generate_charts",
    "analysis_agent",
    "prediction_agent",
    "complete",
    "fail",
]:
    if state.get("error"):
        return "fail"
    step_index = state.get("step_index", 0)
    max_steps = state.get("max_steps", _MAX_STEPS)
    decision = state.get("decision") or "finish"

    if decision == "repair":
        return "generate_queries" if step_index < max_steps else "complete"
    if decision == "accept":
        task_kind = (state.get("turn_route") or {}).get("task_kind")
        if task_kind == "analysis":
            return "analysis_agent"
        if task_kind == "prediction":
            return "prediction_agent"
        if _finish_step_value(state) <= int(ChatFinishStep.QUERY_DATA.value):
            return "complete"
        return "generate_charts"
    return "complete"


def route_after_presentation(
    state: NlqState,
) -> Literal["summarize_answer", "analysis_agent", "prediction_agent", "fail"]:
    if state.get("error"):
        return "fail"
    task_kind = (state.get("turn_route") or {}).get("task_kind")
    if task_kind == "analysis":
        return "analysis_agent"
    if task_kind == "prediction":
        return "prediction_agent"
    return "summarize_answer"
