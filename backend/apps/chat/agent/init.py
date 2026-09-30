"""Turn bootstrap: record header, referenced-turn context, tools, transcript."""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping, Sequence
from typing import Any, Literal

from sqlalchemy import select

from apps.chat.agent.budget import empty_budget
from apps.chat.agent.context_spec import (
    context_fingerprint,
    recap_from_turn_answer,
)
from apps.chat.agent.workspace import SqlWorkspace
from apps.chat.agent_config import load_agent_config
from apps.chat.agent_knowledge import EXECUTION_ROUND_LIMIT, AgentKnowledgePlane
from apps.chat.graphs.turn_state import fail_turn_state, llm_service
from apps.chat.memory_slots import (
    MemorySlots,
    answer_has_executable_sql,
    hydrate_memory_slots_from_referenced_turns,
)
from apps.chat.models.chat_model import ChatRecord
from apps.chat.tools.registry import build_agent_tools
from apps.chat.turn_contracts import TurnRoute
from apps.conversation.graph_hooks import register_hydrate
from apps.conversation.messages import serialize_messages
from apps.conversation.models import ConversationRun
from apps.conversation.outcome import running_outcome
from apps.conversation.run_service import (
    load_prior_user_evidence,
    require_active_run,
)
from apps.conversation.runtime_context import attach_runtime
from apps.conversation.session import session_scope
from apps.conversation.sink import StreamSink
from apps.datasource.access import resolve_access_scope
from common.error import SingleMessageError
from common.utils.utils import SQLBotLogUtil

_REFERENCED_FIELD_LIMIT = 20
_REFERENCED_ROW_LIMIT = 3
_REFERENCED_CELL_WIDTH = 24
_TEMPORAL_RE = re.compile(r"^\d{4}[-/]\d{1,2}([-/]\d{1,2})?$")


def rehydrate_access_scope(session: Any, service: Any) -> Any:
    """Rebuild datasource access after a checkpoint resume."""
    if getattr(service, "ds", None) is None:
        from apps.chat.models.chat_model import Chat
        from apps.datasource.models.datasource import CoreDatasource

        rec = (
            service.get_record()
            if hasattr(service, "get_record")
            else getattr(service, "record", None)
        )
        ds_id = getattr(rec, "datasource", None) if rec else None
        if not ds_id and rec and getattr(rec, "chat_id", None):
            chat = session.get(Chat, rec.chat_id)
            if chat:
                ds_id = chat.datasource
        if ds_id:
            ds = session.get(CoreDatasource, ds_id)
            if ds:
                service.ds = ds
    if getattr(service, "ds", None) is None:
        return None
    from apps.chat.steps.datasource import validate_history_ds
    from apps.datasource.access import resolve_access_scope

    validate_history_ds(service, session)
    return resolve_access_scope(
        session,
        current_user=service.current_user,
        ds=service.ds,
    )


def hydrate_runtime(_run: ConversationRun, service: Any) -> dict[str, Any]:
    """Resume extras for the chat graph: tools, config, access scope."""
    with session_scope() as session:
        scope = rehydrate_access_scope(session, service)
    agent_config = load_agent_config()
    return {
        "access_scope": scope,
        "llm": service.llm,
        "agent_config": agent_config,
        "bound_tools": build_agent_tools(
            service, access_scope=scope, config=agent_config
        ),
    }


def prepare_record(state: Mapping[str, Any]) -> dict[str, Any]:
    """Emit SSE header and bind chat/record ids for this turn."""
    service = llm_service(state)
    sink = StreamSink.from_state(state)
    record = service.get_record()
    json_result: dict[str, Any] = {"success": True}

    try:
        sink.event({"type": "id", "id": record.id})
        sink.event({"type": "question", "question": record.question})
        sink.record_header(
            record_id=record.id,
            question=record.question,
            prefix=service.trans("i18n_chat.record_id_in_mcp"),
        )
        if sink.mode == "json":
            json_result["record_id"] = record.id

        return {
            **dict(state),
            "graph_key": "chat",
            "mode": "primary",
            "chat_id": record.chat_id,
            "record_id": record.id,
            "json_result": json_result,
            "turn_route": {},
            "source_datasets": [],
            "terminal_answer": {},
            "outcome": running_outcome(),
        }
    except Exception as exc:
        return {
            **fail_turn_state(state, record.id, exc),
            "graph_key": "chat",
            "mode": "primary",
            "chat_id": record.chat_id,
            "record_id": record.id,
            "json_result": json_result,
        }


