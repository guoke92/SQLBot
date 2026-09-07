"""Finalize node for the Unified Agent runtime."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date, datetime
from typing import Any, cast

from apps.chat.graphs.nodes.nlq.audit import _record_snapshot_values
from apps.chat.graphs.nodes.nlq.presentation import _table_chart
from apps.chat.graphs.nodes.nlq.state import _llm_service
from apps.chat.presentation import ResultPresentation, build_result_presentation, chart_columns
from apps.conversation.outcome import successful_outcome
from apps.conversation.process_timeline import (
    PREVIEW_ROW_LIMIT,
    load_result_datasets,
    preview_rows,
)
from apps.conversation.run_service import finalize_run
from apps.conversation.session import session_scope
from apps.conversation.sink import StreamSink
from common.utils.utils import SQLBotLogUtil


def _is_numeric(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, int | float):
        return True
    if isinstance(value, str):
        text = value.strip().replace(",", "")
        if not text:
            return False
        try:
            float(text)
            return True
        except ValueError:
            return False
    return False


def _is_temporal(value: Any) -> bool:
    if isinstance(value, datetime | date):
        return True
    if not isinstance(value, str) or len(value) < 8:
        return False
    text = value.strip().replace("Z", "+00:00")
    try:
        datetime.fromisoformat(text[:32])
        return True
    except ValueError:
        return False


def _column_kinds(
    fields: Sequence[str], rows: Sequence[Mapping[str, Any]]
) -> tuple[list[str], list[str], list[str]]:
    temporal: list[str] = []
    numeric: list[str] = []
    categorical: list[str] = []
    sample = list(rows)[:40]
    for field in fields:
        values = [
            row.get(field)
            for row in sample
            if isinstance(row, Mapping) and row.get(field) is not None
        ]
        if not values:
            categorical.append(field)
            continue
        temporal_hits = sum(1 for item in values if _is_temporal(item))
        numeric_hits = sum(1 for item in values if _is_numeric(item))
        n = len(values)
        if temporal_hits >= max(1, n * 0.6):
            temporal.append(field)
        elif numeric_hits >= max(1, n * 0.6):
            numeric.append(field)
        else:
            categorical.append(field)
    return temporal, numeric, categorical


def infer_chart_for_presentation(
    presentation: ResultPresentation,
    fields: list[str],
    rows: list[dict[str, Any]],
    *,
    instance_id: int = 0,
) -> dict[str, Any]:
    """Infer chart type from column value kinds, never from column-name keywords."""
    if not rows or len(fields) < 2:
        tbl = _table_chart(presentation)
        tbl["instance_id"] = instance_id
        return tbl

    cols = chart_columns(presentation)
    col_by_field = {str(col.get("value") or col.get("name")): col for col in cols}
    temporal_fields, numeric_fields, categorical_fields = _column_kinds(fields, rows)

    if temporal_fields and numeric_fields and len(rows) > 1:
        x_col = col_by_field.get(temporal_fields[0]) or cols[0]
        y_col = col_by_field.get(numeric_fields[0]) or cols[-1]
        return {
            "type": "line",
            "title": presentation["title"],
            "columns": cols,
            "xAxis": x_col["value"],
            "yAxis": y_col["value"],
            "axis": {
                "x": {"name": x_col["name"], "value": x_col["value"]},
                "y": {"name": y_col["name"], "value": y_col["value"]},
                "series": {"name": "", "value": ""},
            },
            "config": {
                "xField": x_col["value"],
                "yField": y_col["value"],
                "smooth": True,
            },
            "instance_id": instance_id,
        }

    if numeric_fields and categorical_fields and 1 < len(rows) <= 30:
        x_col = col_by_field.get(categorical_fields[0]) or cols[0]
        y_col = col_by_field.get(numeric_fields[0]) or cols[-1]
        return {
            "type": "bar",
            "title": presentation["title"],
            "columns": cols,
            "xAxis": x_col["value"],
            "yAxis": y_col["value"],
            "axis": {
                "x": {"name": x_col["name"], "value": x_col["value"]},
                "y": {"name": y_col["name"], "value": y_col["value"]},
                "series": {"name": "", "value": ""},
            },
            "config": {
                "xField": x_col["value"],
                "yField": y_col["value"],
            },
            "instance_id": instance_id,
        }

    tbl = _table_chart(presentation)
    tbl["instance_id"] = instance_id
    return tbl


def _assumptions_from_slots(memory_slots: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Surface confirmed calibers as human-readable assumptions for the answer UI."""
    items: list[dict[str, Any]] = []
    confirmed = memory_slots.get("confirmed_calibers")
    if isinstance(confirmed, Mapping):
        for _key, value in confirmed.items():
            if isinstance(value, Mapping):
                question = str(value.get("question") or "").strip()
                label = str(value.get("label") or "").strip()
                meaning = str(value.get("meaning") or label).strip()
                text = meaning or label
                if not text and not question:
                    continue
                items.append(
                    {
                        "question": question,
                        "label": label or text,
                        "meaning": meaning or text,
                        "value": meaning or text,
                        "source": "clarification",
                    }
                )
            elif value not in (None, ""):
                text = str(value).strip()
                if text:
                    items.append(
                        {
                            "question": "",
                            "label": text,
                            "meaning": text,
                            "value": text,
                            "source": "clarification",
                        }
                    )
    declared = memory_slots.get("assumptions")
    if isinstance(declared, list):
        for item in declared:
            if not isinstance(item, Mapping) or not item:
                continue
            payload = dict(item)
            meaning = str(
                payload.get("meaning")
                or payload.get("label")
                or payload.get("value")
                or ""
            ).strip()
            question = str(payload.get("question") or "").strip()
            if not meaning and not question:
                continue
            payload["question"] = question
            payload["meaning"] = meaning
            payload["label"] = str(payload.get("label") or meaning).strip()
            payload["value"] = meaning
            payload.setdefault("source", "declared")
            items.append(payload)
    return items


