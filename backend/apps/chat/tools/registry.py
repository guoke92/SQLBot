"""Registry and LangChain tool binding for unified agent tools."""

from __future__ import annotations

from typing import Any

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from apps.chat.tools.clarification import request_clarification
from apps.chat.tools.compare_results import compare_query_results
from apps.chat.tools.execute_sql import execute_sql_sandbox
from apps.chat.tools.patch_sql import patch_and_compile_sql
from apps.chat.tools.wiki_search import search_wiki_knowledge


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


class ClarificationOptionSchema(BaseModel):
    label: str = Field(description="Display label of this candidate option.")
    description: str = Field(
        default="",
        description="Business explanation, field name, or condition meaning of this option.",
    )
    option_id: str = Field(default="", description="Unique identifier for this option.")
    table: str = Field(
        default="",
        description="Physical table this option maps to. Must exist on the datasource.",
    )
    field: str = Field(
        default="",
        description="Physical field this option maps to. Must exist on that table.",
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


class SearchWikiInput(BaseModel):
    query: str = Field(
        description=(
            "Business concept, table name, caliber, or keyword to search Wiki for. "
            "Use again when the first recall is incomplete, clarification introduces "
            "new concepts, or thinking finds a missing table/enum/org mapping."
        )
    )


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
            "Max rows to retrieve when SQL has no LIMIT. "
            "If SQL already contains LIMIT N, that N is respected (up to system max)."
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

    def _search_wiki(query: str) -> dict[str, Any]:
        res = search_wiki_knowledge(llm_service, query, access_scope=access_scope)
        return dict(res)

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
    ) -> dict[str, Any]:
        res = execute_sql_sandbox(
            llm_service,
            sql,
            access_scope=access_scope,
            limit=limit,
            required=required,
            result_title=result_title,
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
            func=_search_wiki,
            name="search_wiki",
            description=(
                "Search Wiki for table structures, field definitions, enums, and calibers. "
                "Returns a coverage stub (added_tables/pages, schema_ready, stop_search); "
                "full schema lives only in the system prompt. "
                "Call again only for a new gap. If the result is schema_missing, one more "
                "targeted query is allowed; if it is stagnant/stop_search, stop. Never "
                "query information_schema to fill schema gaps."
            ),
            args_schema=SearchWikiInput,
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
                "Do not use this to inspect catalogs (information_schema, SHOW COLUMNS, DESCRIBE). "
                "If Wiki has not provided table/enum schema, do not call this tool."
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
            func=_request_clarification,
            name="request_clarification",
            description="Ask the user for clarification when there is significant business ambiguity that alters query results. Each option must map to a real table/field from search_wiki or the current schema. Do not invent products, platforms, or objects that are not in the datasource.",
            args_schema=RequestClarificationInput,
        ),
    ]

    return tools
