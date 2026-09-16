"""ConversationPack: one chat_id dump for identical read-only restore."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlmodel import Session, select

from apps.chat.curd.chat import (
    _hydrate_turn_answer_rows,
    _latest_reasoning_by_record,
    _run_duration_breakdown,
    _token_usage_by_record,
    format_record,
)
from apps.chat.models.chat_model import Chat, ChatRecord, ChatRecordResult
from apps.conversation.models import (
    ConversationInterrupt,
    ConversationRun,
    ResultDataset,
)
from apps.conversation.process_timeline import (
    load_result_datasets,
    project_process_timeline,
)
from apps.conversation.run_service import serialize_interrupt
from apps.datasource.models.datasource import CoreDatasource
from apps.dev.jsonutil import jsonable
from apps.knowledge.db_models import WikiCorpus
from apps.knowledge.wiki.binding_service import list_bindings
from apps.system.models.system_model import WorkspaceModel
from apps.system.models.user import UserModel

EXPORT_VERSION = 2


def _iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.isoformat()


def _user_brief(session: Session, user_id: int | None) -> dict[str, Any] | None:
    if not user_id:
        return None
    user = session.get(UserModel, int(user_id))
    if user is None:
        return {"id": int(user_id), "account": None, "name": None}
    return {"id": int(user.id), "account": user.account, "name": user.name}


def _datasource_database(ds: CoreDatasource | None) -> str | None:
    if ds is None:
        return None
    try:
        from apps.protocol import get_protocol_for_ds

        name = get_protocol_for_ds(ds).schema_namespace(ds)
        cleaned = str(name or "").strip()
        return cleaned or None
    except Exception:  # noqa: BLE001
        return None


def _datasource_meta(session: Session, ds_id: int | None) -> dict[str, Any] | None:
    if not ds_id:
        return None
    ds = session.get(CoreDatasource, int(ds_id))
    if ds is None:
        return {"id": int(ds_id), "exists": False}
    return {
        "id": int(ds.id),
        "exists": True,
        "name": ds.name,
        "type": ds.type,
        "type_name": ds.type_name,
        "status": ds.status,
        "oid": ds.oid,
        "database": _datasource_database(ds),
    }


def _wiki_bindings(
    session: Session, *, oid: int | None, datasource_id: int | None
) -> list[dict[str, Any]]:
    if not datasource_id:
        return []
    oid_value = int(oid or 1)
    views = list_bindings(session, oid_value, datasource_id=int(datasource_id))
    rows: list[dict[str, Any]] = []
    for view in views:
        corpus = session.get(WikiCorpus, view.corpus_id)
        rows.append(
            {
                "corpus_id": view.corpus_id,
                "corpus_key": view.corpus_key,
                "enabled": view.enabled,
                "remap_databases": view.remap_databases,
                "generation": int(getattr(corpus, "generation", 0) or 0)
                if corpus is not None
                else None,
                "page_count": int(getattr(corpus, "page_count", 0) or 0)
                if corpus is not None
                else None,
                "published_count": int(getattr(corpus, "published_count", 0) or 0)
                if corpus is not None
                else None,
                "status": getattr(corpus, "status", None)
                if corpus is not None
                else None,
            }
        )
    return rows


def _serialize_dataset(item: ResultDataset) -> dict[str, Any]:
    return {
        "result_id": item.result_id,
        "run_id": item.run_id,
        "dataset_id": item.dataset_id,
        "plan_id": item.plan_id,
        "status": item.status,
        "required": bool(item.required),
        "fields": list(item.fields or []),
        "rows": list(item.rows or []),
        "row_count": item.row_count
        if item.row_count is not None
        else len(item.rows or []),
        "truncated": bool(item.truncated),
        "schema_snapshot": item.schema_snapshot or {},
        "statistics": item.statistics or {},
        "error": item.error,
        "create_time": _iso(item.create_time),
    }


def _timeline(
    session: Session, record_id: int, run_id: str | None, trans: Any = None
) -> dict[str, Any]:
    compact = project_process_timeline(
        session, record_id=record_id, run_id=run_id, view="compact", trans=trans
    )
    detail = project_process_timeline(
        session, record_id=record_id, run_id=run_id, view="detail", trans=trans
    )
    return {"compact": jsonable(compact), "detail": jsonable(detail)}


def hydrate_answer_with_full_rows(
    session: Session, record: ChatRecord
) -> dict[str, Any] | None:
    """Inline complete result_dataset.rows into ChatRecord.answer."""
    answer = _hydrate_turn_answer_rows(session, record)
    if isinstance(answer, dict) and answer:
        return jsonable(answer)
    return None


def pack_to_view(pack: dict[str, Any]) -> dict[str, Any]:
    chat = pack.get("chat") or {}
    datasource = pack.get("datasource") or {}
    records = []
    for item in pack.get("records") or []:
        view = item.get("view")
        if isinstance(view, dict):
            records.append(view)
    return {
        "id": chat.get("id"),
        "create_time": chat.get("create_time"),
        "create_by": chat.get("create_by"),
        "brief": chat.get("brief") or "",
        "chat_type": chat.get("chat_type") or "chat",
        "datasource": chat.get("datasource"),
        "engine_type": chat.get("engine_type") or "",
        "ds_type": datasource.get("type") or "",
        "datasource_name": datasource.get("name") or "",
        "datasource_exists": bool(datasource.get("exists", True)),
        "recommended_question": chat.get("recommended_question"),
        "recommended_generate": chat.get("recommended_generate"),
        "records": records,
        "operator": chat.get("operator"),
        "workspace_name": chat.get("workspace_name"),
        "wiki": pack.get("wiki") or [],
        "datasource_meta": datasource,
    }


def snapshot_index_fields(pack: dict[str, Any]) -> dict[str, Any]:
    chat = pack.get("chat") or {}
    operator = chat.get("operator") or {}
    up = down = 0
    has_error = False
    for item in pack.get("records") or []:
        view = item.get("view") or {}
        if view.get("feedback") == "up":
            up += 1
        elif view.get("feedback") == "down":
            down += 1
        if view.get("error"):
            has_error = True
    return {
        "source_oid": chat.get("oid"),
        "source_chat_id": int(chat.get("id") or pack.get("chat_id") or 0),
        "operator_id": operator.get("id"),
        "operator_account": operator.get("account"),
        "operator_name": operator.get("name"),
        "brief": chat.get("brief"),
        "feedback_up": up,
        "feedback_down": down,
        "has_error": has_error,
    }


def build_conversation_pack(
    session: Session,
    chat_id: int,
    *,
    trans: Any = None,
) -> dict[str, Any]:
    chat = session.get(Chat, chat_id)
    if chat is None:
        raise LookupError(f"Chat with id {chat_id} not found")

    records = list(
        session.exec(
            select(ChatRecord)
            .where(ChatRecord.chat_id == chat_id)
            .order_by(ChatRecord.create_time, ChatRecord.id)
        ).all()
    )
    record_ids = [int(row.id) for row in records if row.id is not None]
    token_usage_map = _token_usage_by_record(session, record_ids)
    reasoning_map = _latest_reasoning_by_record(session, record_ids)

    run_rows = (
        list(
            session.exec(
                select(ConversationRun)
                .where(ConversationRun.chat_record_id.in_(record_ids))
                .order_by(ConversationRun.chat_record_id, ConversationRun.attempt_index)
            ).all()
        )
        if record_ids
        else []
    )
    runs_by_record: dict[int, list[ConversationRun]] = {}
    for run in run_rows:
        runs_by_record.setdefault(int(run.chat_record_id), []).append(run)

    run_ids = [run.run_id for run in run_rows]
    interrupts = (
        list(
            session.exec(
                select(ConversationInterrupt).where(
                    ConversationInterrupt.run_id.in_(run_ids)
                )
            ).all()
        )
        if run_ids
        else []
    )
    interrupts_by_run: dict[str, list[ConversationInterrupt]] = {}
    for item in interrupts:
        interrupts_by_run.setdefault(item.run_id, []).append(item)
    for items in interrupts_by_run.values():
        items.sort(key=lambda row: row.version)

    packed_records: list[dict[str, Any]] = []
    for record in records:
        rid = int(record.id or 0)
        record_runs = runs_by_record.get(rid, [])
        run = next(
            (item for item in record_runs if item.run_id == record.active_run_id),
            record_runs[-1] if record_runs else None,
        )
        run_interrupts = interrupts_by_run.get(run.run_id, []) if run else []
        _elapsed, _waiting, duration = _run_duration_breakdown(
            run,
            run_interrupts,
            fallback_start=record.create_time,
            fallback_end=record.finish_time,
        )
        active_interrupt = (
            next(
                (
                    item
                    for item in run_interrupts
                    if item.interrupt_id == run.active_interrupt_id
                ),
                None,
            )
            if run and run.active_interrupt_id
            else None
        )
        hydrated = hydrate_answer_with_full_rows(session, record)
        datasets = (
            [
                _serialize_dataset(item)
                for item in load_result_datasets(session, str(run.run_id))
            ]
            if run
            else []
        )
        reason = reasoning_map.get(rid) or {}
        kwargs: dict[str, Any] = {
            "id": record.id,
            "chat_id": record.chat_id,
            "create_time": record.create_time,
            "finish_time": record.finish_time,
            "duration": duration,
            "total_tokens": token_usage_map.get(rid, 0),
            "question": record.question,
            "turn_kind": getattr(record, "turn_kind", "query"),
            "relation": getattr(record, "relation", "independent"),
            "reference_record_ids": getattr(record, "reference_record_ids", []) or [],
            "answer_revision": int(getattr(record, "answer_revision", 0) or 0),
            "answer": hydrated,
            "sql_answer": record.sql_answer,
            "sql": record.sql,
            "datasource": record.datasource,
            "engine_type": getattr(record, "engine_type", None),
            "re_exec": getattr(record, "re_exec", None),
            "feedback": getattr(record, "feedback", None),
            "feedback_comment": getattr(record, "feedback_comment", None),
            "chart_answer": record.chart_answer,
            "chart": record.chart,
            "analysis": record.analysis,
            "predict": record.predict,
            "data": record.data,
            "predict_data": record.predict_data,
            "datasource_select_answer": record.datasource_select_answer,
            "recommended_question": record.recommended_question,
            "first_chat": record.first_chat,
            "finish": record.finish,
            "error": record.error,
            "sql_reasoning_content": reason.get("sql_reasoning_content"),
            "chart_reasoning_content": reason.get("chart_reasoning_content"),
            "analysis_reasoning_content": reason.get("analysis_reasoning_content"),
            "predict_reasoning_content": reason.get("predict_reasoning_content"),
            "intent_reasoning_content": reason.get("intent_reasoning_content"),
            "run_id": run.run_id if run else None,
            "run_attempt_index": int(run.attempt_index or 0) if run else 0,
            "run_status": run.status if run else None,
            "run_event_cursor": int(run.event_cursor or 0) if run else 0,
            "run_current_node": run.current_node if run else None,
            "run_dispatch_attempts": int(run.dispatch_attempts or 0) if run else 0,
            "run_update_time": run.update_time if run else None,
            "run_started_at": run.started_at if run else None,
            "run_completed_at": run.completed_at if run else None,
            "active_interrupt": (
                serialize_interrupt(active_interrupt) if active_interrupt else None
            ),
            "interrupts": [serialize_interrupt(item) for item in run_interrupts],
        }
        view = jsonable(format_record(ChatRecordResult(**kwargs)))
        packed_records.append(
            {
                "record_id": rid,
                "view": view,
                "timelines": _timeline(
                    session, rid, run.run_id if run else record.active_run_id, trans
                ),
                "result_datasets": jsonable(datasets),
            }
        )

    ds_id = chat.datasource or (records[-1].datasource if records else None)
    workspace = session.get(WorkspaceModel, chat.oid) if chat.oid else None
    pack = {
        "export_version": EXPORT_VERSION,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "chat_id": chat_id,
        "chat": {
            "id": chat.id,
            "oid": chat.oid,
            "workspace_name": workspace.name if workspace is not None else None,
            "create_time": _iso(chat.create_time),
            "create_by": chat.create_by,
            "operator": _user_brief(session, chat.create_by),
            "brief": chat.brief,
            "chat_type": chat.chat_type,
            "datasource": chat.datasource,
            "engine_type": chat.engine_type,
            "origin": chat.origin,
            "brief_generate": chat.brief_generate,
            "recommended_question": chat.recommended_question,
            "recommended_generate": chat.recommended_generate,
        },
        "datasource": _datasource_meta(session, int(ds_id) if ds_id else None),
        "wiki": _wiki_bindings(
            session, oid=chat.oid, datasource_id=int(ds_id) if ds_id else None
        ),
        "records": packed_records,
    }
    return jsonable(pack)