def _dataset_capabilities(dataset: dict[str, Any]) -> dict[str, Any]:
    rows = [item for item in dataset.get("rows") or [] if isinstance(item, dict)]
    fields = [str(item) for item in dataset.get("fields") or []]
    temporal = False
    numeric = False
    for field in fields:
        values = [row.get(field) for row in rows if row.get(field) is not None]
        if not values:
            continue
        if any(
            isinstance(value, int | float) and not isinstance(value, bool)
            for value in values
        ):
            numeric = True
        if any(_TEMPORAL_RE.match(str(value).strip()) for value in values):
            temporal = True
    return {
        **dataset,
        "has_time_field": temporal,
        "has_numeric_measure": numeric,
        "valid_points": len(rows),
    }


def referenced_dataset_outline(dataset: dict[str, Any]) -> dict[str, Any]:
    def _clip_cell(value: Any) -> Any:
        text = str(value)
        return (
            text[:_REFERENCED_CELL_WIDTH]
            if len(text) > _REFERENCED_CELL_WIDTH
            else value
        )

    fields = [str(item) for item in dataset.get("fields") or []][
        :_REFERENCED_FIELD_LIMIT
    ]
    sample_rows = [
        {key: _clip_cell(value) for key, value in row.items() if key in fields}
        for row in (dataset.get("preview_rows") or dataset.get("rows") or [])[
            :_REFERENCED_ROW_LIMIT
        ]
        if isinstance(row, dict)
    ]
    return {
        "dataset_id": dataset.get("dataset_id"),
        "title": dataset.get("title") or "",
        "rev": dataset.get("rev") or "",
        "fields": fields,
        "row_count": dataset.get("row_count"),
        "sample_rows": sample_rows,
    }


def record_answer_datasets(record: ChatRecord) -> list[dict[str, Any]]:
    answer = record.answer if isinstance(record.answer, dict) else {}
    raw = answer.get("datasets") or answer.get("source_datasets") or []
    return [
        _dataset_capabilities(
            {
                **dict(item),
                "source_record_id": int(record.id or 0),
                "rows": list(item.get("preview_rows") or item.get("rows") or []),
                "preview_rows": list(
                    item.get("preview_rows") or item.get("rows") or []
                ),
            }
        )
        for item in raw
        if isinstance(item, dict) and item.get("status") in {"succeeded", "degraded"}
    ]


def sql_datasets_along_continue(
    record: Any,
    *,
    load: Callable[[int], Any],
    chat_id: int,
    user_id: int,
    datasource: int | None = None,
    max_hops: int = 8,
    seen: set[int] | None = None,
) -> list[dict[str, Any]]:
    """Walk continue parents until a turn that stored executable SQL datasets."""
    visited = seen if seen is not None else set()
    current: Any = record
    hops = 0
    while current is not None and hops < max_hops:
        hops += 1
        record_id = int(getattr(current, "id", 0) or 0)
        if record_id <= 0 or record_id in visited:
            break
        visited.add(record_id)
        if int(getattr(current, "chat_id", 0) or 0) != int(chat_id):
            break
        if int(getattr(current, "create_by", 0) or 0) != int(user_id):
            break
        current_ds = getattr(current, "datasource", None)
        if (
            datasource is not None
            and current_ds is not None
            and int(current_ds) != int(datasource)
        ):
            break
        datasets = record_answer_datasets(current)
        if any(str(item.get("sql") or "").strip() for item in datasets):
            return datasets
        parents = [
            int(item)
            for item in (getattr(current, "reference_record_ids", None) or [])
            if int(item) > 0
        ]
        current = None
        for parent_id in parents:
            parent = load(parent_id)
            if parent is not None:
                current = parent
                break
    return []


