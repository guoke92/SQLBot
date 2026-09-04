"""Planning nodes: plan_query, plan_gate, review_query, clarification, unsupported-query."""

from __future__ import annotations

import re
from typing import Any, Literal, cast

from langgraph.types import interrupt
from sqlalchemy import select

from apps.chat.aggregation_window import (
    apply_grouped_metric_order,
)
from apps.chat.graphs.nodes.nlq.audit import (
    _record_snapshot_values,
)

# ── Constants ────────────────────────────────────────────────────────────────
from apps.chat.graphs.nodes.nlq.state import (
    _MAX_BATCH_SIZE,
    NlqState,
    _access_scope,
    _ds_databases,
    _ds_scope,
    _fail,
    _llm_service,
    _sql_dialect,
)
from apps.chat.graphs.nodes.nlq.topup import (
    _GateExpansion,
    _run_topup,
    _topup_on_failed_gates,
    _wiki_business_text_safely,
)
from apps.chat.models.chat_model import (
    OperationEnum,
)
from apps.chat.plan_facts import PlanFacts, extract_sql_plan_facts
from apps.chat.planning_context import (
    restore_planning_context,
)
from apps.chat.query_risk import QueryRiskInput, classify_query_risk
from apps.chat.result_quality import (
    build_overall_quality,
)
from apps.chat.semantic_planning import (
    ClarificationCard,
    NeedClarification,
    QueryUnsupported,
    Ready,
    enforce_clarification_policy,
    question_id_of,
)

# monkeypatch-surface imports: tests setattr these names on submodules
from apps.chat.steps.knowledge import get_compiled_knowledge  # noqa: F401
from apps.chat.steps.observability import log_span
from apps.chat.steps.query_agent import (
    QueryAgentError,
    plan_body_fingerprint,
    revalidate_query_plans,
    review_query_semantics,
    run_query_agent,
)
from apps.chat.steps.recall_map import render_knowledge_map, render_schema_map
from apps.chat.steps.recall_topup import (
    TopupSignals,
    record_topup_event,
    tables_from_clarify_card,
    topup_enabled_for,
)
from apps.chat.steps.stream import consume_llm  # noqa: F401
from apps.chat.task.llm import LLMService
from apps.conversation.models import ConversationInterrupt, QueryRun
from apps.conversation.outcome import (
    RunOutcome,
    failed_outcome,
)
from apps.conversation.run_service import (
    active_evidence,
    create_interrupt,
    finalize_run,
    load_prior_user_evidence,  # noqa: F401
    persist_query_clarification,
    persist_query_decision,
    require_active_run,
)
from apps.conversation.runtime_context import attach_runtime  # noqa: F401
from apps.conversation.session import session_scope
from apps.conversation.sink import StreamSink
from common.core.config import settings
from common.error import SingleMessageError
from common.utils.utils import SQLBotLogUtil


def _resolved_question_ids(evidence: list[Any]) -> set[str]:
    return {
        question_id_of(item.structured_value)
        for item in evidence
        if item.kind
        in {"clarification_option", "clarification_custom", "user_correction"}
        and question_id_of(item.structured_value)
    }


def _clarification_card_from_review(
    payload: dict[str, Any],
) -> ClarificationCard | None:
    try:
        return ClarificationCard.model_validate(payload)
    except Exception:
        return None


def _accepted_review_card(
    payload: dict[str, Any],
    evidence: list[Any],
    *,
    clarification_rounds: int,
) -> ClarificationCard | None:
    if clarification_rounds >= 2:
        return None
    card = _clarification_card_from_review(payload)
    if card is None:
        return None
    try:
        return enforce_clarification_policy(
            card, resolved_question_ids=_resolved_question_ids(evidence)
        )
    except ValueError:
        return None


def _planning_elapsed_for_state(*, interrupt: bool, elapsed: float) -> float:
    """Clarification ends this planning attempt; ready/repair continue the budget."""
    return 0.0 if interrupt else elapsed


def _planning_call_timeout_sec() -> float:
    """Per-call LLM timeout. Planning does not abort because wall-clock budget is spent."""
    return float(settings.LLM_REQUEST_TIMEOUT_SEC)


