"""Presentation nodes: charts, summary, complete, fail."""

from __future__ import annotations

import traceback
from typing import Any, Literal, cast

import orjson
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from apps.chat.curd.chat import rename_chat
from apps.chat.graphs.nodes.nlq.audit import (
    _enqueue_knowledge_capture,
    _record_snapshot_values,
)
from apps.chat.graphs.nodes.nlq.planning import (
    _persist_query_terminal_failure,
)
from apps.chat.graphs.nodes.nlq.quality import (
    _assess_all_steps,
    _fallback_analysis,
    _merge_batch_into_steps,
)

# ── Constants ────────────────────────────────────────────────────────────────
from apps.chat.graphs.nodes.nlq.state import (
    CandidateBatch,
    NlqState,
    _ds_scope,  # noqa: F401
    _fail,
    _finish_step_value,
    _generation_question,
    _llm_service,
)
from apps.chat.models.chat_model import (
    ChatFinishStep,
    OperationEnum,
    RenameChat,
)

# monkeypatch-surface imports: tests setattr these names on submodules
from apps.chat.planning_context import capture_planning_context  # noqa: F401
from apps.chat.presentation import (
    ResultPresentation,
    build_result_presentation,
    chart_columns,
)
from apps.chat.result_data import format_json_data
from apps.chat.steps.chart import generate_chart
from apps.chat.steps.observability import log_span
from apps.chat.steps.persist import parse_chart
from apps.chat.task.llm import request_picture
from apps.conversation.messages import message_content_text
from apps.conversation.outcome import (
    ResultQuality,
    RunOutcome,
    failed_outcome,
    format_error_message,
    outcome_from_steps,
    outcome_is_success,
    public_error_message,
    successful_outcome,
)
from apps.conversation.run_service import (
    finalize_run,
    require_active_run,  # noqa: F401
)
from apps.conversation.runtime_context import attach_runtime  # noqa: F401
from apps.conversation.session import session_scope
from apps.conversation.sink import StreamSink
from apps.conversation.usage import usage_from_response
from common.error import SingleMessageError
from common.utils.data_format import DataFormat
from common.utils.json_utils import extract_nested_json
from common.utils.utils import SQLBotLogUtil


def _table_chart(presentation: ResultPresentation) -> dict[str, Any]:
    return {
        "type": "table",
        "title": presentation["title"],
        "columns": chart_columns(presentation),
    }


def generate_charts_node(state: NlqState) -> NlqState:
    """Generate presentation only for a structurally accepted candidate."""
    llm_service = _llm_service(state)
    sink = StreamSink.from_state(state)
    accepted_candidate = dict(state.get("accepted_candidate") or {})
    batch_results = accepted_candidate.get("results") or []
    base = 0
    prompt_schema = str(getattr(llm_service.chat_question, "db_schema", "") or "")

    try:
        charts: list[dict[str, Any]] = []
        presentations: list[ResultPresentation] = []
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
                presentation: ResultPresentation = {
                    "title": "Error",
                    "columns": [],
                }
                chart = _table_chart(presentation)
                presentations.append(presentation)
                charts.append(chart)
                continue

            plan_dict = entry.get("plan") or {}
            result = entry.get("result") or {}
            chart_type = (plan_dict.get("chart_type") or "table") or "table"
            fields = result.get("fields") or []
            data = result.get("data") or []
            brief = plan_dict.get("brief") or ""
            presentation_title = plan_dict.get("presentation_title") or brief
            presentation = build_result_presentation(
                fields,
                title=presentation_title,
                projection_requirements=plan_dict.get("projection_requirements") or {},
                schema_text=prompt_schema,
            )
            presentations.append(presentation)

            if chart_type == "table":
                with log_span(
                    operate=OperationEnum.GENERATE_CHART,
                    record_id=llm_service.record.id,
                    local_operation=True,
                    graph_node="generate_charts",
                    title_key="chat.log.GENERATE_CHART",
                    step_index=state.get("step_index", 0),
                    unit_index=gidx,
                    brief="table",
                ) as span:
                    chart = _table_chart(presentation)
                    span.set_detail(
                        {
                            "chart_type": "table",
                            "column_count": len(presentation.get("columns") or []),
                        }
                    )
                    span.set_summary("chat.audit.table_ready")
                charts.append(chart)
                continue

            try:
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
                        llm_service.retrieval_question,
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
                        sink.token(
                            content=chunk.get("content") or "",
                            reasoning_content=chunk.get("reasoning_content") or "",
                            event_type="step-chart-result",
                            metadata={"index": gidx},
                        )
                    chart = parse_chart(
                        res=full_chart_text,
                        fields=fields,
                    )
                    chart["title"] = presentation["title"]
                    chart["columns"] = chart_columns(presentation)
            except Exception as chart_exc:
                SQLBotLogUtil.warning(
                    f"Chart generation fallback to table at step {gidx}: {chart_exc}"
                )
                chart = _table_chart(presentation)
                with log_span(
                    operate=OperationEnum.GENERATE_CHART,
                    record_id=llm_service.record.id,
                    local_operation=True,
                    graph_node="generate_charts",
                    title_key="chat.log.GENERATE_CHART",
                    step_index=state.get("step_index", 0),
                    unit_index=gidx,
                    brief="table fallback",
                ) as fallback_span:
                    fallback_span.set_detail(
                        {
                            "chart_type": "table",
                            "source": "chart_fallback",
                            "column_count": len(presentation.get("columns") or []),
                        }
                    )
                    fallback_span.set_summary("chat.audit.table_ready")
                    fallback_span.mark_degraded(str(chart_exc))
            charts.append(chart)

        # Restore base chart messages after batch
        llm_service.chart_message = list(base_chart_messages)

        published_plans = [
            {
                **plan,
                "presentation": presentations[index],
            }
            for index, plan in enumerate(accepted_candidate.get("plans") or [])
            if index < len(presentations)
        ]
        steps = _merge_batch_into_steps(
            [],
            published_plans,
            list(batch_results),
            charts,
            entity_bindings=state.get("entity_bindings"),
        )
        return {
            **state,
            "accepted_candidate": {
                **accepted_candidate,
                "plans": published_plans,
                "charts": charts,
                "steps": steps,
                "outcome": accepted_candidate.get("outcome")
                or outcome_from_steps(steps),
            },
            "active_candidate": {},
        }
    except Exception as e:
        return _fail(state, llm_service.record.id, e)


