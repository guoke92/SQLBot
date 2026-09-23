"""Chat session bootstrap shell.

Domain atoms live in ``apps.chat.steps``; orchestration with SSE is owned by
``apps.chat.graphs``. This module only constructs the per-request context
(``LLMService``).

Table / datasource vector recall is **not** a constructor or API flag on this
class. Ranking is gated solely by ``settings.TABLE_EMBEDDING_ENABLED`` inside
``apps.chat.steps.schema`` / ``apps.chat.steps.datasource`` and the protocol
CRUD path. Do not re-add ``embedding`` to ``LLMService.__init__``.
"""

from __future__ import annotations

import os
import urllib.parse
import warnings
from typing import Any, List, Optional, Union

import orjson
import requests
from langchain.chat_models.base import BaseChatModel
from langchain_core.messages import BaseMessage
from sqlbot_xpack.config.model import SysArgModel
from sqlmodel import Session

from apps.ai_model.model_factory import LLMConfig
from apps.chat.constants import DYNAMIC_DS_TYPES
from apps.chat.curd.chat import (
    get_chat_brief_generate,
    get_last_execute_sql_error,
    list_generate_chart_logs,
    save_question,
)
from apps.chat.models.chat_model import Chat, ChatLog, ChatQuestion, ChatRecord
from apps.conversation.llm import get_chat_model, resolve_chat_llm_config
from apps.datasource.models.datasource import CoreDatasource
from apps.protocol import get_protocol
from apps.system.crud.assistant import AssistantOutDs, AssistantOutDsFactory
from apps.system.crud.parameter_manage import get_groups
from apps.system.crud.user import user_ws_list
from apps.system.schemas.system_schema import AssistantOutDsSchema
from common.core.config import settings
from common.core.deps import CurrentAssistant, CurrentUser
from common.error import SingleMessageError
from common.utils.locale import I18n, I18nHelper

warnings.filterwarnings("ignore")

i18n = I18n()


