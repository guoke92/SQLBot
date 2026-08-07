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
ChatRecord.data stores::

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
from sqlbot_xpack.custom_prompt.models.custom_prompt_model import CustomPromptTypeEnum

from apps.chat.answer_payload import build_answer_payload
from apps.chat.binding_resolver import (
    apply_confirmed_entity_bindings,
    binding_resource_names,
    resolve_entity_bindings,
    retain_binding_resources,
)
from apps.chat.constants import DYNAMIC_DS_TYPES
from apps.chat.contract.issues import blocking_issues
from apps.chat.curd.chat import rename_chat
from apps.chat.models.chat_model import ChatFinishStep, OperationEnum, RenameChat
from apps.chat.plan_context import (
    render_plan_context,
    wrap_plan_context,
)
from apps.chat.plan_policy import (
    MAX_BATCH_ROUNDS,
    MAX_PLAN_REGEN,
    MAX_QUERIES_PER_BATCH,
    ROW_LIMIT,
)
from apps.chat.planning import parse_query_generation
from apps.chat.presentation import (
    ResultPresentation,
    build_result_presentation,
    chart_columns,
)
from apps.chat.query_contract import GroupRequirement, OutputRequirement, QueryContract
from apps.chat.result_data import format_json_data
from apps.chat.result_quality import (
    CompletionEvidence,
    ExecutionStatus,
    build_overall_quality,
    build_step_quality,
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
from apps.chat.semantic_intent import (
    intent_context_from_payload,
    new_intent_context,
    public_intent_payload,
)
from apps.chat.simple_sql import try_compile_simple_batch
from apps.chat.steps.chart import generate_chart
from apps.chat.steps.clarification import (
    assess_semantic_intent,
    assessment_contract_rows,
    render_assumptions,
)
from apps.chat.steps.custom_prompt import match_custom_prompts
from apps.chat.steps.datasource import select_datasource, validate_history_ds
from apps.chat.steps.knowledge import get_compiled_knowledge, match_knowledge
from apps.chat.steps.messages import (
    assemble_prompt_messages,
    retrieve_prompt_schema,
)
from apps.chat.steps.observability import log_span
from apps.chat.steps.permissions import (
    DYNAMIC_SUBSQL_PREFIX,
    generate_assistant_dynamic_sql,
    generate_filter,
)
from apps.chat.steps.persist import parse_chart
from apps.chat.steps.sql import generate_sql
from apps.chat.steps.training import match_training
from apps.knowledge.bind import apply_bound_calibers_to_intent, render_bind_lock_line
from apps.chat.task.llm import LLMService, request_picture
from apps.chat.time_intent import TemporalParse, infer_time_intent
from apps.conversation.messages import message_content_text
from apps.conversation.observability import end_log, trigger_log_error
from apps.conversation.outcome import (
    ResultQuality,
    RunOutcome,
    awaiting_input_outcome,
    blocked_outcome,
    classify_failure,
    failed_outcome,
    format_error_message,
    outcome_from_steps,
    outcome_is_success,
    running_outcome,
)
from apps.conversation.record import persist_snapshot
from apps.conversation.runtime import submit_query
from apps.conversation.session import session_scope
from apps.conversation.sink import StreamSink
from apps.conversation.state import RunState
from apps.conversation.turn import fail_node as fail_turn_node
from apps.conversation.usage import usage_from_response
from apps.datasource.access import AccessScope, resolve_access_scope
from apps.datasource.crud.permission import is_normal_user
from apps.datasource.models.datasource import CoreDatasource
from apps.protocol import QueryPlan
from apps.protocol.base import CAP_ROW_PERMISSION
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
    contract_status: Literal["verified", "partial", "unsupported"]


class NlqState(RunState, total=False):
    """Agentic batch loop state.

    This is the canonical state contract for the production chat graph.
    """

    llm_service: LLMService
    finish_step: ChatFinishStep
    return_img: bool
    json_result: dict[str, Any]

    # batch loop
    step_index: int  # current batch iteration (0-based)
    active_candidate: CandidateBatch
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
    compiled_knowledge: dict[str, Any]  # CompiledKnowledge dump; Bind/apply_log
    access_scope: AccessScope | None
    temporal_parse: TemporalParse  # deterministic evidence; never executable truth
    intent_context: dict[str, Any]
    query_contract: QueryContract
    outcome: RunOutcome


# ── Helpers ──────────────────────────────────────────────────────────────────


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
    """Persist a capture job and best-effort drain one item (failure-isolated)."""
    from apps.chat.steps.scope import match_scope
    from apps.knowledge.capture import (
        build_turn_snapshot,
        enqueue_capture_job,
        run_capture_worker_once,
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
    snapshot = build_turn_snapshot(
        record_id=int(llm_service.record.id),
        oid=int(calculate_oid or 1),
        ds_id=calculate_ds_id if assistant_id is None else None,
        question=_generation_question(llm_service),
        intent_context=state.get("intent_context")
        or getattr(llm_service.chat_question, "intent_context", None),
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
    # Best-effort immediate drain; restart path can drain remaining jobs.
    try:
        with session_scope() as session:
            run_capture_worker_once(session)
    except Exception as exc:  # noqa: BLE001
        SQLBotLogUtil.warning(f"knowledge capture drain failed: {exc}")


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
    traceback.print_exc()
    error_msg = format_error_message(exc)
    return {
        **state,
        "error": error_msg,
        "outcome": failed_outcome(exc),
    }


def _finish_step_value(state: NlqState) -> int:
    fs = state.get("finish_step") or ChatFinishStep.GENERATE_CHART
    try:
        return int(fs.value if hasattr(fs, "value") else fs)
    except Exception:
        return int(ChatFinishStep.GENERATE_CHART.value)


def _context_steps(state: NlqState) -> list[dict[str, Any]]:
    """Return the preceding atomic candidate used as repair evidence."""
    candidate = state.get("rejected_candidate")
    return list(candidate.get("steps") or []) if candidate else []


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
        if isinstance(v, (int, float)):
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


def _contract_role_hints(
    contract: QueryContract | None,
) -> dict[str, Literal["metric", "dimension"]]:
    """Project confirmed physical roles for direct result-field matches."""
    hints: dict[str, Literal["metric", "dimension"]] = {}
    for requirement in contract.requirements if contract else ():
        if isinstance(requirement, OutputRequirement):
            label_role: Literal["metric", "dimension"] | None = (
                "dimension" if requirement.operation == "value" else "metric"
            )
            fields = [requirement.field]
        elif isinstance(requirement, GroupRequirement):
            label_role = "dimension"
            fields = [requirement.field]
        else:
            label_role = None
            fields = []
        normalized_label = str(requirement.label or "").strip().casefold()
        if label_role and normalized_label:
            hints[normalized_label] = label_role

        for field in fields:
            if label_role is None:
                continue
            role = label_role
            normalized = field.field.strip().casefold()
            if normalized:
                if role == "metric" or normalized not in hints:
                    hints[normalized] = role
    return hints


def _assess_step_quality(
    step: dict[str, Any],
    index: int,
    *,
    contract: QueryContract | None = None,
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
        _contract_role_hints(contract),
    )

    null_rates: dict[str, float] = {}
    metrics: dict[str, Any] = {}
    col_stats: dict[str, Any] = {}
    limitations: list[str] = []
    if truncated:
        limitations.append(
            f"本次仅查询并展示前 {window['row_count']} 行；"
            "未查询结果总数，行数上限不是 SQL 修复条件"
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
    }


def _assess_all_steps(
    all_steps: list[dict[str, Any]],
    *,
    contract: QueryContract | None = None,
) -> list[dict[str, Any]]:
    return [
        {
            **_assess_step_quality(step, index, contract=contract),
            "structural_issues": list(step.get("_structural_issues") or []),
        }
        for index, step in enumerate(all_steps or [])
    ]


def _format_assessment_block(assessments: list[dict[str, Any]]) -> str:
    blocks: list[str] = []
    for a in assessments:
        row_count = int(a.get("row_count") or 0)
        row_text = (
            f"- 行数: 仅查询并展示前 {row_count} 行"
            if a.get("truncated")
            else f"- 行数: {row_count}"
        )
        lines = [
            f"### 查询{a['index'] + 1}"
            + (f"（{a['brief']}）" if a.get("brief") else ""),
            row_text,
            f"- 字段: {', '.join(a.get('fields') or []) or '（无）'}",
        ]
        if a.get("null_rates"):
            nr = ", ".join(
                f"{k}={v:.0%}" for k, v in (a.get("null_rates") or {}).items()
            )
            lines.append(f"- 维度空值率: {nr}")
        if a.get("metrics"):
            ms = []
            for k, st in (a.get("metrics") or {}).items():
                if st.get("count"):
                    ms.append(
                        f"{k}: sum={st.get('sum')} min={st.get('min')} max={st.get('max')}"
                    )
                else:
                    ms.append(f"{k}: 无数值")
            metric_label = "展示样本指标" if a.get("truncated") else "指标"
            lines.append(f"- {metric_label}: {'; '.join(ms)}")

        # Column stats: unique values, top-N for categoricals, min/max for
        # temporal/numeric fields
        col_stats = a.get("column_stats") or {}
        if col_stats:
            stat_parts: list[str] = []
            for fname, cs in col_stats.items():
                if not isinstance(cs, dict):
                    continue
                if cs.get("type") == "numeric":
                    stat_parts.append(
                        f"{fname}: unique={cs.get('unique')} "
                        f"min={cs.get('min')} max={cs.get('max')} "
                        f"avg={cs.get('avg')} median={cs.get('median')}"
                    )
                elif cs.get("type") == "temporal":
                    stat_parts.append(
                        f"{fname}: unique={cs.get('unique')} "
                        f"min={cs.get('min')} max={cs.get('max')}"
                    )
                elif cs.get("type") == "categorical":
                    top = cs.get("top_values") or []
                    top_str = ", ".join(
                        f"{tv['value']}({tv['count']})" for tv in top[:6]
                    )
                    stat_parts.append(
                        f"{fname}: unique={cs.get('unique')} top=[{top_str}]"
                    )
                else:
                    stat_parts.append(f"{fname}: unique={cs.get('unique')}")
            if stat_parts:
                lines.append("- 列统计: " + "; ".join(stat_parts))

        # Data sample: actual rows so LLM can reason about real values
        sample = a.get("data_sample") or []
        if sample:
            lines.append(f"- 数据样本（前{len(sample)}行）:")
            for row in sample[:5]:
                row_str = ", ".join(f"{k}={v}" for k, v in row.items())
                lines.append(f"  {row_str}")
            if len(sample) > 5:
                lines.append(f"  ... 共{len(sample)}行")

        sql = (a.get("sql") or "").strip()
        if sql:
            sql_show = sql if len(sql) <= 4000 else sql[:4000] + " …"
            lines.append(f"- SQL:\n```sql\n{sql_show}\n```")
        limitations = a.get("limitations") or []
        if limitations:
            lines.append("- 展示限制:")
            lines.extend(f"  - {item}" for item in limitations)
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def _summarize_steps(
    all_steps: list[dict[str, Any]],
    assessments: list[dict[str, Any]] | None = None,
) -> str:
    """Quality-aware step summary for decide / continue context."""
    assessments = (
        assessments if assessments is not None else _assess_all_steps(all_steps)
    )
    if not assessments:
        return "（尚无已执行查询）"
    header = (
        "下列为已通过执行与结构门禁的查询及其**需求完成度**摘要。"
        "查询行数上限只影响返回窗口，不代表 SQL 错误；截断结果中的统计均为样本统计，"
        "不得解释为全量合计。需求完成度评分不参与发布门禁，空结果和数据形态只作为"
        "独立观察，不自动扣分。\n"
    )
    return header + "\n\n" + _format_assessment_block(assessments)


def _format_generation_context(assessments: list[dict[str, Any]]) -> str:
    """Compact prior-attempt context for SQL repair or extension generation."""
    blocks: list[str] = []
    for assessment in assessments:
        row_count = int(assessment.get("row_count") or 0)
        lines = [
            f"### 查询{assessment['index'] + 1}"
            + (f"（{assessment['brief']}）" if assessment.get("brief") else ""),
            (
                f"- 结果: 仅查询并展示前 {row_count} 行"
                if assessment.get("truncated")
                else f"- 结果: {row_count} 行"
            ),
            f"- 字段: {', '.join(assessment.get('fields') or []) or '（无）'}",
        ]
        structural_issues = assessment.get("structural_issues") or []
        if structural_issues:
            lines.append("- 必须修复:")
            lines.extend(
                f"  - {validation_issue_prompt_text(item)}"
                for item in structural_issues
            )
        limitations = assessment.get("limitations") or []
        if limitations:
            lines.append("- 展示限制（不得据此重写 SQL）:")
            lines.extend(f"  - {item}" for item in limitations)
        sql = (assessment.get("sql") or "").strip()
        if sql:
            sql_show = sql if len(sql) <= 1200 else sql[:1200] + " …"
            lines.append(f"- 已执行 SQL:\n```sql\n{sql_show}\n```")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks) or "（尚无已执行查询）"


def _repair_instruction(assessments: list[dict[str, Any]], question: str) -> str:
    reasons: list[str] = []
    empty_or_zero = False
    for a in assessments:
        if int(a.get("row_count") or 0) == 0 or a.get("error"):
            empty_or_zero = True
        if a.get("error"):
            reasons.append(f"查询{a['index'] + 1}: {a['error']}")
        for item in a.get("structural_issues") or []:
            reasons.append(
                f"查询{a['index'] + 1}: {validation_issue_prompt_text(item)}"
            )
    issue_text = "\n".join(f"- {item}" for item in reasons) or "- 未提供确定性结构原因"
    anti_empty = ""
    if empty_or_zero:
        anti_empty = (
            "7. **禁止改得更空**：禁止在已有 0 行/近空结果上继续收紧等值过滤；"
            "应核对标准实体值、时间列与 join 键；不得把诊断候选自动并入 IN，"
            "或保持可出数的结构并在总结中说明局限。\n"
        )
    return (
        "上一轮候选未通过执行或结构门禁，请**改写 SQL** 后重新查询，不要只重复同样语句。\n"
        f"用户原问题：{question}\n"
        f"质检问题：\n{issue_text}\n"
        "改写要求：\n"
        "1. 时间字段对齐用户语义（完成/创建/更新等），结合表结构注释选择，禁止机械套用固定时间列。\n"
        "2. 若报错字段不存在：必须去掉或改写该列，只使用 schema 中的列。\n"
        "3. 维度过滤按实体绑定（IN/eq），禁止只用口语短词过窄等值；关联用维表主键与事实表外键。\n"
        "4. 多事实表对比时，统一维度并对齐粒度；不得只挂一侧事实表的时间维。\n"
        "5. 聚合分析不要用无意义的 SQL LIMIT 充当前 N 页全貌；明细展示必须限制时，"
        "ORDER BY 应使用业务指标。平台 query_limit 不属于 SQL 修复范围。\n"
        "6. 仍返回系统约定的 JSON（单对象或数组）。\n"
        f"{anti_empty}"
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
    intent_ready: bool,
    plan_validated: bool,
    contract_status: Literal["verified", "partial", "unsupported"],
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
            "intent_ready": intent_ready,
            "plan_validated": plan_validated,
            "contract_status": contract_status,
            "execution_status": execution_status,
            "result_structure_valid": (
                execution_status == "success"
                and not bool(assessment.get("structural_issues"))
            ),
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
    """Build a complete deterministic report when summary generation fails."""
    returned_rows = sum(int(item.get("row_count") or 0) for item in assessments)
    truncated = any(bool(item.get("truncated")) for item in assessments)
    query_count = len(assessments)
    window_note = (
        f"{query_count} 个查询共返回 {returned_rows} 行；"
        "至少一个查询仅展示上限内数据，未查询结果总数。"
        if truncated
        else f"{query_count} 个查询共返回 {returned_rows} 行。"
    )
    limitation = (
        "结果受查询行数窗口限制，下面的样本指标不能视为全量合计。"
        if truncated
        else "未检测到平台查询行数截断。"
    )
    if "english" in target_language.casefold() or target_language.casefold() == "en":
        return "\n".join(
            [
                "## Conclusion",
                f"The query completed. {query_count} query result(s) returned "
                f"{returned_rows} displayed row(s).",
                "",
                "## SQL basis",
                _format_assessment_block(assessments),
                "",
                "## Data interpretation",
                window_note,
                "",
                "## Data quality and limitations",
                limitation,
                f"Generated summary was unavailable: {reason}",
                "",
                "## Recommendation",
                "Use the displayed result together with its confidence score.",
            ]
        )
    return "\n".join(
        [
            "## 结论",
            f"查询已完成。{window_note}",
            "",
            "## SQL 生成依据与解释",
            "以下内容来自已执行 SQL、结果字段和自动质检信息：",
            _format_assessment_block(assessments),
            "",
            "## 数据解读",
            window_note,
            "",
            "## 数据质量与局限",
            limitation,
            f"文字总结生成异常：{reason}",
            "",
            "## 建议",
            "请结合已展示结果和可信度评分使用；如需调整业务口径，可继续说明期望范围。",
        ]
    )


def _persist_record_snapshot(
    llm_service: LLMService,
    all_steps: list[dict[str, Any]],
    analysis_text: str = "",
    *,
    finish: bool = False,
    outcome: RunOutcome | None = None,
) -> None:
    """Persist the accepted NLQ answer projection."""
    if outcome is None:
        raise ValueError("Terminal NLQ snapshot requires an outcome")
    payload = build_answer_payload(all_steps, analysis_text, outcome)
    primary = all_steps[0] if all_steps and finish else {}
    primary_sql = primary.get("format_statement") or primary.get("sql") or None
    chart = primary.get("chart")
    re_exec = primary.get("re_exec")
    error: str | None = None
    if finish and outcome and outcome["status"] in {"failed", "limit_reached"}:
        failures = outcome.get("failures") or []
        error = str(
            failures[0].get("message")
            if failures
            else "Conversation completed without a usable result"
        )

    with session_scope() as session:
        persist_snapshot(
            session,
            llm_service.record.id,
            data=orjson.dumps(payload).decode(),
            sql=primary_sql,
            chart=orjson.dumps(chart).decode() if chart else None,
            re_exec=(
                re_exec
                if isinstance(re_exec, str)
                else orjson.dumps(re_exec).decode()
                if re_exec is not None
                else None
            ),
            analysis=(
                orjson.dumps({"content": analysis_text}).decode()
                if analysis_text and finish
                else None
            ),
            intent_context=getattr(
                getattr(llm_service, "chat_question", None),
                "intent_context",
                None,
            ),
            terminal=finish,
            error=error,
        )


def _apply_row_permissions(
    llm_service: LLMService,
    session: Any,
    plan_dict: dict[str, Any],
    access_scope: AccessScope | None = None,
) -> QueryPlan:
    """Return a plan copy with row-permission SQL applied (main thread only)."""
    qp: QueryPlan = plan_dict["plan"]
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
    llm_service = state["llm_service"]
    sink = StreamSink.from_state(state)
    record = llm_service.get_record()
    return_img = bool(state.get("return_img", True))
    json_result: dict[str, Any] = {"success": True}

    try:
        sink.event({"type": "id", "id": record.id})
        if record.regenerate_record_id:
            sink.event(
                {
                    "type": "regenerate_record_id",
                    "regenerate_record_id": record.regenerate_record_id,
                }
            )
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
            "access_scope": None,
            "temporal_parse": {},
            "intent_context": (
                llm_service.chat_question.intent_context
                or public_intent_payload(
                    new_intent_context(llm_service.chat_question.question or "")
                )
            ),
            "outcome": running_outcome(),
            "finish_step": state.get("finish_step") or ChatFinishStep.GENERATE_CHART,
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
    llm_service = state["llm_service"]
    sink = StreamSink.from_state(state)

    with session_scope() as session:
        try:
            if not llm_service.ds:
                for chunk in select_datasource(llm_service, session):
                    sink.event(
                        {
                            "content": chunk.get("content"),
                            "reasoning_content": chunk.get("reasoning_content"),
                            "type": "datasource-result",
                        }
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
            return {**state, "record": llm_service.record}
        except Exception as e:
            return _fail(state, llm_service.record.id, e)


def recall_knowledge_node(state: NlqState) -> NlqState:
    llm_service = state["llm_service"]
    oid, ds_id = _ds_scope(llm_service)
    with session_scope() as session:
        try:
            has_joins = False
            if ds_id is not None:
                try:
                    from apps.datasource.profiling.service import get_published_relations

                    rels = get_published_relations(session, ds_id=int(ds_id))
                    has_joins = bool(rels)
                except Exception:
                    has_joins = False
            matches = match_knowledge(
                llm_service,
                session,
                oid,
                ds_id,
                access_scope=state.get("access_scope"),
                stage="assess",
                has_confirmed_joins=has_joins,
            )
            compiled = get_compiled_knowledge(llm_service)
            return {
                **state,
                "knowledge_matches": [match.model_dump() for match in matches],
                "compiled_knowledge": (
                    compiled.model_dump(mode="json") if compiled else {}
                ),
                "record": llm_service.record,
            }
        except Exception as e:
            return _fail(state, llm_service.record.id, e)


def parse_temporal_evidence_node(state: NlqState) -> NlqState:
    """Capture deterministic temporal evidence without creating contract state."""
    llm_service = state.get("llm_service")
    question = (
        getattr(llm_service, "generation_question", "")
        if llm_service
        else state.get("question", "")
    )
    temporal_parse = infer_time_intent(str(question or ""))
    if not temporal_parse:
        return state
    return {**state, "temporal_parse": temporal_parse}


def resolve_access_scope_node(state: NlqState) -> NlqState:
    """Resolve datasource visibility once for every downstream NLQ stage."""
    llm_service = state["llm_service"]
    with session_scope() as session:
        try:
            access_scope = resolve_access_scope(
                session,
                current_user=llm_service.current_user,
                ds=llm_service.ds,
            )
            return {
                **state,
                "access_scope": access_scope,
                "record": llm_service.record,
            }
        except Exception as exc:
            return _fail(state, llm_service.record.id, exc)


def match_training_node(state: NlqState) -> NlqState:
    """Defer Example injection until after assess (assemble_context).

    Assess must not receive large SQL examples; Compile Exemplify runs only
    once the semantic gate is ready.
    """
    llm_service = state["llm_service"]
    # Clear any stale training so assess/clarification cannot see examples.
    if getattr(llm_service, "chat_question", None) is not None:
        llm_service.chat_question.data_training = ""
    return {**state, "record": llm_service.record}


def match_custom_prompts_node(state: NlqState) -> NlqState:
    llm_service = state["llm_service"]
    oid, ds_id = _ds_scope(llm_service)
    with session_scope() as session:
        try:
            match_custom_prompts(
                llm_service, session, CustomPromptTypeEnum.GENERATE_SQL, oid, ds_id
            )
            return {**state, "record": llm_service.record}
        except Exception as e:
            return _fail(state, llm_service.record.id, e)


def retrieve_schema_node(state: NlqState) -> NlqState:
    """Retrieve permission-scoped schema before the semantic gate."""
    llm_service = state["llm_service"]
    with session_scope() as session:
        try:
            resource_names = retrieve_prompt_schema(
                llm_service,
                session,
                required_resource_names=binding_resource_names(
                    state.get("entity_bindings") or {}
                ),
                access_scope=state.get("access_scope"),
            )
            return {
                **state,
                "entity_bindings": retain_binding_resources(
                    state.get("entity_bindings") or {},
                    resource_names,
                ),
                "record": llm_service.record,
            }
        except Exception as e:
            return _fail(state, llm_service.record.id, e)


def assess_clarity_node(state: NlqState) -> NlqState:
    """Block SQL generation until every material semantic choice is confirmed."""
    llm_service = state["llm_service"]
    record_id = getattr(llm_service.record, "id", None) or state.get("record_id")
    try:
        intent_payload = (
            state.get("intent_context")
            or llm_service.chat_question.intent_context
            or public_intent_payload(
                new_intent_context(llm_service.chat_question.question or "")
            )
        )
        # Prefill certified Caliber slots before assess (user evidence still wins).
        from apps.knowledge.compile.bundle import CompiledKnowledge

        compiled_raw = state.get("compiled_knowledge") or {}
        compiled = None
        if compiled_raw:
            try:
                compiled = CompiledKnowledge.model_validate(compiled_raw)
            except Exception:
                compiled = get_compiled_knowledge(llm_service)
        else:
            compiled = get_compiled_knowledge(llm_service)
        if compiled is not None:
            intent_payload, bind_extra = apply_bound_calibers_to_intent(
                intent_payload if isinstance(intent_payload, dict) else {},
                compiled,
            )
            if bind_extra:
                compiled = compiled.model_copy(
                    update={
                        "apply_log": list(compiled.apply_log) + list(bind_extra)
                    }
                )
                llm_service.compiled_knowledge = compiled
        context = intent_context_from_payload(intent_payload)
        # L-5: surface confirmed-join clarify hints from compile into reasoning
        join_hint = ""
        if compiled and compiled.clarify_hints:
            join_hint = "\n".join(f"- {h}" for h in compiled.clarify_hints)
        with log_span(
            operate=OperationEnum.CLARIFY_INTENT,
            record_id=record_id,
            ai_modal_id=llm_service.chat_question.ai_modal_id,
            ai_modal_name=llm_service.chat_question.ai_modal_name,
            local_operation=context.status == "ready",
            graph_node="assess_clarity",
            brief="确认查询口径",
        ) as span:
            if context.status == "ready":
                assessed, usage, reasoning, attempts = context, {}, "", []
            else:
                assessment_result = assess_semantic_intent(
                    llm_service,
                    context=context,
                    bindings=state.get("entity_bindings") or {},
                    temporal_parse=state.get("temporal_parse") or {},
                )
                assessed = assessment_result.context
                usage = assessment_result.usage
                reasoning = assessment_result.reasoning
                attempts = assessment_result.attempts
            payload = public_intent_payload(assessed)
            if assessed.status == "blocked":
                display_reasoning = (
                    "\n".join(assessed.blocking_messages) or assessed.summary
                )
            else:
                display_reasoning = (
                    reasoning.strip()
                    or "\n".join(f"- {issue.reason}" for issue in assessed.issues)
                    or assessed.summary
                )
            # A choice made without the user must reach the user, not only the
            # execution log.
            display_reasoning = "\n\n".join(
                part
                for part in (
                    display_reasoning,
                    render_assumptions(
                        assessed.assumptions, getattr(llm_service, "trans", None)
                    ),
                )
                if part
            )
            bind_line = ""
            if compiled and compiled.bound_calibers:
                bind_line = render_bind_lock_line(compiled.bound_calibers)
            if join_hint:
                display_reasoning = "\n\n".join(
                    part
                    for part in (
                        "连接提示：\n" + join_hint if join_hint else "",
                        display_reasoning,
                    )
                    if part
                )
            if bind_line:
                display_reasoning = "\n\n".join(
                    part for part in (bind_line, display_reasoning) if part
                )
            span["payload"] = {
                "status": assessed.status,
                "summary": assessed.summary,
                "assessment_attempt_count": len(attempts),
                "assessment_attempts": attempts,
                "contract_requirements": assessment_contract_rows(assessed),
                "issues": [issue.model_dump(mode="json") for issue in assessed.issues],
                "questions": [
                    {
                        "id": question.id,
                        "title": question.title,
                        "recommended_option_ids": question.recommended_option_ids,
                    }
                    for question in assessed.questions
                ],
                "blocking_reasons": assessed.blocking_reasons,
                "contract_issues": [
                    item.model_dump(mode="json") for item in assessed.contract_issues
                ],
                # Inferences resolved on the user's behalf, including any the
                # gate had to drop to stay executable.
                "assumptions": [
                    item.model_dump(mode="json") for item in assessed.assumptions
                ],
                "knowledge_apply": (
                    compiled.knowledge_apply_payload() if compiled else []
                ),
                "clarify_hints": list(compiled.clarify_hints) if compiled else [],
            }
            span["token_usage"] = usage
            span["reasoning_content"] = display_reasoning
            if display_reasoning:
                StreamSink.from_state(state).event(
                    {
                        "type": "clarification-reasoning",
                        "content": display_reasoning,
                    }
                )
        llm_service.chat_question.intent_context = payload
        llm_service.record.intent_context = payload
        # Clarification/blocked terminals persist in ``complete_intent``.
        # Ready continues into SQL generation, so commit the semantic state now;
        # a later generation failure must not leave history at "evaluating".
        if assessed.status == "ready":
            with session_scope() as session:
                persist_snapshot(
                    session,
                    llm_service.record.id,
                    intent_context=payload,
                )
        return {
            **state,
            "intent_context": payload,
            "compiled_knowledge": (
                compiled.model_dump(mode="json") if compiled else state.get("compiled_knowledge") or {}
            ),
            "record": llm_service.record,
        }
    except Exception as exc:
        return _fail(state, record_id, exc)


def assemble_context_node(state: NlqState) -> NlqState:
    """Assemble SQL/chart prompts only after the semantic gate is ready."""
    llm_service = state["llm_service"]
    try:
        context = intent_context_from_payload(state["intent_context"])
        if context.status != "ready" or context.contract is None:
            raise ValueError("Semantic gate is ready without a frozen query contract")
        query_contract = context.contract
        # Examples only after assess — sole Exemplify channel for generate.
        oid, ds_id = _ds_scope(llm_service)
        with session_scope() as session:
            match_training(llm_service, session, oid, ds_id)
        assemble_prompt_messages(llm_service)
        compiled = getattr(llm_service, "compiled_knowledge", None)
        updates: dict[str, Any] = {
            "query_contract": query_contract,
            "record": llm_service.record,
        }
        if compiled is not None and hasattr(compiled, "model_dump"):
            updates["compiled_knowledge"] = compiled.model_dump(mode="json")
        return {**state, **updates}
    except Exception as exc:
        return _fail(state, llm_service.record.id, exc)


def complete_intent_node(state: NlqState) -> NlqState:
    """Persist and publish a clarification or non-actionable intent terminal."""
    llm_service = state["llm_service"]
    sink = StreamSink.from_state(state)
    context = intent_context_from_payload(state["intent_context"])
    payload = public_intent_payload(context)
    if context.status == "needs_clarification":
        outcome = awaiting_input_outcome()
        event_type = "clarification"
        error = None
    else:
        message = "; ".join(context.blocking_messages) or "当前信息不足，无法生成查询"
        outcome = blocked_outcome(message)
        event_type = (
            "contract-preparation-blocked"
            if blocking_issues(context.contract_issues)
            else "clarification-blocked"
        )
        error = None

    try:
        with session_scope() as session:
            persist_snapshot(
                session,
                llm_service.record.id,
                intent_context=payload,
                terminal=True,
                error=error,
            )
        _maybe_update_chat_brief(
            llm_service,
            sink,
            context.original_question,
        )
    except Exception as exc:
        return _fail(state, llm_service.record.id, exc)

    sink.event(
        {
            "type": event_type,
            "record_id": llm_service.record.id,
            "intent_context": payload,
        }
    )
    if sink.mode == "markdown":
        if context.status == "blocked":
            sink.text(
                "## 查询暂无法继续\n\n"
                + "\n".join(f"- {reason}" for reason in context.blocking_messages)
                + "\n"
            )
        else:
            lines = ["## 生成查询前需要确认\n"]
            for index, question in enumerate(context.questions, start=1):
                lines.append(f"{index}. **{question.title}**")
                if question.reason:
                    lines.append(f"   {question.reason}")
                for option in question.options:
                    recommended = (
                        "（推荐）"
                        if option.id in question.recommended_option_ids
                        else ""
                    )
                    lines.append(
                        f"   - `{option.id}` {option.label}{recommended}"
                        + (f"：{option.impact}" if option.impact else "")
                    )
                if question.allow_custom:
                    lines.append("   - 也可以提供自定义口径")
            sink.text("\n".join(lines) + "\n")
    sink.event(
        {
            "type": "finish",
            "id": llm_service.record.id,
            "status": outcome["status"],
        }
    )
    if sink.mode == "json":
        sink.json_result(
            {
                "success": outcome_is_success(outcome),
                "status": outcome["status"],
                "record_id": llm_service.record.id,
                "intent_context": payload,
            }
        )
    return {
        **state,
        "intent_context": payload,
        "outcome": outcome,
        "record": llm_service.record,
    }


# ── Nodes (agentic batch loop) ───────────────────────────────────────────────


def ground_entities_node(state: NlqState) -> NlqState:
    """Resolve bindings from local knowledge snapshots; never query the datasource."""
    llm_service = state["llm_service"]
    record_id = getattr(llm_service.record, "id", None) or state.get("record_id")
    with log_span(
        operate=OperationEnum.GROUND_ENTITIES,
        record_id=record_id,
        ai_modal_id=getattr(llm_service.chat_question, "ai_modal_id", None),
        ai_modal_name=getattr(llm_service.chat_question, "ai_modal_name", None),
        local_operation=True,
        graph_node="ground_entities",
    ) as span:
        bindings = resolve_entity_bindings(
            state.get("knowledge_matches") or [],
        )
        bindings = apply_confirmed_entity_bindings(
            bindings,
            state.get("intent_context"),
        )
        span["payload"] = {
            "candidates": bindings.get("candidates") or [],
            "resolved": bindings.get("resolved") or {},
            "match_count": bindings.get("match_count") or 0,
        }
        return {
            **state,
            "entity_bindings": bindings,
            "record": llm_service.record,
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
        "【计划校验失败 — 基于上一版 SQL 做最小修改】",
        base,
        "要求：",
        "1. 列名/表名必须来自 schema；关联用维表主键与事实表外键（勿臆造 *_id 列名）。",
        "2. 保留上一版中已正确的表、过滤和聚合结构，只修复校验指出的问题。",
        "3. 多事实聚合每段只定义一次；缺侧用 UNION 去重的维键集合再 LEFT JOIN，禁止重复扫描模拟 FULL OUTER。",
        "4. 直接输出协议 JSON（对象或数组，带 brief），不要讨论候选方案、规则取舍或子查询效率。",
        "5. 须继续遵守 <plan-context>：实体 eq/IN、边界、时间口径与共享粒度。",
    ]
    return chr(10).join(parts) + chr(10)


def _mark_generate_validation_failed(
    llm_service: LLMService,
    *,
    message: str,
    attempt: int,
) -> None:
    """Persist validation outcome in the existing GENERATE_QUERY ChatLog."""
    log = llm_service.current_logs.get(OperationEnum.GENERATE_QUERY)
    if not log:
        return
    try:
        with session_scope() as session:
            messages = list(log.messages or [])
            if messages and isinstance(messages[0], dict):
                head = dict(messages[0])
                if head.get("sqlbot_span_meta") and head.get("content"):
                    try:
                        meta = orjson.loads(head["content"])
                        payload = dict(meta.get("payload") or {})
                        payload.update(
                            {
                                "validation_status": "failed",
                                "validation_attempt": attempt,
                                "validation_error": message[:1200],
                            }
                        )
                        meta["payload"] = payload
                        head["content"] = orjson.dumps(meta).decode()
                        messages[0] = head
                        end_log(
                            session=session,
                            log=log,
                            full_message=messages,
                            reasoning_content=log.reasoning_content,
                            token_usage=log.token_usage or {},
                        )
                    except Exception:
                        pass
            trigger_log_error(session, log)
    except Exception:
        # Observability must not affect retry/failure behavior.
        SQLBotLogUtil.warning("Failed to mark GENERATE_QUERY validation error")


def _attach_plan_context_for_generate(
    llm_service: LLMService,
    state: NlqState,
    *,
    repair: str = "",
    extra_sections: list[str] | None = None,
    include_playbook: bool = True,
) -> str:
    """Render PlanContext once and stash on chat_question for build_user_prompt."""
    body = render_plan_context(
        entity_bindings=state.get("entity_bindings"),
        contract=state.get("query_contract"),
        include_playbook=include_playbook,
        repair=repair,
        extra_sections=extra_sections,
    )
    wrapped = wrap_plan_context(body)
    try:
        llm_service.chat_question.plan_context = wrapped
    except Exception:
        pass
    return wrapped


def _needs_multi_fact_playbook(llm_service: LLMService) -> bool:
    """Inject join-grain guidance whenever planning spans multiple resources."""
    names = {
        str(name).strip().lower()
        for name in (getattr(llm_service, "table_name_list", None) or [])
        if str(name).strip()
    }
    return len(names) >= 2


def generate_queries_node(state: NlqState) -> NlqState:
    """Plan SQL queries for the current batch.

    Plan-time validate failures set ``repair_hint`` + ``gen_attempts`` and let
    ``route_after_queries`` loop back (no hard-fail until budget exhausted).

    This node assembles one PlanContext block into the user prompt via
    ``chat_question.plan_context``.
    """
    llm_service = state["llm_service"]
    sink = StreamSink.from_state(state)
    step_index = state.get("step_index", 0)
    context_steps = _context_steps(state)
    base = 0
    json_result: dict[str, Any] = dict(state.get("json_result") or {"success": True})
    gen_attempts = int(state.get("gen_attempts") or 0)

    try:
        # Reuse assess CompiledKnowledge — do NOT re-recall calibers/examples here.
        # Examples already injected via assemble_context → match_training.
        # Caliber Bind already applied to draft at assess; frozen contract is SoT.
        prior_compiled = state.get("compiled_knowledge") or {}
        extra_lock = ""
        try:
            from apps.knowledge.compile.bundle import CompiledKnowledge

            if isinstance(prior_compiled, dict) and prior_compiled:
                prior_obj = CompiledKnowledge.model_validate(prior_compiled)
                extra_lock = render_bind_lock_line(prior_obj.bound_calibers) or ""
        except Exception as _compile_exc:  # noqa: BLE001
            SQLBotLogUtil.warning(f"reuse compiled_knowledge failed: {_compile_exc}")
            extra_lock = ""

        sink.event(
            {
                "type": "batch-start",
                "index": step_index,
                "base_index": base,
                "gen_attempts": gen_attempts,
            }
        )

        repair = (state.get("repair_hint") or "").strip()
        extra_sections: list[str] = []
        if extra_lock:
            extra_sections.append(extra_lock)

        # Inherit entity bindings from previous round when current round has none
        # (follow-up like "只查看今年的吧" has no org name in question)
        current_bindings = state.get("entity_bindings") or {}
        if step_index > 0 and context_steps and not current_bindings.get("resolved"):
            prev_bindings = {}
            for step in reversed(context_steps):
                eb = step.get("_entity_bindings") or {}
                if eb.get("resolved"):
                    prev_bindings = eb
                    break
            if prev_bindings.get("resolved"):
                state = {**state, "entity_bindings": prev_bindings}
                SQLBotLogUtil.info(
                    "inherited entity_bindings from previous round: "
                    f"{list((prev_bindings.get('resolved') or {}).keys())}"
                )

        # Subsequent rounds are repairs only. Successful queries are terminal;
        # an autonomous model must not reinterpret the question and invent
        # additional deliverables after execution.
        if step_index > 0 and context_steps:
            assessments = _assess_all_steps(
                context_steps,
                contract=state.get("query_contract"),
            )
            extra_sections.append(
                "## 已执行查询（仅用于本轮改写或补充）\n"
                + _format_generation_context(assessments)
            )
            if repair:
                extra_sections.append("## 改写指令\n" + repair)

        # Prefer a deterministic single-table filter over an LLM round-trip.
        # Repair rounds always use the model: the compiler does not rewrite.
        batch_parse = None
        full_sql_text = ""
        generation_source = "llm"
        if not repair:
            chat_question = getattr(llm_service, "chat_question", None)
            intent_context = getattr(chat_question, "intent_context", None)
            question = str(
                getattr(chat_question, "generation_question", "")
                or getattr(chat_question, "question", "")
                or ""
            )
            default_limit = (
                _ROW_LIMIT if llm_service.enable_sql_row_limit else None
            )
            batch_parse = try_compile_simple_batch(
                state.get("query_contract"),
                llm_service,
                question=question,
                intent_context=intent_context,
                default_limit=default_limit,
            )
            if not (batch_parse and batch_parse.plans):
                batch_parse = None
            else:
                generation_source = "compiled"
                full_sql_text = str(batch_parse.plans[0].get("sql") or "")
                with log_span(
                    operate=OperationEnum.GENERATE_QUERY,
                    record_id=getattr(llm_service.record, "id", None),
                    ai_modal_id=getattr(
                        getattr(llm_service, "chat_question", None),
                        "ai_modal_id",
                        None,
                    ),
                    ai_modal_name=getattr(
                        getattr(llm_service, "chat_question", None),
                        "ai_modal_name",
                        None,
                    ),
                    graph_node="generate_queries",
                    step_index=step_index,
                    gen_attempts=gen_attempts,
                    initial_payload={
                        "generation_source": "compiled",
                        "sql": full_sql_text[:2000],
                    },
                ):
                    try:
                        sink.event(
                            {
                                "content": full_sql_text,
                                "type": "step-sql-result",
                                "index": base,
                                "generation_source": "compiled",
                            }
                        )
                    except Exception:
                        pass

        if batch_parse is None:
            _attach_plan_context_for_generate(
                llm_service,
                state,
                repair=repair if step_index == 0 else "",
                extra_sections=extra_sections,
                include_playbook=_needs_multi_fact_playbook(llm_service),
            )
            try:
                sink.event(
                    {
                        "type": "plan-context",
                        "content": getattr(
                            llm_service.chat_question, "plan_context", ""
                        )
                        or "",
                    }
                )
            except Exception:
                pass

            full_sql_text = ""
            try:
                with session_scope() as session:
                    for chunk in generate_sql(
                        llm_service,
                        session,
                        step_index=step_index,
                        gen_attempts=gen_attempts,
                        graph_node="generate_queries",
                    ):
                        content = chunk.get("content") or ""
                        reasoning = chunk.get("reasoning_content") or ""
                        full_sql_text += content
                        sink.event(
                            {
                                "content": content,
                                "reasoning_content": reasoning,
                                "type": "step-sql-result",
                                "index": base,
                            }
                        )
            finally:
                # Avoid sticky plan_context on later non-SQL prompts.
                try:
                    llm_service.chat_question.plan_context = ""
                except Exception:
                    pass

            max_batch = state.get("max_batch_size") or _MAX_BATCH_SIZE
            batch_parse = parse_query_generation(
                full_sql_text,
                llm_service,
                max_batch_size=max_batch,
                query_contract=state.get("query_contract"),
            )
            generation_source = "llm"

        plans = list(batch_parse.plans)
        refusal = batch_parse.error_message

        _maybe_update_chat_brief(
            llm_service, sink, _extract_title_from_sql_answer(full_sql_text, plans)
        )

        candidate: CandidateBatch = {
            "plans": plans,
            "plan_validated": batch_parse.plan_validated,
            "contract_status": batch_parse.contract_status,
        }
        if plans and batch_parse.contract_message:
            # Advisory: execute anyway.  The scoreboard reads contract_status.
            SQLBotLogUtil.warning(
                f"plan contract shortfall accepted: "
                f"{batch_parse.contract_message[:240]}"
            )
        if generation_source == "compiled":
            SQLBotLogUtil.info(
                f"plan compiled from contract without LLM: {full_sql_text[:240]}"
            )

        if not plans:
            msg = refusal or "Failed to generate any valid SQL queries"
            attempts = gen_attempts + 1
            repair_msg = _plan_repair_message(msg)
            _mark_generate_validation_failed(
                llm_service, message=msg, attempt=attempts
            )
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
            if attempts <= MAX_PLAN_REGEN:
                return {
                    **state,
                    "json_result": json_result,
                    "active_candidate": {},
                    "repair_hint": repair_msg,
                    "gen_attempts": attempts,
                    "record": llm_service.record,
                    "error": None,
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
                "record": llm_service.record,
            }

        sink.event(
            {
                "type": "batch-plans",
                "index": step_index,
                "base_index": base,
                "count": len(candidate["plans"]),
            }
        )

        return {
            **state,
            "json_result": json_result,
            "active_candidate": candidate,
            "repair_hint": "",
            "gen_attempts": 0,
            "record": llm_service.record,
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
    llm_service = state["llm_service"]
    active_candidate = dict(state.get("active_candidate") or {})
    plans = list(active_candidate.get("plans") or [])
    base = 0

    if not plans:
        return _fail(
            state, llm_service.record.id, SingleMessageError("No plans to execute")
        )

    # 1) Prepare executable plans (permissions) on main thread
    prepared: list[dict[str, Any]] = []
    with session_scope() as session:
        for i, plan_dict in enumerate(plans):
            try:
                qp = _apply_row_permissions(
                    llm_service,
                    session,
                    plan_dict,
                    state.get("access_scope"),
                )
                prepared.append({**plan_dict, "plan": qp, "index": i})
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
        with log_span(
            operate=OperationEnum.EXECUTE_QUERY,
            record_id=record_id,
            local_operation=True,
            graph_node="execute_queries",
            step_index=state.get("step_index", 0),
            unit_index=gidx,
            brief=brief,
            initial_payload={
                "count": 0,
                "sql": sql_show[:2000],
                "index": gidx,
            },
        ) as span:
            try:
                if plan_dict.get("prep_error"):
                    raise SingleMessageError(plan_dict["prep_error"])
                qp: QueryPlan = plan_dict["plan"]
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
                        code = result.get("code_value")
                        msg = (
                            f"Query failed (code={code})"
                            if code is not None
                            else "Query failed"
                        )
                        raise SingleMessageError(msg)
                    result = _normalize_result_data(result, llm_service)
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
                    }
                    return {
                        "index": idx,
                        "result": result,
                        "plan": plan_dict,
                        "re_exec": result.get("re_exec")
                        or getattr(qr, "re_exec", None),
                    }
            except Exception as exc:
                span["error"] = True
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
    llm_service = state["llm_service"]
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
                contract=state.get("query_contract"),
                projection_requirements=plan_dict.get("projection_requirements") or {},
                schema_text=prompt_schema,
            )
            presentations.append(presentation)

            if chart_type == "table":
                chart = _table_chart(presentation)
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
                        sink.event(
                            {
                                "content": chunk.get("content") or "",
                                "reasoning_content": chunk.get("reasoning_content")
                                or "",
                                "type": "step-chart-result",
                                "index": gidx,
                            }
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
                log = llm_service.current_logs.get(OperationEnum.GENERATE_CHART)
                if log is not None:
                    try:
                        with session_scope() as session:
                            trigger_log_error(session, log)
                    except Exception:
                        SQLBotLogUtil.warning(
                            f"Failed to mark chart fallback log at step {gidx}"
                        )
                chart = _table_chart(presentation)
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
            "record": llm_service.record,
        }
    except Exception as e:
        return _fail(state, llm_service.record.id, e)


_SUMMARY_PROMPT = """\
你是数据分析助手。请只根据已执行结果生成最终总结，不能再生成或修改 SQL。

{steps_summary}

平台已经使用确定性规则冻结了以下需求完成度报告：
{quality_summary}

用户原问题：{question}

直接输出完整 Markdown 报告，不要输出 JSON、action 或额外说明。
不得修改评分、等级、各指标得分或数据观察，也不得将总结作为结果发布门禁。
只能解释已执行结果和确定性元数据：
- MIN/MAX 只表示数值最小/最大，不得擅自解释成业务上的更优/更差；
- 多个金额相等、空值或单侧为 0 时，只陈述观察；没有证据不得推断业务原因；
- 描述数值范围或主要分布时必须同时披露样本中的空值情况；
- 面向用户的字段称谓优先采用“业务名称(field_name)”，不要只罗列技术字段名。

报告必须包含：
## 结论
直接回答用户问题。

## SQL 生成依据与解释
说明事实表、共享粒度、关联键、时间范围、过滤、聚合和排序依据。

## 数据解读
引用实际返回的数据。若结果达到 query_limit，必须写明仅查询并展示了前 N 行、
未查询总数；样本的 sum/avg 不能解释为全量统计。

## 数据质量与局限
区分 SQL 本身的限制与平台查询行数窗口，明确尚不能从数据中得出的结论。

## 建议
只给出 1～3 条与本次结果直接相关的后续分析建议。平台固定仅查询并展示前 N 行时，
不得建议取消/提高行数窗口或额外查询总记录数；用户确实要求全量统计时，应建议另行生成
聚合结果，而不是扩大明细展示窗口。
"""


def _summary_messages(
    steps_summary: str,
    question: str,
    quality: dict[str, Any],
    *,
    target_language: str,
) -> list[Any]:
    quality_summary = orjson.dumps(quality).decode()
    return [
        SystemMessage(
            content=(
                "你负责根据已执行查询结果生成完整 Markdown 总结。"
                "不要生成或修改 SQL，不要返回 JSON。"
                f"所有面向用户的内容必须使用当前会话语言：{target_language}。"
            )
        ),
        HumanMessage(
            _SUMMARY_PROMPT.format(
                steps_summary=steps_summary,
                quality_summary=quality_summary,
                question=question,
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
    llm_service = state["llm_service"]
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
        brief=f"batch={step_index}",
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
    assessments = _assess_all_steps(
        current_steps,
        contract=state.get("query_contract"),
    )
    validation: ResultValidationReport = validate_result_structure(
        assessments,
        contract=state.get("query_contract"),
    )
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
        intent_ready=(state.get("intent_context") or {}).get("status") == "ready",
        plan_validated=bool(active_candidate.get("plan_validated")),
        contract_status=active_candidate.get("contract_status", "unsupported"),
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
            "step_index": step_index + 1,
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
        "step_index": step_index + 1,
        "repair_hint": "",
        "outcome": candidate_outcome,
    }


def summarize_answer_node(state: NlqState) -> NlqState:
    """Summarize an already accepted candidate; never gate its publication."""
    llm_service = state["llm_service"]
    candidate = dict(state.get("accepted_candidate") or {})
    steps = list(candidate.get("steps") or [])
    if not steps:
        return _fail(
            state,
            getattr(llm_service.record, "id", None),
            SingleMessageError("No accepted result to summarize"),
        )
    assessments = _assess_all_steps(
        steps,
        contract=state.get("query_contract"),
    )
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
        brief="结果总结",
        step_index=state.get("step_index"),
    ) as span:
        try:
            target_language = str(
                getattr(llm_service.chat_question, "lang", "") or "简体中文"
            )
            response: AIMessage = llm_service.llm.invoke(
                _summary_messages(
                    _summarize_steps(steps, assessments),
                    question,
                    quality,
                    target_language=target_language,
                )
            )
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
            span["payload"] = {
                "fallback": not bool(
                    _extract_summary_text(message_content_text(response.content))
                ),
                "chars": len(analysis_text),
            }
        except Exception as exc:
            SQLBotLogUtil.error(f"summarize_answer_node error: {exc}")
            analysis_text = _fallback_analysis(
                assessments,
                reason=f"总结模型调用异常：{exc}",
                target_language=str(
                    getattr(llm_service.chat_question, "lang", "") or "简体中文"
                ),
            )
            span["error"] = True
            span["payload"] = {"fallback": True, "chars": len(analysis_text)}
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


def complete_node(state: NlqState) -> NlqState:
    """Commit the terminal snapshot, then publish the same answer to clients."""
    llm_service = state["llm_service"]
    sink = StreamSink.from_state(state)
    json_result: dict[str, Any] = dict(state.get("json_result") or {})
    analysis_text = state.get("analysis_text") or ""
    return_img = bool(state.get("return_img", True))

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
                contract=state.get("query_contract"),
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

    try:
        _persist_record_snapshot(
            llm_service,
            updated_steps,
            analysis_text,
            finish=True,
            outcome=outcome,
        )
    except Exception as exc:
        traceback.print_exc()
        return cast(
            NlqState,
            fail_turn_node(
                {
                    **state,
                    "accepted_candidate": {
                        **source_candidate,
                        "steps": updated_steps,
                    },
                    "error": format_error_message(exc),
                    "outcome": failed_outcome(exc),
                }
            ),
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
        failures = outcome.get("failures") or []
        failure_message = next(
            (str(item.get("message")) for item in failures if item.get("message")),
            "Conversation completed without a usable result",
        )
        return cast(
            NlqState,
            fail_turn_node(
                {
                    **state,
                    "accepted_candidate": {
                        **source_candidate,
                        "steps": updated_steps,
                    },
                    "json_result": json_result,
                    "error": failure_message,
                    "outcome": outcome,
                }
            ),
        )

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
        "record": llm_service.record,
    }


def fail_node(state: NlqState) -> NlqState:
    """Persist the canonical empty NLQ answer before emitting terminal failure."""
    llm_service = state["llm_service"]
    error = str(state.get("error") or "unknown error")
    current_outcome = state.get("outcome")
    outcome = (
        cast(RunOutcome, dict(current_outcome))
        if current_outcome and current_outcome.get("status") != "running"
        else failed_outcome(error)
    )
    if "quality" not in outcome:
        outcome["quality"] = build_overall_quality([])
    try:
        _persist_record_snapshot(
            llm_service,
            [],
            "",
            finish=True,
            outcome=outcome,
        )
    except Exception as exc:
        # Failure reporting must still reach the client when persistence itself
        # is unavailable; the shared terminal node remains the single emitter.
        SQLBotLogUtil.error(f"persist NLQ failure snapshot failed: {exc}")
    return cast(
        NlqState,
        fail_turn_node(
            {
                **state,
                "error": error,
                "outcome": outcome,
            }
        ),
    )


# ── Routers ──────────────────────────────────────────────────────────────────


def route_after_clarity(
    state: NlqState,
) -> Literal["assemble_context", "complete_intent", "fail"]:
    if state.get("error"):
        return "fail"
    context = intent_context_from_payload(state.get("intent_context") or {})
    if context.status == "ready":
        return "assemble_context"
    return "complete_intent"


def route_after_queries(
    state: NlqState,
) -> Literal["generate_queries", "execute_queries", "complete", "fail"]:
    """Execute when plans exist; else plan-regen within MAX_PLAN_REGEN, else fail."""
    if state.get("error"):
        return "fail"

    plans = (state.get("active_candidate") or {}).get("plans") or []
    if plans:
        if _finish_step_value(state) <= int(ChatFinishStep.GENERATE_QUERY.value):
            return "complete"
        return "execute_queries"

    attempts = int(state.get("gen_attempts") or 0)
    repair = (state.get("repair_hint") or "").strip()
    if repair and attempts <= MAX_PLAN_REGEN:
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
) -> Literal["generate_queries", "generate_charts", "complete", "fail"]:
    if state.get("error"):
        return "fail"
    step_index = state.get("step_index", 0)
    max_steps = state.get("max_steps", _MAX_STEPS)
    decision = state.get("decision") or "finish"

    if decision == "repair":
        return "generate_queries" if step_index < max_steps else "complete"
    if decision == "accept":
        if _finish_step_value(state) <= int(ChatFinishStep.QUERY_DATA.value):
            return "complete"
        return "generate_charts"
    return "complete"