_SUMMARY_PROMPT = """\
根据已执行结果写一段简要分析，直接回答用户问题。

{steps_summary}

用户原问题：{question}

要求：
- 只用 3～6 句；不要 SQL、不要 JSON、不要分节标题。
- 若限制中写明“仅展示前 N 行”或“没有全量合计”，必须先说明这是展示窗口，禁止把窗口内合计写成累计、总额或全量。
- 引用关键数字；结果被截断时，若提供了全量合计必须引用全量合计，并说明表格只是展示窗口；没有全量合计时明确说当前数字不能当作全量。
- 没有证据不要推断业务原因。
- 使用会话语言：{target_language}。
"""


def _brief_result_facts(assessments: list[dict[str, Any]]) -> str:
    """Compact facts for the user-facing summary — not a second SQL dump."""
    if not assessments:
        return "（尚无已执行查询）"
    lines: list[str] = []
    for item in assessments:
        index = int(item.get("index") or 0) + 1
        rows = int(item.get("row_count") or 0)
        truncated = bool(item.get("truncated"))
        limit = item.get("limit") or rows
        truncated_note = f"，仅展示前 {limit} 行" if truncated else ""
        fields = ", ".join(str(name) for name in (item.get("fields") or [])[:12])
        lines.append(f"查询{index}: {rows} 行{truncated_note}")
        if fields:
            lines.append(f"字段: {fields}")
        coverage_totals = item.get("coverage_totals")
        has_full_totals = isinstance(coverage_totals, dict) and bool(coverage_totals)
        metrics = item.get("metrics") or {}
        if isinstance(metrics, dict) and metrics and not truncated:
            parts = []
            for name, stats in list(metrics.items())[:6]:
                if not isinstance(stats, dict):
                    continue
                if stats.get("count"):
                    parts.append(f"{name} sum={stats.get('sum')}")
            if parts:
                lines.append("指标: " + "; ".join(parts))
        if has_full_totals:
            bits = [f"{name}={value}" for name, value in coverage_totals.items()]
            lines.append("全量合计: " + "; ".join(bits[:8]))
        elif truncated:
            lines.append(
                f"限制: 仅展示前 {limit} 行，没有全量合计；窗口内数字不能写成累计或全量"
            )
        limitations = item.get("limitations") or []
        lines.extend(f"限制: {note}" for note in limitations[:3])
    return "\n".join(lines)


