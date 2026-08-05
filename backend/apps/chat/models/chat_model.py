from datetime import datetime
from enum import Enum
from typing import List, Optional, Any, Union

from fastapi import Body
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from pydantic import BaseModel
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    Text,
)
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import SQLModel, Field

from apps.template.filter.generator import get_permissions_template
from apps.template.generate_analysis.generator import get_analysis_template
from apps.template.generate_dynamic.generator import get_dynamic_template
from apps.template.generate_guess_question.generator import get_guess_question_template
from apps.template.generate_predict.generator import get_predict_template
from apps.template.select_datasource.generator import get_datasource_template
from common.core.branding import APP_DISPLAY_NAME


def enum_values(enum_class: type[Enum]) -> list:
    """Get values for enum."""
    return [status.value for status in enum_class]


class TypeEnum(Enum):
    CHAT = "0"


#     TODO other usage

class OperationEnum(Enum):
    GENERATE_QUERY = '0'
    GENERATE_CHART = '1'
    ANALYSIS = '2'
    PREDICT_DATA = '3'
    GENERATE_RECOMMENDED_QUESTIONS = '4'
    GENERATE_QUERY_WITH_PERMISSIONS = '5'
    CHOOSE_DATASOURCE = '6'
    GENERATE_DYNAMIC_QUERY = '7'
    CHOOSE_TABLE = '8'
    FILTER_TERMS = '9'
    FILTER_QUERY_EXAMPLE = '10'
    FILTER_CUSTOM_PROMPT = '11'
    EXECUTE_QUERY = '12'
    GENERATE_PICTURE = '13'
    # Shared tool-agent process channel
    TOOL_CALL = '14'
    AGENT_STEP = '15'
    # Agentic NLQ graph spans (process channel; execution-details UI)
    GROUND_ENTITIES = '16'
    CLARIFY_INTENT = '17'
    DECIDE_NEXT = '18'


class ChatFinishStep(Enum):
    GENERATE_QUERY = 1
    QUERY_DATA = 2
    GENERATE_CHART = 3


class QuickCommand(Enum):
    REGENERATE = '/regenerate'
    ANALYSIS = '/analysis'
    PREDICT_DATA = '/predict'


#     TODO choose table / check connection / generate description

class ChatLog(SQLModel, table=True):
    __tablename__ = "chat_log"
    id: Optional[int] = Field(sa_column=Column(BigInteger, Identity(always=True), primary_key=True))
    type: TypeEnum = Field(
        sa_column=Column(SQLAlchemyEnum(TypeEnum, native_enum=False, values_callable=enum_values, length=3)))
    operate: OperationEnum = Field(
        sa_column=Column(SQLAlchemyEnum(OperationEnum, native_enum=False, values_callable=enum_values, length=3)))
    pid: Optional[int] = Field(sa_column=Column(BigInteger, nullable=True))
    ai_modal_id: Optional[int] = Field(sa_column=Column(BigInteger))
    base_modal: Optional[str] = Field(max_length=255)
    messages: Optional[list[dict]] = Field(sa_column=Column(JSONB))
    reasoning_content: Optional[str | None] = Field(sa_column=Column(Text, nullable=True))
    start_time: datetime = Field(sa_column=Column(DateTime(timezone=False), nullable=True))
    finish_time: datetime = Field(sa_column=Column(DateTime(timezone=False), nullable=True))
    token_usage: Optional[dict | None | int] = Field(sa_column=Column(JSONB))
    local_operation: bool = Field(default=False)
    error: bool = Field(default=False)


class Chat(SQLModel, table=True):
    __tablename__ = "chat"
    id: Optional[int] = Field(sa_column=Column(BigInteger, Identity(always=True), primary_key=True))
    oid: Optional[int] = Field(sa_column=Column(BigInteger, nullable=True, default=1))
    create_time: datetime = Field(sa_column=Column(DateTime(timezone=False), nullable=True))
    create_by: int = Field(sa_column=Column(BigInteger, nullable=True))
    brief: str = Field(max_length=64, nullable=True)
    chat_type: str = Field(max_length=20, default="chat")  # chat | config
    datasource: int = Field(sa_column=Column(BigInteger, nullable=True))
    engine_type: str = Field(max_length=64)
    origin: Optional[int] = Field(
        sa_column=Column(Integer, nullable=False, default=0))  # 0: default, 1: mcp, 2: assistant
    brief_generate: bool = Field(default=False)
    recommended_question_answer: str = Field(sa_column=Column(Text, nullable=True))
    recommended_question: str = Field(sa_column=Column(Text, nullable=True))
    recommended_generate: bool = Field(default=False)


