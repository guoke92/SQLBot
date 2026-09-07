"""Wiki knowledge search tool for the unified agent."""

from __future__ import annotations

from typing import Any
from apps.chat.steps.wiki_recall import retrieve_wiki_context
from apps.chat.tools.base import failure_result, success_result
from apps.conversation.tooling import ToolResult
from common.utils.utils import SQLBotLogUtil


def search_wiki_knowledge(
    llm_service: Any,
    query: str,
    *,
    access_scope: Any = None,
    top_k: int = 5,
) -> ToolResult:
    """Retrieve authoritative business definitions, calibers, and table definitions from Wiki."""
    clean_query = str(query or "").strip()
    if not clean_query:
        return failure_result("Query cannot be empty for Wiki search", retryable=True)

    try:
        res = retrieve_wiki_context(
            llm_service,
            clean_query,
            access_scope=access_scope,
            top_k=top_k,
        )
        knowledge_text = res.get("knowledge_text") or res.get("schema_text") or ""
        tables = res.get("tables") or []
        backend = res.get("backend")

        if not knowledge_text.strip():
            return success_result(
                f"No knowledge found for: '{clean_query}'. Please rely on currently available tables and standard schema.",
                data={"tables": [], "knowledge_text": ""},
            )

        return success_result(
            f"Retrieved knowledge (source: {backend}, tables: {tables}).",
            data={
                "tables": tables,
                "knowledge_text": knowledge_text,
            },
        )
    except Exception as exc:
        SQLBotLogUtil.error(f"search_wiki_knowledge failed: {exc}")
        return failure_result(f"Failed to search Wiki: {exc}", retryable=True)
