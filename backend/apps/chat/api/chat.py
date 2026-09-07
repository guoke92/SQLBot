import asyncio
import io
import traceback
from time import monotonic

import pandas as pd
from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import StreamingResponse
from sqlalchemy import and_, select
from starlette.responses import JSONResponse

from apps.chat.answer_payload import (
    build_failed_answer_payload,
    normalize_answer_payload,
)
from apps.chat.curd.chat import (
    create_chat,
    delete_chat_with_user,
    get_chart_data_with_user,
    get_chart_data_with_user_live,
    get_chat_chart_config,
    get_chat_chart_data,
    get_chat_log_history,
    get_chat_predict_data,
    get_chat_predict_data_with_user,
    get_chat_record_by_id,
    get_chat_with_records,
    get_chat_with_records_with_data,
    list_chats,
    list_recent_questions,
    rename_chat_with_user,
)
from apps.chat.curd.debug_bundle import build_chat_debug_bundle
from apps.chat.models.chat_model import (
    Chat,
    ChatFinishStep,
    ChatInfo,
    ChatQuestion,
    ChatRecord,
    CreateChat,
    QuickCommand,
    RenameChat,
    SimpleChat,
)
from apps.chat.result_data import (
    excel_rows_from_dataset,
    format_json_data,
    format_json_list_data,
)

# Graph registration is handled by each FastAPI process lifespan; no
# import-time side effects are needed here. submit_graph is the sole runtime
# entry.
from apps.chat.task.llm import LLMService
from apps.conversation.events import emit
from apps.conversation.models import ConversationRun
from apps.conversation.run_service import (
    CorrectionRequest,
    CreateRunRequest,
    ResumeRequest,
    consume_interrupt,
    correct_interrupt_answer,
    create_run,
    finalize_run,
    get_owned_run,
    run_events_after,
    run_snapshot,
)
from apps.conversation.process_timeline import (
    load_dataset_rows,
    localize_process_event,
    project_process_timeline,
)
from apps.conversation.runtime import submit_graph
from apps.conversation.runtime_context import attach_runtime
from apps.conversation.session import session_scope
from apps.conversation.sink import resolve_sink, sink_error_chunks
from apps.swagger.i18n import PLACEHOLDER_PREFIX
from apps.system.schemas.permission import SqlbotPermission, require_permissions
from common.audit.models.log_model import OperationModules, OperationType
from common.audit.schemas.logger_decorator import LogConfig, system_log
from common.core.config import settings
from common.core.deps import CurrentAssistant, CurrentUser, SessionDep, Trans
from common.utils.command_utils import parse_quick_command
from common.utils.data_format import DataFormat

router = APIRouter(tags=["Data Q&A"], prefix="/chat")


def _user_id(user: object) -> int:
    return int(user.id)


