"""Config-assistant tools for metadata cognition (refresh / confirm)."""

from __future__ import annotations

from typing import Any

from langchain_core.tools import BaseTool, StructuredTool
from pydantic import BaseModel, Field
from sqlmodel import select

from apps.config_assistant.tools.common import require_workspace_admin
from apps.conversation.session import session_scope
from apps.conversation.tooling import tool_failure, tool_success
from apps.datasource.models.datasource import CoreDatasource, CoreTable
from apps.datasource.profiling.models import FieldRelation, RelationStatus, ScanRunMode
from apps.datasource.profiling.service import (
    ALLOWED_RUN_MODES,
    build_profile_brief,
    decide_field_relation,
    enqueue_manual_refresh,
    schedule_worker_kick,
)


class DsArgs(BaseModel):
    ds_id: int = Field(description="Datasource id")


class RefreshArgs(BaseModel):
    ds_id: int
    table_id: int | None = None
    run_mode: str = ScanRunMode.FACTS_ONLY.value


class RelationDecisionArgs(BaseModel):
    relation_id: int
    status: str = Field(description="CONFIRMED or REJECTED")


def build_profiling_tools(user: Any) -> list[BaseTool]:
    def get_profile_brief(ds_id: int) -> dict[str, Any]:
        require_workspace_admin(user)
        with session_scope() as session:
            ds = session.get(CoreDatasource, ds_id)
            if ds is None or int(ds.oid or 1) != int(getattr(user, "oid", None) or 1):
                return tool_failure("brief failed", "datasource not found")
            return tool_success(
                "profile brief",
                build_profile_brief(session, ds_id=int(ds.id)),
            )

    def refresh_metadata_profile(
        ds_id: int,
        table_id: int | None = None,
        run_mode: str = ScanRunMode.FACTS_ONLY.value,
    ) -> dict[str, Any]:
        require_workspace_admin(user)
        with session_scope() as session:
            ds = session.get(CoreDatasource, ds_id)
            if ds is None or int(ds.oid or 1) != int(getattr(user, "oid", None) or 1):
                return tool_failure("refresh failed", "datasource not found")
            mode = (run_mode or ScanRunMode.FACTS_ONLY.value).strip()
            if mode not in ALLOWED_RUN_MODES:
                return tool_failure("refresh failed", f"invalid run_mode={mode}")
            stmt = select(CoreTable).where(
                CoreTable.ds_id == ds_id, CoreTable.checked == True  # noqa: E712
            )
            tables = list(session.exec(stmt).all())
            if table_id is not None:
                tables = [
                    t for t in tables if t.id is not None and int(t.id) == int(table_id)
                ]
            runs = enqueue_manual_refresh(
                session, ds=ds, tables=tables, run_mode=mode
            )
            schedule_worker_kick()
            return tool_success(
                "profiling enqueued",
                {"count": len(runs), "run_mode": mode, "run_ids": [r.id for r in runs]},
            )

    def decide_field_relation_tool(relation_id: int, status: str) -> dict[str, Any]:
        require_workspace_admin(user)
        with session_scope() as session:
            row = session.get(FieldRelation, relation_id)
            if row is None:
                return tool_failure("decision failed", "relation not found")
            ds = session.get(CoreDatasource, row.ds_id)
            if ds is None or int(ds.oid or 1) != int(getattr(user, "oid", None) or 1):
                return tool_failure("decision failed", "datasource not found")
            wanted = (status or "").upper()
            if wanted not in {
                RelationStatus.CONFIRMED.value,
                RelationStatus.REJECTED.value,
            }:
                return tool_failure(
                    "decision failed", "status must be CONFIRMED or REJECTED"
                )
            try:
                updated = decide_field_relation(
                    session,
                    relation_id=relation_id,
                    status=wanted,
                    confirmed_by=int(getattr(user, "id", 0) or 0),
                )
            except (ValueError, LookupError) as exc:
                return tool_failure("decision failed", str(exc))
            return tool_success(
                f"relation {updated.status}",
                {"id": updated.id, "status": updated.status},
            )

    return [
        StructuredTool.from_function(
            func=get_profile_brief,
            name="get_profile_brief",
            description="Get published profile brief for a datasource.",
            args_schema=DsArgs,
        ),
        StructuredTool.from_function(
            func=refresh_metadata_profile,
            name="refresh_metadata_profile",
            description="Enqueue metadata profiling for tables.",
            args_schema=RefreshArgs,
        ),
        StructuredTool.from_function(
            func=decide_field_relation_tool,
            name="decide_field_relation",
            description="Confirm or reject a candidate field relation.",
            args_schema=RelationDecisionArgs,
        ),
    ]
