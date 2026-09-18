"""Registry and LangChain tool binding for unified agent tools."""

from __future__ import annotations

from typing import Any, Self

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field, model_validator

from apps.chat.tools.catalog_tools import (
    get_dict_values,
    get_table_relations,
    get_table_schema,
    search_knowledge,
)
from apps.chat.tools.clarification import request_clarification
from apps.chat.tools.compare_results import compare_query_results
from apps.chat.tools.complete_answer import complete_without_sql
from apps.chat.tools.execute_sql import execute_sql_sandbox
from apps.chat.tools.patch_sql import patch_and_compile_sql


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
        description="Physical field name this mapping cites. Prefer this over field.",
    )
    field: str = Field(
        default="",
        description="Alias of name. Either name or field is required.",
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
    label: str = Field(description="Display label of this candidate option.")
    description: str = Field(
        default="",
        description="Business explanation, field name, or condition meaning of this option.",
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
    question: str = Field(description="The concrete business question to ask the user.")
    options: list[ClarificationOptionSchema] = Field(
        description="List of mutually exclusive candidate options."
    )
    question_id: str = Field(
        default="", description="Unique identifier for this question."
    )


class RequestClarificationInput(BaseModel):
    questions: list[ClarificationQuestionSchema] = Field(
        description="List of clarification questions to present to the user. Each item must have 'question' and 'options'."
    )


class GetTableSchemaInput(BaseModel):
    tables: list[str] = Field(
        description=(
            "Physical table names from schema_outline to expand (max 3). "
            "Do not pass tables already listed in schema_catalog."
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
            "Business caliber, formula, or proper noun to resolve. "
            "Do not use this to discover tables or field lists."
        ),
        min_length=1,
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
    action: str = Field(
        description="Action: add_dimension, add_filter, replace_filter, change_limit, change_order."
    )
    payload: dict[str, Any] = Field(
        description="Payload specific to the action, e.g. {'fields': ['dept']} or {'condition': 'status != 0'}."
    )


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
            "True for datasets that should appear in the final answer. "
            "False for exploratory / verification queries (GROUP BY probes, compare_results)."
        ),
    )
    result_title: str = Field(
        default="",
        description="Short Chinese title for a delivery result, e.g. 企业清单. Empty for probes.",
    )
    chart_type: str = Field(
        default="",
        description=(
            "Required for delivery (required=true): table|line|bar|column|pie. "
            "Use table for entity lists/detail dumps; line for trends; "
            "bar/column for category comparison; pie for share-of-total. "
            "Ignored for probes (required=false)."
        ),
    )


class CompleteWithoutSqlInput(BaseModel):
    content: str = Field(
        description=(
            "User-facing terminal answer in business language. Do not pile "
            "physical table names. Use only when this turn will not deliver SQL."
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
                "schema_outline. Does not return joins or wiki prose. "
                "Do not recall tables already in schema_catalog. "
                "Never query information_schema."
            ),
            args_schema=GetTableSchemaInput,
        ),
        StructuredTool.from_function(
            func=_get_table_relations,
            name="get_table_relations",
            description=(
                "Return known JOIN edges among two or more named tables. "
                "Call only when the question spans multiple entities. "
                "Do not call for a single-table export."
            ),
            args_schema=GetTableRelationsInput,
        ),
        StructuredTool.from_function(
            func=_search_knowledge,
            name="search_knowledge",
            description=(
                "Retrieve business caliber / concept / metric text. "
                "Does not select tables or return DDL. At most once per turn. "
                "Skip when field comments already explain the column."
            ),
            args_schema=SearchKnowledgeInput,
        ),
        StructuredTool.from_function(
            func=_get_dict_values,
            name="get_dict_values",
            description=(
                "Look up one field's value→label dictionary. "
                "Skip when schema labels= or comments already list codes."
            ),
            args_schema=GetDictValuesInput,
        ),
        StructuredTool.from_function(
            func=_patch_sql,
            name="patch_and_compile_sql",
            description="Incrementally patch a base SQL without full rewrite. Supports add_dimension, add_filter, replace_filter, change_order.",
            args_schema=PatchSqlInput,
        ),
        StructuredTool.from_function(
            func=_execute_sql,
            name="execute_sql_sandbox",
            description=(
                "Safely execute a business SQL query against the datasource. "
                "For delivery (required=true), set chart_type to table|line|bar|column|pie "
                "and a short result_title. Do not use this to inspect catalogs "
                "(information_schema, SHOW COLUMNS, DESCRIBE). "
                "If the needed tables are not yet in schema_catalog, call "
                "get_table_schema first."
            ),
            args_schema=ExecuteSqlInput,
        ),
        StructuredTool.from_function(
            func=_compare_results,
            name="compare_results",
            description="Compare results between base SQL and revised SQL to test a challenge hypothesis or verify caliber difference.",
            args_schema=CompareResultsInput,
        ),
        StructuredTool.from_function(
            func=_complete_without_sql,
            name="complete_without_sql",
            description=(
                "Finish this turn without delivering SQL. Call when the user "
                "needs a capability/usage/knowledge explanation rather than a "
                "dataset, or when the catalog cannot cover the question. content is "
                "the user-facing answer. Do not use this to skip a data query; "
                "probes (required=false) are not an exit. After a successful "
                "delivery SQL, do not call this tool."
            ),
            args_schema=CompleteWithoutSqlInput,
        ),
        StructuredTool.from_function(
            func=_request_clarification,
            name="request_clarification",
            description=(
                "Ask the user for clarification when there is significant business "
                "ambiguity that changes query semantics: row set, output-column "
                "values/lineage, or aggregation/grouping caliber. Each option must "
                "map to real table/field(s) from schema_outline or schema_catalog; "
                "use fields when one option carries a complete multi-column mapping. "
                "Do not invent products, platforms, or objects that are not in the datasource."
            ),
            args_schema=RequestClarificationInput,
        ),
    ]

    return tools
