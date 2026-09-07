"""Snapshot/audit projection helpers: snapshot values, row permissions, capture enqueue."""

from __future__ import annotations

from copy import deepcopy
from collections.abc import Mapping
from typing import Any, Literal, cast

import orjson

from apps.chat.constants import DYNAMIC_DS_TYPES
from apps.chat.graphs.nodes.nlq.state import (
    NlqState,
    _ds_scope,
    _generation_question,
)
from apps.chat.steps.knowledge import get_compiled_knowledge
from apps.chat.steps.permissions import (
    DYNAMIC_SUBSQL_PREFIX,
    generate_assistant_dynamic_sql,
    generate_filter,
)
from apps.chat.task.llm import LLMService
from apps.conversation.outcome import (
    RunOutcome,
    public_error_message,
)
from apps.conversation.run_service import (
    active_evidence,
)
from apps.conversation.session import session_scope
from apps.datasource.access import (
    AccessScope,
)
from apps.datasource.crud.permission import is_normal_user
from apps.protocol import QueryPlan
from apps.protocol.base import CAP_ROW_PERMISSION

# ── Constants ────────────────────────────────────────────────────────────────
from common.utils.utils import SQLBotLogUtil


def _merge_compiled_apply_log(llm_service: Any, additions: Any) -> dict[str, Any]:
    return {}


def _record_intent_default_application(
    llm_service: LLMService,
    applied_ids: list[int],
    *,
    unverified: bool = False,
) -> dict[str, Any]:
    return {}


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


def _enqueue_knowledge_capture(
    state: NlqState,
    llm_service: LLMService,
    outcome: RunOutcome,
    steps: list[dict[str, Any]],
) -> None:
    return


def _sql_alias_columns(sql: str, dialect: str) -> list[dict[str, str]]:
    from apps.chat.steps.enum_display import _sql_alias_columns as _impl

    return _impl(sql, dialect)


def _enum_refs_for_step(
    step: dict[str, Any],
    result_fields: list[str] | None = None,
    *,
    dialect: str = "mysql",
) -> tuple[list[str], dict[str, str]]:
    from apps.chat.steps.enum_display import enum_refs_for_query

    return enum_refs_for_query(
        sql=str(step.get("format_statement") or step.get("sql") or ""),
        fields=[str(f) for f in (result_fields or [])],
        tables=[str(t) for t in (step.get("tables") or step.get("resources") or [])],
        dialect=dialect,
    )


def _wiki_table_columns(table: str) -> set[str]:
    from apps.chat.steps.enum_display import wiki_table_columns

    return wiki_table_columns(table)


def _record_snapshot_values(
    all_steps: list[dict[str, Any]],
    analysis_text: str = "",
    *,
    finish: bool = False,
    outcome: RunOutcome | None = None,
    public_error: str | None = None,
    llm_service: Any = None,
    failure_code: str | None = None,
    failure_retryable: bool = True,
    execution_mode: Literal["verified", "unverified", "agent"] = "verified",
    assumptions: list[dict[str, Any]] | None = None,
    confirmed_calibers: list[dict[str, Any]] | None = None,
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
        rows = list(result.get("preview_rows") or result.get("data") or [])
        preview = list(result.get("preview_rows") or rows[:3])
        # Prefer labels already projected at row-store write (single source of truth).
        existing_labels = result.get("value_labels")
        step_value_labels: dict[str, dict[str, str]] = (
            {
                str(field): {str(raw): str(label) for raw, label in mapping.items()}
                for field, mapping in existing_labels.items()
                if isinstance(mapping, Mapping)
            }
            if isinstance(existing_labels, Mapping)
            else {}
        )
        if not step_value_labels:
            try:
                from apps.chat.steps.enum_display import apply_wiki_enum_labels

                preview, step_value_labels = apply_wiki_enum_labels(
                    sql=str(step.get("format_statement") or step.get("sql") or ""),
                    fields=[str(f) for f in (result.get("fields") or [])],
                    rows=preview,
                    llm_service=llm_service,
                    tables=[str(t) for t in (step.get("tables") or step.get("resources") or [])],
                )
            except Exception as _enum_exc:  # noqa: BLE001 — translation must not fail the turn
                SQLBotLogUtil.warning("enum translate degraded: %s", _enum_exc)
        row_count = result.get("row_count")
        if row_count is None:
            row_count = len(result.get("data") or preview)
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
                "rows": [],
                "preview_rows": preview,
                "row_count": row_count,
                **({"value_labels": step_value_labels} if step_value_labels else {}),
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
            "code": str(
                failure_code or parsed_error.get("type") or "QUERY_FAILED"
            ).upper(),
            "message": str(parsed_error.get("message") or "Query failed"),
            "retryable": failure_retryable,
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
            "confirmed_calibers": list(confirmed_calibers or []),
            "assumptions": list(assumptions or []),
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
