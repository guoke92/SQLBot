import datetime
from typing import Any, Dict, List, Optional

import orjson
from sqlalchemy import and_, desc, func, select, update

from apps.chat.answer_payload import (
    get_answer_step_data,
    is_answer_payload,
    normalize_answer_payload,
    project_turn_answer,
)
from apps.chat.constants import DYNAMIC_DS_TYPES
from apps.chat.models.chat_model import (
    Chat,
    ChatInfo,
    ChatLog,
    ChatLogHistory,
    ChatLogHistoryItem,
    ChatQuestion,
    ChatRecord,
    ChatRecordResult,
    CreateChat,
    OperationEnum,
    RenameChat,
    TypeEnum,
)
from apps.chat.result_data import format_json_data
from apps.chat.steps.observability import project_audit_message
from apps.conversation.models import ConversationInterrupt, ConversationRun
from apps.conversation.run_service import serialize_interrupt
from apps.datasource.crud.datasource import get_ds
from apps.datasource.crud.recommended_problem import get_datasource_recommended_chart
from apps.datasource.models.datasource import CoreDatasource
from apps.db.constant import DB
from apps.protocol import get_protocol_for_ds
from apps.system.crud.assistant import AssistantOutDs, AssistantOutDsFactory
from apps.system.schemas.system_schema import AssistantOutDsSchema
from common.core.deps import CurrentAssistant, CurrentUser, SessionDep, Trans
from common.utils.data_format import DataFormat
from common.utils.json_utils import extract_nested_json
from common.utils.utils import SQLBotLogUtil


def _run_duration_breakdown(
    run: ConversationRun | None,
    interrupts: list[ConversationInterrupt],
    *,
    fallback_start: datetime.datetime | None,
    fallback_end: datetime.datetime | None,
) -> tuple[float | None, float, float | None]:
    """Return elapsed, user-waiting and actual processing seconds."""
    start = (run.started_at or run.create_time) if run is not None else fallback_start
    end = (
        run.completed_at or datetime.datetime.now()
        if run is not None
        else fallback_end or datetime.datetime.now()
    )
    elapsed: float | None = None
    if start and end:
        try:
            elapsed = round(max(0.0, (end - start).total_seconds()), 2)
        except Exception:
            elapsed = None
    waiting = 0.0
    if run is not None:
        for interrupt in interrupts:
            wait_end = (
                interrupt.consumed_at or run.completed_at or datetime.datetime.now()
            )
            if interrupt.create_time and wait_end > interrupt.create_time:
                waiting += (wait_end - interrupt.create_time).total_seconds()
    waiting = round(waiting, 2)
    processing = round(max(0.0, elapsed - waiting), 2) if elapsed is not None else None
    return elapsed, waiting, processing


def _clarification_wait_items(
    interrupts: list[ConversationInterrupt],
    *,
    run_end: datetime.datetime | None,
    fallback_end: datetime.datetime | None,
) -> list[ChatLogHistoryItem]:
    """澄清卡的 create_time→consumed_at 用户响应窗口投影成时间线 item。

    该窗口没有任何 chat_log span 承载；不投影则执行详情的 span 耗时总和对
    不上总时长（chat 165：106s spans vs 277s total）。未消费的澄清卡等待
    延伸到 run 结束，让"挂起中"也可对账。"""
    items: list[ChatLogHistoryItem] = []
    for interrupt in interrupts:
        if interrupt.create_time is None:
            continue
        wait_end = interrupt.consumed_at or run_end or fallback_end
        if wait_end is None or wait_end < interrupt.create_time:
            continue
        items.append(
            ChatLogHistoryItem(
                id=None,
                run_id=interrupt.run_id,
                start_time=interrupt.create_time,
                finish_time=wait_end,
                duration=round((wait_end - interrupt.create_time).total_seconds(), 2),
                operate=None,
                local_operation=True,
                error=False,
                status="interrupted",
                graph_node="await_clarification",
                title_key="chat.log.WAIT_CLARIFICATION",
                detail={
                    "interrupt_id": interrupt.interrupt_id,
                    "user_wait": True,
                },
            )
        )
    return items


def get_chat_record_by_id(session: SessionDep, record_id: int):
    record: ChatRecord | None = None

    stmt = select(
        ChatRecord.id,
        ChatRecord.question,
        ChatRecord.chat_id,
        ChatRecord.datasource,
        ChatRecord.engine_type,
        ChatRecord.ai_modal_id,
        ChatRecord.create_by,
        ChatRecord.re_exec,
    ).where(and_(ChatRecord.id == record_id))
    result = session.execute(stmt)
    for r in result:
        record = ChatRecord(
            id=r.id,
            question=r.question,
            chat_id=r.chat_id,
            datasource=r.datasource,
            engine_type=r.engine_type,
            ai_modal_id=r.ai_modal_id,
            create_by=r.create_by,
            re_exec=r.re_exec,
        )
    return record


def get_chat(session: SessionDep, chat_id: int) -> Chat:
    statement = select(Chat).where(Chat.id == chat_id)
    chat = session.exec(statement).scalars().first()
    return chat


def list_chats(session: SessionDep, current_user: CurrentUser) -> List[Chat]:
    oid = current_user.oid if current_user.oid is not None else 1
    chart_list = (
        session.query(Chat)
        .filter(and_(Chat.create_by == current_user.id, Chat.oid == oid))
        .order_by(Chat.create_time.desc())
        .all()
    )
    return chart_list


def list_recent_questions(
    session: SessionDep, current_user: CurrentUser, datasource_id: int
) -> List[str]:
    chat_records = (
        session.query(ChatRecord.question)
        .join(Chat, ChatRecord.chat_id == Chat.id)  # 关联Chat表
        .filter(
            Chat.datasource == datasource_id,  # 使用Chat表的datasource字段
            ChatRecord.question.isnot(None),
            ChatRecord.create_by == current_user.id,
        )
        .group_by(ChatRecord.question)
        .order_by(desc(func.max(ChatRecord.create_time)))
        .limit(10)
        .all()
    )
    return [record[0] for record in chat_records] if chat_records else []


def rename_chat_with_user(
    session: SessionDep, current_user: CurrentUser, rename_object: RenameChat
) -> str:
    chat = session.get(Chat, rename_object.id)
    if not chat:
        raise Exception(f"Chat with id {rename_object.id} not found")
    if chat.create_by != current_user.id:
        raise Exception(
            f"Chat with id {rename_object.id} not Owned by the current user"
        )
    chat.brief = rename_object.brief.strip()[:20]
    chat.brief_generate = rename_object.brief_generate
    session.add(chat)
    session.flush()
    session.refresh(chat)

    brief = chat.brief
    session.commit()
    return brief