def _summary_messages(
    steps_summary: str,
    question: str,
    quality: dict[str, Any],
    *,
    target_language: str,
) -> list[Any]:
    del quality  # Quality stays on the stamp; do not ask the model to rewrite it.
    return [
        SystemMessage(
            content=(
                "你负责用几句话解释已执行查询结果。"
                "不要生成或修改 SQL，不要返回 JSON。"
                f"所有面向用户的内容必须使用当前会话语言：{target_language}。"
            )
        ),
        HumanMessage(
            _SUMMARY_PROMPT.format(
                steps_summary=steps_summary,
                question=question,
                target_language=target_language,
            )
        ),
    ]


def _extract_summary_text(response_text: str) -> str:
    """Accept plain Markdown and tolerate providers that still wrap it in JSON."""
    text = (response_text or "").strip()
    if not text:
        return ""
    if text.startswith("{") or text.lower().startswith("```json"):
        json_str = extract_nested_json(text)
        try:
            data = orjson.loads(json_str) if json_str else None
            if isinstance(data, dict):
                return str(data.get("text") or "").strip()
        except Exception:
            return ""
    return text


def summarize_answer_node(state: NlqState) -> NlqState:
    """Summarize an already accepted candidate; never gate its publication."""
    llm_service = _llm_service(state)
    candidate = dict(state.get("accepted_candidate") or {})
    steps = list(candidate.get("steps") or [])
    if not steps:
        return _fail(
            state,
            getattr(llm_service.record, "id", None),
            SingleMessageError("No accepted result to summarize"),
        )
    assessments = _assess_all_steps(steps)
    candidate_quality = candidate.get("quality")
    if not isinstance(candidate_quality, dict):
        return _fail(
            state,
            getattr(llm_service.record, "id", None),
            SingleMessageError("Accepted candidate is missing its quality report"),
        )
    quality = cast(ResultQuality, candidate_quality)
    question = _generation_question(llm_service)
    record_id = getattr(llm_service.record, "id", None) or state.get("record_id")
    meta: dict[str, Any] = {"used_llm": False}
    with log_span(
        operate=OperationEnum.ANALYSIS,
        record_id=record_id,
        ai_modal_id=getattr(llm_service.chat_question, "ai_modal_id", None),
        ai_modal_name=getattr(llm_service.chat_question, "ai_modal_name", None),
        local_operation=False,
        graph_node="summarize_answer",
        title_key="chat.log.SUMMARIZE",
        brief="结果总结",
        step_index=state.get("step_index"),
    ) as span:
        try:
            target_language = str(
                getattr(llm_service.chat_question, "lang", "") or "简体中文"
            )
            summary_messages = _summary_messages(
                _brief_result_facts(assessments),
                question,
                quality,
                target_language=target_language,
            )
            response: AIMessage = llm_service.llm.bind(
                temperature=0, max_tokens=600
            ).invoke(summary_messages)
            meta["used_llm"] = True
            meta["token_usage"] = usage_from_response(response)
            analysis_text = _extract_summary_text(
                message_content_text(response.content)
            )
            if not analysis_text:
                analysis_text = _fallback_analysis(
                    assessments,
                    reason="总结模型未返回可用正文",
                    target_language=target_language,
                )
            span["token_usage"] = meta["token_usage"]
            span.set_model_context([*summary_messages, response])
            span["payload"] = {
                "fallback": not bool(
                    _extract_summary_text(message_content_text(response.content))
                ),
                "chars": len(analysis_text),
            }
            span.set_summary("chat.audit.response_ready")
        except Exception as exc:
            SQLBotLogUtil.error(f"summarize_answer_node error: {exc}")
            analysis_text = _fallback_analysis(
                assessments,
                reason=f"总结模型调用异常：{exc}",
                target_language=str(
                    getattr(llm_service.chat_question, "lang", "") or "简体中文"
                ),
            )
            span.mark_degraded(str(exc))
            span["payload"] = {"fallback": True, "chars": len(analysis_text)}
            span.set_summary("chat.audit.response_ready")
    return {
        **state,
        "analysis_text": analysis_text,
        "accepted_candidate": {
            **candidate,
            "steps": steps,
            "quality": quality,
        },
        "active_candidate": {},
    }