def _invoke_semantic_review(
    *,
    llm_service: LLMService,
    record_id: int,
    evidence: list[Any],
    plans: list[dict[str, Any]],
    fact_payloads: list[dict[str, Any]],
    risk_payload: dict[str, Any],
    compiled: Any,
    timeout_seconds: float,
    brief: str,
    prior_user_evidence: list[dict[str, Any]] | None = None,
    wiki_knowledge: str = "",
) -> tuple[dict[str, Any], float]:
    """Run high-risk semantic review. Returns (payload, elapsed_sec)."""
    with log_span(
        operate=OperationEnum.CLARIFY_INTENT,
        record_id=record_id,
        ai_modal_id=llm_service.chat_question.ai_modal_id,
        ai_modal_name=llm_service.chat_question.ai_modal_name,
        graph_node="semantic_review",
        title_key="chat.log.SEMANTIC_REVIEW",
        brief=brief,
    ) as review_span:
        reviewed = review_query_semantics(
            llm_service,
            evidence=evidence,
            plans=plans,
            plan_facts=fact_payloads,
            risk=risk_payload,
            relevant_knowledge=compiled,
            timeout_seconds=timeout_seconds,
            prior_user_evidence=prior_user_evidence or [],
            wiki_knowledge=wiki_knowledge,
        )
        review_payload = {
            **reviewed.review.model_dump(mode="json"),
            "reviewed_fingerprints": [plan_body_fingerprint(item) for item in plans],
        }
        review_span.set_usage(reviewed.usage)
        review_span["reasoning_content"] = reviewed.reasoning
        review_span.set_model_calls(reviewed.model_calls)
        review_span.set_detail({"risk": risk_payload, "review": review_payload})
        elapsed = sum(
            float(item.get("elapsed_ms") or 0) / 1000 for item in reviewed.model_calls
        )
    return review_payload, elapsed


def _plan_fact_models(
    plans: list[dict[str, Any]],
    *,
    dialect: str | None = None,
) -> tuple[PlanFacts, ...]:
    return tuple(
        extract_sql_plan_facts(str(plan.get("sql") or ""), dialect=dialect)
        if plan.get("sql")
        else PlanFacts(
            resources=tuple(str(item) for item in plan.get("tables") or []),
            parser_coverage="full",
        )
        for plan in plans
    )


def _classify_plan_risk(
    *,
    llm_service: Any,
    planning_context: Any,
    evidence: list[Any],
    facts: tuple[PlanFacts, ...],
) -> tuple[dict[str, Any], dict[str, Any]]:
    compiled = planning_context.compiled_knowledge or {}
    certified_relations = sum(
        1
        for item in compiled.get("relationships") or []
        if isinstance(item, dict)
        and (
            str(item.get("status") or "").casefold() == "confirmed"
            or float(item.get("confidence") or 0) >= 0.8
        )
    )
    risk = classify_query_risk(
        QueryRiskInput(
            facts=facts,
            schema_text=str(llm_service.chat_question.db_schema or ""),
            entity_bindings=planning_context.entity_bindings,
            temporal_evidence=planning_context.temporal_parse,
            evidence_kinds=tuple(item.kind for item in evidence),
            certified_relation_count=certified_relations,
            certified_knowledge=True,
        )
    )
    return risk.model_dump(mode="json"), compiled


def _prune_prompt_schema(
    llm_service: LLMService,
    planning_context: Any,
    state: NlqState,
) -> None:
    """澄清恢复轮把 prompt 呈现的 schema 收敛到确认表 ∪ SQL 引用表（呈现层）。

    快照 ``schema_text``/``resources``/``schema_fingerprint`` 一律不动——
    硬门禁、执行期 drift 重校验都锚定在快照上。只改写
    ``llm_service.chat_question.db_schema``（planner/reviewer/risk 共用的
    prompt 呈现），把与本轮无关的表段剔除，砍掉澄清后全量下发的主延迟。
    topup 扩窗在先（窗口超集安全），裁剪在后（呈现子集经济）。

    keep 的构成：evidence 确认的表（fields[].table）∪ SQL 已引用的表
    （plan_facts.tables）。无任何证据时不裁剪（宁多勿漏，门禁兜底）。
    """
    schema_text = str(planning_context.schema_text or "")
    if not schema_text:
        return
    resources = [str(t) for t in (planning_context.resources or [])]
    if not resources:
        return
    keep: set[str] = set()
    for item in state.get("prior_user_evidence") or []:
        if not isinstance(item, dict):
            continue
        structured = (
            item.get("structured_value")
            if isinstance(item.get("structured_value"), dict)
            else item
        )
        for ref in structured.get("fields") or []:
            if isinstance(ref, dict) and ref.get("table"):
                keep.add(str(ref["table"]))
        if structured.get("table"):
            keep.add(str(structured["table"]))
    for item in state.get("plan_facts") or []:
        if isinstance(item, dict):
            for t in item.get("tables") or []:
                keep.add(str(t))
    if not keep:
        return
    keep_casefold = {t.casefold() for t in keep}
    # schema 段按 "## <desc> (<table>)" 分块；db 直渲行带 "[db]" 后缀，
    # 正则允许任意尾注，否则 db 兜底块会被整块丢掉
    blocks: list[tuple[str, str]] = []
    current_table = ""
    current_lines: list[str] = []
    for line in schema_text.split("\n"):
        m = re.match(r"^## .*\(([^)]+)\)\s*(?:\[db\])?\s*$", line)
        if m:
            if current_table:
                blocks.append((current_table, "\n".join(current_lines)))
            current_table = m.group(1).strip()
            current_lines = [line]
        elif current_lines:
            current_lines.append(line)
    if current_table:
        blocks.append((current_table, "\n".join(current_lines)))
    kept = [body for table, body in blocks if table.casefold() in keep_casefold]
    if not kept or len(kept) == len(blocks):
        return
    llm_service.chat_question.db_schema = "\n".join(kept)
    SQLBotLogUtil.info(
        "replan prompt schema pruned: %d/%d blocks kept (keep=%s)",
        len(kept),
        len(blocks),
        sorted(keep),
    )


