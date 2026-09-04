"""Registry and LangChain tool binding for unified agent tools."""

from __future__ import annotations

from typing import Any, Callable
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from apps.chat.steps.wiki_recall import wiki_backend_active
from apps.chat.tools.clarification import request_clarification
from apps.chat.tools.compare_results import compare_query_results
from apps.chat.tools.execute_sql import execute_sql_sandbox
from apps.chat.tools.patch_sql import patch_and_compile_sql
from apps.chat.tools.schema_search import search_and_inspect_schema
from apps.chat.tools.wiki_search import search_wiki_knowledge
from apps.conversation.tooling import ToolResult, normalize_tool_result


class ClarificationOptionSchema(BaseModel):
    label: str = Field(description="Display label of this candidate option.")
    description: str = Field(default="", description="Business explanation, field name, or condition meaning of this option.")
    option_id: str = Field(default="", description="Unique identifier for this option.")


class ClarificationQuestionSchema(BaseModel):
    question: str = Field(description="The concrete business question to ask the user.")
    options: list[ClarificationOptionSchema] = Field(description="List of mutually exclusive candidate options.")
    question_id: str = Field(default="", description="Unique identifier for this question.")


class RequestClarificationInput(BaseModel):
    questions: list[ClarificationQuestionSchema] = Field(
        description="List of clarification questions to present to the user. Each item must have 'question' and 'options'."
    )


class SearchWikiInput(BaseModel):
    query: str = Field(description="Business concept, table name, caliber, or keyword to search authoritative Wiki knowledge for.")


class SearchSchemaInput(BaseModel):
    keywords: list[str] = Field(description="List of keywords or entities to search database schema for (used as fallback when Wiki is not configured).")


class PatchSqlInput(BaseModel):
    base_sql: str = Field(description="The existing valid base SQL to be modified.")
    action: str = Field(description="Action: add_dimension, add_filter, replace_filter, change_limit, change_order.")
    payload: dict[str, Any] = Field(description="Payload specific to the action, e.g. {'fields': ['dept']} or {'condition': 'status != 0'}.")


class ExecuteSqlInput(BaseModel):
    sql: str = Field(description="SQL query string to execute safely in the sandbox.")
    limit: int = Field(default=1000, description="Max rows to retrieve, default 1000.")


class CompareResultsInput(BaseModel):
    base_sql: str = Field(description="Original base SQL representing prior caliber or result.")
    new_sql: str = Field(description="New SQL representing the challenged or revised caliber.")
    hypothesis: str = Field(default="", description="The hypothesis being tested, e.g. 'Exclude cancelled orders'.")


def build_agent_tools(llm_service: Any, access_scope: Any = None) -> list[StructuredTool]:
    """Construct bound LangChain tools scoped to current LLMService and access permissions."""
    ds_id = getattr(getattr(llm_service, "ds", None), "id", None)
    has_wiki = wiki_backend_active(ds_id)

    def _search_wiki(query: str) -> dict[str, Any]:
        res = search_wiki_knowledge(llm_service, query)
        return dict(res)

    def _search_schema(keywords: list[str]) -> dict[str, Any]:
        res = search_and_inspect_schema(llm_service, keywords, access_scope=access_scope)
        return dict(res)

    def _patch_sql(base_sql: str, action: str, payload: dict[str, Any]) -> dict[str, Any]:
        dialect = getattr(getattr(llm_service, "datasource", None), "type", None)
        res = patch_and_compile_sql(base_sql, action, payload, dialect=dialect)
        return dict(res)

    def _execute_sql(sql: str, limit: int = 1000) -> dict[str, Any]:
        res = execute_sql_sandbox(llm_service, sql, access_scope=access_scope, limit=limit)
        return dict(res)

    def _compare_results(base_sql: str, new_sql: str, hypothesis: str = "") -> dict[str, Any]:
        res = compare_query_results(llm_service, base_sql, new_sql, hypothesis=hypothesis, access_scope=access_scope)
        return dict(res)

    def _request_clarification(questions: list[Any]) -> dict[str, Any]:
        raw_list = []
        for q in questions:
            if hasattr(q, "model_dump"):
                raw_list.append(q.model_dump(mode="python"))
            elif isinstance(q, dict):
                raw_list.append(q)
        res = request_clarification(raw_list)
        return dict(res)

    tools: list[StructuredTool] = []

    # Wiki is the primary knowledge source containing schema and rules
    if has_wiki:
        tools.append(
            StructuredTool.from_function(
                func=_search_wiki,
                name="search_wiki",
                description="Search authoritative Wiki knowledge containing table structures, field definitions, enum values, and business calibers.",
                args_schema=SearchWikiInput,
            )
        )
    else:
        # Fallback to physical schema search only when Wiki is not configured
        tools.append(
            StructuredTool.from_function(
                func=_search_schema,
                name="search_schema",
                description="Search table schemas and comments for relevant business entities and fields (fallback mode).",
                args_schema=SearchSchemaInput,
            )
        )

    tools.extend([
        StructuredTool.from_function(
            func=_patch_sql,
            name="patch_and_compile_sql",
            description="Incrementally patch a base SQL without full rewrite. Supports add_dimension, add_filter, replace_filter, change_order.",
            args_schema=PatchSqlInput,
        ),
        StructuredTool.from_function(
            func=_execute_sql,
            name="execute_sql_sandbox",
            description="Safely execute a SQL query in the sandboxed database and return summary statistics and sample rows.",
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
            description="Ask the user for clarification when there is significant business ambiguity that alters query results. Provide structured question and options.",
            args_schema=RequestClarificationInput,
        ),
    ])

    return tools
