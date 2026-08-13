"""Build a self-contained debug dump for one chat conversation.

Goal: enough local artifacts to reproduce and locate failures without
re-running the live turn — records, AnswerPayload/outcome, intent/contract,
full chat_log spans, and datasource schema (secrets redacted).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import orjson
from sqlmodel import Session, select

from apps.chat.answer_payload import is_answer_payload, normalize_answer_payload
from apps.chat.models.chat_model import (
    Chat,
    ChatLog,
    ChatLogHistory,
    ChatLogHistoryItem,
    ChatRecord,
    OperationEnum,
)
from apps.chat.steps.observability import parse_audit_envelope, project_audit_message
from apps.conversation.models import (
    ConversationInterrupt,
    ConversationRun,
    ConversationRunEvent,
    NlqEvidenceEvent,
    NlqRun,
)
from apps.datasource.models.datasource import CoreDatasource, CoreField, CoreTable
from apps.knowledge.db_models import KnowledgeCaptureJob, KnowledgeEvidence
from apps.system.models.system_model import AiModelDetail
from common.core.deps import CurrentUser

EXPORT_VERSION = 1

_SECRET_KEYS = {
    "access_token",
    "access_key",
    "api_key",
    "apikey",
    "authorization",
    "bearer_token",
    "basic_password",
    "client_key",
    "client_secret",
    "credential",
    "credentials",
    "password",
    "passwd",
    "pwd",
    "private_key",
    "refresh_token",
    "secret",
    "secret_access_key",
    "secret_key",
    "token",
}


def _json_load_maybe(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, dict | list):
        return value
    if isinstance(value, bytes | bytearray):
        try:
            return orjson.loads(value)
        except Exception:
            return value.decode("utf-8", errors="replace")
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if text[0] in "{[":
            try:
                return orjson.loads(text)
            except Exception:
                return value
        return value
    return value


def _redact_mapping(obj: Any) -> Any:
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for key, value in obj.items():
            if str(key).lower() in _SECRET_KEYS:
                out[key] = "***REDACTED***"
            else:
                out[key] = _redact_mapping(value)
        return out
    if isinstance(obj, list):
        return [_redact_mapping(item) for item in obj]
    return obj


def _truncate_answer_payload(payload: Any, max_rows: int | None) -> Any:
    if max_rows is None or max_rows < 0 or not isinstance(payload, dict):
        return payload
    steps = payload.get("steps")
    if not isinstance(steps, list):
        return payload
    clipped_steps: list[Any] = []
    for step in steps:
        if not isinstance(step, dict):
            clipped_steps.append(step)
            continue
        step_copy = dict(step)
        data = step_copy.get("data")
        if isinstance(data, dict):
            data_copy = dict(data)
            rows = data_copy.get("data")
            if isinstance(rows, list) and len(rows) > max_rows:
                data_copy["data"] = rows[:max_rows]
                data_copy["truncated"] = True
                data_copy["row_count_original"] = len(rows)
                data_copy["row_count_exported"] = max_rows
            step_copy["data"] = data_copy
        clipped_steps.append(step_copy)
    out = dict(payload)
    out["steps"] = clipped_steps
    return out


def _operate_name(operate: Any) -> str | None:
    if operate is None:
        return None
    if isinstance(operate, OperationEnum):
        return operate.name
    if isinstance(operate, str):
        for item in OperationEnum:
            if item.value == operate or item.name == operate:
                return item.name
        return operate
    return str(operate)


def _span_brief(message: Any) -> dict[str, Any]:
    """Use the same normalized contract as ExecutionDetails."""
    envelope = parse_audit_envelope(message)
    if envelope is None:
        return {}
    return {
        key: value
        for key, value in {
            "version": envelope.get("version"),
            "phase": envelope.get("phase"),
            "graph_node": envelope.get("graph_node"),
            "batch_index": envelope.get("batch_index"),
            "attempt_index": envelope.get("attempt_index"),
            "unit_index": envelope.get("unit_index"),
            "outcome": envelope.get("outcome"),
            "summary_key": envelope.get("summary_key"),
            "detail": envelope.get("detail"),
        }.items()
        if value is not None
    }


def _build_timeline(log_history: Any) -> list[dict[str, Any]]:
    steps = getattr(log_history, "steps", None) or []
    timeline: list[dict[str, Any]] = []
    for step in steps:
        if hasattr(step, "model_dump"):
            item = step.model_dump()
        elif isinstance(step, dict):
            item = step
        else:
            continue
        message = item.get("message")
        entry = {
            "id": item.get("id"),
            "operate": item.get("operate"),
            "error": bool(item.get("error")),
            "local_operation": bool(item.get("local_operation")),
            "duration": item.get("duration"),
            "total_tokens": item.get("total_tokens"),
            "start_time": item.get("start_time"),
            "finish_time": item.get("finish_time"),
            "status": item.get("status"),
            "phase": item.get("phase"),
            "graph_node": item.get("graph_node"),
            "summary_key": item.get("summary_key"),
            "detail": item.get("detail") or {},
            "signal": _span_brief(message),
        }
        timeline.append(entry)
    return timeline


def _specification_summary(specification: Any) -> dict[str, Any] | None:
    if not isinstance(specification, dict) or not specification:
        return None
    return {
        "version": specification.get("version"),
        "revision": specification.get("revision"),
        "confidence": specification.get("confidence"),
        "assumption_count": len(specification.get("assumptions") or []),
        "output_count": len(specification.get("outputs") or []),
        "predicate_count": len(specification.get("predicates") or []),
    }


def _outcome_summary(payload: Any) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    outcome = payload.get("outcome")
    if not isinstance(outcome, dict):
        return None
    failures = outcome.get("failures") or []
    quality = outcome.get("quality") if isinstance(outcome.get("quality"), dict) else None
    return {
        "status": outcome.get("status"),
        "successful_steps": outcome.get("successful_steps"),
        "total_steps": outcome.get("total_steps"),
        "failure_count": len(failures) if isinstance(failures, list) else 0,
        "failures": failures if isinstance(failures, list) else [],
        "quality_score": (quality or {}).get("score"),
        "quality_grade": (quality or {}).get("grade"),
    }


def _datasource_bundle(session: Session, ds_id: int | None) -> dict[str, Any] | None:
    if not ds_id:
        return None
    ds = session.get(CoreDatasource, ds_id)
    if not ds:
        return {"id": ds_id, "exists": False}

    configuration: Any = None
    try:
        from apps.datasource.utils.utils import aes_decrypt

        raw = aes_decrypt(ds.configuration) if ds.configuration else None
        configuration = _redact_mapping(_json_load_maybe(raw))
    except Exception as exc:
        configuration = {"_error": f"decrypt_failed: {exc}"}

    tables = session.exec(
        select(CoreTable).where(CoreTable.ds_id == ds.id).order_by(CoreTable.id)
    ).all()
    table_rows: list[dict[str, Any]] = []
    fields_by_table: dict[str, list[dict[str, Any]]] = {}
    for table in tables:
        table_rows.append(
            {
                "id": table.id,
                "table_name": table.table_name,
                "table_comment": table.table_comment,
                "custom_comment": table.custom_comment,
                "checked": table.checked,
                "approx_rows": table.approx_rows,
                "data_bytes": table.data_bytes,
                "index_summary": table.index_summary,
            }
        )
        fields = session.exec(
            select(CoreField)
            .where(CoreField.table_id == table.id)
            .order_by(CoreField.field_index, CoreField.id)
        ).all()
        fields_by_table[str(table.table_name)] = [
            {
                "id": field.id,
                "field_name": field.field_name,
                "field_type": field.field_type,
                "field_comment": field.field_comment,
                "custom_comment": field.custom_comment,
                "checked": field.checked,
                "field_index": field.field_index,
            }
            for field in fields
        ]

    return {
        "id": ds.id,
        "exists": True,
        "name": ds.name,
        "description": ds.description,
        "type": ds.type,
        "type_name": ds.type_name,
        "status": ds.status,
        "oid": ds.oid,
        "configuration": configuration,
        "table_relation": ds.table_relation,
        "tables": table_rows,
        "fields_by_table": fields_by_table,
    }


def _model_bundle(session: Session, model_ids: set[int]) -> list[dict[str, Any]]:
    models: list[dict[str, Any]] = []
    for model_id in sorted(model_ids):
        detail = session.get(AiModelDetail, model_id)
        if not detail:
            models.append({"id": model_id, "exists": False})
            continue
        models.append(
            {
                "id": detail.id,
                "exists": True,
                "name": detail.name,
                "supplier": detail.supplier,
                "model_type": detail.model_type,
                "base_model": detail.base_model,
                "protocol": detail.protocol,
                "status": detail.status,
                "default_model": detail.default_model,
                "api_domain_set": bool(detail.api_domain),
                # Never export api_key / api_domain ciphertext.
            }
        )
    return models


def _token_count(token_usage: Any) -> int:
    if isinstance(token_usage, dict):
        value = token_usage.get("total_tokens")
        if isinstance(value, int | float):
            return int(value)
    if isinstance(token_usage, int | float):
        return int(token_usage)
    return 0


def _raw_logs_for_record(session: Session, record_id: int) -> list[dict[str, Any]]:
    """All chat_log rows for a record, including filtered operates."""
    logs = session.exec(
        select(ChatLog)
        .where(ChatLog.pid == record_id)
        .order_by(ChatLog.start_time, ChatLog.id)
    ).all()
    rows: list[dict[str, Any]] = []
    for log in logs:
        rows.append(
            {
                "id": log.id,
                "type": getattr(log.type, "name", str(log.type)) if log.type else None,
                "operate": _operate_name(log.operate),
                "operate_value": getattr(log.operate, "value", log.operate),
                "ai_modal_id": log.ai_modal_id,
                "base_modal": log.base_modal,
                "messages": log.messages,
                "reasoning_content": log.reasoning_content,
                "token_usage": log.token_usage,
                "local_operation": log.local_operation,
                "error": log.error,
                "start_time": log.start_time,
                "finish_time": log.finish_time,
            }
        )
    return rows


def _log_history_from_raw(
    record: ChatRecord,
    raw_logs: list[dict[str, Any]],
    run: ConversationRun | None = None,
) -> ChatLogHistory:
    steps: list[ChatLogHistoryItem] = []
    total_tokens = 0
    for row in raw_logs:
        if row.get("operate") == OperationEnum.GENERATE_RECOMMENDED_QUESTIONS.name:
            continue
        log_tokens = _token_count(row.get("token_usage"))
        total_tokens += log_tokens
        duration = None
        if row.get("start_time") and row.get("finish_time"):
            try:
                duration = round(
                    (row["finish_time"] - row["start_time"]).total_seconds(), 2
                )
            except Exception:
                duration = None
        projection = project_audit_message(
            row.get("messages"),
            finish_time=row.get("finish_time"),
            error=bool(row.get("error")),
            run_terminal=bool(
                run
                and run.status in {"succeeded", "degraded", "failed", "cancelled"}
            ),
        )
        steps.append(
            ChatLogHistoryItem(
                id=row.get("id"),
                start_time=row.get("start_time"),
                finish_time=row.get("finish_time"),
                duration=duration,
                total_tokens=log_tokens,
                operate=row.get("operate"),
                local_operation=bool(row.get("local_operation")),
                error=bool(row.get("error")),
                status=projection["status"],
                phase=projection["phase"],
                graph_node=projection["graph_node"],
                title_key=projection["title_key"],
                title_params=projection["title_params"],
                summary_key=projection["summary_key"],
                summary_params=projection["summary_params"],
                batch_index=projection["batch_index"],
                attempt_index=projection["attempt_index"],
                unit_index=projection["unit_index"],
                detail=projection["detail"],
                input=projection["input"],
                output=projection["output"],
                reasoning_content=row.get("reasoning_content"),
                message=projection["message"],
            )
        )
    total_duration = None
    if record.create_time and record.finish_time:
        try:
            total_duration = round(
                (record.finish_time - record.create_time).total_seconds(), 2
            )
        except Exception:
            total_duration = None
    return ChatLogHistory(
        start_time=record.create_time,
        finish_time=record.finish_time,
        duration=total_duration,
        total_tokens=total_tokens,
        steps=steps,
    )


def build_chat_debug_bundle(
    session: Session,
    current_user: CurrentUser,
    chat_id: int,
    *,
    max_rows: int | None = 50,
    include_raw_logs: bool = True,
) -> dict[str, Any]:
    chat = session.get(Chat, chat_id)
    if not chat:
        raise ValueError(f"Chat with id {chat_id} not found")

    is_admin = bool(getattr(current_user, "isAdmin", False))
    if not is_admin and chat.create_by != current_user.id:
        raise PermissionError(f"Chat with id {chat_id} not owned by the current user")

    records = session.exec(
        select(ChatRecord)
        .where(ChatRecord.chat_id == chat_id)
        .order_by(ChatRecord.create_time, ChatRecord.id)
    ).all()

    # Owner check for non-admin: records should belong to same user.
    if not is_admin:
        for record in records:
            if record.create_by != current_user.id:
                raise PermissionError(
                    f"ChatRecord {record.id} not owned by the current user"
                )

    model_ids: set[int] = set()
    record_bundles: list[dict[str, Any]] = []
    analysis_failures: list[dict[str, Any]] = []
    clarification_links: list[dict[str, Any]] = []
    high_signal: list[dict[str, Any]] = []
    record_ids = [int(record.id) for record in records if record.id is not None]
    runs = (
        session.exec(
            select(ConversationRun).where(
                ConversationRun.chat_record_id.in_(record_ids)
            )
        ).all()
        if record_ids
        else []
    )
    runs_by_record = {int(run.chat_record_id): run for run in runs}

    for record in records:
        if record.ai_modal_id:
            model_ids.add(int(record.ai_modal_id))

        payload_raw = _json_load_maybe(record.data)
        payload: Any = payload_raw
        if isinstance(payload_raw, dict) and is_answer_payload(payload_raw):
            try:
                payload = normalize_answer_payload(payload_raw)
            except Exception:
                payload = payload_raw
        payload = _truncate_answer_payload(payload, max_rows)

        run = runs_by_record.get(int(record.id))
        nlq_run = session.get(NlqRun, run.run_id) if run and run.graph_key == "chat" else None
        specification = (
            nlq_run.specifications[-1]
            if nlq_run and nlq_run.specifications
            else None
        )
        outcome = _outcome_summary(payload)
        intent = _specification_summary(specification)
        run_events = (
            [
                item.model_dump(mode="json")
                for item in session.exec(
                    select(ConversationRunEvent)
                    .where(ConversationRunEvent.run_id == run.run_id)
                    .order_by(ConversationRunEvent.cursor)
                ).all()
            ]
            if run
            else []
        )
        interrupts = (
            [
                item.model_dump(mode="json")
                for item in session.exec(
                    select(ConversationInterrupt)
                    .where(ConversationInterrupt.run_id == run.run_id)
                    .order_by(ConversationInterrupt.version)
                ).all()
            ]
            if run
            else []
        )
        capture_job = session.exec(
            select(KnowledgeCaptureJob).where(
                KnowledgeCaptureJob.record_id == int(record.id)
            )
        ).first()
        knowledge_evidence = [
            item.model_dump(mode="json")
            for item in session.exec(
                select(KnowledgeEvidence)
                .where(KnowledgeEvidence.record_id == int(record.id))
                .order_by(KnowledgeEvidence.create_time, KnowledgeEvidence.id)
            ).all()
        ]

        raw_logs = _raw_logs_for_record(session, int(record.id))
        log_history = _log_history_from_raw(record, raw_logs, run)
        timeline = _build_timeline(log_history)
        for entry in timeline:
            if entry.get("error") or entry.get("operate") in {
                "CLARIFY_INTENT",
                "GENERATE_QUERY",
                "EXECUTE_QUERY",
                "DECIDE_NEXT",
                "GROUND_ENTITIES",
            }:
                high_signal.append({"record_id": record.id, **entry})
        for row in raw_logs:
            if row.get("ai_modal_id"):
                try:
                    model_ids.add(int(row["ai_modal_id"]))
                except Exception:
                    pass
        if not include_raw_logs:
            raw_logs = []

        if record.error or (outcome and outcome.get("status") in {"failed", "degraded", "blocked"}):
            analysis_failures.append(
                {
                    "record_id": record.id,
                    "question": (record.question or "")[:200],
                    "error": record.error,
                    "outcome": outcome,
                    "finish": record.finish,
                }
            )

        if run and run.active_interrupt_id:
            active_interrupt = session.get(
                ConversationInterrupt, run.active_interrupt_id
            )
            clarification_links.append(
                {
                    "record_id": record.id,
                    "run_id": run.run_id,
                    "interrupt_id": run.active_interrupt_id,
                    "version": active_interrupt.version if active_interrupt else None,
                    "question": (record.question or "")[:200],
                }
            )

        duration = None
        if record.create_time and record.finish_time:
            try:
                duration = round(
                    (record.finish_time - record.create_time).total_seconds(), 2
                )
            except Exception:
                duration = None

        record_bundles.append(
            {
                "record_id": record.id,
                "chat_id": record.chat_id,
                "create_time": record.create_time,
                "finish_time": record.finish_time,
                "duration": duration,
                "finish": record.finish,
                "first_chat": record.first_chat,
                "question": record.question,
                "error": record.error,
                "sql": record.sql,
                "sql_answer": record.sql_answer,
                "chart": _json_load_maybe(record.chart),
                "chart_answer": record.chart_answer,
                "analysis": _json_load_maybe(record.analysis),
                "predict": _json_load_maybe(record.predict),
                "predict_data": _json_load_maybe(record.predict_data),
                "recommended_question": record.recommended_question,
                "datasource": record.datasource,
                "engine_type": record.engine_type,
                "ai_modal_id": record.ai_modal_id,
                "re_exec": _json_load_maybe(record.re_exec),
                "run": run.model_dump(mode="json") if run else None,
                "run_events": run_events,
                "interrupts": interrupts,
                "query_specification": specification,
                "specification_summary": intent,
                "planning_context": (
                    {
                        "version": (nlq_run.planning_context or {}).get("version"),
                        "resources": (nlq_run.planning_context or {}).get(
                            "resources", []
                        ),
                        "fingerprint": (nlq_run.planning_context or {}).get(
                            "fingerprint"
                        ),
                        "usable": bool(
                            str(
                                (nlq_run.planning_context or {}).get(
                                    "schema_text", ""
                                )
                            ).strip()
                        ),
                    }
                    if nlq_run
                    else None
                ),
                "evidence": (
                    [
                        item.model_dump(mode="json")
                        for item in session.exec(
                            select(NlqEvidenceEvent)
                            .where(NlqEvidenceEvent.run_id == run.run_id)
                            .order_by(NlqEvidenceEvent.sequence)
                        ).all()
                    ]
                    if run and run.graph_key == "chat"
                    else []
                ),
                "plans": nlq_run.plans if nlq_run else [],
                "executed_plan_ids": nlq_run.executed_plan_ids if nlq_run else [],
                "knowledge_capture_job": (
                    capture_job.model_dump(mode="json") if capture_job else None
                ),
                "knowledge_evidence": knowledge_evidence,
                "analysis_record_id": record.analysis_record_id,
                "predict_record_id": record.predict_record_id,
                "regenerate_record_id": record.regenerate_record_id,
                "answer_payload": payload,
                "outcome": outcome,
                "log": log_history.model_dump() if hasattr(log_history, "model_dump") else log_history,
                "timeline": timeline,
                "raw_logs": raw_logs,
            }
        )

    ds_id = chat.datasource or (records[-1].datasource if records else None)
    datasource = _datasource_bundle(session, int(ds_id) if ds_id else None)
    models = _model_bundle(session, model_ids)

    chat_dump = {
        "id": chat.id,
        "oid": chat.oid,
        "create_time": chat.create_time,
        "create_by": chat.create_by,
        "brief": chat.brief,
        "chat_type": chat.chat_type,
        "datasource": chat.datasource,
        "engine_type": chat.engine_type,
        "origin": chat.origin,
        "brief_generate": chat.brief_generate,
        "recommended_question": chat.recommended_question,
        "recommended_generate": chat.recommended_generate,
    }

    diagnostics: list[dict[str, Any]] = []
    now = datetime.now()
    for item in record_bundles:
        run_data = item.get("run") or {}
        record_id = item.get("record_id")
        run_status = run_data.get("status")
        updated = run_data.get("update_time")
        if isinstance(updated, str):
            try:
                updated = datetime.fromisoformat(updated)
            except ValueError:
                updated = None
        if run_status == "queued" and isinstance(updated, datetime):
            if (now - updated).total_seconds() > 15:
                diagnostics.append({"record_id": record_id, "code": "stale_queued"})
        if run_status == "running" and not run_data.get("checkpoint_id"):
            diagnostics.append(
                {"record_id": record_id, "code": "running_without_checkpoint"}
            )
        if run_data and not item.get("run_events"):
            diagnostics.append({"record_id": record_id, "code": "no_run_events"})
        if any(
            not step.get("finish_time") and not step.get("error")
            for step in item.get("raw_logs") or []
        ):
            diagnostics.append(
                {"record_id": record_id, "code": "unfinished_chat_log"}
            )
        if run_status in {"succeeded", "degraded", "failed", "cancelled"}:
            if not item.get("finish"):
                diagnostics.append(
                    {"record_id": record_id, "code": "terminal_record_mismatch"}
                )
        capture = item.get("knowledge_capture_job") or {}
        if capture.get("status") in {"pending", "failed"}:
            diagnostics.append(
                {
                    "record_id": record_id,
                    "code": f"capture_{capture.get('status')}",
                    "attempt": capture.get("attempt"),
                    "error": capture.get("error"),
                }
            )

    return {
        "export_version": EXPORT_VERSION,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "chat_id": chat_id,
        "viewer": {
            "user_id": current_user.id,
            "is_admin": is_admin,
            "oid": getattr(current_user, "oid", None),
        },
        "chat": chat_dump,
        "datasource": datasource,
        "ai_models": models,
        "records": record_bundles,
        "analysis": {
            "record_count": len(record_bundles),
            "failed_or_degraded": analysis_failures,
            "clarification_links": clarification_links,
            "high_signal_steps": high_signal,
            "diagnostics": diagnostics,
            "notes": [
                "answer_payload.outcome is the terminal run status/quality.",
                "conversation_run owns lifecycle; nlq_run owns specification revisions.",
                "nlq_evidence_event is the immutable user/system evidence ledger.",
                "timeline.signal extracts span meta from chat_log messages.",
                "raw_logs includes all operates (incl. recommended questions).",
                "datasource.configuration secrets are redacted.",
            ],
        },
        "options": {
            "max_rows": max_rows,
            "include_raw_logs": include_raw_logs,
        },
    }