def _wiki_recall_summary(state: NlqState) -> dict[str, Any] | None:
    """wiki_context 召回遥测 → 执行详情摘要（detail.wiki_recall）。

    hits 上限 12 条（完整清单在 planning_context.wiki_context 快照，
    摘要只服务一眼可读）；无召回（wiki 后端关闭/零命中）返回 None——
    span detail 不加空块。"""
    wiki_context = state.get("wiki_context") or {}
    hits = wiki_context.get("wiki_hits") or []
    if not hits:
        return None
    return {
        "hit_count": len(hits),
        "hits": hits[:12],
        "elapsed_ms": wiki_context.get("wiki_recall_elapsed_ms"),
        "embedding_built": bool(wiki_context.get("wiki_embedding_built")),
        "source": wiki_context.get("wiki_recall_source"),
    }


def plan_query_node(state: NlqState) -> NlqState:
    """Generate compact plans and apply hard gates. High-risk review is the next node."""
    llm_service = _llm_service(state)
    sink = StreamSink.from_state(state)
    run_id = str(state["run_id"])
    record_id = int(llm_service.record.id)
    consumed_budget = float(state.get("planning_model_elapsed_sec") or 0.0)
    try:
        with session_scope() as session:
            run = require_active_run(session, run_id)
            query_run = session.get(QueryRun, run_id)
            if query_run is None:
                raise LookupError(f"Query run {run_id} not found")
            planning_context = restore_planning_context(
                llm_service,
                dict(query_run.planning_context or {}),
            )
            # 澄清恢复轮的 prompt 裁剪（仅呈现层）：快照 resources/fingerprint
            # 不动（门禁与指纹语义保持），只收敛下发 planner 的 schema_text。
            if state.get("planning_decision") == "replan":
                _prune_prompt_schema(llm_service, planning_context, state)
            evidence = active_evidence(session, run_id)
            clarification_rounds = len(
                session.exec(
                    select(ConversationInterrupt).where(
                        ConversationInterrupt.run_id == run_id,
                        ConversationInterrupt.status == "consumed",
                    )
                )
                .scalars()
                .all()
            )
            business_now_text = run.business_now.isoformat()
            business_timezone = run.timezone
            schema_map_text = ""
            knowledge_map_text = ""
            if topup_enabled_for(getattr(llm_service.ds, "id", None)):
                # Window complement only: tables already in the schema window
                # are noise here.
                schema_map_text = render_schema_map(
                    session,
                    ds=llm_service.ds,
                    access_scope=_access_scope(state),
                    exclude=frozenset(planning_context.resources or []),
                )
                oid, _map_ds_id = _ds_scope(llm_service)
                if oid is not None:
                    # wiki 命中页裁剪地图（prompt 版）；gate 校验走完整目录
                    _wc = state.get("wiki_context") or {}
                    _hit_keys = [
                        str(h.get("page_key") or "")
                        for h in (_wc.get("wiki_hits") or [])
                        if h.get("page_key")
                    ]
                    knowledge_map_text = render_knowledge_map(
                        session,
                        oid=int(oid),
                        ds_id=int(_map_ds_id or 0),
                        hit_keys=_hit_keys or None,
                        databases=_ds_databases(llm_service),
                    )
        with log_span(
            operate=OperationEnum.CLARIFY_INTENT,
            record_id=record_id,
            ai_modal_id=llm_service.chat_question.ai_modal_id,
            ai_modal_name=llm_service.chat_question.ai_modal_name,
            graph_node="plan_query",
            title_key="chat.log.PLAN_QUERY",
            brief="理解需求并生成查询",
        ) as span:
            try:
                result = run_query_agent(
                    llm_service,
                    evidence=evidence,
                    context={
                        "target_task": (state.get("turn_route") or {}).get("task_kind"),
                        "data_strategy": state.get("data_strategy"),
                        "entity_bindings": planning_context.entity_bindings,
                        "temporal_parse": planning_context.temporal_parse,
                        "resources": list(planning_context.resources),
                        "context_fingerprint": planning_context.fingerprint,
                        "business_now": business_now_text,
                        "timezone": business_timezone,
                        "schema_fingerprint": planning_context.schema_fingerprint,
                        "referenced_turns": state.get("referenced_turns") or [],
                        "prior_user_evidence": state.get("prior_user_evidence") or [],
                        "context_truncation": list(planning_context.truncation or []),
                        "certified_knowledge": planning_context.compiled_knowledge,
                        "schema_map": schema_map_text,
                        "knowledge_map": knowledge_map_text,
                        "recall_topup_notice": state.get("recall_topup_notice") or {},
                        "business_knowledge": str(
                            state.get("wiki_knowledge_text") or ""
                        ),
                    },
                    resolved_question_ids=_resolved_question_ids(evidence),
                    max_batch_size=state.get("max_batch_size") or _MAX_BATCH_SIZE,
                    timeout_seconds=_planning_call_timeout_sec(),
                    system_knowledge=str(state.get("wiki_knowledge_text") or ""),
                    on_stream=lambda chunk: sink.token(
                        content="",
                        reasoning_content=chunk.get("reasoning_content") or "",
                        event_type="clarification-reasoning",
                    ),
                )
            except QueryAgentError as exc:
                if exc.result is not None:
                    span.set_usage(exc.result.usage)
                    span["reasoning_content"] = exc.result.reasoning
                    span.set_model_calls(exc.result.model_calls)
                    span.set_detail({"decision": "failed", "error": str(exc)})
                raise
            span.set_usage(result.usage)
            span["reasoning_content"] = result.reasoning
            span.set_model_calls(result.model_calls)
            # wiki 召回摘要（detail.wiki_recall）：执行详情的结构化召回视图，
            # 替代人工读完整提示词——hits/耗时/嵌入构建一次采集多处消费。
            span.set_detail(
                {
                    "decision": result.decision.decision,
                    "plan_count": len(result.plans),
                    "wiki_recall": _wiki_recall_summary(state),
                }
            )
        planning_elapsed = consumed_budget + sum(
            float(item.get("elapsed_ms") or 0) / 1000 for item in result.model_calls
        )
        if isinstance(result.decision, NeedClarification):
            if clarification_rounds >= 2:
                raise SingleMessageError(
                    "经过两轮确认后仍存在影响结果的关键歧义，请补充更明确的业务口径后重新提问。"
                )
            with session_scope() as session:
                persist_query_clarification(
                    session,
                    run_id=run_id,
                    held_plans=None,
                )
            return {
                **state,
                "planning_decision": "clarify",
                "ambiguity_payload": {
                    **result.decision.as_card().model_dump(mode="json"),
                    # The plan gate resolves these concepts (knowledge units /
                    # catalog) before the interrupt reaches the user.
                    "missing_concepts": list(result.decision.missing_concepts),
                },
                "active_candidate": {},
                "planning_model_elapsed_sec": _planning_elapsed_for_state(
                    interrupt=True, elapsed=planning_elapsed
                ),
            }
        if isinstance(result.decision, QueryUnsupported):
            with session_scope() as session:
                persist_query_decision(
                    session,
                    run_id=run_id,
                    decision=result.decision.model_dump(mode="json"),
                    plans=[],
                    hard_gate_report={},
                    risk_assessment={},
                    plan_facts=[],
                    planning_status="unsupported",
                )
            return {
                **state,
                "planning_decision": "unsupported",
                "unsupported_payload": result.decision.model_dump(mode="json"),
                "active_candidate": {},
                "planning_model_elapsed_sec": planning_elapsed,
            }
        if not isinstance(result.decision, Ready) or not result.plans:
            raise SingleMessageError("Query Agent did not produce an executable plan")

        # Hard-gate evaluation loop: an evidence-driven working-set expansion
        # invalidates the recorded gate errors (the rejected table is now in
        # the window), so the same decision is re-validated against the
        # expanded schema once before any error text reaches the repair turn.
        plans = result.plans
        fact_models = _plan_fact_models(plans, dialect=_sql_dialect(llm_service))
        fact_payloads = [item.model_dump(mode="json") for item in fact_models]
        failed_gates: list[dict[str, Any]] = []
        for _gate_round in range(2):
            failed_gates = [
                {
                    "plan_id": plan.get("plan_id"),
                    "code": str(plan.get("hard_gate_code") or "PLAN_VALIDATION_FAILED"),
                    "errors": list(plan.get("hard_gate_errors") or []),
                }
                for plan in plans
                if plan.get("hard_gate_status") == "failed"
            ]
            if not failed_gates:
                break
            # ACCESS_POLICY_VIOLATION is fatal only for tables the resolver
            # cannot admit (hallucinated / out of scope): a map-visible table
            # outside the working set is a recall gap — expand, then re-run
            # the gates on the expanded window. Unconditionally-fatal codes
            # skip the expansion entirely (the run is dying; no schema writes).
            hard_fatal = any(
                item["code"] in {"NON_READ_ONLY_PLAN", "PROTOCOL_UNSUPPORTED"}
                for item in failed_gates
            )
            expansion = (
                _GateExpansion(frozenset(), False, False)
                if hard_fatal
                else _topup_on_failed_gates(state, llm_service, plans)
            )
            if hard_fatal or expansion.uncovered or expansion.undetermined:
                with session_scope() as session:
                    persist_query_decision(
                        session,
                        run_id=run_id,
                        decision=result.decision.model_dump(mode="json"),
                        plans=plans,
                        hard_gate_report={"status": "failed", "plans": failed_gates},
                        risk_assessment={},
                        plan_facts=fact_payloads,
                        planning_status="rejected",
                        repair_record={
                            "attempt": 0,
                            "reason": "hard_gate_failed",
                            "status": "failed",
                            "plan_ids": [item.get("plan_id") for item in plans],
                            "sql": [str(item.get("sql") or "") for item in plans],
                        },
                    )
                raise SingleMessageError("查询未通过安全、权限或协议门禁，已停止执行。")
            if not expansion.expanded:
                break
            # The window grew: restore the fresh snapshot for its fingerprint,
            # then re-validate the same decision against the expanded schema.
            fresh_context = planning_context
            with session_scope() as session:
                nlq_run = session.get(QueryRun, run_id)
                if nlq_run is not None:
                    try:
                        fresh_context = restore_planning_context(
                            llm_service, dict(nlq_run.planning_context or {})
                        )
                    except ValueError:
                        fresh_context = planning_context
            plans = revalidate_query_plans(
                llm_service,
                decision=result.decision,
                schema_fingerprint=str(fresh_context.schema_fingerprint or ""),
                max_batch_size=state.get("max_batch_size") or _MAX_BATCH_SIZE,
            )
            fact_models = _plan_fact_models(plans, dialect=_sql_dialect(llm_service))
            fact_payloads = [item.model_dump(mode="json") for item in fact_models]

        if failed_gates:
            with session_scope() as session:
                persist_query_decision(
                    session,
                    run_id=run_id,
                    decision=result.decision.model_dump(mode="json"),
                    plans=plans,
                    hard_gate_report={"status": "failed", "plans": failed_gates},
                    risk_assessment={},
                    plan_facts=fact_payloads,
                    planning_status="repairing",
                    repair_record={
                        "attempt": 0,
                        "reason": "hard_gate_failed",
                        "status": "failed",
                        "plan_ids": [item.get("plan_id") for item in plans],
                        "sql": [str(item.get("sql") or "") for item in plans],
                    },
                )
            repair_errors = [
                message for item in failed_gates for message in item.get("errors") or []
            ]
            # The rejection→repair transition is a real planning decision;
            # surface it as its own audit step instead of letting the panel
            # jump from "生成查询" to "修复查询语句" with no visible cause.
            with log_span(
                operate=OperationEnum.CLARIFY_INTENT,
                record_id=record_id,
                local_operation=True,
                graph_node="plan_query",
                title_key="chat.log.PLAN_REJECTED",
                brief="物理校验未通过，转入修复",
            ) as gate_span:
                gate_span.set_detail({"failures": failed_gates})
            return {
                **state,
                "planning_decision": "ready",
                "active_candidate": {},
                "repair_source_plans": plans,
                "repair_hint": _plan_repair_message("\n".join(repair_errors)),
                "gen_attempts": 0,
                "plan_facts": fact_payloads,
                "planning_model_elapsed_sec": planning_elapsed,
            }
        dialect = _sql_dialect(llm_service)
        if apply_grouped_metric_order(plans, dialect=dialect):
            fact_models = _plan_fact_models(plans, dialect=dialect)
            fact_payloads = [item.model_dump(mode="json") for item in fact_models]
        with session_scope() as session:
            persist_query_decision(
                session,
                run_id=run_id,
                decision=result.decision.model_dump(mode="json"),
                plans=plans,
                hard_gate_report={
                    "status": "passed",
                    "plan_count": len(plans),
                },
                risk_assessment={},
                plan_facts=fact_payloads,
                planning_status="reviewing",
            )
        return {
            **state,
            "planning_decision": "ready",
            "active_candidate": {
                "plans": plans,
                "plan_validated": True,
                "semantic_status": "partial",
            },
            "gen_attempts": 0,
            "repair_hint": "",
            "plan_facts": fact_payloads,
            "planning_model_elapsed_sec": planning_elapsed,
        }
    except QueryAgentError as exc:
        elapsed = consumed_budget
        if exc.result is not None:
            elapsed += sum(
                float(item.get("elapsed_ms") or 0) / 1000
                for item in exc.result.model_calls
            )
        return _fail(
            {**state, "planning_model_elapsed_sec": elapsed},
            record_id,
            exc,
        )
    except Exception as exc:
        return _fail(state, record_id, exc)


