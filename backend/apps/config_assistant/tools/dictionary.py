"""Dictionary-field configuration tools."""

from __future__ import annotations

from typing import Any

from langchain_core.tools import BaseTool, StructuredTool
from pydantic import BaseModel, Field

from apps.config_assistant.tools.common import require_workspace_admin
from apps.conversation.session import session_scope
from apps.conversation.tooling import ToolResult, tool_failure, tool_success
from apps.dictionary.models import DictionaryConfigCreate, DictionaryConfigUpdate
from apps.dictionary.service import (
    create_manual_config,
    get_field_option,
    list_field_options,
    refresh_configs,
    update_config,
)


class DictionaryListArgs(BaseModel):
    ds_id: int
    table_id: int | None = None


class DictionaryConfigureArgs(BaseModel):
    ds_id: int
    field_id: int
    enabled: bool = True
    max_values: int = Field(default=500, ge=1, le=5000)


class DictionaryUpdateArgs(BaseModel):
    config_id: int
    enabled: bool | None = None
    max_values: int | None = Field(default=None, ge=1, le=5000)


class DictionaryRefreshArgs(BaseModel):
    config_ids: list[int]


def build_dictionary_tools(user: Any) -> list[BaseTool]:
    oid = int(getattr(user, "oid", None) or 1)

    def list_dictionary_fields(
        ds_id: int,
        table_id: int | None = None,
    ) -> ToolResult:
        with session_scope() as session:
            options = list_field_options(
                session,
                oid=oid,
                ds_id=ds_id,
                table_id=table_id,
            )
            return tool_success(
                f"Found {len(options)} dictionary-capable fields",
                [option.model_dump() for option in options],
            )

    def configure_dictionary_field(
        ds_id: int,
        field_id: int,
        enabled: bool = True,
        max_values: int = 500,
    ) -> ToolResult:
        require_workspace_admin(user)
        with session_scope() as session:
            config = create_manual_config(
                session,
                oid=oid,
                ds_id=ds_id,
                data=DictionaryConfigCreate(
                    field_id=field_id,
                    enabled=enabled,
                    max_values=max_values,
                ),
            )
            option = get_field_option(
                session,
                oid=oid,
                config_id=int(config.id),
            )
            return tool_success(
                "Dictionary field configured",
                option.model_dump(),
            )

    def update_dictionary_config(
        config_id: int,
        enabled: bool | None = None,
        max_values: int | None = None,
    ) -> ToolResult:
        require_workspace_admin(user)
        with session_scope() as session:
            update_config(
                session,
                oid=oid,
                config_id=config_id,
                data=DictionaryConfigUpdate(enabled=enabled, max_values=max_values),
            )
            option = get_field_option(session, oid=oid, config_id=config_id)
            return tool_success(
                "Dictionary configuration updated",
                option.model_dump(),
            )

    def refresh_dictionary_values(config_ids: list[int]) -> ToolResult:
        require_workspace_admin(user)
        with session_scope() as session:
            results = refresh_configs(session, oid=oid, config_ids=config_ids)
            success_count = sum(1 for result in results if not result.error)
            data = [result.model_dump() for result in results]
            if success_count != len(results):
                failure_count = len(results) - success_count
                return tool_failure(
                    f"Refreshed {success_count}/{len(results)} dictionary fields",
                    f"{failure_count} dictionary field refreshes failed",
                    data,
                )
            return tool_success(
                f"Refreshed {success_count}/{len(results)} dictionary fields",
                data,
            )

    return [
        StructuredTool.from_function(
            func=list_dictionary_fields,
            name="list_dictionary_fields",
            description="List string fields and their dictionary configuration state.",
            args_schema=DictionaryListArgs,
        ),
        StructuredTool.from_function(
            func=configure_dictionary_field,
            name="configure_dictionary_field",
            description="Create or replace dictionary settings for one datasource field.",
            args_schema=DictionaryConfigureArgs,
        ),
        StructuredTool.from_function(
            func=update_dictionary_config,
            name="update_dictionary_config",
            description="Update an existing dictionary configuration by config id.",
            args_schema=DictionaryUpdateArgs,
        ),
        StructuredTool.from_function(
            func=refresh_dictionary_values,
            name="refresh_dictionary_values",
            description="Extract and publish current values for dictionary configurations.",
            args_schema=DictionaryRefreshArgs,
        ),
    ]