class ChatRecord(SQLModel, table=True):
    __tablename__ = "chat_record"
    id: Optional[int] = Field(sa_column=Column(BigInteger, Identity(always=True), primary_key=True))
    chat_id: int = Field(sa_column=Column(BigInteger, nullable=False))
    ai_modal_id: Optional[int] = Field(sa_column=Column(BigInteger))
    first_chat: bool = Field(sa_column=Column(Boolean, nullable=True, default=False))
    create_time: datetime = Field(sa_column=Column(DateTime(timezone=False), nullable=True))
    finish_time: datetime = Field(sa_column=Column(DateTime(timezone=False), nullable=True))
    create_by: int = Field(sa_column=Column(BigInteger, nullable=True))
    datasource: int = Field(sa_column=Column(BigInteger, nullable=True))
    engine_type: str = Field(max_length=64, nullable=True)
    question: str = Field(sa_column=Column(Text, nullable=True))
    sql_answer: str = Field(sa_column=Column(Text, nullable=True))
    sql: str = Field(sa_column=Column(Text, nullable=True))
    sql_exec_result: str = Field(sa_column=Column(Text, nullable=True))
    data: str = Field(sa_column=Column(Text, nullable=True))
    chart_answer: str = Field(sa_column=Column(Text, nullable=True))
    chart: str = Field(sa_column=Column(Text, nullable=True))
    analysis: str = Field(sa_column=Column(Text, nullable=True))
    predict: str = Field(sa_column=Column(Text, nullable=True))
    predict_data: str = Field(sa_column=Column(Text, nullable=True))
    recommended_question_answer: str = Field(sa_column=Column(Text, nullable=True))
    recommended_question: str = Field(sa_column=Column(Text, nullable=True))
    datasource_select_answer: str = Field(sa_column=Column(Text, nullable=True))
    finish: bool = Field(sa_column=Column(Boolean, nullable=True, default=False))
    error: str = Field(sa_column=Column(Text, nullable=True))
    analysis_record_id: int = Field(sa_column=Column(BigInteger, nullable=True))
    predict_record_id: int = Field(sa_column=Column(BigInteger, nullable=True))
    regenerate_record_id: int = Field(sa_column=Column(BigInteger, nullable=True))
    re_exec: Optional[str] = Field(sa_column=Column(Text, nullable=True))
    intent_context: Optional[dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSONB, nullable=True),
    )
    clarification_parent_id: Optional[int] = Field(
        default=None,
        sa_column=Column(
            BigInteger,
            ForeignKey("chat_record.id", ondelete="CASCADE"),
            nullable=True,
        ),
    )


class ChatRecordResult(BaseModel):
    id: Optional[int] = None
    chat_id: Optional[int] = None
    ai_modal_id: Optional[int] = None
    first_chat: bool = False
    create_time: Optional[datetime] = None
    finish_time: Optional[datetime] = None
    question: Optional[str] = None
    sql_answer: Optional[str] = None
    sql: Optional[str] = None
    datasource: Optional[int] = None
    engine_type: Optional[str] = None
    data: Optional[str] = None
    chart_answer: Optional[str] = None
    chart: Optional[str] = None
    analysis: Optional[str] = None
    predict: Optional[str] = None
    predict_data: Optional[str] = None
    recommended_question: Optional[str] = None
    datasource_select_answer: Optional[str] = None
    finish: Optional[bool] = None
    error: Optional[str] = None
    analysis_record_id: Optional[int] = None
    predict_record_id: Optional[int] = None
    regenerate_record_id: Optional[int] = None
    sql_reasoning_content: Optional[str] = None
    chart_reasoning_content: Optional[str] = None
    analysis_reasoning_content: Optional[str] = None
    predict_reasoning_content: Optional[str] = None
    intent_reasoning_content: Optional[str] = None
    duration: Optional[float] = None  # 耗时字段（单位：秒）
    total_tokens: Optional[int] = None  # token总消耗
    re_exec: Optional[str] = None
    intent_context: Optional[dict[str, Any]] = None
    clarification_parent_id: Optional[int] = None