def rename_chat(session: SessionDep, rename_object: RenameChat) -> str:
    chat = session.get(Chat, rename_object.id)
    if not chat:
        raise Exception(f"Chat with id {rename_object.id} not found")

    chat.brief = rename_object.brief.strip()[:20]
    chat.brief_generate = rename_object.brief_generate
    session.add(chat)
    session.flush()
    session.refresh(chat)

    brief = chat.brief
    session.commit()
    return brief


def delete_chat(session, chart_id) -> str:
    chat = session.query(Chat).filter(Chat.id == chart_id).first()
    if not chat:
        return f"Chat with id {chart_id} has been deleted"

    session.delete(chat)
    session.commit()

    return f"Chat with id {chart_id} has been deleted"


def delete_chat_with_user(session, current_user: CurrentUser, chart_id) -> str:
    chat = session.query(Chat).filter(Chat.id == chart_id).first()
    if not chat:
        return f"Chat with id {chart_id} has been deleted"
    if chat.create_by != current_user.id:
        raise Exception(f"Chat with id {chart_id} not Owned by the current user")
    session.delete(chat)
    session.commit()

    return f"Chat with id {chart_id} has been deleted"


def get_chart_config(session: SessionDep, chart_record_id: int):
    stmt = select(ChatRecord.chart).where(and_(ChatRecord.id == chart_record_id))
    res = session.execute(stmt)
    for row in res:
        try:
            return orjson.loads(row.chart)
        except Exception:
            pass
    return {}


def _format_column(column: dict) -> str:
    """格式化单个column字段"""
    value = column.get("value", "")
    name = column.get("name", "")
    if value != name and name:
        return f"{value}({name})"
    return value


def format_chart_fields(chart_info: dict) -> list:
    fields = []

    # 处理 columns
    for column in chart_info.get("columns") or []:
        fields.append(_format_column(column))

    # 处理 axis
    if axis := chart_info.get("axis"):
        # 处理 x 轴
        if x_axis := axis.get("x"):
            fields.append(_format_column(x_axis))

        # 处理 y 轴
        if y_axis := axis.get("y"):
            if isinstance(y_axis, list):
                for column in y_axis:
                    fields.append(_format_column(column))
            else:
                fields.append(_format_column(y_axis))

        # 处理 series
        if series := axis.get("series"):
            fields.append(_format_column(series))

    return [field for field in fields if field]  # 过滤空字符串


def get_last_execute_sql_error(session: SessionDep, chart_id: int):
    stmt = (
        select(ChatRecord.error)
        .where(and_(ChatRecord.chat_id == chart_id))
        .order_by(ChatRecord.create_time.desc())
        .limit(1)
    )
    res = session.execute(stmt).scalar()
    if res:
        try:
            obj = orjson.loads(res)
            if obj.get("type") and obj.get("type") == "exec-query-err":
                return obj.get("traceback")
        except Exception:
            pass

    return None


def get_chat_chart_config(
    session: SessionDep, chat_record_id: int, step_index: int = 0
):
    stmt = select(ChatRecord.answer, ChatRecord.chart).where(
        and_(ChatRecord.id == chat_record_id)
    )
    res = session.execute(stmt)
    for row in res:
        if isinstance(row.answer, dict):
            datasets = (
                row.answer.get("datasets") or row.answer.get("source_datasets") or []
            )
            if datasets:
                index = step_index if 0 <= step_index < len(datasets) else 0
                item = datasets[index]
                if isinstance(item, dict) and isinstance(item.get("chart"), dict):
                    return item.get("chart") or {}
        try:
            return orjson.loads(row.chart)
        except Exception:
            pass
    return {}


def get_chart_data_with_user(
    session: SessionDep, current_user: CurrentUser, chat_record_id: int
):
    stmt = select(ChatRecord.answer, ChatRecord.data).where(
        and_(ChatRecord.id == chat_record_id, ChatRecord.create_by == current_user.id)
    )
    res = session.execute(stmt)
    for row in res:
        if isinstance(row.answer, dict):
            return project_turn_answer(row.answer)
        try:
            return orjson.loads(row.data)
        except Exception:
            pass
    return {}


def get_chart_data_with_user_live(
    session: SessionDep, current_user: CurrentUser, chat_record_id: int
):
    stmt = select(ChatRecord.datasource, ChatRecord.sql, ChatRecord.re_exec).where(
        and_(ChatRecord.id == chat_record_id, ChatRecord.create_by == current_user.id)
    )
    row = session.execute(stmt).first()
    if not row:
        return {"status": "failed", "data": [], "message": "Record not found"}
    return get_chart_data_ds(session, row.datasource, re_exec_json=row.re_exec)


def get_chart_data_ds(session: SessionDep, ds_id, re_exec_json: Optional[str] = None):
    """Re-run a stored chart query through the datasource protocol.

    ``re_exec_json`` is the protocol-owned executable contract. Display SQL is
    never reinterpreted as an execution plan.
    """
    json_result: Dict[str, Any] = {"status": "success", "data": [], "message": ""}
    try:
        datasource = get_ds(session, ds_id)
        if datasource is None:
            json_result["status"] = "failed"
            json_result["message"] = "Datasource not found"
            return json_result

        proto = get_protocol_for_ds(datasource)
        plan = None
        if re_exec_json:
            try:
                re_exec = (
                    orjson.loads(re_exec_json)
                    if isinstance(re_exec_json, (str, bytes))
                    else re_exec_json
                )
            except Exception:
                re_exec = None
            if isinstance(re_exec, dict):
                plan = proto.plan_from_re_exec(datasource, re_exec)

        if plan is None or not plan.success:
            json_result["status"] = "failed"
            json_result["message"] = (
                plan.message
                if plan is not None
                else "Missing re_exec payload; cannot re-execute without a protocol plan"
            )
            return json_result

        qr = proto.execute(datasource, plan)
        _data = DataFormat.convert_large_numbers_in_object_array(qr.data)
        _data = DataFormat.normalize_qualified_sql_column_keys_in_object_array(_data)
        json_result["data"] = _data
        return json_result
    except Exception as e:
        SQLBotLogUtil.error(f"Function failed: {e}")
        json_result["status"] = "failed"
        json_result["message"] = f"{e}"
    return json_result


