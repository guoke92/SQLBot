"""NLQ node implementations — reviewed batch loop.

Topology: generate_queries → execute_queries → decide_next
  → (repair loop | generate_charts → summarize_answer → complete)

Each iteration plans and executes 1~N candidate queries. Candidate plans,
results remain private until ``decide_next`` moves the complete candidate into
``accepted_candidate``. Only then are charts and summary generated. Rejected
attempts remain available to observability and the next generation round, but
never become answer cards.
Loop and batch limits are defined only in ``apps.chat.plan_policy``.

SSE result cards are hydrated only from the terminal accepted snapshot.
The accepted candidate is projected to ``TurnAnswerV1`` at completion::

    {
        "steps": [{"sql","chart","data","brief","error"?}, ...],
        "analysis": "...",
        "outcome": {"status","quality",...},
    }
"""

from __future__ import annotations

import re
import traceback
from collections.abc import Mapping
from concurrent.futures import as_completed
from copy import deepcopy
from typing import Any, Literal, TypedDict, cast

import orjson
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.types import interrupt
from sqlalchemy import select
from sqlbot_xpack.custom_prompt.models.custom_prompt_model import CustomPromptTypeEnum

from apps.chat.aggregation_window import (
    aggregation_totals_sql,
    apply_grouped_metric_order,
)
from apps.chat.binding_resolver import (
    binding_resource_names,
    resolve_entity_bindings,
    retain_binding_resources,
)
from apps.chat.constants import DYNAMIC_DS_TYPES
from apps.chat.context_bundle import choose_data_strategy, context_fingerprint
from apps.chat.curd.chat import rename_chat
from apps.chat.models.chat_model import (
    ChatFinishStep,
    ChatRecord,
    OperationEnum,
    RenameChat,
)
from apps.chat.plan_facts import PlanFacts, extract_sql_plan_facts, sqlglot_dialect_for
from apps.chat.plan_policy import (
    MAX_BATCH_ROUNDS,
    MAX_PLAN_REGEN,
    MAX_QUERIES_PER_BATCH,
    ROW_LIMIT,
)
from apps.chat.planning import parse_query_generation
from apps.chat.planning_context import (
    capture_planning_context,
    execution_schema_resources,
    restore_planning_context,
)
from apps.chat.presentation import (
    ResultPresentation,
    build_result_presentation,
    chart_columns,
)
from apps.chat.query_risk import QueryRiskInput, classify_query_risk
from apps.chat.result_data import format_json_data
from apps.chat.result_quality import (
    CompletionEvidence,
    ExecutionStatus,
    build_overall_quality,
    build_step_quality,
    cap_quality,
)
from apps.chat.result_semantics import (
    apply_display_window,
    classify_field_roles,
    read_result_window,
)
from apps.chat.result_validation import (
    ResultValidationReport,
    validate_result_structure,
    validation_issue_prompt_text,
)
from apps.chat.semantic_planning import (
    ClarificationCard,
    NeedClarification,
    QueryUnsupported,
    Ready,
    enforce_clarification_policy,
    question_id_of,
)
from apps.chat.steps.chart import generate_chart
from apps.chat.steps.custom_prompt import match_custom_prompts
from apps.chat.steps.datasource import select_datasource, validate_history_ds
from apps.chat.steps.knowledge import get_compiled_knowledge, match_knowledge
from apps.chat.steps.observability import log_span
from apps.chat.steps.permissions import (
    DYNAMIC_SUBSQL_PREFIX,
    generate_assistant_dynamic_sql,
    generate_filter,
)
from apps.chat.steps.persist import parse_chart
from apps.chat.steps.query_agent import (
    QueryAgentError,
    plan_body_fingerprint,
    repair_physical_plans,
    review_query_semantics,
    run_query_agent,
)
from apps.chat.steps.schema import match_table_schema
from apps.chat.steps.stream import consume_llm
from apps.chat.steps.turn_agents import run_turn_agent
from apps.chat.task.llm import LLMService, request_picture
from apps.chat.time_intent import TemporalParse, infer_time_intent
from apps.chat.turn_contracts import TurnRoute
from apps.chat.turn_router import route_turn
from apps.conversation.messages import message_content_text
from apps.conversation.models import ConversationInterrupt, ConversationRun, QueryRun
from apps.conversation.outcome import (
    ResultQuality,
    RunOutcome,
    classify_failure,
    failed_outcome,
    format_error_message,
    outcome_from_steps,
    outcome_is_success,
    public_error_message,
    running_outcome,
    successful_outcome,
)
from apps.conversation.run_service import (
    ConversationRunCancelled,
    active_evidence,
    create_interrupt,
    finalize_run,
    load_prior_user_evidence,
    load_query_plan_result,
    persist_query_clarification,
    persist_query_decision,
    persist_query_plan_failure,
    persist_query_plan_result,
    register_query_plans,
    require_active_run,
)
from apps.conversation.runtime import submit_query
from apps.conversation.runtime_context import attach_runtime, runtime_value
from apps.conversation.session import session_scope
from apps.conversation.sink import StreamSink
from apps.conversation.state import RunState
from apps.conversation.usage import usage_from_response
from apps.datasource.access import (
    AccessScope,
    access_scope_fingerprint,
    resolve_access_scope,
)
from apps.datasource.crud.permission import is_normal_user
from apps.datasource.models.datasource import CoreDatasource
from apps.knowledge.compile import matched_revision_ids, seed_revisions_for_turn
from apps.knowledge.compile.bundle import ApplyHit
from apps.protocol import QueryPlan
from apps.protocol.base import CAP_ROW_PERMISSION
from common.core.config import settings
from common.error import SingleMessageError, SQLBotDBConnectionError
from common.utils.data_format import DataFormat
from common.utils.json_utils import extract_nested_json
from common.utils.utils import SQLBotLogUtil, prepare_for_orjson

# ── Constants ────────────────────────────────────────────────────────────────

_MAX_STEPS = MAX_BATCH_ROUNDS
_MAX_BATCH_SIZE = MAX_QUERIES_PER_BATCH
_ROW_LIMIT = ROW_LIMIT

# Match YYYY-MM or YYYY-MM-DD (with - or / separators).  Used by _column_stats
# to detect temporal string columns for min/max computation.
_TEMPORAL_RE = re.compile(r"^\d{4}[-/]\d{1,2}([-/]\d{1,2})?$")


# ── State ────────────────────────────────────────────────────────────────────


class CandidateBatch(TypedDict, total=False):
    """One plan batch through planning, execution, review and publication."""

    plans: list[dict[str, Any]]
    results: list[dict[str, Any]]
    charts: list[dict[str, Any]]
    steps: list[dict[str, Any]]
    quality: ResultQuality
    outcome: RunOutcome
    plan_validated: bool
    semantic_status: Literal["verified", "partial", "unsupported"]


class NlqState(RunState, total=False):
    """Agentic batch loop state.

    This is the canonical state contract for the production chat graph.
    """

    finish_step: int
    return_img: bool
    turn_route: dict[str, Any]
    referenced_turns: list[dict[str, Any]]
    prior_user_evidence: list[dict[str, Any]]
    source_datasets: list[dict[str, Any]]
    data_strategy: Literal[
        "direct_query", "existing_results", "derived_query", "unavailable"
    ]
    business_now: str
    timezone: str
    context_fingerprint: str
    terminal_answer: dict[str, Any]
    execution_mode: Literal["verified", "unverified"]
    quality_cap: int
    risk_assessment: dict[str, Any]
    semantic_review: dict[str, Any]
    plan_facts: list[dict[str, Any]]
    planning_model_elapsed_sec: float
    json_result: dict[str, Any]

    # batch loop
    step_index: int  # current batch iteration (0-based)
    active_candidate: CandidateBatch
    repair_source_plans: list[dict[str, Any]]
    # Candidates move atomically between these lifecycle slots. Individual
    # plans/results/charts are never published or combined across candidates.
    rejected_candidate: CandidateBatch | None
    accepted_candidate: CandidateBatch | None
    analysis_text: str
    max_steps: int
    max_batch_size: int
    decision: str
    decision_reason: str
    repair_hint: str  # plan-validate or execute-quality rewrite brief
    gen_attempts: int  # plan-time generate→validate failures in current slot
    entity_bindings: dict[str, Any]  # NL phrase → canonical dimension values
    knowledge_matches: list[dict[str, Any]]
    compiled_knowledge: dict[str, Any]  # BusinessDataBundle dump; Bind/apply_log
    temporal_parse: TemporalParse  # deterministic evidence; never executable truth
    planning_decision: Literal["pending", "clarify", "ready", "replan"]
    ambiguity_payload: dict[str, Any]
    outcome: RunOutcome


# ── Helpers ──────────────────────────────────────────────────────────────────


def _llm_service(state: NlqState) -> LLMService:
    return cast(LLMService, runtime_value(state, "llm_service"))


def _merge_compiled_apply_log(
    llm_service: LLMService,
    additions: list[ApplyHit],
) -> dict[str, Any]:
    compiled = get_compiled_knowledge(llm_service)
    if compiled is None:
        return {}
    merged = list(compiled.apply_log)
    identities = {
        orjson.dumps(item.model_dump(mode="json"), option=orjson.OPT_SORT_KEYS)
        for item in merged
    }
    for item in additions:
        identity = orjson.dumps(
            item.model_dump(mode="json"),
            option=orjson.OPT_SORT_KEYS,
        )
        if identity not in identities:
            identities.add(identity)
            merged.append(item)
    compiled = compiled.model_copy(update={"apply_log": merged})
    llm_service.compiled_knowledge = compiled
    return compiled.model_dump(mode="json")


def _record_intent_default_application(
    llm_service: LLMService,
    applied_ids: list[int],
    *,
    unverified: bool = False,
) -> dict[str, Any]:
    """Turn recalled calibers into truthful Bind/Drop audit facts."""
    compiled = get_compiled_knowledge(llm_service)
    if compiled is None:
        return {}
    applied = set(applied_ids)
    additions = [
        ApplyHit(
            asset_kind="caliber",
            asset_id=str(item.get("caliber_id") or "") or None,
            lineage_id=str(item.get("caliber_id") or None),
            trust_tier="published",
            apply="bind" if item.get("caliber_id") in applied else "drop",
            reason=(
                "intent_default_applied"
                if item.get("caliber_id") in applied
                else "intent_unverified"
                if unverified
                else "intent_default_not_applicable"
            ),
        )
        for item in compiled.calibers
        if isinstance(item, dict)
    ]
    return _merge_compiled_apply_log(llm_service, additions)


def _access_scope(state: NlqState) -> AccessScope | None:
    return cast(AccessScope | None, runtime_value(state, "access_scope"))


def _query_plan(plan_dict: dict[str, Any]) -> QueryPlan:
    return QueryPlan(
        success=True,
        statement=str(plan_dict.get("format_statement") or plan_dict.get("sql") or ""),
        payload=dict(plan_dict.get("payload") or {"sql": plan_dict.get("sql") or ""}),
        resources=list(plan_dict.get("tables") or []),
        chart_type=str(plan_dict.get("chart_type") or "table"),
        brief=str(plan_dict.get("brief") or ""),
        message=plan_dict.get("message"),
    )


