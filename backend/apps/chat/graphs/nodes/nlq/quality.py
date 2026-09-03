"""Pure result-quality helpers: row scans, step assessments, batch merging."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any, Literal, cast

from apps.chat.aggregation_window import (
    aggregation_totals_sql,
)

# ── Constants ────────────────────────────────────────────────────────────────
from apps.chat.graphs.nodes.nlq.state import (
    _ROW_LIMIT,
    _TEMPORAL_RE,
    CandidateBatch,
    _sql_dialect,
)
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
    validation_issue_prompt_text,
)
from apps.chat.task.llm import LLMService
from apps.conversation.outcome import (
    ResultQuality,
    RunOutcome,
    outcome_from_steps,
)
from apps.protocol import QueryPlan
from common.utils.data_format import DataFormat
from common.utils.utils import SQLBotLogUtil, prepare_for_orjson


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