async def _launch_run(
    session: SessionDep,
    current_user: CurrentUser,
    current_assistant: CurrentAssistant,
    request: CreateRunRequest,
) -> ConversationRun:
    chat = session.get(Chat, request.chat_id)
    if chat is None or int(chat.create_by) != _user_id(current_user):
        raise HTTPException(status_code=404, detail="Chat not found")
    if request.datasource_id is not None:
        chat.datasource = request.datasource_id
        session.add(chat)
        session.commit()
    graph_key = "config" if (chat.chat_type or "chat").strip() == "config" else "chat"
    if graph_key == "config":
        from apps.config_assistant.nodes import initialize_config_state

        state = await initialize_config_state(
            session,
            user=current_user,
            chat_id=request.chat_id,
            question=request.question,
            base_state={"sink": "sse", "in_chat": True, "stream": True},
        )
        run = session.get(ConversationRun, str(state["run_id"]))
        if run is None:
            raise RuntimeError("Config run was not created")
    else:
        regenerate_record = (
            session.get(ChatRecord, request.regenerate_record_id)
            if request.regenerate_record_id is not None
            else None
        )
        if regenerate_record is not None and (
            int(regenerate_record.chat_id) != int(request.chat_id)
            or int(regenerate_record.create_by) != _user_id(current_user)
        ):
            raise HTTPException(status_code=404, detail="Turn not found")
        question = ChatQuestion(
            chat_id=request.chat_id,
            question=(
                str(regenerate_record.question)
                if regenerate_record is not None
                else request.question
            ),
        )
        service = await LLMService.create(
            session, current_user, question, current_assistant
        )
        if regenerate_record is not None:
            service.set_record(regenerate_record)
        else:
            service.init_record(session=session, commit=False)
            service.record.reference_record_ids = request.reference_record_ids
            if request.reference_record_ids:
                service.record.relation = "continue"
        run = create_run(
            session,
            record=service.record,
            graph_key="chat",
            user_id=_user_id(current_user),
            oid=int(getattr(current_user, "oid", None) or 1),
            assistant_id=(
                int(current_assistant.id)
                if current_assistant is not None
                and getattr(current_assistant, "id", None) is not None
                else None
            ),
        )
        attach_runtime(run.run_id, llm_service=service)
        explicit_refs = (
            list(regenerate_record.reference_record_ids or [])
            if regenerate_record is not None
            else list(request.reference_record_ids or [])
        )
        route_hint = (
            regenerate_record.turn_kind
            if regenerate_record is not None
            else request.route_hint
        )
        preset_route = None
        if regenerate_record is not None:
            preset_route = {
                "task_kind": regenerate_record.turn_kind or "query",
                "relation": regenerate_record.relation or "independent",
                "reference_record_ids": explicit_refs,
                "source": "hint",
                "confidence": 1.0,
            }
        elif explicit_refs:
            preset_route = {
                "task_kind": route_hint or "query",
                "relation": "continue",
                "reference_record_ids": explicit_refs,
                "source": "hint",
                "confidence": 1.0,
            }
        state = {
            "run_id": run.run_id,
            "record_id": service.record.id,
            "chat_id": request.chat_id,
            "sink": "sse",
            "graph_key": "chat",
            "mode": "primary",
            "route_hint": route_hint,
            "reference_record_ids": explicit_refs,
            "preset_route": preset_route,
            "turn_route": preset_route or {},
            "finish_step": request.finish_step
            or int(ChatFinishStep.GENERATE_CHART.value),
            "return_img": request.return_img,
        }
    runner = submit_graph(graph_key, state)
    runner.detach()
    return run


@router.post("/runs", summary="Create and start a durable conversation run")
@require_permissions(
    permission=SqlbotPermission(type="chat", keyExpression="request.chat_id")
)
async def create_conversation_run(
    session: SessionDep,
    current_user: CurrentUser,
    request: CreateRunRequest,
    current_assistant: CurrentAssistant,
):
    run = await _launch_run(session, current_user, current_assistant, request)
    session.refresh(run)
    return run_snapshot(session, run)


