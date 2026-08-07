"""Enqueue, publish, and brief APIs for metadata cognition."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

from sqlalchemy import and_, or_
from sqlmodel import Session, select

from apps.datasource.models.datasource import CoreDatasource, CoreField, CoreTable
from apps.datasource.profiling.fingerprint import table_schema_fingerprint
from apps.datasource.schema_text import (  # noqa: F401 — re-export for callers
    SchemaTextPurpose,
    render_table_schema_text,
)
from apps.datasource.profiling.models import (
    FieldProfileSnapshot,
    FieldRelation,
    MetadataScanRun,
    ProfileStatus,
    RelationKind,
    RelationSource,
    RelationStatus,
    ScanRunMode,
    ScanRunStatus,
    ScanTrigger,
)
from common.utils.utils import SQLBotLogUtil

LEASE_SECONDS = 600
DEFAULT_MAX_ATTEMPTS = 3
PROFILE_HISTORY_GENERATIONS = 3
# Require at least half of attempted fields to succeed before publishing a generation.
PROFILE_MIN_SUCCESS_RATIO = 0.5
ALLOWED_RUN_MODES = frozenset(m.value for m in ScanRunMode)


def enqueue_table_scan(
    session: Session,
    *,
    ds: CoreDatasource,
    table: CoreTable,
    run_mode: str = ScanRunMode.FACTS_ONLY.value,
    trigger: str = ScanTrigger.TABLE_ADDED.value,
    targets: dict[str, Any] | None = None,
    commit: bool = True,
    skip_if_unchanged: bool = False,
    dedupe: bool = True,
) -> MetadataScanRun | None:
    """Create a pending scan run. Returns None when skipped by fingerprint/dedupe."""
    now = datetime.now()
    fields = session.exec(
        select(CoreField).where(CoreField.table_id == table.id)
    ).all()
    new_fp = table_schema_fingerprint(table, fields)
    old_fp = table.schema_fingerprint
    mode = (run_mode or ScanRunMode.FACTS_ONLY.value).strip()
    had_published = int(table.active_profile_generation or 0) > 0
    fp_changed = bool(old_fp and old_fp != new_fp)
    facts_modes = {
        ScanRunMode.FACTS_ONLY.value,
        ScanRunMode.FULL.value,
    }

    if (
        skip_if_unchanged
        and mode == ScanRunMode.FACTS_ONLY.value
        and table.profile_status == ProfileStatus.READY.value
        and had_published
        and old_fp
        and old_fp == new_fp
    ):
        table.schema_fingerprint = new_fp
        session.add(table)
        if commit:
            session.commit()
        return None

    if dedupe and table.id is not None:
        active = session.exec(
            select(MetadataScanRun)
            .where(
                MetadataScanRun.table_id == int(table.id),
                MetadataScanRun.run_mode == mode,
                MetadataScanRun.status.in_(  # type: ignore[attr-defined]
                    [
                        ScanRunStatus.PENDING.value,
                        ScanRunStatus.RUNNING.value,
                    ]
                ),
            )
            .order_by(MetadataScanRun.id.desc())
        ).first()
        if active is not None:
            return active

    table.schema_fingerprint = new_fp
    if had_published and fp_changed:
        # Structure drifted: published stats are no longer trustworthy for PROMPT.
        table.profile_status = ProfileStatus.STALE.value
        table.profile_error = "schema fingerprint changed; awaiting reprofile"
    elif mode in facts_modes or not had_published:
        table.profile_status = ProfileStatus.PROFILING.value
        table.profile_error = None
    # SEMANTIC / VALIDATE / MANUAL on READY facts: leave status alone.
    session.add(table)
    # Only facts/full runs allocate a new profile generation slot.
    if mode in facts_modes:
        pending_generation = int(table.active_profile_generation or 0) + 1
    else:
        pending_generation = int(table.active_profile_generation or 0) or None
    run = MetadataScanRun(
        oid=int(ds.oid or 1),
        ds_id=int(ds.id),
        table_id=int(table.id) if table.id is not None else None,
        run_mode=mode,
        trigger=trigger,
        status=ScanRunStatus.PENDING.value,
        attempt=0,
        max_attempts=DEFAULT_MAX_ATTEMPTS,
        targets=targets,
        schema_fingerprint=new_fp,
        pending_generation=pending_generation,
        create_time=now,
        update_time=now,
    )
    session.add(run)
    if commit:
        session.commit()
        session.refresh(run)
    else:
        session.flush()
    return run


def enqueue_tables_after_sync(
    session: Session,
    *,
    ds: CoreDatasource,
    tables: list[CoreTable],
    trigger: str = ScanTrigger.SCHEMA_SYNC.value,
    run_mode: str = ScanRunMode.FACTS_ONLY.value,
    skip_if_unchanged: bool = True,
) -> list[MetadataScanRun]:
    runs: list[MetadataScanRun] = []
    for table in tables:
        if table.id is None:
            continue
        run = enqueue_table_scan(
            session,
            ds=ds,
            table=table,
            run_mode=run_mode,
            trigger=trigger,
            commit=False,
            skip_if_unchanged=skip_if_unchanged,
        )
        if run is not None:
            runs.append(run)
    session.commit()
    for run in runs:
        session.refresh(run)
    return runs


def enqueue_manual_refresh(
    session: Session,
    *,
    ds: CoreDatasource,
    tables: list[CoreTable],
    run_mode: str = ScanRunMode.FACTS_ONLY.value,
) -> list[MetadataScanRun]:
    """Admin/API refresh: always enqueue (no fingerprint skip)."""
    mode = (run_mode or ScanRunMode.FACTS_ONLY.value).strip()
    if mode not in ALLOWED_RUN_MODES:
        raise ValueError(f"invalid run_mode={mode}")
    return enqueue_tables_after_sync(
        session,
        ds=ds,
        tables=tables,
        trigger=ScanTrigger.MANUAL.value,
        run_mode=mode,
        skip_if_unchanged=False,
    )


def claim_next_run(
    session: Session,
    *,
    worker_id: str,
    lease_seconds: int = LEASE_SECONDS,
) -> MetadataScanRun | None:
    """Claim one runnable scan. Exhausted attempts are failed and skipped."""
    now = datetime.now()
    expired = or_(
        MetadataScanRun.lease_until.is_(None),  # type: ignore[union-attr]
        MetadataScanRun.lease_until < now,
    )
    runnable = or_(
        MetadataScanRun.status == ScanRunStatus.PENDING.value,
        and_(
            MetadataScanRun.status == ScanRunStatus.RUNNING.value,
            expired,
        ),
    )
    # Drain poison-pill rows (max attempts) without stopping the worker loop.
    for _ in range(32):
        run = session.exec(
            select(MetadataScanRun)
            .where(runnable)
            .order_by(MetadataScanRun.id.asc())
            .with_for_update(skip_locked=True)
            .limit(1)
        ).first()
        if run is None:
            return None
        if int(run.attempt or 0) >= int(run.max_attempts or DEFAULT_MAX_ATTEMPTS):
            run.status = ScanRunStatus.FAILED.value
            run.error = run.error or "max attempts exceeded"
            run.update_time = now
            run.finished_at = now
            run.lease_until = None
            session.add(run)
            _mark_table_failed(session, run)
            session.commit()
            continue
        # Lease reclaim of an expired RUNNING job is not a failure — do not burn attempts.
        is_fresh_claim = run.status == ScanRunStatus.PENDING.value
        run.status = ScanRunStatus.RUNNING.value
        if is_fresh_claim:
            run.attempt = int(run.attempt or 0) + 1
        run.lease_owner = worker_id
        run.lease_until = now + timedelta(seconds=lease_seconds)
        run.started_at = run.started_at or now
        run.update_time = now
        run.error = None
        session.add(run)
        session.commit()
        session.refresh(run)
        return run
    return None


def _mark_table_failed(session: Session, run: MetadataScanRun) -> None:
    if run.table_id is None:
        return
    table = session.get(CoreTable, run.table_id)
    if table is None:
        return
    # Do not resurrect READY after a failed refresh — prior bits may be drifted.
    if table.profile_status in {
        ProfileStatus.PROFILING.value,
        ProfileStatus.STALE.value,
    }:
        if int(table.active_profile_generation or 0) > 0:
            table.profile_status = ProfileStatus.STALE.value
        else:
            table.profile_status = ProfileStatus.FAILED.value
        table.profile_error = run.error
        session.add(table)


def renew_run_lease(
    session: Session,
    *,
    run_id: int,
    worker_id: str,
    lease_seconds: int = LEASE_SECONDS,
) -> bool:
    """Extend lease for the owning worker. Returns False if ownership was lost."""
    run = session.get(MetadataScanRun, run_id)
    if run is None:
        return False
    if (run.lease_owner or "") != worker_id:
        return False
    if run.status != ScanRunStatus.RUNNING.value:
        return False
    now = datetime.now()
    run.lease_until = now + timedelta(seconds=lease_seconds)
    run.update_time = now
    session.add(run)
    session.commit()
    return True


def mark_run_succeeded(session: Session, run: MetadataScanRun) -> None:
    now = datetime.now()
    run.status = ScanRunStatus.SUCCEEDED.value
    run.update_time = now
    run.finished_at = now
    run.lease_until = None
    session.add(run)
    session.commit()


def mark_run_partial(
    session: Session, run: MetadataScanRun, *, detail: str | None = None
) -> None:
    """Run finished without publishing a new generation (or with partial caps)."""
    now = datetime.now()
    run.status = ScanRunStatus.PARTIAL.value
    if detail:
        run.error = (detail or "")[:4000]
    run.update_time = now
    run.finished_at = now
    run.lease_until = None
    session.add(run)
    session.commit()


def mark_run_failed(session: Session, run: MetadataScanRun, error: str) -> None:
    now = datetime.now()
    run.error = (error or "")[:4000]
    run.update_time = now
    if int(run.attempt or 0) >= int(run.max_attempts or DEFAULT_MAX_ATTEMPTS):
        run.status = ScanRunStatus.FAILED.value
        run.finished_at = now
        run.lease_until = None
        _mark_table_failed(session, run)
    else:
        run.status = ScanRunStatus.PENDING.value
        run.lease_owner = None
        run.lease_until = None
    session.add(run)
    session.commit()


def profile_generation_ready(
    *,
    success_count: int | None,
    attempted_count: int | None = None,
    min_success_ratio: float = PROFILE_MIN_SUCCESS_RATIO,
) -> bool:
    """Whether a profile attempt is strong enough to become the active generation."""
    if success_count is None:
        return True
    ok_n = int(success_count)
    if ok_n <= 0:
        return False
    if attempted_count is None or int(attempted_count) <= 0:
        return True
    return (ok_n / float(attempted_count)) >= float(min_success_ratio)


def publish_table_profile_generation(
    session: Session,
    *,
    table: CoreTable,
    generation: int,
    unsupported: bool = False,
    error: str | None = None,
    success_count: int | None = None,
    attempted_count: int | None = None,
    commit: bool = True,
) -> bool:
    """Publish a new profile generation, or keep the prior one on total failure.

    Returns True when a new READY generation was published.
    """
    now = datetime.now()
    prior_generation = int(table.active_profile_generation or 0)
    ok = profile_generation_ready(
        success_count=success_count, attempted_count=attempted_count
    )
    published = False

    if unsupported:
        table.profile_status = ProfileStatus.UNSUPPORTED.value
        table.profile_error = error
        table.profile_updated_at = now
        session.add(table)
        if commit:
            session.commit()
        return False

    if not ok:
        # Do not flip active generation to a failed / sparse snapshot.
        ratio_note = ""
        if success_count is not None and attempted_count:
            ratio_note = f" ({int(success_count)}/{int(attempted_count)} fields)"
        table.profile_error = (error or f"profile below publish threshold{ratio_note}")[
            :2000
        ]
        # Keep prior generation id but mark STALE so PROMPT stops injecting stats
        # until a successful republish (avoids "looks profiled, actually drifted").
        if prior_generation > 0:
            table.profile_status = ProfileStatus.STALE.value
        else:
            table.profile_status = ProfileStatus.FAILED.value
        table.profile_updated_at = now
        session.add(table)
        if commit:
            session.commit()
        return False

    table.active_profile_generation = int(generation)
    table.profile_status = ProfileStatus.READY.value
    table.profile_error = error  # advisory field-level warnings allowed
    table.profile_updated_at = now
    session.add(table)
    _prune_old_generations(session, table_id=int(table.id), keep_generation=int(generation))
    published = True
    if commit:
        session.commit()
    return published


def _prune_old_generations(session: Session, *, table_id: int, keep_generation: int) -> None:
    min_keep = max(0, keep_generation - PROFILE_HISTORY_GENERATIONS + 1)
    stale = session.exec(
        select(FieldProfileSnapshot).where(
            FieldProfileSnapshot.table_id == table_id,
            FieldProfileSnapshot.generation < min_keep,
        )
    ).all()
    for row in stale:
        session.delete(row)


def get_active_field_profiles(
    session: Session, *, table_id: int, window_code: str = "ALL"
) -> list[FieldProfileSnapshot]:
    table = session.get(CoreTable, table_id)
    if table is None:
        return []
    generation = int(table.active_profile_generation or 0)
    if generation <= 0:
        return []
    return list(
        session.exec(
            select(FieldProfileSnapshot).where(
                FieldProfileSnapshot.table_id == table_id,
                FieldProfileSnapshot.generation == generation,
                FieldProfileSnapshot.window_code == window_code,
            )
        ).all()
    )


def get_published_relations(
    session: Session,
    *,
    ds_id: int,
    table_ids: list[int] | None = None,
    statuses: list[str] | None = None,
) -> list[FieldRelation]:
    wanted = statuses or [RelationStatus.CONFIRMED.value]
    stmt = select(FieldRelation).where(
        FieldRelation.ds_id == ds_id,
        FieldRelation.status.in_(wanted),  # type: ignore[attr-defined]
    )
    rows = list(session.exec(stmt).all())
    if not table_ids:
        return rows
    allowed = {int(tid) for tid in table_ids}
    return [
        row
        for row in rows
        if int(row.source_table_id) in allowed or int(row.target_table_id) in allowed
    ]


def resolve_table_mining_policy(
    session: Session, *, ds: CoreDatasource, table: CoreTable
) -> Any:
    """Resolve EffectivePolicy for a table (table > ds > default)."""
    from apps.datasource.profiling.policy import resolve_mining_policy

    return resolve_mining_policy(
        ds_policy=getattr(ds, "mining_policy", None),
        table_policy=getattr(table, "mining_policy", None),
    )


def build_profile_brief(
    session: Session,
    *,
    ds_id: int,
    table_ids: list[int] | None = None,
    include_top_values: bool = False,
) -> dict[str, Any]:
    """Compact read model for schema prompts and mining agents."""
    from apps.datasource.profiling.policy import policy_to_public_dict
    from apps.datasource.profiling.soft_signals import (
        derive_field_soft_signals,
        infer_table_role,
    )

    ds = session.get(CoreDatasource, ds_id)
    stmt = select(CoreTable).where(CoreTable.ds_id == ds_id, CoreTable.checked == True)  # noqa: E712
    tables = list(session.exec(stmt).all())
    if table_ids:
        wanted = {int(tid) for tid in table_ids}
        tables = [t for t in tables if t.id is not None and int(t.id) in wanted]

    field_rows = session.exec(
        select(CoreField).where(
            CoreField.ds_id == ds_id,
            CoreField.checked == True,  # noqa: E712
        )
    ).all()
    fields_by_table: dict[int, list[CoreField]] = {}
    for field in field_rows:
        fields_by_table.setdefault(int(field.table_id), []).append(field)

    relations = get_published_relations(
        session,
        ds_id=ds_id,
        table_ids=[int(t.id) for t in tables if t.id is not None],
        statuses=[RelationStatus.CONFIRMED.value],
    )
    field_name = {
        int(f.id): f.field_name for f in field_rows if f.id is not None
    }
    table_name = {
        int(t.id): t.table_name for t in tables if t.id is not None
    }

    briefs: list[dict[str, Any]] = []
    for table in tables:
        if table.id is None:
            continue
        tid = int(table.id)
        policy = (
            resolve_table_mining_policy(session, ds=ds, table=table)
            if ds is not None
            else None
        )
        enabled = set(policy.capabilities) if policy is not None else set()
        profiles = {
            int(p.field_id): p
            for p in get_active_field_profiles(session, table_id=tid)
        }
        present: set[str] = {"structure"}
        if table.approx_rows is not None or table.index_summary:
            present.add("catalog_stats")
        if profiles:
            present.add("field_profile")
        if any(
            r.source_table_id == tid or r.target_table_id == tid
            for r in relations
            if r.source == RelationSource.DDL.value
        ):
            present.add("ddl_constraints")

        field_briefs: list[dict[str, Any]] = []
        high_keys = 0
        soft_enabled = "soft_signals" in enabled
        for field in sorted(
            fields_by_table.get(tid, []),
            key=lambda item: int(item.field_index or 0),
        ):
            if field.id is None:
                continue
            snap = profiles.get(int(field.id))
            entry: dict[str, Any] = {
                "field_id": int(field.id),
                "field_name": field.field_name,
                "field_type": field.field_type,
                "comment": (field.custom_comment or field.field_comment or "")[:120],
            }
            if snap is not None and "field_profile" in enabled:
                entry.update(
                    {
                        "null_rate": snap.null_rate,
                        "approx_distinct": snap.approx_distinct,
                        "distinct_ratio": snap.distinct_ratio,
                        "min_value": snap.min_value,
                        "max_value": snap.max_value,
                    }
                )
                if include_top_values and snap.top_values is not None:
                    entry["top_values"] = snap.top_values
            elif snap is not None:
                # Profile exists but capability disabled: still mark present for missing calc.
                pass
            if soft_enabled and snap is not None:
                signals = derive_field_soft_signals(
                    field_name=field.field_name or "",
                    field_type=field.field_type,
                    null_rate=snap.null_rate,
                    distinct_ratio=snap.distinct_ratio,
                    approx_distinct=snap.approx_distinct,
                    min_value=snap.min_value,
                    max_value=snap.max_value,
                )
                entry["soft_signals"] = signals
                if signals.get("key_likelihood") == "high":
                    high_keys += 1
                present.add("soft_signals")
            field_briefs.append(entry)

        table_brief: dict[str, Any] = {
            "table_id": tid,
            "table_name": table.table_name,
            "database_name": table.database_name or "",
            "comment": (table.custom_comment or table.table_comment or "")[:160],
            "approx_rows": table.approx_rows if "catalog_stats" in enabled else None,
            "profile_status": table.profile_status,
            "active_profile_generation": table.active_profile_generation,
            "schema_fingerprint": table.schema_fingerprint,
            "fields": field_briefs,
        }
        if policy is not None:
            missing = sorted(enabled - present)
            table_brief["mining_policy"] = policy_to_public_dict(policy)
            table_brief["enabled_capabilities"] = sorted(enabled)
            table_brief["present_signals"] = sorted(present)
            table_brief["missing_optional"] = missing
        if "table_role" in enabled:
            role = infer_table_role(
                approx_rows=table.approx_rows,
                field_count=len(field_briefs),
                high_key_fields=high_keys,
            )
            table_brief["table_role"] = role.get("table_role")
            table_brief["table_role_reasons"] = role.get("reasons") or []
            present.add("table_role")
            table_brief["present_signals"] = sorted(present)
            if policy is not None:
                table_brief["missing_optional"] = sorted(enabled - present)
        briefs.append(table_brief)

    relation_briefs = []
    for rel in relations:
        relation_briefs.append(
            {
                "id": rel.id,
                "kind": rel.kind,
                "status": rel.status,
                "source": rel.source,
                "confidence": rel.confidence,
                "source_table": table_name.get(int(rel.source_table_id)),
                "source_field": field_name.get(int(rel.source_field_id)),
                "target_table": table_name.get(int(rel.target_table_id)),
                "target_field": field_name.get(int(rel.target_field_id)),
            }
        )

    return {
        "ds_id": ds_id,
        "tables": briefs,
        "relations": relation_briefs,
    }


def ddl_may_overwrite_status(status: str | None) -> bool:
    """Human REJECTED/DISABLED vetoes automatic DDL republish."""
    if status is None:
        return True
    return status not in {
        RelationStatus.REJECTED.value,
        RelationStatus.DISABLED.value,
    }


def apply_ddl_constraints_for_table(
    session: Session,
    *,
    ds: CoreDatasource,
    table: CoreTable,
    commit: bool = True,
) -> int:
    """Facts-only path: extract dialect constraints and publish CONFIRMED FKs."""
    from apps.protocol.registry import get_protocol_for_ds

    if table.id is None or ds.id is None:
        return 0
    proto = get_protocol_for_ds(ds)
    try:
        constraints = proto.extract_table_constraints(
            ds,
            resource=table.table_name,
            database_name=table.database_name,
        )
    except Exception as exc:
        SQLBotLogUtil.warning(
            f"constraint extract failed table={table.id}: {exc}"
        )
        return 0
    if not constraints.supported:
        return 0
    return upsert_ddl_foreign_keys(
        session,
        oid=int(ds.oid or 1),
        ds_id=int(ds.id),
        table=table,
        foreign_keys=list(constraints.foreign_keys or []),
        commit=commit,
    )


def upsert_ddl_foreign_keys(
    session: Session,
    *,
    oid: int,
    ds_id: int,
    table: CoreTable,
    foreign_keys: list[dict[str, Any]] | None,
    commit: bool = True,
) -> int:
    """Upsert DDL FK edges as CONFIRMED EQUI_JOIN. Returns upsert count.

    Skips endpoints the human has REJECTED or DISABLED.
    """
    if table.id is None or not foreign_keys:
        return 0
    table_id = int(table.id)
    now = datetime.now()
    field_by_name = {
        f.field_name: f
        for f in session.exec(select(CoreField).where(CoreField.table_id == table_id)).all()
        if f.field_name
    }
    from apps.datasource.models.datasource import resolve_catalog_table

    all_tables = session.exec(select(CoreTable).where(CoreTable.ds_id == ds_id)).all()
    fk_count = 0
    for fk in foreign_keys:
        src_field = field_by_name.get(str(fk.get("column") or ""))
        ref_name = str(fk.get("ref_table") or "")
        ref_db = str(
            fk.get("ref_database") or fk.get("ref_schema") or ""
        ).strip() or None
        # Prefer explicit ref DB, else same DB as the source table, else unique bare name.
        ref_table = resolve_catalog_table(
            all_tables,
            ref_name,
            database_name=ref_db or table.database_name,
        )
        if ref_table is None and (ref_db or table.database_name):
            ref_table = resolve_catalog_table(all_tables, ref_name, database_name=None)
        if src_field is None or ref_table is None or ref_table.id is None:
            continue
        ref_fields = session.exec(
            select(CoreField).where(CoreField.table_id == ref_table.id)
        ).all()
        dst_field = next(
            (f for f in ref_fields if f.field_name == str(fk.get("ref_column") or "")),
            None,
        )
        if dst_field is None or src_field.id is None or dst_field.id is None:
            continue
        existing = session.exec(
            select(FieldRelation).where(
                FieldRelation.ds_id == ds_id,
                FieldRelation.source_field_id == int(src_field.id),
                FieldRelation.target_field_id == int(dst_field.id),
                FieldRelation.kind == RelationKind.EQUI_JOIN.value,
            )
        ).first()
        if existing is not None:
            if not ddl_may_overwrite_status(existing.status):
                continue
            existing.status = RelationStatus.CONFIRMED.value
            existing.source = RelationSource.DDL.value
            existing.confidence = 1.0
            existing.evidence = {"ddl": True, "fk": fk}
            existing.update_time = now
            existing.confirmed_at = existing.confirmed_at or now
            session.add(existing)
        else:
            session.add(
                FieldRelation(
                    oid=oid,
                    ds_id=ds_id,
                    source_table_id=table_id,
                    source_field_id=int(src_field.id),
                    target_table_id=int(ref_table.id),
                    target_field_id=int(dst_field.id),
                    kind=RelationKind.EQUI_JOIN.value,
                    cardinality="N:1",
                    status=RelationStatus.CONFIRMED.value,
                    source=RelationSource.DDL.value,
                    confidence=1.0,
                    evidence={"ddl": True, "fk": fk},
                    create_time=now,
                    update_time=now,
                    confirmed_at=now,
                )
            )
        fk_count += 1
    if commit:
        session.commit()
    return fk_count


def sync_manual_equi_joins(
    session: Session,
    *,
    oid: int,
    ds_id: int,
    pairs: list[dict[str, int]],
    confirmed_by: int | None = None,
    commit: bool = True,
) -> dict[str, Any]:
    """Canvas/human bulk sync for EQUI_JOIN edges.

    - Upsert non-DDL rows as MANUAL CONFIRMED for each pair.
    - Never mutate DDL-sourced CONFIRMED rows.
    - Disable MANUAL CONFIRMED EQUI_JOIN edges absent from ``pairs``.
    """
    now = datetime.now()
    seen: set[tuple[int, int]] = set()
    upserted = 0
    for item in pairs:
        src_f = int(item["source_field_id"])
        dst_f = int(item["target_field_id"])
        src_t = int(item["source_table_id"])
        dst_t = int(item["target_table_id"])
        seen.add((src_f, dst_f))
        existing = session.exec(
            select(FieldRelation).where(
                FieldRelation.ds_id == ds_id,
                FieldRelation.source_field_id == src_f,
                FieldRelation.target_field_id == dst_f,
                FieldRelation.kind == RelationKind.EQUI_JOIN.value,
            )
        ).first()
        if existing is not None:
            if existing.source == RelationSource.DDL.value:
                continue
            existing.status = RelationStatus.CONFIRMED.value
            existing.source = RelationSource.MANUAL.value
            existing.confirmed_at = now
            if confirmed_by is not None:
                existing.confirmed_by = int(confirmed_by)
            existing.update_time = now
            session.add(existing)
            upserted += 1
            continue
        session.add(
            FieldRelation(
                oid=oid,
                ds_id=ds_id,
                source_table_id=src_t,
                source_field_id=src_f,
                target_table_id=dst_t,
                target_field_id=dst_f,
                kind=RelationKind.EQUI_JOIN.value,
                status=RelationStatus.CONFIRMED.value,
                source=RelationSource.MANUAL.value,
                confidence=1.0,
                confirmed_by=int(confirmed_by) if confirmed_by is not None else None,
                confirmed_at=now,
                create_time=now,
                update_time=now,
            )
        )
        upserted += 1

    disabled = 0
    manual_confirmed = session.exec(
        select(FieldRelation).where(
            FieldRelation.ds_id == ds_id,
            FieldRelation.kind == RelationKind.EQUI_JOIN.value,
            FieldRelation.status == RelationStatus.CONFIRMED.value,
            FieldRelation.source == RelationSource.MANUAL.value,
        )
    ).all()
    for row in manual_confirmed:
        key = (int(row.source_field_id), int(row.target_field_id))
        if key not in seen:
            row.status = RelationStatus.DISABLED.value
            row.update_time = now
            session.add(row)
            disabled += 1

    if commit:
        session.commit()
    return {"upserted": upserted, "disabled": disabled, "pair_count": len(seen)}


def project_datasource_relation_layout(
    session: Session,
    *,
    ds: CoreDatasource,
    layout: list[dict[str, Any]] | None = None,
    commit: bool = True,
) -> list[dict[str, Any]]:
    """Refresh ``ds.table_relation`` from CONFIRMED field_relation + layout nodes."""
    from apps.datasource.relation_service import project_confirmed_relations_graph

    oid = int(ds.oid or 1)
    graph = project_confirmed_relations_graph(
        session,
        oid=oid,
        ds_id=int(ds.id),
        layout=layout if layout is not None else list(ds.table_relation or []),
    )
    ds.table_relation = graph
    session.add(ds)
    if commit:
        session.commit()
    return graph


def decide_field_relation(
    session: Session,
    *,
    relation_id: int,
    status: str,
    confirmed_by: int | None = None,
    project_graph: bool = True,
) -> FieldRelation:
    """Update relation status and refresh X6 layout from CONFIRMED edges."""
    wanted = (status or "").upper()
    if wanted not in {
        RelationStatus.CONFIRMED.value,
        RelationStatus.REJECTED.value,
        RelationStatus.DISABLED.value,
        RelationStatus.CANDIDATE.value,
    }:
        raise ValueError(f"invalid status={status}")
    row = session.get(FieldRelation, relation_id)
    if row is None:
        raise LookupError("relation not found")
    now = datetime.now()
    row.status = wanted
    row.update_time = now
    if wanted == RelationStatus.CONFIRMED.value:
        row.confirmed_at = now
        if confirmed_by is not None:
            row.confirmed_by = int(confirmed_by)
        row.source = row.source or RelationSource.MANUAL.value
    session.add(row)
    session.commit()
    if project_graph:
        ds = session.get(CoreDatasource, int(row.ds_id))
        if ds is not None:
            try:
                project_datasource_relation_layout(session, ds=ds, commit=True)
            except Exception as exc:
                SQLBotLogUtil.warning(
                    f"project confirmed relations graph failed ds={row.ds_id}: {exc}"
                )
    # Relations are prompt/Brief knowledge only — RANK vectors stay structural.
    return row


def new_worker_id() -> str:
    return f"profiling-{uuid4().hex[:12]}"


def schedule_worker_kick() -> None:
    """Fire-and-forget drain of pending/expired-lease scan runs (best-effort)."""
    try:
        from apps.datasource.profiling.worker import run_profiling_worker_drain

        from common.utils.embedding_threads import executor

        executor.submit(run_profiling_worker_drain)
    except Exception as exc:  # pragma: no cover
        SQLBotLogUtil.warning(f"schedule profiling worker failed: {exc}")
