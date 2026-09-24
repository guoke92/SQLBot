"""Registry and LangChain tool binding for unified agent tools."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, Self

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field, model_validator

from apps.chat.chart_presentation import LEGAL_CHART_TYPES
from apps.chat.tools.catalog_tools import (
    get_dict_values,
    get_table_relations,
    get_table_schema,
    lookup_values,
    search_knowledge,
)
from apps.chat.tools.clarification import request_clarification
from apps.chat.tools.compare_results import compare_query_results
from apps.chat.tools.complete_answer import complete_without_sql
from apps.chat.tools.execute_sql import execute_sql_sandbox
from apps.chat.tools.patch_sql import patch_and_compile_sql

PatchAction = Literal[
    "add_dimension",
    "add_filter",
    "replace_filter",
    "change_limit",
    "change_order",
]
ChartType = Literal["", "table", "line", "bar", "column", "pie"]

_PATCH_PAYLOAD_KEYS: dict[str, frozenset[str]] = {
    "add_dimension": frozenset({"fields"}),
    "add_filter": frozenset({"condition"}),
    "replace_filter": frozenset({"old_field", "new_condition"}),
    "change_limit": frozenset({"limit"}),
    "change_order": frozenset({"order"}),
}


def _clarification_catalog(llm_service: Any, access_scope: Any) -> dict[str, set[str]]:
    """Live datasource catalog for grounding clarification options."""
    ds_id = getattr(getattr(llm_service, "ds", None), "id", None)
    if ds_id is None:
        return {}
    try:
        from apps.conversation.session import session_scope
        from apps.datasource.embedding.schema_index import catalog_field_index

        with session_scope() as session:
            return catalog_field_index(
                session, ds_id=int(ds_id), access_scope=access_scope
            )
    except Exception:
        return {}


class ClarificationFieldRefSchema(BaseModel):
    name: str = Field(
        default="",
        description=(
            "Physical field name this mapping cites. Prefer this; leave field empty."
        ),
    )
    field: str = Field(
        default="",
        description=(
            "Legacy alias of name. Omit when name is set; either name or field is "
            "required."
        ),
    )
    table: str = Field(
        default="",
        description="Physical table this field belongs to. Must exist on the datasource.",
    )
    comment: str = Field(default="", description="Optional field comment.")
    value: str = Field(
        default="",
        description="Optional enum literal when this option also fixes a value.",
    )

    @model_validator(mode="after")
    def require_name(self) -> Self:
        resolved = (self.name or self.field).strip()
        if not resolved:
            raise ValueError("Clarification field requires a name")
        self.name = resolved
        return self


class ClarificationOptionSchema(BaseModel):
    label: str = Field(
        description=(
            "One short business sentence for the difference this option makes. "
            "No physical table/field/enum names. No contrastive phrasing such as "
            "'not A but B'."
        )
    )
    description: str = Field(
        default="",
        description=(
            "Optional extra business meaning of this option (what rows or values "
            "the user would get). No physical table/field/enum names. Physical "
            "mapping belongs only in table, field, or fields."
        ),
    )
    option_id: str = Field(default="", description="Unique identifier for this option.")
    table: str = Field(
        default="",
        description="Physical table this option maps to when using a single field. Must exist on the datasource.",
    )
    field: str = Field(
        default="",
        description="Physical field this option maps to when using a single field. Must exist on that table.",
    )
    fields: list[ClarificationFieldRefSchema] = Field(
        default_factory=list,
        description=(
            "Complete mapping for this option. Use when one choice binds several "
            "output columns or a composite caliber. Each item must cite a real "
            "table/field. Legacy single table/field remains valid."
        ),
    )


class ClarificationQuestionSchema(BaseModel):
    question: str = Field(
        description=(
            "Business question shown to the user. No physical table, field, or "
            "enum identifiers."
        )
    )
    options: list[ClarificationOptionSchema] = Field(
        description="List of mutually exclusive candidate options."
    )
    question_id: str = Field(
        default="", description="Unique identifier for this question."
    )


def _repair_clarification_payload(data: Any) -> Any:
    """Normalize common model shapes before schema validation.

    Models sometimes emit q2's options as sibling ``questions`` entries and park
    the real question text on the payload root — repair into one question with
    options so StructuredTool validation and the runtime coercer agree.
    """
    if not isinstance(data, Mapping):
        return data
    payload = dict(data)
    questions = payload.get("questions")
    if not isinstance(questions, list):
        return payload
    fixed: list[Any] = []
    leaked_options: list[Any] = []
    for item in questions:
        if not isinstance(item, Mapping):
            fixed.append(item)
            continue
        if item.get("options") is not None and item.get("question"):
            fixed.append(dict(item))
            continue
        if item.get("label") or item.get("option_id") or item.get("description"):
            leaked_options.append(dict(item))
            continue
        fixed.append(dict(item))
    dangling_question = str(payload.get("question") or "").strip()
    dangling_id = str(payload.get("question_id") or "").strip()
    if leaked_options and dangling_question:
        fixed.append(
            {
                "question": dangling_question,
                "question_id": dangling_id,
                "options": leaked_options,
            }
        )
        payload.pop("question", None)
        payload.pop("question_id", None)
    elif leaked_options and fixed:
        last = dict(fixed[-1])
        options = list(last.get("options") or [])
        options.extend(leaked_options)
        last["options"] = options
        fixed[-1] = last
    payload["questions"] = fixed
    return payload


class RequestClarificationInput(BaseModel):
    questions: list[ClarificationQuestionSchema] = Field(
        description="List of clarification questions to present to the user. Each item must have 'question' and 'options'."
    )

    @model_validator(mode="before")
    @classmethod
    def repair_payload(cls, data: Any) -> Any:
        return _repair_clarification_payload(data)


class GetTableSchemaInput(BaseModel):
    tables: list[str] = Field(
        description=(
            "Physical table names from schema_outline to expand (max 3). "
            "Do not pass tables already returned in this conversation's ToolMessages."
        ),
        min_length=1,
        max_length=3,
    )


class GetTableRelationsInput(BaseModel):
    tables: list[str] = Field(
        description=(
            "Two or more physical table names whose JOIN path is needed. "
            "Do not call for a single-table question."
        ),
        min_length=2,
    )


class SearchKnowledgeInput(BaseModel):
    query: str = Field(
        description=(
            "Business caliber, concept, metric, or scenario to resolve. "
            "Returns structured maps_to/adjudication/hubs objects, not table DDL. "
            "Do not use this to discover tables or field lists."
        ),
        min_length=1,
    )


class LookupValuesInput(BaseModel):
    phrases: list[str] = Field(
        default_factory=list,
        description=(
            "Business instance fragments named by the user, e.g. ['刘宁']. "
            "Empty only when sampling a field via scope table.field. "
            "Do not pass whole questions, dates, quantities, or concept names "
            "like 平台录入 (use search_knowledge for those)."
        ),
    )
    scope: list[str] = Field(
        default_factory=list,
        description=(
            "Optional table or table.field tokens, e.g. "
            "['wechat_project_approval_apply', "
            "'tenant_project_approval.solution_manager_name']. "
            "Caps: 3 tables + 3 fields. Required (field-level) when phrases is empty."
        ),
    )

    @model_validator(mode="after")
    def _phrases_or_field_scope(self) -> Self:
        phrases = [
            str(item).strip() for item in self.phrases or [] if str(item).strip()
        ]
        tokens = [str(item).strip() for item in self.scope or [] if str(item).strip()]
        field_items = [item for item in tokens if "." in item]
        if phrases or field_items:
            return self
        raise ValueError(
            "lookup_values requires phrases or field-level scope (table.field)"
        )


class GetDictValuesInput(BaseModel):
    dict_name: str = Field(
        default="",
        description="Dictionary slug (schema dict= pointer). Prefer this when known.",
    )
    table: str = Field(
        default="",
        description="Physical table of the enum field when dict_name is unknown.",
    )
    field: str = Field(
        default="",
        description="Physical field of the enum when dict_name is unknown.",
    )

    @model_validator(mode="after")
    def _need_dict_or_field(self) -> Self:
        if str(self.dict_name or "").strip():
            return self
        if str(self.table or "").strip() and str(self.field or "").strip():
            return self
        raise ValueError("get_dict_values requires dict_name or table+field")


class PatchSqlInput(BaseModel):
    base_sql: str = Field(description="The existing valid base SQL to be modified.")
    action: PatchAction = Field(
        description=(
            "Patch kind. add_dimension→payload.fields; add_filter→condition; "
            "replace_filter→old_field+new_condition; change_limit→limit; "
            "change_order→order. Prefer this over rewriting SQL for follow-up "
            "caliber edits."
        ),
    )
    payload: dict[str, Any] = Field(
        description=(
            "Keys required by action: "
            "add_dimension={'fields':['dept']}; "
            "add_filter={'condition':\"status != '0'\"}; "
            "replace_filter={'old_field':'status','new_condition':\"status='1'\"}; "
            "change_limit={'limit':100}; "
            "change_order={'order':'total DESC'}."
        ),
    )

    @model_validator(mode="after")
    def _payload_matches_action(self) -> Self:
        allowed = _PATCH_PAYLOAD_KEYS[self.action]
        keys = {str(key) for key in (self.payload or {}) if str(key).strip()}
        unknown = keys - allowed
        if unknown:
            raise ValueError(
                f"payload keys {sorted(unknown)} invalid for action={self.action}; "
                f"allowed={sorted(allowed)}"
            )
        if self.action == "add_dimension":
            fields = self.payload.get("fields")
            if not fields or (isinstance(fields, list) and not any(fields)):
                raise ValueError("add_dimension requires payload.fields")
        elif self.action == "add_filter":
            if not str(self.payload.get("condition") or "").strip():
                raise ValueError("add_filter requires payload.condition")
        elif self.action == "replace_filter":
            if not str(self.payload.get("new_condition") or "").strip():
                raise ValueError("replace_filter requires payload.new_condition")
        elif self.action == "change_order":
            if not str(self.payload.get("order") or "").strip():
                raise ValueError("change_order requires payload.order")
        elif self.action == "change_limit":
            if "limit" not in self.payload:
                raise ValueError("change_limit requires payload.limit (int or null)")
        return self


class ExecuteSqlInput(BaseModel):
    sql: str = Field(description="SQL query string to execute safely in the sandbox.")
    limit: int = Field(
        default=1000,
        description=(
            "Max rows to retrieve when SQL has no LIMIT (default 1000). "
            "If SQL already contains LIMIT N, that N is respected (up to system max); "
            "when the user names a row count, write it into the SQL LIMIT."
        ),
    )
    required: bool = Field(
        default=True,
        description=(
            "True: delivery — mounts/replaces a result card in the final answer. "
            "False: probe only — not a terminal exit; use for GROUP BY shape checks."
        ),
    )
    result_title: str = Field(
        default="",
        description=(
            "Short business title for this result card. No SQL or physical table "
            "names. Same title replaces the previous delivery card; a new title "
            "adds another card. Empty for probes (required=false)."
        ),
    )
    chart_type: ChartType = Field(
        default="",
        description=(
            "Delivery chart: table|line|bar|column|pie. table for lists; line for "
            "trends; bar/column for category comparison; pie for share. "
            "Empty only when required=false."
        ),
    )

    @model_validator(mode="after")
    def _delivery_needs_chart(self) -> Self:
        chart = str(self.chart_type or "").strip().lower()
        if chart and chart not in LEGAL_CHART_TYPES:
            raise ValueError(
                f"chart_type must be one of {sorted(LEGAL_CHART_TYPES)} or empty"
            )
        if self.required and not chart:
            # Allow empty at schema time; execute_sql defaults to table — but
            # nudge the model via description. Soft: do not hard-fail empty.
            return self
        return self


class CompleteWithoutSqlInput(BaseModel):
    content: str = Field(
        description=(
            "User-facing terminal answer for this turn (no SQL delivery). "
            "Lead with whether it can be done or what is missing, in business "
            "language. No boilerplate, no contrastive 'not X but Y', no physical "
            "table dump."
        ),
    )


class CompareResultsInput(BaseModel):
    base_sql: str = Field(
        description="Original base SQL representing prior caliber or result."
    )
    new_sql: str = Field(
        description="New SQL representing the challenged or revised caliber."
    )
    hypothesis: str = Field(
        default="",
        description="The hypothesis being tested, e.g. 'Exclude cancelled orders'.",
    )


def build_agent_tools(
    llm_service: Any, access_scope: Any = None
) -> list[StructuredTool]:
    """Construct bound LangChain tools scoped to current LLMService and access permissions."""

    def _get_table_schema(tables: list[str]) -> dict[str, Any]:
        return dict(get_table_schema(llm_service, tables, access_scope=access_scope))

    def _get_table_relations(tables: list[str]) -> dict[str, Any]:
        return dict(get_table_relations(llm_service, tables, access_scope=access_scope))

    def _search_knowledge(query: str) -> dict[str, Any]:
        return dict(search_knowledge(llm_service, query, access_scope=access_scope))

    def _lookup_values(
        phrases: list[str] | None = None,
        scope: list[str] | None = None,
    ) -> dict[str, Any]:
        return dict(
            lookup_values(
                llm_service,
                phrases or [],
                scope=scope or [],
                access_scope=access_scope,
            )
        )

    def _get_dict_values(
        dict_name: str = "", table: str = "", field: str = ""
    ) -> dict[str, Any]:
        return dict(
            get_dict_values(
                llm_service,
                dict_name=dict_name,
                table=table,
                field=field,
                access_scope=access_scope,
            )
        )

    def _patch_sql(
        base_sql: str, action: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        dialect = getattr(getattr(llm_service, "datasource", None), "type", None)
        res = patch_and_compile_sql(base_sql, action, payload, dialect=dialect)
        return dict(res)

    def _execute_sql(
        sql: str,
        limit: int = 1000,
        required: bool = True,
        result_title: str = "",
        chart_type: str = "",
    ) -> dict[str, Any]:
        res = execute_sql_sandbox(
            llm_service,
            sql,
            access_scope=access_scope,
            limit=limit,
            required=required,
            result_title=result_title,
            chart_type=chart_type,
        )
        return dict(res)

    def _compare_results(
        base_sql: str, new_sql: str, hypothesis: str = ""
    ) -> dict[str, Any]:
        res = compare_query_results(
            llm_service,
            base_sql,
            new_sql,
            hypothesis=hypothesis,
            access_scope=access_scope,
        )
        return dict(res)

    def _complete_without_sql(content: str) -> dict[str, Any]:
        res = complete_without_sql(content)
        return dict(res)

    def _request_clarification(questions: list[Any]) -> dict[str, Any]:
        raw_list = []
        for q in questions:
            if hasattr(q, "model_dump"):
                raw_list.append(q.model_dump(mode="python"))
            elif isinstance(q, dict):
                raw_list.append(q)
        catalog = _clarification_catalog(llm_service, access_scope)
        res = request_clarification(raw_list, catalog=catalog)
        return dict(res)

    tools: list[StructuredTool] = [
        StructuredTool.from_function(
            func=_get_table_schema,
            name="get_table_schema",
            description=(
                "Expand full field definitions for up to 3 tables named in "
                "schema_outline. Call when SQL needs column names not yet in "
                "this conversation. Safe to parallel with get_table_relations / "
                "lookup_values / search_knowledge. Do not recall tables already "
                "returned; never query information_schema."
            ),
            args_schema=GetTableSchemaInput,
        ),
        StructuredTool.from_function(
            func=_get_table_relations,
            name="get_table_relations",
            description=(
                "Return known JOIN edges among two or more named tables. "
                "Call only when the question spans multiple entities. "
                "Safe to parallel with get_table_schema. Do not call for a "
                "single-table export. trust is advisory and does not forbid JOIN."
            ),
            args_schema=GetTableRelationsInput,
        ),
        StructuredTool.from_function(
            func=_search_knowledge,
            name="search_knowledge",
            description=(
                "Retrieve structured business caliber / concept / metric / scenario "
                "objects (maps_to, adjudication, hubs). Call for abstract business "
                "terms or name/value conflicts. Do not use to discover tables/DDL "
                "or open instance phrases (use get_table_schema / lookup_values). "
                "Skip when field comments already explain the column."
            ),
            args_schema=SearchKnowledgeInput,
        ),
        StructuredTool.from_function(
            func=_lookup_values,
            name="lookup_values",
            description=(
                "Reverse-lookup open instance values from named phrases, or sample "
                "a column when phrases is empty and scope has table.field. "
                "Call for people/dept fragments or column topk. Returns match_hint "
                "(eq|contains), aliases, and display_name for id columns. "
                "Evidence only, not a WHERE. Do not pass dates, quantities, closed "
                "schema labels, or concept names (use get_dict_values / "
                "search_knowledge)."
            ),
            args_schema=LookupValuesInput,
        ),
        StructuredTool.from_function(
            func=_get_dict_values,
            name="get_dict_values",
            description=(
                "Look up one known field's value→label dictionary. Call when schema "
                "inline codes are incomplete. Do not reverse-lookup open instances "
                "(use lookup_values); skip when labels= or comments already list codes."
            ),
            args_schema=GetDictValuesInput,
        ),
        StructuredTool.from_function(
            func=_patch_sql,
            name="patch_and_compile_sql",
            description=(
                "Incrementally patch an existing valid SQL (follow-up caliber edits). "
                "Call for add_dimension / add_filter / replace_filter / change_limit / "
                "change_order. Do not use for a brand-new query — write SQL and "
                "execute_sql_sandbox instead."
            ),
            args_schema=PatchSqlInput,
        ),
        StructuredTool.from_function(
            func=_execute_sql,
            name="execute_sql_sandbox",
            description=(
                "Execute business SQL. required=true delivers a result card "
                "(same result_title replaces; new title appends) and is a terminal "
                "data exit; required=false is probe-only and not a final answer. "
                "Set chart_type table|line|bar|column|pie for delivery. "
                "Do not inspect catalogs (information_schema, SHOW COLUMNS, DESCRIBE). "
                "Call get_table_schema first if needed tables are not in schema_catalog."
            ),
            args_schema=ExecuteSqlInput,
        ),
        StructuredTool.from_function(
            func=_compare_results,
            name="compare_results",
            description=(
                "Compare result sets of a base SQL and a revised SQL. Call when "
                "the user challenges numbers or a caliber change must be verified. "
                "Do not use as the delivery exit — follow with execute_sql_sandbox "
                "or complete_without_sql."
            ),
            args_schema=CompareResultsInput,
        ),
        StructuredTool.from_function(
            func=_complete_without_sql,
            name="complete_without_sql",
            description=(
                "Terminal exit without SQL delivery. Call for capability, usage, or "
                "catalog-gap answers. content is the only user-facing answer for this "
                "turn (lead with the conclusion; business language; no physical names). "
                "Do not use to skip a data query; probes (required=false) are not an "
                "exit. After a successful delivery SQL, do not call this tool."
            ),
            args_schema=CompleteWithoutSqlInput,
        ),
        StructuredTool.from_function(
            func=_request_clarification,
            name="request_clarification",
            description=(
                "Ask the user to pick among mutually exclusive business calibers. "
                "Call when ambiguity changes row set, output-column values/lineage, "
                "or aggregation/grouping. Shows a card and waits for the user — "
                "do not deliver SQL in the same turn. question/label/description are "
                "user-facing business copy only; bind physical mapping in "
                "table/field/fields. Do not invent objects absent from "
                "schema_outline or schema_catalog."
            ),
            args_schema=RequestClarificationInput,
        ),
    ]

    return tools