class LLMService:
    """Per-request chat context — not an orchestrator.

    Graphs compose domain steps from ``apps.chat.steps`` against this object.
    Schema/DS embedding policy lives in steps + settings, not on this instance.
    """

    ds: CoreDatasource
    chat_question: ChatQuestion
    oid: int
    record: ChatRecord
    config: LLMConfig
    llm: BaseChatModel
    chart_message: List[Union[BaseMessage, dict[str, Any]]]

    current_user: CurrentUser
    current_assistant: Optional[CurrentAssistant] = None
    out_ds_instance: Optional[AssistantOutDs] = None
    change_title: bool = False

    generate_chart_logs: List[ChatLog]
    current_logs: dict
    trans: I18nHelper = None

    last_execute_sql_error: str = None
    articles_number: int = 4

    enable_sql_row_limit: bool = settings.GENERATE_SQL_QUERY_LIMIT_ENABLED
    base_message_round_count_limit: int = settings.GENERATE_SQL_QUERY_HISTORY_ROUND_COUNT
    _protocol: Any = None

    def __init__(
        self,
        session: Session,
        current_user: CurrentUser,
        chat_question: ChatQuestion,
        current_assistant: Optional[CurrentAssistant] = None,
        no_reasoning: bool = False,
        config: LLMConfig = None,
    ):
        self.chart_message = []
        self.generate_chart_logs = []
        self.current_logs = {}
        self.current_user = current_user
        self.current_assistant = current_assistant

        self.table_name_list = []

        chat_question.lang = get_lang_name(current_user.language)
        self.trans = i18n(lang=current_user.language)

        chat_id = chat_question.chat_id
        chat: Chat | None = session.get(Chat, chat_id)
        if not chat:
            raise SingleMessageError(f"Chat with id {chat_id} not found")
        self.oid = chat.oid

        if self.oid and not current_assistant:
            w_list = user_ws_list(session, self.current_user.id)
            oid_list = [item.id for item in w_list]
            if int(self.oid) not in oid_list:
                raise SingleMessageError("Current user cannot not access this chat")
        if self.oid and current_assistant:
            if self.oid != self.current_user.oid:
                raise SingleMessageError("Current assistant user cannot not access this chat")

        self.current_user.oid = chat.oid
        ds: CoreDatasource | AssistantOutDsSchema | None = None
        if not chat.datasource and chat_question.datasource_id:
            _ds = session.get(CoreDatasource, chat_question.datasource_id)
            if _ds:
                if _ds.oid != self.oid:
                    raise SingleMessageError(
                        f"Datasource with id {chat_question.datasource_id} does not belong to current workspace"
                    )
                chat.datasource = _ds.id
                # Persist type key (e.g. "api"/"mysql"), not display name.
                chat.engine_type = _ds.type
                session.add(chat)
                session.flush()
                session.refresh(chat)
                session.commit()

        if chat.datasource:
            if current_assistant and current_assistant.type in DYNAMIC_DS_TYPES:
                self.out_ds_instance = AssistantOutDsFactory.get_instance(current_assistant)
                ds = self.out_ds_instance.get_ds(chat.datasource)
                if not ds:
                    raise SingleMessageError("No available datasource configuration found")
                _proto = get_protocol(ds.type)
                chat_question.engine = _proto.engine_display_name(ds) + _proto.server_version(ds)
            else:
                ds = session.get(CoreDatasource, chat.datasource)
                if not ds:
                    raise SingleMessageError("No available datasource configuration found")
                _proto = get_protocol(ds.type)
                chat_question.engine = _proto.engine_display_name(ds) + _proto.server_version(ds)

        self.generate_chart_logs = list_generate_chart_logs(session=session, chart_id=chat_id)

        self.change_title = not get_chat_brief_generate(session=session, chat_id=chat_id)

        self.ds = (
            ds if isinstance(ds, AssistantOutDsSchema) else CoreDatasource(**ds.model_dump())
        ) if ds else None
        self.chat_question = chat_question
        self.config = config
        if no_reasoning:
            # Recommend / no-think callers: force DeepSeek effort=none (and drop
            # Qwen Completions enable_thinking) instead of only stripping Qwen.
            from apps.ai_model.model_factory import with_reasoning_effort

            self.config = with_reasoning_effort(self.config, "none")
            if self.config.additional_params:
                extra = self.config.additional_params.get("extra_body")
                if isinstance(extra, dict) and "enable_thinking" in extra:
                    extra = dict(extra)
                    extra["enable_thinking"] = False
                    self.config.additional_params = {
                        **self.config.additional_params,
                        "extra_body": extra,
                    }

        self.chat_question.ai_modal_id = self.config.model_id
        self.chat_question.ai_modal_name = self.config.model_name

        self.llm = get_chat_model(self.config)

        last_execute_sql_error = get_last_execute_sql_error(session, self.chat_question.chat_id)
        if last_execute_sql_error:
            self.chat_question.error_msg = f"""<error-msg>
{last_execute_sql_error}
</error-msg>"""
        else:
            self.chat_question.error_msg = ""

    @classmethod
    async def create(cls, *args, **kwargs):
        reasoning_effort = kwargs.pop("reasoning_effort", None)
        config: LLMConfig = await resolve_chat_llm_config(
            args[0] if args else None,
            args[1] if len(args) > 1 else None,
            args[3] if len(args) > 3 else kwargs.get("current_assistant"),
            reasoning_effort,
        )
        instance = cls(*args, **kwargs, config=config)

        chat_params: list[SysArgModel] = await get_groups(args[0], "chat")
        for param in chat_params:
            if param.pkey == "chat.sqlbot_name":
                if param.pval.strip():
                    instance.chat_question.sqlbot_name = param.pval
            if param.pkey == "chat.limit_rows":
                if param.pval.lower().strip() == "true":
                    instance.enable_sql_row_limit = True
                else:
                    instance.enable_sql_row_limit = False
            if param.pkey == "chat.context_record_count":
                count_value = param.pval
                if count_value is None:
                    count_value = settings.GENERATE_SQL_QUERY_HISTORY_ROUND_COUNT
                count_value = int(count_value)
                if count_value < 0:
                    count_value = 0
                instance.base_message_round_count_limit = count_value
        return instance

    @property
    def protocol(self):
        """Resolve protocol for the *current* ds.

        Re-resolve when ds type changes so select-datasource cannot sticky-cache
        a stale protocol after self.ds is swapped mid-request.
        """
        if not self.ds:
            self._protocol = None
            return None
        ds_type = getattr(self.ds, "type", None)
        if self._protocol is None or getattr(self._protocol, "type_key", None) != ds_type:
            self._protocol = get_protocol(ds_type)
        return self._protocol

    @property
    def planning_question(self) -> str:
        """Return the enriched semantic text used only by intent reasoning."""
        return (
            self.chat_question.planning_question
            or self.chat_question.question
            or ""
        ).strip()

    def _original_intent_question(self) -> str:
        # Immutable question/clarification evidence is owned by EvidenceLedger;
        # the runtime prompt object keeps only the original visible question.
        return (self.chat_question.question or "").strip()

    @property
    def retrieval_question(self) -> str:
        """Compact stable text for terminology/example/schema vector recall."""
        return (
            self.chat_question.retrieval_question
            or self._original_intent_question()
        ).strip()

    @property
    def generation_question(self) -> str:
        """Original user request for SQL/API/chart generation and repair."""
        return (
            self.chat_question.generation_question
            or self._original_intent_question()
        ).strip()

    def init_record(self, session: Session, *, commit: bool = True) -> ChatRecord:
        # save_question returns a detached copy; keep the ORM instance away
        # from long-lived state so request-session commits cannot expire it.
        record = save_question(
            session=session,
            current_user=self.current_user,
            question=self.chat_question,
            commit=commit,
        )
        self.record = ChatRecord(**record.model_dump())
        return self.record

    def get_record(self) -> ChatRecord:
        return self.record

    def set_record(self, record: ChatRecord) -> None:
        # Graph workers outlive the request session: a session-bound record
        # expires on the API teardown commit and detaches on close, so node
        # attribute reads raise DetachedInstanceError. Bind a detached,
        # fully materialized copy (same discipline as recovery rehydration).
        self.record = ChatRecord(**record.model_dump())

    def set_articles_number(self, articles_number: int) -> None:
        self.articles_number = articles_number