def assemble_turn_context(state: Mapping[str, Any]) -> dict[str, Any]:
    """Select durable history/results before any datasource or model work."""
    try:
        route = TurnRoute.model_validate(state.get("turn_route") or {})
        source_datasets: list[dict[str, Any]] = []
        referenced_turns: list[dict[str, Any]] = []
        prior_user_evidence: list[dict[str, Any]] = []
        with session_scope() as session:
            run = require_active_run(session, str(state["run_id"]))
            current = session.get(ChatRecord, run.chat_record_id)
            if current is None:
                raise LookupError("Conversation turn not found")
            prior_user_evidence = load_prior_user_evidence(
                session,
                chat_id=int(current.chat_id),
                user_id=int(run.user_id),
                reference_record_ids=route.reference_record_ids,
            )
            seen_spine: set[int] = set()
            current_ds = (
                int(current.datasource) if current.datasource is not None else None
            )
            for record_id in route.reference_record_ids:
                referenced = session.get(ChatRecord, int(record_id))
                if (
                    referenced is None
                    or int(referenced.create_by or 0) != int(run.user_id)
                    or int(referenced.chat_id) != int(current.chat_id)
                ):
                    raise SingleMessageError(
                        "Referenced conversation result is unavailable"
                    )
                if (
                    current.datasource is not None
                    and referenced.datasource is not None
                    and int(current.datasource) != int(referenced.datasource)
                ):
                    raise SingleMessageError(
                        "Cannot continue a query across different datasources"
                    )
                spine_datasets = sql_datasets_along_continue(
                    referenced,
                    load=lambda rid: session.get(ChatRecord, int(rid)),
                    chat_id=int(current.chat_id),
                    user_id=int(run.user_id),
                    datasource=current_ds,
                    seen=seen_spine,
                )
                source_datasets.extend(spine_datasets)
                latest_run = (
                    session.exec(
                        select(ConversationRun)
                        .where(
                            ConversationRun.chat_record_id == int(referenced.id),
                        )
                        .order_by(ConversationRun.attempt_index.desc())
                        .limit(1)
                    )
                    .scalars()
                    .one_or_none()
                )
                answer = (
                    referenced.answer if isinstance(referenced.answer, dict) else {}
                )
                recap = recap_from_turn_answer(answer)
                knowledge_refs = recap.knowledge_refs
                outlines = [
                    referenced_dataset_outline(item)
                    for item in record_answer_datasets(referenced)
                ]
                if not outlines:
                    for ds in recap.datasets:
                        if ds.dataset_id or ds.rev:
                            outlines.append(
                                referenced_dataset_outline(ds.model_dump(mode="json"))
                            )
                referenced_turns.append(
                    {
                        "record_id": referenced.id,
                        "question": referenced.question,
                        "turn_kind": referenced.turn_kind,
                        "answer_status": recap.status,
                        "answer_summary": recap.content,
                        "run_status": latest_run.status
                        if latest_run is not None
                        else None,
                        "datasets": outlines,
                        "confirmed_calibers": recap.confirmed_calibers,
                        "assumptions": recap.assumptions,
                        "knowledge_refs": knowledge_refs,
                        "revision_ids": list(knowledge_refs.get("page_keys") or []),
                    }
                )
            business_now_text = run.business_now.isoformat()
            business_timezone = run.timezone
            fingerprint = context_fingerprint(
                {
                    "message": current.question,
                    "route": route.model_dump(mode="json"),
                    "references": referenced_turns,
                    "prior_user_evidence": prior_user_evidence,
                    "dataset_ids": [item.get("dataset_id") for item in source_datasets],
                    "business_now": business_now_text,
                    "timezone": business_timezone,
                }
            )
            run.context_fingerprint = fingerprint
            session.add(run)
            session.commit()
        return {
            **dict(state),
            "referenced_turns": referenced_turns,
            "prior_user_evidence": prior_user_evidence,
            "source_datasets": source_datasets,
            "context_fingerprint": fingerprint,
            "business_now": business_now_text,
            "timezone": business_timezone,
            "reference_record_ids": list(route.reference_record_ids),
        }
    except Exception as exc:
        return fail_turn_state(state, state.get("record_id"), exc)


def resolve_continue_reference_ids(
    *,
    chat_id: int | None,
    user_id: int | None,
    exclude_record_id: int | None = None,
    explicit_ids: Sequence[int] | None = None,
) -> list[int]:
    """Prefer explicit refs; otherwise attach the latest succeeded query in-chat."""
    explicit = [int(item) for item in (explicit_ids or []) if int(item) > 0]
    if explicit:
        return explicit[:3]
    if chat_id is None or user_id is None:
        return []

    with session_scope() as session:
        rows = (
            session.exec(
                select(ChatRecord)
                .where(
                    ChatRecord.chat_id == int(chat_id),
                    ChatRecord.create_by == int(user_id),
                    ChatRecord.question.is_not(None),
                )
                .order_by(ChatRecord.id.desc())
                .limit(20)
            )
            .scalars()
            .all()
        )
        for row in rows:
            if exclude_record_id is not None and int(row.id) == int(exclude_record_id):
                continue
            answer = row.answer if isinstance(row.answer, dict) else None
            if answer_has_executable_sql(answer):
                return [int(row.id)]
    return []