def _persist_query_terminal_failure(
    state: NlqState,
    *,
    error_summary: str,
    public_error: str | None,
    current_node: str | None = None,
    failure_code: str | None = None,
    failure_retryable: bool = True,
    outcome: RunOutcome | None = None,
) -> RunOutcome:
    """Persist one canonical failed query answer at every terminal boundary.

    The graph owns *why* a query cannot proceed; this helper owns the durable
    query-answer projection, quality fallback, and lifecycle finalization.  A
    caller providing ``public_error`` has already crossed the user-facing
    error boundary, so ``finalize_run`` must not sanitize it a second time.
    """
    terminal_outcome = outcome or failed_outcome(error_summary)
    if "quality" not in terminal_outcome:
        terminal_outcome["quality"] = build_overall_quality([])
    try:
        with session_scope() as session:
            finalize_run(
                session,
                run_id=str(state["run_id"]),
                status="failed",
                current_node=current_node,
                result_quality=terminal_outcome.get("quality"),
                record_snapshot=_record_snapshot_values(
                    [],
                    "",
                    finish=True,
                    outcome=terminal_outcome,
                    public_error=public_error,
                    failure_code=failure_code,
                    failure_retryable=failure_retryable,
                    execution_mode=cast(
                        Literal["verified", "unverified"],
                        state.get("execution_mode") or "verified",
                    ),
                ),
                error_summary=error_summary,
                error_visibility="public" if public_error is not None else "sanitize",
            )
    except Exception as exc:
        SQLBotLogUtil.error(f"persist NLQ failure snapshot failed: {exc}")
    return terminal_outcome


