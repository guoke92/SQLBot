"""Resolve sql_ref handles to a SQL string for patch / compare / continue."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from apps.chat.delivery import select_delivery_datasets
from apps.conversation.process_timeline import load_result_datasets
from apps.conversation.runtime_context import current_worker_identity, peek_runtime
from apps.conversation.session import session_scope


def resolve_sql_handle(
    *,
    sql: str = "",
    sql_ref: str = "",
) -> str:
    """Prefer explicit SQL; otherwise ``active`` or a ``dataset_id`` handle."""
    explicit = str(sql or "").strip()
    if explicit:
        return explicit
    ref = str(sql_ref or "active").strip() or "active"
    run_id, _token = current_worker_identity()
    snap: dict[str, Any] = peek_runtime(run_id) if run_id else {}
    slots = (
        snap.get("memory_slots")
        if isinstance(snap.get("memory_slots"), Mapping)
        else {}
    )
    if ref in {"active", "*"}:
        baseline = str((slots or {}).get("active_baseline_sql") or "").strip()
        if baseline:
            return baseline
        return _sql_from_datasets(run_id, dataset_id=None)
    from_outline = (slots or {}).get("active_dataset_outline")
    if (
        isinstance(from_outline, Mapping)
        and str(from_outline.get("dataset_id") or "") == ref
    ):
        sql_from_outline = str((slots or {}).get("active_baseline_sql") or "").strip()
        if sql_from_outline:
            return sql_from_outline
    return _sql_from_datasets(run_id, dataset_id=ref)


def _sql_from_datasets(run_id: str | None, *, dataset_id: str | None) -> str:
    if not run_id:
        return ""
    try:
        with session_scope() as session:
            rows = load_result_datasets(session, run_id)
    except Exception:
        return ""
    if dataset_id:
        for item in rows:
            if str(getattr(item, "dataset_id", "") or "") == dataset_id:
                snapshot = getattr(item, "schema_snapshot", None) or {}
                if isinstance(snapshot, Mapping):
                    return str(snapshot.get("sql") or "").strip()
        return ""
    delivered = select_delivery_datasets(rows)
    if not delivered:
        return ""
    snapshot = getattr(delivered[-1], "schema_snapshot", None) or {}
    if isinstance(snapshot, Mapping):
        return str(snapshot.get("sql") or "").strip()
    return ""
