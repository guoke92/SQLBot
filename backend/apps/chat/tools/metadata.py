"""Metadata for agent deterministic tools.

Display copy lives in i18n (`chat.timeline.tool.<name>`); this module only
stores stable keys and icons.
"""

from __future__ import annotations

AGENT_TOOLS_METADATA: dict[str, dict[str, str]] = {
    "execute_sql_sandbox": {
        "title_key": "chat.timeline.tool.execute_sql_sandbox",
        "icon": "sql",
    },
    "patch_and_compile_sql": {
        "title_key": "chat.timeline.tool.patch_and_compile_sql",
        "icon": "edit",
    },
    "compare_results": {
        "title_key": "chat.timeline.tool.compare_results",
        "icon": "compare",
    },
    "get_table_schema": {
        "title_key": "chat.timeline.tool.get_table_schema",
        "icon": "schema",
    },
    "get_table_relations": {
        "title_key": "chat.timeline.tool.get_table_relations",
        "icon": "relation",
    },
    "search_knowledge": {
        "title_key": "chat.timeline.tool.search_knowledge",
        "icon": "book",
    },
    "get_dict_values": {
        "title_key": "chat.timeline.tool.get_dict_values",
        "icon": "book",
    },
    "search_wiki": {
        "title_key": "chat.timeline.tool.search_wiki",
        "icon": "book",
    },
    "prepare_wiki": {
        "title_key": "chat.timeline.tool.prepare_wiki",
        "icon": "book",
    },
    "request_clarification": {
        "title_key": "chat.timeline.tool.request_clarification",
        "icon": "question",
    },
    "complete_without_sql": {
        "title_key": "chat.timeline.tool.complete_without_sql",
        "icon": "answer",
    },
    "restore_wiki": {
        "title_key": "chat.timeline.tool.restore_wiki",
        "icon": "book",
    },
}


def get_tool_title_key(tool_name: str) -> str:
    meta = AGENT_TOOLS_METADATA.get(tool_name)
    if meta:
        return meta["title_key"]
    return "chat.timeline.tool.generic"
