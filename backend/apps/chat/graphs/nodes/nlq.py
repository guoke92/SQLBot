"""NLQ node implementations — Agentic Batch Loop.

Topology: generate_queries → execute_queries → generate_charts → decide_next
  → (loop back | summarize → complete | complete)

Each iteration: LLM plans 1~N SQL queries → concurrent execution → chart generation → LLM decision.
Max 3 iterations, max 5 queries per batch.

SSE step identity uses a single global ``index`` (0-based across all batches).
ChatRecord.data stores::

    {"steps": [{"sql","chart","data","brief","error"?}, ...], "analysis": "..."}
"""

from __future__ import annotations

import re
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from copy import deepcopy
from typing import Any, Dict, List, Literal, Optional

import orjson
from langchain_core.messages import AIMessage, HumanMessage
from sqlbot_xpack.custom_prompt.models.custom_prompt_model import CustomPromptTypeEnum

from apps.chat.constants import DYNAMIC_DS_TYPES
from apps.chat.curd.chat import (
    format_json_data,
    rename_chat,
    save_analysis_answer,
    save_chart,
    save_re_exec,
    save_sql,
    save_sql_exec_data,
    trigger_log_error,
)
from apps.chat.models.chat_model import ChatFinishStep, OperationEnum, RenameChat
from apps.chat.steps.chart import generate_chart
from apps.chat.steps.custom_prompt import match_custom_prompts
from apps.chat.steps.datasource import select_datasource, validate_history_ds
from apps.chat.steps.messages import build_prompt_messages
from apps.chat.steps.observability import log_span
from apps.chat.steps.permissions import (
    DYNAMIC_SUBSQL_PREFIX,
    generate_assistant_dynamic_sql,
    generate_filter,
)
from apps.chat.steps.persist import check_save_chart
from apps.chat.steps.sql import generate_sql
from apps.chat.steps.terminology import match_terminology
from apps.chat.steps.training import match_training
from apps.chat.plan_context import (
    build_cross_validation_section,
    render_plan_context,
    wrap_plan_context,
)
from apps.chat.plan_policy import (
    MAX_BATCH_ROUNDS,
    MAX_PLAN_REGEN,
    MAX_QUERIES_PER_BATCH,
    NULL_DIM_SEVERE,
    ROW_LIMIT,
    ROW_LIMIT_NEAR,
)
from apps.chat.task.llm import LLMService, request_picture
from apps.conversation.record import finish as record_finish
from apps.conversation.record import save_error as record_save_error
from apps.conversation.session import session_scope
from apps.conversation.sink import StreamSink
from apps.conversation.state import RunState
from apps.datasource.crud.permission import is_normal_user
from apps.datasource.models.datasource import CoreDatasource
from apps.protocol import QueryPlan
from apps.protocol.base import CAP_ROW_PERMISSION
from common.error import SingleMessageError, SQLBotDBConnectionError, SQLBotDBError
from common.utils.data_format import DataFormat
from common.utils.utils import SQLBotLogUtil, extract_nested_json, prepare_for_orjson

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

    Field contract is shared with ``apps.chat.graphs.chat.state.ChatState``
    (nlq_* keys). Keep batch-loop keys in sync when evolving either side.
    """

    llm_service: LLMService
    finish_step: ChatFinishStep
    return_img: bool
    json_result: Dict[str, Any]

    # batch loop
    step_index: int  # current batch iteration (0-based)
    batch_plans: List[Dict[str, Any]]
    batch_results: List[Dict[str, Any]]
    batch_charts: List[Dict[str, Any]]
    all_steps: List[Dict[str, Any]]  # accumulated finished steps
    analysis_text: str
    max_steps: int
    max_batch_size: int
    decision: str
    repair_hint: str  # plan-validate or execute-quality rewrite brief
    gen_attempts: int  # plan-time generate→validate failures in current slot
    entity_bindings: Dict[str, Any]  # NL phrase → canonical dimension values
    query_bindings: Dict[str, Any]  # boundary probe binds (pk thresholds, etc.)


# ── Helpers ──────────────────────────────────────────────────────────────────


def _error_message(exc: BaseException) -> str:
    if isinstance(exc, SingleMessageError):
        return str(exc)
    if isinstance(exc, SQLBotDBConnectionError):
        return orjson.dumps({"message": str(exc), "type": "db-connection-err"}).decode()
    if isinstance(exc, SQLBotDBError):
        return orjson.dumps(
            {
                "message": "Query execution failed",
                "traceback": str(exc),
                "type": "exec-query-err",
            }
        ).decode()
    return orjson.dumps(
        {"message": str(exc), "traceback": traceback.format_exc(limit=1)}
    ).decode()


def _ds_scope(llm_service: LLMService) -> tuple[Optional[int], Optional[int]]:
    if not llm_service.ds:
        return None, None
    oid = llm_service.ds.oid if isinstance(llm_service.ds, CoreDatasource) else 1
    ds_id = llm_service.ds.id if isinstance(llm_service.ds, CoreDatasource) else None
    return oid, ds_id


def _fail(state: NlqState, record_id: Optional[int], exc: BaseException) -> NlqState:
    traceback.print_exc()
    error_msg = _error_message(exc)
    if record_id is not None:
        try:
            with session_scope() as session:
                record_save_error(session, record_id, error_msg)
        except Exception:
            traceback.print_exc()
    return {**state, "error": error_msg}


def _finish_step_value(state: NlqState) -> int:
    fs = state.get("finish_step") or ChatFinishStep.GENERATE_CHART
    try:
        return int(fs.value if hasattr(fs, "value") else fs)
    except Exception:
        return int(ChatFinishStep.GENERATE_CHART.value)


def _step_base(state: NlqState) -> int:
    return len(state.get("all_steps") or [])


def _plan_dict_from_query_plan(plan: QueryPlan) -> Dict[str, Any]:
    format_statement = plan.statement
    return {
        "sql": plan.payload.get("sql", plan.statement),
        "format_statement": format_statement,
        "tables": list(plan.resources or []),
        "chart_type": plan.chart_type or "table",
        "brief": plan.brief or "",
        "plan": plan,
    }


def _accept_plan(
    llm_service: Any, plan: QueryPlan
) -> tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Validate a successful QueryPlan and shape it into a batch entry.

    Returns ``(entry, error_message)``. ``error_message`` is set when protocol
    validate_plan rejects the SQL (unknown column, unsafe, unauthorized table).
    """
    if not plan.success:
        return None, (plan.message or None)
    plan = llm_service.protocol.validate_plan(
        llm_service.ds, plan, llm_service.table_name_list
    )
    if not plan.success:
        msg = plan.message or "Plan validation failed"
        SQLBotLogUtil.warning(f"Plan validation failed: {msg}")
        return None, msg
    format_statement = llm_service.protocol.format_statement_for_display(plan)
    entry = _plan_dict_from_query_plan(plan)
    entry["format_statement"] = format_statement
    entry["sql"] = plan.payload.get("sql", plan.statement)
    return entry, None


