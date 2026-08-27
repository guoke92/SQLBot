"""Transactional lifecycle service for conversation runs.

All workflow writes pass through this module.  Graph nodes, APIs and SSE are
consumers of one lifecycle; none of them infer terminal state independently.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timedelta
from typing import Any, Literal
from uuid import uuid4
from zoneinfo import ZoneInfo

import orjson
from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import func, select
from sqlmodel import Session

from apps.chat.models.chat_model import Chat, ChatRecord
from apps.chat.semantic_planning import (
    ClarificationCard,
    public_interrupt_payload,
    public_resume_answers,
    question_id_of,
)
from apps.chat.steps.observability import close_open_audit_spans
from apps.chat.turn_contracts import (
    TURN_ANSWER_ADAPTER,
    AnalysisTurnAnswer,
    PredictionTurnAnswer,
    QueryTurnAnswer,
    UnsupportedTurnAnswer,
)
from apps.conversation.lifecycle_log import log_lifecycle
from apps.conversation.models import (
    ConversationEvidence,
    ConversationInterrupt,
    ConversationRun,
    ConversationRunEvent,
    QueryRun,
    ResultDataset,
)
from common.core.config import settings

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
_USER_EVIDENCE_KINDS = (
    "user_question",
    "clarification_option",
    "clarification_custom",
    "user_correction",
)
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

    Display wording may vary across a replay; the unresolved questions and
    option meanings decide whether it is the same interrupt.
    """
    try:
        card = ClarificationCard.model_validate(payload or {})
    except Exception:
        return orjson.dumps([], option=orjson.OPT_SORT_KEYS)
    questions = [
        {
            "question_id": item.question_id,
            "meanings": sorted(option.meaning for option in item.options),
        }
        for item in card.questions
    ]
    questions.sort(key=lambda value: str(value.get("question_id") or ""))
    return orjson.dumps(questions, option=orjson.OPT_SORT_KEYS, default=str)


