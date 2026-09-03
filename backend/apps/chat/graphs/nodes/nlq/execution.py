"""Agentic batch execution nodes: generate_queries, execute_queries, decide_next."""

from __future__ import annotations

from concurrent.futures import as_completed
from typing import Any, Literal, cast

from sqlalchemy import select

from apps.chat.aggregation_window import (
    apply_grouped_metric_order,
)
from apps.chat.graphs.nodes.nlq.audit import (
    _apply_row_permissions,
    _query_plan,
    _serialized_plan,
)
from apps.chat.graphs.nodes.nlq.planning import (
    _accepted_review_card,
    _classify_plan_risk,
    _invoke_semantic_review,
    _plan_fact_models,
    _plan_repair_message,
    _planning_call_timeout_sec,
    _planning_elapsed_for_state,
)
from apps.chat.graphs.nodes.nlq.quality import (
    _assess_all_steps,
    _attach_aggregation_totals,
    _build_candidate_quality,
    _candidate_batch,
    _merge_batch_into_steps,
    _normalize_result_data,
    _repair_instruction,
)

# ── Constants ────────────────────────────────────────────────────────────────
from apps.chat.graphs.nodes.nlq.state import (
    _MAX_BATCH_SIZE,
    _MAX_STEPS,
    _ROW_LIMIT,
    CandidateBatch,
    NlqState,
    _access_scope,
    _fail,
    _generation_question,
    _llm_service,
    _sql_dialect,
)
from apps.chat.models.chat_model import (
    OperationEnum,
)
from apps.chat.plan_policy import (
    MAX_PLAN_REGEN,
)
from apps.chat.planning import apply_batch_display_defaults, parse_query_generation
from apps.chat.planning_context import (
    capture_planning_context,
    execution_schema_resources,
    restore_planning_context,
)
from apps.chat.result_quality import (
    build_overall_quality,
    cap_quality,
)
from apps.chat.result_validation import (
    ResultValidationReport,
    validate_result_structure,
    validation_issue_prompt_text,
)
from apps.chat.steps.chat_scope import (
    invalidate_connection,
)
from apps.chat.steps.observability import log_span
from apps.chat.steps.query_agent import (
    plan_body_fingerprint,
    repair_physical_plans,
    revalidate_query_plans,  # noqa: F401
    review_query_semantics,  # noqa: F401
    run_query_agent,  # noqa: F401
)
from apps.chat.steps.schema import match_table_schema

# monkeypatch-surface imports: tests setattr these names on submodules
from apps.chat.steps.stream import consume_llm  # noqa: F401
from apps.chat.task.llm import LLMService
from apps.conversation.models import ConversationInterrupt, QueryRun
from apps.conversation.outcome import (
    RunOutcome,
    classify_failure,
    format_error_message,
    outcome_from_steps,
    running_outcome,
)
from apps.conversation.run_service import (
    ConversationRunCancelled,
    active_evidence,
    load_query_plan_result,
    persist_query_clarification,
    persist_query_decision,
    persist_query_plan_failure,
    persist_query_plan_result,
    register_query_plans,
    require_active_run,  # noqa: F401
)
from apps.conversation.runtime import submit_query
from apps.conversation.runtime_context import attach_runtime
from apps.conversation.session import session_scope
from apps.conversation.sink import StreamSink
from apps.datasource.access import (
    access_scope_fingerprint,
    resolve_access_scope,
)
from common.error import SingleMessageError
from common.utils.utils import SQLBotLogUtil


