"""sql_ref resolves through SqlWorkspace, not pasted SQL or memory slots."""

from __future__ import annotations

from apps.chat.agent.workspace import SqlWorkspace
from apps.chat.tools.registry import _workspace
from apps.conversation.runtime_context import (
    attach_runtime,
    detach_runtime,
    worker_scope,
)


def test_workspace_resolve_active() -> None:
    ws = SqlWorkspace()
    item = ws.add_revision("SELECT id FROM t", origin="model", status="executed")
    ws.current = item.rev
    assert ws.resolve_sql("active") == "SELECT id FROM t"
    assert ws.resolve_sql(item.rev) == "SELECT id FROM t"


def test_workspace_rejects_unknown_ref() -> None:
    ws = SqlWorkspace()
    ws.add_revision("SELECT 1", origin="model", status="executed")
    assert ws.resolve_sql("SELECT 1") == ""


def test_runtime_workspace_active() -> None:
    run_id = "run-sql-ref"
    ws = SqlWorkspace()
    item = ws.add_revision("SELECT id FROM t", origin="inherit", status="executed")
    ws.current = item.rev
    with worker_scope(run_id, "tok"):
        attach_runtime(run_id, sql_workspace=ws.model_dump(mode="json"))
        try:
            assert _workspace().resolve_sql("active") == "SELECT id FROM t"
        finally:
            detach_runtime(run_id)


def test_inherit_dataset_is_current_not_this_turn_delivery() -> None:
    ws = SqlWorkspace()
    item = ws.inherit_dataset(
        {"sql": "SELECT 1", "dataset_id": "prior", "rev": "r1", "fields": ["id"]}
    )
    assert item is not None
    assert ws.current == item.rev
    assert ws.delivered is None


def test_render_index_shows_truncation_window() -> None:
    ws = SqlWorkspace()
    item = ws.add_revision("SELECT id FROM t", status="executed")
    ws.mark_executed(
        item.rev,
        row_count=1000,
        fields=["id"],
        purpose="delivery",
        truncated=True,
        display_limit=1000,
    )
    index = ws.render_index()
    assert "1000 行" in index
    assert "截断前 1000" in index