def request_picture(chat_id: int, record_id: int, chart: dict, data: dict):
    file_name = f"c_{chat_id}_r_{record_id}"

    columns = chart.get("columns") if chart.get("columns") else []
    x = None
    y = None
    series = None
    multi_quota_fields = []
    multi_quota_name = None

    if chart.get("axis"):
        axis_data = chart.get("axis")
        x = axis_data.get("x")
        y = axis_data.get("y")
        series = axis_data.get("series")
        if axis_data.get("multi-quota") and "value" in axis_data.get("multi-quota"):
            multi_quota_fields = axis_data.get("multi-quota").get("value", [])
            multi_quota_name = axis_data.get("multi-quota").get("name")

    axis = []
    for v in columns:
        axis.append({"name": v.get("name"), "value": v.get("value")})
    if x:
        axis.append({"name": x.get("name"), "value": x.get("value"), "type": "x"})
    if y:
        y_list = y if isinstance(y, list) else [y]
        for y_item in y_list:
            if isinstance(y_item, dict) and "value" in y_item:
                y_obj = {
                    "name": y_item.get("name"),
                    "value": y_item.get("value"),
                    "type": "y",
                }
                if y_item.get("value") in multi_quota_fields:
                    y_obj["multi-quota"] = True
                axis.append(y_obj)
    if series and series.get("value"):
        axis.append({"name": series.get("name"), "value": series.get("value"), "type": "series"})
    if multi_quota_name:
        axis.append({"name": multi_quota_name, "value": multi_quota_name, "type": "other-info"})

    request_obj = {
        "path": os.path.join(settings.MCP_IMAGE_PATH, file_name),
        "type": chart.get("type"),
        "data": orjson.dumps(data.get("data") if data.get("data") else []).decode(),
        "axis": orjson.dumps(axis).decode(),
    }

    _error = None
    try:
        requests.post(
            url=settings.MCP_IMAGE_HOST,
            json=request_obj,
            timeout=settings.SERVER_IMAGE_TIMEOUT,
        )
    except Exception as e:
        _error = e

    request_path = urllib.parse.urljoin(settings.SERVER_IMAGE_HOST, f"{file_name}.png")
    return request_path, _error


def get_lang_name(lang: str):
    if not lang:
        return "简体中文"
    normalized = lang.lower()
    if normalized.startswith("zh-tw"):
        return "繁体中文"
    if normalized.startswith("en"):
        return "英文"
    if normalized.startswith("ko"):
        return "韩语"
    return "简体中文"


__all__ = [
    "LLMService",
    "request_picture",
    "get_lang_name",
]
