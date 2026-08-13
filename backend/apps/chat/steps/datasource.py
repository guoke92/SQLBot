"""Select / bind datasource step (domain atom; graph owns SSE tokens).

DS vector recall is gated solely by ``settings.TABLE_EMBEDDING_ENABLED``
(same deployment kill-switch as table embedding). No per-request API flag,
and no ``LLMService.embedding`` field.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import orjson
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from sqlalchemy import and_, select
from sqlmodel import Session

from apps.chat.constants import DYNAMIC_DS_TYPES
from apps.chat.curd.chat import save_select_datasource_answer
from apps.chat.models.chat_model import Chat, SystemPromptMessage
from apps.chat.steps.observability import AuditSpanHandle
from apps.chat.steps.stream import process_stream
from apps.datasource.embedding.ds_embedding import get_ds_embedding
from apps.datasource.models.datasource import CoreDatasource
from apps.protocol import get_protocol
from apps.system.crud.assistant import get_assistant_ds
from common.core.config import settings
from common.error import SingleMessageError
from common.utils.json_utils import extract_nested_json

# Re-export for ``from apps.chat.steps.datasource import DYNAMIC_DS_TYPES``.
__all__ = ["DYNAMIC_DS_TYPES", "select_datasource", "validate_history_ds"]


def select_datasource(
    llm_service: Any,
    session: Session,
    *,
    audit_span: AuditSpanHandle | None = None,
) -> Iterator[dict[str, Any]]:
    """Choose datasource for unbound chats; yield LLM tokens when multi-DS selection runs.

    Does **not** re-run terminology / training / prompts — those are graph match nodes.
    Multi-DS ranking uses ``get_ds_embedding`` only when ``TABLE_EMBEDDING_ENABLED``.
    """
    datasource_msg: list[BaseMessage | dict[str, Any]] = [
        SystemPromptMessage(llm_service.chat_question.datasource_sys_question())
    ]
    if llm_service.current_assistant and llm_service.current_assistant.type != 4:
        ds_list = get_assistant_ds(session=session, llm_service=llm_service)
    else:
        stmt = select(CoreDatasource.id, CoreDatasource.name, CoreDatasource.description).where(
            and_(CoreDatasource.oid == llm_service.oid)
        )
        ds_list = [
            {"id": ds.id, "name": ds.name, "description": ds.description}
            for ds in session.exec(stmt)
        ]
    if not ds_list:
        raise SingleMessageError("No available datasource configuration found")

    ignore_auto_select = bool(ds_list and len(ds_list) == 1)
    if audit_span is not None:
        audit_span["local_operation"] = ignore_auto_select
    full_thinking_text = ""
    full_text = ""
    ds: dict[str, Any] | None = None

    if not ignore_auto_select:
        if settings.TABLE_EMBEDDING_ENABLED and (
            not llm_service.current_assistant
            or (llm_service.current_assistant and llm_service.current_assistant.type != 1)
        ):
            ds_list = get_ds_embedding(
                session,
                ds_list,
                llm_service.out_ds_instance,
                llm_service.retrieval_question,
                llm_service.current_assistant,
            )

        ds_list_dict = list(ds_list)
        datasource_msg.append(
            HumanMessage(
                llm_service.chat_question.datasource_user_question(
                    orjson.dumps(ds_list_dict).decode()
                )
            )
        )
        token_usage: dict[str, Any] = {}
        for chunk in process_stream(llm_service.llm.stream(datasource_msg), token_usage):
            if chunk.get("content"):
                full_text += chunk.get("content")
            if chunk.get("reasoning_content"):
                full_thinking_text += chunk.get("reasoning_content")
            yield chunk
        datasource_msg.append(AIMessage(full_text))
        if audit_span is not None:
            audit_span.set_model_context(datasource_msg)
            audit_span.set_usage(token_usage)
            audit_span["reasoning_content"] = full_thinking_text
        json_str = extract_nested_json(full_text)
        if json_str is None:
            raise SingleMessageError(f"Cannot parse datasource from answer: {full_text}")
        ds = orjson.loads(json_str)

    error: Exception | None = None
    datasource_id: int | None = None
    engine_type: str | None = None
    try:
        data: dict = ds_list[0] if ignore_auto_select else ds  # type: ignore[assignment]
        if data.get("id") and data.get("id") != 0:
            datasource_id = data["id"]
            chat = session.get(Chat, llm_service.record.chat_id)
            chat.datasource = datasource_id
            if (
                llm_service.current_assistant
                and llm_service.current_assistant.type in DYNAMIC_DS_TYPES
            ):
                picked = llm_service.out_ds_instance.get_ds(data["id"])
                llm_service.ds = picked
                proto = get_protocol(picked.type)
                llm_service.chat_question.engine = (
                    proto.engine_display_name(picked) + proto.server_version(picked)
                )
                engine_type = picked.type
                chat.engine_type = picked.type
            else:
                picked_core = session.get(CoreDatasource, datasource_id)
                if not picked_core:
                    datasource_id = None
                    raise SingleMessageError(
                        f"Datasource configuration with id {datasource_id} not found"
                    )
                llm_service.ds = CoreDatasource(**picked_core.model_dump())
                proto = get_protocol(picked_core.type)
                llm_service.chat_question.engine = (
                    proto.engine_display_name(picked_core) + proto.server_version(picked_core)
                )
                engine_type = picked_core.type
                chat.engine_type = picked_core.type
            with session.begin_nested():
                try:
                    session.add(chat)
                    session.flush()
                    session.refresh(chat)
                    session.commit()
                except Exception as e:
                    session.rollback()
                    raise e
        elif data.get("fail"):
            raise SingleMessageError(data["fail"])
        else:
            raise SingleMessageError("No available datasource configuration found")
    except Exception as e:
        error = e

    if not ignore_auto_select and not settings.TABLE_EMBEDDING_ENABLED:
        llm_service.record = save_select_datasource_answer(
            session=session,
            record_id=llm_service.record.id,
            answer=orjson.dumps({"content": full_text}).decode(),
            datasource=datasource_id,
            engine_type=engine_type,
        )

    if error:
        raise error


def validate_history_ds(llm_service: Any, session: Session) -> None:
    """Ensure chat-bound datasource is still reachable for this user/assistant."""
    ds = llm_service.ds
    if not llm_service.current_assistant or llm_service.current_assistant.type == 4:
        try:
            current_ds = session.get(CoreDatasource, ds.id)
            if not current_ds:
                raise SingleMessageError("chat.ds_is_invalid")
        except Exception:
            raise SingleMessageError("chat.ds_is_invalid")
    else:
        try:
            ds_list: list[dict] = get_assistant_ds(session=session, llm_service=llm_service)
            if not any(item.get("id") == ds.id for item in ds_list):
                typ = llm_service.current_assistant.type
                msg = (
                    "[please check ds list and public ds list]"
                    if typ == 0
                    else "[please check ds api]"
                )
                raise SingleMessageError(msg)
        except Exception as e:
            raise SingleMessageError(f"ds is invalid [{str(e)}]")