class CreateChat(BaseModel):
    id: int = None
    question: str = None
    datasource: int = None
    origin: Optional[int] = 0  # 0是页面上，mcp是1，小助手是2
    chat_type: str = "chat"  # chat | config


class RenameChat(BaseModel):
    id: int = None
    brief: str = ''
    brief_generate: bool = True

class SimpleChat(BaseModel):
    id: int = None
    brief: str = ''

class ChatInfo(BaseModel):
    id: Optional[int] = None
    create_time: datetime = None
    create_by: int = None
    brief: str = ''
    chat_type: str = "chat"
    datasource: Optional[int] = None
    engine_type: str = ''
    ds_type: str = ''
    datasource_name: str = ''
    datasource_exists: bool = True
    recommended_question: Optional[str] = None
    recommended_generate: Optional[bool] = False
    records: List[ChatRecord | dict] = []


class ChatLogHistoryItem(BaseModel):
    id: Optional[int] = None  # chat_log.id — stable UI key
    start_time: Optional[datetime] = None
    finish_time: Optional[datetime] = None
    duration: Optional[float] = None  # 耗时字段（单位：秒）
    total_tokens: Optional[int] = None  # token总消耗
    operate: Optional[str] = None
    local_operation: Optional[bool] = False
    message: Optional[str | dict | list] = None
    error: Optional[bool] = False


class ChatLogHistory(BaseModel):
    start_time: Optional[datetime] = None
    finish_time: Optional[datetime] = None
    duration: Optional[float] = None  # 耗时字段（单位：秒）
    total_tokens: Optional[int] = None  # token总消耗
    steps: List[ChatLogHistoryItem | dict] = []


class AiModelQuestion(BaseModel):
    question: str = None
    ai_modal_id: int = None
    ai_modal_name: str = None  # Specific model name
    engine: str = ""
    db_schema: str = ""
    sql: str = ""
    rule: str = ""
    fields: str = ""
    data: str = ""
    lang: str = "简体中文"
    filter: str = []
    sub_query: Optional[list[dict]] = None
    terminologies: str = ""
    data_training: str = ""
    custom_prompt: str = ""
    error_msg: str = ""
    regenerate_record_id: Optional[int] = None
    sample_data: str = ""
    sqlbot_name: str = APP_DISPLAY_NAME
    # Filled by NLQ generate_queries (PlanContext); empty outside agentic path.
    plan_context: str = ""
    # Request-local projections of one persisted clause-oriented contract.
    # ``question`` remains the user-visible message persisted on ChatRecord.
    # Retrieval stays compact; generation keeps the original user request;
    # the frozen contract is rendered once through ``plan_context``.
    planning_question: str = ""
    retrieval_question: str = ""
    generation_question: str = ""

    def analysis_sys_question(self):
        return get_analysis_template()['system'].format(lang=self.lang, terminologies=self.terminologies,
                                                        custom_prompt=self.custom_prompt, sqlbot_name=self.sqlbot_name)

    def analysis_user_question(self):
        return get_analysis_template()['user'].format(fields=self.fields, data=self.data)

    def predict_sys_question(self):
        return get_predict_template()['system'].format(lang=self.lang, custom_prompt=self.custom_prompt,
                                                       sqlbot_name=self.sqlbot_name)

    def predict_user_question(self):
        return get_predict_template()['user'].format(fields=self.fields, data=self.data)

    def datasource_sys_question(self):
        return get_datasource_template()['system'].format(lang=self.lang, sqlbot_name=self.sqlbot_name)

    def datasource_user_question(self, datasource_list: str = "[]"):
        return get_datasource_template()['user'].format(
            lang=self.lang,
            question=self.generation_question or self.question,
            data=datasource_list,
        )

    def guess_sys_question(self, articles_number: int = 4):
        return get_guess_question_template()['system'].format(lang=self.lang, articles_number=articles_number,
                                                              sqlbot_name=self.sqlbot_name)

    def guess_user_question(self, old_questions: str = "[]"):
        return get_guess_question_template()['user'].format(
            question=self.generation_question or self.question,
            schema=self.db_schema,
            old_questions=old_questions,
        )

    def filter_sys_question(self):
        return get_permissions_template()['system'].format(lang=self.lang, engine=self.engine,
                                                           sqlbot_name=self.sqlbot_name)

    def filter_user_question(self):
        return get_permissions_template()['user'].format(sql=self.sql, filter=self.filter)

    def dynamic_sys_question(self):
        return get_dynamic_template()['system'].format(lang=self.lang, engine=self.engine, sqlbot_name=self.sqlbot_name)

    def dynamic_user_question(self):
        return get_dynamic_template()['user'].format(sql=self.sql, sub_query=self.sub_query)