def get_chat_chart_data(session: SessionDep, chat_record_id: int, step_index: int = 0):
    """Return chart rows for a record.

    For multi-step payloads, returns ``steps[step_index].data`` (default first step)
    so analysis / predict / legacy single-chart consumers keep working.
    """
    stmt = select(ChatRecord.answer, ChatRecord.data).where(
        and_(ChatRecord.id == chat_record_id)
    )
    res = session.execute(stmt)
    for row in res:
        try:
            raw = (
                project_turn_answer(row.answer)
                if isinstance(row.answer, dict)
                else orjson.loads(row.data)
            )
            return get_answer_step_data(raw, step_index=step_index)
        except Exception:
            pass
    return {}


def get_chat_predict_data_with_user(
    session: SessionDep, current_user: CurrentUser, chat_record_id: int
):
    stmt = select(ChatRecord.predict_data).where(
        and_(ChatRecord.id == chat_record_id, ChatRecord.create_by == current_user.id)
    )
    res = session.execute(stmt)
    for row in res:
        try:
            return orjson.loads(row.predict_data)
        except Exception:
            pass
    return {}


def get_chat_predict_data(session: SessionDep, chat_record_id: int):
    stmt = select(ChatRecord.predict_data).where(and_(ChatRecord.id == chat_record_id))
    res = session.execute(stmt)
    for row in res:
        try:
            return orjson.loads(row.predict_data)
        except Exception:
            pass
    return {}


def get_chat_with_records_with_data(
    session: SessionDep,
    chart_id: int,
    current_user: CurrentUser,
    current_assistant: CurrentAssistant,
) -> ChatInfo:
    return get_chat_with_records(
        session, chart_id, current_user, current_assistant, True
    )


# Chat-list may attach at most one reasoning blob per (record, operate).
# Multi generate_query / chart logs (agentic regen) must not multiply ChatRecord rows.
_REASONING_OPERATES: tuple[OperationEnum, ...] = (
    OperationEnum.CLARIFY_INTENT,
    OperationEnum.GENERATE_QUERY,
    OperationEnum.GENERATE_CHART,
    OperationEnum.ANALYSIS,
    OperationEnum.PREDICT_DATA,
)

_REASONING_FIELD_BY_OPERATE: dict[OperationEnum, str] = {
    OperationEnum.CLARIFY_INTENT: "intent_reasoning_content",
    OperationEnum.GENERATE_QUERY: "sql_reasoning_content",
    OperationEnum.GENERATE_CHART: "chart_reasoning_content",
    OperationEnum.ANALYSIS: "analysis_reasoning_content",
    OperationEnum.PREDICT_DATA: "predict_reasoning_content",
}


def _latest_reasoning_by_record(
    session: SessionDep,
    record_ids: List[int],
) -> Dict[int, Dict[str, Optional[str]]]:
    """Map record_id → {sql_reasoning_content, ...} using the latest log per operate.

    ChatLog is 1:N to ChatRecord; never join raw logs into the record list query.
    """
    out: Dict[int, Dict[str, Optional[str]]] = {
        rid: {field: None for field in _REASONING_FIELD_BY_OPERATE.values()}
        for rid in record_ids
    }
    if not record_ids:
        return out

    stmt = (
        select(
            ChatLog.pid, ChatLog.operate, ChatLog.reasoning_content, ChatLog.start_time
        )
        .where(
            and_(
                ChatLog.pid.in_(record_ids),
                ChatLog.type == TypeEnum.CHAT,
                ChatLog.operate.in_(_REASONING_OPERATES),
            )
        )
        .order_by(ChatLog.pid.asc(), ChatLog.start_time.desc())
    )
    # First row per (pid, operate) wins (latest start_time).
    seen: set[tuple[int, str]] = set()
    for pid, operate, reasoning, _start in session.execute(stmt).all():
        if pid is None or operate is None:
            continue
        op_key = operate.value if isinstance(operate, OperationEnum) else str(operate)
        # Normalize operate enum from DB string / enum
        op_enum: Optional[OperationEnum] = None
        if isinstance(operate, OperationEnum):
            op_enum = operate
        else:
            for item in OperationEnum:
                if item.value == op_key or item.name == op_key:
                    op_enum = item
                    break
        if op_enum is None or op_enum not in _REASONING_FIELD_BY_OPERATE:
            continue
        text = reasoning if isinstance(reasoning, str) else None
        if text is not None and text.strip() == "":
            text = None
        if text is None:
            continue
        sk = (int(pid), op_enum.value)
        if sk in seen:
            continue
        seen.add(sk)
        field = _REASONING_FIELD_BY_OPERATE[op_enum]
        bucket = out.setdefault(
            int(pid), {f: None for f in _REASONING_FIELD_BY_OPERATE.values()}
        )
        bucket[field] = text
    return out



def _agent_stages_by_record(
    session: SessionDep,
    record_ids: List[int],
) -> Dict[int, List[Dict[str, Any]]]:
    stages_map: Dict[int, List[Dict[str, Any]]] = {rid: [] for rid in record_ids}
    if not record_ids:
        return stages_map
    stmt = (
        select(ChatLog.pid, ChatLog.operate, ChatLog.reasoning_content, ChatLog.messages)
        .where(
            and_(
                ChatLog.pid.in_(record_ids),
                ChatLog.operate.in_([OperationEnum.AGENT_STEP, OperationEnum.TOOL_CALL]),
            )
        )
        .order_by(ChatLog.pid.asc(), ChatLog.start_time.asc(), ChatLog.id.asc())
    )
    tool_map = {
        "execute_sql_sandbox": "执行查询 (execute_sql_sandbox)",
        "patch_and_compile_sql": "增量补丁 (patch_and_compile_sql)",
        "compare_results": "数据对比 (compare_results)",
        "search_schema": "结构检索 (search_schema)",
        "search_wiki": "查阅知识 (search_wiki)",
        "request_clarification": "请求澄清 (request_clarification)",
    }
    counters: Dict[int, int] = {}
    for pid, operate, reasoning, messages in session.execute(stmt).all():
        if pid is None or operate is None:
            continue
        pid_int = int(pid)
        msg = messages if isinstance(messages, dict) else {}
        op_str = str(operate)
        if "AGENT_STEP" in op_str:
            thought = reasoning or ""
            out = msg.get("output")
            if isinstance(out, dict) and out.get("content"):
                if out.get("tool_calls"):
                    thought = thought or out.get("content")
            elif isinstance(out, str) and "round" in str(msg.get("brief")):
                thought = thought or out
            if thought and str(thought).strip():
                counters[pid_int] = counters.get(pid_int, 0) + 1
                stages_map[pid_int].append({
                    "id": f"thought-{counters[pid_int]}",
                    "type": "thought",
                    "title": "思考",
                    "content": str(thought).strip(),
                    "status": "completed",
                })
        elif "TOOL_CALL" in op_str:
            inp = msg.get("input") or {}
            t_name = inp.get("tool") or "tool"
            args = inp.get("arguments") or {}
            counters[pid_int] = counters.get(pid_int, 0) + 1
            stages_map[pid_int].append({
                "id": f"tool-{counters[pid_int]}",
                "type": "tool",
                "title": tool_map.get(t_name, f"工具调用 ({t_name})"),
                "toolName": t_name,
                "toolArgs": args,
                "sql": args.get("sql") if isinstance(args, dict) else None,
                "status": "completed",
            })
    return stages_map


