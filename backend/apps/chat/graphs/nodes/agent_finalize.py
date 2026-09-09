"""Finalize node for the Unified Agent runtime."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, cast

from apps.chat.agent_copy import (
    compact_agent_final_text,
    truncated_display_note,
    truncation_from_delivery_steps,
)
from apps.chat.caliber_surface import project_caliber_surface
from apps.chat.chart_presentation import (
    infer_chart_for_presentation,
    resolve_delivery_chart,
)
from apps.chat.graphs.nodes.nlq.audit import _record_snapshot_values
from apps.chat.graphs.nodes.nlq.presentation import _maybe_update_chat_brief
from apps.chat.graphs.nodes.nlq.state import _llm_service
from apps.chat.presentation import (
    ResultPresentation,
    build_result_presentation,
)
from apps.conversation.outcome import failed_outcome, successful_outcome
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
    "infer_chart_for_presentation",
    "select_delivery_datasets",
]


def _dataset_row_count(item: Any) -> int:
    raw = getattr(item, "row_count", None)
    if raw is not None:
        try:
            return int(raw)
        except (TypeError, ValueError):
            pass
    rows = getattr(item, "rows", None) or []
    try:
        return len(rows)
    except TypeError:
        return 0


def select_delivery_datasets(datasets: Sequence[Any]) -> list[Any]:
    """Publish required successful datasets; drop superseded empty attempts.

    When a later required query returns rows, earlier 0-row attempts in the
    same turn are discarded. If every required attempt is empty, keep the
    last one so the UI can honestly show a 0-row result.
    """
    candidates = [
        item
        for item in datasets
        if str(getattr(item, "status", None) or "succeeded") != "failed"
        and getattr(item, "required", True) is not False
    ]
    if any(_dataset_row_count(item) > 0 for item in candidates):
        return [item for item in candidates if _dataset_row_count(item) > 0]
    return list(candidates[-1:]) if candidates else []


def _assumptions_from_slots(memory_slots: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Deprecated combined projection — prefer project_caliber_surface."""
    surface = project_caliber_surface(memory_slots)
    return [*surface["confirmed_calibers"], *surface["assumptions"]]


def finalize_agent_turn_node(state: Mapping[str, Any]) -> dict[str, Any]:
    """Assemble final TurnAnswerV1 from result_dataset rows and emit finish once."""
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
        chart = resolve_delivery_chart(
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
            chart = resolve_delivery_chart(
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
    if str(route.get("task_kind") or "query") == "query" and not all_steps:
        from apps.chat.graphs.nodes.unified_agent import _incomplete_query_message

        text = _incomplete_query_message(state)
        return {
            **state,
            "error": text,
            "public_error": text,
            "final_text": text,
            "outcome": failed_outcome(text, kind="empty_response"),
        }

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
    outcome = successful_outcome()
    snapshot_vals = _record_snapshot_values(
        all_steps,
        analysis_text=final_text,
        finish=True,
        outcome=outcome,
        llm_service=llm_service,
        execution_mode="agent",
        confirmed_calibers=surface["confirmed_calibers"],
        assumptions=surface["assumptions"],
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
                status="succeeded",
                current_node="finalize_turn",
                record_snapshot=snapshot_vals,
            )
            session.commit()
    except Exception as exc:
        SQLBotLogUtil.error(f"Error finalizing agent run: {exc}")

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
        "terminal_answer": answer,
        "memory_slots": raw_slots,
        "outcome": outcome,
    }