def _parse_query_generation(
    raw_text: str, llm_service: Any, max_batch_size: int = _MAX_BATCH_SIZE
) -> tuple[List[Dict[str, Any]], Optional[str]]:
    """Parse LLM SQL-generation output through the protocol.

    Returns ``(plans, refusal_message)``.

    Protocol contract (unchanged from single-query era):
    - success plan object/array → executable plans after validate_plan
    - ``{"success": false, "message": "..."}`` → user-facing refusal/clarification
    - non-JSON / empty → parse error message
    """
    plans: List[Dict[str, Any]] = []
    refusals: List[str] = []

    json_str = extract_nested_json(raw_text)
    if json_str is None:
        # Protocol owns parse diagnostics for free-form text
        plan = llm_service.protocol.parse_llm_output(raw_text)
        if plan.success:
            entry, err = _accept_plan(llm_service, plan)
            if entry:
                return [entry], None
            return [], err or plan.message or "SQL answer is not a valid json object"
        return [], plan.message or "SQL answer is not a valid json object"

    try:
        data = orjson.loads(json_str)
    except Exception:
        plan = llm_service.protocol.parse_llm_output(raw_text)
        return [], (plan.message if not plan.success else "Cannot parse sql from answer")

    items = data if isinstance(data, list) else [data]
    for item in items:
        if not isinstance(item, dict):
            continue
        # Reuse protocol.parse_llm_output so chart-type/tables/brief stay one code path
        plan = llm_service.protocol.parse_llm_output(orjson.dumps(item).decode())
        if not plan.success:
            if plan.message:
                refusals.append(str(plan.message))
            continue
        entry, err = _accept_plan(llm_service, plan)
        if entry:
            plans.append(entry)
        elif err:
            refusals.append(str(err))
        elif plan.message:
            refusals.append(str(plan.message))

    if plans:
        return plans[:max_batch_size], None

    # No executable plan — surface LLM refusal/clarification as the error (legacy UX).
    if refusals:
        # Prefer last refusal (usually the only one for single-object outputs)
        return [], refusals[-1]

    # Last resort through full text
    plan = llm_service.protocol.parse_llm_output(raw_text)
    if plan.success:
        entry, err = _accept_plan(llm_service, plan)
        if entry:
            return [entry], None
        return [], err or plan.message or "Failed to generate any valid SQL queries"
    return [], plan.message or "Failed to generate any valid SQL queries"


def _result_rows(step: Dict[str, Any]) -> List[Dict[str, Any]]:
    result = step.get("result") or {}
    rows = result.get("data") if isinstance(result, dict) else None
    return rows if isinstance(rows, list) else []


def _result_fields(step: Dict[str, Any]) -> List[str]:
    result = step.get("result") or {}
    fields = result.get("fields") if isinstance(result, dict) else None
    if isinstance(fields, list) and fields:
        return [str(f) for f in fields]
    rows = _result_rows(step)
    if rows and isinstance(rows[0], dict):
        return [str(k) for k in rows[0].keys()]
    return []


# ── Shared row-scan primitives ────────────────────────────────────────────


def _scan_field(rows: List[Dict[str, Any]], field: str) -> Dict[str, Any]:
    """Single row scan returning null_count, values (non-null), numeric_vals."""
    values: List[Any] = []
    numeric_vals: List[float] = []
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


def _null_rate(rows: List[Dict[str, Any]], field: str) -> float:
    if not rows:
        return 0.0
    scan = _scan_field(rows, field)
    return scan["null_count"] / max(len(rows), 1)


def _metric_stats(rows: List[Dict[str, Any]], field: str) -> Dict[str, Any]:
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


def _column_stats(rows: List[Dict[str, Any]], field: str) -> Dict[str, Any]:
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

    unique_count = len(set(str(v) for v in values))
    stats: Dict[str, Any] = {"unique": unique_count, "null_count": scan["null_count"]}

    # Temporal: string dates (YYYY-MM / YYYY-MM-DD) — sort for min/max so the
    # LLM gets the true time span instead of guessing from top-N frequency.
    if not numeric_vals:
        str_vals = [str(v).strip() for v in values if v is not None and str(v).strip()]
        temporal_vals = [v for v in str_vals if _TEMPORAL_RE.match(v)]
        if temporal_vals and len(temporal_vals) >= len(str_vals) * 0.5:
            temporal_vals.sort()
            stats.update({
                "type": "temporal",
                "min": temporal_vals[0],
                "max": temporal_vals[-1],
            })
            return stats

    if numeric_vals and len(numeric_vals) >= len(values) * 0.5:
        numeric_vals.sort()
        mid = len(numeric_vals) // 2
        median = (
            numeric_vals[mid]
            if len(numeric_vals) % 2
            else (numeric_vals[mid - 1] + numeric_vals[mid]) / 2
        )
        stats.update({
            "type": "numeric",
            "min": numeric_vals[0],
            "max": numeric_vals[-1],
            "avg": round(sum(numeric_vals) / len(numeric_vals), 2),
            "median": median,
        })
    else:
        freq: Dict[str, int] = {}
        for v in values:
            s = str(v).strip()
            if s:
                freq[s] = freq.get(s, 0) + 1
        top = sorted(freq.items(), key=lambda x: -x[1])[:8]
        stats.update({
            "type": "categorical",
            "top_values": [{"value": k, "count": c} for k, c in top],
        })
    return stats


def _data_sample(rows: List[Dict[str, Any]], max_rows: int = 8) -> List[Dict[str, Any]]:
    """Compact sample rows for LLM (values truncated to avoid token waste)."""
    out: List[Dict[str, Any]] = []
    for r in rows[:max_rows]:
        if not isinstance(r, dict):
            continue
        compact: Dict[str, Any] = {}
        for k, v in r.items():
            s = str(v) if v is not None else ""
            compact[k] = s[:80] if len(s) > 80 else v
        out.append(compact)
    return out