def _token_usage_by_record(
    session: SessionDep, record_ids: List[int]
) -> Dict[int, int]:
    """Sum non-local log token_usage per ChatRecord (1:N safe bulk attach)."""
    token_usage_map: Dict[int, int] = {}
    if not record_ids:
        return token_usage_map
    log_stmt = select(ChatLog.pid, ChatLog.token_usage).where(
        and_(
            ChatLog.pid.in_(record_ids),
            ChatLog.local_operation == False,  # noqa: E712
            ChatLog.operate != OperationEnum.GENERATE_RECOMMENDED_QUESTIONS,
            ChatLog.token_usage.is_not(None),
        )
    )
    for pid, token_usage in session.execute(log_stmt).all():
        if not pid or token_usage is None:
            continue
        tokens_to_add = 0
        if isinstance(token_usage, dict):
            if token_usage and "total_tokens" in token_usage:
                token_value = token_usage["total_tokens"]
                if isinstance(token_value, (int, float)):
                    tokens_to_add = int(token_value)
        elif isinstance(token_usage, (int, float)):
            tokens_to_add = int(token_usage)
        if tokens_to_add > 0:
            token_usage_map[int(pid)] = token_usage_map.get(int(pid), 0) + tokens_to_add
    return token_usage_map


def get_chat_with_records(
    session: SessionDep,
    chart_id: int,
    current_user: CurrentUser,
    current_assistant: CurrentAssistant,
    with_data: bool = False,
    trans: Trans = None,
) -> ChatInfo:
    """Load one chat timeline: result cardinality == ChatRecord rows for this chat.

    Reasoning / tokens come from ChatLog via bulk maps — never multi-outerjoin
    raw logs onto records (agentic regen multiplies GENERATE_* logs).
    """
    chat = session.get(Chat, chart_id)
    if not chat:
        raise Exception(f"Chat with id {chart_id} not found")
    if chat.create_by != current_user.id:
        raise Exception(f"Chat with id {chart_id} not Owned by the current user")
    chat_info = ChatInfo(**chat.model_dump())

    if current_assistant and current_assistant.type in DYNAMIC_DS_TYPES:
        out_ds_instance = AssistantOutDsFactory.get_instance(current_assistant)
        ds = out_ds_instance.get_ds(chat.datasource, trans)
    else:
        ds = session.get(CoreDatasource, chat.datasource) if chat.datasource else None

    if not ds:
        chat_info.datasource_exists = False
        chat_info.datasource_name = "Datasource not exist"
    else:
        chat_info.datasource_exists = True
        chat_info.datasource_name = ds.name
        chat_info.ds_type = ds.type

    # Single record base query (with_data only toggles data columns).
    base_cols = [
        ChatRecord.id,
        ChatRecord.chat_id,
        ChatRecord.create_time,
        ChatRecord.finish_time,
        ChatRecord.question,
        ChatRecord.turn_kind,
        ChatRecord.relation,
        ChatRecord.reference_record_ids,
        ChatRecord.answer_revision,
        ChatRecord.answer,
        ChatRecord.active_run_id,
        ChatRecord.sql_answer,
        ChatRecord.sql,
        ChatRecord.datasource,
        ChatRecord.engine_type,
        ChatRecord.re_exec,
        ChatRecord.chart_answer,
        ChatRecord.chart,
        ChatRecord.analysis,
        ChatRecord.predict,
        ChatRecord.datasource_select_answer,
        ChatRecord.recommended_question,
        ChatRecord.first_chat,
        ChatRecord.finish,
        ChatRecord.error,
    ]
    if with_data:
        base_cols.extend([ChatRecord.data, ChatRecord.predict_data])

    stmt = (
        select(*base_cols)
        .where(
            and_(
                ChatRecord.create_by == current_user.id, ChatRecord.chat_id == chart_id
            )
        )
        .order_by(ChatRecord.create_time)
    )
    rows = session.execute(stmt).all()
    record_ids = [int(row.id) for row in rows if row.id is not None]

    run_rows = (
        list(
            session.exec(
                select(ConversationRun)
                .where(ConversationRun.chat_record_id.in_(record_ids))
                .order_by(ConversationRun.chat_record_id, ConversationRun.attempt_index)
            ).scalars()
        )
        if record_ids
        else []
    )
    runs_by_record = {int(run.chat_record_id): run for run in run_rows}
    run_ids = [run.run_id for run in run_rows]
    interrupts = (
        list(
            session.exec(
                select(ConversationInterrupt).where(
                    ConversationInterrupt.run_id.in_(run_ids)
                )
            ).scalars()
        )
        if run_ids
        else []
    )
    interrupts_by_run: dict[str, list[ConversationInterrupt]] = {}
    for item in interrupts:
        interrupts_by_run.setdefault(item.run_id, []).append(item)
    for items in interrupts_by_run.values():
        items.sort(key=lambda item: item.version)

    token_usage_map = _token_usage_by_record(session, record_ids)
    agent_stages_map = _agent_stages_by_record(session, record_ids)
    # Reasoning is for history hydrate when payload omits or prefers log reasoning;
    # with_data path historically skipped joins — keep that behavior (maps empty unused).
    reasoning_map = (
        {} if with_data else _latest_reasoning_by_record(session, record_ids)
    )

    record_list: list[ChatRecordResult] = []
    for row in rows:
        rid = int(row.id)
        reason = reasoning_map.get(rid) or {}
        run = runs_by_record.get(rid)
        _elapsed, _waiting, duration = _run_duration_breakdown(
            run,
            interrupts_by_run.get(run.run_id, []) if run is not None else [],
            fallback_start=row.create_time,
            fallback_end=row.finish_time,
        )
        active_interrupt = (
            next(
                (
                    item
                    for item in interrupts_by_run.get(run.run_id, [])
                    if item.interrupt_id == run.active_interrupt_id
                ),
                None,
            )
            if run and run.active_interrupt_id
            else None
        )
        kwargs: Dict[str, Any] = dict(
            id=row.id,
            chat_id=row.chat_id,
            create_time=row.create_time,
            finish_time=row.finish_time,
            duration=duration,
            total_tokens=token_usage_map.get(rid, 0),
            agent_stages=agent_stages_map.get(rid, []),
            question=row.question,
            turn_kind=getattr(row, "turn_kind", "query"),
            relation=getattr(row, "relation", "independent"),
            reference_record_ids=getattr(row, "reference_record_ids", []) or [],
            answer_revision=int(getattr(row, "answer_revision", 0) or 0),
            answer=getattr(row, "answer", None),
            sql_answer=row.sql_answer,
            sql=row.sql,
            datasource=row.datasource,
            engine_type=getattr(row, "engine_type", None),
            re_exec=getattr(row, "re_exec", None),
            feedback=getattr(row, "feedback", None),
            chart_answer=row.chart_answer,
            chart=row.chart,
            analysis=row.analysis,
            predict=row.predict,
            datasource_select_answer=row.datasource_select_answer,
            recommended_question=row.recommended_question,
            first_chat=row.first_chat,
            finish=row.finish,
            error=row.error,
            run_id=run.run_id if run else None,
            run_attempt_index=int(run.attempt_index or 0) if run else 0,
            run_status=run.status if run else None,
            run_event_cursor=int(run.event_cursor or 0) if run else 0,
            run_current_node=run.current_node if run else None,
            run_dispatch_attempts=int(run.dispatch_attempts or 0) if run else 0,
            run_update_time=run.update_time if run else None,
            run_started_at=run.started_at if run else None,
            run_completed_at=run.completed_at if run else None,
            active_interrupt=(
                serialize_interrupt(active_interrupt) if active_interrupt else None
            ),
            interrupts=(
                [
                    serialize_interrupt(item)
                    for item in interrupts_by_run.get(run.run_id, [])
                ]
                if run
                else []
            ),
            sql_reasoning_content=reason.get("sql_reasoning_content"),
            chart_reasoning_content=reason.get("chart_reasoning_content"),
            analysis_reasoning_content=reason.get("analysis_reasoning_content"),
            predict_reasoning_content=reason.get("predict_reasoning_content"),
            intent_reasoning_content=reason.get("intent_reasoning_content"),
        )
        if with_data:
            canonical_answer = getattr(row, "answer", None)
            kwargs["data"] = (
                orjson.dumps(project_turn_answer(canonical_answer)).decode()
                if isinstance(canonical_answer, dict)
                else getattr(row, "data", None)
            )
            kwargs["predict_data"] = getattr(row, "predict_data", None)
        record_list.append(ChatRecordResult(**kwargs))

    formatted = list(map(format_record, record_list))
    for row in formatted:
        try:
            data_value = row.get("data")
            if isinstance(data_value, dict) and is_answer_payload(data_value):
                row["data"] = normalize_answer_payload(
                    data_value,
                    normalize_data=format_json_data,
                )
        except Exception:
            pass

    chat_info.records = formatted
    return chat_info


