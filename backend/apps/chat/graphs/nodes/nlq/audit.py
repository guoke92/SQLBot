"""Snapshot/audit projection helpers: snapshot values, row permissions, capture enqueue."""

from __future__ import annotations

from copy import deepcopy
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
from apps.knowledge.compile.bundle import ApplyHit
from apps.protocol import QueryPlan
from apps.protocol.base import CAP_ROW_PERMISSION

# ── Constants ────────────────────────────────────────────────────────────────
from common.utils.utils import SQLBotLogUtil


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


def _sql_alias_columns(sql: str, dialect: str) -> list[dict[str, str]]:
    """SELECT 投影的 别名→物理列 回解（sqlglot，与 identifier_validation 同依赖）。

    只取 ``col AS alias`` / 裸列投影：``alias`` = 结果列名（用户看到的），
    ``column`` = 物理列名，``table`` 限定符经表别名归一（多表同列消歧）。
    表达式/聚合投影无单一物理列，跳过。解析失败返回空——调用方走列集
    匹配兜底。"""
    projections: list[dict[str, str]] = []
    try:
        import sqlglot
        from sqlglot import exp

        for statement in sqlglot.parse(sql, dialect=dialect):
            if statement is None:
                continue
            for select in statement.find_all(exp.Select):
                for proj in select.expressions:
                    inner = proj.this
                    if not isinstance(inner, exp.Column):
                        continue
                    projections.append(
                        {
                            "alias": str(proj.alias_or_name or inner.name),
                            "column": str(inner.name),
                            "table": str(inner.table or ""),
                        }
                    )
    except Exception:  # noqa: BLE001 — 解析失败走兜底
        return []
    return projections


def _enum_refs_for_step(
    step: dict[str, Any],
    result_fields: list[str] | None = None,
    *,
    dialect: str = "mysql",
) -> tuple[list[str], dict[str, str]]:
    """从 plan 的表引用+结果列提取 表.列 物理键（枚举翻译的输入）。

    返回 ``(refs, alias_to_ref)``：``refs`` = 命中枚举映射候选的 ``表.列``
    物理键；``alias_to_ref`` = SQL 别名回解出的精确对应（结果列名 →
    ``表.列``）——translate 层据此精确重挂，不再按字典序猜（chat 171：
    双枚举列场景插入序兜底会把 录入方式 错挂到 认证状态 的映射）。

    主路径 = SQL 别名回解：结果列常是中文别名（``identify_style AS 认证方式``），
    先用 sqlglot 把投影列回解成物理列（表限定符消歧），再与 wiki 列集求交。
    解析失败/无别名列时走列集匹配兜底（refs 语义不变，alias_to_ref 为空）——
    列集从 wiki 表页 ground:table 取（与 enum_maps_for 同源单一真相）。"""
    refs: list[str] = []
    alias_to_ref: dict[str, str] = {}
    tables = [str(t) for t in (step.get("tables") or step.get("resources") or [])]
    fields = [str(f) for f in (result_fields or [])]
    if not fields:
        return refs, alias_to_ref
    sql = str(step.get("format_statement") or step.get("sql") or "")
    projections = _sql_alias_columns(sql, dialect) if sql else []
    alias_map = {p["alias"]: p for p in projections}

    table_columns: dict[str, set[str]] = {}
    for table in tables:
        table_columns[table] = _wiki_table_columns(table)
    known = {col for cols in table_columns.values() for col in cols}

    resolved: list[tuple[str, str, str]] = []  # (结果列名, 物理列名, 表限定)
    seen: set[str] = set()
    for f in fields:
        proj = alias_map.get(f)
        if proj is not None and proj["column"] not in seen:
            seen.add(proj["column"])
            resolved.append((f, proj["column"], proj["table"]))
    if resolved:
        for result_field, column, table_qualifier in resolved:
            candidates = (
                [table_qualifier]
                if table_qualifier and table_qualifier in table_columns
                else [t for t, cols in table_columns.items() if column in cols]
                or list(table_columns)
            )
            for t in candidates:
                if not known or column in (table_columns.get(t) or set()):
                    ref = f"{t}.{column}"
                    if ref not in refs:
                        refs.append(ref)
                    # 别名 = 结果列名本身（无 AS 时 alias_or_name 回落列名）
                    alias_to_ref.setdefault(result_field, ref)
                    break
        return refs, alias_to_ref

    # 兜底：结果列名即物理列名（无别名/解析失败）——refs 旧路径行为不变
    for t in tables:
        cols = table_columns.get(t) or set()
        for f in fields:
            if known and f not in cols:
                continue
            ref = f"{t}.{f}"
            if ref not in refs:
                refs.append(ref)
    return refs, alias_to_ref


def _wiki_table_columns(table: str) -> set[str]:
    """wiki 表页 ground:table 的列名集合（store 不可用/页缺失返回空集）。"""
    try:
        from apps.chat.steps.wiki_recall import _store

        store = _store()
        if store is None:
            return set()
        page = store.pages.get(table)
        if page is None:
            return set()
        for anchor in getattr(page, "ground_blocks", ()) or ():
            if anchor.kind != "table":
                continue
            return {
                str(f.get("name") or "")
                for f in anchor.data.get("fields") or []
                if isinstance(f, dict) and f.get("name")
            }
        return set()
    except Exception:  # noqa: BLE001 — 列集缺失不影响翻译主路径
        return set()


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
        rows = list(result.get("data") or [])
        # 枚举值→描述翻译（P3）：查询引用字段 ∩ 权威枚举页承载字段。
        # 纯函数双调（datasets 组装与 replay 同源），失败=原样展示。
        # 翻译作用于用户看到的结果列（可能是中文别名）；value_labels 的
        # 键同步用结果列名，前端悬停与表格列一致。
        step_value_labels: dict[str, dict[str, str]] = {}
        try:
            _dialect = (
                getattr(getattr(llm_service, "protocol", None), "type_key", None)
                if llm_service is not None
                else None
            ) or "mysql"
            _enum_refs, _alias_to_ref = _enum_refs_for_step(
                step,
                [str(f) for f in (result.get("fields") or [])],
                dialect=str(_dialect),
            )
            if _enum_refs and rows:
                from apps.chat.steps.wiki_recall import (
                    enum_maps_for,
                    translate_enum_cells,
                )

                _ds_id_enum = (
                    getattr(getattr(llm_service, "ds", None), "id", None)
                    if llm_service is not None
                    else None
                )
                _maps = enum_maps_for(_enum_refs, ds_id=_ds_id_enum)
                if _maps:
                    rows, step_value_labels = translate_enum_cells(
                        list(result.get("fields") or []),
                        rows,
                        _maps,
                        alias_to_ref=_alias_to_ref,
                    )
        except Exception as _enum_exc:  # noqa: BLE001 — 翻译失败零影响
            SQLBotLogUtil.warning("enum translate degraded: %s", _enum_exc)
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
                "rows": rows,
                "row_count": len(result.get("data") or []),
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
