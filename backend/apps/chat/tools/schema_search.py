"""Schema and catalog search tool for the unified agent."""

from __future__ import annotations

from typing import Any, Sequence
from sqlmodel import Session

from apps.chat.steps.schema import match_table_schema
from apps.chat.tools.base import failure_result, success_result
from apps.conversation.session import session_scope
from apps.conversation.tooling import ToolResult


def search_and_inspect_schema(
    llm_service: Any,
    keywords: Sequence[str],
    *,
    access_scope: Any = None,
    table_limit: int = 6,
) -> ToolResult:
    """Retrieve database schema and field descriptions relevant to user concepts."""
    clean_keywords = [str(k).strip() for k in keywords if str(k).strip()]
    if not clean_keywords:
        return failure_result("Keywords cannot be empty for schema search", retryable=True)

    try:
        with session_scope() as session:
            # Match tables using existing schema step
            table_names = match_table_schema(
                llm_service,
                session,
                access_scope=access_scope,
                table_limit=table_limit,
                audit=False,
            )
            schema_text = str(getattr(llm_service.chat_question, "db_schema", "") or "")

        return success_result(
            f"Retrieved schema for tables: {list(table_names)}",
            data={
                "tables": list(table_names),
                "schema_text": schema_text,
                "keywords": clean_keywords,
            },
        )
    except Exception as exc:
        return failure_result(f"Failed to search schema: {exc}", retryable=True)
