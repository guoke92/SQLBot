"""Wiki knowledge and business catalog search tool for the unified agent."""

from __future__ import annotations

from typing import Any, Sequence
from apps.chat.steps.wiki_recall import (
    _store,
    datasource_databases,
    wiki_backend_active,
    wiki_business_recall,
)
from apps.chat.steps.wiki_schema import WikiSchemaRenderer
from apps.chat.tools.base import failure_result, success_result
from apps.conversation.tooling import ToolResult
from apps.knowledge.wiki.anchors import closure_tables
from common.utils.utils import SQLBotLogUtil


def search_wiki_knowledge(
    llm_service: Any,
    query: str,
    *,
    top_k: int = 5,
) -> ToolResult:
    """Retrieve authoritative business definitions, calibers, state machines, and table definitions from Wiki."""
    clean_query = str(query or "").strip()
    if not clean_query:
        return failure_result("Query cannot be empty for Wiki search", retryable=True)

    ds_id = getattr(getattr(llm_service, "ds", None), "id", None)
    if not wiki_backend_active(ds_id):
        return failure_result("Wiki knowledge backend is not active or available for this datasource", retryable=False)

    try:
        databases = datasource_databases(getattr(llm_service, "ds", None))
        res = wiki_business_recall(clean_query, ds_id=ds_id, databases=databases, top_k=top_k)
        if not res or not res.text:
            return success_result(
                f"No matching Wiki pages found for: {clean_query}",
                data={"pages": [], "text": "", "tables": []},
            )

        # Include table structures rendered from Wiki anchors so Agent has complete table/field definitions
        store = _store()
        schema_segment = ""
        tables: list[str] = []
        if store is not None:
            closure, _ = closure_tables(store, res.page_keys)
            if closure:
                tables = list(closure)
                renderer = WikiSchemaRenderer.from_store(store)
                if renderer:
                    raw_schema = renderer.render(closure)
                    lines = raw_schema.splitlines()
                    compact_lines = []
                    for line in lines:
                        if line.startswith("## ") or "topk=" in line or any(k in line for k in ["Id", "时间", "状态", "名称", "类型", "方式", "来源", "编码", "金额", "部门", "日期"]):
                            compact_lines.append(line)
                    header = "\n\n### 【权威表结构与字段定义（已完整提供，严禁重复查表结构）】：\n"
                    schema_segment = header + "\n".join(compact_lines)

        full_knowledge = res.text + schema_segment

        return success_result(
            f"Retrieved Wiki knowledge ({len(res.page_keys)} pages: {list(res.page_keys)[:4]}, tables: {tables}). Table structures are fully provided.",
            data={
                "page_keys": list(res.page_keys),
                "tables": tables,
                "knowledge_text": full_knowledge,
            },
        )
    except Exception as exc:
        SQLBotLogUtil.error(f"search_wiki_knowledge failed: {exc}")
        return failure_result(f"Failed to search Wiki: {exc}", retryable=True)
