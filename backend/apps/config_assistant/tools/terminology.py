"""Terminology configuration tools backed by the existing terminology domain."""

from __future__ import annotations

from typing import Any

from langchain_core.tools import BaseTool, StructuredTool
from pydantic import BaseModel, Field

from apps.config_assistant.tools.common import (
    require_datasource_scope,
    require_workspace_admin,
    translator_for,
)
from apps.conversation.session import session_scope
from apps.conversation.tooling import ToolResult, tool_success
from apps.datasource.crud.datasource import get_ds
from apps.terminology.curd.terminology import (
    create_terminology,
    delete_terminology,
    enable_terminology,
    get_all_terminology,
    update_terminology,
)
from apps.terminology.models.terminology_model import Terminology, TerminologyInfo


class TerminologyListArgs(BaseModel):
    word: str | None = Field(default=None, description="Optional word filter")


class TerminologySaveArgs(BaseModel):
    id: int | None = Field(default=None, description="Terminology id when updating")
    word: str = Field(description="Canonical terminology word")
    description: str = Field(description="Business definition")
    other_words: list[str] = Field(default_factory=list, description="Synonyms")
    datasource_ids: list[int] = Field(
        default_factory=list,
        description="Datasource scope; empty means all datasources",
    )
    enabled: bool = Field(default=True)


class TerminologyIdsArgs(BaseModel):
    ids: list[int] = Field(description="Terminology ids")


class TerminologyEnableArgs(BaseModel):
    id: int
    enabled: bool


def build_terminology_tools(user: Any) -> list[BaseTool]:
    oid = int(getattr(user, "oid", None) or 1)

    def require_owned_ids(session: Any, ids: list[int]) -> None:
        owned = {
            int(row.id)
            for row in session.query(Terminology)
            .filter(
                Terminology.oid == oid,
                Terminology.pid.is_(None),
                Terminology.id.in_(ids),
            )
            .all()
        }
        missing = set(ids) - owned
        if missing:
            raise ValueError(f"Terminology not found: {sorted(missing)}")

    def list_terminologies(word: str | None = None) -> ToolResult:
        with session_scope() as session:
            rows = get_all_terminology(session, word, oid=oid)
            data = [
                {
                    "id": row.id,
                    "word": row.word,
                    "description": row.description,
                    "other_words": row.other_words or [],
                    "specific_ds": row.specific_ds,
                    "datasource_ids": row.datasource_ids or [],
                    "datasource_names": row.datasource_names or [],
                    "enabled": row.enabled,
                }
                for row in rows[:200]
            ]
            return tool_success(
                f"Found {len(data)} terminology entries",
                data,
            )

    def save_terminology(
        word: str,
        description: str,
        id: int | None = None,
        other_words: list[str] | None = None,
        datasource_ids: list[int] | None = None,
        enabled: bool = True,
    ) -> ToolResult:
        require_workspace_admin(user)
        scoped_ids = datasource_ids or []
        with session_scope() as session:
            for ds_id in scoped_ids:
                require_datasource_scope(user, get_ds(session, ds_id))
            info = TerminologyInfo(
                id=id,
                word=word,
                description=description,
                other_words=other_words or [],
                specific_ds=bool(scoped_ids),
                datasource_ids=scoped_ids,
                enabled=enabled,
            )
            result_id = (
                update_terminology(session, info, oid, translator_for(user))
                if id is not None
                else create_terminology(session, info, oid, translator_for(user))
            )
            return tool_success(
                "Terminology updated" if id is not None else "Terminology created",
                {
                    "id": result_id,
                    "word": info.word,
                    "description": info.description,
                    "other_words": info.other_words,
                    "specific_ds": info.specific_ds,
                    "datasource_ids": info.datasource_ids,
                    "enabled": info.enabled,
                },
            )

    def delete_terminologies(ids: list[int]) -> ToolResult:
        require_workspace_admin(user)
        with session_scope() as session:
            require_owned_ids(session, ids)
            delete_terminology(session, ids)
        return tool_success(
            f"Deleted {len(ids)} terminology entries",
            {"ids": ids},
        )

    def set_terminology_enabled(id: int, enabled: bool) -> ToolResult:
        require_workspace_admin(user)
        with session_scope() as session:
            require_owned_ids(session, [id])
            enable_terminology(session, id, enabled, translator_for(user))
        return tool_success(
            f"Terminology {'enabled' if enabled else 'disabled'}",
            {"id": id, "enabled": enabled},
        )

    return [
        StructuredTool.from_function(
            func=list_terminologies,
            name="list_terminologies",
            description="List terminology definitions in the current workspace.",
            args_schema=TerminologyListArgs,
        ),
        StructuredTool.from_function(
            func=save_terminology,
            name="save_terminology",
            description="Create or update one terminology definition and its synonyms.",
            args_schema=TerminologySaveArgs,
        ),
        StructuredTool.from_function(
            func=delete_terminologies,
            name="delete_terminologies",
            description="Delete terminology definitions by id.",
            args_schema=TerminologyIdsArgs,
        ),
        StructuredTool.from_function(
            func=set_terminology_enabled,
            name="set_terminology_enabled",
            description="Enable or disable one terminology definition.",
            args_schema=TerminologyEnableArgs,
        ),
    ]