def _assess_step_quality(step: Dict[str, Any], index: int) -> Dict[str, Any]:
    """Deterministic quality signals for one executed step (no LLM).

    Returns metadata (row_count, fields, null_rates, metrics) for severity
    scoring plus column_stats + data_sample so the decide LLM can reason
    about actual values rather than writing hypothetical conclusions.
    """
    issues: List[str] = []
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
            "truncated": True,
            "null_rates": {},
            "metrics": {},
            "column_stats": {},
            "data_sample": [],
            "issues": issues,
            "severity": True,
        }

    rows = _result_rows(step)
    fields = _result_fields(step)
    result = step.get("result") or {}
    truncated = bool(isinstance(result, dict) and result.get("limit"))
    if len(rows) >= _ROW_LIMIT:
        truncated = True

    # Use DB-engine-reported column types (from cursor.description) instead of
    # guessing by field name. fields_info is [{name, is_numeric}] per result.
    fields_info_list = result.get("fields_info") or []
    fields_info_map = {
        fi.get("name"): fi
        for fi in fields_info_list
        if isinstance(fi, dict) and fi.get("name")
    }

    null_rates: Dict[str, float] = {}
    metrics: Dict[str, Any] = {}
    col_stats: Dict[str, Any] = {}
    for f in fields:
        is_metric = bool(fields_info_map.get(f, {}).get("is_numeric", False))
        if is_metric:
            metrics[f] = _metric_stats(rows, f)
        else:
            rate = _null_rate(rows, f)
            null_rates[f] = round(rate, 3)
            if rows and rate >= NULL_DIM_SEVERE:
                issues.append(
                    f"维度列「{f}」空值率 {rate:.0%}（join/字段选择可能错误）"
                )
            elif rows and rate >= 0.35:
                issues.append(f"维度列「{f}」空值率偏高 {rate:.0%}")
        # column_stats for ALL fields (metrics get numeric stats, dims get categorical)
        col_stats[f] = _column_stats(rows, f)

    if not rows:
        issues.append("结果为空（0 行）")
    for mf, st in metrics.items():
        if st.get("count", 0) == 0:
            issues.append(f"指标列「{mf}」无可汇总数值")
        elif st.get("sum", 0) == 0 and st.get("max", 0) == 0:
            issues.append(f"指标列「{mf}」全为 0")

    if truncated and len(rows) >= ROW_LIMIT_NEAR:
        issues.append(
            f"结果接近截断上限（{len(rows)} 行 / limit {_ROW_LIMIT}），排序靠前可能偏置"
        )

    severity = bool(step.get("error")) or (not rows) or any(
        r >= NULL_DIM_SEVERE for r in null_rates.values()
    )

    return {
        "index": index,
        "brief": brief,
        "sql": sql,
        "row_count": len(rows),
        "fields": fields,
        "truncated": truncated,
        "null_rates": null_rates,
        "metrics": metrics,
        "column_stats": col_stats,
        "data_sample": _data_sample(rows),
        "issues": issues,
        "severity": severity,
    }