def complete_node(state: NlqState) -> NlqState:
    """Commit the terminal snapshot, then publish the same answer to clients."""
    llm_service = _llm_service(state)
    sink = StreamSink.from_state(state)
    json_result: dict[str, Any] = dict(state.get("json_result") or {})
    analysis_text = state.get("analysis_text") or ""
    return_img = bool(state.get("return_img", True))

    terminal_answer = state.get("terminal_answer") or {}
    if terminal_answer:
        # Analysis/prediction turns skip plan_query: name the conversation from
        # the user question when no query plan has done it yet.
        _maybe_update_chat_brief(
            llm_service,
            sink,
            str(llm_service.record.question or llm_service.chat_question.question),
        )
        terminal_status: Literal["succeeded", "degraded"] = (
            "degraded"
            if (state.get("outcome") or {}).get("status") == "degraded"
            else "succeeded"
        )
        with session_scope() as session:
            finalize_run(
                session,
                run_id=str(state["run_id"]),
                status=terminal_status,
                current_node=None,
                result_quality=terminal_answer.get("quality"),
                record_snapshot={
                    "answer": terminal_answer,
                    "analysis": orjson.dumps(
                        {"content": terminal_answer.get("content") or ""}
                    ).decode(),
                    "terminal": True,
                },
            )
        content = str(terminal_answer.get("content") or "")
        if content:
            sink.event({"type": terminal_answer.get("kind"), "content": content})
            if sink.mode == "markdown":
                sink.text(content + "\n\n")
        sink.event({"type": "finish"})
        if sink.mode == "json":
            sink.json_result(
                {
                    "success": True,
                    "status": terminal_status,
                    "answer": terminal_answer,
                }
            )
        return {**state, "outcome": state.get("outcome") or successful_outcome()}

    # Query-only stops before execution and publishes the already validated plan.
    # Every executed result, including QUERY_DATA, must arrive here through the
    # same decide_next gate and therefore lives in accepted_candidate.
    if _finish_step_value(state) <= int(ChatFinishStep.GENERATE_QUERY.value):
        source_candidate = dict(state.get("active_candidate") or {})
        updated_steps = _merge_batch_into_steps(
            [],
            list(source_candidate.get("plans") or []),
            list(source_candidate.get("results") or []),
            list(source_candidate.get("charts") or []),
            entity_bindings=state.get("entity_bindings"),
        )
    else:
        source_candidate = dict(state.get("accepted_candidate") or {})
        updated_steps = list(source_candidate.get("steps") or [])
    # Name the conversation once: first plan's brief for query turns,
    # user question for analysis/prediction (terminal_answer branch above).
    _maybe_update_chat_brief(
        llm_service,
        sink,
        str(
            (source_candidate.get("plans") or [{}])[0].get("brief")
            or llm_service.chat_question.question
            or ""
        ),
    )
    # Ensure every successful step has one canonical presentation and a chart
    # adapter (MCP QUERY_DATA / table fallback).
    for step in updated_steps:
        if step.get("error"):
            continue
        fields = (step.get("result") or {}).get("fields") or []
        presentation = step.get("presentation")
        if not isinstance(presentation, dict):
            presentation = build_result_presentation(
                fields,
                title=step.get("presentation_title") or step.get("brief") or "",
                projection_requirements=step.get("projection_requirements") or {},
                schema_text=str(
                    getattr(llm_service.chat_question, "db_schema", "") or ""
                ),
            )
            step["presentation"] = presentation
        if step.get("chart"):
            continue
        step["chart"] = _table_chart(
            cast(ResultPresentation, presentation),
        )

    outcome = outcome_from_steps(
        updated_steps,
        planned_count=len(source_candidate.get("plans") or []),
    )
    state_outcome = state.get("outcome")
    if (
        not updated_steps
        and state_outcome
        and state_outcome.get("status") in {"failed", "limit_reached"}
    ):
        # The rejected candidate is intentionally absent from answer data, but
        # its authoritative terminal failure must still reach persistence/API.
        outcome = cast(RunOutcome, dict(state_outcome))
    elif state_outcome and state_outcome.get("status") in {"success", "degraded"}:
        outcome["status"] = state_outcome["status"]
    quality = (state_outcome or {}).get("quality") or source_candidate.get("quality")
    if isinstance(quality, dict):
        outcome["quality"] = cast(ResultQuality, quality)
    json_result["success"] = outcome_is_success(outcome)
    json_result["status"] = outcome["status"]
    if "quality" in outcome:
        json_result["quality"] = outcome["quality"]
    if outcome["failures"]:
        json_result["failures"] = outcome["failures"]

    failure_message = next(
        (
            str(item.get("message"))
            for item in outcome.get("failures") or []
            if item.get("message")
        ),
        "Conversation completed without a usable result",
    )
    run_status: Literal["succeeded", "degraded", "failed"] = (
        "failed"
        if not outcome_is_success(outcome)
        else "degraded"
        if outcome["status"] == "degraded"
        else "succeeded"
    )
    try:
        with session_scope() as session:
            finalize_run(
                session,
                run_id=str(state["run_id"]),
                status=run_status,
                current_node=None,
                result_quality=outcome.get("quality"),
                record_snapshot=_record_snapshot_values(
                    updated_steps,
                    analysis_text,
                    finish=True,
                    outcome=outcome,
                    llm_service=llm_service,
                    execution_mode=cast(
                        Literal["verified", "unverified"],
                        state.get("execution_mode") or "verified",
                    ),
                ),
                error_summary=failure_message if run_status == "failed" else None,
            )
    except Exception as exc:
        traceback.print_exc()
        return fail_node(
            cast(
                NlqState,
                {
                    **state,
                    "accepted_candidate": {
                        **source_candidate,
                        "steps": updated_steps,
                    },
                    "error": format_error_message(exc),
                    "outcome": failed_outcome(exc),
                },
            )
        )

    # Async knowledge capture — never fails the published answer.
    if outcome_is_success(outcome):
        try:
            _enqueue_knowledge_capture(state, llm_service, outcome, updated_steps)
        except Exception as _cap_exc:  # noqa: BLE001
            SQLBotLogUtil.warning(f"knowledge capture enqueue failed: {_cap_exc}")

    # The persisted snapshot is the source of truth. Publish analysis only
    # after that commit so live SSE and a subsequent page refresh cannot
    # observe different terminal answers.
    if analysis_text:
        sink.event({"type": "analysis", "content": analysis_text})
        if sink.mode == "markdown":
            sink.text(analysis_text + "\n\n")

    if not outcome_is_success(outcome):
        sink.error(failure_message)
        return {
            **state,
            "accepted_candidate": {
                **source_candidate,
                "steps": updated_steps,
            },
            "json_result": json_result,
            "error": failure_message,
            "outcome": outcome,
        }

    # Optional last-chart image (MCP markdown / json)
    if return_img and updated_steps:
        last_step = updated_steps[-1]
        chart = last_step.get("chart") or {}
        result = last_step.get("result") or {}
        if chart.get("type") and chart.get("type") != "table" and result:
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
                    sink.text(f"![{chart.get('type')}]({image_url})")
            except Exception:
                if sink.mode == "markdown":
                    sink.text("generate or fetch chart picture error.\n\n")

    sink.event({"type": "finish"})
    if sink.mode == "json":
        sink.json_result(json_result)

    completed_candidate: CandidateBatch = {
        **source_candidate,
        "steps": updated_steps,
        "outcome": outcome,
    }
    if "quality" in outcome:
        completed_candidate["quality"] = outcome["quality"]
    return {
        **state,
        "json_result": json_result,
        "accepted_candidate": completed_candidate,
        "outcome": outcome,
    }


