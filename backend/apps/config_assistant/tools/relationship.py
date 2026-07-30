"""Table-relation configuration tools."""

from __future__ import annotations

from typing import Any

from langchain_core.tools import BaseTool, StructuredTool
from pydantic import BaseModel, Field

from apps.config_assistant.tools.common import require_workspace_admin
from apps.conversation.session import session_scope
from apps.conversation.tooling import ToolResult, tool_success
from apps.datasource.relation_service import (
    field_relations_from_graph,
    get_relation_graph,
    replace_field_relations,
)


class RelationListArgs(BaseModel):
    ds_id: int = Field(description="Datasource id")


class FieldRelation(BaseModel):
    source_field_id: int = Field(description="Source CoreField id")
    target_field_id: int = Field(description="Target CoreField id")


class RelationReplaceArgs(BaseModel):
    ds_id: int = Field(description="Datasource id")
    relations: list[FieldRelation] = Field(
        description="Complete set of directed field relationships"
    )


def build_relationship_tools(user: Any) -> list[BaseTool]:
    oid = int(getattr(user, "oid", None) or 1)

    def list_table_relations(ds_id: int) -> ToolResult:
        with session_scope() as session:
            graph = get_relation_graph(session, oid=oid, ds_id=ds_id)
            relations = field_relations_from_graph(graph)
            return tool_success(
                f"Found {len(relations)} relations",
                relations,
            )

    def replace_table_relations(
        ds_id: int,
        relations: list[FieldRelation],
    ) -> ToolResult:
        require_workspace_admin(user)
        payload = [
            relation.model_dump() if hasattr(relation, "model_dump") else dict(relation)
            for relation in relations
        ]
        with session_scope() as session:
            graph = replace_field_relations(
                session,
                oid=oid,
                ds_id=ds_id,
                relations=payload,
            )
            persisted = field_relations_from_graph(graph)
        return tool_success(
            f"Replaced table relationships with {len(persisted)} relations",
            persisted,
        )

    return [
        StructuredTool.from_function(
            func=list_table_relations,
            name="list_table_relations",
            description="List configured field relationships for a datasource.",
            args_schema=RelationListArgs,
        ),
        StructuredTool.from_function(
            func=replace_table_relations,
            name="replace_table_relations",
            description=(
                "Replace the complete field-relationship set for a datasource. "
                "Use list_table_relations first when preserving existing relations."
            ),
            args_schema=RelationReplaceArgs,
        ),
    ]