def _assess_all_steps(all_steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [_assess_step_quality(s, i) for i, s in enumerate(all_steps or [])]


def _quality_requires_repair(assessments: List[Dict[str, Any]]) -> bool:
    """Force another SQL round only on severe failures (empty / high-null / errors)."""
    if not assessments:
        return False
    return any(a.get("severity") for a in assessments)


def _format_assessment_block(assessments: List[Dict[str, Any]]) -> str:
    blocks: List[str] = []
    for a in assessments:
        lines = [
            f"### 查询{a['index'] + 1}"
            + (f"（{a['brief']}）" if a.get("brief") else ""),
            f"- 行数: {a.get('row_count')}"
            + ("（可能截断）" if a.get("truncated") else ""),
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
            lines.append(f"- 指标: {'; '.join(ms)}")

        # Column stats: unique values, top-N for categoricals, min/max for
        # temporal/numeric fields
        col_stats = a.get("column_stats") or {}
        if col_stats:
            stat_parts: List[str] = []
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
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def _summarize_steps(all_steps: List[Dict[str, Any]]) -> str:
    """Quality-aware step summary for decide / continue context."""
    assessments = _assess_all_steps(all_steps)
    if not assessments:
        return "（尚无已执行查询）"
    header = (
        "下列为已落地执行的查询及其**数据质检**摘要。"
        "若存在高空值维度、空结果、聚合 LIMIT 截断或字段口径可疑，应优先改写 SQL 而非直接下结论。\n"
    )
    return header + "\n\n" + _format_assessment_block(assessments)


def _repair_instruction(assessments: List[Dict[str, Any]], question: str) -> str:
    issues = []
    empty_or_zero = False
    for a in assessments:
        if int(a.get("row_count") or 0) == 0 or a.get("error"):
            empty_or_zero = True
        for it in a.get("issues") or []:
            issues.append(f"查询{a['index'] + 1}: {it}")
    issue_text = "\n".join(f"- {x}" for x in issues) or "- （未列出细则，请对照质检摘要）"
    anti_empty = ""
    if empty_or_zero:
        anti_empty = (
            "7. **禁止改得更空**：禁止在已有 0 行/近空结果上继续收紧等值过滤；"
            "应放宽为 plan-context 的 IN/后缀匹配、核对时间列与 join 键，"
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
        "5. 聚合分析不要用无意义的 LIMIT 充当前 N 页全貌；若必须限制，ORDER BY 应用业务指标。\n"
        "6. 仍返回系统约定的 JSON（单对象或数组）。\n"
        f"{anti_empty}"
    )


def _normalize_result_data(result: Dict[str, Any], llm_service: LLMService) -> Dict[str, Any]:
    data = DataFormat.convert_large_numbers_in_object_array(result.get("data"))
    data = DataFormat.normalize_qualified_sql_column_keys_in_object_array(data)
    if data:
        data = prepare_for_orjson(data)
        result = dict(result)
        result["row_count"] = len(data)
        if (
            llm_service.enable_sql_row_limit
            and isinstance(data, list)
            and len(data) > _ROW_LIMIT
        ):
            result["data"] = data[:_ROW_LIMIT]
            result["limit"] = _ROW_LIMIT
        else:
            result["data"] = data
    else:
        result = dict(result)
        result["data"] = data or []
    if llm_service.ds is not None:
        result["datasource"] = getattr(llm_service.ds, "id", None)
    return result


def _merge_batch_into_steps(
    all_steps: List[Dict[str, Any]],
    batch_plans: List[Dict[str, Any]],
    batch_results: List[Dict[str, Any]],
    batch_charts: List[Dict[str, Any]],
    *,
    entity_bindings: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Append current batch entries once. Idempotent by global offset."""
    updated = list(all_steps or [])
    base = len(updated)
    if not batch_plans:
        return updated

    # Already merged (same batch base size growth)
    if batch_results and len(updated) >= base + len(batch_plans):
        # Heuristic: if last N steps match plan sqls, skip
        tail = updated[-len(batch_plans) :]
        if all(
            (tail[i].get("format_statement") or tail[i].get("sql"))
            == (batch_plans[i].get("format_statement") or batch_plans[i].get("sql"))
            for i in range(len(batch_plans))
        ):
            return updated

    result_by_idx = {
        r.get("index"): r for r in (batch_results or []) if isinstance(r, dict)
    }
    def _sql_fp(entry: Dict[str, Any]) -> str:
        sql = (entry.get("format_statement") or entry.get("sql") or "").strip().lower()
        return re.sub(r"\s+", " ", sql)

    existing_fps = {_sql_fp(s) for s in updated if (s.get("format_statement") or s.get("sql"))}

    for i, plan_dict in enumerate(batch_plans):
        entry: Dict[str, Any] = {
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


def _steps_payload(all_steps: List[Dict[str, Any]], analysis_text: str = "") -> Dict[str, Any]:
    steps_data: List[Dict[str, Any]] = []
    for step in all_steps or []:
        step_entry: Dict[str, Any] = {
            "sql": step.get("format_statement") or step.get("sql", ""),
            "brief": step.get("brief") or "",
            "chart": step.get("chart"),
        }
        if step.get("error"):
            step_entry["error"] = step["error"]
        result = step.get("result") or {}
        if result:
            step_entry["data"] = {
                "fields": result.get("fields", []),
                "fields_info": result.get("fields_info"),
                "data": result.get("data", []),
                "limit": result.get("limit"),
                "row_count": result.get("row_count"),
                "datasource": result.get("datasource"),
            }
        steps_data.append(step_entry)
    return {"steps": steps_data, "analysis": analysis_text or ""}


def _persist_record_snapshot(
    llm_service: LLMService,
    all_steps: List[Dict[str, Any]],
    analysis_text: str = "",
    *,
    finish: bool = False,
) -> None:
    """Write multi-step payload + last-sql/chart/re_exec compatibility fields."""
    payload = _steps_payload(all_steps, analysis_text)
    with session_scope() as session:
        save_sql_exec_data(
            session=session,
            record_id=llm_service.record.id,
            data=orjson.dumps(payload).decode(),
        )
        if all_steps:
            last = all_steps[-1]
            last_sql = last.get("format_statement") or last.get("sql") or ""
            if last_sql:
                save_sql(session=session, sql=last_sql, record_id=llm_service.record.id)
            if last.get("chart"):
                save_chart(
                    session=session,
                    chart=orjson.dumps(last["chart"]).decode(),
                    record_id=llm_service.record.id,
                )
            re_exec = last.get("re_exec")
            if re_exec:
                save_re_exec(
                    session=session,
                    record_id=llm_service.record.id,
                    re_exec=orjson.dumps(re_exec).decode()
                    if not isinstance(re_exec, str)
                    else re_exec,
                )
        if analysis_text:
            save_analysis_answer(
                session=session,
                record_id=llm_service.record.id,
                answer=orjson.dumps({"content": analysis_text}).decode(),
            )
        if finish:
            record_finish(session, llm_service.record.id)


def _apply_row_permissions(
    llm_service: LLMService, session: Any, plan_dict: Dict[str, Any]
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
        ((not llm_service.current_assistant or is_page_embedded) and is_normal_user(llm_service.current_user))
        or use_dynamic_ds
    ):
        return qp

    if use_dynamic_ds:
        dynamic_result = generate_assistant_dynamic_sql(
            llm_service, session, sql, qp.resources
        )
        temp_sql = dynamic_result.get("sqlbot_temp_sql_text") if dynamic_result else None
        if temp_sql:
            assistant_sql = (
                generate_filter(llm_service, session, sql, qp.resources) or sql
            )
            for origin_table, subsql in (dynamic_result or {}).items():
                if origin_table == "sqlbot_temp_sql_text":
                    continue
                assistant_sql = assistant_sql.replace(
                    f"{DYNAMIC_SUBSQL_PREFIX}{origin_table}", subsql
                )
            sql = assistant_sql
    else:
        sql_result = generate_filter(llm_service, session, sql, qp.resources)
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


def _table_chart(fields: List[str], title: str = "") -> Dict[str, Any]:
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
    json_result: Dict[str, Any] = {"success": True}

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
            "batch_plans": [],
            "batch_results": [],
            "batch_charts": [],
            "max_steps": state.get("max_steps") or _MAX_STEPS,
            "max_batch_size": state.get("max_batch_size") or _MAX_BATCH_SIZE,
            "analysis_text": "",
            "decision": "",
            "repair_hint": "",
            "gen_attempts": 0,
            "entity_bindings": {},
            "query_bindings": {},
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


def match_terminology_node(state: NlqState) -> NlqState:
    llm_service = state["llm_service"]
    oid, ds_id = _ds_scope(llm_service)
    with session_scope() as session:
        try:
            match_terminology(llm_service, session, oid, ds_id)
            return {**state, "record": llm_service.record}
        except Exception as e:
            return _fail(state, llm_service.record.id, e)


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


def build_context_node(state: NlqState) -> NlqState:
    """Schema retrieval + SQL/chart prompt message assembly."""
    llm_service = state["llm_service"]
    with session_scope() as session:
        try:
            build_prompt_messages(llm_service, session)
            return {**state, "record": llm_service.record}
        except Exception as e:
            return _fail(state, llm_service.record.id, e)


# ── Nodes (agentic batch loop) ───────────────────────────────────────────────

def ground_entities_node(state: NlqState) -> NlqState:
    """Probe organization-like dimensions before SQL generation.

    NL labels (e.g. 研发二部) often differ from warehouse values (战客研发二部).
    Run small DISTINCT probes and write structured ``entity_bindings`` only —
    prompt text is assembled later via ``plan_context``.
    """
    llm_service = state["llm_service"]
    sink = StreamSink.from_state(state)
    record_id = getattr(llm_service.record, "id", None) or state.get("record_id")
    question = (llm_service.chat_question.question or "").strip()
    if not question or not llm_service.ds:
        return {**state, "entity_bindings": state.get("entity_bindings") or {}}

    with log_span(
        operate=OperationEnum.GROUND_ENTITIES,
        record_id=record_id,
        ai_modal_id=getattr(llm_service.chat_question, "ai_modal_id", None),
        ai_modal_name=getattr(llm_service.chat_question, "ai_modal_name", None),
        local_operation=True,
        graph_node="ground_entities",
    ) as span:
        result_state = _ground_entities_impl(state, llm_service, sink)
        binds = result_state.get("entity_bindings") or {}
        span["payload"] = {
            "candidates": binds.get("candidates") or [],
            "resolved": binds.get("resolved") or {},
        }
        return result_state


def _extract_entity_candidates_via_llm(
    llm_service: LLMService, question: str, history_context: str = ""
) -> List[str]:
    """Use LLM to extract dimension entity candidates from the question.

    Unlike regex, this understands context: question modifiers like "应该是"
    are separated from the actual entity name. Language-agnostic, no hardcoded terms.
    """
    prompt = (
        "从以下用户问题中提取可能的维度实体名称（如组织、部门、人员、系统、项目等）。\n"
        "只提取用户指代的具体名称，忽略疑问词、修饰词、动词。\n"
        "例如：'X是Y的项目吗' → [\"X\", \"Y\"]；"
        "'应该是Z吧' → [\"Z\"]；"
        "'W负责的指标有多少' → [\"W\"]。\n"
    )
    if history_context:
        prompt += f"上文参考：{history_context}\n"
    prompt += (
        f"用户问题：{question}\n\n"
        "只返回 JSON 数组：[\"名称1\", \"名称2\"]。如果没有可提取的名称返回 []。"
    )
    try:
        resp = llm_service.llm.invoke([HumanMessage(prompt)])
        raw = resp.content if isinstance(resp.content, str) else str(resp.content or "")
        js = extract_nested_json(raw)
        if js:
            data = orjson.loads(js)
            if isinstance(data, list):
                return [
                    str(v).strip()
                    for v in data
                    if isinstance(v, (str, int, float)) and str(v).strip() and len(str(v).strip()) >= 2
                ]
    except Exception as exc:
        SQLBotLogUtil.warning("entity candidate extraction failed: %s" % exc)
    return []


def _ground_entities_impl(
    state: NlqState, llm_service: LLMService, sink: StreamSink
) -> NlqState:
    question = (llm_service.chat_question.question or "").strip()

    # Get history context for follow-up questions
    history_context = ""
    all_steps = state.get("all_steps") or []
    if all_steps:
        last_bindings = all_steps[-1].get("_entity_bindings") or {}
        resolved = last_bindings.get("resolved") or {}
        if resolved:
            parts = []
            for phrase, info in resolved.items():
                if isinstance(info, dict):
                    parts.append(f"{phrase}→{info.get('canonical')}")
            if parts:
                history_context = "之前已解析的实体：" + "；".join(parts)

    # LLM-based candidate extraction (context-aware, no regex/hardcoded terms)
    candidates = _extract_entity_candidates_via_llm(llm_service, question, history_context)
    if not candidates:
        return {**state, "entity_bindings": state.get("entity_bindings") or {}}

    # Dimension probes — independent of RAG table_name_list so org tables
    # are still explored even when embedding only returned fact tables.
    probe_specs = [
        ("d_organization", "organization_name", "organization_name"),
        ("d_user", "organization_name", "organization_name"),
    ]

    def _probe(table: str, col: str, phrase: str) -> List[str]:
        phrase_esc = phrase.replace("'", "''").replace("%", "").replace("_", "")
        if not phrase_esc:
            return []
        sql = (
            "SELECT DISTINCT `{col}` AS v FROM `{table}` "
            "WHERE `{col}` LIKE '%{ph}%' "
            "AND `{col}` IS NOT NULL AND `{col}` <> '' "
            "LIMIT 30"
        ).format(col=col, table=table, ph=phrase_esc)
        vals: List[str] = []
        try:
            plan = QueryPlan(
                success=True,
                statement=sql,
                payload={"sql": sql},
                resources=[table],
            )
            qr = llm_service.protocol.execute(llm_service.ds, plan)
            for r in qr.data or []:
                if not isinstance(r, dict):
                    continue
                v = r.get("v")
                if v is None and r:
                    v = next(iter(r.values()), None)
                if v is not None and str(v).strip():
                    vals.append(str(v).strip())
        except Exception as exc:
            SQLBotLogUtil.warning("entity probe fail %s.%s: %s" % (table, col, exc))
        out: List[str] = []
        seen: set[str] = set()
        for v in vals:
            if v not in seen:
                seen.add(v)
                out.append(v)
        return out

    matched: Dict[str, List[str]] = {}
    col_hints: Dict[str, str] = {}
    for phrase in candidates:
        hits: List[str] = []
        hint = "organization_name"
        for table, col, col_hint in probe_specs:
            got = _probe(table, col, phrase)
            if got:
                hits.extend(got)
                hint = col_hint
        uh: List[str] = []
        s: set[str] = set()
        for h in hits:
            if h not in s:
                s.add(h)
                uh.append(h)
        if uh:
            matched[phrase] = uh[:20]
            col_hints[phrase] = hint

    if not matched:
        return {
            **state,
            "entity_bindings": {"candidates": candidates, "resolved": {}},
        }

    resolved: Dict[str, Any] = {}
    for phrase, hits in matched.items():
        ranked = sorted(
            hits,
            key=lambda h: (
                0 if h == phrase else 1,
                0 if h.endswith(phrase) else 1,
                0 if phrase in h else 1,
                len(h),
            ),
        )
        pick = ranked[0]
        if len(ranked) > 1:
            try:
                prompt = (
                    "将用户说法映射到数据库机构/部门标准名称。\n"
                    "用户说法：%s\n"
                    "候选：%s\n"
                    "只返回 JSON：{\"canonical\":\"必须来自候选\",\"reason\":\"一句\"}"
                ) % (phrase, orjson.dumps(ranked[:12]).decode())
                resp = llm_service.llm.invoke([HumanMessage(prompt)])
                raw = (
                    resp.content
                    if isinstance(resp.content, str)
                    else str(resp.content or "")
                )
                js = extract_nested_json(raw)
                if js:
                    data = orjson.loads(js)
                    cand = (data.get("canonical") or "").strip()
                    if cand in hits:
                        pick = cand
            except Exception as exc:
                SQLBotLogUtil.warning("entity disambiguation fail: %s" % exc)
        # Canonical picked → use eq (= canonical).  Alternatives are advisory
        # notes only; they are NOT auto-injected into an IN list (which would
        # pull in deprecated/废弃 values the user didn't ask for).
        resolved[phrase] = {
            "canonical": pick,
            "alternatives": [h for h in ranked if h != pick][:8],
            "match": "eq",
            "column_hint": col_hints.get(phrase) or "organization_name",
        }

    # State only — do not append sql_message here.
    try:
        sink.event(
            {
                "type": "entity-grounding",
                "content": orjson.dumps(
                    {"candidates": candidates, "resolved": resolved}
                ).decode(),
            }
        )
    except Exception:
        pass
    SQLBotLogUtil.info("entity_bindings resolved=%s" % resolved)
    return {
        **state,
        "entity_bindings": {"candidates": candidates, "resolved": resolved},
        "record": llm_service.record,
    }



def _extract_title_from_sql_answer(raw_text: str, plans: List[Dict[str, Any]]) -> str:
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
        title = (llm_service.chat_question.question or "").strip()[:20]
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


def _mark_generate_validation_failed(llm_service: LLMService) -> None:
    """Reflect post-generation validation failure in the existing ChatLog row."""
    log = llm_service.current_logs.get(OperationEnum.GENERATE_QUERY)
    if not log:
        return
    try:
        with session_scope() as session:
            trigger_log_error(session, log)
    except Exception:
        # Observability must not affect retry/failure behavior.
        SQLBotLogUtil.warning("Failed to mark GENERATE_QUERY validation error")


def _attach_plan_context_for_generate(
    llm_service: LLMService,
    state: NlqState,
    *,
    repair: str = "",
    extra_sections: Optional[List[str]] = None,
    include_playbook: bool = True,
) -> str:
    """Render PlanContext once and stash on chat_question for build_user_prompt."""
    body = render_plan_context(
        entity_bindings=state.get("entity_bindings"),
        query_bindings=state.get("query_bindings"),
        include_playbook=include_playbook,
        repair=repair,
        extra_sections=extra_sections,
    )
    wrapped = wrap_plan_context(body)
    try:
        setattr(llm_service.chat_question, "plan_context", wrapped)
    except Exception:
        pass
    return wrapped


def generate_queries_node(state: NlqState) -> NlqState:
    """Plan SQL queries for the current batch.

    Plan-time validate failures set ``repair_hint`` + ``gen_attempts`` and let
    ``route_after_queries`` loop back (no hard-fail until budget exhausted).

    Prompt path: probe nodes write state only；this node assembles one PlanContext
    block into the user prompt via ``chat_question.plan_context``.
    """
    llm_service = state["llm_service"]
    sink = StreamSink.from_state(state)
    step_index = state.get("step_index", 0)
    all_steps = state.get("all_steps") or []
    base = _step_base(state)
    json_result: Dict[str, Any] = dict(state.get("json_result") or {"success": True})
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
        extra_sections: List[str] = []

        # Inherit entity bindings from previous round when current round has none
        # (follow-up like "只查看今年的吧" has no org name in question)
        current_bindings = state.get("entity_bindings") or {}
        if step_index > 0 and all_steps and not current_bindings.get("resolved"):
            prev_bindings = {}
            for step in reversed(all_steps):
                eb = step.get("_entity_bindings") or {}
                if eb.get("resolved"):
                    prev_bindings = eb
                    break
            if prev_bindings.get("resolved"):
                state = {**state, "entity_bindings": prev_bindings}
                SQLBotLogUtil.info(
                    "inherited entity_bindings from previous round: %s"
                    % list((prev_bindings.get("resolved") or {}).keys())
                )

        # Subsequent post-exec rounds: quality summary is secondary insurance.
        if step_index > 0 and all_steps:
            assessments = _assess_all_steps(all_steps)
            if not repair and _quality_requires_repair(assessments):
                repair = _repair_instruction(
                    assessments, llm_service.chat_question.question or ""
                )
            summary = _summarize_steps(all_steps)
            extra_sections.append(
                "## 已执行查询与质检摘要（改写时参考，禁止改得更空）\n" + summary
            )
            if repair:
                extra_sections.append("## 改写指令\n" + repair)

            # Inject previous SQL join paths for cross-validation on follow-up
            prev_sqls = [
                (s.get("format_statement") or s.get("sql") or "")
                for s in all_steps
                if (s.get("format_statement") or s.get("sql") or "").strip()
            ]
            xval = build_cross_validation_section(
                prev_sqls,
                llm_service.chat_question.question or "",
            )
            if xval:
                extra_sections.append(xval)

        _attach_plan_context_for_generate(
            llm_service,
            state,
            repair=repair if step_index == 0 else "",
            extra_sections=extra_sections,
            include_playbook=True,
        )
        try:
            sink.event(
                {
                    "type": "plan-context",
                    "content": getattr(llm_service.chat_question, "plan_context", "") or "",
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
                setattr(llm_service.chat_question, "plan_context", "")
            except Exception:
                pass

        max_batch = state.get("max_batch_size") or _MAX_BATCH_SIZE
        plans, refusal = _parse_query_generation(
            full_sql_text, llm_service, max_batch_size=max_batch
        )

        _maybe_update_chat_brief(
            llm_service, sink, _extract_title_from_sql_answer(full_sql_text, plans)
        )

        if not plans:
            msg = refusal or "Failed to generate any valid SQL queries"
            attempts = gen_attempts + 1
            repair_msg = _plan_repair_message(msg)
            _mark_generate_validation_failed(llm_service)
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

        for i, pitem in enumerate(plans):
            gidx = base + i
            display_sql = pitem.get("format_statement") or pitem.get("sql") or ""
            sink.event(
                {
                    "content": display_sql,
                    "type": "step-sql",
                    "index": gidx,
                    "engine_type": getattr(llm_service.ds, "type", None),
                    "brief": pitem.get("brief") or "",
                    "title": pitem.get("brief") or "",
                }
            )

        sink.event(
            {
                "type": "batch-plans",
                "index": step_index,
                "base_index": base,
                "count": len(plans),
            }
        )

        with session_scope() as session:
            save_sql(
                session=session,
                sql=plans[-1].get("format_statement") or plans[-1].get("sql") or "",
                record_id=llm_service.record.id,
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
    Progressive ChatRecord.data snapshots enable frontend mid-stream REST fetches.
    """
    llm_service = state["llm_service"]
    sink = StreamSink.from_state(state)
    plans = list(state.get("batch_plans") or [])
    base = _step_base(state)
    all_steps = list(state.get("all_steps") or [])

    if not plans:
        return _fail(state, llm_service.record.id, SingleMessageError("No plans to execute"))

    # 1) Prepare executable plans (permissions) on main thread
    prepared: List[Dict[str, Any]] = []
    with session_scope() as session:
        for i, plan_dict in enumerate(plans):
            try:
                qp = _apply_row_permissions(llm_service, session, plan_dict)
                prepared.append({**plan_dict, "plan": qp, "index": i})
            except Exception as e:
                prepared.append(
                    {
                        **plan_dict,
                        "index": i,
                        "prep_error": _error_message(e),
                    }
                )

    results: List[Optional[Dict[str, Any]]] = [None] * len(prepared)

    def _execute_single(idx: int, plan_dict: Dict[str, Any]) -> Dict[str, Any]:
        gidx = base + idx
        sql_show = (
            plan_dict.get("format_statement")
            or plan_dict.get("sql")
            or ""
        )
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
                    qr = llm_service.protocol.execute(llm_service.ds, qp)
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
                    "error": _error_message(exc)[:500],
                }
                raise

    try:
        # Fast path: single query no thread pool
        workers = min(len(prepared), state.get("max_batch_size") or _MAX_BATCH_SIZE)
        if workers <= 1:
            idx = 0
            try:
                r = _execute_single(0, prepared[0])
                results[0] = r
            except Exception as e:
                results[0] = {
                    "index": 0,
                    "error": _error_message(e),
                    "plan": prepared[0],
                }
        else:
            with ThreadPoolExecutor(max_workers=workers) as pool:
                futures = {
                    pool.submit(_execute_single, i, p): i for i, p in enumerate(prepared)
                }
                for future in as_completed(futures):
                    idx = futures[future]
                    try:
                        results[idx] = future.result()
                    except Exception as e:
                        results[idx] = {
                            "index": idx,
                            "error": _error_message(e),
                            "plan": prepared[idx],
                        }

        # Emit SSE in plan-index order, then persist via the single merge helper
        flat_results: List[Dict[str, Any]] = []
        for i, r in enumerate(results):
            if r is None:
                continue
            gidx = base + i
            if r.get("error"):
                sink.event(
                    {
                        "type": "step-error",
                        "index": gidx,
                        "error": r.get("error"),
                        "content": r.get("error"),
                    }
                )
            else:
                sink.event(
                    {
                        "type": "step-data",
                        "index": gidx,
                        "record_id": llm_service.record.id,
                        "datasource": getattr(llm_service.ds, "id", None),
                    }
                )
            flat_results.append(r)

        snapshot_steps = _merge_batch_into_steps(
            all_steps, prepared, flat_results, [],
            entity_bindings=state.get("entity_bindings"),
        )
        try:
            _persist_record_snapshot(
                llm_service, snapshot_steps, state.get("analysis_text") or ""
            )
        except Exception:
            traceback.print_exc()

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
        }
    except Exception as e:
        return _fail(state, llm_service.record.id, e)


def generate_charts_node(state: NlqState) -> NlqState:
    """Generate chart configs for each batch result (sequential; isolates chart_message)."""
    llm_service = state["llm_service"]
    sink = StreamSink.from_state(state)
    batch_results = state.get("batch_results") or []
    base = _step_base(state)
    finish_v = _finish_step_value(state)

    # MCP / early stop: data only — emit table charts without LLM
    skip_llm = finish_v < int(ChatFinishStep.GENERATE_CHART.value)

    try:
        charts: List[Dict[str, Any]] = []
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
                sink.event(
                    {
                        "content": orjson.dumps(chart).decode(),
                        "type": "step-chart",
                        "index": gidx,
                    }
                )
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
                sink.event(
                    {
                        "content": orjson.dumps(chart).decode(),
                        "type": "step-chart",
                        "index": gidx,
                    }
                )
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
                    llm_service.chat_question.question,
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
                chart = check_save_chart(
                    llm_service, session=session, res=full_chart_text, fields=fields
                )
                charts.append(chart)
                sink.event(
                    {
                        "content": orjson.dumps(chart).decode(),
                        "type": "step-chart",
                        "index": gidx,
                    }
                )

        # Restore base chart messages after batch
        llm_service.chart_message = list(base_chart_messages)

        # Progressive snapshot with charts
        merged = _merge_batch_into_steps(
            state.get("all_steps") or [],
            state.get("batch_plans") or [],
            batch_results,
            charts,
            entity_bindings=state.get("entity_bindings"),
        )
        try:
            _persist_record_snapshot(
                llm_service, merged, state.get("analysis_text") or ""
            )
        except Exception:
            traceback.print_exc()

        return {**state, "batch_charts": charts, "record": llm_service.record}
    except Exception as e:
        return _fail(state, llm_service.record.id, e)


_DECIDE_PROMPT = """\
你是数据分析助手。系统已执行查询，并给出**数据质检摘要**（含 SQL、字段、空值率、指标、截断风险）。

{steps_summary}

用户原问题：{question}

{repair_policy}

请只返回一个 JSON（不要其它文字），action 取其一：
1. 需要改写/补充 SQL 以修复质检问题或补齐口径：
   {{"action":"continue","reason":"具体要改什么"}}
2. 已有足够数据，可以总结（text 必须是完整 Markdown 报告）：
   {{"action":"summarize","text":"..."}}
3. 无需更多文字（极少用，一般有数据就 summarize）：
   {{"action":"finish"}}

当 action=summarize 时，text **必须**包含以下小节（中文）：
## 结论
（直接回答用户问题；若数据有偏差要先写清局限）

## SQL 生成依据与解释
对**每条**已执行查询说明：
- 业务意图（回答问题的哪一部分）
- 选择的事实表/维度表及关联键
- 时间、人员、部门等字段为什么用这个（对照用户问题里的字段名/业务含义）
- 过滤条件、聚合与排序/LIMIT 的理由
- 与其它查询的口径是否一致

## 数据解读
结合行数、空值率、指标汇总解读结果；指出哪些维度大量为空、是否被截断。

## 数据质量与局限
明确列出仍存疑问或可能误导的点（join 失败、字段错用、LIMIT 偏置等）。

## 建议
若需进一步分析，给 1～3 条可执行的下一步（改字段/加过滤/换关联）。

## 结论规则
- 结论必须基于实际查询返回的数据值，禁止使用"如果/可能/或许"等假设性表述。
- 如果数据中未包含用户预期的值，直接说明"数据中未找到相关记录"并列出实际查到的值。
- 列出关键数据值作为证据（如具体名称、数量、ID），不得笼统概括。
"""


def decide_next_node(state: NlqState) -> NlqState:
    """Merge batch, run deterministic quality gate, then LLM decide/summarize."""
    llm_service = state["llm_service"]
    step_index = state.get("step_index", 0)
    max_steps = state.get("max_steps", _MAX_STEPS)
    finish_v = _finish_step_value(state)
    record_id = getattr(llm_service.record, "id", None) or state.get("record_id")

    # Impl may set used_llm=True when invoking model. Pure QC auto-continue is local.
    meta: Dict[str, Any] = {"used_llm": False}
    # Start as local; promote only if LLM fires (payload). Avoid false non-local spans.
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
        span["payload"] = {
            "decision": out.get("decision"),
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
    finish_v: int,
    *,
    meta: Optional[Dict[str, Any]] = None,
) -> NlqState:
    if meta is None:
        meta = {}
    batch_results = state.get("batch_results") or []
    batch_charts = state.get("batch_charts") or []
    batch_plans = state.get("batch_plans") or []

    updated_steps = _merge_batch_into_steps(
        state.get("all_steps") or [],
        batch_plans,
        batch_results,
        batch_charts,
        entity_bindings=state.get("entity_bindings"),
    )
    assessments = _assess_all_steps(updated_steps)
    needs_repair = _quality_requires_repair(assessments)
    question = llm_service.chat_question.question or ""
    repair_hint = _repair_instruction(assessments, question) if needs_repair else ""

    if finish_v < int(ChatFinishStep.GENERATE_CHART.value):
        meta["path"] = "finish_step_early"
        meta["used_llm"] = False
        return {
            **state,
            "decision": "finish",
            "all_steps": updated_steps,
            "step_index": step_index + 1,
            "batch_plans": [],
            "batch_results": [],
            "batch_charts": [],
            "repair_hint": "",
        }

    force_terminal = step_index >= max_steps - 1

    # Post-exec QC is insurance, not the main fix path.
    # Prefer summarize with honest limitations over automatic continue that
    # often rewrites filters dryer (empty → emptier). Allow at most one
    # continue when there is a clear recoverable signal (exec error / unknown
    # column class) and rounds remain.
    def _recoverable_continue(assess: List[Dict[str, Any]]) -> bool:
        if force_terminal:
            return False
        # Already spent a post-exec continuation batch.
        if step_index >= 1:
            return False
        texts: List[str] = []
        for a in assess:
            if a.get("error"):
                texts.append(str(a.get("error") or ""))
            for it in a.get("issues") or []:
                texts.append(str(it))
        blob = " ".join(texts).lower()
        markers = (
            "unknown column",
            "字段不存在",
            "doesn't exist",
            "执行失败",
            "syntax",
            "timeout",
            "超时",
        )
        if any(m in blob for m in markers):
            return True
        # Pure empty / all-zero without structural error → summarize, don't thrash.
        return False

    auto_continue = bool(needs_repair and _recoverable_continue(assessments))
    if auto_continue:
        SQLBotLogUtil.info(
            "decide_next quality gate -> continue (recoverable); issues="
            + str(sum(len(a.get("issues") or []) for a in assessments))
        )
        meta["path"] = "auto_continue"
        meta["used_llm"] = False
        return {
            **state,
            "decision": "continue",
            "analysis_text": state.get("analysis_text") or "",
            "all_steps": updated_steps,
            "step_index": step_index + 1,
            "batch_plans": [],
            "batch_results": [],
            "batch_charts": [],
            "repair_hint": repair_hint,
            "gen_attempts": 0,
        }

    try:
        steps_summary = _summarize_steps(updated_steps)
        if needs_repair:
            repair_policy = (
                "【质检未通过】默认 action=summarize，在「数据质量与局限」如实说明"
                "（空结果、过窄过滤、join/字段问题），展示已有表格，不要假装数据充分。"
                "仅当存在明确可修复的执行/列错误且 reason 写清时才 continue；"
                "**禁止**把已有近空结果改得更空。"
            )
        else:
            repair_policy = (
                "【质检基本通过】优先 action=summarize，给出带 SQL 依据的完整报告；"
                "仅当仍缺关键切片时再 continue。"
            )

        prompt = _DECIDE_PROMPT.format(
            steps_summary=steps_summary,
            question=question,
            repair_policy=repair_policy,
        )
        messages = list(llm_service.sql_message) + [HumanMessage(prompt)]
        meta["path"] = "llm_decide"
        meta["used_llm"] = True
        response: AIMessage = llm_service.llm.invoke(messages)
        response_text = (
            response.content
            if isinstance(response.content, str)
            else str(response.content or "")
        )

        decision = "summarize"
        analysis_text = state.get("analysis_text") or ""
        reason = ""
        json_str = extract_nested_json(response_text)
        if json_str:
            try:
                data = orjson.loads(json_str)
                action = data.get("action", "summarize")
                if action in ("continue", "summarize", "finish"):
                    decision = action
                if data.get("text"):
                    analysis_text = data.get("text") or analysis_text
                reason = data.get("reason") or ""
            except Exception:
                pass

        if force_terminal and decision == "continue":
            decision = "summarize"

        if decision == "summarize" and not (analysis_text or "").strip():
            analysis_text = (
                "## 结论\n"
                "系统未能生成完整文字总结，以下基于自动质检与数据样本给出判断。\n\n"
                "## 查询详情\n"
                + _format_assessment_block(assessments)
            )

        if decision == "continue" and reason:
            SQLBotLogUtil.info(f"LLM decides to continue: {reason}")
            if reason and not repair_hint:
                repair_hint = (
                    f"模型续写原因：{reason}\n\n"
                    + _repair_instruction(assessments, question)
                )

        if decision == "finish" and not (analysis_text or "").strip():
            decision = "summarize" if assessments else "finish"
            if decision == "summarize" and not analysis_text:
                analysis_text = "\n".join(
                    [
                        "## 结论",
                        "查询已完成。",
                        "",
                        "## SQL 生成依据与解释",
                        _format_assessment_block(assessments),
                    ]
                )

        return {
            **state,
            "decision": decision,
            "analysis_text": analysis_text,
            "all_steps": updated_steps,
            "step_index": step_index + 1,
            "batch_plans": [],
            "batch_results": [],
            "batch_charts": [],
            "repair_hint": repair_hint if decision == "continue" else "",
        }
    except Exception as e:
        meta["path"] = "error"
        meta["used_llm"] = False
        SQLBotLogUtil.error(f"decide_next_node error: {e}")
        stub = state.get("analysis_text") or ""
        if not stub and assessments:
            stub = (
                "## 结论\n"
                "分析决策阶段异常，以下仅列出已执行查询质检信息。\n\n"
                + _format_assessment_block(assessments)
            )
        return {
            **state,
            "decision": "summarize" if stub else "finish",
            "analysis_text": stub,
            "all_steps": updated_steps,
            "step_index": step_index + 1,
            "batch_plans": [],
            "batch_results": [],
            "batch_charts": [],
            "repair_hint": "",
        }


def summarize_node(state: NlqState) -> NlqState:
    """Stream the analysis text to the user."""
    sink = StreamSink.from_state(state)
    analysis_text = state.get("analysis_text") or ""
    llm_service = state.get("llm_service")
    record_id = None
    if llm_service is not None:
        record_id = getattr(getattr(llm_service, "record", None), "id", None)
    record_id = record_id or state.get("record_id")

    with log_span(
        operate=OperationEnum.ANALYSIS,
        record_id=record_id,
        ai_modal_id=getattr(getattr(llm_service, "chat_question", None), "ai_modal_id", None)
        if llm_service
        else None,
        ai_modal_name=getattr(
            getattr(llm_service, "chat_question", None), "ai_modal_name", None
        )
        if llm_service
        else None,
        local_operation=True,
        graph_node="summarize",
        brief="综合分析",
        step_index=state.get("step_index"),
        initial_payload={"source": "nlq_summarize", "chars": len(analysis_text)},
    ) as span:
        if analysis_text:
            sink.event({"type": "analysis", "content": analysis_text})
            if sink.mode == "markdown":
                sink.text(analysis_text + "\n\n")
            # Persist analysis like dedicated analysis path
            if llm_service is not None and getattr(llm_service, "record", None):
                try:
                    with session_scope() as session:
                        save_analysis_answer(
                            session=session,
                            record_id=llm_service.record.id,
                            answer=analysis_text,
                        )
                except Exception:
                    traceback.print_exc()
        span["payload"] = {
            "source": "nlq_summarize",
            "chars": len(analysis_text),
            "empty": not bool(analysis_text.strip()),
        }
        return state


def complete_node(state: NlqState) -> NlqState:
    """Persist multi-step payload and emit finish."""
    llm_service = state["llm_service"]
    sink = StreamSink.from_state(state)
    json_result: Dict[str, Any] = dict(state.get("json_result") or {"success": True})
    analysis_text = state.get("analysis_text") or ""
    return_img = bool(state.get("return_img", True))

    # Merge any leftover uncommitted batch (e.g. finish_step early routes that skip decide)
    updated_steps = _merge_batch_into_steps(
        state.get("all_steps") or [],
        state.get("batch_plans") or [],
        state.get("batch_results") or [],
        state.get("batch_charts") or [],
        entity_bindings=state.get("entity_bindings"),
    )
    # Ensure every successful step has a chart (MCP QUERY_DATA / table fallback)
    for step in updated_steps:
        if step.get("chart") or step.get("error"):
            continue
        fields = (step.get("result") or {}).get("fields") or []
        step["chart"] = _table_chart(fields, title=step.get("brief") or "")

    try:
        _persist_record_snapshot(
            llm_service, updated_steps, analysis_text, finish=True
        )
    except Exception:
        traceback.print_exc()
        try:
            with session_scope() as session:
                record_finish(session, llm_service.record.id)
        except Exception:
            traceback.print_exc()

    # Optional last-chart image (MCP markdown / json)
    if return_img and updated_steps:
        last_step = updated_steps[-1]
        chart = last_step.get("chart") or {}
        result = last_step.get("result") or {}
        if chart.get("type") and chart.get("type") != "table" and result:
            with session_scope() as session:
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
                        sink.text(f'![{chart.get("type")}]({image_url})')
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
        "record": llm_service.record,
    }


def fail_node(state: NlqState) -> NlqState:
    llm_service = state["llm_service"]
    sink = StreamSink.from_state(state)
    error_msg = state.get("error") or "unknown error"
    sink.error(error_msg)
    try:
        with session_scope() as session:
            record_finish(session, llm_service.record.id)
    except Exception:
        traceback.print_exc()
    return state


# ── Routers ──────────────────────────────────────────────────────────────────


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
) -> Literal["generate_queries", "summarize", "complete", "fail"]:
    if state.get("error"):
        return "fail"
    step_index = state.get("step_index", 0)
    max_steps = state.get("max_steps", _MAX_STEPS)
    decision = state.get("decision") or "finish"

    if step_index >= max_steps:
        if decision == "summarize" and (state.get("analysis_text") or ""):
            return "summarize"
        return "complete"

    if decision == "continue":
        return "generate_queries"
    if decision == "summarize":
        return "summarize"
    return "complete"