def _serialized_plan(plan: QueryPlan, base: dict[str, Any]) -> dict[str, Any]:
    return {
        **base,
        "sql": plan.payload.get("sql", plan.statement),
        "format_statement": plan.statement,
        "payload": dict(plan.payload or {}),
        "tables": list(plan.resources or []),
        "chart_type": plan.chart_type or base.get("chart_type") or "table",
        "brief": plan.brief or base.get("brief") or "",
        "message": plan.message,
    }


def _ds_scope(llm_service: LLMService) -> tuple[int | None, int | None]:
    if not llm_service.ds:
        return None, None
    oid = llm_service.ds.oid if isinstance(llm_service.ds, CoreDatasource) else 1
    ds_id = llm_service.ds.id if isinstance(llm_service.ds, CoreDatasource) else None
    return oid, ds_id


def _enqueue_knowledge_capture(
    state: NlqState,
    llm_service: LLMService,
    outcome: RunOutcome,
    steps: list[dict[str, Any]],
) -> None:
    """Persist a capture job; the process worker drains it asynchronously."""
    risk = dict(state.get("risk_assessment") or {})
    review = dict(state.get("semantic_review") or {})
    verified = risk.get("level") == "low" or review.get("verdict") == "pass"
    if state.get("execution_mode") == "unverified" or not verified:
        return
    from apps.chat.steps.scope import match_scope
    from apps.knowledge.capture import (
        build_turn_snapshot,
        enqueue_capture_job,
        schedule_capture_worker_kick,
    )

    # Same scope as Compile — do not force oid=1 / drop assistant via _ds_scope alone.
    calculate_oid, calculate_ds_id, assistant_id = match_scope(
        llm_service, *_ds_scope(llm_service)
    )
    compiled = state.get("compiled_knowledge") or {}
    apply_log = []
    if isinstance(compiled, dict):
        apply_log = list(compiled.get("apply_log") or [])
    sql_list = [
        str(step.get("sql") or "")
        for step in steps
        if step.get("sql") and not step.get("error")
    ]
    with session_scope() as evidence_session:
        evidence = active_evidence(evidence_session, str(state["run_id"]))
    resolutions = [
        {
            "evidence_id": item.evidence_id,
            "question": str(
                (item.structured_value or {}).get("question")
                or (item.structured_value or {}).get("business_question")
                or ""
            ),
            "meaning": str((item.structured_value or {}).get("meaning") or ""),
            "resolution": item.structured_value or {},
            "answer": item.content,
        }
        for item in evidence
        if item.kind
        in {"clarification_option", "clarification_custom", "user_correction"}
    ]
    snapshot = build_turn_snapshot(
        record_id=int(llm_service.record.id),
        oid=int(calculate_oid or 1),
        ds_id=calculate_ds_id if assistant_id is None else None,
        question=_generation_question(llm_service),
        risk_assessment=risk,
        semantic_review=review,
        plan_facts=list(state.get("plan_facts") or []),
        clarification_resolutions=resolutions,
        outcome=str(outcome.get("status") or "success"),
        knowledge_apply=apply_log,
        sql_list=sql_list,
        chat_id=getattr(llm_service.record, "chat_id", None),
        entity_bindings=state.get("entity_bindings") or {},
        assistant_id=assistant_id,
    )
    with session_scope() as session:
        enqueue_capture_job(session, snapshot=snapshot)
        session.commit()
    schedule_capture_worker_kick()


def _generation_question(llm_service: Any) -> str:
    """Read the canonical user request from real or lightweight services."""
    projected = str(getattr(llm_service, "generation_question", "") or "").strip()
    if projected:
        return projected
    question = getattr(llm_service, "chat_question", None)
    return str(
        getattr(question, "generation_question", "")
        or getattr(question, "question", "")
        or ""
    ).strip()


def _fail(state: NlqState, _record_id: int | None, exc: BaseException) -> NlqState:
    # This is an internal ownership fence, not a query failure.  Re-raising lets
    # the graph runtime stop a late worker without routing it through the fail
    # node or publishing a second terminal outcome.
    if isinstance(exc, ConversationRunCancelled):
        raise exc
    traceback.print_exc()
    error_msg = format_error_message(exc)
    return {
        **state,
        "error": error_msg,
        "public_error": public_error_message(exc),
        "outcome": failed_outcome(exc),
    }


def _finish_step_value(state: NlqState) -> int:
    fs = state.get("finish_step") or ChatFinishStep.GENERATE_CHART
    try:
        return int(fs.value if hasattr(fs, "value") else fs)
    except Exception:
        return int(ChatFinishStep.GENERATE_CHART.value)


def _result_rows(step: dict[str, Any]) -> list[dict[str, Any]]:
    result = step.get("result") or {}
    rows = result.get("data") if isinstance(result, dict) else None
    return rows if isinstance(rows, list) else []


def _result_fields(step: dict[str, Any]) -> list[str]:
    result = step.get("result") or {}
    fields = result.get("fields") if isinstance(result, dict) else None
    if isinstance(fields, list) and fields:
        return [str(f) for f in fields]
    rows = _result_rows(step)
    if rows and isinstance(rows[0], dict):
        return [str(k) for k in rows[0].keys()]
    return []


# ── Shared row-scan primitives ────────────────────────────────────────────


def _scan_field(rows: list[dict[str, Any]], field: str) -> dict[str, Any]:
    """Single row scan returning null_count, values (non-null), numeric_vals."""
    values: list[Any] = []
    numeric_vals: list[float] = []
    null_count = 0
    for r in rows:
        if not isinstance(r, dict):
            null_count += 1
            continue
        v = r.get(field)
        if v is None or v == "":
            null_count += 1
            continue
        values.append(v)
        if isinstance(v, bool):
            continue
        if isinstance(v, int | float):
            numeric_vals.append(float(v))
        else:
            try:
                if str(v).strip() != "":
                    numeric_vals.append(float(v))
            except Exception:
                pass
    return {
        "null_count": null_count,
        "values": values,
        "numeric_vals": numeric_vals,
    }


def _null_rate(rows: list[dict[str, Any]], field: str) -> float:
    if not rows:
        return 0.0
    scan = _scan_field(rows, field)
    return scan["null_count"] / max(len(rows), 1)


def _metric_stats(rows: list[dict[str, Any]], field: str) -> dict[str, Any]:
    scan = _scan_field(rows, field)
    vals = scan["numeric_vals"]
    if not vals:
        return {"count": 0}
    return {
        "count": len(vals),
        "sum": sum(vals),
        "min": min(vals),
        "max": max(vals),
    }


def _column_stats(rows: list[dict[str, Any]], field: str) -> dict[str, Any]:
    """Per-column statistical summary for LLM analysis context.

    Shares scan primitives with _null_rate / _metric_stats.
    Temporal: min/max for YYYY-MM / YYYY-MM-DD strings.
    Numeric: min/max/avg/median.  Categorical: unique + top-N.
    """
    if not rows:
        return {"unique": 0, "null_count": 0}
    scan = _scan_field(rows, field)
    values = scan["values"]
    numeric_vals = scan["numeric_vals"]
    if not values:
        return {"unique": 0, "null_count": scan["null_count"]}

    unique_count = len({str(v) for v in values})
    stats: dict[str, Any] = {"unique": unique_count, "null_count": scan["null_count"]}

    # Temporal: string dates (YYYY-MM / YYYY-MM-DD) — sort for min/max so the
    # LLM gets the true time span instead of guessing from top-N frequency.
    if not numeric_vals:
        str_vals = [str(v).strip() for v in values if v is not None and str(v).strip()]
        temporal_vals = [v for v in str_vals if _TEMPORAL_RE.match(v)]
        if temporal_vals and len(temporal_vals) >= len(str_vals) * 0.5:
            temporal_vals.sort()
            stats.update(
                {
                    "type": "temporal",
                    "min": temporal_vals[0],
                    "max": temporal_vals[-1],
                }
            )
            return stats

    if numeric_vals and len(numeric_vals) >= len(values) * 0.5:
        numeric_vals.sort()
        mid = len(numeric_vals) // 2
        median = (
            numeric_vals[mid]
            if len(numeric_vals) % 2
            else (numeric_vals[mid - 1] + numeric_vals[mid]) / 2
        )
        stats.update(
            {
                "type": "numeric",
                "min": numeric_vals[0],
                "max": numeric_vals[-1],
                "avg": round(sum(numeric_vals) / len(numeric_vals), 2),
                "median": median,
            }
        )
    else:
        freq: dict[str, int] = {}
        for v in values:
            s = str(v).strip()
            if s:
                freq[s] = freq.get(s, 0) + 1
        top = sorted(freq.items(), key=lambda x: -x[1])[:8]
        stats.update(
            {
                "type": "categorical",
                "top_values": [{"value": k, "count": c} for k, c in top],
            }
        )
    return stats


def _data_sample(rows: list[dict[str, Any]], max_rows: int = 8) -> list[dict[str, Any]]:
    """Compact sample rows for LLM (values truncated to avoid token waste)."""
    out: list[dict[str, Any]] = []
    for r in rows[:max_rows]:
        if not isinstance(r, dict):
            continue
        compact: dict[str, Any] = {}
        for k, v in r.items():
            s = str(v) if v is not None else ""
            compact[k] = s[:80] if len(s) > 80 else v
        out.append(compact)
    return out


def _assess_step_quality(
    step: dict[str, Any],
    index: int,
) -> dict[str, Any]:
    """Deterministic quality signals for one executed step (no LLM).

    Returns raw result signals plus compact statistics. Scoring, reason
    classification and repairability belong exclusively to result_quality.
    """
    brief = step.get("brief") or ""
    sql = step.get("format_statement") or step.get("sql") or ""
    if step.get("error"):
        failure = step.get("failure") or {}
        return {
            "index": index,
            "brief": brief,
            "sql": sql,
            "error": str(step.get("error") or ""),
            "retryable": bool(failure.get("retryable")),
            "execution_status": "failed",
            "row_count": 0,
            "fields": [],
            "truncated": False,
            "truncation_reason": None,
            "null_rates": {},
            "metrics": {},
            "column_stats": {},
            "data_sample": [],
            "limitations": [],
            "data_rows": [],
        }

    result = step.get("result")
    execution_status = "success" if isinstance(result, Mapping) else "not_run"
    rows = _result_rows(step)
    fields = _result_fields(step)
    result_payload = result if isinstance(result, Mapping) else {}
    window = read_result_window(result_payload, rows)
    truncated = window["truncated"]

    # Result semantics are classified before presentation. Charts consume the
    # accepted roles; they never redefine validation or quality inputs.
    fields_info_list = result_payload.get("fields_info") or []
    fields_info_map = {
        fi.get("name"): fi
        for fi in fields_info_list
        if isinstance(fi, dict) and fi.get("name")
    }
    field_roles = classify_field_roles(
        fields,
        list(fields_info_map.values()),
        {},
    )

    null_rates: dict[str, float] = {}
    metrics: dict[str, Any] = {}
    col_stats: dict[str, Any] = {}
    limitations: list[str] = []
    coverage_totals = result_payload.get("coverage_totals")
    if truncated:
        if isinstance(coverage_totals, dict) and coverage_totals:
            group_count = coverage_totals.get("__group_count")
            metric_bits = [
                f"{name}={value}"
                for name, value in coverage_totals.items()
                if name != "__group_count"
            ]
            window_note = f"展示窗口 {window['row_count']} 行"
            if group_count is not None:
                window_note += f"，全量 {group_count} 组"
            if metric_bits:
                window_note += "；全量合计: " + ", ".join(metric_bits[:6])
            limitations.append(window_note)
        else:
            limitations.append(
                f"本次仅展示前 {window['row_count']} 行，未查询全量合计；"
                "展示窗口内的数字不能当作累计或全量结果"
            )
    for f in fields:
        if f in field_roles["metrics"]:
            metrics[f] = _metric_stats(rows, f)
        else:
            rate = _null_rate(rows, f)
            null_rates[f] = round(rate, 3)
        # column_stats for ALL fields (metrics get numeric stats, dims get categorical)
        col_stats[f] = _column_stats(rows, f)

    return {
        "index": index,
        "brief": brief,
        "sql": sql,
        "execution_status": execution_status,
        "row_count": window["row_count"],
        "fields": fields,
        "truncated": truncated,
        "limit": window.get("limit"),
        "truncation_reason": window["truncation_reason"],
        "null_rates": null_rates,
        "metrics": metrics,
        "field_roles": {
            "metrics": sorted(field_roles["metrics"]),
            "dimensions": sorted(field_roles["dimensions"]),
        },
        "column_stats": col_stats,
        "data_sample": _data_sample(rows),
        "limitations": limitations,
        "data_rows": rows,
        "coverage_totals": coverage_totals if isinstance(coverage_totals, dict) else {},
    }