def format_record(record: ChatRecordResult):
    _dict = record.model_dump()

    if (
        record.sql_answer
        and record.sql_answer.strip() != ""
        and record.sql_answer.strip()[0] == "{"
        and record.sql_answer.strip()[-1] == "}"
    ):
        _obj = orjson.loads(record.sql_answer)
        _dict["sql_answer"] = _obj.get("reasoning_content")
    if record.sql_reasoning_content and record.sql_reasoning_content.strip() != "":
        _dict["sql_answer"] = record.sql_reasoning_content
    if (
        record.chart_answer
        and record.chart_answer.strip() != ""
        and record.chart_answer.strip()[0] == "{"
        and record.chart_answer.strip()[-1] == "}"
    ):
        _obj = orjson.loads(record.chart_answer)
        _dict["chart_answer"] = _obj.get("reasoning_content")
    if record.chart_reasoning_content and record.chart_reasoning_content.strip() != "":
        _dict["chart_answer"] = record.chart_reasoning_content
    if (
        record.analysis
        and record.analysis.strip() != ""
        and record.analysis.strip()[0] == "{"
        and record.analysis.strip()[-1] == "}"
    ):
        _obj = orjson.loads(record.analysis)
        _dict["analysis_thinking"] = _obj.get("reasoning_content")
        _dict["analysis"] = _obj.get("content")
    if (
        record.analysis_reasoning_content
        and record.analysis_reasoning_content.strip() != ""
    ):
        _dict["analysis_thinking"] = record.analysis_reasoning_content
    if (
        record.predict
        and record.predict.strip() != ""
        and record.predict.strip()[0] == "{"
        and record.predict.strip()[-1] == "}"
    ):
        _obj = orjson.loads(record.predict)
        _dict["predict"] = _obj.get("reasoning_content")
        _dict["predict_content"] = _obj.get("content")
    if (
        record.predict_reasoning_content
        and record.predict_reasoning_content.strip() != ""
    ):
        _dict["predict"] = record.predict_reasoning_content
    if record.data and record.data.strip() != "":
        try:
            _obj = orjson.loads(record.data)
            _dict["data"] = _obj
        except Exception:
            pass
    if record.predict_data and record.predict_data.strip() != "":
        try:
            _obj = orjson.loads(record.predict_data)
            _dict["predict_data"] = _obj
        except Exception:
            pass
    if record.sql and record.sql.strip() != "":
        # Display statement is already protocol-formatted at write time
        # (SqlProtocol.format_statement_for_display / RestProtocol).
        # Do not re-apply SQL-only pretty printers based on content sniffing.
        _dict["sql"] = record.sql.strip()

    # 格式化duration字段，保留2位小数
    if "duration" in _dict and _dict["duration"] is not None:
        try:
            # 可以格式化为更易读的形式
            _dict["duration"] = round(_dict["duration"], 2)  # 保留2位小数
        except Exception:
            pass

    # 格式化total_tokens字段
    if "total_tokens" in _dict and _dict["total_tokens"] is not None:
        try:
            # 确保是整数类型
            _dict["total_tokens"] = (
                int(_dict["total_tokens"]) if _dict["total_tokens"] else 0
            )
        except Exception:
            _dict["total_tokens"] = 0

    # 去除返回前端多余的字段
    _dict.pop("sql_reasoning_content", None)
    _dict.pop("chart_reasoning_content", None)
    _dict.pop("analysis_reasoning_content", None)
    _dict.pop("predict_reasoning_content", None)

    return _dict


