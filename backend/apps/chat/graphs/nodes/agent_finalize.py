"""Finalize node for the Unified Agent runtime."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

from apps.chat.agent_copy import (
    compact_agent_final_text,
    truncated_display_note,
    truncation_from_delivery_steps,
)
from apps.chat.agent_knowledge import AgentKnowledgePlane
from apps.chat.caliber_surface import project_caliber_surface
from apps.chat.chart_presentation import (
    infer_chart_for_presentation,
    resolve_delivery_chart,
)
from apps.chat.delivery import select_delivery_datasets
from apps.chat.graphs.nodes.nlq.audit import _record_snapshot_values
from apps.chat.graphs.nodes.nlq.presentation import _maybe_update_chat_brief
from apps.chat.graphs.nodes.nlq.state import _llm_service
from apps.chat.presentation import (
    ResultPresentation,
    build_result_presentation,
)
from apps.conversation.outcome import (
    degraded_outcome,
    failed_outcome,
    successful_outcome,
)
from apps.conversation.process_timeline import (
    PREVIEW_ROW_LIMIT,
    load_result_datasets,
    preview_rows,
)
from apps.conversation.run_service import finalize_run
from apps.conversation.session import session_scope
from apps.conversation.sink import StreamSink
from common.utils.utils import SQLBotLogUtil

# Re-export for tests / callers that historically imported from here.
__all__ = [
    "finalize_agent_turn_node",
    "has_publishable_query_result",
    "infer_chart_for_presentation",
    "select_delivery_datasets",
    "try_publish_query_salvage",
]


def _safe_delivery_chart(**kwargs: Any) -> dict[str, Any] | None:
    try:
        return resolve_delivery_chart(**kwargs)
    except Exception as exc:
        SQLBotLogUtil.warning(f"delivery chart inference skipped: {exc}")
        return None


def has_publishable_query_result(state: Mapping[str, Any]) -> bool:
    """True when this turn already has a required successful SQL dataset.

    Prefers in-memory tool_steps / current-turn messages; falls back to
    ``result_dataset`` rows for ``run_id`` (never prior-turn transcript).
    """
    from apps.chat.graphs.nodes.unified_agent import _agent_has_sql_result
    from apps.conversation.messages import deserialize_messages

    messages = deserialize_messages(list(state.get("messages") or []))
    if _agent_has_sql_result(state, messages):
        return True
    run_id = str(state.get("run_id") or "")
    if not run_id:
        return False
    try:
        with session_scope() as session:
            rows = load_result_datasets(session, run_id)
        return bool(select_delivery_datasets(rows))
    except Exception:
        return False


def try_publish_query_salvage(
    run_id: str, state: Mapping[str, Any] | None = None
) -> bool:
    """Publish persisted SQL results as a degraded turn. True when datasets land."""
    payload: dict[str, Any] = {
        **dict(state or {}),
        "run_id": run_id,
        "analysis_incomplete": True,
        "error": None,
        "public_error": None,
    }
    if not isinstance(payload.get("turn_route"), Mapping):
        payload["turn_route"] = {"task_kind": "query"}
    try:
        out = finalize_agent_turn_node(payload)
    except Exception as exc:
        SQLBotLogUtil.warning(f"query salvage publish failed: {exc}")
        return False
    answer = out.get("terminal_answer") or {}
    datasets = answer.get("datasets") if isinstance(answer, Mapping) else None
    return not out.get("error") and bool(datasets)


def _assumptions_from_slots(memory_slots: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Deprecated combined projection — prefer project_caliber_surface."""
    surface = project_caliber_surface(memory_slots)
    return [*surface["confirmed_calibers"], *surface["assumptions"]]


