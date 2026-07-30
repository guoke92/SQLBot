"""Configuration tool catalog assembled from focused domain adapters."""

from __future__ import annotations

from typing import Any

from langchain_core.tools import BaseTool

CONFIG_TOOL_NAMES = frozenset(
    {
        "list_datasources",
        "get_datasource",
        "create_datasource",
        "update_datasource",
        "check_datasource",
        "list_catalog_tables",
        "list_selected_tables",
        "choose_tables",
        "list_catalog_fields",
        "list_table_fields",
        "update_table_meta",
        "update_field_meta",
        "get_sample_data",
        "list_table_relations",
        "replace_table_relations",
        "list_terminologies",
        "save_terminology",
        "delete_terminologies",
        "set_terminology_enabled",
        "list_dictionary_fields",
        "configure_dictionary_field",
        "update_dictionary_config",
        "refresh_dictionary_values",
    }
)


def build_tools(user: Any) -> list[BaseTool]:
    """Return the explicit, auditable system-configuration tool catalog."""
    from apps.config_assistant.tools.dictionary import build_dictionary_tools
    from apps.config_assistant.tools.metadata import build_metadata_tools
    from apps.config_assistant.tools.relationship import build_relationship_tools
    from apps.config_assistant.tools.terminology import build_terminology_tools

    tools = [
        *build_metadata_tools(user),
        *build_relationship_tools(user),
        *build_terminology_tools(user),
        *build_dictionary_tools(user),
    ]
    actual = {tool.name for tool in tools}
    if actual != CONFIG_TOOL_NAMES or len(tools) != len(CONFIG_TOOL_NAMES):
        raise RuntimeError(
            f"Config tool catalog mismatch: missing={CONFIG_TOOL_NAMES - actual}, "
            f"unexpected={actual - CONFIG_TOOL_NAMES}, "
            f"registered={len(tools)}, unique={len(actual)}"
        )
    return tools
