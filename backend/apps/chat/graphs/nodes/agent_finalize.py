"""Finalize node for the Unified Agent runtime."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

from apps.chat.graphs.nodes.nlq.audit import _record_snapshot_values
from apps.chat.graphs.nodes.nlq.presentation import _table_chart
from apps.chat.graphs.nodes.nlq.state import _llm_service
from apps.chat.models.chat_model import ChatRecord
from apps.chat.presentation import ResultPresentation, build_result_presentation
from apps.conversation.outcome import successful_outcome
from apps.conversation.run_service import finalize_run
from apps.conversation.session import session_scope
from apps.conversation.sink import StreamSink
from common.utils.utils import SQLBotLogUtil


def _extract_agent_stages(state: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Extract lightweight agent stages (thoughts and tool calls) for hydration on reload."""
    stages: list[dict[str, Any]] = []
    messages = list(state.get("messages") or [])

    tool_name_map = {
        "execute_sql_sandbox": "执行查询 (execute_sql_sandbox)",
        "patch_and_compile_sql": "增量补丁 (patch_and_compile_sql)",
        "compare_results": "数据对比 (compare_results)",
        "search_schema": "结构检索 (search_schema)",
        "search_wiki": "查阅知识 (search_wiki)",
        "request_clarification": "请求澄清 (request_clarification)",
    }

    stage_idx = 0
    for m in messages:
        if not isinstance(m, Mapping):
            continue
        m_type = m.get("type")
        content = str(m.get("content") or "")

        if m_type == "ai":
            tool_calls = m.get("tool_calls") or []
            thought = (
                m.get("additional_kwargs", {}).get("reasoning_content")
                or m.get("reasoning_content")
                or (content if tool_calls else "")
            )
            if thought and thought.strip():
                stage_idx += 1
                stages.append({
                    "id": f"thought-{stage_idx}",
                    "type": "thought",
                    "title": "思考",
                    "content": thought.strip(),
                    "status": "completed",
                })
            for c in tool_calls:
                c_name = c.get("name") or "tool"
                args = c.get("args") or {}
                stage_idx += 1
                stages.append({
                    "id": f"tool-{stage_idx}",
                    "type": "tool",
                    "title": tool_name_map.get(c_name, f"工具调用 ({c_name})"),
                    "toolName": c_name,
                    "toolArgs": args,
                    "sql": args.get("sql") if isinstance(args, dict) else None,
                    "status": "completed",
                })

    return stages


