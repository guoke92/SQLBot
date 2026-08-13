"""Durable capture job queue + drain (restart-safe)."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

from sqlalchemy.dialects.postgresql import insert
from sqlmodel import Session, col, or_, select

from apps.conversation.lifecycle_log import log_lifecycle
from apps.knowledge.capture.extractors import (
    extract_process_episode,
    extract_v_t1_caliber,
    staging_payload_from_candidate,
)
from apps.knowledge.capture.snapshot import TurnSnapshot
from apps.knowledge.db_models import KnowledgeCaptureJob, KnowledgeEpisode
from apps.knowledge.gateway import (
    KnowledgeCandidate,
    KnowledgeScope,
    KnowledgeSignal,
    emit_signal,
    submit_candidate,
)


def _capture_lease_seconds() -> int:
    from common.core.config import settings

    return max(60, int(getattr(settings, "KNOWLEDGE_CAPTURE_LEASE_SECONDS", 300)))


# Only genuinely applied knowledge earns apply_outcome evidence; drops and
# anonymous hits (terminology/dictionary have no asset_id) must not count.
_APPLY_WEIGHT = {"reuse": 4, "bind": 3, "constrain": 2, "exemplify": 1}


def _applied_hits(knowledge_apply: list[Any]) -> list[dict[str, Any]]:
    """Dedupe per asset keeping the strongest apply action."""
    best: dict[tuple[str, Any], dict[str, Any]] = {}
    for hit in knowledge_apply:
        if not isinstance(hit, dict):
            continue
        weight = _APPLY_WEIGHT.get(str(hit.get("apply") or ""), 0)
        if weight <= 0 or hit.get("asset_id") is None:
            continue
        key = (str(hit.get("asset_kind") or ""), hit.get("asset_id"))
        prev = best.get(key)
        if prev is None or weight > _APPLY_WEIGHT.get(str(prev.get("apply") or ""), 0):
            best[key] = hit
    return list(best.values())


def enqueue_capture_job(
    session: Session,
    *,
    snapshot: TurnSnapshot,
) -> KnowledgeCaptureJob:
    """Persist a capture job; never raise into the NLQ complete path callers."""
    now = datetime.utcnow()
    stmt = (
        insert(KnowledgeCaptureJob)
        .values(
            oid=snapshot.oid,
            record_id=snapshot.record_id,
            status="pending",
            attempt=0,
            max_attempts=3,
            snapshot=snapshot.model_dump(mode="json"),
            create_time=now,
            update_time=now,
        )
        .on_conflict_do_nothing(index_elements=["record_id"])
        .returning(KnowledgeCaptureJob.id)
    )
    inserted_id = session.scalar(stmt)
    job = (
        session.get(KnowledgeCaptureJob, int(inserted_id))
        if inserted_id is not None
        else session.exec(
            select(KnowledgeCaptureJob).where(
                KnowledgeCaptureJob.record_id == snapshot.record_id
            )
        ).first()
    )
    if job is None:  # pragma: no cover - protects unusual DB adapters
        raise RuntimeError(f"capture enqueue failed for record {snapshot.record_id}")
    if inserted_id is not None:
        log_lifecycle(
            "capture_enqueued", record_id=snapshot.record_id, status=job.status
        )
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
    job.lease_until = now + timedelta(seconds=_capture_lease_seconds())
    job.update_time = now
    session.add(job)
    session.flush()
    return job


def process_capture_job(session: Session, job: KnowledgeCaptureJob) -> None:
    snapshot = TurnSnapshot.model_validate(job.snapshot or {})

    candidate = extract_v_t1_caliber(snapshot)
    if candidate is not None:
        payload = staging_payload_from_candidate(candidate)
        scope = KnowledgeScope(
            oid=snapshot.oid,
            datasource_id=snapshot.ds_id,
            assistant_id=snapshot.assistant_id,
        )
        kc = KnowledgeCandidate(
            kind="caliber",
            payload=payload,
            scope=scope,
            provenance={
                "source_type": "chat",
                "trigger_id": str(candidate.get("trigger_id") or "V-T1"),
                "record_id": snapshot.record_id,
            },
            suggested_tier=str(candidate.get("suggested_trust_tier") or "admitted"),
        )
        submit_candidate(session, kc, source_record_id=snapshot.record_id)

    for apply_hit in _applied_hits(snapshot.knowledge_apply):
        emit_signal(
            session,
            KnowledgeSignal(
                kind="apply_outcome",
                refs={
                    "asset_id": apply_hit.get("asset_id"),
                    "asset_kind": apply_hit.get("asset_kind", "caliber"),
                },
                fact={
                    "record_id": snapshot.record_id,
                    "outcome": snapshot.outcome,
                    "apply_action": apply_hit.get("apply"),
                },
            ),
        )

    from apps.knowledge.linkage import (
        maybe_stage_entity_for_dictionary,
        maybe_trigger_query_log_joins,
    )

    entity_bindings = (job.snapshot or {}).get("entity_bindings")
    if isinstance(entity_bindings, dict):
        maybe_stage_entity_for_dictionary(
            session, snapshot=snapshot, entity_bindings=entity_bindings
        )

    process = extract_process_episode(snapshot)
    if process is not None:
        _store_knowledge_episode(session, snapshot, process)

    maybe_trigger_query_log_joins(session, snapshot=snapshot)

    job.status = "succeeded"
    job.finished_at = datetime.utcnow()
    job.update_time = job.finished_at
    job.error = None
    session.add(job)
    session.flush()


def _store_knowledge_episode(
    session: Session,
    snapshot: TurnSnapshot,
    process: dict[str, Any],
) -> KnowledgeEpisode:
    now = datetime.utcnow()
    episode = KnowledgeEpisode(
        oid=snapshot.oid,
        datasource_id=snapshot.ds_id,
        record_id=snapshot.record_id,
        question_norm=str(process.get("question_norm") or "")[:512],
        episode=dict(process.get("episode") or {}),
        provenance={"trigger_id": "V-T9"},
        create_time=now,
    )
    session.add(episode)
    session.flush()
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
        log_lifecycle(
            "capture_started",
            record_id=job.record_id,
            status=job.status,
            dispatch_attempt=attempt,
        )
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
        log_lifecycle(
            "capture_failed",
            level="error",
            record_id=job.record_id,
            status=job.status,
            dispatch_attempt=attempt,
            error_type=type(exc).__name__,
        )
        return True


def run_capture_worker_drain(session: Session, *, max_jobs: int = 20) -> int:
    done = 0
    for _ in range(max_jobs):
        if not run_capture_worker_once(session):
            break
        done += 1
    return done


def schedule_capture_worker_kick(*, max_jobs: int = 20) -> None:
    """Drain committed jobs in the shared bounded background pool."""
    from apps.conversation.runtime import submit_background
    from apps.conversation.session import session_scope

    def _drain() -> None:
        with session_scope() as worker_session:
            drained = run_capture_worker_drain(worker_session, max_jobs=max_jobs)
        if drained >= max_jobs:
            # Yield the bounded worker after each batch, but keep draining a
            # restart backlog without waiting for another conversation.
            schedule_capture_worker_kick(max_jobs=max_jobs)

    submit_background(_drain)