class ResumeAnswer(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    question_id: str = Field(
        validation_alias=AliasChoices("question_id", "ambiguity_id")
    )
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
        self.question_id = self.question_id.strip()
        self.option_id = option or None
        self.text = text or None
        if not self.question_id:
            raise ValueError("question_id is required")
        return self


class ResumeRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    version: int = Field(gt=0)
    idempotency_key: str = Field(min_length=1, max_length=128)
    answers: list[ResumeAnswer] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_answers(self) -> ResumeRequest:
        ids = [answer.question_id for answer in self.answers]
        if len(ids) != len(set(ids)):
            raise ValueError("Each question may be answered only once")
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
    route_hint: Literal["query", "analysis", "prediction", "unsupported"] | None = None
    reference_record_ids: list[int] = Field(default_factory=list, max_length=3)
    finish_step: int | None = None
    return_img: bool = True


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
    business_now = datetime.now(ZoneInfo(settings.BUSINESS_TIMEZONE)).replace(
        tzinfo=None
    )
    # Serialize attempts for the visible turn and fence the whole chat against
    # two concurrent user operations.  A regenerate is another immutable run,
    # never a reopening of a terminal run.
    locked_record = _entity_one(
        session.exec(
            select(ChatRecord).where(ChatRecord.id == int(record.id)).with_for_update()
        )
    )
    # Different new records in the same chat do not contend on the record row.
    # Lock the chat aggregate as the single concurrency fence before checking
    # the partial unique active-run invariant.
    _entity_one(
        session.exec(
            select(Chat).where(Chat.id == int(locked_record.chat_id)).with_for_update()
        )
    )
    active = _entity_one_or_none(
        session.exec(
            select(ConversationRun)
            .where(
                ConversationRun.chat_id == int(locked_record.chat_id),
                ConversationRun.status.in_(("queued", "running", "awaiting_input")),
            )
            .with_for_update()
        )
    )
    if active is not None:
        raise ValueError("This conversation already has an active run")
    last_attempt = session.scalar(
        select(func.coalesce(func.max(ConversationRun.attempt_index), 0)).where(
            ConversationRun.chat_record_id == int(record.id)
        )
    )
    run = ConversationRun(
        chat_record_id=int(record.id),
        chat_id=int(locked_record.chat_id),
        attempt_index=int(last_attempt or 0) + 1,
        graph_key=graph_key,
        status="queued",
        business_now=business_now,
        timezone=settings.BUSINESS_TIMEZONE,
        user_id=user_id,
        assistant_id=assistant_id,
        oid=oid,
        create_time=now,
        update_time=now,
    )
    session.add(run)
    session.flush()
    locked_record.active_run_id = run.run_id
    session.add(locked_record)
    _append_run_event_locked(
        session,
        run=run,
        payload={"type": "run_started", "status": "queued"},
    )
    if graph_key == "chat":
        session.add(QueryRun(run_id=run.run_id, update_time=now))
        if not _record_has_user_question(session, int(record.id)):
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


def _lease_deadline() -> datetime:
    return datetime.now() + timedelta(
        seconds=max(60, int(settings.CONVERSATION_RUNNING_LEASE_SEC))
    )


def lease_renew_interval_sec() -> int:
    """Heartbeat interval so a long model call cannot outlive the worker lease."""
    lease = max(60, int(settings.CONVERSATION_RUNNING_LEASE_SEC))
    return max(30, lease // 4)


def renew_owned_run_lease() -> bool:
    """Extend the current worker's running lease. No-op without ownership."""
    from apps.conversation.runtime_context import current_worker_identity
    from apps.conversation.session import session_scope

    run_id, token = current_worker_identity()
    if not run_id or not token:
        return False
    try:
        with session_scope() as session:
            run = session.get(ConversationRun, run_id)
            if (
                run is None
                or run.status != "running"
                or (run.worker_token or "") != token
            ):
                return False
            run.lease_expires_at = _lease_deadline()
            run.update_time = datetime.now()
            session.add(run)
            session.commit()
        return True
    except Exception:
        return False


def _assert_worker_ownership(run: ConversationRun) -> None:
    """Fence late workers after cancellation or lease recovery."""
    from apps.conversation.runtime_context import current_worker_identity

    worker_run_id, worker_token = current_worker_identity()
    if worker_run_id is None and worker_token is None:
        return
    if worker_run_id != run.run_id or not worker_token:
        raise ConversationRunCancelled(run.run_id)
    if run.worker_token != worker_token:
        raise ConversationRunCancelled(
            f"Conversation run {run.run_id} is owned by another worker"
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
    _assert_worker_ownership(run)
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
    run.worker_token = None
    run.lease_expires_at = None
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
    run.worker_token = str(uuid4())
    run.lease_expires_at = _lease_deadline()
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
) -> ConversationEvidence:
    run = _entity_one(
        session.exec(
            select(ConversationRun)
            .where(ConversationRun.run_id == run_id)
            .with_for_update()
        )
    )
    # Aggregate selects return Row via session.exec(...).one(); use scalar().
    current_sequence = session.scalar(
        select(func.coalesce(func.max(ConversationEvidence.sequence), 0)).where(
            ConversationEvidence.chat_record_id == run.chat_record_id
        )
    )
    sequence = int(current_sequence or 0) + 1
    if supersedes:
        previous = session.get(ConversationEvidence, supersedes)
        if previous is None or previous.chat_record_id != run.chat_record_id:
            raise ValueError("Superseded evidence does not belong to this turn")
    event = ConversationEvidence(
        chat_record_id=run.chat_record_id,
        created_by_run_id=run_id,
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
) -> ConversationEvidence:
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


def _record_has_user_question(session: Session, chat_record_id: int) -> bool:
    return bool(
        session.scalar(
            select(func.count(ConversationEvidence.evidence_id)).where(
                ConversationEvidence.chat_record_id == chat_record_id,
                ConversationEvidence.kind == "user_question",
                ConversationEvidence.source == "user",
            )
        )
    )


def active_evidence(session: Session, run_id: str) -> list[ConversationEvidence]:
    run = session.get(ConversationRun, run_id)
    if run is None:
        raise LookupError(f"Conversation run {run_id} not found")
    events = list(
        session.exec(
            select(ConversationEvidence)
            .where(ConversationEvidence.chat_record_id == run.chat_record_id)
            .order_by(ConversationEvidence.sequence)
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


def walk_reference_record_ids(
    start: Sequence[int],
    references: Mapping[int, Sequence[int]],
    *,
    max_records: int = 8,
) -> list[int]:
    """Return referenced record ids oldest-first, following the continue chain."""
    seen: set[int] = set()
    ordered: list[int] = []
    queue = [int(item) for item in start if int(item) > 0]
    while queue and len(ordered) < max_records:
        record_id = queue.pop(0)
        if record_id in seen:
            continue
        seen.add(record_id)
        ordered.append(record_id)
        for child in references.get(record_id, ()):
            child_id = int(child)
            if child_id > 0 and child_id not in seen:
                queue.append(child_id)
    ordered.reverse()
    return ordered


def load_prior_user_evidence(
    session: Session,
    *,
    chat_id: int,
    user_id: int,
    reference_record_ids: Sequence[int],
    max_records: int = 8,
) -> list[dict[str, Any]]:
    """Collect user questions and confirmed calibers from referenced turns."""
    pending = [int(item) for item in reference_record_ids if int(item) > 0]
    references: dict[int, list[int]] = {}
    owned: set[int] = set()
    while pending:
        record_id = pending.pop()
        if record_id in references:
            continue
        record = session.get(ChatRecord, record_id)
        if (
            record is None
            or int(record.chat_id) != int(chat_id)
            or int(record.create_by or 0) != int(user_id)
        ):
            references[record_id] = []
            continue
        owned.add(record_id)
        children = [
            int(item) for item in (record.reference_record_ids or []) if int(item) > 0
        ]
        references[record_id] = children
        pending.extend(children)

    order = [
        record_id
        for record_id in walk_reference_record_ids(
            reference_record_ids, references, max_records=max_records
        )
        if record_id in owned
    ]
    if not order:
        return []
    events = list(
        session.exec(
            select(ConversationEvidence)
            .where(
                ConversationEvidence.chat_record_id.in_(order),
                ConversationEvidence.kind.in_(_USER_EVIDENCE_KINDS),
            )
            .order_by(ConversationEvidence.sequence)
        )
        .scalars()
        .all()
    )
    by_record: dict[int, list[ConversationEvidence]] = {
        record_id: [] for record_id in order
    }
    for event in events:
        by_record.setdefault(int(event.chat_record_id), []).append(event)
    payload: list[dict[str, Any]] = []
    for record_id in order:
        for event in by_record.get(record_id, []):
            payload.append(
                {
                    "record_id": record_id,
                    "kind": event.kind,
                    "content": event.content,
                    "structured_value": event.structured_value,
                }
            )
    return payload


def _merge_query_plans(
    query_run: QueryRun,
    *,
    plans: list[dict[str, Any]],
) -> None:
    """Merge idempotent candidates into an already locked NLQ aggregate."""
    existing = {
        str(item.get("plan_id")): dict(item)
        for item in (query_run.plans or [])
        if item.get("plan_id")
    }
    order = [
        str(item.get("plan_id"))
        for item in query_run.plans or []
        if item.get("plan_id")
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
            "status": plan.get("status") or previous.get("status") or "held",
        }
        if plan_id not in order:
            order.append(plan_id)
    query_run.plans = [existing[plan_id] for plan_id in order]
    query_run.active_plan_id = order[-1] if order else query_run.active_plan_id
    query_run.update_time = datetime.now()


def persist_query_clarification(
    session: Session,
    *,
    run_id: str,
    held_plans: list[dict[str, Any]] | None = None,
) -> None:
    """Persist one clarification boundary without publishing held plans."""
    require_active_run(session, run_id)
    query_run = _entity_one(
        session.exec(
            select(QueryRun).where(QueryRun.run_id == run_id).with_for_update()
        )
    )
    query_run.planning_status = "awaiting_input"
    if held_plans:
        _merge_query_plans(query_run, plans=held_plans)
    session.add(query_run)
    session.commit()


# Keys on ``query_run.agent_decision`` owned by the server rather than the
# planner decision payload. Decision persistence replaces model-owned content
# wholesale; these survive so telemetry history is never erased.
_SERVER_OWNED_DECISION_KEYS = frozenset({"topup"})


def _merged_agent_decision(
    previous: dict[str, Any] | None, decision: dict[str, Any]
) -> dict[str, Any]:
    merged = dict(decision)
    for key in _SERVER_OWNED_DECISION_KEYS:
        if key in (previous or {}):
            merged[key] = previous[key]
    return merged


def persist_query_decision(
    session: Session,
    *,
    run_id: str,
    decision: dict[str, Any],
    plans: list[dict[str, Any]],
    hard_gate_report: dict[str, Any],
    risk_assessment: dict[str, Any],
    plan_facts: list[dict[str, Any]],
    planning_status: str,
    semantic_review: dict[str, Any] | None = None,
    repair_record: dict[str, Any] | None = None,
) -> None:
    """Persist the v7 query boundary without inventing a semantic contract."""
    require_active_run(session, run_id)
    query_run = _entity_one(
        session.exec(
            select(QueryRun).where(QueryRun.run_id == run_id).with_for_update()
        )
    )
    query_run.agent_decision = _merged_agent_decision(
        query_run.agent_decision, decision
    )
    query_run.hard_gate_report = hard_gate_report
    query_run.risk_assessment = risk_assessment
    query_run.plan_facts = plan_facts
    query_run.planning_status = planning_status
    if semantic_review is not None:
        query_run.semantic_reviews = [
            *(query_run.semantic_reviews or []),
            semantic_review,
        ]
    if plans:
        _merge_query_plans(query_run, plans=plans)
    if repair_record is not None:
        query_run.repair_history = [
            *(query_run.repair_history or []),
            repair_record,
        ]
    query_run.update_time = datetime.now()
    session.add(query_run)
    session.commit()


def register_query_plans(
    session: Session,
    *,
    run_id: str,
    plans: list[dict[str, Any]],
    repair_record: dict[str, Any] | None = None,
) -> None:
    """Upsert physical candidates without replacing prior audit history."""
    require_active_run(session, run_id)
    query_run = _entity_one(
        session.exec(
            select(QueryRun).where(QueryRun.run_id == run_id).with_for_update()
        )
    )
    _merge_query_plans(query_run, plans=plans)
    if repair_record is not None:
        query_run.repair_history = [
            *(query_run.repair_history or []),
            repair_record,
        ]
    session.add(query_run)
    session.commit()


def load_query_plan_result(
    session: Session,
    *,
    run_id: str,
    plan_id: str,
    schema_fingerprint: str,
    access_policy_fingerprint: str,
) -> dict[str, Any] | None:
    result = _entity_one_or_none(
        session.exec(
            select(ResultDataset)
            .where(
                ResultDataset.run_id == run_id,
                ResultDataset.plan_id == plan_id,
                ResultDataset.status.in_(("succeeded", "degraded")),
            )
            .order_by(ResultDataset.create_time.desc())
            .limit(1)
        )
    )
    if result is None:
        return None
    snapshot = dict(result.schema_snapshot or {})
    if (
        snapshot.get("schema_fingerprint") != schema_fingerprint
        or snapshot.get("access_policy_fingerprint") != access_policy_fingerprint
    ):
        return None
    payload = {
        "is_success": True,
        "fields": list(result.fields or []),
        "data": list(result.rows or []),
        "row_count": result.row_count,
        "truncated": result.truncated,
    }
    totals = dict(result.statistics or {}).get("coverage_totals")
    if isinstance(totals, dict) and totals:
        payload["coverage_totals"] = totals
    return payload


def persist_query_plan_result(
    session: Session,
    *,
    run_id: str,
    plan_id: str,
    result: dict[str, Any],
    schema_fingerprint: str,
    access_policy_fingerprint: str,
) -> None:
    """Persist a result dataset before publishing any transport event."""
    require_active_run(session, run_id)
    query_run = _entity_one(
        session.exec(
            select(QueryRun).where(QueryRun.run_id == run_id).with_for_update()
        )
    )
    plans = [dict(item) for item in (query_run.plans or [])]
    dataset_id = ""
    required = True
    for index, plan in enumerate(plans):
        if str(plan.get("plan_id") or "") != plan_id:
            continue
        dataset_id = str(plan.get("dataset_id") or "dataset_1")
        required = bool(plan.get("required", True))
        if plan.get("status") != "executed":
            plan["status"] = "executed"
            plan["executed_at"] = datetime.now().isoformat()
            plans[index] = plan
        break
    else:
        raise ValueError(f"Cannot persist result for unknown query plan {plan_id}")
    existing_result = _entity_one_or_none(
        session.exec(
            select(ResultDataset)
            .where(
                ResultDataset.run_id == run_id,
                ResultDataset.dataset_id == dataset_id,
                ResultDataset.plan_id == plan_id,
            )
            .with_for_update()
        )
    )
    rows_raw = result.get("data")
    rows = [dict(item) for item in rows_raw or [] if isinstance(item, dict)]
    fields = [str(item) for item in result.get("fields") or []]
    execution_snapshot = {
        "schema_fingerprint": schema_fingerprint,
        "access_policy_fingerprint": access_policy_fingerprint,
    }
    statistics = dict(getattr(existing_result, "statistics", None) or {})
    totals = result.get("coverage_totals")
    if isinstance(totals, dict) and totals:
        statistics["coverage_totals"] = dict(totals)
    if existing_result is None:
        existing_result = ResultDataset(
            run_id=run_id,
            dataset_id=dataset_id,
            plan_id=plan_id,
            status="succeeded",
            required=required,
            fields=fields,
            rows=rows,
            row_count=int(result.get("row_count") or len(rows)),
            truncated=bool(result.get("truncated")),
            schema_snapshot=execution_snapshot,
            statistics=statistics,
        )
        session.add(existing_result)
        session.flush()
    else:
        existing_result.status = "succeeded"
        existing_result.fields = fields
        existing_result.rows = rows
        existing_result.row_count = int(result.get("row_count") or len(rows))
        existing_result.truncated = bool(result.get("truncated"))
        existing_result.error = None
        existing_result.schema_snapshot = execution_snapshot
        existing_result.statistics = statistics
        session.add(existing_result)
    query_run.plans = plans
    execution = {
        "dataset_id": dataset_id,
        "plan_id": plan_id,
        "required": required,
        "status": "succeeded",
        "result_id": existing_result.result_id,
        "row_count": existing_result.row_count,
        "truncated": existing_result.truncated,
    }
    prior = [
        item
        for item in query_run.executions or []
        if not (item.get("dataset_id") == dataset_id and item.get("plan_id") == plan_id)
    ]
    query_run.executions = [*prior, execution]
    query_run.executed_plan_ids = list(
        dict.fromkeys([*(query_run.executed_plan_ids or []), plan_id])
    )
    query_run.execution_status = "running"
    query_run.update_time = datetime.now()
    session.add(query_run)
    session.commit()


def persist_query_plan_failure(
    session: Session,
    *,
    run_id: str,
    plan_id: str,
    error: dict[str, Any],
) -> None:
    """Persist one failed dataset attempt without exposing it as result data."""
    require_active_run(session, run_id)
    query_run = _entity_one(
        session.exec(
            select(QueryRun).where(QueryRun.run_id == run_id).with_for_update()
        )
    )
    plan = next(
        (
            dict(item)
            for item in (query_run.plans or [])
            if str(item.get("plan_id") or "") == plan_id
        ),
        None,
    )
    if plan is None:
        raise ValueError(f"Cannot persist failure for unknown query plan {plan_id}")
    dataset_id = str(plan.get("dataset_id") or "dataset_1")
    required = bool(plan.get("required", True))
    existing = _entity_one_or_none(
        session.exec(
            select(ResultDataset)
            .where(
                ResultDataset.run_id == run_id,
                ResultDataset.dataset_id == dataset_id,
                ResultDataset.plan_id == plan_id,
            )
            .with_for_update()
        )
    )
    if existing is None:
        existing = ResultDataset(
            run_id=run_id,
            dataset_id=dataset_id,
            plan_id=plan_id,
            status="failed",
            required=required,
            error=error,
        )
        session.add(existing)
        session.flush()
    else:
        existing.status = "failed"
        existing.error = error
        session.add(existing)
    execution = {
        "dataset_id": dataset_id,
        "plan_id": plan_id,
        "required": required,
        "status": "failed",
        "result_id": existing.result_id,
        "error": error,
    }
    prior = [
        item
        for item in query_run.executions or []
        if not (item.get("dataset_id") == dataset_id and item.get("plan_id") == plan_id)
    ]
    query_run.executions = [*prior, execution]
    query_run.execution_status = "running"
    query_run.update_time = datetime.now()
    session.add(query_run)
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
    # ``create_interrupt`` persists the clarification together with the state
    # transition. The subsequent sink write is live transport only.
    if run.status == "awaiting_input" and payload.get("type") == "clarification":
        return -int(run.event_cursor or 0)
    _assert_worker_ownership(run)
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
    _assert_worker_ownership(run)
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
    if status == "running":
        run.lease_expires_at = _lease_deadline()
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
    error_visibility: Literal["sanitize", "public"] = "sanitize",
) -> ConversationRun:
    """Atomically publish the record, domain result, and run terminal state.

    This is the sole conversation terminal write boundary. Transport delivery and
    checkpoint bookkeeping happen only after this transaction commits.
    ``error_visibility="public"`` is reserved for terminal nodes that have
    already constructed a safe business-facing error; all other failures are
    sanitized into the stable public envelope here.
    """
    run = _entity_one(
        session.exec(
            select(ConversationRun)
            .where(ConversationRun.run_id == run_id)
            .with_for_update()
        )
    )
    _assert_worker_ownership(run)
    if run.status in TERMINAL_STATUSES:
        if run.status != status:
            raise ValueError(
                f"Terminal run {run_id} is {run.status} and cannot change to {status}"
            )
        return run
    _assert_transition(run, status)
    query_run = _entity_one_or_none(
        session.exec(
            select(QueryRun).where(QueryRun.run_id == run_id).with_for_update()
        )
    )
    record = _entity_one(
        session.exec(
            select(ChatRecord)
            .where(ChatRecord.id == run.chat_record_id)
            .with_for_update()
        )
    )
    published_snapshot = dict(record_snapshot)
    if status == "failed" and error_visibility == "sanitize":
        from apps.conversation.outcome import public_error_message

        published_snapshot["error"] = public_error_message(
            published_snapshot.get("error") or error_summary or "Conversation failed"
        )
    # The separate config tool graph still renders its plain-text response
    # through ``sql_answer``. Ordinary chat turns persist only TurnAnswerV1;
    # writing historical fields here would recreate a second answer truth.
    if run.graph_key == "config" and published_snapshot.get("sql_answer") is not None:
        record.sql_answer = published_snapshot["sql_answer"]
    record.finish = True
    record.finish_time = datetime.now()
    record.error = published_snapshot.get("error")

    supplied_answer = published_snapshot.get("answer")
    should_publish_answer = status in {"succeeded", "degraded"} or record.answer is None
    if should_publish_answer:
        next_revision = int(record.answer_revision or 0) + 1
        answer_status = "failed" if status == "cancelled" else status
        if isinstance(supplied_answer, dict):
            supplied_answer = {
                **supplied_answer,
                "answer_revision": next_revision,
                "source_run_id": run_id,
                "status": answer_status,
            }
            answer = TURN_ANSWER_ADAPTER.validate_python(supplied_answer)
        else:
            common = {
                "answer_revision": next_revision,
                "source_run_id": run_id,
                "status": answer_status,
                "content": str(
                    published_snapshot.get("analysis")
                    or published_snapshot.get("sql_answer")
                    or ""
                ),
                "error": (
                    {
                        "code": "RUN_FAILED",
                        "message": str(published_snapshot.get("error") or ""),
                        "retryable": True,
                    }
                    if status == "failed"
                    else None
                ),
            }
            if record.turn_kind == "analysis":
                answer = AnalysisTurnAnswer(**common)
            elif record.turn_kind == "prediction":
                answer = PredictionTurnAnswer(**common)
            elif record.turn_kind == "unsupported":
                answer = UnsupportedTurnAnswer(**common)
            else:
                answer = QueryTurnAnswer(**common)
        record.answer_revision = next_revision
        record.answer = answer.model_dump(mode="json")
    # A failed regenerate keeps last-known-good Answer but remains the active
    # attempt so the UI can display its failure alongside the preserved answer.
    record.active_run_id = run_id
    session.add(record)
    close_open_audit_spans(session, run.chat_record_id)
    terminal_node = current_node or run.current_node
    if query_run is not None:
        if status == "failed":
            if getattr(query_run, "planning_status", "pending") not in {
                "ready",
                "unsupported",
            }:
                query_run.planning_status = "failed"
            query_run.execution_status = (
                "failed"
                if query_run.execution_status == "running"
                or bool(getattr(query_run, "executed_plan_ids", []))
                else "not_started"
            )
        elif status == "cancelled":
            query_run.execution_status = "cancelled"
        else:
            query_run.execution_status = "completed"
        query_run.result_quality = result_quality
        query_run.update_time = datetime.now()
    run.status = status
    run.current_node = terminal_node
    run.error_summary = error_summary
    run.completed_at = datetime.now()
    run.active_interrupt_id = None
    run.worker_token = None
    run.lease_expires_at = None
    run.update_time = datetime.now()
    if query_run is not None:
        session.add(query_run)
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
    _assert_worker_ownership(run)
    if run.status in TERMINAL_STATUSES:
        raise ValueError("Cannot interrupt a terminal run")
    payload = public_interrupt_payload(payload)
    if not payload.get("questions"):
        raise ValueError("Clarification card has no questions")
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
    run.worker_token = None
    run.lease_expires_at = None
    run.update_time = datetime.now()
    session.add(run)
    _append_run_event_locked(
        session,
        run=run,
        payload={
            "type": "clarification",
            "interrupt_id": interrupt.interrupt_id,
            "version": interrupt.version,
            "ambiguities": payload.get("ambiguities", []),
            "summary": payload.get("summary", ""),
        },
    )
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
    locked_run = _entity_one(
        session.exec(
            select(ConversationRun)
            .where(ConversationRun.run_id == run.run_id)
            .with_for_update()
        )
    )
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
    if (
        locked_run.status != "awaiting_input"
        or locked_run.active_interrupt_id != interrupt_id
    ):
        raise ValueError("Clarification is no longer active")
    if interrupt.status != "open" or interrupt.version != request.version:
        raise ValueError("Clarification version is stale")

    catalog = {
        question.question_id: question
        for question in ClarificationCard.model_validate(interrupt.payload).questions
    }
    required = set(catalog)
    supplied = {answer.question_id for answer in request.answers}
    missing = required - supplied
    if missing:
        raise ValueError("Missing clarification answers: " + ", ".join(sorted(missing)))

    stored_answers: list[dict[str, Any]] = []
    for answer in request.answers:
        question = catalog.get(answer.question_id)
        if question is None:
            raise ValueError(f"Unknown question: {answer.question_id}")
        if answer.mode == "option":
            options = {item.option_id: item for item in question.options}
            option = options.get(str(answer.option_id))
            if option is None:
                raise ValueError(
                    f"Unknown option {answer.option_id} for {answer.question_id}"
                )
            evidence = append_evidence(
                session,
                run_id=locked_run.run_id,
                kind="clarification_option",
                source="user",
                content=option.label,
                structured_value={
                    "question_id": answer.question_id,
                    "option_id": answer.option_id,
                    "question": question.question,
                    "meaning": option.meaning,
                    "field": option.field,
                    "field_comment": option.field_comment,
                    "table": option.table,
                    "fields": [item.model_dump(mode="json") for item in option.fields],
                },
            )
        else:
            evidence = append_evidence(
                session,
                run_id=locked_run.run_id,
                kind="clarification_custom",
                source="user",
                content=str(answer.text),
                structured_value={
                    "question_id": answer.question_id,
                    "question": question.question,
                    "meaning": str(answer.text),
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
    _assert_transition(locked_run, "queued")
    locked_run.status = "queued"
    locked_run.dispatch_attempts = 0
    locked_run.active_interrupt_id = None
    locked_run.worker_token = None
    locked_run.lease_expires_at = None
    locked_run.update_time = now
    query_run = session.get(QueryRun, locked_run.run_id)
    if query_run is not None:
        query_run.planning_status = "planning"
        query_run.update_time = now
        session.add(query_run)
    session.add(interrupt)
    session.add(locked_run)
    session.commit()
    log_lifecycle(
        "run_resumed",
        run_id=locked_run.run_id,
        record_id=locked_run.chat_record_id,
        graph_key=locked_run.graph_key,
        status=locked_run.status,
    )
    return interrupt, True


def correct_interrupt_answer(
    session: Session,
    *,
    run: ConversationRun,
    interrupt_id: str,
    request: CorrectionRequest,
) -> tuple[ConversationEvidence, bool]:
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
            if question_id_of(item) == request.answer.question_id
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
        question.question_id: question
        for question in ClarificationCard.model_validate(
            source_interrupt.payload
        ).questions
    }
    question = catalog.get(request.answer.question_id)
    if question is None:
        raise ValueError("Clarification question no longer exists")
    structured: dict[str, Any] = {
        "question_id": request.answer.question_id,
        "question": question.question,
        "idempotency_key": request.idempotency_key,
    }
    if request.answer.mode == "option":
        options = {item.option_id: item for item in question.options}
        option = options.get(str(request.answer.option_id))
        if option is None:
            raise ValueError("Correction option does not belong to this question")
        content = option.label
        structured.update(
            {
                "option_id": request.answer.option_id,
                "meaning": option.meaning,
            }
        )
    else:
        content = str(request.answer.text)
        structured["meaning"] = content

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
    locked_run.worker_token = None
    locked_run.lease_expires_at = None
    locked_run.update_time = datetime.now()
    query_run = session.get(QueryRun, locked_run.run_id)
    if query_run is not None:
        query_run.planning_status = "planning"
        query_run.update_time = locked_run.update_time
        session.add(query_run)
    session.add(locked_run)
    session.commit()
    return correction, True


def serialize_interrupt(interrupt: ConversationInterrupt) -> dict[str, Any]:
    return {
        "interrupt_id": interrupt.interrupt_id,
        "version": interrupt.version,
        "status": interrupt.status,
        "payload": public_interrupt_payload(interrupt.payload),
        "answers": public_resume_answers(interrupt.answers),
    }


def run_snapshot(session: Session, run: ConversationRun) -> dict[str, Any]:
    record = session.get(ChatRecord, run.chat_record_id)
    interrupt = (
        session.get(ConversationInterrupt, run.active_interrupt_id)
        if run.active_interrupt_id
        else None
    )
    query_run = session.get(QueryRun, run.run_id) if run.graph_key == "chat" else None
    datasets = list(
        session.exec(
            select(ResultDataset)
            .where(ResultDataset.run_id == run.run_id)
            .order_by(ResultDataset.create_time)
        ).scalars()
    )
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
        "chat_id": run.chat_id,
        "attempt_index": run.attempt_index,
        "graph_key": run.graph_key,
        "status": run.status,
        "current_node": run.current_node,
        "event_cursor": run.event_cursor,
        "dispatch_attempts": run.dispatch_attempts,
        "lease_expires_at": run.lease_expires_at,
        "active_interrupt": serialize_interrupt(interrupt) if interrupt else None,
        "interrupts": [serialize_interrupt(item) for item in interrupts],
        "query": (
            {
                "planning_status": query_run.planning_status,
                "agent_decision": query_run.agent_decision,
                "hard_gate_report": query_run.hard_gate_report,
                "plan_facts": query_run.plan_facts,
                "risk_assessment": query_run.risk_assessment,
                "semantic_reviews": query_run.semantic_reviews,
                "repair_history": query_run.repair_history,
                "execution_status": query_run.execution_status,
                "quality": query_run.result_quality,
                "plans": query_run.plans,
                "executions": query_run.executions,
            }
            if query_run
            else None
        ),
        "result_datasets": [item.model_dump(mode="json") for item in datasets],
        "record": record.model_dump(mode="json") if record else None,
        "error_summary": (
            record.error if record is not None and record.error else run.error_summary
        ),
        "started_at": run.started_at,
        "completed_at": run.completed_at,
        "update_time": run.update_time,
    }