def finalize_agent_turn_node(state: Mapping[str, Any]) -> dict[str, Any]:
    """Assemble final TurnAnswerV1 from result_dataset rows and emit finish once."""
    try:
        llm_service = _llm_service(state)
    except Exception:
        llm_service = None
    sink = StreamSink.from_state(state)
    final_text = str(state.get("final_text") or "")
    run_id = str(state.get("run_id") or "")
    record_id = state.get("record_id")
    schema_txt = str(getattr(getattr(llm_service, "chat_question", None), "db_schema", "") or "")

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
    for index, dataset in enumerate(datasets):
        ds_id = str(dataset.dataset_id)
        if ds_id in seen:
            continue
        seen.add(ds_id)
        fields = list(dataset.fields or [])
        rows = [dict(item) for item in (dataset.rows or []) if isinstance(item, Mapping)]
        sql = str((dataset.schema_snapshot or {}).get("sql") or "")
        pres = build_result_presentation(fields, title="", schema_text=schema_txt)
        chart = infer_chart_for_presentation(
            cast(ResultPresentation, pres), fields, rows, instance_id=index
        )
        samples = preview_rows(rows, limit=PREVIEW_ROW_LIMIT)
        value_labels = (dataset.schema_snapshot or {}).get("value_labels") or {}
        snapshot_limit = (dataset.schema_snapshot or {}).get("limit")
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
            pres = build_result_presentation(fields, title="", schema_text=schema_txt)
            chart = infer_chart_for_presentation(
                cast(ResultPresentation, pres), fields, samples, instance_id=idx
            )
            truncated = bool(data.get("truncated"))
            value_labels = data.get("value_labels") if isinstance(data.get("value_labels"), Mapping) else {}
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

    raw_slots = dict(state.get("memory_slots") or {})
    assumptions = _assumptions_from_slots(raw_slots)
    outcome = successful_outcome()
    snapshot_vals = _record_snapshot_values(
        all_steps,
        analysis_text=final_text,
        finish=True,
        outcome=outcome,
        llm_service=llm_service,
        execution_mode="agent",
        assumptions=assumptions,
    )
    answer = snapshot_vals.get("answer") or {}

    if latest_sql:
        raw_slots["active_baseline_sql"] = latest_sql
        raw_slots["active_dataset_outline"] = {
            "fields": latest_fields,
            "row_count": latest_row_count,
        }

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
        SQLBotLogUtil.warning(f"Stream output skipped outside of runnable context: {stream_exc}")

    return {
        **state,
        "terminal_answer": answer,
        "memory_slots": raw_slots,
        "outcome": outcome,
    }
