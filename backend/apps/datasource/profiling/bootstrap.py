"""Deterministic bootstrap for facts_only / pre-agent profiling."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlmodel import Session, select

from apps.datasource.models.datasource import CoreDatasource, CoreField, CoreTable
from apps.datasource.profiling.models import (
    FieldProfileSnapshot,
    MetadataScanRun,
    ProfileStatus,
)
from apps.datasource.profiling.service import (
    apply_ddl_constraints_for_table,
    publish_table_profile_generation,
    resolve_table_mining_policy,
)
from apps.protocol.base import CAP_FIELD_PROFILE
from apps.protocol.registry import get_protocol_for_ds
from common.utils.utils import SQLBotLogUtil


def _clear_profiling_without_new_snapshots(
    session: Session, *, table: CoreTable, commit: bool = True
) -> None:
    """Leave PROFILING when facts skip field_profile (custom/lite variants)."""
    now = datetime.now()
    if table.profile_status == ProfileStatus.PROFILING.value:
        if int(table.active_profile_generation or 0) > 0:
            table.profile_status = ProfileStatus.READY.value
        else:
            # Structure/DDL-only tables are usable without snapshots.
            table.profile_status = ProfileStatus.READY.value
        table.profile_error = None
        table.profile_updated_at = now
        session.add(table)
        if commit:
            session.commit()


def run_facts_bootstrap(
    session: Session,
    *,
    run: MetadataScanRun,
) -> dict[str, Any]:
    """Refresh catalog stats, field profiles, and DDL FK relations for one table."""
    ds = session.get(CoreDatasource, run.ds_id)
    if ds is None:
        raise ValueError(f"datasource {run.ds_id} not found")
    if run.table_id is None:
        raise ValueError("facts bootstrap requires table_id")
    table = session.get(CoreTable, run.table_id)
    if table is None:
        raise ValueError(f"table {run.table_id} not found")

    policy = resolve_table_mining_policy(session, ds=ds, table=table)
    facts_caps = set(policy.facts_caps)

    from apps.datasource.crud.catalog_stats import refresh_table_stats

    if "catalog_stats" in facts_caps:
        try:
            refresh_table_stats(session, ds, [table])
            session.refresh(table)
        except Exception as exc:
            SQLBotLogUtil.warning(
                f"catalog stats bootstrap failed table={table.id}: {exc}"
            )

    fk_count = 0
    if "ddl_constraints" in facts_caps:
        fk_count = apply_ddl_constraints_for_table(
            session, ds=ds, table=table, commit=True
        )
        session.refresh(table)

    proto = get_protocol_for_ds(ds)
    generation = int(
        run.pending_generation or (int(table.active_profile_generation or 0) + 1)
    )
    fields = session.exec(
        select(CoreField).where(
            CoreField.table_id == table.id,
            CoreField.checked == True,  # noqa: E712
        )
    ).all()

    if "field_profile" not in facts_caps:
        _clear_profiling_without_new_snapshots(session, table=table, commit=True)
        session.refresh(table)
        return {
            "status": table.profile_status or ProfileStatus.READY.value,
            "fields": 0,
            "fk_count": fk_count,
            "skipped_field_profile": True,
            "published": False,
            "facts_caps": sorted(facts_caps),
        }

    if not proto.supports(CAP_FIELD_PROFILE):
        publish_table_profile_generation(
            session,
            table=table,
            generation=int(table.active_profile_generation or 0),
            unsupported=True,
            commit=True,
        )
        return {
            "status": ProfileStatus.UNSUPPORTED.value,
            "fields": 0,
            "fk_count": fk_count,
            "published": False,
            "facts_caps": sorted(facts_caps),
        }

    # Consume gate: PROFILING while remote work runs (STALE → PROFILING).
    table.profile_status = ProfileStatus.PROFILING.value
    table.profile_error = None
    session.add(table)
    session.commit()

    # Detach before remote probes to avoid long local TX.
    ds_id = int(ds.id)
    table_id = int(table.id)
    table_name = table.table_name
    database_name = table.database_name
    run_id = int(run.id) if run.id is not None else None
    lease_owner = (run.lease_owner or "").strip()
    field_payload = [
        {
            "id": int(f.id),
            "name": f.field_name,
            "type": f.field_type,
        }
        for f in fields
        if f.id is not None and f.field_name
    ]
    session.expunge(ds)
    session.rollback()

    from apps.datasource.profiling.service import renew_run_lease

    snapshots: list[dict[str, Any]] = []
    errors: list[str] = []
    for index, item in enumerate(field_payload):
        if run_id is not None and lease_owner and index > 0 and index % 5 == 0:
            # Thin heartbeat so wide tables do not lose the lease mid-run.
            renew_run_lease(session, run_id=run_id, worker_id=lease_owner)
        try:
            result = proto.profile_field(
                ds,
                resource=table_name,
                field=item["name"],
                field_type=item.get("type"),
                database_name=database_name,
            )
            if not result.supported:
                errors.append(f"{item['name']}: {result.error or 'unsupported'}")
                continue
            if result.error:
                errors.append(f"{item['name']}: {result.error}")
            snapshots.append(
                {
                    "field_id": item["id"],
                    "row_count": result.row_count,
                    "non_null_count": result.non_null_count,
                    "null_rate": result.null_rate,
                    "approx_distinct": result.approx_distinct,
                    "distinct_ratio": result.distinct_ratio,
                    "min_value": result.min_value,
                    "max_value": result.max_value,
                    "top_values": result.top_values,
                    "sample_method": result.sample_method,
                    "sample_size": result.sample_size,
                    "error": result.error,
                }
            )
        except Exception as exc:
            errors.append(f"{item['name']}: {exc}")

    # Re-load local rows after remote work.
    table = session.get(CoreTable, table_id)
    ds = session.get(CoreDatasource, ds_id)
    if table is None or ds is None:
        raise ValueError("table/datasource disappeared during profiling")

    now = datetime.now()
    # Idempotent replace for retries / concurrent claims of the same generation.
    prior = session.exec(
        select(FieldProfileSnapshot).where(
            FieldProfileSnapshot.table_id == table_id,
            FieldProfileSnapshot.generation == generation,
            FieldProfileSnapshot.window_code == "ALL",
        )
    ).all()
    for row in prior:
        session.delete(row)
    session.flush()

    for snap in snapshots:
        row = FieldProfileSnapshot(
            scan_id=int(run.id) if run.id is not None else None,
            ds_id=ds_id,
            table_id=table_id,
            field_id=int(snap["field_id"]),
            generation=generation,
            window_code="ALL",
            row_count=snap.get("row_count"),
            non_null_count=snap.get("non_null_count"),
            null_rate=snap.get("null_rate"),
            approx_distinct=snap.get("approx_distinct"),
            distinct_ratio=snap.get("distinct_ratio"),
            min_value=snap.get("min_value"),
            max_value=snap.get("max_value"),
            top_values=snap.get("top_values"),
            sample_method=snap.get("sample_method"),
            sample_size=snap.get("sample_size"),
            status="READY" if not snap.get("error") else "FAILED",
            error=snap.get("error"),
            profiled_at=now,
        )
        session.add(row)

    ok_snapshots = [s for s in snapshots if not s.get("error")]
    attempted = len(field_payload)
    published = publish_table_profile_generation(
        session,
        table=table,
        generation=generation,
        success_count=len(ok_snapshots),
        attempted_count=attempted,
        error="; ".join(errors[:5]) if errors else None,
        commit=False,
    )
    if not published and ok_snapshots == []:
        # Drop empty failed attempt so retries can reuse the generation cleanly.
        failed_rows = session.exec(
            select(FieldProfileSnapshot).where(
                FieldProfileSnapshot.table_id == table_id,
                FieldProfileSnapshot.generation == generation,
            )
        ).all()
        for row in failed_rows:
            session.delete(row)
    session.commit()
    session.refresh(table)
    # Profile publish updates PROMPT/Brief only. RANK embeddings index structure
    # (see apps.datasource.schema_text) and refresh on catalog/comment sync.
    status = table.profile_status or ProfileStatus.FAILED.value
    return {
        "status": status,
        "fields": len(ok_snapshots),
        "fk_count": fk_count,
        "errors": errors[:20],
        "generation": int(table.active_profile_generation or 0),
        "published": bool(published),
        "facts_caps": sorted(facts_caps),
    }