class ChatQuestion(AiModelQuestion):
    chat_id: int
    datasource_id: Optional[int] = None
    clarification_for_record_id: Optional[int] = None
    clarification_answers: list[dict[str, Any]] = Field(default_factory=list)
    intent_context: Optional[dict[str, Any]] = None


class ChatMcp(ChatQuestion):
    token: str


class McpDs(BaseModel):
    token: str = Body(description='用户token')
    oid: Optional[str] = Body(description='组织ID，如果不传则为最后一次登录AI智能问数时所使用的组织ID', default=None)


class ChatToken(BaseModel):
    username: str = Body(description='用户名')
    password: str = Body(description='密码')


class ChatStart(BaseModel):
    username: str = Body(description='用户名', default=None)
    password: str = Body(description='密码', default=None)
    token: str = Body(description='token', default=None)
    oid: Optional[str] = Body(
        description='组织ID，仅当数据源ID为空时有效，如果不传则为最后一次登录AI智能问数时所使用的组织ID', default=None)


class ChatQuestionBase(BaseModel):
    question: str = Body(description='用户提问')
    chat_id: int = Body(description='会话ID')
    clarification_for_record_id: Optional[int] = Body(
        description='当前回答对应的澄清记录ID',
        default=None,
    )
    clarification_answers: list[dict[str, Any]] = Body(
        description='结构化澄清回答',
        default_factory=list,
    )


class McpQuestion(ChatQuestionBase):
    token: str = Body(description='token')
    stream: Optional[bool] = Body(description='是否流式输出，默认为true开启, 关闭false则返回JSON对象', default=True)
    lang: Optional[str] = Body(description='语言：zh-CN|zh-TW|en|ko-KR', default='zh-CN')
    datasource_id: Optional[int | str] = Body(description='数据源ID，仅当当前对话没有确定数据源时有效', default=None)
    return_img: Optional[bool] = Body(description='是否返回图表，默认为true开启, 关闭false则仅返回数据', default=True)


class AxisObj(BaseModel):
    name: str = ''
    value: str = ''
    type: str | None = None


class ExcelData(BaseModel):
    axis: list[AxisObj] = []
    data: list[dict] = []
    name: str = 'Excel'


class McpAssistant(BaseModel):
    question: str = Body(description='用户提问')
    url: str = Body(description='第三方数据接口')
    authorization: str = Body(description='第三方接口凭证')
    stream: Optional[bool] = Body(description='是否流式输出，默认为true开启, 关闭false则返回JSON对象', default=True)


class SystemPromptMessage(SystemMessage):
    sqlbot_system: bool = True

    def __init__(
            self, content: Union[str, list[Union[str, dict]]], **kwargs: Any
    ) -> None:
        super().__init__(content=content, **kwargs)


class HumanPromptMessage(HumanMessage):
    sqlbot_system: bool = True

    def __init__(
            self, content: Union[str, list[Union[str, dict]]], **kwargs: Any
    ) -> None:
        super().__init__(content=content, **kwargs)


class AIPromptMessage(AIMessage):
    sqlbot_system: bool = True

    def __init__(
            self, content: Union[str, list[Union[str, dict]]], **kwargs: Any
    ) -> None:
        super().__init__(content=content, **kwargs)