@router.post(
    "/runs/{run_id}/interrupts/{interrupt_id}/correct",
    summary="Correct an earlier clarification answer and replan the same run",
)
async def correct_conversation_answer(
    session: SessionDep,
    current_user: CurrentUser,
    run_id: str,
    interrupt_id: str,
    request: CorrectionRequest,
):
    try:
        run = get_owned_run(session, run_id=run_id, user_id=_user_id(current_user))
        correction, should_resume = correct_interrupt_answer(
            session,
            run=run,
            interrupt_id=interrupt_id,
            request=request,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if should_resume:
        submit_graph(
            run.graph_key,
            {
                "run_id": run.run_id,
                "record_id": run.chat_record_id,
                "sink": "sse",
                "graph_key": run.graph_key,
                "__resume__": {
                    "type": "correction",
                    "evidence_id": correction.evidence_id,
                },
            },
        ).detach()
    session.refresh(run)
    return run_snapshot(session, run)


@router.get(
    "/runs/{run_id}",
    summary="Get the canonical run snapshot",
    operation_id="get_conversation_run",
)
async def get_conversation_run(
    session: SessionDep,
    current_user: CurrentUser,
    run_id: str,
):
    try:
        run = get_owned_run(session, run_id=run_id, user_id=_user_id(current_user))
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return run_snapshot(session, run)


@router.get("/runs/{run_id}/events", summary="Subscribe to persisted run events")
async def conversation_run_events(
    session: SessionDep,
    current_user: CurrentUser,
    trans: Trans,
    run_id: str,
    cursor: int = 0,
):
    get_owned_run(session, run_id=run_id, user_id=_user_id(current_user))

    async def event_stream():
        nonlocal cursor
        last_status_push = 0.0
        while True:
            with session_scope() as event_session:
                run = event_session.get(ConversationRun, run_id)
                if run is None:
                    return
                events = run_events_after(event_session, run_id=run_id, cursor=cursor)
                status = run.status
                latest_cursor = int(run.event_cursor or 0)
                status_payload = {
                    "type": "run_status",
                    "status": run.status,
                    "current_node": run.current_node,
                    "event_cursor": latest_cursor,
                    "dispatch_attempts": run.dispatch_attempts,
                    "update_time": run.update_time.isoformat(),
                    "started_at": run.started_at.isoformat()
                    if run.started_at
                    else None,
                    "completed_at": (
                        run.completed_at.isoformat() if run.completed_at else None
                    ),
                }
            for item in events:
                cursor = int(item.get("cursor") or cursor)
                yield emit(localize_process_event(item, trans))
            if cursor < latest_cursor:
                continue
            now = monotonic()
            if now - last_status_push >= max(1, settings.CONVERSATION_STATUS_PUSH_SEC):
                yield emit(status_payload)
                yield ": heartbeat\n\n"
                last_status_push = now
            if status in {
                "awaiting_input",
                "succeeded",
                "degraded",
                "failed",
                "cancelled",
            }:
                return
            await asyncio.sleep(0.25)

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post(
    "/runs/{run_id}/interrupts/{interrupt_id}/resume",
    summary="Resume the same run with immutable clarification evidence",
    operation_id="resume_conversation_run",
)
async def resume_conversation_run(
    session: SessionDep,
    current_user: CurrentUser,
    run_id: str,
    interrupt_id: str,
    request: ResumeRequest,
):
    try:
        run = get_owned_run(session, run_id=run_id, user_id=_user_id(current_user))
        consumed, should_resume = consume_interrupt(
            session,
            run=run,
            interrupt_id=interrupt_id,
            request=request,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if should_resume:
        runner = submit_graph(
            run.graph_key,
            {
                "run_id": run.run_id,
                "record_id": run.chat_record_id,
                "sink": "sse",
                "graph_key": run.graph_key,
                "__resume__": consumed.answers or [],
            },
        )
        runner.detach()
    session.refresh(run)
    return run_snapshot(session, run)


@router.post("/runs/{run_id}/cancel", summary="Cancel a conversation run")
async def cancel_conversation_run(
    session: SessionDep,
    current_user: CurrentUser,
    run_id: str,
):
    try:
        run = get_owned_run(session, run_id=run_id, user_id=_user_id(current_user))
        run = finalize_run(
            session,
            run_id=run.run_id,
            status="cancelled",
            current_node="cancel",
            record_snapshot={"terminal": True},
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return run_snapshot(session, run)


@router.get(
    "/list", response_model=list[Chat], summary=f"{PLACEHOLDER_PREFIX}get_chat_list"
)
async def chats(session: SessionDep, current_user: CurrentUser):
    return list_chats(session, current_user)


@router.get(
    "/{chart_id}", response_model=ChatInfo, summary=f"{PLACEHOLDER_PREFIX}get_chat"
)
async def get_chat(
    session: SessionDep,
    current_user: CurrentUser,
    chart_id: int,
    current_assistant: CurrentAssistant,
    trans: Trans,
):
    def inner():
        return get_chat_with_records(
            chart_id=chart_id,
            session=session,
            current_user=current_user,
            current_assistant=current_assistant,
            trans=trans,
        )

    return await asyncio.to_thread(inner)


@router.get(
    "/{chart_id}/with_data",
    response_model=ChatInfo,
    summary=f"{PLACEHOLDER_PREFIX}get_chat_with_data",
)
async def get_chat_with_data(
    session: SessionDep,
    current_user: CurrentUser,
    chart_id: int,
    current_assistant: CurrentAssistant,
):
    def inner():
        return get_chat_with_records_with_data(
            chart_id=chart_id,
            session=session,
            current_user=current_user,
            current_assistant=current_assistant,
        )

    return await asyncio.to_thread(inner)


@router.get(
    "/{chart_id}/debug_bundle",
    summary="Export a full debug bundle for one chat (owner or admin)",
)
async def chat_debug_bundle(
    session: SessionDep,
    current_user: CurrentUser,
    chart_id: int,
    max_rows: int = 50,
    include_raw_logs: bool = True,
):
    """One-shot dump for offline triage: records, outcome, intent, logs, schema."""

    def inner():
        return build_chat_debug_bundle(
            session,
            current_user,
            chart_id,
            max_rows=max_rows if max_rows >= 0 else None,
            include_raw_logs=include_raw_logs,
        )

    try:
        return await asyncio.to_thread(inner)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/record/{chat_record_id}/data", summary=f"{PLACEHOLDER_PREFIX}get_chart_data"
)
async def chat_record_data(
    session: SessionDep, current_user: CurrentUser, chat_record_id: int
):
    def inner():
        data = get_chart_data_with_user(
            chat_record_id=chat_record_id, session=session, current_user=current_user
        )
        try:
            return normalize_answer_payload(
                data,
                normalize_data=format_json_data,
            )
        except ValueError:
            record = get_chat_record_by_id(session, chat_record_id)
            if record and record.error:
                return build_failed_answer_payload(record.error)
            raise

    return await asyncio.to_thread(inner)


@router.get(
    "/record/{chat_record_id}/data_live",
    summary=f"{PLACEHOLDER_PREFIX}get_chart_data_live",
)
async def chat_record_data_live(
    session: SessionDep, current_user: CurrentUser, chat_record_id: int
):
    def inner():
        data = get_chart_data_with_user_live(
            chat_record_id=chat_record_id, session=session, current_user=current_user
        )
        return format_json_data(data)

    return await asyncio.to_thread(inner)


@router.get(
    "/record/{chat_record_id}/predict_data",
    summary=f"{PLACEHOLDER_PREFIX}get_chart_predict_data",
)
async def chat_predict_data(
    session: SessionDep, current_user: CurrentUser, chat_record_id: int
):
    def inner():
        data = get_chat_predict_data_with_user(
            chat_record_id=chat_record_id, session=session, current_user=current_user
        )
        return format_json_list_data(data)

    return await asyncio.to_thread(inner)


@router.get(
    "/record/{chat_record_id}/log", summary=f"{PLACEHOLDER_PREFIX}get_record_log"
)
async def chat_record_log(
    session: SessionDep,
    current_user: CurrentUser,
    chat_record_id: int,
    run_id: str | None = None,
):
    def inner():
        return get_chat_log_history(
            session, chat_record_id, current_user, run_id=run_id
        )

    return await asyncio.to_thread(inner)


@router.get(
    "/record/{chat_record_id}/timeline",
    summary="Process timeline (compact or detail view)",
)
async def chat_record_timeline(
    session: SessionDep,
    current_user: CurrentUser,
    trans: Trans,
    chat_record_id: int,
    view: str = "compact",
    run_id: str | None = None,
):
    record = session.get(ChatRecord, chat_record_id)
    if record is None or int(record.create_by) != _user_id(current_user):
        raise HTTPException(status_code=404, detail="Turn not found")
    resolved_view = "detail" if view == "detail" else "compact"

    def inner():
        return project_process_timeline(
            session,
            record_id=chat_record_id,
            run_id=run_id,
            view=resolved_view,  # type: ignore[arg-type]
            trans=trans,
        )

    return await asyncio.to_thread(inner)


@router.get(
    "/record/{chat_record_id}/datasets/{dataset_id}/rows",
    summary="Paginated result_dataset rows",
)
async def chat_record_dataset_rows(
    session: SessionDep,
    current_user: CurrentUser,
    chat_record_id: int,
    dataset_id: str,
    offset: int = 0,
    limit: int = 1000,
):
    try:
        return load_dataset_rows(
            session,
            record_id=chat_record_id,
            dataset_id=dataset_id,
            offset=offset,
            limit=limit,
            user_id=_user_id(current_user),
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.get(
    "/record/{chat_record_id}/usage", summary=f"{PLACEHOLDER_PREFIX}get_record_usage"
)
async def chat_record_usage(
    session: SessionDep, current_user: CurrentUser, chat_record_id: int
):
    def inner():
        return get_chat_log_history(session, chat_record_id, current_user, True)

    return await asyncio.to_thread(inner)


@router.post(
    "/record/{chat_record_id}/feedback",
    summary="Submit user feedback (up/down) for a chat record",
)
async def chat_record_feedback(
    session: SessionDep,
    current_user: CurrentUser,
    chat_record_id: int,
    body: dict,
):
    from apps.chat.curd.chat import submit_record_feedback

    def inner():
        feedback = body.get("feedback")
        if feedback not in ("up", "down", None):
            raise HTTPException(
                status_code=400, detail="feedback must be 'up', 'down' or null"
            )
        return submit_record_feedback(
            session,
            chat_record_id=chat_record_id,
            user_id=current_user.id,
            feedback=feedback,
        )

    return await asyncio.to_thread(inner)


@router.post("/rename", response_model=str, summary=f"{PLACEHOLDER_PREFIX}rename_chat")
@system_log(
    LogConfig(
        operation_type=OperationType.UPDATE,
        module=OperationModules.CHAT,
        resource_id_expr="chat.id",
    )
)
async def rename(session: SessionDep, current_user: CurrentUser, chat: RenameChat):
    try:
        return rename_chat_with_user(
            session=session, current_user=current_user, rename_object=chat
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{chart_id}", response_model=str, summary=f"{PLACEHOLDER_PREFIX}delete_chat"
)
@system_log(
    LogConfig(
        operation_type=OperationType.DELETE,
        module=OperationModules.CHAT,
        resource_id_expr="chart_id",
        remark_expr="chat.brief",
    )
)
async def delete(
    session: SessionDep, current_user: CurrentUser, chart_id: int, chat: SimpleChat
):
    try:
        return delete_chat_with_user(
            session=session, current_user=current_user, chart_id=chart_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/start", response_model=ChatInfo, summary=f"{PLACEHOLDER_PREFIX}start_chat"
)
@require_permissions(
    permission=SqlbotPermission(type="ds", keyExpression="create_chat_obj.datasource")
)
@system_log(
    LogConfig(
        operation_type=OperationType.CREATE,
        module=OperationModules.CHAT,
        result_id_expr="id",
    )
)
async def start_chat_session(
    session: SessionDep, current_user: CurrentUser, create_chat_obj: CreateChat
):
    try:
        # config chats need no datasource; NLQ still requires one via create_chat.
        require_ds = (create_chat_obj.chat_type or "chat") != "config"
        return create_chat(
            session, current_user, create_chat_obj, require_datasource=require_ds
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/assistant/start",
    response_model=ChatInfo,
    summary=f"{PLACEHOLDER_PREFIX}assistant_start_chat",
)
@system_log(
    LogConfig(
        operation_type=OperationType.CREATE,
        module=OperationModules.CHAT,
        result_id_expr="id",
    )
)
async def start_assistant_chat_session(
    session: SessionDep,
    current_user: CurrentUser,
    current_assistant: CurrentAssistant,
    create_chat_obj: CreateChat = CreateChat(origin=2),
):
    try:
        return create_chat(
            session,
            current_user,
            create_chat_obj,
            create_chat_obj and create_chat_obj.datasource,
            current_assistant,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/recommend_questions/{chat_record_id}",
    summary=f"{PLACEHOLDER_PREFIX}ask_recommend_questions",
)
async def ask_recommend_questions(
    session: SessionDep,
    current_user: CurrentUser,
    chat_record_id: int,
    current_assistant: CurrentAssistant,
    articles_number: int | None = 4,
):
    def _return_empty():
        yield emit({"content": "[]", "type": "recommended_question"})

    try:
        record = get_chat_record_by_id(session, chat_record_id)

        if not record:
            return StreamingResponse(_return_empty(), media_type="text/event-stream")
        run = (
            session.get(ConversationRun, record.active_run_id)
            if record.active_run_id
            else None
        )
        if run is not None and run.status not in {"succeeded", "degraded"}:
            return StreamingResponse(_return_empty(), media_type="text/event-stream")

        request_question = ChatQuestion(
            chat_id=record.chat_id, question=record.question if record.question else ""
        )

        llm_service = await LLMService.create(
            session, current_user, request_question, current_assistant, True
        )
        llm_service.set_record(record)
        llm_service.set_articles_number(articles_number)
        runner = submit_graph(
            "recommend",
            {
                "llm_service": llm_service,
                "record": record,
                "sink": "sse",
                "graph_key": "recommend",
                "mode": "side",
            },
        )
    except Exception as e:
        traceback.print_exc()

        def _err(_e: Exception):
            yield from sink_error_chunks({"sink": "sse"}, str(_e))

        return StreamingResponse(_err(e), media_type="text/event-stream")

    return StreamingResponse(runner.await_result(), media_type="text/event-stream")


@router.get(
    "/recent_questions/{datasource_id}",
    response_model=list[str],
    summary=f"{PLACEHOLDER_PREFIX}get_recommend_questions",
)
# @require_permissions(permission=SqlbotPermission(type='ds', keyExpression="datasource_id"))
async def recommend_questions(
    session: SessionDep,
    current_user: CurrentUser,
    datasource_id: int = Path(..., description=f"{PLACEHOLDER_PREFIX}ds_id"),
):
    return list_recent_questions(
        session=session, current_user=current_user, datasource_id=datasource_id
    )


def find_base_question(record_id: int, session: SessionDep):
    record = session.get(ChatRecord, record_id)
    if record is None:
        raise Exception("Cannot find base chat record")
    return record.question


async def question_answer_inner(
    session: SessionDep,
    current_user: CurrentUser,
    request_question: ChatQuestion,
    current_assistant: CurrentAssistant | None = None,
    in_chat: bool = True,
    stream: bool = True,
    finish_step: ChatFinishStep = ChatFinishStep.GENERATE_CHART,
    return_img: bool = True,
):
    sink_mode = resolve_sink(in_chat=in_chat, stream=stream)
    try:
        command, text_before_command, record_id, warning_info = parse_quick_command(
            request_question.question
        )
        if command:
            # todo 对话界面下，暂不支持分析和预测，需要改造前端
            if in_chat and (
                command == QuickCommand.ANALYSIS or command == QuickCommand.PREDICT_DATA
            ):
                raise Exception(f"Command: {command.value} temporary not supported")

            if record_id is not None:
                source_record = session.get(ChatRecord, record_id)
                if source_record is None:
                    raise Exception(f"Record id: {record_id} does not exist")
                if source_record.chat_id != request_question.chat_id:
                    raise Exception(
                        f"Record id: {record_id} does not belong to this chat"
                    )
                if source_record.create_by != current_user.id:
                    raise Exception(f"Record id: {record_id} is not owned by the user")
                if source_record.first_chat:
                    raise Exception(
                        f"Record id: {record_id} does not support this operation"
                    )
                rec_id = int(source_record.id)

            else:  # get last record id
                source_record = (
                    session.exec(
                        select(ChatRecord)
                        .where(
                            and_(
                                ChatRecord.chat_id == request_question.chat_id,
                                ChatRecord.create_by == current_user.id,
                                ChatRecord.first_chat.is_(False),
                            )
                        )
                        .order_by(ChatRecord.create_time.desc())
                        .limit(1)
                    )
                    .scalars()
                    .one_or_none()
                )
                if source_record is None:
                    raise Exception("You have not ask any question")
                rec_id = int(source_record.id)

            base_question_text = find_base_question(rec_id, session)
            text_before_command = (
                text_before_command
                + ("\n" if text_before_command else "")
                + base_question_text
            )

            if command == QuickCommand.REGENERATE:
                request_question.question = text_before_command
                request_question.regenerate_record_id = rec_id
                return await stream_sql(
                    session,
                    current_user,
                    request_question,
                    current_assistant,
                    in_chat,
                    stream,
                    finish_step,
                    return_img=return_img,
                )

            elif command == QuickCommand.ANALYSIS:
                return await analysis_or_predict(
                    session,
                    current_user,
                    rec_id,
                    "analysis",
                    current_assistant,
                    in_chat,
                    stream,
                )

            elif command == QuickCommand.PREDICT_DATA:
                return await analysis_or_predict(
                    session,
                    current_user,
                    rec_id,
                    "predict",
                    current_assistant,
                    in_chat,
                    stream,
                )
            else:
                raise Exception(f"Unknown command: {command.value}")
        else:
            return await stream_sql(
                session,
                current_user,
                request_question,
                current_assistant,
                in_chat,
                stream,
                finish_step,
                return_img=return_img,
            )
    except Exception as e:
        traceback.print_exc()

        if stream:

            def _err(_e: Exception):
                yield from sink_error_chunks(
                    {"sink": sink_mode, "in_chat": in_chat, "stream": stream},
                    str(_e),
                )

            return StreamingResponse(_err(e), media_type="text/event-stream")
        else:
            return JSONResponse(
                content={"message": str(e)},
                status_code=500,
            )


async def stream_sql(
    session: SessionDep,
    current_user: CurrentUser,
    request_question: ChatQuestion,
    current_assistant: CurrentAssistant | None = None,
    in_chat: bool = True,
    stream: bool = True,
    finish_step: ChatFinishStep = ChatFinishStep.GENERATE_CHART,
    return_img: bool = True,
):
    sink_mode = resolve_sink(in_chat=in_chat, stream=stream)
    try:
        chat = session.get(Chat, request_question.chat_id)
        if not chat:
            raise Exception(f"Chat with id {request_question.chat_id} not found")
        chat_type = (chat.chat_type or "chat").strip() or "chat"
        # Route truth source = registry key from chat_type (primary scenarios only).
        if chat_type == "config":
            from apps.config_assistant.nodes import initialize_config_state

            graph_key = "config"
            state = await initialize_config_state(
                session,
                user=current_user,
                chat_id=int(request_question.chat_id),
                question=request_question.question or "",
                base_state={
                    "sink": sink_mode,
                    "in_chat": in_chat,
                    "stream": stream,
                },
            )
        else:
            graph_key = "chat"
            llm_service = await LLMService.create(
                session, current_user, request_question, current_assistant
            )
            if request_question.regenerate_record_id:
                regenerate_record = session.get(
                    ChatRecord, int(request_question.regenerate_record_id)
                )
                if (
                    regenerate_record is None
                    or int(regenerate_record.create_by or 0) != _user_id(current_user)
                    or int(regenerate_record.chat_id) != int(request_question.chat_id)
                ):
                    raise Exception("Turn to regenerate was not found")
                llm_service.set_record(regenerate_record)
            else:
                llm_service.init_record(session=session, commit=False)
            run = create_run(
                session,
                record=llm_service.record,
                graph_key="chat",
                user_id=_user_id(current_user),
                oid=int(getattr(current_user, "oid", None) or 1),
                assistant_id=(
                    int(current_assistant.id)
                    if current_assistant is not None
                    and getattr(current_assistant, "id", None) is not None
                    else None
                ),
            )
            attach_runtime(run.run_id, llm_service=llm_service)
            state = {
                "run_id": run.run_id,
                "record_id": llm_service.record.id,
                "sink": sink_mode,
                "graph_key": graph_key,
                "mode": "primary",
                "chat_id": request_question.chat_id,
                "route_hint": "query",
                "reference_record_ids": list(
                    llm_service.record.reference_record_ids or []
                ),
                "finish_step": int(
                    finish_step.value if hasattr(finish_step, "value") else finish_step
                ),
                "return_img": return_img,
            }
        # Sole runtime entry — no run_task dual path.
        runner = submit_graph(graph_key, state)
    except Exception as e:
        traceback.print_exc()

        if stream:

            def _err(_e: Exception):
                yield from sink_error_chunks(
                    {"sink": sink_mode, "in_chat": in_chat, "stream": stream},
                    str(_e),
                )

            return StreamingResponse(_err(e), media_type="text/event-stream")
        else:
            return JSONResponse(
                content={"message": str(e)},
                status_code=500,
            )
    if stream:
        return StreamingResponse(runner.await_result(), media_type="text/event-stream")
    else:
        res = runner.await_result()
        raw_data = {}
        for chunk in res:
            if chunk:
                raw_data = chunk
        status_code = 200
        if not raw_data.get("success"):
            status_code = 500

        return JSONResponse(
            content=raw_data,
            status_code=status_code,
        )


@router.post(
    "/record/{chat_record_id}/{action_type}",
    summary=f"{PLACEHOLDER_PREFIX}analysis_or_predict",
)
async def analysis_or_predict_question(
    session: SessionDep,
    current_user: CurrentUser,
    current_assistant: CurrentAssistant,
    chat_record_id: int,
    action_type: str = Path(
        ..., description=f"{PLACEHOLDER_PREFIX}analysis_or_predict_action_type"
    ),
):
    return await analysis_or_predict(
        session, current_user, chat_record_id, action_type, current_assistant
    )


async def analysis_or_predict(
    session: SessionDep,
    current_user: CurrentUser,
    chat_record_id: int,
    action_type: str,
    current_assistant: CurrentAssistant,
    in_chat: bool = True,
    stream: bool = True,
):
    sink_mode = resolve_sink(in_chat=in_chat, stream=stream)
    try:
        if action_type != "analysis" and action_type != "predict":
            raise Exception(f"Type {action_type} Not Found")
        base_record = session.get(ChatRecord, chat_record_id)
        if not base_record or int(base_record.create_by) != _user_id(current_user):
            raise Exception(f"Chat record with id {chat_record_id} not found")

        answer = base_record.answer if isinstance(base_record.answer, dict) else {}
        if not (answer.get("datasets") or answer.get("source_datasets")):
            raise Exception(
                f"Chat record with id {chat_record_id} has no usable result dataset"
            )

        task_kind = "analysis" if action_type == "analysis" else "prediction"
        request_question = ChatQuestion(
            chat_id=base_record.chat_id,
            question=(
                "请分析上一条查询结果"
                if task_kind == "analysis"
                else "请基于上一条查询结果进行预测"
            ),
        )

        llm_service = await LLMService.create(
            session, current_user, request_question, current_assistant
        )
        llm_service.init_record(session=session, commit=False)
        record = llm_service.record
        record.turn_kind = task_kind
        record.relation = "continue"
        record.reference_record_ids = [int(base_record.id)]
        session.add(record)
        session.flush()
        run = create_run(
            session,
            record=record,
            graph_key="chat",
            user_id=_user_id(current_user),
            oid=int(getattr(current_user, "oid", None) or 1),
            assistant_id=(
                int(current_assistant.id)
                if current_assistant is not None
                and getattr(current_assistant, "id", None) is not None
                else None
            ),
        )
        llm_service.set_record(record)
        attach_runtime(run.run_id, llm_service=llm_service)
        # Compatibility endpoint only adapts the old button shape into the
        # one durable chat graph. It does not create an analysis/predict graph.
        runner = submit_graph(
            "chat",
            {
                "run_id": run.run_id,
                "record_id": record.id,
                "sink": sink_mode,
                "graph_key": "chat",
                "mode": "follow_up",
                "chat_id": base_record.chat_id,
                "route_hint": task_kind,
                "reference_record_ids": [int(base_record.id)],
            },
        )
    except Exception as e:
        traceback.print_exc()
        if stream:

            def _err(_e: Exception):
                yield from sink_error_chunks(
                    {"sink": sink_mode, "in_chat": in_chat, "stream": stream},
                    str(_e),
                )

            return StreamingResponse(_err(e), media_type="text/event-stream")
        else:
            return JSONResponse(
                content={"message": str(e)},
                status_code=500,
            )
    if stream:
        return StreamingResponse(runner.await_result(), media_type="text/event-stream")
    else:
        res = runner.await_result()
        raw_data = {}
        for chunk in res:
            if chunk:
                raw_data = chunk
        status_code = 200
        if not raw_data.get("success"):
            status_code = 500

        return JSONResponse(
            content=raw_data,
            status_code=status_code,
        )


@router.get(
    "/record/{chat_record_id}/excel/export/{chat_id}",
    summary=f"{PLACEHOLDER_PREFIX}export_chart_data",
)
@system_log(
    LogConfig(
        operation_type=OperationType.EXPORT,
        module=OperationModules.CHAT,
        resource_id_expr="chat_id",
    )
)
async def export_excel(
    session: SessionDep,
    current_user: CurrentUser,
    chat_record_id: int,
    chat_id: int,
    trans: Trans,
):
    chat_record = session.get(ChatRecord, chat_record_id)
    if not chat_record:
        raise HTTPException(
            status_code=500, detail=f"ChatRecord with id {chat_record_id} not found"
        )
    if chat_record.create_by != current_user.id:
        raise HTTPException(
            status_code=500,
            detail=f"ChatRecord with id {chat_record_id} not Owned by the current user",
        )
    is_predict_data = bool(
        isinstance(chat_record.answer, dict)
        and chat_record.answer.get("kind") == "prediction"
    )

    _origin_data = format_json_data(
        get_chat_chart_data(chat_record_id=chat_record_id, session=session)
    )

    _base_field = _origin_data.get("fields")
    _data = _origin_data.get("data")

    if not _data:
        raise HTTPException(
            status_code=500, detail=trans("i18n_excel_export.data_is_empty")
        )

    chart_info = get_chat_chart_config(session, chat_record_id)

    _predict_data = []
    if is_predict_data:
        _predict_data = format_json_list_data(
            get_chat_predict_data(chat_record_id=chat_record_id, session=session)
        )

    data_list = DataFormat.convert_large_numbers_in_object_array(
        obj_array=_data + _predict_data, int_threshold=1e11
    )
    md_data, fields_list = excel_rows_from_dataset(
        chart=chart_info,
        fields=_base_field,
        rows=data_list,
    )
    if not fields_list:
        raise HTTPException(
            status_code=500, detail=trans("i18n_excel_export.data_is_empty")
        )

    def inner():
        df = pd.DataFrame(md_data, columns=fields_list)
        buffer = io.BytesIO()
        with pd.ExcelWriter(
            buffer,
            engine="xlsxwriter",
            engine_kwargs={"options": {"strings_to_numbers": False}},
        ) as writer:
            df.to_excel(writer, sheet_name="Sheet1", index=False)
        buffer.seek(0)
        return io.BytesIO(buffer.getvalue())

    result = await asyncio.to_thread(inner)
    return StreamingResponse(
        result,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