def ensure_agent_turn_route(
    state: Mapping[str, Any],
    *,
    reference_record_ids: Sequence[int],
    task_kind: str = "query",
) -> dict[str, Any]:
    """Build a valid TurnRoute for assemble_turn_context."""
    refs = tuple(int(item) for item in reference_record_ids[:3] if int(item) > 0)
    existing = (
        state.get("turn_route") if isinstance(state.get("turn_route"), dict) else {}
    )
    kind = str(
        existing.get("task_kind") or state.get("route_hint") or task_kind or "query"
    )
    if kind not in {"query", "analysis", "prediction", "unsupported"}:
        kind = "query"
    if kind == "analysis" and not refs:
        kind = "query"
    relation: Literal["independent", "continue", "revise"] = (
        "continue" if refs else "independent"
    )
    return TurnRoute(
        task_kind=kind,  # type: ignore[arg-type]
        relation=relation,
        reference_record_ids=refs,
        source="deterministic",
        confidence=0.9 if refs else 1.0,
    ).model_dump(mode="json")


def init_agent_turn(state: Mapping[str, Any]) -> dict[str, Any]:
    """Prepare messages, bound tools, memory slots, and runtime context once."""
    base_state = prepare_record(dict(state))
    if base_state.get("error"):
        return base_state

    service = llm_service(base_state)
    run_id = str(base_state["run_id"])
    record_id = base_state.get("record_id")
    question_text = str(getattr(service.chat_question, "question", "") or "")
    chat_id = base_state.get("chat_id") or getattr(
        getattr(service, "record", None), "chat_id", None
    )
    user_id = getattr(getattr(service, "current_user", None), "id", None)

    ref_ids = resolve_continue_reference_ids(
        chat_id=int(chat_id) if chat_id is not None else None,
        user_id=int(user_id) if user_id is not None else None,
        exclude_record_id=int(record_id) if record_id is not None else None,
        explicit_ids=base_state.get("reference_record_ids") or [],
    )
    turn_route = ensure_agent_turn_route(base_state, reference_record_ids=ref_ids)
    base_state["reference_record_ids"] = list(
        turn_route.get("reference_record_ids") or []
    )
    base_state["turn_route"] = turn_route

    if base_state["reference_record_ids"]:
        ctx_state = assemble_turn_context(base_state)
        if not ctx_state.get("error"):
            base_state.update(ctx_state)
            try:
                with session_scope() as session:
                    record = (
                        session.get(ChatRecord, int(record_id))
                        if record_id is not None
                        else None
                    )
                    if record is not None:
                        record.relation = str(turn_route.get("relation") or "continue")
                        record.reference_record_ids = list(
                            base_state["reference_record_ids"]
                        )
                        session.add(record)
                        session.commit()
            except Exception as exc:
                SQLBotLogUtil.warning(
                    f"Failed to persist continue refs on record {record_id}: {exc}"
                )
        else:
            SQLBotLogUtil.warning(
                f"assemble_turn_context failed for agent turn {record_id}: "
                f"{ctx_state.get('error')}"
            )

    access_scope = None
    try:
        if not getattr(service, "ds", None):
            with session_scope() as session:
                from apps.datasource.models.datasource import CoreDatasource

                chat_obj = session.get(ChatRecord, record_id) if record_id else None
                ds_id = getattr(chat_obj, "datasource", None) if chat_obj else None
                if not ds_id and getattr(service, "record", None):
                    ds_id = getattr(service.record, "datasource", None)
                if ds_id:
                    ds = session.get(CoreDatasource, ds_id)
                    if ds:
                        service.ds = ds

        if getattr(service, "ds", None):
            with session_scope() as session:
                access_scope = resolve_access_scope(
                    session,
                    current_user=service.current_user,
                    ds=service.ds,
                )
    except Exception as exc:
        SQLBotLogUtil.warning(
            f"Failed to resolve access_scope in init_agent_turn: {exc}"
        )

    raw_slots = base_state.get("memory_slots") or {}
    memory_slots = MemorySlots.model_validate(raw_slots) if raw_slots else MemorySlots()
    referenced = list(base_state.get("referenced_turns") or [])
    memory_slots = hydrate_memory_slots_from_referenced_turns(memory_slots, referenced)
    workspace = SqlWorkspace()
    ds_id = getattr(getattr(service, "ds", None), "id", None)
    dialect = getattr(getattr(service, "ds", None), "type", None)
    for dataset in base_state.get("source_datasets") or []:
        if isinstance(dataset, Mapping):
            workspace.inherit_dataset(
                dataset,
                ds_id=int(ds_id) if ds_id is not None else None,
                dialect=str(dialect) if dialect else None,
            )
    if workspace.current:
        memory_slots.current_rev = workspace.current

    from apps.chat.steps.schema_outline import render_schema_outline
    from apps.chat.steps.wiki_recall import _store

    plane = AgentKnowledgePlane.from_dump(base_state.get("knowledge_plane"))
    plane.question = plane.question or question_text
    try:
        ds = getattr(service, "ds", None)
        ds_id = getattr(ds, "id", None)
        store = _store(int(ds_id)) if ds_id is not None else None
        with session_scope() as session:
            plane.schema_outline = render_schema_outline(
                ds=ds,
                store=store,
                session=session,
            )
    except Exception as exc:
        SQLBotLogUtil.warning("schema outline render failed: %s", exc)

    agent_config = load_agent_config()
    tools = build_agent_tools(service, access_scope=access_scope, config=agent_config)
    attach_runtime(
        run_id,
        llm=service.llm,
        bound_tools=tools,
        access_scope=access_scope,
        llm_service=service,
        knowledge_plane=plane.to_dump(),
        agent_config=agent_config,
        memory_slots=memory_slots.model_dump(),
        sql_workspace=workspace.model_dump(mode="json"),
    )

    history: list[Any] = []
    stored_folds: list[dict[str, Any]] = []
    if chat_id is not None:
        try:
            from apps.chat.agent.context_spec import (
                load_agent_transcript,
                load_fold_ledger,
            )

            with session_scope() as session:
                history = load_agent_transcript(session, int(chat_id))
                stored_folds = load_fold_ledger(session, int(chat_id))
        except Exception as exc:
            SQLBotLogUtil.warning(
                f"Failed to load agent_transcript for chat {chat_id}: {exc}"
            )
            history = []

    from apps.chat.agent.context_spec import build_continued_messages, save_fold_meta

    initial_messages, turn_message_start, fold_meta = build_continued_messages(
        history=history,
        question=question_text,
        knowledge_plane=plane,
        memory_slots=memory_slots.model_dump(),
        referenced_turns=referenced,
        workspace=workspace,
        stored_folds=stored_folds,
        state=base_state,
        config=agent_config,
    )
    if fold_meta and chat_id is not None:
        try:
            with session_scope() as session:
                save_fold_meta(session, int(chat_id), fold_meta)
                session.commit()
        except Exception as exc:
            SQLBotLogUtil.warning(
                f"Failed to persist fold meta for chat {chat_id}: {exc}"
            )
        try:
            from apps.chat.agent.audit import emit_compact_span

            emit_compact_span(
                record_id=record_id,
                run_id=run_id,
                sink=StreamSink.from_state(base_state),
                folds=list(fold_meta),
                ai_modal_id=base_state.get("ai_modal_id"),
                ai_modal_name=base_state.get("ai_modal_name"),
            )
        except Exception as exc:
            SQLBotLogUtil.warning(f"compact span skipped: {exc}")

    loop_budget = empty_budget(config=agent_config)
    return {
        **base_state,
        "messages": serialize_messages(initial_messages),
        "turn_message_start": turn_message_start,
        "loop_budget": loop_budget.model_dump(mode="json"),
        "sql_workspace": workspace.model_dump(mode="json"),
        "batch_signals": {},
        "tool_rounds": 0,
        "tool_round_limit": agent_config.param(
            "execution_round_limit", EXECUTION_ROUND_LIMIT
        ),
        "knowledge_plane": plane.to_dump(),
        "memory_slots": memory_slots.model_dump(),
        "outcome": running_outcome(),
    }


register_hydrate("chat", hydrate_runtime)