def generate_queries_node(state: NlqState) -> NlqState:
    """Plan SQL queries for the current batch.

    The initial physical plan is produced by Query Agent. This node
    re-enters only for bounded structural repair (empty/invalid SQL or an
    execute-time rewrite). It must never reinterpret user evidence.
    """
    llm_service = _llm_service(state)
    sink = StreamSink.from_state(state)
    step_index = state.get("step_index", 0)
    base = 0
    json_result: dict[str, Any] = dict(state.get("json_result") or {"success": True})
    gen_attempts = int(state.get("gen_attempts") or 0)

    # Query Agent generated the initial plan. This node is entered again only
    # for bounded physical repair and must never reinterpret business meaning.
    if (state.get("active_candidate") or {}).get("plans") and not state.get(
        "repair_hint"
    ):
        return state

    try:
        sink.event(
            {
                "type": "batch-start",
                "index": step_index,
                "base_index": base,
                "gen_attempts": gen_attempts,
            }
        )

        repair = (state.get("repair_hint") or "").strip()
        previous_plans = list(state.get("repair_source_plans") or [])
        if not previous_plans and state.get("rejected_candidate"):
            previous_plans = list(
                (state.get("rejected_candidate") or {}).get("plans") or []
            )
        with log_span(
            operate=OperationEnum.GENERATE_QUERY,
            record_id=llm_service.record.id,
            ai_modal_id=llm_service.chat_question.ai_modal_id,
            ai_modal_name=llm_service.chat_question.ai_modal_name,
            graph_node="generate_queries",
            title_key="chat.log.REPAIR_QUERY",
            brief="修复查询语句",
            step_index=step_index,
            gen_attempts=gen_attempts,
        ) as span:
            consumed_budget = float(state.get("planning_model_elapsed_sec") or 0.0)
            repair_evidence: list[Any] = []
            try:
                with session_scope() as session:
                    repair_evidence = list(
                        active_evidence(session, str(state["run_id"]))
                    )
            except Exception:  # noqa: BLE001
                repair_evidence = []
            physical = repair_physical_plans(
                llm_service,
                previous_plans=previous_plans,
                validation_error=repair,
                timeout_seconds=_planning_call_timeout_sec(),
                attempt=gen_attempts + 1,
                evidence=repair_evidence,
                prior_user_evidence=state.get("prior_user_evidence") or [],
            )
            span["token_usage"] = physical.usage
            span["reasoning_content"] = physical.reasoning
            span.set_model_calls(physical.model_calls)
            span["payload"] = {
                "status": ("valid" if physical.plans else "needs_repair"),
                "attempt": gen_attempts + 1,
                "error": None if physical.plans else "No safe repaired plan",
                # Why this repair round exists — the rejection cause from the
                # physical gates (kept concise; full text stays in repair_hint).
                "reason": (repair or "")[:300],
            }
        planning_elapsed = consumed_budget + sum(
            float(item.get("elapsed_ms") or 0) / 1000 for item in physical.model_calls
        )
        if physical.reasoning:
            sink.token(
                content="",
                reasoning_content=physical.reasoning,
                event_type="step-sql-result",
                metadata={"index": base},
            )
        plans = list(physical.plans)
        refusal = None if plans else "No safe repaired query plan"
        plans = apply_batch_display_defaults(
            plans,
            str(
                llm_service.generation_question
                or llm_service.chat_question.question
                or ""
            ),
        )
        dialect = _sql_dialect(llm_service)
        apply_grouped_metric_order(plans, dialect=dialect)
        fact_models = _plan_fact_models(plans, dialect=dialect)
        fact_payloads = [item.model_dump(mode="json") for item in fact_models]
        with session_scope() as session:
            query_run = session.get(QueryRun, str(state["run_id"]))
            if query_run is None:
                raise LookupError(f"Query run {state['run_id']} not found")
            planning_context = restore_planning_context(
                llm_service,
                dict(query_run.planning_context or {}),
            )
            evidence = active_evidence(session, str(state["run_id"]))
            clarification_rounds = len(
                session.exec(
                    select(ConversationInterrupt).where(
                        ConversationInterrupt.run_id == str(state["run_id"]),
                        ConversationInterrupt.status == "consumed",
                    )
                )
                .scalars()
                .all()
            )
            agent_decision = dict(query_run.agent_decision or {})
        risk_payload, compiled = _classify_plan_risk(
            llm_service=llm_service,
            planning_context=planning_context,
            evidence=evidence,
            facts=fact_models,
        )
        review_payload = dict(state.get("semantic_review") or {})
        semantic_status: Literal["verified", "partial", "unsupported"] = "verified"
        if plans and risk_payload.get("level") == "high":
            current_fingerprints = [plan_body_fingerprint(item) for item in plans]
            reviewed_fingerprints = [
                str(item) for item in review_payload.get("reviewed_fingerprints") or []
            ]
            if review_payload and reviewed_fingerprints != current_fingerprints:
                review_payload = {
                    "verdict": "uncertain",
                    "issues": [
                        {
                            "code": "PLAN_CHANGED_AFTER_REVIEW",
                            "message": "查询计划已在复核后修复，本轮不重复调用复核模型",
                        }
                    ],
                    "reviewed_fingerprints": current_fingerprints,
                }
            elif not review_payload:
                try:
                    review_payload, review_elapsed = _invoke_semantic_review(
                        llm_service=llm_service,
                        record_id=int(llm_service.record.id),
                        evidence=evidence,
                        plans=plans,
                        fact_payloads=fact_payloads,
                        risk_payload=risk_payload,
                        compiled=compiled,
                        timeout_seconds=_planning_call_timeout_sec(),
                        brief="复核查询语句",
                        prior_user_evidence=state.get("prior_user_evidence") or [],
                        wiki_knowledge=str(state.get("wiki_knowledge_text") or ""),
                    )
                    planning_elapsed += review_elapsed
                except Exception as review_error:
                    SQLBotLogUtil.warning(f"semantic reviewer degraded: {review_error}")
                    review_payload = {
                        "verdict": "uncertain",
                        "issues": [
                            {
                                "code": "REVIEW_UNAVAILABLE",
                                "message": "语义复核调用失败",
                            }
                        ],
                        "reviewed_fingerprints": current_fingerprints,
                    }
            verdict = str(review_payload.get("verdict") or "uncertain")
            if verdict == "repair":
                attempts = gen_attempts + 1
                if attempts >= MAX_PLAN_REGEN:
                    raise SingleMessageError(
                        "高风险语义复核仍发现查询实现问题，且物理修复次数已达到上限。"
                    )
                repair_hint = "\n".join(
                    str(item.get("message") or "")
                    for item in review_payload.get("issues") or []
                )
                with session_scope() as session:
                    persist_query_decision(
                        session,
                        run_id=str(state["run_id"]),
                        decision=agent_decision,
                        plans=plans,
                        hard_gate_report={"status": "passed", "plan_count": len(plans)},
                        risk_assessment=risk_payload,
                        plan_facts=fact_payloads,
                        semantic_review=review_payload,
                        planning_status="repairing",
                    )
                return {
                    **state,
                    "active_candidate": {},
                    "repair_source_plans": plans,
                    "repair_hint": repair_hint or "语义复核要求修复物理查询计划",
                    "gen_attempts": attempts,
                    "risk_assessment": risk_payload,
                    "semantic_review": review_payload,
                    "plan_facts": fact_payloads,
                    "planning_model_elapsed_sec": planning_elapsed,
                }
            if verdict == "clarify":
                review_card = _accepted_review_card(
                    review_payload,
                    evidence,
                    clarification_rounds=clarification_rounds,
                )
                if review_card is not None:
                    with session_scope() as session:
                        persist_query_decision(
                            session,
                            run_id=str(state["run_id"]),
                            decision=agent_decision,
                            plans=plans,
                            hard_gate_report={
                                "status": "passed",
                                "plan_count": len(plans),
                            },
                            risk_assessment=risk_payload,
                            plan_facts=fact_payloads,
                            semantic_review=review_payload,
                            planning_status="awaiting_input",
                        )
                        persist_query_clarification(
                            session,
                            run_id=str(state["run_id"]),
                            held_plans=plans,
                        )
                    return {
                        **state,
                        "planning_decision": "clarify",
                        "ambiguity_payload": review_card.model_dump(mode="json"),
                        "active_candidate": {},
                        "repair_source_plans": [],
                        "risk_assessment": risk_payload,
                        "semantic_review": review_payload,
                        "plan_facts": fact_payloads,
                        "planning_model_elapsed_sec": _planning_elapsed_for_state(
                            interrupt=True, elapsed=planning_elapsed
                        ),
                    }
                review_payload = {
                    **review_payload,
                    "verdict": "uncertain",
                    "issues": [
                        *(review_payload.get("issues") or []),
                        {
                            "code": "CLARIFICATION_UNAVAILABLE",
                            "message": "复核未返回可交互的业务选项或已达到澄清上限",
                        },
                    ],
                }
                verdict = "uncertain"
            if verdict != "pass":
                semantic_status = "partial"
                state = {**state, "quality_cap": 69, "execution_mode": "unverified"}
        if plans:
            with session_scope() as session:
                persist_query_decision(
                    session,
                    run_id=str(state["run_id"]),
                    decision=agent_decision,
                    plans=plans,
                    hard_gate_report={"status": "passed", "plan_count": len(plans)},
                    risk_assessment=risk_payload,
                    plan_facts=fact_payloads,
                    semantic_review=review_payload or None,
                    planning_status="ready",
                )
        candidate: CandidateBatch = {
            "plans": plans,
            "plan_validated": bool(plans),
            "semantic_status": semantic_status,
        }

        if not plans:
            msg = refusal or "Failed to generate any valid SQL queries"
            attempts = gen_attempts + 1
            repair_msg = _plan_repair_message(msg)
            SQLBotLogUtil.warning(
                f"plan generation empty attempt={attempts}: {msg[:240]}"
            )
            try:
                sink.event(
                    {
                        "type": "plan-validation",
                        "status": "failed",
                        "attempt": attempts,
                        "message": msg[:800],
                    }
                )
            except Exception:
                pass
            if attempts < MAX_PLAN_REGEN:
                return {
                    **state,
                    "json_result": json_result,
                    "active_candidate": {},
                    "repair_hint": repair_msg,
                    "gen_attempts": attempts,
                    "error": None,
                    "planning_model_elapsed_sec": planning_elapsed,
                }
            return {
                **_fail(
                    {
                        **state,
                        "active_candidate": {},
                        "repair_hint": repair_msg,
                        "gen_attempts": attempts,
                    },
                    llm_service.record.id,
                    SingleMessageError(msg),
                ),
                "json_result": json_result,
            }

        sink.event(
            {
                "type": "batch-plans",
                "index": step_index,
                "base_index": base,
                "count": len(candidate["plans"]),
            }
        )

        with session_scope() as session:
            register_query_plans(
                session,
                run_id=str(state["run_id"]),
                plans=candidate["plans"],
                repair_record={
                    "attempt": gen_attempts + 1,
                    "reason": repair,
                    "plan_ids": [item.get("plan_id") for item in candidate["plans"]],
                    "status": "valid",
                },
            )

        return {
            **state,
            "json_result": json_result,
            "active_candidate": candidate,
            "repair_hint": "",
            "gen_attempts": 0,
            "repair_source_plans": [],
            "planning_model_elapsed_sec": planning_elapsed,
            "risk_assessment": risk_payload,
            "semantic_review": review_payload,
            "plan_facts": fact_payloads,
            "error": None,
        }
    except Exception as e:
        return _fail(state, llm_service.record.id, e)


