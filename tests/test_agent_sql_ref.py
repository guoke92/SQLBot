"""sql_ref handle resolution for patch / compare."""

from __future__ import annotations

from apps.chat.agent.tools.sql_ref import resolve_sql_handle
from apps.conversation.runtime_context import (
    attach_runtime,
    detach_runtime,
    worker_scope,
)


def test_resolve_sql_handle_prefers_explicit_sql() -> None:
    assert resolve_sql_handle(sql="SELECT 1", sql_ref="active") == "SELECT 1"


def test_resolve_sql_handle_active_from_memory_slots() -> None:
    run_id = "run-sql-ref"
    with worker_scope(run_id, "tok"):
        attach_runtime(
            run_id,
            memory_slots={"active_baseline_sql": "SELECT id FROM t"},
        )
        try:
            assert resolve_sql_handle(sql_ref="active") == "SELECT id FROM t"
        finally:
            detach_runtime(run_id)