def finalize_agent_turn_node(state: Mapping[str, Any]) -> dict[str, Any]:
    """Assemble final TurnAnswerV1 from result_dataset rows and emit finish once."""
    analysis_incomplete = bool(state.get("analysis_incomplete"))
    try:
        llm_service = _llm_service(state)
    except Exception:
        llm_service = None
    sink = StreamSink.from_state(state)
    final_text = str(state.get("final_text") or "")
    run_id = str(state.get("run_id") or "")
    schema_txt = str(
        getattr(getattr(llm_service, "chat_question", None), "db_schema", "") or ""
    )

    all_steps: list[dict[str, Any]] = []
    latest_sql = ""
    latest_fields: list[str] = []
    latest_row_count = 0

    datasets = []
    if run_id:
        try:
            with session_scope() as session:
                datasets = load_result_datasets(session, run_id)
        except Exception as exc:
            SQLBotLogUtil.warning(f"load result_dataset failed: {exc}")

    seen: set[str] = set()
    for index, dataset in enumerate(select_delivery_datasets(datasets)):
        ds_id = str(dataset.dataset_id)
        if ds_id in seen:
            continue
        seen.add(ds_id)
        fields = list(dataset.fields or [])
        rows = [
            dict(item) for item in (dataset.rows or []) if isinstance(item, Mapping)
        ]
        snapshot = dict(dataset.schema_snapshot or {})
        sql = str(snapshot.get("sql") or "")
        result_title = str(snapshot.get("result_title") or "").strip()
        suggested = str(snapshot.get("chart_type") or "").strip()
        pres = build_result_presentation(
            fields, title=result_title, schema_text=schema_txt
        )
        chart = _safe_delivery_chart(
            presentation=cast(ResultPresentation, pres),
            fields=fields,
            rows=rows,
            suggested_type=suggested,
            sql=sql,
            llm_service=llm_service,
            instance_id=index,
        )
        samples = preview_rows(rows, limit=PREVIEW_ROW_LIMIT)
        value_labels = snapshot.get("value_labels") or {}
        snapshot_limit = snapshot.get("limit")
        result_payload = {
            "fields": fields,
            "data": samples,
            "row_count": int(dataset.row_count or len(rows)),
            "truncated": bool(dataset.truncated),
            "preview_rows": samples,
            **({"value_labels": value_labels} if value_labels else {}),
        }
        # Only surface limit when the result is a capped display window.
        if dataset.truncated:
            result_payload["limit"] = (
                int(snapshot_limit)
                if snapshot_limit is not None
                else int(dataset.row_count or len(rows))
            )
        all_steps.append(
            {
                "index": index,
                "dataset_id": ds_id,
                "status": dataset.status or "succeeded",
                "required": getattr(dataset, "required", True) is not False,
                "brief": result_title,
                "sql": sql,
                "format_statement": sql,
                "fields": fields,
                "data": result_payload,
                "result": result_payload,
                "presentation": pres,
                "chart": chart,
            }
        )
        latest_sql = sql or latest_sql
        latest_fields = fields or latest_fields
        latest_row_count = int(dataset.row_count or len(rows))

    if not all_steps:
        for step in state.get("tool_steps") or []:
            if not isinstance(step, Mapping) or not step.get("ok"):
                continue
            data = (step.get("result") or {}).get("data") or {}
            if not isinstance(data, Mapping) or not data.get("sql"):
                continue
            if data.get("required") is False:
                continue
            sql = str(data.get("sql") or "")
            if sql in seen:
                continue
            seen.add(sql)
            fields = list(data.get("fields") or [])
            samples = preview_rows(
                data.get("preview_rows") or data.get("sample_rows") or [],
                limit=PREVIEW_ROW_LIMIT,
            )
            idx = len(all_steps)
            result_title = str(data.get("result_title") or "").strip()
            suggested = str(data.get("chart_type") or "").strip()
            pres = build_result_presentation(
                fields, title=result_title, schema_text=schema_txt
            )
            chart = _safe_delivery_chart(
                presentation=cast(ResultPresentation, pres),
                fields=fields,
                rows=[dict(r) for r in samples if isinstance(r, Mapping)],
                suggested_type=suggested,
                sql=sql,
                llm_service=llm_service,
                instance_id=idx,
            )
            truncated = bool(data.get("truncated"))
            value_labels = (
                data.get("value_labels")
                if isinstance(data.get("value_labels"), Mapping)
                else {}
            )
            result_payload = {
                "fields": fields,
                "data": samples,
                "row_count": data.get("row_count") or data.get("total_rows"),
                "truncated": truncated,
                "preview_rows": samples,
                **({"value_labels": value_labels} if value_labels else {}),
            }
            if truncated and data.get("limit") is not None:
                result_payload["limit"] = data.get("limit")
            all_steps.append(
                {
                    "index": idx,
                    "dataset_id": str(data.get("dataset_id") or f"dataset_{idx + 1}"),
                    "status": "succeeded",
                    "required": data.get("required") is not False,
                    "brief": result_title,
                    "sql": sql,
                    "format_statement": sql,
                    "fields": fields,
                    "data": result_payload,
                    "result": result_payload,
                    "presentation": pres,
                    "chart": chart,
                }
            )
            latest_sql = sql
            latest_fields = fields
            latest_row_count = int(data.get("row_count") or data.get("total_rows") or 0)

    route = (
        state.get("turn_route") if isinstance(state.get("turn_route"), Mapping) else {}
    )
    from apps.chat.tools.complete_answer import terminal_text_from_steps

    text_exit = terminal_text_from_steps(state.get("tool_steps"))
    if all_steps:
        text_exit = ""
    elif text_exit:
        final_text = text_exit
    elif str(route.get("task_kind") or "query") == "query":
        from apps.chat.graphs.nodes.unified_agent import _incomplete_query_message

        text = _incomplete_query_message(state)
        failed = {
            **state,
            "error": text,
            "public_error": text,
            "final_text": text,
            "outcome": failed_outcome(text, kind="empty_response"),
        }
        try:
            from apps.chat.session_transcript import persist_turn_from_state

            failed["agent_transcript_saved"] = persist_turn_from_state(failed)
        except Exception as exc:
            SQLBotLogUtil.warning(f"agent_transcript append skipped: {exc}")
        return failed

    truncated, trunc_limit = truncation_from_delivery_steps(all_steps)
    trans = getattr(llm_service, "trans", None) if llm_service is not None else None
    final_text = compact_agent_final_text(
        final_text,
        truncated=truncated,
        limit=trunc_limit,
        truncation_note=truncated_display_note(trunc_limit, trans=trans),
    )

    raw_slots = dict(state.get("memory_slots") or {})
    surface = project_caliber_surface(raw_slots)
    if analysis_incomplete:
        outcome = degraded_outcome(
            "Summary analysis was incomplete; query results were kept.",
            successful_steps=max(len(all_steps), 1),
            total_steps=max(len(all_steps), 1),
        )
    else:
        outcome = successful_outcome()
    if text_exit and not all_steps:
        from apps.chat.result_quality import build_text_answer_quality

        outcome["quality"] = build_text_answer_quality()
    plane = AgentKnowledgePlane.from_dump(state.get("knowledge_plane"))
    dialect = getattr(getattr(llm_service, "ds", None), "type", None)
    if not (plane.tables or plane.page_keys):
        knowledge_refs = None
    elif latest_sql:
        knowledge_refs = plane.knowledge_refs(
            sql=latest_sql,
            dialect=str(dialect) if dialect else None,
        )
    else:
        knowledge_refs = {"page_keys": [], "tables": []}
    snapshot_vals = _record_snapshot_values(
        all_steps,
        analysis_text=final_text,
        finish=True,
        outcome=outcome,
        llm_service=llm_service,
        execution_mode="agent",
        confirmed_calibers=surface["confirmed_calibers"],
        assumptions=surface["assumptions"],
        knowledge_refs=knowledge_refs,
    )
    answer = snapshot_vals.get("answer") or {}

    if latest_sql:
        raw_slots["active_baseline_sql"] = latest_sql
        raw_slots["active_dataset_outline"] = {
            "fields": latest_fields,
            "row_count": latest_row_count,
        }

    if llm_service is not None:
        title = next(
            (
                str(step.get("brief") or "").strip()
                for step in all_steps
                if str(step.get("brief") or "").strip()
            ),
            "",
        )
        if not title:
            title = str(
                getattr(getattr(llm_service, "chat_question", None), "question", "")
                or ""
            )
        try:
            _maybe_update_chat_brief(llm_service, sink, title)
        except Exception as exc:
            SQLBotLogUtil.warning(f"chat brief update skipped: {exc}")

    try:
        with session_scope() as session:
            finalize_run(
                session,
                run_id=run_id,
                status="degraded" if analysis_incomplete else "succeeded",
                current_node="finalize_turn",
                record_snapshot=snapshot_vals,
            )
            session.commit()
    except Exception as exc:
        SQLBotLogUtil.error(f"Error finalizing agent run: {exc}")

    saved = False
    try:
        from apps.chat.session_transcript import persist_turn_from_state

        saved = persist_turn_from_state(state)
    except Exception as exc:
        SQLBotLogUtil.warning(f"agent_transcript append skipped: {exc}")

    try:
        if sink.mode == "markdown" and final_text:
            sink.text(final_text + "\n\n")
        elif sink.mode == "json":
            sink.json_result({"success": True, "content": final_text, "answer": answer})
    except Exception as stream_exc:
        SQLBotLogUtil.warning(
            f"Stream output skipped outside of runnable context: {stream_exc}"
        )

    return {
        **state,
        "error": None,
        "public_error": None,
        "terminal_answer": answer,
        "memory_slots": raw_slots,
        "outcome": outcome,
        "analysis_incomplete": analysis_incomplete,
        "agent_transcript_saved": saved,
    }