def execute_queries_node(state: NlqState) -> NlqState:
    """Execute batch plans concurrently.

    Row-permission rewrites run serially on the main thread (LLMService is not
    thread-safe). Only protocol.execute runs in the pool with independent sessions.
    Candidate results stay in graph state until the review node accepts them.
    ChatLog remains the complete audit trail for every attempt.
    """
    llm_service = _llm_service(state)
    active_candidate = dict(state.get("active_candidate") or {})
    plans = list(active_candidate.get("plans") or [])
    base = 0

    if not plans:
        return _fail(
            state, llm_service.record.id, SingleMessageError("No plans to execute")
        )

    # Access policy and schema are execution-time facts. Re-read both after
    # planning so a long model call cannot execute with stale permissions or
    # identifiers. Schema drift never changes user evidence; it either passes a
    # fresh structural parse or enters the bounded physical-repair loop.
    schema_drift_errors: dict[str, str] = {}
    fresh_schema_fingerprint = ""
    fresh_access_fingerprint = ""
    try:
        with session_scope() as gate_session:
            fresh_scope = resolve_access_scope(
                gate_session,
                current_user=llm_service.current_user,
                ds=llm_service.ds,
            )
            attach_runtime(str(state["run_id"]), access_scope=fresh_scope)
            fresh_access_fingerprint = access_scope_fingerprint(fresh_scope)
            query_run = gate_session.get(QueryRun, str(state["run_id"]))
            planned_payload = (
                dict(query_run.planning_context or {}) if query_run is not None else {}
            )
            required_resources = execution_schema_resources(
                [
                    str(name)
                    for name in (planned_payload.get("resources") or [])
                    if str(name).strip()
                ],
                plans,
            )
            match_table_schema(
                llm_service,
                gate_session,
                resource_names=required_resources,
                access_scope=fresh_scope,
                graph_node="execute_queries",
                brief="refresh schema",
                audit=False,
            )
            current_context = capture_planning_context(
                llm_service,
                entity_bindings=state.get("entity_bindings") or {},
                temporal_parse=state.get("temporal_parse") or {},
                wiki_context=dict(state.get("wiki_context") or {}),
            )
            fresh_schema_fingerprint = current_context.schema_fingerprint
            planned_context = (
                restore_planning_context(llm_service, planned_payload)
                if planned_payload
                else current_context
            )
            # restore_planning_context above restores the planned prompt. Put
            # the fresh schema back before validating candidates.
            llm_service.chat_question.db_schema = current_context.schema_text
            llm_service.table_name_list = list(current_context.resources)
            if current_context.schema_fingerprint != planned_context.schema_fingerprint:
                for plan in plans:
                    plan_id = str(plan.get("plan_id") or "")
                    payload = dict(plan.get("payload") or {})
                    if not payload and plan.get("sql"):
                        payload = {"sql": plan.get("sql")}
                    parsed = parse_query_generation(
                        payload,
                        llm_service,
                        max_batch_size=1,
                    )
                    if not parsed.success or not parsed.plans:
                        schema_drift_errors[plan_id] = (
                            parsed.error_message
                            or "Schema changed and the query plan is no longer valid"
                        )
    except Exception as exc:
        return _fail(state, llm_service.record.id, exc)

    # 1) Prepare executable plans (permissions) on main thread
    prepared: list[dict[str, Any]] = []
    with session_scope() as session:
        for i, plan_dict in enumerate(plans):
            try:
                plan_id = str(plan_dict.get("plan_id") or "")
                if plan_id in schema_drift_errors:
                    prepared.append(
                        {
                            **plan_dict,
                            "index": i,
                            "prep_error": schema_drift_errors[plan_id],
                            "prep_failure": {
                                "kind": "unknown_identifier",
                                "message": schema_drift_errors[plan_id],
                                "retryable": True,
                                "step_index": i,
                            },
                        }
                    )
                    continue
                qp = _apply_row_permissions(
                    llm_service,
                    session,
                    plan_dict,
                    _access_scope(state),
                )
                prepared.append({**_serialized_plan(qp, plan_dict), "index": i})
            except Exception as e:
                prepared.append(
                    {
                        **plan_dict,
                        "index": i,
                        "prep_error": format_error_message(e),
                        "prep_failure": classify_failure(e, step_index=i),
                    }
                )

    results: list[dict[str, Any] | None] = [None] * len(prepared)

    def _execute_single(idx: int, plan_dict: dict[str, Any]) -> dict[str, Any]:
        gidx = base + idx
        sql_show = plan_dict.get("format_statement") or plan_dict.get("sql") or ""
        brief = (plan_dict.get("brief") or "")[:40]
        record_id = getattr(llm_service.record, "id", None)
        plan_id = str(plan_dict.get("plan_id") or "")
        with log_span(
            operate=OperationEnum.EXECUTE_QUERY,
            record_id=record_id,
            run_id=str(state["run_id"]),
            local_operation=True,
            graph_node="execute_queries",
            title_key="chat.log.EXECUTE_QUERY",
            step_index=state.get("step_index", 0),
            unit_index=gidx,
            brief=brief,
        ) as span:
            try:
                if plan_id:
                    with session_scope() as replay_session:
                        persisted = load_query_plan_result(
                            replay_session,
                            run_id=str(state["run_id"]),
                            plan_id=plan_id,
                            schema_fingerprint=fresh_schema_fingerprint,
                            access_policy_fingerprint=fresh_access_fingerprint,
                        )
                    if persisted is not None:
                        rows = persisted.get("data")
                        count = len(rows) if isinstance(rows, list) else 0
                        span.set_detail(
                            {
                                "count": count,
                                "sql": sql_show[:2000],
                                "index": gidx,
                                "brief": brief,
                                "source": "replay",
                            }
                        )
                        span.set_input(plan_dict)
                        span.set_output(persisted)
                        span.set_summary("chat.audit.query_replayed", count=count)
                        return {
                            "index": idx,
                            "result": persisted,
                            "plan": plan_dict,
                            "re_exec": persisted.get("re_exec"),
                            "replayed": True,
                        }
                if plan_dict.get("prep_error"):
                    raise SingleMessageError(plan_dict["prep_error"])
                qp = _query_plan(plan_dict)
                span.set_input(plan_dict)
                with session_scope() as session:
                    _ = session
                    qr = llm_service.protocol.execute(
                        llm_service.ds,
                        qp,
                        max_rows=(
                            _ROW_LIMIT if llm_service.enable_sql_row_limit else None
                        ),
                    )
                    result = qr.as_dict()
                    if result.get("is_success") is False:
                        span.set_output(result)
                        code = result.get("code_value")
                        msg = (
                            f"Query failed (code={code})"
                            if code is not None
                            else "Query failed"
                        )
                        raise SingleMessageError(msg)
                    result = _normalize_result_data(result, llm_service)
                    result = _attach_aggregation_totals(llm_service, plan_dict, result)
                    span.set_output(result)
                    if plan_id:
                        with session_scope() as persist_session:
                            persist_query_plan_result(
                                persist_session,
                                run_id=str(state["run_id"]),
                                plan_id=plan_id,
                                result=result,
                                schema_fingerprint=fresh_schema_fingerprint,
                                access_policy_fingerprint=fresh_access_fingerprint,
                            )
                    rows = result.get("data") if isinstance(result, dict) else None
                    n = len(rows) if isinstance(rows, list) else 0
                    span["payload"] = {
                        "count": n,
                        "sql": sql_show[:2000],
                        "index": gidx,
                        "brief": brief,
                        "fields": (result.get("fields") or [])[:40]
                        if isinstance(result, dict)
                        else [],
                        "coverage_totals": result.get("coverage_totals") or {},
                    }
                    span.set_summary("chat.audit.query_executed", count=n)
                    return {
                        "index": idx,
                        "result": result,
                        "plan": plan_dict,
                        "re_exec": result.get("re_exec")
                        or getattr(qr, "re_exec", None),
                    }
            except Exception as exc:
                span.mark_failed(format_error_message(exc)[:500])
                span["payload"] = {
                    "count": 0,
                    "sql": sql_show[:2000],
                    "index": gidx,
                    "brief": brief,
                    "error": format_error_message(exc)[:500],
                }
                raise

    try:
        # Every datasource execution uses the shared bounded query pool.
        workers = min(len(prepared), state.get("max_batch_size") or _MAX_BATCH_SIZE)
        if workers <= 1:
            idx = 0
            try:
                r = submit_query(_execute_single, 0, prepared[0]).result()
                results[0] = r
            except ConversationRunCancelled:
                raise
            except Exception as e:
                failure = prepared[0].get("prep_failure") or classify_failure(
                    e, step_index=0
                )
                if failure.get("kind") == "connection":
                    # A dead connection invalidates the chat-scoped verdict so
                    # the next turn re-checks instead of trusting the TTL.
                    invalidate_connection(getattr(llm_service.ds, "id", None))
                results[0] = {
                    "index": 0,
                    "error": format_error_message(e),
                    "failure": failure,
                    "plan": prepared[0],
                }
        else:
            futures = {
                submit_query(_execute_single, i, p): i for i, p in enumerate(prepared)
            }
            for future in as_completed(futures):
                idx = futures[future]
                try:
                    results[idx] = future.result()
                except ConversationRunCancelled:
                    raise
                except Exception as e:
                    failure = prepared[idx].get("prep_failure") or classify_failure(
                        e, step_index=idx
                    )
                    if failure.get("kind") == "connection":
                        invalidate_connection(getattr(llm_service.ds, "id", None))
                    results[idx] = {
                        "index": idx,
                        "error": format_error_message(e),
                        "failure": failure,
                        "plan": prepared[idx],
                    }

        # Materialize the ordered candidate batch. Do not persist or emit result
        # cards here: quality review still owns accept-versus-repair.
        flat_results: list[dict[str, Any]] = []
        for r in results:
            if r is None:
                continue
            flat_results.append(r)
            if r.get("error"):
                failed_plan = dict(r.get("plan") or {})
                failed_plan_id = str(failed_plan.get("plan_id") or "")
                if failed_plan_id:
                    failure = dict(r.get("failure") or {})
                    with session_scope() as failure_session:
                        persist_query_plan_failure(
                            failure_session,
                            run_id=str(state["run_id"]),
                            plan_id=failed_plan_id,
                            error={
                                "kind": str(failure.get("kind") or "execution"),
                                "message": str(r.get("error") or "Query failed")[:1000],
                                "retryable": bool(failure.get("retryable")),
                            },
                        )

        snapshot_steps = _merge_batch_into_steps(
            [],
            prepared,
            flat_results,
            [],
            entity_bindings=state.get("entity_bindings"),
        )
        if not flat_results:
            raise SingleMessageError("No query results produced")

        # Always return per-step outcomes (including errors). The agentic loop's
        # quality gate / decide_next owns rewrite-or-summarize; do not collapse
        # the batch into a single generic failure that skips repair.
        any_ok = any(not r.get("error") for r in flat_results)
        if not any_ok:
            first_err = next(
                (r.get("error") for r in flat_results if r.get("error")),
                "",
            )
            SQLBotLogUtil.warning(
                f"All queries in batch failed; deferring to decide/repair. first={first_err[:200]}"
            )

        return {
            **state,
            "active_candidate": {
                **active_candidate,
                "plans": prepared,
                "results": flat_results,
                "steps": snapshot_steps,
                "outcome": outcome_from_steps(snapshot_steps),
            },
            "outcome": outcome_from_steps(snapshot_steps),
        }
    except Exception as e:
        return _fail(state, llm_service.record.id, e)