def get_chat_log_history(
    session: SessionDep,
    chat_record_id: int,
    current_user: CurrentUser,
    without_steps: bool = False,
    *,
    run_id: str | None = None,
) -> ChatLogHistory:
    """
    获取ChatRecord的详细历史记录

    Args:
        session: 数据库会话
        chat_record_id: ChatRecord的ID
        current_user: 当前用户
        without_steps

    Returns:
        ChatLogHistory: 包含历史步骤和时间信息的对象
    """
    # 1. 首先验证ChatRecord存在且属于当前用户
    chat_record = session.get(ChatRecord, chat_record_id)
    if not chat_record:
        raise Exception(f"ChatRecord with id {chat_record_id} not found")

    if chat_record.create_by != current_user.id:
        raise Exception(
            f"ChatRecord with id {chat_record_id} not owned by the current user"
        )

    runs = list(
        session.exec(
            select(ConversationRun)
            .where(ConversationRun.chat_record_id == chat_record_id)
            .order_by(ConversationRun.attempt_index)
        ).scalars()
    )
    selected_run_id = run_id or chat_record.active_run_id
    run = next(
        (item for item in runs if item.run_id == selected_run_id),
        runs[-1] if runs and selected_run_id is None else None,
    )
    if run_id is not None and run is None:
        raise Exception(f"Run {run_id} does not belong to ChatRecord {chat_record_id}")

    # 2. 查询与该ChatRecord相关的所有ChatLog记录
    log_query = session.query(ChatLog).filter(
        ChatLog.pid == chat_record_id,
        ChatLog.operate != OperationEnum.GENERATE_RECOMMENDED_QUESTIONS,
    )
    if run is not None:
        log_query = log_query.filter(ChatLog.run_id == run.run_id)
    chat_logs = log_query.order_by(ChatLog.start_time.asc(), ChatLog.id.asc()).all()

    # 3. 计算总的时间和token信息
    total_tokens = 0
    steps = []

    for log in chat_logs:
        # 计算单条记录的token消耗
        log_tokens = 0
        if log.token_usage is not None:
            if isinstance(log.token_usage, dict):
                if log.token_usage and "total_tokens" in log.token_usage:
                    token_value = log.token_usage["total_tokens"]
                    if isinstance(token_value, (int, float)):
                        log_tokens = int(token_value)
            elif isinstance(log.token_usage, (int, float)):
                log_tokens = log.token_usage

        # 累加到总token消耗
        total_tokens += log_tokens

        if not without_steps:
            # 计算单条记录的耗时
            duration = None
            if log.start_time and log.finish_time:
                try:
                    time_diff = log.finish_time - log.start_time
                    duration = round(time_diff.total_seconds(), 2)
                except Exception:
                    duration = None

            # 获取操作类型的枚举名称
            operate_name = None
            message = None
            if log.operate:
                # 如果是OperationEnum枚举实例
                if isinstance(log.operate, OperationEnum):
                    operate_name = log.operate.name
                # 如果是字符串，尝试从枚举值获取名称
                elif isinstance(log.operate, str):
                    try:
                        # 通过枚举值找到对应的枚举实例
                        for enum_item in OperationEnum:
                            if enum_item.value == log.operate:
                                operate_name = enum_item.name
                                break
                    except Exception:
                        operate_name = log.operate
                else:
                    operate_name = str(log.operate)

                if log.messages is not None:
                    message = log.messages
                    # JSONB may already be dict/list; string payloads try parse.
                    if not log.operate == OperationEnum.CHOOSE_TABLE and isinstance(
                        message, (str, bytes)
                    ):
                        try:
                            message = orjson.loads(message)
                        except Exception:
                            pass

            run_terminal = bool(
                run is not None
                and run.status in {"succeeded", "degraded", "failed", "cancelled"}
            )
            projection = project_audit_message(
                message,
                finish_time=log.finish_time,
                error=bool(log.error),
                run_terminal=run_terminal,
            )

            # V1 fields are normalized here. The frontend never guesses the
            # storage shape; unversioned history remains one raw fallback.
            history_item = ChatLogHistoryItem(
                id=log.id,
                run_id=log.run_id,
                start_time=log.start_time,
                finish_time=log.finish_time,
                duration=duration,
                total_tokens=log_tokens,
                operate=operate_name,
                local_operation=log.local_operation,
                error=log.error,
                status=projection["status"],
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
                model_calls=projection["model_calls"],
                reasoning_content=log.reasoning_content,
                message=projection["message"],
            )

            steps.append(history_item)

    # 4. 计算总耗时（使用ChatRecord的时间）
    run_interrupts: list[ConversationInterrupt] = []
    if run is not None:
        run_interrupts = list(
            session.exec(
                select(ConversationInterrupt).where(
                    ConversationInterrupt.run_id == run.run_id
                )
            ).scalars()
        )
    history_start = (
        run.started_at or run.create_time
        if run is not None
        else chat_record.create_time
    )
    elapsed_duration, waiting_duration, processing_duration = _run_duration_breakdown(
        run,
        run_interrupts,
        fallback_start=chat_record.create_time,
        fallback_end=chat_record.finish_time,
    )

    if run is not None:
        run_summary = {
            "run_id": run.run_id,
            "status": run.status,
            "current_node": run.current_node,
            "dispatch_attempts": int(run.dispatch_attempts or 0),
            "started_at": run.started_at,
            "completed_at": run.completed_at,
            "update_time": run.update_time,
        }
    else:
        run_summary = {
            "status": (
                "failed"
                if chat_record.error
                else "succeeded"
                if chat_record.finish
                else "running"
            ),
            "started_at": chat_record.create_time,
            "completed_at": chat_record.finish_time,
        }

    attempt_summaries = [
        {
            "run_id": item.run_id,
            "status": item.status,
            "current_node": item.current_node,
            "dispatch_attempts": int(item.dispatch_attempts or 0),
            "started_at": item.started_at,
            "completed_at": item.completed_at,
            "update_time": item.update_time,
        }
        for item in runs
    ]

    # 4.5 澄清等待 interval → 时间线 item：span 总和 + 等待 + 系统活动 = 对账
    # （run_interrupts 的 create_time→consumed_at 是用户响应窗口，无 chat_log
    # span 承载——时间线不显示会让 106s spans vs 277s 总时长对不上账。）
    steps.extend(
        _clarification_wait_items(
            run_interrupts,
            run_end=run.completed_at if run is not None else chat_record.finish_time,
            fallback_end=chat_record.finish_time,
        )
    )
    steps.sort(key=lambda item: item.start_time or datetime.datetime.min)

    # 5. 创建并返回统一的 ExecutionDetails 读取模型
    chat_log_history = ChatLogHistory(
        start_time=history_start,
        finish_time=run.completed_at if run is not None else chat_record.finish_time,
        duration=processing_duration,
        elapsed_duration=elapsed_duration,
        waiting_duration=waiting_duration,
        total_tokens=total_tokens,
        run=run_summary,
        attempts=attempt_summaries,
        steps=steps,
    )

    return chat_log_history


