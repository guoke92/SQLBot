"""Single policy for turning immutable knowledge facts into governance evidence."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlmodel import Session, select

from apps.knowledge.db_models import KnowledgeEvidence

SUCCESS_OUTCOMES = frozenset(
    {"success", "degraded", "accepted", "completed", "ok"}
)
STRONG_APPLY_ACTIONS = frozenset({"bind", "reuse"})


@dataclass(frozen=True)
class EvidenceSummary:
    reproduce_count: int = 0
    successful_apply_count: int = 0
    positive_feedback_count: int = 0
    negative_feedback_count: int = 0

    @property
    def requires_review(self) -> bool:
        return self.negative_feedback_count > 0

    def promotion_ready(
        self,
        *,
        reproduce_threshold: int,
        positive_feedback_threshold: int,
    ) -> bool:
        return not self.requires_review and (
            self.reproduce_count >= reproduce_threshold
            or self.positive_feedback_count >= positive_feedback_threshold
        )


def summarize_asset_evidence(
    session: Session,
    *,
    asset_id: int,
    asset_kind: str,
) -> EvidenceSummary:
    """Project current evidence without mutating the append-only ledger."""
    asset_events = list(
        session.exec(
            select(KnowledgeEvidence)
            .where(KnowledgeEvidence.asset_id == asset_id)
            .where(KnowledgeEvidence.asset_kind == asset_kind)
        ).all()
    )
    reproduce_records: set[int] = set()
    successful_apply: dict[int, str] = {}
    for event in asset_events:
        if event.record_id is None:
            continue
        record_id = int(event.record_id)
        fact = dict(event.fact or {})
        if event.signal_kind == "reproduce":
            reproduce_records.add(record_id)
        elif (
            event.signal_kind == "apply_outcome"
            and str(fact.get("outcome") or "") in SUCCESS_OUTCOMES
        ):
            successful_apply[record_id] = str(fact.get("apply_action") or "")

    attributable_records = reproduce_records | set(successful_apply)
    if not attributable_records:
        return EvidenceSummary()

    feedback_events = list(
        session.exec(
            select(KnowledgeEvidence)
            .where(KnowledgeEvidence.signal_kind == "turn_feedback")
            .where(KnowledgeEvidence.record_id.in_(attributable_records))  # type: ignore[attr-defined]
        ).all()
    )
    latest_feedback: dict[int, tuple[int, str | None]] = {}
    for event in feedback_events:
        if event.record_id is None:
            continue
        fact: dict[str, Any] = dict(event.fact or {})
        revision = int(fact.get("revision") or 0)
        current = latest_feedback.get(int(event.record_id))
        if current is None or revision > current[0]:
            latest_feedback[int(event.record_id)] = (revision, fact.get("feedback"))

    positive = 0
    negative = 0
    for record_id, (_revision, feedback) in latest_feedback.items():
        # A turn-level vote is strong enough for automatic governance only when
        # this asset was bound/reused. Other applications remain audit facts.
        action = successful_apply.get(record_id)
        if action not in STRONG_APPLY_ACTIONS:
            continue
        if feedback == "up":
            positive += 1
        elif feedback == "down":
            negative += 1

    return EvidenceSummary(
        reproduce_count=len(reproduce_records),
        successful_apply_count=len(successful_apply),
        positive_feedback_count=positive,
        negative_feedback_count=negative,
    )