def finalize_agent_turn_node(state: Mapping[str, Any]) -> dict[str, Any]:
    """Assemble final TurnAnswerV1, adapt charts, update memory slots, and emit finish."""
    try:
        llm_service = _llm_service(state)
    except Exception:
        llm_service = None
    sink = StreamSink.from_state(state)
    final_text = str(state.get("final_text") or "")
    run_id = str(state.get("run_id") or "")
    record_id = state.get("record_id")

    # 1. Harvest successful query results from tool_steps
    all_steps: list[dict[str, Any]] = []
    latest_sql = ""
    latest_fields: list[str] = []
    latest_rows: list[dict[str, Any]] = []

    for index, step in enumerate(state.get("tool_steps") or []):
        if not isinstance(step, Mapping):
            continue
        name = step.get("name")
        res = step.get("result") or {}
        data = res.get("data") or {}

        if name == "execute_sql_sandbox" and res.get("ok"):
            sql = data.get("sql") or ""
            fields = list(data.get("fields") or [])
            rows = list(data.get("full_rows") or data.get("sample_rows") or [])
            total_rows = int(data.get("total_rows", len(rows)))

            # Auto-infer presentation & AntV chart
            schema_txt = str(getattr(getattr(llm_service, "chat_question", None), "db_schema", "") or "")
            pres = build_result_presentation(
                fields,
                title="查询结果",
                schema_text=schema_txt,
            )
            chart = _table_chart(cast(ResultPresentation, pres))

            step_entry = {
                "dataset_id": f"dataset_{len(all_steps) + 1}",
                "status": "succeeded",
                "brief": f"查询结果 {len(all_steps) + 1}",
                "sql": sql,
                "format_statement": sql,
                "fields": fields,
                "data": {"fields": fields, "data": rows, "row_count": total_rows},
                "result": {"fields": fields, "data": rows, "row_count": total_rows},
                "presentation": pres,
                "chart": chart,
            }
            all_steps.append(step_entry)
            latest_sql = sql
            latest_fields = fields
            latest_rows = rows

        elif name == "compare_results" and res.get("ok"):
            # Multi-dataset for comparison
            base = data.get("base") or {}
            new = data.get("new") or {}
            schema_txt = str(getattr(getattr(llm_service, "chat_question", None), "db_schema", "") or "")
            if base.get("sql"):
                b_fields = list((base.get("sample_rows") or [{}])[0].keys())
                b_rows = list(base.get("sample_rows") or [])
                b_pres = build_result_presentation(b_fields, title="原口径结果", schema_text=schema_txt)
                b_chart = _table_chart(cast(ResultPresentation, b_pres))
                all_steps.append({
                    "dataset_id": "dataset_base",
                    "status": "succeeded",
                    "brief": "原口径结果",
                    "sql": base.get("sql"),
                    "format_statement": base.get("sql"),
                    "fields": b_fields,
                    "data": {"fields": b_fields, "data": b_rows, "row_count": base.get("row_count")},
                    "result": {"fields": b_fields, "data": b_rows, "row_count": base.get("row_count")},
                    "presentation": b_pres,
                    "chart": b_chart,
                })
            if new.get("sql"):
                n_fields = list((new.get("sample_rows") or [{}])[0].keys())
                n_rows = list(new.get("sample_rows") or [])
                n_pres = build_result_presentation(n_fields, title="修正口径结果", schema_text=schema_txt)
                n_chart = _table_chart(cast(ResultPresentation, n_pres))
                all_steps.append({
                    "dataset_id": "dataset_revised",
                    "status": "succeeded",
                    "brief": "修正口径结果",
                    "sql": new.get("sql"),
                    "format_statement": new.get("sql"),
                    "fields": n_fields,
                    "data": {"fields": n_fields, "data": n_rows, "row_count": new.get("row_count")},
                    "result": {"fields": n_fields, "data": n_rows, "row_count": new.get("row_count")},
                    "presentation": n_pres,
                    "chart": n_chart,
                })
            latest_sql = new.get("sql") or base.get("sql")

    outcome = successful_outcome()
    # 2. Build canonical snapshot using standard _record_snapshot_values
    snapshot_vals = _record_snapshot_values(
        all_steps,
        analysis_text=final_text,
        finish=True,
        outcome=outcome,
        llm_service=llm_service,
    )
    answer = snapshot_vals.get("answer") or {}



    # 3. Update memory slots
    raw_slots = state.get("memory_slots") or {}
    if latest_sql:
        raw_slots["active_baseline_sql"] = latest_sql
        raw_slots["active_dataset_outline"] = {
            "fields": latest_fields,
            "row_count": len(latest_rows),
        }

    # 4. Finalize database run & record snapshot
    try:
        with session_scope() as session:
            finalize_run(
                session,
                run_id=run_id,
                status="succeeded",
                current_node=None,
                record_snapshot={
                    **snapshot_vals,
                    "sql_answer": latest_sql,
                    "sql": latest_sql,
                    "analysis": final_text,
                    "finish": True,
                },
            )
            if record_id:
                rec = session.get(ChatRecord, int(record_id))
                if rec:
                    rec.sql = latest_sql
                    rec.sql_answer = latest_sql
                    rec.analysis = final_text
                    rec.finish = True
                    session.add(rec)
            session.commit()
    except Exception as exc:
        SQLBotLogUtil.error(f"Error finalizing agent run: {exc}")

    # 5. Emit analysis text and finish events to client SSE
    try:
        if latest_sql:
            sink.event({"type": "step-sql-result", "sql": latest_sql})
        if final_text:
            sink.event({"type": "analysis", "content": final_text})
            if sink.mode == "markdown":
                sink.text(final_text + "\n\n")
        sink.event({"type": "finish", "id": record_id})
    except Exception as stream_exc:
        SQLBotLogUtil.warning(f"Stream output skipped outside of runnable context: {stream_exc}")

    return {
        **state,
        "terminal_answer": answer,
        "memory_slots": raw_slots,
        "outcome": outcome,
    }