def decide_next_node(state: NlqState) -> NlqState:
    """Validate the candidate batch and decide repair, accept, or reject."""
    llm_service = _llm_service(state)
    step_index = state.get("step_index", 0)
    max_steps = state.get("max_steps", _MAX_STEPS)
    record_id = getattr(llm_service.record, "id", None) or state.get("record_id")

    # Impl sets used_llm/usage only when it actually invokes the model.
    meta: dict[str, Any] = {"used_llm": False}
    with log_span(
        operate=OperationEnum.DECIDE_NEXT,
        record_id=record_id,
        ai_modal_id=getattr(llm_service.chat_question, "ai_modal_id", None),
        ai_modal_name=getattr(llm_service.chat_question, "ai_modal_name", None),
        local_operation=True,
        graph_node="decide_next",
        title_key="chat.log.DECIDE_NEXT",
        step_index=step_index,
    ) as span:
        out = _decide_next_impl(state, llm_service, step_index, max_steps, meta=meta)
        span["local_operation"] = not bool(meta.get("used_llm"))
        span["token_usage"] = meta.get("token_usage") or {}
        span["payload"] = {
            "decision": out.get("decision"),
            "reason": out.get("decision_reason") or "",
            "step_index": out.get("step_index"),
            "has_analysis": bool((out.get("analysis_text") or "").strip()),
            "repair": bool((out.get("repair_hint") or "").strip()),
            "used_llm": bool(meta.get("used_llm")),
            "path": meta.get("path") or "unknown",
        }
        decision = str(out.get("decision") or "")
        if decision == "accept":
            span.set_summary("chat.audit.execution_accepted")
        elif decision == "repair":
            span.set_summary("chat.audit.execution_needs_repair")
        else:
            span.set_summary("chat.audit.execution_finished")
        return out