def get_chat_brief_generate(session: SessionDep, chat_id: int):
    chat = get_chat(session=session, chat_id=chat_id)
    if chat is not None and chat.brief_generate is not None:
        return chat.brief_generate
    else:
        return False


def list_generate_chart_logs(session: SessionDep, chart_id: int) -> List[ChatLog]:
    stmt = (
        select(ChatLog)
        .where(
            and_(
                ChatLog.pid.in_(
                    select(ChatRecord.id).where(and_(ChatRecord.chat_id == chart_id))
                ),
                ChatLog.type == TypeEnum.CHAT,
                ChatLog.operate == OperationEnum.GENERATE_CHART,
            )
        )
        .order_by(ChatLog.start_time)
    )
    result = session.execute(stmt).all()
    _list = []
    for row in result:
        for r in row:
            _list.append(ChatLog(**r.model_dump()))
    return _list


def create_chat(
    session: SessionDep,
    current_user: CurrentUser,
    create_chat_obj: CreateChat,
    require_datasource: bool = True,
    current_assistant: CurrentAssistant = None,
) -> ChatInfo:
    chat_type = (create_chat_obj.chat_type or "chat").strip() or "chat"
    if chat_type not in ("chat", "config"):
        raise Exception(f"Unsupported chat_type: {chat_type}")
    # Config assistant is metadata-only; never require NLQ datasource.
    # Resolve before the DS-None check so curd is the single truth source.
    if chat_type == "config":
        require_datasource = False

    if not create_chat_obj.datasource and require_datasource:
        raise Exception("Datasource cannot be None")

    if not create_chat_obj.question or create_chat_obj.question.strip() == "":
        # Config chats default to a recognizable brief (not a bare timestamp).
        if chat_type == "config":
            create_chat_obj.question = "Config Assistant"
        else:
            create_chat_obj.question = datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

    chat = Chat(
        create_time=datetime.datetime.now(),
        create_by=current_user.id,
        oid=current_user.oid if current_user.oid is not None else 1,
        brief=create_chat_obj.question.strip()[:20],
        chat_type=chat_type,
        origin=create_chat_obj.origin if create_chat_obj.origin is not None else 0,
    )
    ds: CoreDatasource | AssistantOutDsSchema | None = None
    if create_chat_obj.datasource:
        chat.datasource = create_chat_obj.datasource
        if current_assistant and current_assistant.type in DYNAMIC_DS_TYPES:
            out_ds_instance: AssistantOutDs = AssistantOutDsFactory.get_instance(
                current_assistant
            )
            ds = out_ds_instance.get_ds(chat.datasource)
            ds.type_name = DB.get_db(ds.type).db_name
        else:
            ds = session.get(CoreDatasource, create_chat_obj.datasource)
            if ds.oid != current_user.oid:
                raise Exception(
                    f"Datasource with id {create_chat_obj.datasource} does not belong to current workspace"
                )

        if not ds:
            raise Exception(
                f"Datasource with id {create_chat_obj.datasource} not found"
            )

        # Persist protocol type key ("api"/"mysql"), not display name ("API"/"MySQL").
        chat.engine_type = ds.type
    else:
        chat.engine_type = ""

    chat_info = ChatInfo(**chat.model_dump())

    session.add(chat)
    session.flush()
    session.refresh(chat)
    chat_info.id = chat.id
    session.commit()

    if ds:
        chat_info.datasource_exists = True
        chat_info.datasource_name = ds.name
        chat_info.ds_type = ds.type

    if require_datasource and ds:
        # generate first empty record
        record = ChatRecord()
        record.chat_id = chat.id
        record.datasource = ds.id
        record.engine_type = ds.type
        record.first_chat = True
        record.finish = True
        record.create_time = datetime.datetime.now()
        # The initial recommendation card is a terminal record. Keep the
        # lifecycle invariant ``finish => finish_time`` so history/usage code
        # never has to special-case this record type.
        record.finish_time = record.create_time
        record.create_by = current_user.id
        if isinstance(ds, CoreDatasource) and ds.recommended_config == 2:
            questions = get_datasource_recommended_chart(session, ds.id)
            record.recommended_question = orjson.dumps(questions).decode()
            record.recommended_question_answer = orjson.dumps(
                {"content": questions}
            ).decode()

        _record = ChatRecord(**record.model_dump())

        session.add(record)
        session.flush()
        session.refresh(record)
        _record.id = record.id
        session.commit()

        chat_info.records.append(_record)

    return chat_info


def save_question(
    session: SessionDep,
    current_user: CurrentUser,
    question: ChatQuestion,
    *,
    commit: bool = True,
) -> ChatRecord:
    if not question.chat_id:
        raise Exception("ChatId cannot be None")
    if not question.question or question.question.strip() == "":
        raise Exception("Question cannot be Empty")

    # chat = session.query(Chat).filter(Chat.id == question.chat_id).first()
    chat: Chat = session.get(Chat, question.chat_id)
    if not chat:
        raise Exception(f"Chat with id {question.chat_id} not found")

    record = ChatRecord()
    record.question = question.question
    record.chat_id = chat.id
    record.create_time = datetime.datetime.now()
    record.create_by = current_user.id
    record.datasource = chat.datasource
    record.engine_type = chat.engine_type
    record.ai_modal_id = question.ai_modal_id

    result = ChatRecord(**record.model_dump())

    session.add(record)
    session.flush()
    session.refresh(record)
    result.id = record.id
    if commit:
        session.commit()

    return result


def save_analysis_answer(
    session: SessionDep, record_id: int, answer: str = ""
) -> ChatRecord:
    if not record_id:
        raise Exception("Record id cannot be None")

    stmt = (
        update(ChatRecord)
        .where(and_(ChatRecord.id == record_id))
        .values(
            analysis=answer,
        )
    )

    session.execute(stmt)

    session.commit()

    record = get_chat_record_by_id(session, record_id)

    return record


def save_predict_answer(session: SessionDep, record_id: int, answer: str) -> ChatRecord:
    if not record_id:
        raise Exception("Record id cannot be None")

    stmt = (
        update(ChatRecord)
        .where(and_(ChatRecord.id == record_id))
        .values(
            predict=answer,
        )
    )

    session.execute(stmt)

    session.commit()

    record = get_chat_record_by_id(session, record_id)

    return record


