"""Durable capture job queue + drain (restart-safe)."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

from sqlmodel import Session, col, or_, select

from apps.knowledge.capture.extractors import (
    extract_process_episode,
    extract_v_t1_caliber,
    staging_payload_from_candidate,
)
from apps.knowledge.capture.snapshot import TurnSnapshot
from apps.knowledge.db_models import KnowledgeCaptureJob, ProcessEpisode
from apps.knowledge.lineage import append_event, new_lineage_id
from apps.knowledge.staging.service import admit_candidate

_LEASE_SECONDS = 120


def enqueue_capture_job(
    session: Session,
    *,
    snapshot: TurnSnapshot,
) -> KnowledgeCaptureJob:
    """Persist a capture job; never raise into the NLQ complete path callers."""
    now = datetime.utcnow()
    job = KnowledgeCaptureJob(
        oid=snapshot.oid,
        record_id=snapshot.record_id,
        status="pending",
        attempt=0,
        max_attempts=3,
        snapshot=snapshot.model_dump(mode="json"),
        create_time=now,
        update_time=now,
    )
    session.add(job)
    session.flush()
    return job


def claim_next_capture_job(
    session: Session,
    *,
    owner: str | None = None,
) -> KnowledgeCaptureJob | None:
    now = datetime.utcnow()
    owner = owner or f"capture-{uuid4().hex[:12]}"
    stmt = (
        select(KnowledgeCaptureJob)
        .where(
            or_(
                KnowledgeCaptureJob.status == "pending",
                (
                    (KnowledgeCaptureJob.status == "running")
                    & (
                        (KnowledgeCaptureJob.lease_until.is_(None))  # type: ignore[attr-defined]
                        | (KnowledgeCaptureJob.lease_until < now)  # type: ignore[operator]
                    )
                ),
            )
        )
        .order_by(col(KnowledgeCaptureJob.create_time).asc())
        .limit(1)
        .with_for_update(skip_locked=True)
    )
    job = session.exec(stmt).first()
    if job is None:
        return None
    job.status = "running"
    job.attempt = int(job.attempt or 0) + 1
    job.lease_owner = owner
    job.lease_until = now + timedelta(seconds=_LEASE_SECONDS)
    job.update_time = now
    session.add(job)
    session.flush()
    return job


def process_capture_job(session: Session, job: KnowledgeCaptureJob) -> None:
    snapshot = TurnSnapshot.model_validate(job.snapshot or {})
    # V-T1 caliber
    candidate = extract_v_t1_caliber(snapshot)
    if candidate is not None:
        admit_candidate(
            session,
            oid=snapshot.oid,
            kind="caliber",
            trigger_id=str(candidate.get("trigger_id") or "V-T1"),
            payload=staging_payload_from_candidate(candidate),
            scope=candidate.get("scope") or {"ds_id": snapshot.ds_id},
            source_record_id=snapshot.record_id,
            suggested_trust_tier=str(
                candidate.get("suggested_trust_tier") or "admitted"
            ),
            quality_snapshot={"outcome": snapshot.outcome},
            field_targets=candidate.get("field_targets"),
        )

    # L-2 entity → dictionary staging (still requires dict publish)
    from apps.knowledge.linkage import (
        maybe_stage_entity_for_dictionary,
        maybe_trigger_query_log_joins,
    )

    entity_bindings = (job.snapshot or {}).get("entity_bindings")
    if isinstance(entity_bindings, dict):
        maybe_stage_entity_for_dictionary(
            session, snapshot=snapshot, entity_bindings=entity_bindings
        )

    # Process episode (weak)
    process = extract_process_episode(snapshot)
    if process is not None:
        _store_process_episode(session, snapshot, process)

    # L-3: trigger Catalog join mining (no second parser)
    maybe_trigger_query_log_joins(session, snapshot=snapshot)

    job.status = "succeeded"
    job.finished_at = datetime.utcnow()
    job.update_time = job.finished_at
    job.error = None
    session.add(job)
    session.flush()


def _store_process_episode(
    session: Session,
    snapshot: TurnSnapshot,
    process: dict[str, Any],
) -> ProcessEpisode:
    now = datetime.utcnow()
    lineage_id = new_lineage_id()
    episode = ProcessEpisode(
        lineage_id=lineage_id,
        oid=snapshot.oid,
        datasource_id=snapshot.ds_id,
        question_norm=str(process.get("question_norm") or "")[:512],
        episode=dict(process.get("episode") or {}),
        trust_tier="published",
        enabled=True,
        source_record_id=snapshot.record_id,
        provenance={"trigger_id": "V-T9"},
        create_time=now,
        update_time=now,
    )
    session.add(episode)
    session.flush()
    append_event(
        session,
        lineage_id=lineage_id,
        asset_kind="process",
        action="published",
        asset_id=episode.id,
        trigger_id="V-T9",
        evidence_snapshot={
            "source_record_id": snapshot.record_id,
            "note": "process_never_bind",
        },
        to_tier="published",
    )
    return episode


def run_capture_worker_once(session: Session) -> bool:
    """Claim and process one job. Returns True if work was done.

    Claim (including ``attempt++``) is committed before process so a poison
    job can reach ``failed`` instead of rolling the counter back forever.
    """
    job = claim_next_capture_job(session)
    if job is None:
        return False
    job_id = int(job.id) if job.id is not None else None
    if job_id is None:
        return False
    attempt = int(job.attempt or 0)
    max_attempts = int(job.max_attempts or 3)
    session.commit()
    try:
        job = session.get(KnowledgeCaptureJob, job_id)
        if job is None:
            return True
        process_capture_job(session, job)
        session.commit()
        return True
    except Exception as exc:  # noqa: BLE001 — job isolation
        session.rollback()
        job = session.get(KnowledgeCaptureJob, job_id)
        if job is None:
            return True
        job.error = str(exc)[:2000]
        job.update_time = datetime.utcnow()
        if attempt >= max_attempts:
            job.status = "failed"
            job.finished_at = job.update_time
        else:
            job.status = "pending"
            job.lease_until = None
        session.add(job)
        session.commit()
        return True


def run_capture_worker_drain(session: Session, *, max_jobs: int = 20) -> int:
    done = 0
    for _ in range(max_jobs):
        if not run_capture_worker_once(session):
            break
        done += 1
    return done