def _decide_next_impl(
    state: NlqState,
    llm_service: LLMService,
    step_index: int,
    max_steps: int,
    *,
    meta: dict[str, Any] | None = None,
) -> NlqState:
    """Accept, repair, or reject one executed candidate without presentation.

    This node is the publication gate. Quality scores never participate in the
    decision; only execution outcome and deterministic structural validation do.
    """
    if meta is None:
        meta = {}
    active_candidate = dict(state.get("active_candidate") or {})
    batch_plans = list(active_candidate.get("plans") or [])
    batch_results = list(active_candidate.get("results") or [])
    batch_charts = list(active_candidate.get("charts") or [])
    current_steps = list(active_candidate.get("steps") or [])
    if not current_steps:
        current_steps = _merge_batch_into_steps(
            [],
            batch_plans,
            batch_results,
            batch_charts,
            entity_bindings=state.get("entity_bindings"),
        )
    assessments = _assess_all_steps(current_steps)
    validation: ResultValidationReport = validate_result_structure(assessments)
    issues_by_step: dict[int, list[dict[str, Any]]] = {}
    for issue in validation["issues"]:
        issues_by_step.setdefault(int(issue["step_index"]), []).append(dict(issue))
    for assessment in assessments:
        step_issues = issues_by_step.get(int(assessment["index"]), [])
        assessment["structural_issues"] = step_issues
        if 0 <= int(assessment["index"]) < len(current_steps):
            current_steps[int(assessment["index"])]["_structural_issues"] = step_issues
    quality = _build_candidate_quality(
        assessments,
        requirements_covered=bool(active_candidate.get("plan_validated")),
        plan_validated=bool(active_candidate.get("plan_validated")),
        semantic_status=active_candidate.get("semantic_status", "unsupported"),
        assumption_risk=(
            "high"
            if (state.get("risk_assessment") or {}).get("level") == "high"
            and (state.get("semantic_review") or {}).get("verdict") != "pass"
            else "low"
        ),
    )
    if state.get("quality_cap"):
        quality = cap_quality(
            quality,
            maximum=int(state["quality_cap"]),
            reason_code="semantic_review_not_confirmed",
        )
    raw_outcome = outcome_from_steps(current_steps)
    current_candidate: CandidateBatch = {
        **active_candidate,
        **_candidate_batch(
            current_steps,
            quality=quality,
            outcome=raw_outcome,
        ),
    }
    current_quality = current_candidate["quality"]
    candidate_outcome = current_candidate["outcome"]
    question = _generation_question(llm_service)

    force_terminal = step_index >= max_steps - 1
    failures = candidate_outcome.get("failures") or []
    execution_valid = candidate_outcome["status"] == "success"
    retryable_failure = bool(failures) and all(
        bool(failure.get("retryable")) for failure in failures
    )
    needs_repair = not validation["valid"] or retryable_failure
    repair_hint = _repair_instruction(assessments, question) if needs_repair else ""
    if needs_repair and not force_terminal:
        SQLBotLogUtil.info(
            "decide_next structural gate -> repair; "
            f"issues={len(validation['issues'])}, failures={len(failures)}"
        )
        meta["path"] = "structural_repair"
        meta["used_llm"] = False
        return {
            **state,
            "decision": "repair",
            "decision_reason": "deterministic result validation",
            "analysis_text": state.get("analysis_text") or "",
            "accepted_candidate": None,
            "rejected_candidate": current_candidate,
            "active_candidate": {},
            "step_index": step_index + 1,
            "repair_hint": repair_hint,
            "gen_attempts": 0,
            "outcome": running_outcome(),
        }

    if execution_valid and not validation["valid"] and force_terminal:
        # The physical plan is structurally safe and executed, but the bounded
        # repair loop could not prove complete semantic coverage.  Publishing a
        # degraded, explicitly scored result is more useful than replacing it
        # with an empty terminal error; the specification itself is unchanged.
        candidate_outcome["status"] = "degraded"
        accepted_candidate = cast(
            CandidateBatch,
            {
                **current_candidate,
                "steps": current_steps,
                "quality": current_quality,
                "outcome": candidate_outcome,
            },
        )
        meta["path"] = "degraded_after_repair_budget"
        meta["used_llm"] = False
        return {
            **state,
            "decision": "accept",
            "decision_reason": "repair budget exhausted; safe result published with structural risks",
            "analysis_text": "",
            "accepted_candidate": accepted_candidate,
            "rejected_candidate": None,
            "step_index": step_index,
            "repair_hint": "",
            "outcome": candidate_outcome,
        }

    if not execution_valid or not validation["valid"]:
        meta["path"] = "terminal_rejection"
        meta["used_llm"] = False
        reason = "; ".join(
            validation_issue_prompt_text(issue) for issue in validation["issues"]
        ) or next(
            (
                str(failure.get("message"))
                for failure in failures
                if failure.get("message")
            ),
            "candidate execution failed",
        )
        terminal_outcome = cast(
            RunOutcome,
            {
                **candidate_outcome,
                "status": "failed",
                "failures": [classify_failure(reason, default_kind="validation")],
                # No candidate is published after terminal rejection. Its
                # internal diagnostic score must not become a user-facing
                # quality stamp for an empty answer.
                "quality": build_overall_quality([]),
            },
        )
        return {
            **state,
            "decision": "complete",
            "decision_reason": reason,
            "analysis_text": "",
            "accepted_candidate": None,
            "rejected_candidate": current_candidate,
            "active_candidate": {},
            "step_index": step_index,
            "repair_hint": "",
            "outcome": terminal_outcome,
        }

    if current_quality["grade"] in {"reference_only", "unreliable"}:
        candidate_outcome["status"] = "degraded"
    accepted_candidate: CandidateBatch = {
        **current_candidate,
        "steps": current_steps,
        "quality": current_quality,
        "outcome": candidate_outcome,
    }
    meta["path"] = "accepted"
    meta["used_llm"] = False
    return {
        **state,
        "decision": "accept",
        "decision_reason": "candidate passed execution and structural validation",
        "analysis_text": "",
        "accepted_candidate": accepted_candidate,
        "rejected_candidate": None,
        "step_index": step_index,
        "repair_hint": "",
        "outcome": candidate_outcome,
    }