def save_select_datasource_answer(
    session: SessionDep,
    record_id: int,
    answer: str,
    datasource: int = None,
    engine_type: str = None,
) -> ChatRecord:
    if not record_id:
        raise Exception("Record id cannot be None")
    record = get_chat_record_by_id(session, record_id)

    record.datasource_select_answer = answer

    if datasource:
        record.datasource = datasource
        record.engine_type = engine_type

    result = ChatRecord(**record.model_dump())

    if datasource:
        stmt = (
            update(ChatRecord)
            .where(and_(ChatRecord.id == record.id))
            .values(
                datasource_select_answer=record.datasource_select_answer,
                datasource=record.datasource,
                engine_type=record.engine_type,
            )
        )
    else:
        stmt = (
            update(ChatRecord)
            .where(and_(ChatRecord.id == record.id))
            .values(
                datasource_select_answer=record.datasource_select_answer,
            )
        )

    session.execute(stmt)

    session.commit()

    return result


def save_recommend_question_answer(
    session: SessionDep,
    record_id: int,
    answer: dict = None,
    articles_number: Optional[int] = 4,
) -> ChatRecord:
    if not record_id:
        raise Exception("Record id cannot be None")

    recommended_question_answer = orjson.dumps(answer).decode()

    json_str = "[]"
    if answer and answer.get("content") and answer.get("content") != "":
        try:
            json_str = extract_nested_json(answer.get("content"))

            if not json_str:
                json_str = "[]"
        except Exception:
            pass
    recommended_question = json_str

    stmt = (
        update(ChatRecord)
        .where(and_(ChatRecord.id == record_id))
        .values(
            recommended_question_answer=recommended_question_answer,
            recommended_question=recommended_question,
        )
    )

    session.execute(stmt)
    session.commit()

    record = get_chat_record_by_id(session, record_id)
    record.recommended_question_answer = recommended_question_answer
    record.recommended_question = recommended_question
    if articles_number > 4:
        stmt_chat = (
            update(Chat)
            .where(and_(Chat.id == record.chat_id))
            .values(
                recommended_question_answer=recommended_question_answer,
                recommended_question=recommended_question,
                recommended_generate=True,
            )
        )
        session.execute(stmt_chat)
        session.commit()

    return record


def save_sql(session: SessionDep, record_id: int, sql: str) -> ChatRecord:
    if not record_id:
        raise Exception("Record id cannot be None")

    record = get_chat_record_by_id(session, record_id)

    record.sql = sql

    result = ChatRecord(**record.model_dump())

    stmt = (
        update(ChatRecord)
        .where(and_(ChatRecord.id == record.id))
        .values(sql=record.sql)
    )

    session.execute(stmt)

    session.commit()

    return result


def save_re_exec(session: SessionDep, record_id: int, re_exec: Optional[str]) -> None:
    """Persist protocol re-execution payload alongside the display statement."""
    if not record_id or not re_exec:
        return
    stmt = (
        update(ChatRecord)
        .where(and_(ChatRecord.id == record_id))
        .values(re_exec=re_exec)
    )
    session.execute(stmt)
    session.commit()


def save_chart_answer(session: SessionDep, record_id: int, answer: str) -> ChatRecord:
    if not record_id:
        raise Exception("Record id cannot be None")

    stmt = (
        update(ChatRecord)
        .where(and_(ChatRecord.id == record_id))
        .values(
            chart_answer=answer,
        )
    )

    session.execute(stmt)

    session.commit()

    record = get_chat_record_by_id(session, record_id)

    return record


def save_chart(session: SessionDep, record_id: int, chart: str) -> ChatRecord:
    if not record_id:
        raise Exception("Record id cannot be None")
    record = get_chat_record_by_id(session, record_id)

    record.chart = chart

    result = ChatRecord(**record.model_dump())

    stmt = (
        update(ChatRecord)
        .where(and_(ChatRecord.id == record.id))
        .values(chart=record.chart)
    )

    session.execute(stmt)

    session.commit()

    return result


def save_predict_data(
    session: SessionDep, record_id: int, data: str = ""
) -> ChatRecord:
    if not record_id:
        raise Exception("Record id cannot be None")
    record = get_chat_record_by_id(session, record_id)

    record.predict_data = data

    result = ChatRecord(**record.model_dump())

    stmt = (
        update(ChatRecord)
        .where(and_(ChatRecord.id == record.id))
        .values(predict_data=record.predict_data)
    )

    session.execute(stmt)

    session.commit()

    return result


def save_sql_exec_data(session: SessionDep, record_id: int, data: str) -> ChatRecord:
    if not record_id:
        raise Exception("Record id cannot be None")
    record = get_chat_record_by_id(session, record_id)

    record.data = data

    result = ChatRecord(**record.model_dump())

    stmt = (
        update(ChatRecord)
        .where(and_(ChatRecord.id == record.id))
        .values(
            data=record.data,
        )
    )

    session.execute(stmt)

    session.commit()

    return result


def finish_record(session: SessionDep, record_id: int) -> ChatRecord:
    if not record_id:
        raise Exception("Record id cannot be None")
    record = get_chat_record_by_id(session, record_id)

    record.finish = True
    record.finish_time = datetime.datetime.now()

    result = ChatRecord(**record.model_dump())

    stmt = (
        update(ChatRecord)
        .where(and_(ChatRecord.id == record.id))
        .values(finish=record.finish, finish_time=record.finish_time)
    )

    session.execute(stmt)

    session.commit()

    return result


def get_old_questions(session: SessionDep, datasource: int):
    records = []
    if not datasource:
        return records
    stmt = (
        select(ChatRecord.question)
        .where(
            and_(
                ChatRecord.datasource == datasource,
                ChatRecord.question.isnot(None),
                ChatRecord.error.is_(None),
            )
        )
        .order_by(ChatRecord.create_time.desc())
        .limit(20)
    )
    result = session.execute(stmt)
    for r in result:
        records.append(r.question)
    return records


def submit_record_feedback(
    session: Any,
    *,
    chat_record_id: int,
    user_id: int,
    feedback: Optional[str],
) -> dict:
    """Persist one turn-level feedback fact independent of capture timing."""
    record = (
        session.exec(
            select(ChatRecord).where(ChatRecord.id == chat_record_id).with_for_update()
        )
        .scalars()
        .one_or_none()
    )
    if record is None or record.create_by != user_id:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="record not found")

    record.feedback = feedback
    record.feedback_revision = int(record.feedback_revision or 0) + 1
    session.add(record)
    session.commit()
    return {"feedback": feedback, "revision": record.feedback_revision}