def _assess_all_steps(
    all_steps: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {
            **_assess_step_quality(step, index),
            "structural_issues": list(step.get("_structural_issues") or []),
        }
        for index, step in enumerate(all_steps or [])
    ]


def _repair_instruction(assessments: list[dict[str, Any]], question: str) -> str:
    reasons: list[str] = []
    for a in assessments:
        if a.get("error"):
            reasons.append(f"查询{a['index'] + 1}: {a['error']}")
        for item in a.get("structural_issues") or []:
            reasons.append(
                f"查询{a['index'] + 1}: {validation_issue_prompt_text(item)}"
            )
    issue_text = "\n".join(f"- {item}" for item in reasons) or "- 未提供确定性结构原因"
    return (
        "上一轮物理候选未通过执行或结构门禁，请在固定用户证据下修复查询计划。\n"
        f"原始问题仅供审计：{question}\n"
        f"质检问题：\n{issue_text}\n"
        "只允许修复物理实现：使用真实标识符并满足协议能力；不得改变规格中的输出、"
        "过滤、时间范围、聚合、粒度、排序或 limit；不得根据空结果自行收紧或放宽业务条件。\n"
    )


def _normalize_result_data(
    result: dict[str, Any], llm_service: LLMService
) -> dict[str, Any]:
    data = DataFormat.convert_large_numbers_in_object_array(result.get("data"))
    data = DataFormat.normalize_qualified_sql_column_keys_in_object_array(data)
    if data:
        data = prepare_for_orjson(data)
        result = dict(result)
        row_limit = _ROW_LIMIT if llm_service.enable_sql_row_limit else None
        if result.get("truncated"):
            displayed = data[:row_limit] if row_limit else data
            window = {
                "row_count": len(displayed),
                "limit": row_limit,
                "truncated": True,
                "truncation_reason": result.get("truncation_reason") or "query_limit",
            }
        else:
            displayed, window = apply_display_window(
                data,
                row_limit=row_limit,
            )
        result["data"] = displayed
        result["row_count"] = window["row_count"]
        result["truncated"] = window["truncated"]
        result["truncation_reason"] = window["truncation_reason"]
        if window["limit"] is not None:
            result["limit"] = window["limit"]
        else:
            result.pop("limit", None)
    else:
        result = dict(result)
        result["data"] = data or []
        result["row_count"] = 0
        result["truncated"] = False
        result["truncation_reason"] = None
        result.pop("limit", None)
    if llm_service.ds is not None:
        result["datasource"] = getattr(llm_service.ds, "id", None)
    return result


def _attach_aggregation_totals(
    llm_service: LLMService,
    plan_dict: dict[str, Any],
    result: dict[str, Any],
) -> dict[str, Any]:
    """Fetch one-row grouped totals when the display window was truncated."""
    if not result.get("truncated"):
        return result
    sql = str((plan_dict.get("payload") or {}).get("sql") or plan_dict.get("sql") or "")
    totals_sql = aggregation_totals_sql(sql, dialect=_sql_dialect(llm_service))
    if not totals_sql:
        return result
    try:
        totals_qr = llm_service.protocol.execute(
            llm_service.ds,
            QueryPlan(
                success=True,
                statement=totals_sql,
                payload={"sql": totals_sql},
                resources=list(plan_dict.get("tables") or []),
            ),
            max_rows=1,
        )
        rows = list(totals_qr.data or [])
        if not rows or not isinstance(rows[0], dict):
            return result
        updated = dict(result)
        updated["coverage_totals"] = dict(rows[0])
        return updated
    except Exception as exc:
        SQLBotLogUtil.warning(f"aggregation totals skipped: {exc}")
        return result