def unsupported_query_node(state: NlqState) -> NlqState:
    """Publish a first-class terminal answer when Query Agent reports unsupported."""
    payload = dict(state.get("unsupported_payload") or {})
    message = str(payload.get("message") or "当前问题无法由已选择的数据源回答。")
    reason_code = (
        str(payload.get("reason_code") or "QUERY_NOT_SUPPORTED").strip().upper()
        or "QUERY_NOT_SUPPORTED"
    )
    outcome = _persist_query_terminal_failure(
        state,
        error_summary=message,
        public_error=message,
        current_node="unsupported_query",
        failure_code=reason_code,
        failure_retryable=True,
    )
    sink = StreamSink.from_state(state)
    sink.error(message)
    sink.event({"type": "finish", "id": state.get("record_id")})
    return {**state, "outcome": outcome}


def review_query_node(state: NlqState) -> NlqState:
    """Review high-risk plans without re-running Query Agent."""
    llm_service = _llm_service(state)
    run_id = str(state["run_id"])
    record_id = int(llm_service.record.id)
    plans = list((state.get("active_candidate") or {}).get("plans") or [])
    planning_elapsed = float(state.get("planning_model_elapsed_sec") or 0.0)
    try:
        with session_scope() as session:
            require_active_run(session, run_id)
            query_run = session.get(QueryRun, run_id)
            if query_run is None:
                raise LookupError(f"Query run {run_id} not found")
            planning_context = restore_planning_context(
                llm_service,
                dict(query_run.planning_context or {}),
            )
            evidence = active_evidence(session, run_id)
            clarification_rounds = len(
                session.exec(
                    select(ConversationInterrupt).where(
                        ConversationInterrupt.run_id == run_id,
                        ConversationInterrupt.status == "consumed",
                    )
                )
                .scalars()
                .all()
            )
            agent_decision = dict(query_run.agent_decision or {})
            if not plans:
                plans = [
                    dict(item)
                    for item in (query_run.plans or [])
                    if item.get("plan_id")
                ]
        if not plans:
            raise SingleMessageError("Query Agent did not produce an executable plan")
        dialect = _sql_dialect(llm_service)
        apply_grouped_metric_order(plans, dialect=dialect)
        fact_models = _plan_fact_models(plans, dialect=dialect)
        fact_payloads = [item.model_dump(mode="json") for item in fact_models]
        risk_payload, compiled = _classify_plan_risk(
            llm_service=llm_service,
            planning_context=planning_context,
            evidence=evidence,
            facts=fact_models,
        )
        review_payload: dict[str, Any] = {}
        if risk_payload.get("level") == "high":
            try:
                review_payload, review_elapsed = _invoke_semantic_review(
                    llm_service=llm_service,
                    record_id=record_id,
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
                }
            verdict = str(review_payload.get("verdict") or "uncertain")
            if verdict == "repair":
                hint = "\n".join(
                    str(item.get("message") or "")
                    for item in review_payload.get("issues") or []
                )
                with session_scope() as session:
                    persist_query_decision(
                        session,
                        run_id=run_id,
                        decision=agent_decision,
                        plans=plans,
                        hard_gate_report={
                            "status": "passed",
                            "plan_count": len(plans),
                        },
                        risk_assessment=risk_payload,
                        plan_facts=fact_payloads,
                        semantic_review=review_payload,
                        planning_status="repairing",
                    )
                return {
                    **state,
                    "planning_decision": "ready",
                    "active_candidate": {},
                    "repair_source_plans": plans,
                    "repair_hint": hint or "语义复核要求修复物理查询计划",
                    "gen_attempts": 0,
                    "quality_cap": 69,
                    "execution_mode": "unverified",
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
                            run_id=run_id,
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
                            run_id=run_id,
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
            if verdict == "uncertain":
                state = {**state, "quality_cap": 69, "execution_mode": "unverified"}
        with session_scope() as session:
            persist_query_decision(
                session,
                run_id=run_id,
                decision=agent_decision,
                plans=plans,
                hard_gate_report={"status": "passed", "plan_count": len(plans)},
                risk_assessment=risk_payload,
                plan_facts=fact_payloads,
                semantic_review=review_payload or None,
                planning_status="ready",
            )
        return {
            **state,
            "planning_decision": "ready",
            "active_candidate": {
                "plans": plans,
                "plan_validated": True,
                "semantic_status": (
                    "verified"
                    if risk_payload.get("level") == "low"
                    or review_payload.get("verdict") == "pass"
                    else "partial"
                ),
            },
            "gen_attempts": 0,
            "repair_hint": "",
            "risk_assessment": risk_payload,
            "semantic_review": review_payload,
            "plan_facts": fact_payloads,
            "planning_model_elapsed_sec": planning_elapsed,
        }
    except Exception as exc:
        return _fail(state, record_id, exc)


def await_clarification_node(state: NlqState) -> NlqState:
    """Durably pause and resume this same graph run and ChatRecord."""
    run_id = str(state["run_id"])
    payload = dict(state.get("ambiguity_payload") or {})
    with session_scope() as session:
        pending = create_interrupt(session, run_id=run_id, payload=payload)
    public = {
        "interrupt_id": pending.interrupt_id,
        "version": pending.version,
        **payload,
    }
    if pending.status == "open":
        StreamSink.from_state(state).awaiting_input(public)
    interrupt(public)
    return {
        **state,
        "planning_decision": "replan",
        "ambiguity_payload": {},
    }


def _ready_entity_coverage_lint(state: NlqState) -> dict[str, Any] | None:
    """Advisory lint: value-index hits whose tables the plans never touch."""
    notice = state.get("recall_topup_notice") or {}
    hits = notice.get("value_hits") or []
    if not hits:
        return None
    hit_tables = {str(item.get("table")) for item in hits if item.get("table")}
    plan_tables: set[str] = set()
    candidate = state.get("active_candidate") or {}
    for plan in candidate.get("plans") or []:
        for name in plan.get("tables") or []:
            plan_tables.add(str(name))
    uncovered = sorted(hit_tables - plan_tables)
    if not uncovered:
        return None
    return {
        "lint": "entity_coverage",
        "severity": "advisory",
        "uncovered_tables": uncovered,
        "value_hits": hits,
    }


def plan_gate_node(state: NlqState) -> NlqState:
    """Deterministic gate on terminal planning decisions (no LLM).

    A terminal negative (unsupported) is only allowed to stand when every
    claimed missing concept was searched — map lexicon, value index, knowledge
    index — and found nowhere. A resolvable concept means the negative was
    premature: expand the working set, persist the snapshot (plan_query
    restores from it on every entry), and bounce once into plan_query. Clarify
    cards whose options name tables outside the working set expand the same
    way. ``ready`` gets an advisory entity-coverage lint only. When the gate
    passes through, routing semantics are exactly the legacy router's.
    """
    state = {**state, "plan_gate_route": ""}
    decision = state.get("planning_decision")
    if state.get("error") or decision not in {"clarify", "unsupported", "ready"}:
        return state
    bounce_count = int(state.get("topup_bounce_count") or 0)
    llm_service = _llm_service(state)
    if not topup_enabled_for(getattr(llm_service.ds, "id", None)):
        return state

    if decision == "ready":
        # Repair-path ready states carry no accepted plans yet — the entity
        # coverage lint only makes sense against an accepted candidate.
        if not (state.get("repair_hint") or "").strip():
            lint = _ready_entity_coverage_lint(state)
            if lint is not None:
                with session_scope() as session:
                    record_topup_event(session, str(state["run_id"]), lint)
                SQLBotLogUtil.info(
                    "plan gate advisory lint (entity coverage): %s",
                    lint["uncovered_tables"],
                )
        return state
    if bounce_count > 0:
        return state

    signals = TopupSignals(question_text=str(llm_service.retrieval_question or ""))
    force_bounce_hint = ""
    if decision == "unsupported":
        payload = dict(state.get("unsupported_payload") or {})
        concepts = tuple(
            str(item).strip()
            for item in payload.get("missing_concepts") or []
            if str(item).strip()
        )
        if not concepts:
            # Protocol gap: a first-attempt unsupported must name its missing
            # concepts, otherwise the negative is unverifiable.
            force_bounce_hint = (
                "上一次 unsupported 未列出缺失概念。必须在 missing_concepts 中"
                "用业务语言列出你认定数据源缺失的每个概念后再下结论。"
            )
        else:
            signals = TopupSignals(
                question_text=str(llm_service.retrieval_question or ""),
                missing_concepts=concepts,
            )
    else:
        card = state.get("ambiguity_payload") or {}
        working = {str(name) for name in (llm_service.table_name_list or [])}
        outside = tuple(
            name for name in tables_from_clarify_card(card) if name not in working
        )
        concepts = tuple(
            str(item).strip()
            for item in (card.get("missing_concepts") or [])
            if str(item).strip()
        )
        if not outside and not concepts:
            return state
        signals = TopupSignals(
            question_text=str(llm_service.retrieval_question or ""),
            evidence_tables=outside,
            missing_concepts=concepts,
        )

    run_id = str(state["run_id"])
    if force_bounce_hint:
        notice: dict[str, Any] = {
            "source": "plan_gate",
            "reason": "missing_concepts_empty",
            "hint": force_bounce_hint,
        }
        with session_scope() as session:
            record_topup_event(
                session,
                run_id,
                {"source": "plan_gate", "reason": "missing_concepts_empty"},
            )
    else:
        run = _run_topup(
            state,
            llm_service,
            signals=signals,
            source="plan_gate",
            graph_node="plan_gate",
        )
        if not run.changed:
            if decision == "unsupported":
                # Legitimate negative: attach the verified misses so the
                # terminal answer is evidence-backed.
                payload = dict(state.get("unsupported_payload") or {})
                payload["verified_missing"] = list(run.manifest.misses)
                with session_scope() as session:
                    record_topup_event(
                        session,
                        run_id,
                        {
                            "source": "plan_gate",
                            "reason": "verified_negative",
                            "verified_missing": list(run.manifest.misses),
                        },
                    )
                return {
                    **state,
                    "wiki_context": run.wiki_context,
                    "unsupported_payload": payload,
                }
            return {**state, "wiki_context": run.wiki_context}
        notice = {
            **run.notice,
            "reason": "premature_negative_expanded"
            if decision == "unsupported"
            else "clarify_expanded",
            "hint": (
                "系统已按你声明的缺失概念扩展了 schema 检索窗口"
                "（见新增表/知识单元与值证据），请基于完整上下文重新决策。"
            ),
        }
    bounce_state = {
        **state,
        "topup_bounce_count": bounce_count + 1,
        "recall_topup_notice": notice,
        "plan_gate_route": "plan_query",
    }
    if not force_bounce_hint:
        # force_bounce_hint 分支未跑 topup,没有 run.wiki_context 可回传
        bounce_state["wiki_context"] = run.wiki_context
        # 扩窗后重拉 wiki 业务段：topup 可能带入新表，扩窗前的业务语义段
        # 不覆盖新窗口——对齐 retrieve_context replan 分支的时序先例。
        _oid_b, _ds_b = _ds_scope(llm_service)
        fresh_wiki = _wiki_business_text_safely(
            str(getattr(llm_service, "retrieval_question", "") or ""),
            ds_id=_ds_b,
            databases=_ds_databases(llm_service),
        )
        if fresh_wiki:
            bounce_state["wiki_knowledge_text"] = fresh_wiki
            bounce_state["wiki_context"] = {
                **bounce_state["wiki_context"],
                "business_recall_source": "gate_bounce_refresh",
                "business_text_chars": len(fresh_wiki),
            }
    return bounce_state


def _plan_repair_message(refusal: str) -> str:
    """Shared plan-time repair text (validate / empty-plan). Schema-general, not ds-specific."""
    base = (refusal or "").strip() or "未能得到可执行 SQL 计划"
    # Catalog hints can be verbose. The full failure remains in server logs and
    # the record error; retry context should stay focused so the model edits the
    # previous SQL instead of reopening a long design monologue.
    if len(base) > 1600:
        base = base[:1600].rstrip() + "…"
    parts = [
        "【物理计划校验失败 — 固定用户证据修复】",
        base,
        "只能改正标识符、方言或请求结构；不得改变用户业务要求。",
        "返回协议原生 JSON，不要解释。",
    ]
    return chr(10).join(parts) + chr(10)
