"""Transactional lifecycle service for conversation runs.

All workflow writes pass through this module.  Graph nodes, APIs and SSE are
consumers of one lifecycle; none of them infer terminal state independently.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

import orjson
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import func, select
from sqlmodel import Session

from apps.chat.models.chat_model import ChatRecord
from apps.chat.steps.observability import close_open_audit_spans
from apps.conversation.lifecycle_log import log_lifecycle
from apps.conversation.models import (
    ConversationInterrupt,
    ConversationRun,
    ConversationRunEvent,
    NlqEvidenceEvent,
    NlqRun,
)
from apps.conversation.record import persist_snapshot

RunStatus = Literal[
    "queued",
    "running",
    "awaiting_input",
    "succeeded",
    "degraded",
    "failed",
    "cancelled",
]
TERMINAL_STATUSES = frozenset({"succeeded", "degraded", "failed", "cancelled"})
_ALLOWED_TRANSITIONS: dict[str, frozenset[str]] = {
    "queued": frozenset({"queued", "running", "failed", "cancelled"}),
    "running": frozenset(
        {
            "queued",
            "running",
            "awaiting_input",
            "succeeded",
            "degraded",
            "failed",
            "cancelled",
        }
    ),
    "awaiting_input": frozenset({"awaiting_input", "queued", "failed", "cancelled"}),
    "succeeded": frozenset({"succeeded"}),
    "degraded": frozenset({"degraded"}),
    "failed": frozenset({"failed"}),
    "cancelled": frozenset({"cancelled"}),
}


class ConversationRunCancelled(RuntimeError):
    """Internal cooperative-stop signal; never rendered as a workflow error."""


def interrupt_payload_identity(payload: dict[str, Any]) -> bytes:
    """Return the semantic identity of a clarification card.

    Display wording and recommendation explanations may vary across a replay;
    the unresolved business axes and structured candidate resolutions decide
    whether it is the same interrupt.
    """
    ambiguities: list[dict[str, Any]] = []
    for item in payload.get("ambiguities") or []:
        if not isinstance(item, dict):
            continue
        candidates = [
            {
                "option_id": option.get("option_id"),
                "resolution": option.get("resolution"),
            }
            for option in item.get("candidate_resolutions") or []
            if isinstance(option, dict)
        ]
        ambiguities.append(
            {
                "ambiguity_id": item.get("ambiguity_id"),
                "candidates": sorted(
                    candidates,
                    key=lambda value: str(value.get("option_id") or ""),
                ),
            }
        )
    ambiguities.sort(key=lambda value: str(value.get("ambiguity_id") or ""))
    return orjson.dumps(ambiguities, option=orjson.OPT_SORT_KEYS, default=str)


class ResumeAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ambiguity_id: str
    mode: Literal["option", "custom"]
    option_id: str | None = None
    text: str | None = None

    @model_validator(mode="after")
    def validate_mode(self) -> ResumeAnswer:
        option = (self.option_id or "").strip()
        text = (self.text or "").strip()
        if self.mode == "option" and (not option or text):
            raise ValueError("option answers require option_id and cannot include text")
        if self.mode == "custom" and (not text or option):
            raise ValueError("custom answers require text and cannot include option_id")
        self.ambiguity_id = self.ambiguity_id.strip()
        self.option_id = option or None
        self.text = text or None
        if not self.ambiguity_id:
            raise ValueError("ambiguity_id is required")
        return self


class ResumeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: int = Field(gt=0)
    idempotency_key: str = Field(min_length=1, max_length=128)
    answers: list[ResumeAnswer] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_answers(self) -> ResumeRequest:
        ids = [answer.ambiguity_id for answer in self.answers]
        if len(ids) != len(set(ids)):
            raise ValueError("Each ambiguity may be answered only once")
        return self


class CorrectionRequest(BaseModel):
    """Replace one effective clarification answer while the run is paused."""

    model_config = ConfigDict(extra="forbid")

    version: int = Field(gt=0)
    idempotency_key: str = Field(min_length=1, max_length=128)
    supersedes_evidence_id: str = Field(min_length=1, max_length=36)
    answer: ResumeAnswer


class CreateRunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chat_id: int
    question: str = Field(min_length=1)
    datasource_id: int | None = None
    regenerate_record_id: int | None = None


def create_run(
    session: Session,
    *,
    record: ChatRecord,
    graph_key: str,
    user_id: int,
    oid: int,
    assistant_id: int | None = None,
) -> ConversationRun:
    if record.id is None:
        raise ValueError("Chat record must be persisted before creating its run")
    now = datetime.now()
    run = ConversationRun(
        chat_record_id=int(record.id),
        graph_key=graph_key,
        status="queued",
        user_id=user_id,
        assistant_id=assistant_id,
        oid=oid,
        create_time=now,
        update_time=now,
    )
    session.add(run)
    session.flush()
    _append_run_event_locked(
        session,
        run=run,
        payload={"type": "run_started", "status": "queued"},
    )
    if graph_key == "chat":
        session.add(NlqRun(run_id=run.run_id, update_time=now))
        append_evidence(
            session,
            run_id=run.run_id,
            kind="user_question",
            source="user",
            content=(record.question or "").strip(),
            confidence=1.0,
        )
    session.commit()
    session.refresh(run)
    log_lifecycle(
        "run_created",
        run_id=run.run_id,
        record_id=run.chat_record_id,
        graph_key=run.graph_key,
        status=run.status,
        dispatch_attempt=run.dispatch_attempts,
    )
    return run


def _entity_one(result: Any) -> Any:
    return result.scalars().one()


def _entity_one_or_none(result: Any) -> Any:
    return result.scalars().one_or_none()


def _assert_transition(run: ConversationRun, target: str) -> None:
    if target not in _ALLOWED_TRANSITIONS.get(run.status, frozenset()):
        raise ValueError(
            f"Illegal conversation run transition {run.status} -> {target} for {run.run_id}"
        )


def require_active_run(session: Session, run_id: str) -> ConversationRun:
    """Lock and fence a domain write to the currently active run.

    A model/database call can finish after recovery, cancellation, or a
    terminal failure was published.  Such late workers may finish their local
    computation, but they must never mutate NLQ state or reopen the visible
    result.  ConversationRun remains the sole ownership boundary.
    """
    run = _entity_one_or_none(
        session.exec(
            select(ConversationRun)
            .where(ConversationRun.run_id == run_id)
            .with_for_update()
        )
    )
    if run is None:
        raise LookupError(f"Conversation run {run_id} not found")
    if run.status != "running":
        raise ConversationRunCancelled(
            f"Conversation run {run_id} is no longer active ({run.status})"
        )
    return run


def queue_run_for_dispatch(
    session: Session,
    run_id: str,
    *,
    reset_attempts: bool = False,
    expected_status: str | None = None,
    expected_update_time: datetime | None = None,
) -> ConversationRun | None:
    """Move a resumable phase to queued before it is submitted to the pool."""
    run = _entity_one(
        session.exec(
            select(ConversationRun)
            .where(ConversationRun.run_id == run_id)
            .with_for_update()
        )
    )
    if run.status in TERMINAL_STATUSES:
        # A recovery snapshot can become terminal between enumeration and the
        # row lock above.  Returning the row would make the caller dispatch and
        # report a recovery that never actually happened.
        return None
    if expected_status is not None and run.status != expected_status:
        return None
    if expected_update_time is not None and run.update_time != expected_update_time:
        return None
    if run.status != "queued":
        _assert_transition(run, "queued")
        run.status = "queued"
    if reset_attempts:
        run.dispatch_attempts = 0
    run.update_time = datetime.now()
    session.add(run)
    session.commit()
    session.refresh(run)
    return run


def record_run_dispatch(
    session: Session,
    run_id: str,
    *,
    force: bool = False,
) -> ConversationRun | None:
    """Record one pool submission; the worker still has to claim the row."""
    run = _entity_one_or_none(
        session.exec(
            select(ConversationRun)
            .where(ConversationRun.run_id == run_id)
            .with_for_update()
        )
    )
    if run is None or run.status != "queued":
        return None
    if not force and run.dispatch_attempts and run.update_time:
        from common.core.config import settings

        age = (datetime.now() - run.update_time).total_seconds()
        if age < max(1, settings.CONVERSATION_QUEUED_RETRY_SEC):
            return None
    run.dispatch_attempts = int(run.dispatch_attempts or 0) + 1
    run.update_time = datetime.now()
    session.add(run)
    session.commit()
    session.refresh(run)
    log_lifecycle(
        "run_dispatched",
        run_id=run.run_id,
        record_id=run.chat_record_id,
        graph_key=run.graph_key,
        status=run.status,
        dispatch_attempt=run.dispatch_attempts,
    )
    return run


def claim_run(session: Session, run_id: str) -> ConversationRun | None:
    """Atomically grant one worker ownership of a queued run."""
    run = _entity_one_or_none(
        session.exec(
            select(ConversationRun)
            .where(ConversationRun.run_id == run_id)
            .with_for_update()
        )
    )
    if run is None or run.status != "queued":
        return None
    _assert_transition(run, "running")
    now = datetime.now()
    run.status = "running"
    run.started_at = run.started_at or now
    run.error_summary = None
    run.update_time = now
    session.add(run)
    session.commit()
    session.refresh(run)
    log_lifecycle(
        "run_claimed",
        run_id=run.run_id,
        record_id=run.chat_record_id,
        graph_key=run.graph_key,
        status=run.status,
        dispatch_attempt=run.dispatch_attempts,
    )
    return run


def get_owned_run(
    session: Session,
    *,
    run_id: str,
    user_id: int,
) -> ConversationRun:
    run = session.get(ConversationRun, run_id)
    if run is None or int(run.user_id) != int(user_id):
        raise LookupError("Conversation run not found")
    return run


def append_evidence(
    session: Session,
    *,
    run_id: str,
    kind: str,
    source: str,
    content: str,
    structured_value: dict[str, Any] | None = None,
    confidence: float = 1.0,
    supersedes: str | None = None,
) -> NlqEvidenceEvent:
    session.exec(
        select(ConversationRun.run_id)
        .where(ConversationRun.run_id == run_id)
        .with_for_update()
    ).first()
    # Aggregate selects return Row via session.exec(...).one(); use scalar().
    current_sequence = session.scalar(
        select(func.coalesce(func.max(NlqEvidenceEvent.sequence), 0)).where(
            NlqEvidenceEvent.run_id == run_id
        )
    )
    sequence = int(current_sequence or 0) + 1
    if supersedes:
        previous = session.get(NlqEvidenceEvent, supersedes)
        if previous is None or previous.run_id != run_id:
            raise ValueError("Superseded evidence does not belong to this run")
    event = NlqEvidenceEvent(
        run_id=run_id,
        sequence=sequence,
        kind=kind,
        source=source,
        content=content,
        structured_value=structured_value,
        confidence=max(0.0, min(float(confidence), 1.0)),
        supersedes=supersedes,
    )
    session.add(event)
    session.flush()
    return event


def ensure_evidence(
    session: Session,
    *,
    run_id: str,
    kind: str,
    source: str,
    content: str,
    structured_value: dict[str, Any] | None = None,
    confidence: float = 1.0,
) -> NlqEvidenceEvent:
    """Append a context fact once; immutable user events still use append_evidence."""
    existing = next(
        (
            event
            for event in active_evidence(session, run_id)
            if event.kind == kind
            and event.source == source
            and event.content == content
        ),
        None,
    )
    if existing is not None:
        return existing
    return append_evidence(
        session,
        run_id=run_id,
        kind=kind,
        source=source,
        content=content,
        structured_value=structured_value,
        confidence=confidence,
    )


def active_evidence(session: Session, run_id: str) -> list[NlqEvidenceEvent]:
    events = list(
        session.exec(
            select(NlqEvidenceEvent)
            .where(NlqEvidenceEvent.run_id == run_id)
            .order_by(NlqEvidenceEvent.sequence)
        )
        .scalars()
        .all()
    )
    # Evidence rows are append-only. Effective state is a projection: a later
    # event may supersede an earlier event, but the earlier audit row is never
    # updated or deleted.
    superseded = {event.supersedes for event in events if event.supersedes}
    effective = [event for event in events if event.evidence_id not in superseded]

    # User statements are immutable additive evidence. Retrieval products are
    # snapshots of mutable external context, however, and retaining several
    # active versions lets a recovered planner consume contradictory schemas
    # or defaults. Keep their full history in the ledger while projecting only
    # the latest value per source into semantic planning.
    latest_context_sequence: dict[tuple[str, str], int] = {}
    snapshot_kinds = {
        "schema_fact",
        "terminology_match",
        "training_example",
        "system_default",
    }
    for event in effective:
        if event.kind in snapshot_kinds:
            latest_context_sequence[(event.kind, event.source)] = event.sequence
    return [
        event
        for event in effective
        if event.kind not in snapshot_kinds
        or event.sequence == latest_context_sequence[(event.kind, event.source)]
    ]


def _merge_query_plans(
    nlq: NlqRun,
    *,
    specification_revision: int,
    plans: list[dict[str, Any]],
) -> None:
    """Merge idempotent candidates into an already locked NLQ aggregate."""
    existing = {
        str(item.get("plan_id")): dict(item)
        for item in (nlq.plans or [])
        if item.get("plan_id")
    }
    order = [
        str(item.get("plan_id")) for item in nlq.plans or [] if item.get("plan_id")
    ]
    for plan in plans:
        plan_id = str(plan.get("plan_id") or "")
        if not plan_id:
            raise ValueError("Every query plan requires plan_id")
        previous = existing.get(plan_id, {})
        existing[plan_id] = {
            **previous,
            **plan,
            "plan_id": plan_id,
            "specification_revision": specification_revision,
            "status": previous.get("status") or "validated",
        }
        if plan_id not in order:
            order.append(plan_id)
    nlq.plans = [existing[plan_id] for plan_id in order]
    nlq.active_plan_id = order[-1] if order else nlq.active_plan_id
    nlq.update_time = datetime.now()


def persist_query_planning_result(
    session: Session,
    *,
    run_id: str,
    specification: dict[str, Any],
    plans: list[dict[str, Any]],
) -> None:
    """Atomically publish one semantic revision and its initial plans."""
    require_active_run(session, run_id)
    nlq = _entity_one(
        session.exec(select(NlqRun).where(NlqRun.run_id == run_id).with_for_update())
    )
    revision = int(specification.get("revision") or 0)
    if revision <= 0:
        raise ValueError("Query specification requires a positive revision")
    if not nlq.specifications or nlq.specifications[-1] != specification:
        nlq.specifications = [*(nlq.specifications or []), specification]
    nlq.active_specification_revision = revision
    nlq.planning_status = "ready"
    _merge_query_plans(
        nlq,
        specification_revision=revision,
        plans=plans,
    )
    session.add(nlq)
    session.commit()


def register_query_plans(
    session: Session,
    *,
    run_id: str,
    specification_revision: int,
    plans: list[dict[str, Any]],
) -> None:
    """Upsert physical candidates without replacing prior audit history."""
    require_active_run(session, run_id)
    nlq = _entity_one(
        session.exec(select(NlqRun).where(NlqRun.run_id == run_id).with_for_update())
    )
    _merge_query_plans(
        nlq,
        specification_revision=specification_revision,
        plans=plans,
    )
    session.add(nlq)
    session.commit()


def load_query_plan_result(
    session: Session, *, run_id: str, plan_id: str
) -> dict[str, Any] | None:
    nlq = session.get(NlqRun, run_id)
    if nlq is None:
        return None
    for plan in nlq.plans or []:
        if (
            str(plan.get("plan_id") or "") == plan_id
            and plan.get("status") == "executed"
        ):
            result = plan.get("execution_result")
            return dict(result) if isinstance(result, dict) else None
    return None


def persist_query_plan_result(
    session: Session,
    *,
    run_id: str,
    plan_id: str,
    result: dict[str, Any],
) -> None:
    """Commit execution once; graph replay reuses this exact result."""
    require_active_run(session, run_id)
    nlq = _entity_one(
        session.exec(select(NlqRun).where(NlqRun.run_id == run_id).with_for_update())
    )
    plans = [dict(item) for item in (nlq.plans or [])]
    for index, plan in enumerate(plans):
        if str(plan.get("plan_id") or "") != plan_id:
            continue
        if plan.get("status") != "executed":
            plan["status"] = "executed"
            plan["execution_result"] = result
            plan["executed_at"] = datetime.now().isoformat()
            plans[index] = plan
        break
    else:
        raise ValueError(f"Cannot persist result for unknown query plan {plan_id}")
    nlq.plans = plans
    nlq.executed_plan_ids = list(
        dict.fromkeys([*(nlq.executed_plan_ids or []), plan_id])
    )
    nlq.execution_status = "running"
    nlq.update_time = datetime.now()
    session.add(nlq)
    session.commit()


def _append_run_event_locked(
    session: Session,
    *,
    run: ConversationRun,
    payload: dict[str, Any],
) -> int:
    cursor = int(run.event_cursor or 0) + 1
    run.event_cursor = cursor
    run.update_time = datetime.now()
    session.add(run)
    session.add(
        ConversationRunEvent(
            run_id=run.run_id,
            cursor=cursor,
            payload={
                "cursor": cursor,
                "at": datetime.now().isoformat(),
                **payload,
            },
        )
    )
    return cursor


def append_run_event(
    session: Session,
    *,
    run_id: str,
    payload: dict[str, Any],
) -> int:
    run = _entity_one_or_none(
        session.exec(
            select(ConversationRun)
            .where(ConversationRun.run_id == run_id)
            .with_for_update()
        )
    )
    if run is None:
        return 0
    # ``finalize_run`` atomically writes the terminal event.  Events emitted by
    # a node after that commit are stale transport echoes and must not reopen
    # the persisted timeline.
    if run.status in TERMINAL_STATUSES:
        return -int(run.event_cursor or 0)
    cursor = _append_run_event_locked(session, run=run, payload=payload)
    session.commit()
    return cursor


def run_events_after(
    session: Session, *, run_id: str, cursor: int, limit: int = 200
) -> list[dict[str, Any]]:
    rows = session.exec(
        select(ConversationRunEvent)
        .where(
            ConversationRunEvent.run_id == run_id,
            ConversationRunEvent.cursor > max(0, cursor),
        )
        .order_by(ConversationRunEvent.cursor)
        .limit(max(1, min(limit, 1000)))
    ).scalars()
    return [dict(item.payload) for item in rows]


def update_run_status(
    session: Session,
    run_id: str,
    status: RunStatus,
    *,
    current_node: str | None = None,
    error_summary: str | None = None,
    checkpoint_id: str | None = None,
) -> ConversationRun:
    if status in TERMINAL_STATUSES:
        raise ValueError("Terminal statuses must be written through finalize_run")
    run = _entity_one(
        session.exec(
            select(ConversationRun)
            .where(ConversationRun.run_id == run_id)
            .with_for_update()
        )
    )
    _assert_transition(run, status)
    now = datetime.now()
    run.status = status
    run.current_node = current_node if current_node is not None else run.current_node
    run.checkpoint_id = (
        checkpoint_id if checkpoint_id is not None else run.checkpoint_id
    )
    run.error_summary = error_summary
    run.update_time = now
    if status == "running" and run.started_at is None:
        run.started_at = now
    session.add(run)
    session.commit()
    session.refresh(run)
    return run


def finalize_run(
    session: Session,
    *,
    run_id: str,
    status: Literal["succeeded", "degraded", "failed", "cancelled"],
    current_node: str | None,
    result_quality: dict[str, Any] | None = None,
    record_snapshot: dict[str, Any],
    error_summary: str | None = None,
) -> ConversationRun:
    """Atomically publish the record, domain result, and run terminal state.

    This is the sole conversation terminal write boundary. Transport delivery and
    checkpoint bookkeeping happen only after this transaction commits.
    """
    run = _entity_one(
        session.exec(
            select(ConversationRun)
            .where(ConversationRun.run_id == run_id)
            .with_for_update()
        )
    )
    if run.status in TERMINAL_STATUSES:
        if run.status != status:
            raise ValueError(
                f"Terminal run {run_id} is {run.status} and cannot change to {status}"
            )
        return run
    _assert_transition(run, status)
    nlq = _entity_one_or_none(
        session.exec(select(NlqRun).where(NlqRun.run_id == run_id).with_for_update())
    )
    published_snapshot = dict(record_snapshot)
    if status == "failed":
        from apps.conversation.outcome import public_error_message

        published_snapshot["error"] = public_error_message(
            published_snapshot.get("error") or error_summary or "Conversation failed"
        )
    persist_snapshot(
        session,
        run.chat_record_id,
        commit=False,
        **published_snapshot,
    )
    close_open_audit_spans(session, run.chat_record_id)
    terminal_node = current_node or run.current_node
    if nlq is not None:
        if status == "failed":
            if getattr(nlq, "planning_status", "pending") != "ready":
                nlq.planning_status = "failed"
            nlq.execution_status = (
                "failed"
                if nlq.execution_status == "running"
                or bool(getattr(nlq, "executed_plan_ids", []))
                else "not_started"
            )
        elif status == "cancelled":
            nlq.execution_status = "cancelled"
        else:
            nlq.execution_status = "completed"
        nlq.result_quality = result_quality
        nlq.update_time = datetime.now()
    run.status = status
    run.current_node = terminal_node
    run.error_summary = error_summary
    run.completed_at = datetime.now()
    run.active_interrupt_id = None
    run.update_time = datetime.now()
    if nlq is not None:
        session.add(nlq)
    session.add(run)
    _append_run_event_locked(
        session,
        run=run,
        payload={
            "type": "error" if status == "failed" else "finish",
            "content": published_snapshot.get("error") if status == "failed" else None,
            "status": status,
            "node": terminal_node,
        },
    )
    session.commit()
    log_lifecycle(
        "run_finalized",
        run_id=run.run_id,
        record_id=run.chat_record_id,
        graph_key=run.graph_key,
        node=terminal_node,
        status=status,
        dispatch_attempt=run.dispatch_attempts,
        error_type="RunFailed" if status == "failed" else None,
    )
    return run


def record_checkpoint_id(session: Session, run_id: str, checkpoint_id: str) -> None:
    """Index the latest durable checkpoint without owning checkpoint content."""
    if not checkpoint_id:
        return
    run = session.get(ConversationRun, run_id)
    if run is None or run.checkpoint_id == checkpoint_id:
        return
    run.checkpoint_id = checkpoint_id
    run.update_time = datetime.now()
    session.add(run)
    session.commit()


def create_interrupt(
    session: Session,
    *,
    run_id: str,
    payload: dict[str, Any],
) -> ConversationInterrupt:
    run = _entity_one(
        session.exec(
            select(ConversationRun)
            .where(ConversationRun.run_id == run_id)
            .with_for_update()
        )
    )
    if run.status in TERMINAL_STATUSES:
        raise ValueError("Cannot interrupt a terminal run")
    latest_interrupt = _entity_one_or_none(
        session.exec(
            select(ConversationInterrupt)
            .where(ConversationInterrupt.run_id == run_id)
            .order_by(ConversationInterrupt.version.desc())
            .limit(1)
        )
    )
    if latest_interrupt is not None:
        if interrupt_payload_identity(
            latest_interrupt.payload
        ) == interrupt_payload_identity(payload) and latest_interrupt.status in {
            "open",
            "consumed",
        }:
            # LangGraph resumes an interrupt by replaying the node from its
            # beginning. The consumed row is therefore the same pause point,
            # not a request to create the next clarification version.
            return latest_interrupt
        # A question card is an audit artifact. A replanned card gets a new
        # version instead of mutating what a client may already be displaying.
        if latest_interrupt.status == "open":
            latest_interrupt.status = "cancelled"
            session.add(latest_interrupt)
    version = int(latest_interrupt.version if latest_interrupt else 0) + 1
    interrupt = ConversationInterrupt(run_id=run_id, version=version, payload=payload)
    session.add(interrupt)
    session.flush()
    _assert_transition(run, "awaiting_input")
    run.status = "awaiting_input"
    run.active_interrupt_id = interrupt.interrupt_id
    run.update_time = datetime.now()
    session.add(run)
    session.commit()
    session.refresh(interrupt)
    log_lifecycle(
        "run_interrupted",
        run_id=run.run_id,
        record_id=run.chat_record_id,
        graph_key=run.graph_key,
        status=run.status,
    )
    return interrupt


def consume_interrupt(
    session: Session,
    *,
    run: ConversationRun,
    interrupt_id: str,
    request: ResumeRequest,
) -> tuple[ConversationInterrupt, bool]:
    interrupt = _entity_one_or_none(
        session.exec(
            select(ConversationInterrupt)
            .where(
                ConversationInterrupt.interrupt_id == interrupt_id,
                ConversationInterrupt.run_id == run.run_id,
            )
            .with_for_update()
        )
    )
    if interrupt is None:
        raise LookupError("Conversation interrupt not found")
    if interrupt.status == "consumed":
        if interrupt.idempotency_key == request.idempotency_key:
            return interrupt, False
        raise ValueError("This clarification has already been answered")
    if interrupt.status != "open" or interrupt.version != request.version:
        raise ValueError("Clarification version is stale")

    catalog = {
        str(item.get("ambiguity_id")): item
        for item in interrupt.payload.get("ambiguities", [])
        if isinstance(item, dict)
    }
    required = {
        ambiguity_id
        for ambiguity_id, item in catalog.items()
        if not bool(item.get("can_assume"))
    }
    supplied = {answer.ambiguity_id for answer in request.answers}
    missing = required - supplied
    if missing:
        raise ValueError("Missing clarification answers: " + ", ".join(sorted(missing)))

    stored_answers: list[dict[str, Any]] = []
    for answer in request.answers:
        ambiguity = catalog.get(answer.ambiguity_id)
        if ambiguity is None:
            raise ValueError(f"Unknown ambiguity: {answer.ambiguity_id}")
        if answer.mode == "option":
            options = {
                str(item.get("option_id")): item
                for item in ambiguity.get("candidate_resolutions", [])
                if isinstance(item, dict)
            }
            option = options.get(str(answer.option_id))
            if option is None:
                raise ValueError(
                    f"Unknown option {answer.option_id} for {answer.ambiguity_id}"
                )
            evidence = append_evidence(
                session,
                run_id=run.run_id,
                kind="clarification_option",
                source="user",
                content=str(option.get("label") or answer.option_id),
                structured_value={
                    "ambiguity_id": answer.ambiguity_id,
                    "business_axis": ambiguity.get("business_axis"),
                    "option_id": answer.option_id,
                    "resolution": option.get("resolution"),
                },
            )
        else:
            evidence = append_evidence(
                session,
                run_id=run.run_id,
                kind="clarification_custom",
                source="user",
                content=str(answer.text),
                structured_value={
                    "ambiguity_id": answer.ambiguity_id,
                    "business_axis": ambiguity.get("business_axis"),
                },
            )
        stored_answers.append(
            {**answer.model_dump(mode="json"), "evidence_id": evidence.evidence_id}
        )

    now = datetime.now()
    interrupt.status = "consumed"
    interrupt.answers = stored_answers
    interrupt.idempotency_key = request.idempotency_key
    interrupt.consumed_at = now
    _assert_transition(run, "queued")
    run.status = "queued"
    run.dispatch_attempts = 0
    run.active_interrupt_id = None
    run.update_time = now
    nlq = session.get(NlqRun, run.run_id)
    if nlq is not None:
        nlq.planning_status = "planning"
        nlq.update_time = now
        session.add(nlq)
    session.add(interrupt)
    session.add(run)
    session.commit()
    log_lifecycle(
        "run_resumed",
        run_id=run.run_id,
        record_id=run.chat_record_id,
        graph_key=run.graph_key,
        status=run.status,
    )
    return interrupt, True


def correct_interrupt_answer(
    session: Session,
    *,
    run: ConversationRun,
    interrupt_id: str,
    request: CorrectionRequest,
) -> tuple[NlqEvidenceEvent, bool]:
    """Append one correction and invalidate the currently open question card.

    Corrections are accepted only while the same run is paused. The graph then
    replans from immutable effective evidence and creates a fresh interrupt if
    a business ambiguity still exists.
    """
    locked_run = _entity_one(
        session.exec(
            select(ConversationRun)
            .where(ConversationRun.run_id == run.run_id)
            .with_for_update()
        )
    )
    if locked_run.status != "awaiting_input" or not locked_run.active_interrupt_id:
        raise ValueError("Corrections require a run that is awaiting input")
    source_interrupt = _entity_one_or_none(
        session.exec(
            select(ConversationInterrupt)
            .where(
                ConversationInterrupt.interrupt_id == interrupt_id,
                ConversationInterrupt.run_id == run.run_id,
            )
            .with_for_update()
        )
    )
    if (
        source_interrupt is None
        or source_interrupt.status != "consumed"
        or source_interrupt.version != request.version
    ):
        raise ValueError("Only a consumed clarification answer can be corrected")

    prior_answer = next(
        (
            item
            for item in source_interrupt.answers or []
            if str(item.get("ambiguity_id")) == request.answer.ambiguity_id
            and str(item.get("evidence_id")) == request.supersedes_evidence_id
        ),
        None,
    )
    if prior_answer is None:
        raise ValueError("Clarification evidence does not match the selected answer")
    effective_ids = {
        event.evidence_id for event in active_evidence(session, run.run_id)
    }
    if request.supersedes_evidence_id not in effective_ids:
        existing = next(
            (
                event
                for event in active_evidence(session, run.run_id)
                if (event.structured_value or {}).get("idempotency_key")
                == request.idempotency_key
            ),
            None,
        )
        if existing is not None:
            return existing, False
        raise ValueError("Clarification answer has already been superseded")

    catalog = {
        str(item.get("ambiguity_id")): item
        for item in source_interrupt.payload.get("ambiguities", [])
        if isinstance(item, dict)
    }
    ambiguity = catalog.get(request.answer.ambiguity_id)
    if ambiguity is None:
        raise ValueError("Clarification ambiguity no longer exists")
    structured: dict[str, Any] = {
        "ambiguity_id": request.answer.ambiguity_id,
        "business_axis": ambiguity.get("business_axis"),
        "idempotency_key": request.idempotency_key,
    }
    if request.answer.mode == "option":
        options = {
            str(item.get("option_id")): item
            for item in ambiguity.get("candidate_resolutions", [])
            if isinstance(item, dict)
        }
        option = options.get(str(request.answer.option_id))
        if option is None:
            raise ValueError("Correction option does not belong to this ambiguity")
        content = str(option.get("label") or request.answer.option_id)
        structured.update(
            {
                "option_id": request.answer.option_id,
                "resolution": option.get("resolution"),
            }
        )
    else:
        content = str(request.answer.text)

    correction = append_evidence(
        session,
        run_id=run.run_id,
        kind="user_correction",
        source="user",
        content=content,
        structured_value=structured,
        supersedes=request.supersedes_evidence_id,
    )
    active_interrupt = session.get(
        ConversationInterrupt, locked_run.active_interrupt_id
    )
    if active_interrupt is not None and active_interrupt.status == "open":
        active_interrupt.status = "cancelled"
        session.add(active_interrupt)
    _assert_transition(locked_run, "queued")
    locked_run.status = "queued"
    locked_run.dispatch_attempts = 0
    locked_run.active_interrupt_id = None
    locked_run.update_time = datetime.now()
    nlq = session.get(NlqRun, locked_run.run_id)
    if nlq is not None:
        nlq.planning_status = "planning"
        nlq.update_time = locked_run.update_time
        session.add(nlq)
    session.add(locked_run)
    session.commit()
    return correction, True


def run_snapshot(session: Session, run: ConversationRun) -> dict[str, Any]:
    record = session.get(ChatRecord, run.chat_record_id)
    interrupt = (
        session.get(ConversationInterrupt, run.active_interrupt_id)
        if run.active_interrupt_id
        else None
    )
    nlq = session.get(NlqRun, run.run_id) if run.graph_key == "chat" else None
    interrupts = list(
        session.exec(
            select(ConversationInterrupt)
            .where(ConversationInterrupt.run_id == run.run_id)
            .order_by(ConversationInterrupt.version)
        ).scalars()
    )
    return {
        "run_id": run.run_id,
        "chat_record_id": run.chat_record_id,
        "graph_key": run.graph_key,
        "status": run.status,
        "current_node": run.current_node,
        "event_cursor": run.event_cursor,
        "dispatch_attempts": run.dispatch_attempts,
        "active_interrupt": (
            {
                "interrupt_id": interrupt.interrupt_id,
                "version": interrupt.version,
                "status": interrupt.status,
                "payload": interrupt.payload,
                "answers": interrupt.answers,
            }
            if interrupt
            else None
        ),
        "interrupts": [
            {
                "interrupt_id": item.interrupt_id,
                "version": item.version,
                "status": item.status,
                "payload": item.payload,
                "answers": item.answers,
            }
            for item in interrupts
        ],
        "nlq": (
            {
                "active_specification_revision": nlq.active_specification_revision,
                "specifications": nlq.specifications,
                "planning_status": nlq.planning_status,
                "execution_status": nlq.execution_status,
                "quality": nlq.result_quality,
            }
            if nlq
            else None
        ),
        "record": record.model_dump(mode="json") if record else None,
        "error_summary": (
            record.error
            if record is not None and record.error
            else run.error_summary
        ),
        "started_at": run.started_at,
        "completed_at": run.completed_at,
        "update_time": run.update_time,
    }