def _merge_batch_into_steps(
    all_steps: list[dict[str, Any]],
    batch_plans: list[dict[str, Any]],
    batch_results: list[dict[str, Any]],
    batch_charts: list[dict[str, Any]],
    *,
    entity_bindings: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Append current batch entries once. Idempotent by global offset."""
    updated = list(all_steps or [])
    if not batch_plans:
        return updated

    result_by_idx = {
        r.get("index"): r for r in (batch_results or []) if isinstance(r, dict)
    }

    def _sql_fp(entry: dict[str, Any]) -> str:
        sql = (entry.get("format_statement") or entry.get("sql") or "").strip().lower()
        return re.sub(r"\s+", " ", sql)

    existing_fps = {
        _sql_fp(s) for s in updated if (s.get("format_statement") or s.get("sql"))
    }

    for i, plan_dict in enumerate(batch_plans):
        entry: dict[str, Any] = {
            "plan_id": plan_dict.get("plan_id", ""),
            "dataset_id": plan_dict.get("dataset_id", f"dataset_{i + 1}"),
            "required": bool(plan_dict.get("required", True)),
            "sql": plan_dict.get("sql", ""),
            "format_statement": plan_dict.get("format_statement", ""),
            "tables": plan_dict.get("tables", []),
            "chart_type": plan_dict.get("chart_type", "table"),
            "brief": plan_dict.get("brief", ""),
            "presentation_title": plan_dict.get("presentation_title", ""),
            "projection_requirements": plan_dict.get("projection_requirements", {}),
            "covered_requirement_keys": plan_dict.get("covered_requirement_keys", []),
        }
        if isinstance(plan_dict.get("presentation"), dict):
            entry["presentation"] = plan_dict["presentation"]
        if entity_bindings:
            entry["_entity_bindings"] = entity_bindings
        r = result_by_idx.get(i)
        if r:
            if r.get("error"):
                entry["error"] = r.get("error")
                if r.get("failure"):
                    entry["failure"] = r.get("failure")
            else:
                entry["result"] = r.get("result") or {}
                if r.get("re_exec") is not None:
                    entry["re_exec"] = r.get("re_exec")
        if i < len(batch_charts or []):
            entry["chart"] = batch_charts[i]
        fp = _sql_fp(entry)
        if fp and fp in existing_fps and not entry.get("error"):
            continue  # skip duplicate successful SQL already in history
        if fp:
            existing_fps.add(fp)
        updated.append(entry)
    return updated


def _build_candidate_quality(
    assessments: list[dict[str, Any]],
    *,
    requirements_covered: bool,
    plan_validated: bool,
    semantic_status: Literal["verified", "partial", "unsupported"],
    assumption_risk: Literal["low", "medium", "high"],
) -> ResultQuality:
    """Score a candidate once from explicit graph-stage evidence."""
    reports: list[dict[str, Any]] = []
    for assessment in assessments:
        raw_status = str(assessment.get("execution_status") or "not_run")
        execution_status: ExecutionStatus = (
            cast(ExecutionStatus, raw_status)
            if raw_status in {"not_run", "success", "failed"}
            else "not_run"
        )
        evidence: CompletionEvidence = {
            "requirements_covered": requirements_covered,
            "plan_validated": plan_validated,
            "semantic_status": semantic_status,
            "execution_status": execution_status,
            "result_structure_valid": (
                execution_status == "success"
                and not bool(assessment.get("structural_issues"))
            ),
            "evidence_confidence": 1.0 if semantic_status == "verified" else 0.6,
            "assumption_risk": assumption_risk,
        }
        report = build_step_quality(assessment, evidence=evidence)
        reports.append(report)
    return build_overall_quality(reports)


def _candidate_batch(
    steps: list[dict[str, Any]],
    *,
    quality: ResultQuality,
    outcome: RunOutcome | None = None,
) -> CandidateBatch:
    candidate_outcome = (
        dict(outcome) if outcome is not None else outcome_from_steps(steps)
    )
    candidate_outcome["quality"] = quality
    return {
        "steps": steps,
        "quality": quality,
        "outcome": candidate_outcome,
    }


def _fallback_analysis(
    assessments: list[dict[str, Any]],
    *,
    reason: str,
    target_language: str = "简体中文",
) -> str:
    """Short deterministic note when summary generation fails."""
    returned_rows = sum(int(item.get("row_count") or 0) for item in assessments)
    truncated = any(bool(item.get("truncated")) for item in assessments)
    query_count = len(assessments)
    if "english" in target_language.casefold() or target_language.casefold() == "en":
        window = f"{query_count} query result(s), {returned_rows} displayed row(s)" + (
            "; at least one result is truncated." if truncated else "."
        )
        return f"The query completed ({window}) Summary generation was unavailable: {reason}"
    window = f"{query_count} 个查询共返回 {returned_rows} 行"
    if truncated:
        window += "（含截断结果，样本统计不能当作全量）。"
    else:
        window += "。"
    return f"查询已完成。{window} 文字总结生成异常：{reason}"


def _record_snapshot_values(
    all_steps: list[dict[str, Any]],
    analysis_text: str = "",
    *,
    finish: bool = False,
    outcome: RunOutcome | None = None,
    public_error: str | None = None,
    execution_mode: Literal["verified", "unverified"] = "verified",
) -> dict[str, Any]:
    """Build the ChatRecord projection committed by ``finalize_run``."""
    if outcome is None:
        raise ValueError("Terminal NLQ snapshot requires an outcome")
    published_outcome = outcome
    if public_error and outcome["status"] in {"failed", "limit_reached"}:
        try:
            parsed_public_error = orjson.loads(public_error)
            safe_message = str(parsed_public_error.get("message") or public_error)
        except (TypeError, ValueError):
            safe_message = public_error
        published_outcome = cast(RunOutcome, deepcopy(outcome))
        for failure in published_outcome.get("failures") or []:
            failure["message"] = safe_message
    error: str | None = None
    if finish and outcome and outcome["status"] in {"failed", "limit_reached"}:
        failures = outcome.get("failures") or []
        error = public_error or str(
            failures[0].get("message")
            if failures
            else "Conversation completed without a usable result"
        )

    answer_datasets: list[dict[str, Any]] = []
    for index, step in enumerate(all_steps):
        if step.get("error"):
            failure = dict(step.get("failure") or {})
            raw_public_error = public_error_message(
                str(step.get("error") or "Query failed")
            )
            try:
                parsed_public_error = orjson.loads(raw_public_error)
            except (TypeError, ValueError):
                parsed_public_error = {
                    "type": "QUERY_FAILED",
                    "message": raw_public_error,
                }
            answer_datasets.append(
                {
                    "dataset_id": str(step.get("dataset_id") or f"dataset_{index + 1}"),
                    "status": "failed",
                    "required": bool(step.get("required", True)),
                    "title": str(step.get("brief") or ""),
                    "sql": "",
                    "fields": [],
                    "rows": [],
                    "row_count": None,
                    "truncated": False,
                    "error": {
                        "code": str(
                            parsed_public_error.get("type")
                            or failure.get("kind")
                            or "QUERY_FAILED"
                        ).upper(),
                        "message": str(
                            parsed_public_error.get("message") or "Query failed"
                        ),
                        "retryable": bool(failure.get("retryable")),
                    },
                }
            )
            continue
        result = (
            step.get("result")
            if isinstance(step.get("result"), dict)
            else step.get("data")
            if isinstance(step.get("data"), dict)
            else {}
        )
        answer_datasets.append(
            {
                "dataset_id": str(step.get("dataset_id") or f"dataset_{index + 1}"),
                "status": "degraded"
                if published_outcome.get("status") == "degraded"
                else "succeeded",
                "required": bool(step.get("required", True)),
                "title": str(step.get("brief") or ""),
                "sql": str(step.get("format_statement") or step.get("sql") or ""),
                "fields": list(result.get("fields") or []),
                "rows": list(result.get("data") or []),
                "row_count": len(result.get("data") or []),
                "truncated": bool(result.get("truncated")),
                "limit": result.get("limit"),
                "truncation_reason": result.get("truncation_reason"),
                "presentation": step.get("presentation"),
                "chart": step.get("chart"),
            }
        )
    answer_status = (
        "failed"
        if published_outcome.get("status") in {"failed", "limit_reached"}
        else "degraded"
        if published_outcome.get("status") == "degraded"
        else "succeeded"
    )
    answer_error: dict[str, Any] | None = None
    if error:
        try:
            parsed_error = orjson.loads(error)
        except (TypeError, ValueError):
            parsed_error = {"type": "QUERY_FAILED", "message": error}
        answer_error = {
            "code": str(parsed_error.get("type") or "QUERY_FAILED").upper(),
            "message": str(parsed_error.get("message") or "Query failed"),
            "retryable": True,
        }
    return {
        "terminal": finish,
        "error": error,
        "answer": {
            "kind": "query",
            "status": answer_status,
            "content": analysis_text,
            "execution_mode": execution_mode,
            "datasets": answer_datasets,
            "intent_summary": "",
            "source_record_ids": [],
            "assumptions": [],
            "quality": published_outcome.get("quality"),
            "error": answer_error,
        },
    }


def _apply_row_permissions(
    llm_service: LLMService,
    session: Any,
    plan_dict: dict[str, Any],
    access_scope: AccessScope | None = None,
) -> QueryPlan:
    """Return a plan copy with row-permission SQL applied (main thread only)."""
    qp = _query_plan(plan_dict)
    sql = plan_dict.get("sql") or qp.payload.get("sql") or qp.statement
    use_dynamic_ds = bool(
        llm_service.current_assistant
        and llm_service.current_assistant.type in DYNAMIC_DS_TYPES
    )
    is_page_embedded = bool(
        llm_service.current_assistant and llm_service.current_assistant.type == 4
    )

    if not llm_service.protocol.supports(CAP_ROW_PERMISSION):
        return qp

    if not (
        (
            (not llm_service.current_assistant or is_page_embedded)
            and is_normal_user(llm_service.current_user)
        )
        or use_dynamic_ds
    ):
        return qp

    if use_dynamic_ds:
        dynamic_result = generate_assistant_dynamic_sql(
            llm_service, session, sql, qp.resources
        )
        temp_sql = (
            dynamic_result.get("sqlbot_temp_sql_text") if dynamic_result else None
        )
        if temp_sql:
            assistant_sql = (
                generate_filter(
                    llm_service,
                    session,
                    sql,
                    qp.resources,
                    resolved_filters=(
                        access_scope.filters_for(qp.resources)
                        if access_scope is not None
                        else None
                    ),
                )
                or sql
            )
            for origin_table, subsql in (dynamic_result or {}).items():
                if origin_table == "sqlbot_temp_sql_text":
                    continue
                assistant_sql = assistant_sql.replace(
                    f"{DYNAMIC_SUBSQL_PREFIX}{origin_table}", subsql
                )
            sql = assistant_sql
    else:
        sql_result = generate_filter(
            llm_service,
            session,
            sql,
            qp.resources,
            resolved_filters=(
                access_scope.filters_for(qp.resources)
                if access_scope is not None
                else None
            ),
        )
        if sql_result:
            sql = sql_result

    # Pydantic v2 model_copy; fall back to deepcopy
    try:
        new_plan = qp.model_copy(deep=True)
    except Exception:
        new_plan = deepcopy(qp)
    new_plan.payload = dict(new_plan.payload or {})
    new_plan.payload["sql"] = sql
    return new_plan


def _table_chart(presentation: ResultPresentation) -> dict[str, Any]:
    return {
        "type": "table",
        "title": presentation["title"],
        "columns": chart_columns(presentation),
    }


# ── Nodes (bootstrap) ────────────────────────────────────────────────────────


def prepare_record_node(state: NlqState) -> NlqState:
    """Emit SSE header only — no domain match (match runs after ds is sure)."""
    llm_service = _llm_service(state)
    sink = StreamSink.from_state(state)
    record = llm_service.get_record()
    return_img = bool(state.get("return_img", True))
    json_result: dict[str, Any] = {"success": True}

    try:
        sink.event({"type": "id", "id": record.id})
        sink.event({"type": "question", "question": record.question})
        sink.record_header(
            record_id=record.id,
            question=record.question,
            prefix=llm_service.trans("i18n_chat.record_id_in_mcp"),
        )
        if sink.mode == "json":
            json_result["record_id"] = record.id

        return {
            **state,
            "graph_key": "chat",
            "mode": "primary",
            "chat_id": record.chat_id,
            "record_id": record.id,
            "return_img": return_img,
            "json_result": json_result,
            "step_index": 0,
            "active_candidate": {},
            "rejected_candidate": None,
            "accepted_candidate": None,
            "max_steps": state.get("max_steps") or _MAX_STEPS,
            "max_batch_size": state.get("max_batch_size") or _MAX_BATCH_SIZE,
            "analysis_text": "",
            "decision": "",
            "decision_reason": "",
            "repair_hint": "",
            "gen_attempts": 0,
            "entity_bindings": {},
            "knowledge_matches": [],
            "compiled_knowledge": {},
            "temporal_parse": {},
            "planning_decision": "pending",
            "ambiguity_payload": {},
            "turn_route": {},
            "source_datasets": [],
            "data_strategy": "direct_query",
            "terminal_answer": {},
            "execution_mode": "verified",
            "risk_assessment": {},
            "semantic_review": {},
            "plan_facts": [],
            "planning_model_elapsed_sec": 0.0,
            "repair_source_plans": [],
            "outcome": running_outcome(),
            "finish_step": state.get("finish_step")
            or int(ChatFinishStep.GENERATE_CHART.value),
        }
    except Exception as e:
        return {
            **_fail(state, record.id, e),
            "graph_key": "chat",
            "mode": "primary",
            "chat_id": record.chat_id,
            "record_id": record.id,
            "return_img": return_img,
            "json_result": json_result,
        }


def ensure_datasource_node(state: NlqState) -> NlqState:
    """Select/validate datasource + connection."""
    llm_service = _llm_service(state)
    sink = StreamSink.from_state(state)

    try:
        silent = state.get("planning_decision") == "replan"

        def _bind_datasource(span: Any) -> None:
            with session_scope() as session:
                selected_by_model = not bool(llm_service.ds)
                if selected_by_model:
                    for chunk in select_datasource(
                        llm_service, session, audit_span=span
                    ):
                        sink.token(
                            content=chunk.get("content"),
                            reasoning_content=chunk.get("reasoning_content"),
                            event_type="datasource-result",
                        )
                    sink.event(
                        {
                            "id": llm_service.ds.id,
                            "datasource_name": llm_service.ds.name,
                            "engine_type": getattr(llm_service.ds, "type", None),
                            "type": "datasource",
                        }
                    )
                else:
                    validate_history_ds(llm_service, session)

                connected = llm_service.protocol.check_connection(ds=llm_service.ds)
                if not connected:
                    raise SQLBotDBConnectionError("Datasource connection failed")
                if span is None:
                    return
                span.set_input(
                    {
                        "datasource_id": getattr(llm_service.ds, "id", None),
                        "selected_by_model": selected_by_model,
                    }
                )
                span.set_output(
                    {
                        "connected": True,
                        "datasource_id": getattr(llm_service.ds, "id", None),
                        "datasource_name": getattr(llm_service.ds, "name", ""),
                        "engine_type": getattr(llm_service.ds, "type", None),
                    }
                )
                span.set_summary("chat.audit.datasource_selected")

        if silent and llm_service.ds:
            _bind_datasource(None)
            return state
        with log_span(
            operate=OperationEnum.CHOOSE_DATASOURCE,
            record_id=llm_service.record.id,
            local_operation=bool(llm_service.ds),
            graph_node="ensure_datasource",
            title_key="chat.log.CHOOSE_DATASOURCE",
        ) as span:
            _bind_datasource(span)
            return state
    except Exception as e:
        return _fail(state, llm_service.record.id, e)


def recall_knowledge_node(state: NlqState) -> NlqState:
    llm_service = _llm_service(state)
    oid, ds_id = _ds_scope(llm_service)
    seed_revision_ids, seed_policy = seed_revisions_for_turn(
        str((state.get("turn_route") or {}).get("relation") or "independent"),
        state.get("referenced_turns") or [],
    )
    with session_scope() as session:
        try:
            matches = match_knowledge(
                llm_service,
                session,
                oid,
                ds_id,
                access_scope=_access_scope(state),
                stage="generate",
                include_examples=True,
                seed_revision_ids=seed_revision_ids,
                seed_policy=seed_policy,
            )
            compiled = get_compiled_knowledge(llm_service)
            return {
                **state,
                "knowledge_matches": [match.model_dump() for match in matches],
                "compiled_knowledge": (
                    compiled.model_dump(mode="json") if compiled else {}
                ),
            }
        except Exception as e:
            return _fail(state, llm_service.record.id, e)


def parse_temporal_evidence_node(state: NlqState) -> NlqState:
    """Capture deterministic temporal evidence without creating contract state."""
    llm_service = _llm_service(state)
    question = llm_service.generation_question
    with session_scope() as session:
        run = require_active_run(session, str(state["run_id"]))
        business_now = run.business_now
    temporal_parse = infer_time_intent(str(question or ""), now=business_now)
    if not temporal_parse:
        return state
    return {**state, "temporal_parse": temporal_parse}


def resolve_access_scope_node(state: NlqState) -> NlqState:
    """Resolve datasource visibility once for every downstream NLQ stage."""
    llm_service = _llm_service(state)
    try:

        def _bind_access_scope(span: Any) -> None:
            with session_scope() as session:
                access_scope = resolve_access_scope(
                    session,
                    current_user=llm_service.current_user,
                    ds=llm_service.ds,
                )
                attach_runtime(str(state["run_id"]), access_scope=access_scope)
                if span is None:
                    return
                span.set_detail(
                    {
                        "access_scope_applied": access_scope is not None,
                        "datasource_id": getattr(llm_service.ds, "id", None),
                    }
                )
                span.set_summary("chat.audit.access_scope_ready")

        if state.get("planning_decision") == "replan":
            _bind_access_scope(None)
            return state
        with log_span(
            operate=OperationEnum.CHOOSE_TABLE,
            record_id=llm_service.record.id,
            local_operation=True,
            graph_node="resolve_access_scope",
            title_key="chat.log.ACCESS_SCOPE",
            brief="确认数据访问范围",
        ) as span:
            _bind_access_scope(span)
            return state
    except Exception as exc:
        return _fail(state, llm_service.record.id, exc)


def match_custom_prompts_node(state: NlqState) -> NlqState:
    llm_service = _llm_service(state)
    oid, ds_id = _ds_scope(llm_service)
    with session_scope() as session:
        try:
            match_custom_prompts(
                llm_service, session, CustomPromptTypeEnum.GENERATE_SQL, oid, ds_id
            )
            return state
        except Exception as e:
            return _fail(state, llm_service.record.id, e)


def retrieve_schema_node(state: NlqState) -> NlqState:
    """Project schema from bound knowledge tables; rank only when no unit hit."""
    llm_service = _llm_service(state)
    compiled = get_compiled_knowledge(llm_service)
    bound = list(compiled.bound_resources) if compiled is not None else []
    entity_tables = binding_resource_names(state.get("entity_bindings") or {})
    exact = list(dict.fromkeys([*bound, *entity_tables])) if bound else None
    with session_scope() as session:
        try:
            resource_names = match_table_schema(
                llm_service,
                session,
                resource_names=exact,
                required_resource_names=() if exact is not None else entity_tables,
                access_scope=_access_scope(state),
            )
            return {
                **state,
                "entity_bindings": retain_binding_resources(
                    state.get("entity_bindings") or {},
                    resource_names,
                ),
            }
        except Exception as e:
            return _fail(state, llm_service.record.id, e)


def retrieve_context_node(state: NlqState) -> NlqState:
    """Build planner context as one checkpointed stage.

    Domain steps keep their own audit spans, but the graph does not checkpoint
    a chain of micro-nodes whose only purpose is passing the same dictionary.
    Re-running this stage after clarification is safe because retrieved facts
    are deduplicated when they enter the evidence ledger.
    """
    # Clarification only appends immutable user evidence; it does not change
    # datasource metadata. Reuse the durable snapshot instead of repeating all
    # external retrieval calls (and their failure modes) after every answer.
    if state.get("planning_decision") == "replan":
        llm_service = _llm_service(state)
        with session_scope() as session:
            nlq_run = session.get(QueryRun, str(state["run_id"]))
            persisted = dict(nlq_run.planning_context or {}) if nlq_run else {}
        if persisted:
            try:
                snapshot = restore_planning_context(llm_service, persisted)
                return {
                    **state,
                    "entity_bindings": snapshot.entity_bindings,
                    "temporal_parse": snapshot.temporal_parse,
                    "compiled_knowledge": snapshot.compiled_knowledge,
                }
            except ValueError:
                # A malformed/incomplete snapshot is rebuilt through the sole
                # retrieval path below; planning is never allowed to consume it.
                pass

    current = state
    for step in (
        recall_knowledge_node,
        ground_entities_node,
        match_custom_prompts_node,
        retrieve_schema_node,
        parse_temporal_evidence_node,
    ):
        current = step(current)
        if current.get("error"):
            break
    if not current.get("error"):
        llm_service = _llm_service(current)
        snapshot = capture_planning_context(
            llm_service,
            entity_bindings=current.get("entity_bindings") or {},
            temporal_parse=current.get("temporal_parse") or {},
        )
        if not snapshot.usable:
            return _fail(
                current,
                llm_service.record.id,
                "No usable datasource schema was retrieved for query planning",
            )
        with session_scope() as session:
            require_active_run(session, str(current["run_id"]))
            nlq_run = session.get(QueryRun, str(current["run_id"]))
            if nlq_run is None:
                return _fail(
                    current,
                    llm_service.record.id,
                    f"NLQ run {current['run_id']} not found",
                )
            nlq_run.planning_context = snapshot.model_dump(mode="json")
            session.add(nlq_run)
            session.commit()
        if snapshot.truncation:
            SQLBotLogUtil.info(
                "planner context truncated: "
                + ", ".join(str(item.get("section")) for item in snapshot.truncation)
            )
    return current


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
                "task_kind 只能是 query/analysis/prediction/unsupported；relation 只能是 "
                "independent/continue/revise。continue/revise 必须从候选历史选择 1~3 个 "
                "reference_record_ids；新问题必须 independent。"
            )
            human = orjson.dumps(
                {"current_message": message, "recent_turns": history_payload}
            ).decode()
            call = consume_llm(
                llm_service.llm.bind(temperature=0),
                [SystemMessage(content=system), HumanMessage(content=human)],
            )
            raw = call.content or message_content_text(
                getattr(call.message, "content", "")
            )
            nested = extract_nested_json(raw)
            if not nested:
                raise ValueError("Turn router response is not JSON")
            result = orjson.loads(nested)
            if not isinstance(result, dict):
                raise ValueError("Turn router response must be an object")
            result["source"] = "model"
            result.setdefault("confidence", 0.7)
            route_call_holder["call"] = call
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
                    # received. Hallucinated IDs must never broaden context.
                    route = TurnRoute(
                        task_kind="query",
                        relation="independent",
                        source="fallback",
                        confidence=0.35,
                    )
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


def _dataset_capabilities(dataset: dict[str, Any]) -> dict[str, Any]:
    rows = [item for item in dataset.get("rows") or [] if isinstance(item, dict)]
    fields = [str(item) for item in dataset.get("fields") or []]
    temporal = False
    numeric = False
    for field in fields:
        values = [row.get(field) for row in rows if row.get(field) is not None]
        if not values:
            continue
        if any(
            isinstance(value, int | float) and not isinstance(value, bool)
            for value in values
        ):
            numeric = True
        if any(_TEMPORAL_RE.match(str(value).strip()) for value in values):
            temporal = True
    return {
        **dataset,
        "has_time_field": temporal,
        "has_numeric_measure": numeric,
        "valid_points": len(rows),
    }


def _record_answer_datasets(record: ChatRecord) -> list[dict[str, Any]]:
    answer = record.answer if isinstance(record.answer, dict) else {}
    raw = answer.get("datasets") or answer.get("source_datasets") or []
    return [
        _dataset_capabilities(
            {
                **dict(item),
                "source_record_id": int(record.id or 0),
                "rows": list(item.get("rows") or []),
            }
        )
        for item in raw
        if isinstance(item, dict) and item.get("status") in {"succeeded", "degraded"}
    ]


def assemble_turn_context_node(state: NlqState) -> NlqState:
    """Select durable history/results before any datasource or model work."""
    try:
        route = TurnRoute.model_validate(state.get("turn_route") or {})
        source_datasets: list[dict[str, Any]] = []
        referenced_turns: list[dict[str, Any]] = []
        prior_user_evidence: list[dict[str, Any]] = []
        with session_scope() as session:
            run = require_active_run(session, str(state["run_id"]))
            current = session.get(ChatRecord, run.chat_record_id)
            if current is None:
                raise LookupError("Conversation turn not found")
            prior_user_evidence = load_prior_user_evidence(
                session,
                chat_id=int(current.chat_id),
                user_id=int(run.user_id),
                reference_record_ids=route.reference_record_ids,
            )
            for record_id in route.reference_record_ids:
                referenced = session.get(ChatRecord, int(record_id))
                if (
                    referenced is None
                    or int(referenced.create_by or 0) != int(run.user_id)
                    or int(referenced.chat_id) != int(current.chat_id)
                ):
                    raise SingleMessageError(
                        "Referenced conversation result is unavailable"
                    )
                if (
                    current.datasource is not None
                    and referenced.datasource is not None
                    and int(current.datasource) != int(referenced.datasource)
                ):
                    raise SingleMessageError(
                        "Cannot continue a query across different datasources"
                    )
                datasets = _record_answer_datasets(referenced)
                source_datasets.extend(datasets)
                latest_run = (
                    session.exec(
                        select(ConversationRun)
                        .where(
                            ConversationRun.chat_record_id == int(referenced.id),
                        )
                        .order_by(ConversationRun.attempt_index.desc())
                        .limit(1)
                    )
                    .scalars()
                    .one_or_none()
                )
                latest_query = (
                    session.get(QueryRun, latest_run.run_id)
                    if latest_run is not None
                    else None
                )
                answer = (
                    referenced.answer if isinstance(referenced.answer, dict) else {}
                )
                planning = (
                    dict(latest_query.planning_context or {})
                    if latest_query is not None
                    else {}
                )
                referenced_turns.append(
                    {
                        "record_id": referenced.id,
                        "question": referenced.question,
                        "turn_kind": referenced.turn_kind,
                        "answer_status": answer.get("status"),
                        "answer_summary": str(answer.get("content") or "")[:1000],
                        "run_status": latest_run.status
                        if latest_run is not None
                        else None,
                        "planning_status": (
                            latest_query.planning_status
                            if latest_query is not None
                            else None
                        ),
                        "dataset_ids": [item.get("dataset_id") for item in datasets],
                        "revision_ids": matched_revision_ids(
                            planning.get("compiled_knowledge")
                            if isinstance(planning.get("compiled_knowledge"), dict)
                            else {}
                        ),
                    }
                )
            strategy = choose_data_strategy(
                route,
                referenced_datasets=tuple(source_datasets),
                message_has_query_need=route.task_kind in {"query", "prediction"},
            )
            business_now_text = run.business_now.isoformat()
            business_timezone = run.timezone
            fingerprint = context_fingerprint(
                {
                    "message": current.question,
                    "route": route.model_dump(mode="json"),
                    "references": referenced_turns,
                    "prior_user_evidence": prior_user_evidence,
                    "dataset_ids": [item.get("dataset_id") for item in source_datasets],
                    "business_now": business_now_text,
                    "timezone": business_timezone,
                }
            )
            run.context_fingerprint = fingerprint
            session.add(run)
            session.commit()
        return {
            **state,
            "referenced_turns": referenced_turns,
            "prior_user_evidence": prior_user_evidence,
            "source_datasets": source_datasets,
            "data_strategy": strategy,
            "context_fingerprint": fingerprint,
            "business_now": business_now_text,
            "timezone": business_timezone,
            "reference_record_ids": list(route.reference_record_ids),
        }
    except Exception as exc:
        return _fail(state, state.get("record_id"), exc)


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


def unavailable_context_node(state: NlqState) -> NlqState:
    route = state.get("turn_route") or {}
    task = str(route.get("task_kind") or "analysis")
    message = (
        "当前没有可用于分析的查询结果，请先提出需要查询的数据。"
        if task == "analysis"
        else "当前没有满足预测条件的时间序列数据，请明确要预测的指标和时间粒度。"
    )
    return _fail(state, state.get("record_id"), SingleMessageError(message))


def route_after_turn_router(
    state: NlqState,
) -> Literal["unsupported", "assemble_context", "fail"]:
    if state.get("error"):
        return "fail"
    route = state.get("turn_route") or {}
    return (
        "unsupported" if route.get("task_kind") == "unsupported" else "assemble_context"
    )


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


def _sql_dialect(llm_service: LLMService) -> str | None:
    return sqlglot_dialect_for(
        getattr(getattr(llm_service, "protocol", None), "type_key", None)
    )


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
                    },
                    resolved_question_ids=_resolved_question_ids(evidence),
                    max_batch_size=state.get("max_batch_size") or _MAX_BATCH_SIZE,
                    timeout_seconds=_planning_call_timeout_sec(),
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
            span.set_detail(
                {
                    "decision": result.decision.decision,
                    "plan_count": len(result.plans),
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
                "ambiguity_payload": result.decision.as_card().model_dump(mode="json"),
                "active_candidate": {},
                "planning_model_elapsed_sec": _planning_elapsed_for_state(
                    interrupt=True, elapsed=planning_elapsed
                ),
            }
        if isinstance(result.decision, QueryUnsupported):
            raise SingleMessageError(result.decision.message)
        if not isinstance(result.decision, Ready) or not result.plans:
            raise SingleMessageError("Query Agent did not produce an executable plan")

        fact_models = _plan_fact_models(result.plans, dialect=_sql_dialect(llm_service))
        fact_payloads = [item.model_dump(mode="json") for item in fact_models]
        failed_gates = [
            {
                "plan_id": plan.get("plan_id"),
                "code": str(plan.get("hard_gate_code") or "PLAN_VALIDATION_FAILED"),
                "errors": list(plan.get("hard_gate_errors") or []),
            }
            for plan in result.plans
            if plan.get("hard_gate_status") == "failed"
        ]
        if failed_gates:
            gate_report = {"status": "failed", "plans": failed_gates}
            with session_scope() as session:
                persist_query_decision(
                    session,
                    run_id=run_id,
                    decision=result.decision.model_dump(mode="json"),
                    plans=result.plans,
                    hard_gate_report=gate_report,
                    risk_assessment={},
                    plan_facts=fact_payloads,
                    planning_status="rejected"
                    if any(
                        item["code"]
                        in {
                            "NON_READ_ONLY_PLAN",
                            "ACCESS_POLICY_VIOLATION",
                            "PROTOCOL_UNSUPPORTED",
                        }
                        for item in failed_gates
                    )
                    else "repairing",
                    repair_record={
                        "attempt": 0,
                        "reason": "hard_gate_failed",
                        "status": "failed",
                        "plan_ids": [item.get("plan_id") for item in result.plans],
                        "sql": [str(item.get("sql") or "") for item in result.plans],
                    },
                )
            fatal_codes = {
                item["code"]
                for item in failed_gates
                if item["code"]
                in {
                    "NON_READ_ONLY_PLAN",
                    "ACCESS_POLICY_VIOLATION",
                    "PROTOCOL_UNSUPPORTED",
                }
            }
            if fatal_codes:
                raise SingleMessageError("查询未通过安全、权限或协议门禁，已停止执行。")
            repair_errors = [
                message for item in failed_gates for message in item.get("errors") or []
            ]
            return {
                **state,
                "planning_decision": "ready",
                "active_candidate": {},
                "repair_source_plans": result.plans,
                "repair_hint": _plan_repair_message("\n".join(repair_errors)),
                "gen_attempts": 0,
                "plan_facts": fact_payloads,
                "planning_model_elapsed_sec": planning_elapsed,
            }
        dialect = _sql_dialect(llm_service)
        if apply_grouped_metric_order(result.plans, dialect=dialect):
            fact_models = _plan_fact_models(result.plans, dialect=dialect)
            fact_payloads = [item.model_dump(mode="json") for item in fact_models]
        with session_scope() as session:
            persist_query_decision(
                session,
                run_id=run_id,
                decision=result.decision.model_dump(mode="json"),
                plans=result.plans,
                hard_gate_report={
                    "status": "passed",
                    "plan_count": len(result.plans),
                },
                risk_assessment={},
                plan_facts=fact_payloads,
                planning_status="reviewing",
            )
        return {
            **state,
            "planning_decision": "ready",
            "active_candidate": {
                "plans": result.plans,
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


# ── Nodes (agentic batch loop) ───────────────────────────────────────────────


def ground_entities_node(state: NlqState) -> NlqState:
    """Resolve bindings from local knowledge snapshots; never query the datasource."""
    llm_service = _llm_service(state)
    record_id = getattr(llm_service.record, "id", None) or state.get("record_id")
    with log_span(
        operate=OperationEnum.GROUND_ENTITIES,
        record_id=record_id,
        ai_modal_id=getattr(llm_service.chat_question, "ai_modal_id", None),
        ai_modal_name=getattr(llm_service.chat_question, "ai_modal_name", None),
        local_operation=True,
        graph_node="ground_entities",
        title_key="chat.log.GROUND_ENTITIES",
    ) as span:
        bindings = resolve_entity_bindings(
            state.get("knowledge_matches") or [],
        )
        span["payload"] = {
            "candidates": bindings.get("candidates") or [],
            "resolved": bindings.get("resolved") or {},
            "ambiguous": bindings.get("ambiguous") or {},
            "match_count": bindings.get("match_count") or 0,
        }
        match_count = int(bindings.get("match_count") or 0)
        if match_count:
            span.set_summary("chat.audit.entities_grounded", count=match_count)
        else:
            span.set_summary("chat.audit.entities_none")
        return {
            **state,
            "entity_bindings": bindings,
        }


def _extract_title_from_sql_answer(raw_text: str, plans: list[dict[str, Any]]) -> str:
    """Best-effort conversation title from plans or raw model JSON (brief)."""
    for item in plans or []:
        b = (item.get("brief") or "").strip()
        if b:
            return b
    try:
        js = extract_nested_json(raw_text or "")
        if not js:
            return ""
        data = orjson.loads(js)
        items = data if isinstance(data, list) else [data]
        for it in items:
            if isinstance(it, dict):
                b = (it.get("brief") or "").strip()
                if b:
                    return b
    except Exception:
        pass
    return ""


def _maybe_update_chat_brief(llm_service: Any, sink: StreamSink, title: str) -> None:
    """Write sidebar title once per chat (works on plan success or validate fail)."""
    if not getattr(llm_service, "change_title", False):
        return
    title = (title or "").replace(chr(10), " ").replace(chr(13), " ").strip()[:20]
    if not title:
        title = _generation_question(llm_service)[:20]
    if not title or not llm_service.record or not llm_service.record.chat_id:
        return
    try:
        with session_scope() as session:
            rename_chat(
                session,
                RenameChat(
                    id=llm_service.record.chat_id,
                    brief=title,
                    brief_generate=True,
                ),
            )
        sink.event({"type": "brief", "brief": title})
        llm_service.change_title = False
    except Exception:
        traceback.print_exc()


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
            physical = repair_physical_plans(
                llm_service,
                previous_plans=previous_plans,
                validation_error=repair,
                timeout_seconds=_planning_call_timeout_sec(),
                attempt=gen_attempts + 1,
            )
            span["token_usage"] = physical.usage
            span["reasoning_content"] = physical.reasoning
            span.set_model_calls(physical.model_calls)
            span["payload"] = {
                "status": ("valid" if physical.plans else "needs_repair"),
                "attempt": gen_attempts + 1,
                "error": None if physical.plans else "No safe repaired plan",
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
                results[0] = {
                    "index": 0,
                    "error": format_error_message(e),
                    "failure": prepared[0].get("prep_failure")
                    or classify_failure(e, step_index=0),
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
                    results[idx] = {
                        "index": idx,
                        "error": format_error_message(e),
                        "failure": prepared[idx].get("prep_failure")
                        or classify_failure(e, step_index=idx),
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


def generate_charts_node(state: NlqState) -> NlqState:
    """Generate presentation only for a structurally accepted candidate."""
    llm_service = _llm_service(state)
    sink = StreamSink.from_state(state)
    accepted_candidate = dict(state.get("accepted_candidate") or {})
    batch_results = accepted_candidate.get("results") or []
    base = 0
    prompt_schema = str(getattr(llm_service.chat_question, "db_schema", "") or "")

    try:
        charts: list[dict[str, Any]] = []
        presentations: list[ResultPresentation] = []
        # Isolate chart prompt base so multi-chart does not pollute history
        base_chart_messages = list(getattr(llm_service, "chart_message", []) or [])

        # Stable order by original plan index
        ordered = sorted(
            [r for r in batch_results if isinstance(r, dict)],
            key=lambda x: int(x.get("index") or 0),
        )
        # Pad gaps if needed
        by_idx = {int(r.get("index") or 0): r for r in ordered}
        max_i = max(by_idx.keys()) if by_idx else -1

        for i in range(max_i + 1):
            entry = by_idx.get(i)
            gidx = base + i
            if entry is None or entry.get("error"):
                presentation: ResultPresentation = {
                    "title": "Error",
                    "columns": [],
                }
                chart = _table_chart(presentation)
                presentations.append(presentation)
                charts.append(chart)
                continue

            plan_dict = entry.get("plan") or {}
            result = entry.get("result") or {}
            chart_type = (plan_dict.get("chart_type") or "table") or "table"
            fields = result.get("fields") or []
            data = result.get("data") or []
            brief = plan_dict.get("brief") or ""
            presentation_title = plan_dict.get("presentation_title") or brief
            presentation = build_result_presentation(
                fields,
                title=presentation_title,
                projection_requirements=plan_dict.get("projection_requirements") or {},
                schema_text=prompt_schema,
            )
            presentations.append(presentation)

            if chart_type == "table":
                with log_span(
                    operate=OperationEnum.GENERATE_CHART,
                    record_id=llm_service.record.id,
                    local_operation=True,
                    graph_node="generate_charts",
                    title_key="chat.log.GENERATE_CHART",
                    step_index=state.get("step_index", 0),
                    unit_index=gidx,
                    brief="table",
                ) as span:
                    chart = _table_chart(presentation)
                    span.set_detail(
                        {
                            "chart_type": "table",
                            "column_count": len(presentation.get("columns") or []),
                        }
                    )
                    span.set_summary("chat.audit.table_ready")
                charts.append(chart)
                continue

            try:
                sample_md = DataFormat.rows_to_markdown_table(
                    fields,
                    data,
                    max_rows=5,
                    title="\n【Sample Data】(first 5 rows, for chart reference)",
                )
                schema_text = ""
                if llm_service.out_ds_instance:
                    schema_text, _ = llm_service.out_ds_instance.get_db_schema(
                        llm_service.ds.id,
                        llm_service.retrieval_question,
                        table_list=plan_dict.get("tables"),
                    )
                if sample_md:
                    schema_text = (schema_text or "") + "\n" + sample_md

                # chart_user_prompt consumes chat_question.sql
                llm_service.chat_question.sql = (
                    plan_dict.get("format_statement")
                    or plan_dict.get("sql")
                    or llm_service.chat_question.sql
                )
                llm_service.chart_message = list(base_chart_messages)

                sink.event(
                    {
                        "type": "step-chart-result",
                        "index": gidx,
                        "content": "",
                        "reasoning_content": "",
                    }
                )

                with session_scope() as session:
                    full_chart_text = ""
                    for chunk in generate_chart(
                        llm_service,
                        session,
                        chart_type,
                        schema_text,
                        step_index=state.get("step_index", 0),
                        unit_index=gidx,
                        graph_node="generate_charts",
                    ):
                        full_chart_text += chunk.get("content") or ""
                        sink.token(
                            content=chunk.get("content") or "",
                            reasoning_content=chunk.get("reasoning_content") or "",
                            event_type="step-chart-result",
                            metadata={"index": gidx},
                        )
                    chart = parse_chart(
                        res=full_chart_text,
                        fields=fields,
                    )
                    chart["title"] = presentation["title"]
                    chart["columns"] = chart_columns(presentation)
            except Exception as chart_exc:
                SQLBotLogUtil.warning(
                    f"Chart generation fallback to table at step {gidx}: {chart_exc}"
                )
                chart = _table_chart(presentation)
                with log_span(
                    operate=OperationEnum.GENERATE_CHART,
                    record_id=llm_service.record.id,
                    local_operation=True,
                    graph_node="generate_charts",
                    title_key="chat.log.GENERATE_CHART",
                    step_index=state.get("step_index", 0),
                    unit_index=gidx,
                    brief="table fallback",
                ) as fallback_span:
                    fallback_span.set_detail(
                        {
                            "chart_type": "table",
                            "source": "chart_fallback",
                            "column_count": len(presentation.get("columns") or []),
                        }
                    )
                    fallback_span.set_summary("chat.audit.table_ready")
                    fallback_span.mark_degraded(str(chart_exc))
            charts.append(chart)

        # Restore base chart messages after batch
        llm_service.chart_message = list(base_chart_messages)

        published_plans = [
            {
                **plan,
                "presentation": presentations[index],
            }
            for index, plan in enumerate(accepted_candidate.get("plans") or [])
            if index < len(presentations)
        ]
        steps = _merge_batch_into_steps(
            [],
            published_plans,
            list(batch_results),
            charts,
            entity_bindings=state.get("entity_bindings"),
        )
        return {
            **state,
            "accepted_candidate": {
                **accepted_candidate,
                "plans": published_plans,
                "charts": charts,
                "steps": steps,
                "outcome": accepted_candidate.get("outcome")
                or outcome_from_steps(steps),
            },
            "active_candidate": {},
        }
    except Exception as e:
        return _fail(state, llm_service.record.id, e)


_SUMMARY_PROMPT = """\
根据已执行结果写一段简要分析，直接回答用户问题。

{steps_summary}

用户原问题：{question}

要求：
- 只用 3～6 句；不要 SQL、不要 JSON、不要分节标题。
- 若限制中写明“仅展示前 N 行”或“没有全量合计”，必须先说明这是展示窗口，禁止把窗口内合计写成累计、总额或全量。
- 引用关键数字；结果被截断时，若提供了全量合计必须引用全量合计，并说明表格只是展示窗口；没有全量合计时明确说当前数字不能当作全量。
- 没有证据不要推断业务原因。
- 使用会话语言：{target_language}。
"""


def _brief_result_facts(assessments: list[dict[str, Any]]) -> str:
    """Compact facts for the user-facing summary — not a second SQL dump."""
    if not assessments:
        return "（尚无已执行查询）"
    lines: list[str] = []
    for item in assessments:
        index = int(item.get("index") or 0) + 1
        rows = int(item.get("row_count") or 0)
        truncated = bool(item.get("truncated"))
        limit = item.get("limit") or rows
        truncated_note = f"，仅展示前 {limit} 行" if truncated else ""
        fields = ", ".join(str(name) for name in (item.get("fields") or [])[:12])
        lines.append(f"查询{index}: {rows} 行{truncated_note}")
        if fields:
            lines.append(f"字段: {fields}")
        coverage_totals = item.get("coverage_totals")
        has_full_totals = isinstance(coverage_totals, dict) and bool(coverage_totals)
        metrics = item.get("metrics") or {}
        if isinstance(metrics, dict) and metrics and not truncated:
            parts = []
            for name, stats in list(metrics.items())[:6]:
                if not isinstance(stats, dict):
                    continue
                if stats.get("count"):
                    parts.append(f"{name} sum={stats.get('sum')}")
            if parts:
                lines.append("指标: " + "; ".join(parts))
        if has_full_totals:
            bits = [f"{name}={value}" for name, value in coverage_totals.items()]
            lines.append("全量合计: " + "; ".join(bits[:8]))
        elif truncated:
            lines.append(
                f"限制: 仅展示前 {limit} 行，没有全量合计；窗口内数字不能写成累计或全量"
            )
        limitations = item.get("limitations") or []
        lines.extend(f"限制: {note}" for note in limitations[:3])
    return "\n".join(lines)


def _summary_messages(
    steps_summary: str,
    question: str,
    quality: dict[str, Any],
    *,
    target_language: str,
) -> list[Any]:
    del quality  # Quality stays on the stamp; do not ask the model to rewrite it.
    return [
        SystemMessage(
            content=(
                "你负责用几句话解释已执行查询结果。"
                "不要生成或修改 SQL，不要返回 JSON。"
                f"所有面向用户的内容必须使用当前会话语言：{target_language}。"
            )
        ),
        HumanMessage(
            _SUMMARY_PROMPT.format(
                steps_summary=steps_summary,
                question=question,
                target_language=target_language,
            )
        ),
    ]


def _extract_summary_text(response_text: str) -> str:
    """Accept plain Markdown and tolerate providers that still wrap it in JSON."""
    text = (response_text or "").strip()
    if not text:
        return ""
    if text.startswith("{") or text.lower().startswith("```json"):
        json_str = extract_nested_json(text)
        try:
            data = orjson.loads(json_str) if json_str else None
            if isinstance(data, dict):
                return str(data.get("text") or "").strip()
        except Exception:
            return ""
    return text


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


def summarize_answer_node(state: NlqState) -> NlqState:
    """Summarize an already accepted candidate; never gate its publication."""
    llm_service = _llm_service(state)
    candidate = dict(state.get("accepted_candidate") or {})
    steps = list(candidate.get("steps") or [])
    if not steps:
        return _fail(
            state,
            getattr(llm_service.record, "id", None),
            SingleMessageError("No accepted result to summarize"),
        )
    assessments = _assess_all_steps(steps)
    candidate_quality = candidate.get("quality")
    if not isinstance(candidate_quality, dict):
        return _fail(
            state,
            getattr(llm_service.record, "id", None),
            SingleMessageError("Accepted candidate is missing its quality report"),
        )
    quality = cast(ResultQuality, candidate_quality)
    question = _generation_question(llm_service)
    record_id = getattr(llm_service.record, "id", None) or state.get("record_id")
    meta: dict[str, Any] = {"used_llm": False}
    with log_span(
        operate=OperationEnum.ANALYSIS,
        record_id=record_id,
        ai_modal_id=getattr(llm_service.chat_question, "ai_modal_id", None),
        ai_modal_name=getattr(llm_service.chat_question, "ai_modal_name", None),
        local_operation=False,
        graph_node="summarize_answer",
        title_key="chat.log.ANALYSIS",
        brief="结果总结",
        step_index=state.get("step_index"),
    ) as span:
        try:
            target_language = str(
                getattr(llm_service.chat_question, "lang", "") or "简体中文"
            )
            summary_messages = _summary_messages(
                _brief_result_facts(assessments),
                question,
                quality,
                target_language=target_language,
            )
            response: AIMessage = llm_service.llm.bind(
                temperature=0, max_tokens=600
            ).invoke(summary_messages)
            meta["used_llm"] = True
            meta["token_usage"] = usage_from_response(response)
            analysis_text = _extract_summary_text(
                message_content_text(response.content)
            )
            if not analysis_text:
                analysis_text = _fallback_analysis(
                    assessments,
                    reason="总结模型未返回可用正文",
                    target_language=target_language,
                )
            span["token_usage"] = meta["token_usage"]
            span.set_model_context([*summary_messages, response])
            span["payload"] = {
                "fallback": not bool(
                    _extract_summary_text(message_content_text(response.content))
                ),
                "chars": len(analysis_text),
            }
            span.set_summary("chat.audit.response_ready")
        except Exception as exc:
            SQLBotLogUtil.error(f"summarize_answer_node error: {exc}")
            analysis_text = _fallback_analysis(
                assessments,
                reason=f"总结模型调用异常：{exc}",
                target_language=str(
                    getattr(llm_service.chat_question, "lang", "") or "简体中文"
                ),
            )
            span.mark_degraded(str(exc))
            span["payload"] = {"fallback": True, "chars": len(analysis_text)}
            span.set_summary("chat.audit.response_ready")
    return {
        **state,
        "analysis_text": analysis_text,
        "accepted_candidate": {
            **candidate,
            "steps": steps,
            "quality": quality,
        },
        "active_candidate": {},
    }


def _turn_source_datasets(state: NlqState) -> list[dict[str, Any]]:
    existing = [
        dict(item)
        for item in state.get("source_datasets") or []
        if isinstance(item, dict) and item.get("status") in {"succeeded", "degraded"}
    ]
    if existing:
        return existing
    candidate = dict(state.get("accepted_candidate") or {})
    datasets: list[dict[str, Any]] = []
    for index, step in enumerate(candidate.get("steps") or []):
        if not isinstance(step, dict) or step.get("error"):
            continue
        result = step.get("result") if isinstance(step.get("result"), dict) else {}
        datasets.append(
            _dataset_capabilities(
                {
                    "dataset_id": str(step.get("dataset_id") or f"dataset_{index + 1}"),
                    "status": "degraded"
                    if (state.get("outcome") or {}).get("status") == "degraded"
                    else "succeeded",
                    "required": bool(step.get("required", True)),
                    "title": str(step.get("brief") or ""),
                    "sql": str(step.get("format_statement") or step.get("sql") or ""),
                    "fields": list(result.get("fields") or []),
                    "rows": list(result.get("data") or []),
                    "row_count": int(
                        result.get("row_count") or len(result.get("data") or [])
                    ),
                    "truncated": bool(result.get("truncated")),
                    "limit": result.get("limit"),
                    "truncation_reason": result.get("truncation_reason"),
                    "presentation": step.get("presentation"),
                    "chart": step.get("chart"),
                }
            )
        )
    return datasets


def _run_downstream_agent(
    state: NlqState, *, task_kind: Literal["analysis", "prediction"]
) -> NlqState:
    llm_service = _llm_service(state)
    candidate_steps = list((state.get("accepted_candidate") or {}).get("steps") or [])
    required_failures = [
        item
        for item in candidate_steps
        if isinstance(item, dict)
        and bool(item.get("required", True))
        and bool(item.get("error"))
    ]
    if required_failures:
        return _fail(
            state,
            state.get("record_id"),
            SingleMessageError(
                f"{task_kind} was not started because a required source dataset failed"
            ),
        )
    datasets = _turn_source_datasets(state)
    if not datasets:
        return _fail(
            state,
            state.get("record_id"),
            SingleMessageError(f"{task_kind} requires a usable result dataset"),
        )
    if task_kind == "prediction" and not any(
        item.get("has_time_field")
        and item.get("has_numeric_measure")
        and int(item.get("valid_points") or 0) >= 6
        for item in datasets
    ):
        return _fail(
            state,
            state.get("record_id"),
            SingleMessageError(
                "Prediction requires a time series with at least 6 valid points"
            ),
        )
    sink = StreamSink.from_state(state)
    operate = (
        OperationEnum.ANALYSIS
        if task_kind == "analysis"
        else OperationEnum.PREDICT_DATA
    )
    try:
        with log_span(
            operate=operate,
            record_id=llm_service.record.id,
            ai_modal_id=llm_service.chat_question.ai_modal_id,
            ai_modal_name=llm_service.chat_question.ai_modal_name,
            local_operation=False,
            graph_node=f"{task_kind}_agent",
            title_key=(
                "chat.log.ANALYSIS"
                if task_kind == "analysis"
                else "chat.log.PREDICT_DATA"
            ),
        ) as span:
            result = run_turn_agent(
                llm_service,
                task_kind=task_kind,
                question=str(llm_service.record.question or ""),
                datasets=datasets,
                on_stream=lambda chunk: sink.token(
                    content="",
                    reasoning_content=chunk.get("reasoning_content") or "",
                    event_type=f"{task_kind}-reasoning",
                ),
            )
            span.set_usage(result.usage)
            span["reasoning_content"] = result.reasoning
            span.set_model_context(result.model_messages)
            span.set_detail(
                {
                    "dataset_ids": [item.get("dataset_id") for item in datasets],
                    "chars": len(result.content),
                    "forecast_rows": len(result.forecast_rows),
                }
            )
            span.set_summary("chat.audit.response_ready")
        source_records = tuple(
            dict.fromkeys(
                int(item.get("source_record_id"))
                for item in datasets
                if item.get("source_record_id")
            )
        )
        if task_kind == "analysis":
            answer = {
                "kind": "analysis",
                "content": result.content,
                "dataset_ids": [str(item.get("dataset_id") or "") for item in datasets],
                "source_datasets": datasets,
                "source_record_ids": list(source_records),
                "assumptions": [],
                "quality": (state.get("outcome") or {}).get("quality"),
            }
            status = "succeeded"
        else:
            status = "succeeded" if result.forecast_rows else "degraded"
            answer = {
                "kind": "prediction",
                "content": result.content,
                "dataset_id": str(datasets[0].get("dataset_id") or ""),
                "forecast_rows": result.forecast_rows,
                "source_datasets": datasets,
                "source_record_ids": list(source_records),
                "assumptions": [],
                "quality": (state.get("outcome") or {}).get("quality"),
            }
        return {
            **state,
            "terminal_answer": answer,
            "analysis_text": result.content,
            "outcome": (
                successful_outcome()
                if status == "succeeded"
                else {**successful_outcome(), "status": "degraded"}
            ),
        }
    except Exception as exc:
        return _fail(state, state.get("record_id"), exc)


def analysis_agent_node(state: NlqState) -> NlqState:
    return _run_downstream_agent(state, task_kind="analysis")


def prediction_agent_node(state: NlqState) -> NlqState:
    return _run_downstream_agent(state, task_kind="prediction")


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


def complete_node(state: NlqState) -> NlqState:
    """Commit the terminal snapshot, then publish the same answer to clients."""
    llm_service = _llm_service(state)
    sink = StreamSink.from_state(state)
    json_result: dict[str, Any] = dict(state.get("json_result") or {})
    analysis_text = state.get("analysis_text") or ""
    return_img = bool(state.get("return_img", True))

    terminal_answer = state.get("terminal_answer") or {}
    if terminal_answer:
        terminal_status: Literal["succeeded", "degraded"] = (
            "degraded"
            if (state.get("outcome") or {}).get("status") == "degraded"
            else "succeeded"
        )
        with session_scope() as session:
            finalize_run(
                session,
                run_id=str(state["run_id"]),
                status=terminal_status,
                current_node=None,
                result_quality=terminal_answer.get("quality"),
                record_snapshot={
                    "answer": terminal_answer,
                    "analysis": orjson.dumps(
                        {"content": terminal_answer.get("content") or ""}
                    ).decode(),
                    "terminal": True,
                },
            )
        content = str(terminal_answer.get("content") or "")
        if content:
            sink.event({"type": terminal_answer.get("kind"), "content": content})
            if sink.mode == "markdown":
                sink.text(content + "\n\n")
        sink.event({"type": "finish"})
        if sink.mode == "json":
            sink.json_result(
                {
                    "success": True,
                    "status": terminal_status,
                    "answer": terminal_answer,
                }
            )
        return {**state, "outcome": state.get("outcome") or successful_outcome()}

    # Query-only stops before execution and publishes the already validated plan.
    # Every executed result, including QUERY_DATA, must arrive here through the
    # same decide_next gate and therefore lives in accepted_candidate.
    if _finish_step_value(state) <= int(ChatFinishStep.GENERATE_QUERY.value):
        source_candidate = dict(state.get("active_candidate") or {})
        updated_steps = _merge_batch_into_steps(
            [],
            list(source_candidate.get("plans") or []),
            list(source_candidate.get("results") or []),
            list(source_candidate.get("charts") or []),
            entity_bindings=state.get("entity_bindings"),
        )
    else:
        source_candidate = dict(state.get("accepted_candidate") or {})
        updated_steps = list(source_candidate.get("steps") or [])
    # Ensure every successful step has one canonical presentation and a chart
    # adapter (MCP QUERY_DATA / table fallback).
    for step in updated_steps:
        if step.get("error"):
            continue
        fields = (step.get("result") or {}).get("fields") or []
        presentation = step.get("presentation")
        if not isinstance(presentation, dict):
            presentation = build_result_presentation(
                fields,
                title=step.get("presentation_title") or step.get("brief") or "",
                projection_requirements=step.get("projection_requirements") or {},
                schema_text=str(
                    getattr(llm_service.chat_question, "db_schema", "") or ""
                ),
            )
            step["presentation"] = presentation
        if step.get("chart"):
            continue
        step["chart"] = _table_chart(
            cast(ResultPresentation, presentation),
        )

    outcome = outcome_from_steps(
        updated_steps,
        planned_count=len(source_candidate.get("plans") or []),
    )
    state_outcome = state.get("outcome")
    if (
        not updated_steps
        and state_outcome
        and state_outcome.get("status") in {"failed", "limit_reached"}
    ):
        # The rejected candidate is intentionally absent from answer data, but
        # its authoritative terminal failure must still reach persistence/API.
        outcome = cast(RunOutcome, dict(state_outcome))
    elif state_outcome and state_outcome.get("status") in {"success", "degraded"}:
        outcome["status"] = state_outcome["status"]
    quality = (state_outcome or {}).get("quality") or source_candidate.get("quality")
    if isinstance(quality, dict):
        outcome["quality"] = cast(ResultQuality, quality)
    json_result["success"] = outcome_is_success(outcome)
    json_result["status"] = outcome["status"]
    if "quality" in outcome:
        json_result["quality"] = outcome["quality"]
    if outcome["failures"]:
        json_result["failures"] = outcome["failures"]

    failure_message = next(
        (
            str(item.get("message"))
            for item in outcome.get("failures") or []
            if item.get("message")
        ),
        "Conversation completed without a usable result",
    )
    run_status: Literal["succeeded", "degraded", "failed"] = (
        "failed"
        if not outcome_is_success(outcome)
        else "degraded"
        if outcome["status"] == "degraded"
        else "succeeded"
    )
    try:
        with session_scope() as session:
            finalize_run(
                session,
                run_id=str(state["run_id"]),
                status=run_status,
                current_node=None,
                result_quality=outcome.get("quality"),
                record_snapshot=_record_snapshot_values(
                    updated_steps,
                    analysis_text,
                    finish=True,
                    outcome=outcome,
                    execution_mode=cast(
                        Literal["verified", "unverified"],
                        state.get("execution_mode") or "verified",
                    ),
                ),
                error_summary=failure_message if run_status == "failed" else None,
            )
    except Exception as exc:
        traceback.print_exc()
        return fail_node(
            cast(
                NlqState,
                {
                    **state,
                    "accepted_candidate": {
                        **source_candidate,
                        "steps": updated_steps,
                    },
                    "error": format_error_message(exc),
                    "outcome": failed_outcome(exc),
                },
            )
        )

    # Async knowledge capture — never fails the published answer.
    if outcome_is_success(outcome):
        try:
            _enqueue_knowledge_capture(state, llm_service, outcome, updated_steps)
        except Exception as _cap_exc:  # noqa: BLE001
            SQLBotLogUtil.warning(f"knowledge capture enqueue failed: {_cap_exc}")

    # The persisted snapshot is the source of truth. Publish analysis only
    # after that commit so live SSE and a subsequent page refresh cannot
    # observe different terminal answers.
    if analysis_text:
        sink.event({"type": "analysis", "content": analysis_text})
        if sink.mode == "markdown":
            sink.text(analysis_text + "\n\n")

    if not outcome_is_success(outcome):
        sink.error(failure_message)
        return {
            **state,
            "accepted_candidate": {
                **source_candidate,
                "steps": updated_steps,
            },
            "json_result": json_result,
            "error": failure_message,
            "outcome": outcome,
        }

    # Optional last-chart image (MCP markdown / json)
    if return_img and updated_steps:
        last_step = updated_steps[-1]
        chart = last_step.get("chart") or {}
        result = last_step.get("result") or {}
        if chart.get("type") and chart.get("type") != "table" and result:
            try:
                image_url, _error = request_picture(
                    llm_service.record.chat_id,
                    llm_service.record.id,
                    chart,
                    format_json_data(
                        {
                            "fields": result.get("fields", []),
                            "fields_info": result.get("fields_info"),
                            "data": result.get("data", []),
                        }
                    ),
                )
                if image_url:
                    json_result["image_url"] = image_url
                if sink.mode == "markdown" and image_url:
                    sink.text(f"![{chart.get('type')}]({image_url})")
            except Exception:
                if sink.mode == "markdown":
                    sink.text("generate or fetch chart picture error.\n\n")

    sink.event({"type": "finish"})
    if sink.mode == "json":
        sink.json_result(json_result)

    completed_candidate: CandidateBatch = {
        **source_candidate,
        "steps": updated_steps,
        "outcome": outcome,
    }
    if "quality" in outcome:
        completed_candidate["quality"] = outcome["quality"]
    return {
        **state,
        "json_result": json_result,
        "accepted_candidate": completed_candidate,
        "outcome": outcome,
    }


def fail_node(state: NlqState) -> NlqState:
    """Persist the canonical empty NLQ answer before emitting terminal failure."""
    error = str(state.get("error") or "unknown error")
    public_error = str(state.get("public_error") or public_error_message(error))
    current_outcome = state.get("outcome")
    outcome = (
        cast(RunOutcome, dict(current_outcome))
        if current_outcome and current_outcome.get("status") != "running"
        else failed_outcome(error)
    )
    if "quality" not in outcome:
        outcome["quality"] = build_overall_quality([])
    sink = StreamSink.from_state(state)
    try:
        with session_scope() as session:
            finalize_run(
                session,
                run_id=str(state["run_id"]),
                status="failed",
                current_node=None,
                result_quality=outcome.get("quality"),
                record_snapshot=_record_snapshot_values(
                    [],
                    "",
                    finish=True,
                    outcome=outcome,
                    public_error=public_error,
                    execution_mode=cast(
                        Literal["verified", "unverified"],
                        state.get("execution_mode") or "verified",
                    ),
                ),
                error_summary=error,
            )
    except Exception as exc:
        # Failure reporting must still reach the client when persistence itself
        # is unavailable; the shared terminal node remains the single emitter.
        SQLBotLogUtil.error(f"persist NLQ failure snapshot failed: {exc}")
    sink.error(public_error)
    return {**state, "error": error, "outcome": outcome}


# ── Routers ──────────────────────────────────────────────────────────────────


def route_after_planning(
    state: NlqState,
) -> Literal["await_clarification", "review_query", "generate_queries", "fail"]:
    if state.get("error"):
        return "fail"
    if state.get("planning_decision") == "clarify":
        return "await_clarification"
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
