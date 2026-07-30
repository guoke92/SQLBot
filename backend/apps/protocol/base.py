"""Protocol abstraction for pluggable query data sources.

Base pipeline calls only Protocol methods; concrete protocols own type-specific
connection, schema, prompt, plan parsing, safety and execution details.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Mapping, Optional, Sequence, Set

from pydantic import BaseModel, Field


class QueryResult(BaseModel):
    """Unified tabular result returned by every protocol."""

    fields: List[str] = Field(default_factory=list)
    data: List[Dict[str, Any]] = Field(default_factory=list)
    fields_info: Optional[List[Dict[str, Any]]] = None
    raw: Optional[Any] = None

    # Extraction metadata — protocol-agnostic, populated by the extraction pipeline.
    # API: extracted from response JSON via code_path/total_path.
    # SQL: reserved for future post-processing / masking.
    code_value: Optional[Any] = None  # Business status code (e.g. rsp.code)
    total: Optional[int] = None  # Total record count (e.g. rsp.data.total)
    # Bounded execution metadata. ``truncated`` means more rows exist than were
    # fetched; it never implies that the exact total is known.
    truncated: bool = False
    limit: Optional[int] = None
    truncation_reason: Optional[str] = None
    # Business-level success after extraction (HTTP status is handled earlier).
    # False when code_path is configured and the value does not match success criteria.
    is_success: bool = True

    # Display statement: SQL text for SQL protocols, "METHOD path\nparams: {...}" for REST.
    statement: Optional[str] = None
    # Re-execution payload: the minimum data needed to re-run this query later.
    # SQL protocols: {"sql": "SELECT ..."}; REST protocols: {"endpoint": ..., "params": ..., "base_url": ...}.
    # Base pipeline stores this on ChatRecord and hands it back through
    # ``plan_from_re_exec`` — never type-sniffed outside the protocol package.
    re_exec: Optional[Dict[str, Any]] = None

    def as_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "fields": self.fields,
            "data": self.data,
            # FE preview historically expects a `sql` key (even for empty).
            "sql": self.statement or "",
            "is_success": self.is_success,
        }
        if self.fields_info is not None:
            result["fields_info"] = self.fields_info
        if self.raw is not None:
            result["raw"] = self.raw
        if self.re_exec is not None:
            result["re_exec"] = self.re_exec
        if self.code_value is not None:
            result["code_value"] = self.code_value
        if self.total is not None:
            result["total"] = self.total
        if self.truncated:
            result["truncated"] = True
            result["limit"] = self.limit
            result["truncation_reason"] = self.truncation_reason or "query_limit"
        return result


class QueryPlan(BaseModel):
    """LLM-decided (or reconstructed) executable plan consumed only by the owning protocol."""

    success: bool = True
    # Display / log representation (SQL text, method+path, etc.)
    statement: str = ""
    # Protocol payload: Sql uses sql; Rest uses endpoint/params/_endpoint/_base_url.
    payload: Dict[str, Any] = Field(default_factory=dict)
    # Resource allow-list candidates: table names or endpoint names.
    resources: List[str] = Field(default_factory=list)
    chart_type: Optional[str] = None
    brief: Optional[str] = None
    message: Optional[str] = None


class SchemaSnapshot(BaseModel):
    """Schema text + resource names for RAG-enhanced generation."""

    schema_text: str = ""
    resource_names: List[str] = Field(default_factory=list)
    sample_data: str = ""


class DictionaryExtractResult(BaseModel):
    """Bounded values returned by a protocol-owned dictionary extraction."""

    values: List[str] = Field(default_factory=list)
    truncated: bool = False
    statement: str = ""


class PromptBundle(BaseModel):
    """Protocol-owned system prompt pieces (LLM message list built by base).

    Prompt *content* may be protocol-specific (SQL rules vs API endpoint rules).
    Human/AI message scaffolding in the chat pipeline must stay generic: it only
    consumes this bundle and never hardcodes SQL/API wording.
    """

    system: str = ""
    rules: str = ""
    schema_text: str = ""
    terminologies: Optional[str] = None
    data_training: Optional[str] = None
    custom_prompt: Optional[str] = None
    # AI acknowledgment messages — defaults are protocol-agnostic.
    # Protocols may override when terminology truly differs (e.g. SQL/table vs API/endpoint).
    ack_rules: str = "我已掌握所有规则，包括数据结构、查询规范、安全限制和输出格式，我会严格遵守这些规则。"
    ack_schema: str = (
        "我已确认您提供的数据源信息与数据结构，我生成的查询不会超出您提供的范围。"
    )
    ack_custom_prompt: str = "我已确认您提供的额外信息，我会进行参考。"
    ack_terminologies: str = "我已确认您提供的术语信息，我会进行参考。"
    ack_data_training: str = "我已确认您提供的查询示例，我会进行参考。"

    def as_dict(self) -> Dict[str, str]:
        result = {
            "system": self.system,
            "rules": self.rules,
            "schema": self.schema_text,
            "ack_rules": self.ack_rules,
            "ack_schema": self.ack_schema,
            "ack_custom_prompt": self.ack_custom_prompt,
            "ack_terminologies": self.ack_terminologies,
            "ack_data_training": self.ack_data_training,
        }
        if self.custom_prompt:
            result["custom_prompt"] = self.custom_prompt
        if self.terminologies:
            result["terminologies"] = self.terminologies
        if self.data_training:
            result["data_training"] = self.data_training
        return result


# Capability flags — prefer these over type branching in the base layer.
CAP_SQL_DIALECT = "sql_dialect"
CAP_ROW_PERMISSION = "row_permission"
CAP_SAMPLE_DATA = "sample_data"
CAP_OPENAPI_IMPORT = "openapi_import"
CAP_TABLE_RELATION = "table_relation"
CAP_DICTIONARY_VALUES = "dictionary_values"
# Resources (tables/endpoints) are owned by datasource conf and always re-projected
# from conf on create/update — free-form chooseTables is not allowed to desync them.
CAP_CONF_OWNED_RESOURCES = "conf_owned_resources"


class BaseProtocol(ABC):
    """Protocol contract. Implementations must be fully isolated from each other."""

    # Type key this instance was resolved for (mysql / pg / api / ...)
    type_key: str = ""
    capabilities: Set[str] = set()
    training_type: str = "sql"  # data_training type this protocol expects (sql / rest)

    def supports(self, capability: str) -> bool:
        return capability in self.capabilities

    def normalize_configuration(
        self,
        configuration: Mapping[str, Any],
    ) -> Dict[str, Any]:
        """Validate and canonicalize plaintext configuration before encryption."""
        return dict(configuration)

    def extract_dictionary_values(
        self,
        ds: Any,
        *,
        resource: str,
        field: str,
        limit: int,
    ) -> DictionaryExtractResult:
        """Extract a bounded distinct snapshot for an enabled dictionary field."""
        raise NotImplementedError("Dictionary extraction is not supported")

    @abstractmethod
    def check_connection(
        self, ds: Any, trans: Any = None, is_raise: bool = False
    ) -> bool: ...

    @abstractmethod
    def get_tables(self, ds: Any) -> List[Any]:
        """Return TableSchema-compatible objects (tableName/tableComment)."""
        ...

    @abstractmethod
    def get_fields(self, ds: Any, table_name: str) -> List[Any]:
        """Return ColumnSchema-compatible objects."""
        ...

    @abstractmethod
    def retrieve_schema(
        self,
        session: Any,
        current_user: Any,
        ds: Any,
        question: str,
        *,
        embedding: bool = True,
        out_ds_instance: Any = None,
        resource_names: Optional[Sequence[str]] = None,
        required_resource_names: Sequence[str] = (),
        access_scope: Any = None,
    ) -> SchemaSnapshot:
        """Return schema text for prompt / chart context.

        ``embedding`` is a **mechanism** default (True). Chat graphs/steps must
        not pass it — table ranking is gated by ``settings.TABLE_EMBEDDING_ENABLED``
        inside CRUD. ``resource_names`` restricts to an exact subset selected
        by a prior plan. ``required_resource_names`` augments normal recall and
        is never removed by ranking. ``access_scope`` is a request-scoped,
        pre-resolved catalog/permission snapshot.
        Assistant out-DS ignores embedding (no table vector rank).
        """
        ...

    @abstractmethod
    def build_prompt_bundle(
        self, chat_question: Any, *, enable_query_limit: bool = True
    ) -> PromptBundle: ...

    @abstractmethod
    def build_user_prompt(
        self, chat_question: Any, *, current_time: str, change_title: bool
    ) -> str: ...

    @abstractmethod
    def parse_llm_output(self, text: str) -> QueryPlan: ...

    @abstractmethod
    def validate_plan(
        self, ds: Any, plan: QueryPlan, allowed_resources: Sequence[str]
    ) -> QueryPlan: ...

    @abstractmethod
    def execute(
        self,
        ds: Any,
        plan: QueryPlan,
        *,
        origin_column: bool = False,
        max_rows: Optional[int] = None,
    ) -> QueryResult: ...

    @abstractmethod
    def preview(
        self,
        session: Any,
        current_user: Any,
        ds: Any,
        table_name: str,
        fields: Sequence[str],
        *,
        where: str = "",
        limit: int = 100,
    ) -> QueryResult: ...

    def plan_from_re_exec(
        self, ds: Any, re_exec: Dict[str, Any]
    ) -> Optional[QueryPlan]:
        """Rebuild a QueryPlan from a stored re_exec payload.

        Default: unsupported. Protocols that emit re_exec on execute() must implement this
        so live refresh / dashboard can re-run without knowing protocol payload shape.
        """
        return None

    def format_statement_for_display(self, plan: QueryPlan) -> str:
        return plan.statement or ""

    def build_chart_system_prompt(self, chat_question: Any) -> Dict[str, str]:
        """Return chart prompt pieces for message construction (graph chart node).

        Keys: ``system``, ``rules``, ``ack``.  Default implementation uses the
        SQL-centric ``template.chart`` section — REST overrides to
        ``template.chart_api`` so the chart LLM sees protocol-appropriate
        language and rules (e.g. "must include all fields" for table).
        """
        from apps.template.generate_chart.generator import get_chart_template

        tpl = get_chart_template()
        return {
            "system": tpl["system"].format(
                lang=chat_question.lang, sqlbot_name=chat_question.sqlbot_name
            ),
            "rules": tpl["generate_rules"].format(lang=chat_question.lang),
            "ack": "我已掌握所有规则，我会严格遵守这些规则来生成符合要求的JSON。",
        }

    def build_chart_user_prompt(
        self,
        chat_question: Any,
        chart_type: str,
        schema: str,
    ) -> str:
        """Return the formatted user prompt for ``generate_chart()``.

        Default uses the SQL-centric ``template.chart.user`` (placeholders:
        ``{sql}``, ``{schema}`` in ``<m-schema>``).  REST overrides to use
        ``{query_plan}`` in ``<query-plan>`` and ``<api-response-schema>``.
        """
        from apps.template.generate_chart.generator import get_chart_template

        tpl = get_chart_template()
        return tpl["user"].format(
            lang=chat_question.lang,
            sql=chat_question.sql,
            question=(
                getattr(chat_question, "generation_question", "")
                or getattr(chat_question, "planning_question", "")
                or chat_question.question
            ),
            rule=chat_question.rule,
            chart_type=chart_type,
            schema=schema,
        )

    def engine_display_name(self, ds: Any) -> str:
        type_name = (
            getattr(ds, "type_name", None) or getattr(ds, "type", "") or self.type_key
        )
        return str(type_name)

    def server_version(self, ds: Any) -> str:
        """Optional engine version suffix for prompts (e.g. MySQL 8.0). Default: empty."""
        return ""

    def schema_namespace(self, ds: Any) -> str:
        """Logical schema / database namespace used when projecting tables/fields.

        Rest / conf-owned protocols have no DB schema namespace and return "".
        """
        return ""

    def get_resource_detail(self, ds: Any, table_name: str) -> Optional[Dict[str, Any]]:
        """Return the structured definition of a resource (table / endpoint).

        Protocol-agnostic concept:
        - REST: method/path, request params, response fields, extraction config
        - SQL (future): columns, keys, comments
        Default: None — callers fall back to ``get_fields`` / field list.
        """
        return None

    def test_extract(
        self,
        ds: Any,
        table_name: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute a resource and return the full extraction pipeline view.

        Used by management / debug UIs. Must share the same execution + extraction
        core as ``execute`` so debug results match production behavior.

        Common keys (protocol may add extras):
        {
            "raw_response": Any,
            "extracted_rows": List[Dict],
            "projected_fields": List[str],
            "projected_data": List[Dict],
            "code_value": Any,
            "total": Optional[int],
            "is_success": bool,
            "error": Optional[str],
            "resource": Dict,           # get_resource_detail(...)
            "params_used": Dict,
        }
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support test_extract"
        )
