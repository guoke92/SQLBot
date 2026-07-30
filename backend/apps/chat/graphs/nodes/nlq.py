"""NLQ node implementations — reviewed batch loop.

Topology: generate_queries → execute_queries → generate_charts → decide_next
  → (repair loop | complete)

Each iteration plans and executes 1~N candidate queries. Candidate plans,
results, and charts remain private until ``decide_next`` accepts them into
``all_steps``. Rejected repair attempts remain available to observability and
the next generation round, but never become answer cards.
Loop and batch limits are defined only in ``apps.chat.plan_policy``.

SSE result cards are hydrated only from the terminal accepted snapshot.
ChatRecord.data stores::

    {"steps": [{"sql","chart","data","brief","error"?}, ...], "analysis": "..."}
"""

from __future__ import annotations

import re
import traceback
from concurrent.futures import as_completed
from copy import deepcopy
from typing import Any, Literal, cast

import orjson
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from sqlbot_xpack.custom_prompt.models.custom_prompt_model import CustomPromptTypeEnum

from apps.chat.binding_resolver import (
    apply_confirmed_entity_bindings,
    binding_resource_names,
    resolve_entity_bindings,
    retain_binding_resources,
)
from apps.chat.constants import DYNAMIC_DS_TYPES
from apps.chat.curd.chat import (
    format_json_data,
    rename_chat,
)
from apps.chat.models.chat_model import ChatFinishStep, OperationEnum, RenameChat
from apps.chat.plan_context import (
    render_plan_context,
    wrap_plan_context,
)
from apps.chat.plan_policy import (
    MAX_BATCH_ROUNDS,
    MAX_PLAN_REGEN,
    MAX_QUERIES_PER_BATCH,
    NULL_DIM_SEVERE,
    ROW_LIMIT,
)
from apps.chat.planning import parse_query_generation
from apps.chat.result_semantics import (
    apply_display_window,
    classify_field_roles,
    read_result_window,
)
from apps.chat.semantic_intent import (
    intent_context_from_payload,
    new_intent_context,
    public_intent_payload,
    render_decision_value,
)
from apps.chat.steps.chart import generate_chart
from apps.chat.steps.clarification import assess_semantic_intent
from apps.chat.steps.custom_prompt import match_custom_prompts
from apps.chat.steps.datasource import select_datasource, validate_history_ds
from apps.chat.steps.knowledge import match_knowledge
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
from apps.chat.task.llm import LLMService, request_picture
from apps.chat.time_intent import TimeIntent, infer_time_intent
from apps.conversation.observability import end_log, trigger_log_error
from apps.conversation.outcome import (
    RunOutcome,
    awaiting_input_outcome,
    blocked_outcome,
    classify_failure,
    failed_outcome,
    format_error_message,
    outcome_allows_retry,
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
from apps.conversation.usage import merge_usage, usage_from_response
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
    batch_plans: list[dict[str, Any]]
    batch_results: list[dict[str, Any]]
    batch_charts: list[dict[str, Any]]
    # Accepted answer steps only. Rejected repair attempts stay in ChatLog and
    # ``repair_steps`` until the replacement round consumes their context.
    all_steps: list[dict[str, Any]]
    repair_steps: list[dict[str, Any]]
    analysis_text: str
    max_steps: int
    max_batch_size: int
    decision: str
    decision_reason: str
    repair_hint: str  # plan-validate or execute-quality rewrite brief
    gen_attempts: int  # plan-time generate→validate failures in current slot
    entity_bindings: dict[str, Any]  # NL phrase → canonical dimension values
    knowledge_matches: list[dict[str, Any]]
    access_scope: AccessScope | None
    time_intent: TimeIntent  # semantic time range, independent of cost probes
    intent_context: dict[str, Any]
    outcome: RunOutcome


# ── Helpers ──────────────────────────────────────────────────────────────────


def _ds_scope(llm_service: LLMService) -> tuple[int | None, int | None]:
    if not llm_service.ds:
        return None, None
    oid = llm_service.ds.oid if isinstance(llm_service.ds, CoreDatasource) else 1
    ds_id = llm_service.ds.id if isinstance(llm_service.ds, CoreDatasource) else None
    return oid, ds_id


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
    """Return only the latest rejected batch used as repair evidence."""
    return list(state.get("repair_steps") or [])


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


def _assess_step_quality(step: dict[str, Any], index: int) -> dict[str, Any]:
    """Deterministic quality signals for one executed step (no LLM).

    Returns metadata (row_count, fields, null_rates, metrics) for severity
    scoring plus column_stats + data_sample so the decide LLM can reason
    about actual values rather than writing hypothetical conclusions.
    """
    issues: list[str] = []
    brief = step.get("brief") or ""
    sql = step.get("format_statement") or step.get("sql") or ""
    if step.get("error"):
        issues.append(f"执行失败: {step.get('error')}")
        return {
            "index": index,
            "brief": brief,
            "sql": sql,
            "row_count": 0,
            "fields": [],
            "truncated": False,
            "truncation_reason": None,
            "null_rates": {},
            "metrics": {},
            "column_stats": {},
            "data_sample": [],
            "issues": issues,
            "limitations": [],
            "severity": True,
        }

    rows = _result_rows(step)
    fields = _result_fields(step)
    result = step.get("result") or {}
    window = read_result_window(result, rows)
    truncated = window["truncated"]

    # Chart bindings are the authoritative semantic roles. DB numeric metadata
    # is only a conservative fallback because IDs and time buckets may be numeric.
    fields_info_list = result.get("fields_info") or []
    fields_info_map = {
        fi.get("name"): fi
        for fi in fields_info_list
        if isinstance(fi, dict) and fi.get("name")
    }
    field_roles = classify_field_roles(
        fields,
        list(fields_info_map.values()),
        step.get("chart") if isinstance(step.get("chart"), dict) else None,
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
            if rows and rate >= NULL_DIM_SEVERE:
                message = f"维度列「{f}」展示样本空值率 {rate:.0%}"
                if truncated:
                    limitations.append(message + "，不能据此判断全量 join 质量")
                else:
                    issues.append(
                        f"维度列「{f}」空值率 {rate:.0%}（join/字段选择可能错误）"
                    )
            elif rows and rate >= 0.35:
                message = f"维度列「{f}」空值率偏高 {rate:.0%}"
                if truncated:
                    limitations.append("展示样本" + message)
                else:
                    issues.append(message)
        # column_stats for ALL fields (metrics get numeric stats, dims get categorical)
        col_stats[f] = _column_stats(rows, f)

    if not rows:
        issues.append("结果为空（0 行）")
    for mf, st in metrics.items():
        if st.get("count", 0) == 0:
            message = f"指标列「{mf}」无可汇总数值"
            if truncated:
                limitations.append("展示样本中" + message)
            else:
                issues.append(message)
        elif st.get("sum", 0) == 0 and st.get("max", 0) == 0:
            message = f"指标列「{mf}」全为 0"
            if truncated:
                limitations.append("展示样本中" + message)
            else:
                issues.append(message)

    severity = (
        bool(step.get("error"))
        or (not rows)
        or (not truncated and any(r >= NULL_DIM_SEVERE for r in null_rates.values()))
    )

    return {
        "index": index,
        "brief": brief,
        "sql": sql,
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
        "issues": issues,
        "limitations": limitations,
        "severity": severity,
    }


def _assess_all_steps(all_steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [_assess_step_quality(s, i) for i, s in enumerate(all_steps or [])]


def _quality_requires_repair(assessments: list[dict[str, Any]]) -> bool:
    """Force another SQL round only on severe failures (empty / high-null / errors)."""
    if not assessments:
        return False
    return any(a.get("severity") for a in assessments)


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
            sql_show = sql if len(sql) <= 800 else sql[:800] + " …"
            lines.append(f"- SQL:\n```sql\n{sql_show}\n```")
        issues = a.get("issues") or []
        if issues:
            lines.append("- 质检问题:")
            for it in issues:
                lines.append(f"  - {it}")
        else:
            lines.append("- 质检问题: 无")
        limitations = a.get("limitations") or []
        if limitations:
            lines.append("- 展示限制:")
            lines.extend(f"  - {item}" for item in limitations)
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def _summarize_steps(all_steps: list[dict[str, Any]]) -> str:
    """Quality-aware step summary for decide / continue context."""
    assessments = _assess_all_steps(all_steps)
    if not assessments:
        return "（尚无已执行查询）"
    header = (
        "下列为已落地执行的查询及其**数据质检**摘要。"
        "查询行数上限只影响返回窗口，不代表 SQL 错误；截断结果中的统计均为样本统计，"
        "不得解释为全量合计。只有执行错误、空结果或严重字段质量问题才应修复 SQL。\n"
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
        issues = assessment.get("issues") or []
        if issues:
            lines.append("- 必须修复:")
            lines.extend(f"  - {item}" for item in issues)
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
    issues = []
    empty_or_zero = False
    for a in assessments:
        if int(a.get("row_count") or 0) == 0 or a.get("error"):
            empty_or_zero = True
        for it in a.get("issues") or []:
            issues.append(f"查询{a['index'] + 1}: {it}")
    issue_text = (
        "\n".join(f"- {x}" for x in issues) or "- （未列出细则，请对照质检摘要）"
    )
    anti_empty = ""
    if empty_or_zero:
        anti_empty = (
            "7. **禁止改得更空**：禁止在已有 0 行/近空结果上继续收紧等值过滤；"
            "应核对标准实体值、时间列与 join 键；不得把诊断候选自动并入 IN，"
            "或保持可出数的结构并在总结中说明局限。\n"
        )
    return (
        "上一轮查询结果未通过数据质检，请**改写 SQL** 后重新查询，不要只重复同样语句。\n"
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
        }
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


def _steps_payload(
    all_steps: list[dict[str, Any]],
    analysis_text: str = "",
    outcome: RunOutcome | None = None,
) -> dict[str, Any]:
    steps_data: list[dict[str, Any]] = []
    for step in all_steps or []:
        step_entry: dict[str, Any] = {
            "sql": step.get("format_statement") or step.get("sql", ""),
            "brief": step.get("brief") or "",
            "chart": step.get("chart"),
        }
        if step.get("error"):
            step_entry["error"] = step["error"]
            if step.get("failure"):
                step_entry["failure"] = step["failure"]
        result = step.get("result") or {}
        if result:
            step_entry["data"] = {
                "fields": result.get("fields", []),
                "fields_info": result.get("fields_info"),
                "data": result.get("data", []),
                "limit": result.get("limit"),
                "row_count": result.get("row_count"),
                "truncated": result.get("truncated"),
                "truncation_reason": result.get("truncation_reason"),
                "datasource": result.get("datasource"),
            }
        steps_data.append(step_entry)
    payload: dict[str, Any] = {
        "steps": steps_data,
        "analysis": analysis_text or "",
    }
    if outcome is not None:
        payload["outcome"] = outcome
    return payload


def _result_quality(all_steps: list[dict[str, Any]]) -> dict[str, Any]:
    returned_rows = 0
    truncated = False
    for step in all_steps:
        result = step.get("result")
        if not isinstance(result, dict):
            continue
        rows = _result_rows(step)
        window = read_result_window(result, rows)
        returned_rows += window["row_count"]
        truncated = truncated or window["truncated"]
    return {
        "status": "partial" if truncated else "complete",
        "truncated": truncated,
        "returned_rows": returned_rows,
    }


def _fallback_analysis(
    assessments: list[dict[str, Any]],
    *,
    reason: str,
) -> str:
    """Build a complete deterministic report when summary generation fails."""
    returned_rows = sum(int(item.get("row_count") or 0) for item in assessments)
    truncated = any(bool(item.get("truncated")) for item in assessments)
    window_note = (
        f"本次仅查询并展示前 {returned_rows} 行，未查询结果总数。"
        if truncated
        else f"查询返回 {returned_rows} 行。"
    )
    limitation = (
        "结果受查询行数窗口限制，下面的样本指标不能视为全量合计。"
        if truncated
        else "未检测到平台查询行数截断。"
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
            "请以已展示表格作为当前结果；如需全量汇总，请进一步明确聚合粒度或导出范围。",
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
    payload = _steps_payload(all_steps, analysis_text, outcome)
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


def _table_chart(fields: list[str], title: str = "") -> dict[str, Any]:
    return {
        "type": "table",
        "title": title or "",
        "columns": [{"name": f, "value": f} for f in fields],
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
            "all_steps": [],
            "repair_steps": [],
            "batch_plans": [],
            "batch_results": [],
            "batch_charts": [],
            "max_steps": state.get("max_steps") or _MAX_STEPS,
            "max_batch_size": state.get("max_batch_size") or _MAX_BATCH_SIZE,
            "analysis_text": "",
            "decision": "",
            "decision_reason": "",
            "repair_hint": "",
            "gen_attempts": 0,
            "entity_bindings": {},
            "knowledge_matches": [],
            "access_scope": None,
            "time_intent": {},
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
            matches = match_knowledge(
                llm_service,
                session,
                oid,
                ds_id,
                access_scope=state.get("access_scope"),
            )
            return {
                **state,
                "knowledge_matches": [match.model_dump() for match in matches],
                "record": llm_service.record,
            }
        except Exception as e:
            return _fail(state, llm_service.record.id, e)


def prepare_time_intent_node(state: NlqState) -> NlqState:
    """Capture time semantics without guessing columns or probing data."""
    llm_service = state.get("llm_service")
    question = (
        getattr(llm_service, "generation_question", "")
        if llm_service
        else state.get("question", "")
    )
    time_intent = infer_time_intent(str(question or ""))
    if not time_intent:
        return state
    return {**state, "time_intent": time_intent}


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
    llm_service = state["llm_service"]
    oid, ds_id = _ds_scope(llm_service)
    with session_scope() as session:
        try:
            match_training(llm_service, session, oid, ds_id)
            return {**state, "record": llm_service.record}
        except Exception as e:
            return _fail(state, llm_service.record.id, e)


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
        context = intent_context_from_payload(
            state.get("intent_context")
            or llm_service.chat_question.intent_context
            or public_intent_payload(
                new_intent_context(llm_service.chat_question.question or "")
            )
        )
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
                assessed, usage, reasoning = context, {}, ""
            else:
                assessed, usage, reasoning = assess_semantic_intent(
                    llm_service,
                    context=context,
                    bindings=state.get("entity_bindings") or {},
                    time_intent=state.get("time_intent") or {},
                )
            payload = public_intent_payload(assessed)
            display_reasoning = (
                reasoning.strip()
                or "\n".join(f"- {issue.reason}" for issue in assessed.issues)
                or assessed.summary
            )
            span["payload"] = {
                "status": assessed.status,
                "summary": assessed.summary,
                "resolved_decisions": [
                    {
                        "key": decision.key,
                        "label": decision.label,
                        "value": render_decision_value(decision.value),
                        "source": decision.source,
                        "required_identifiers": decision.required_identifiers,
                    }
                    for decision in assessed.decisions
                    if decision.locked
                ],
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
            "record": llm_service.record,
        }
    except Exception as exc:
        return _fail(state, record_id, exc)


def assemble_context_node(state: NlqState) -> NlqState:
    """Assemble SQL/chart prompts only after the semantic gate is ready."""
    llm_service = state["llm_service"]
    try:
        assemble_prompt_messages(llm_service)
        return {**state, "record": llm_service.record}
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
        message = "; ".join(context.blocking_reasons) or "当前信息不足，无法生成查询"
        outcome = blocked_outcome(message)
        event_type = "clarification-blocked"
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
                + "\n".join(f"- {reason}" for reason in context.blocking_reasons)
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
        time_intent=state.get("time_intent"),
        intent_context=state.get("intent_context"),
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
            assessments = _assess_all_steps(context_steps)
            if not repair and _quality_requires_repair(assessments):
                repair = _repair_instruction(
                    assessments, _generation_question(llm_service)
                )
            extra_sections.append(
                "## 已执行查询（仅用于本轮改写或补充）\n"
                + _format_generation_context(assessments)
            )
            if repair:
                extra_sections.append("## 改写指令\n" + repair)

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
                    "content": getattr(llm_service.chat_question, "plan_context", "")
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
        )
        plans = batch_parse.plans if batch_parse.success else []
        refusal = batch_parse.error_message

        _maybe_update_chat_brief(
            llm_service, sink, _extract_title_from_sql_answer(full_sql_text, plans)
        )

        if not plans:
            msg = refusal or "Failed to generate any valid SQL queries"
            attempts = gen_attempts + 1
            repair_msg = _plan_repair_message(msg)
            _mark_generate_validation_failed(
                llm_service,
                message=msg,
                attempt=attempts,
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
                    "batch_plans": [],
                    "batch_results": [],
                    "batch_charts": [],
                    "repair_hint": repair_msg,
                    "gen_attempts": attempts,
                    "record": llm_service.record,
                    "error": None,
                }
            return {
                **_fail(
                    {
                        **state,
                        "batch_plans": [],
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
                "count": len(plans),
            }
        )

        return {
            **state,
            "json_result": json_result,
            "batch_plans": plans,
            "batch_results": [],
            "batch_charts": [],
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
    plans = list(state.get("batch_plans") or [])
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
            "batch_results": flat_results,
            "batch_plans": prepared,
            "outcome": outcome_from_steps(snapshot_steps),
        }
    except Exception as e:
        return _fail(state, llm_service.record.id, e)


def generate_charts_node(state: NlqState) -> NlqState:
    """Generate candidate chart configs without publishing answer cards."""
    llm_service = state["llm_service"]
    sink = StreamSink.from_state(state)
    batch_results = state.get("batch_results") or []
    base = 0
    finish_v = _finish_step_value(state)

    # MCP / early stop: data only — emit table charts without LLM
    skip_llm = finish_v < int(ChatFinishStep.GENERATE_CHART.value)

    try:
        charts: list[dict[str, Any]] = []
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
                chart = _table_chart([], title="Error")
                charts.append(chart)
                continue

            plan_dict = entry.get("plan") or {}
            result = entry.get("result") or {}
            chart_type = (plan_dict.get("chart_type") or "table") or "table"
            fields = result.get("fields") or []
            data = result.get("data") or []
            brief = plan_dict.get("brief") or ""

            if skip_llm or chart_type == "table":
                chart = _table_chart(fields, title=brief)
                charts.append(chart)
                continue

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
                            "reasoning_content": chunk.get("reasoning_content") or "",
                            "type": "step-chart-result",
                            "index": gidx,
                        }
                    )
                chart = parse_chart(
                    res=full_chart_text,
                    fields=fields,
                )
                charts.append(chart)

        # Restore base chart messages after batch
        llm_service.chart_message = list(base_chart_messages)

        return {**state, "batch_charts": charts, "record": llm_service.record}
    except Exception as e:
        return _fail(state, llm_service.record.id, e)


_SUMMARY_PROMPT = """\
你是数据分析助手。请只根据已执行结果生成最终总结，不能再生成或修改 SQL。

{steps_summary}

用户原问题：{question}

直接输出完整 Markdown 报告，不要输出 JSON、action 或额外说明。

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
给出 1～3 条必要且可执行的后续分析建议。
"""


def _summary_messages(steps_summary: str, question: str) -> list[Any]:
    return [
        SystemMessage(
            content=(
                "你负责根据已执行查询结果生成完整 Markdown 总结。"
                "不要生成或修改 SQL，不要返回 JSON。"
            )
        ),
        HumanMessage(
            _SUMMARY_PROMPT.format(
                steps_summary=steps_summary,
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
    """Review the candidate batch, repair deterministically, or summarize."""
    llm_service = state["llm_service"]
    step_index = state.get("step_index", 0)
    max_steps = state.get("max_steps", _MAX_STEPS)
    finish_v = _finish_step_value(state)
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
        out = _decide_next_impl(
            state, llm_service, step_index, max_steps, finish_v, meta=meta
        )
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
            "summary_retried": bool(meta.get("summary_retried")),
        }
        return out


def _decide_next_impl(
    state: NlqState,
    llm_service: LLMService,
    step_index: int,
    max_steps: int,
    finish_v: int,
    *,
    meta: dict[str, Any] | None = None,
) -> NlqState:
    if meta is None:
        meta = {}
    batch_results = state.get("batch_results") or []
    batch_charts = state.get("batch_charts") or []
    batch_plans = state.get("batch_plans") or []
    current_steps = _merge_batch_into_steps(
        [],
        batch_plans,
        batch_results,
        batch_charts,
        entity_bindings=state.get("entity_bindings"),
    )
    assessments = _assess_all_steps(current_steps)
    needs_repair = _quality_requires_repair(assessments)
    current_outcome = outcome_from_steps(current_steps)
    question = _generation_question(llm_service)
    repair_hint = _repair_instruction(assessments, question) if needs_repair else ""

    if finish_v < int(ChatFinishStep.GENERATE_CHART.value):
        meta["path"] = "finish_step_early"
        meta["used_llm"] = False
        return {
            **state,
            "decision": "finish",
            "decision_reason": "",
            "all_steps": current_steps,
            "repair_steps": [],
            "step_index": step_index + 1,
            "batch_plans": [],
            "batch_results": [],
            "batch_charts": [],
            "repair_hint": "",
            "outcome": current_outcome,
        }

    force_terminal = step_index >= max_steps - 1

    # Post-exec QC is insurance, not the main fix path.
    # Prefer summarize with honest limitations over automatic repair that
    # often rewrites filters dryer (empty → emptier). Allow at most one
    # repair when there is a clear recoverable signal (exec error / unknown
    # column class) and rounds remain.
    batch_outcome = outcome_from_steps(current_steps)
    auto_repair = bool(
        needs_repair
        and not force_terminal
        and step_index < 1
        and outcome_allows_retry(batch_outcome)
    )
    if auto_repair:
        SQLBotLogUtil.info(
            "decide_next quality gate -> repair (recoverable); issues="
            + str(sum(len(a.get("issues") or []) for a in assessments))
        )
        meta["path"] = "auto_repair"
        meta["used_llm"] = False
        return {
            **state,
            "decision": "repair",
            "decision_reason": "deterministic quality gate",
            "analysis_text": state.get("analysis_text") or "",
            "all_steps": [],
            "repair_steps": current_steps,
            "step_index": step_index + 1,
            "batch_plans": [],
            "batch_results": [],
            "batch_charts": [],
            "repair_hint": repair_hint,
            "gen_attempts": 0,
            "outcome": running_outcome(),
        }

    if current_outcome["status"] in {"failed", "degraded"}:
        meta["path"] = "terminal_failure"
        meta["used_llm"] = False
        terminal_outcome = cast(
            RunOutcome,
            {
                **current_outcome,
                "status": "failed",
            },
        )
        analysis_text = (
            "## 结论\n"
            "本次查询未取得可用数据，无法基于结果回答原问题。\n\n"
            "## 数据质量与局限\n" + _format_assessment_block(assessments)
        )
        return {
            **state,
            "decision": "complete",
            "decision_reason": "terminal query failure",
            "analysis_text": analysis_text,
            # A failed terminal batch means the atomic answer contract was not
            # completed. Keep every attempted step as diagnostic evidence, but
            # publish no partial result card.
            "all_steps": [],
            "repair_steps": current_steps,
            "step_index": step_index + 1,
            "batch_plans": [],
            "batch_results": [],
            "batch_charts": [],
            "repair_hint": "",
            "outcome": terminal_outcome,
        }

    try:
        # A successful, contract-valid batch already answers the confirmed
        # question. Additional independent outputs must be planned in the
        # original atomic batch, never invented after seeing valid data.
        steps_summary = _summarize_steps(current_steps)
        messages = _summary_messages(steps_summary, question)
        meta["path"] = "llm_summary"
        meta["used_llm"] = True
        response: AIMessage = llm_service.llm.invoke(messages)
        meta["token_usage"] = usage_from_response(response)
        response_text = (
            response.content
            if isinstance(response.content, str)
            else str(response.content or "")
        )

        analysis_text = _extract_summary_text(response_text)
        reason = "accepted candidate batch"

        if not analysis_text:
            retry_response: AIMessage = llm_service.llm.invoke(
                _summary_messages(steps_summary, question)
            )
            meta["token_usage"] = merge_usage(
                meta.get("token_usage") or {},
                usage_from_response(retry_response),
            )
            meta["summary_retried"] = True
            retry_text = (
                retry_response.content
                if isinstance(retry_response.content, str)
                else str(retry_response.content or "")
            )
            analysis_text = _extract_summary_text(retry_text)
            if not analysis_text:
                analysis_text = _fallback_analysis(
                    assessments,
                    reason="总结模型连续两次未返回可用正文",
                )

        return {
            **state,
            "decision": "complete",
            "decision_reason": reason,
            "analysis_text": analysis_text,
            "all_steps": current_steps,
            "repair_steps": [],
            "step_index": step_index + 1,
            "batch_plans": [],
            "batch_results": [],
            "batch_charts": [],
            "repair_hint": "",
            "outcome": current_outcome,
        }
    except Exception as e:
        meta["path"] = "error"
        SQLBotLogUtil.error(f"decide_next_node error: {e}")
        stub = state.get("analysis_text") or ""
        if not stub and assessments:
            stub = _fallback_analysis(
                assessments,
                reason=f"分析决策阶段异常：{e}",
            )
        return {
            **state,
            "decision": "complete",
            "decision_reason": format_error_message(e),
            "analysis_text": stub,
            "all_steps": current_steps,
            "repair_steps": [],
            "step_index": step_index + 1,
            "batch_plans": [],
            "batch_results": [],
            "batch_charts": [],
            "repair_hint": "",
            "outcome": current_outcome,
        }


def complete_node(state: NlqState) -> NlqState:
    """Commit the terminal snapshot, then publish the same answer to clients."""
    llm_service = state["llm_service"]
    sink = StreamSink.from_state(state)
    json_result: dict[str, Any] = dict(state.get("json_result") or {})
    analysis_text = state.get("analysis_text") or ""
    return_img = bool(state.get("return_img", True))

    # Normal chat completion publishes accepted steps only. Query/data-only
    # protocol exits intentionally skip review, so accept their current batch
    # at this explicit boundary instead of relying on a broad fallback merge.
    if _finish_step_value(state) < int(ChatFinishStep.GENERATE_CHART.value):
        updated_steps = _merge_batch_into_steps(
            [],
            state.get("batch_plans") or [],
            state.get("batch_results") or [],
            state.get("batch_charts") or [],
            entity_bindings=state.get("entity_bindings"),
        )
    else:
        updated_steps = list(state.get("all_steps") or [])
    # Ensure every successful step has a chart (MCP QUERY_DATA / table fallback)
    for step in updated_steps:
        if step.get("chart") or step.get("error"):
            continue
        fields = (step.get("result") or {}).get("fields") or []
        step["chart"] = _table_chart(fields, title=step.get("brief") or "")

    outcome = outcome_from_steps(
        updated_steps,
        planned_count=len(state.get("batch_plans") or []),
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
    outcome["quality"] = _result_quality(updated_steps)
    json_result["success"] = outcome_is_success(outcome)
    json_result["status"] = outcome["status"]
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
                    "all_steps": updated_steps,
                    "error": format_error_message(exc),
                    "outcome": failed_outcome(exc),
                }
            ),
        )

    # The persisted snapshot is the source of truth. Publish analysis only
    # after that commit so live SSE and a subsequent page refresh cannot
    # observe different terminal answers.
    with log_span(
        operate=OperationEnum.ANALYSIS,
        record_id=getattr(llm_service.record, "id", None) or state.get("record_id"),
        ai_modal_id=getattr(llm_service.chat_question, "ai_modal_id", None),
        ai_modal_name=getattr(llm_service.chat_question, "ai_modal_name", None),
        local_operation=True,
        graph_node="complete",
        brief="综合分析",
        step_index=state.get("step_index"),
        initial_payload={"source": "terminal_snapshot", "chars": len(analysis_text)},
    ) as span:
        if analysis_text:
            sink.event({"type": "analysis", "content": analysis_text})
            if sink.mode == "markdown":
                sink.text(analysis_text + "\n\n")
        span["payload"] = {
            "source": "terminal_snapshot",
            "chars": len(analysis_text),
            "empty": not bool(analysis_text.strip()),
        }

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
                    "all_steps": updated_steps,
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

    return {
        **state,
        "json_result": json_result,
        "all_steps": updated_steps,
        "outcome": outcome,
        "record": llm_service.record,
    }


def fail_node(state: NlqState) -> NlqState:
    """Use the shared terminal failure contract for every conversation graph."""
    return cast(NlqState, fail_turn_node(state))


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

    plans = state.get("batch_plans") or []
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
) -> Literal["generate_charts", "complete", "fail"]:
    if state.get("error"):
        return "fail"
    if _finish_step_value(state) <= int(ChatFinishStep.QUERY_DATA.value):
        return "complete"
    return "generate_charts"


def route_after_decision(
    state: NlqState,
) -> Literal["generate_queries", "complete", "fail"]:
    if state.get("error"):
        return "fail"
    step_index = state.get("step_index", 0)
    max_steps = state.get("max_steps", _MAX_STEPS)
    decision = state.get("decision") or "finish"

    if step_index >= max_steps:
        return "complete"

    if decision == "repair":
        return "generate_queries"
    return "complete"