def fail_node(state: NlqState) -> NlqState:
    """Persist the canonical empty NLQ answer before emitting terminal failure."""
    try:
        from apps.chat.graphs.nodes.agent_finalize import (
            finalize_agent_turn_node,
            has_publishable_query_result,
        )

        if has_publishable_query_result(state):
            salvaged = finalize_agent_turn_node(
                {
                    **state,
                    "error": None,
                    "public_error": None,
                    "analysis_incomplete": True,
                }
            )
            if not salvaged.get("error"):
                return salvaged
    except Exception as salvage_exc:
        SQLBotLogUtil.warning(f"query salvage on fail skipped: {salvage_exc}")

    error = str(state.get("error") or "unknown error")
    public_error = str(state.get("public_error") or public_error_message(error))
    current_outcome = state.get("outcome")
    outcome = (
        cast(RunOutcome, dict(current_outcome))
        if current_outcome and current_outcome.get("status") != "running"
        else None
    )
    outcome = _persist_query_terminal_failure(
        state,
        error_summary=error,
        public_error=public_error,
        outcome=outcome,
    )
    StreamSink.from_state(state).error(public_error)
    return {**state, "error": error, "outcome": outcome}


def _extract_title_from_sql_answer(raw_text: str, plans: list[dict[str, Any]]) -> str:
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
        title = _generation_question(llm_service)[:20]
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
