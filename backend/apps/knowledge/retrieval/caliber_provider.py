"""Retrieve published calibers; Compile decides Bind vs Constrain vs Drop."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlmodel import Session, col, or_, select

from apps.knowledge.compile.bundle import BoundCaliber
from apps.knowledge.db_models import BusinessCaliber
from apps.knowledge.policy import KnowledgePolicy

# Without embedding ranking: hard cap Bind to one relevant caliber.
_DEFAULT_BIND_LIMIT = 1


@dataclass
class CaliberCandidate:
    apply: str  # bind | constrain | drop
    bound: BoundCaliber | None = None
    card: dict[str, Any] | None = None
    asset_id: int | None = None
    lineage_id: str | None = None
    trust_tier: str | None = None
    drop_reason: str | None = None


def _is_bindable(caliber: BusinessCaliber, policy: KnowledgePolicy) -> bool:
    if not caliber.enabled or caliber.superseded_by is not None:
        return False
    if policy.caliber_bind_requires == "certified":
        return bool(
            caliber.certified and caliber.trust_tier in ("certified", "golden")
        )
    return caliber.trust_tier in ("trusted", "certified", "golden") and (
        caliber.certified or caliber.trust_tier != "certified"
    )


def _relevance_score(caliber: BusinessCaliber, question: str) -> float:
    """Cheap lexical overlap — no embedding. Zero ⇒ must not Bind."""
    q = (question or "").casefold().strip()
    if not q:
        return 0.0
    score = 0.0
    for text in (caliber.label, caliber.summary or ""):
        t = (text or "").casefold().strip()
        if not t:
            continue
        if t in q or q in t:
            score += 3.0
            continue
        for tok in t.replace("_", " ").split():
            if len(tok) >= 2 and tok in q:
                score += 1.0
    for syn in caliber.synonyms or []:
        s = str(syn).casefold().strip()
        if s and (s in q or q in s):
            score += 2.0
    for target in caliber.field_targets or []:
        if not isinstance(target, dict):
            continue
        for key in ("field_name", "table_name"):
            name = str(target.get(key) or "").casefold()
            if name and len(name) >= 2 and name in q:
                score += 1.5
    return score


def recall_bindable_calibers(
    session: Session,
    *,
    oid: int,
    ds_id: int,
    question: str,
    policy: KnowledgePolicy,
    limit: int = _DEFAULT_BIND_LIMIT,
) -> list[CaliberCandidate]:
    """Return caliber candidates for the question.

    Staging is never queried. Bind only when lexical relevance > 0, capped at
    ``limit`` (default 1). Unrelated certified rows are Dropped with reason.
    """
    bind_limit = max(1, min(int(limit), 3))
    stmt = (
        select(BusinessCaliber)
        .where(BusinessCaliber.oid == oid)
        .where(BusinessCaliber.enabled.is_(True))  # type: ignore[attr-defined]
        .where(BusinessCaliber.superseded_by.is_(None))  # type: ignore[attr-defined]
        .where(
            or_(
                BusinessCaliber.datasource_id == ds_id,
                BusinessCaliber.datasource_id.is_(None),  # type: ignore[attr-defined]
            )
        )
        .order_by(col(BusinessCaliber.update_time).desc())
        .limit(40)
    )
    rows = list(session.exec(stmt).all())
    scored: list[tuple[float, BusinessCaliber]] = []
    out: list[CaliberCandidate] = []

    for caliber in rows:
        assert caliber.id is not None
        if not _is_bindable(caliber, policy):
            if (
                caliber.trust_tier == "trusted"
                and policy.assess_constrain_uncertified_caliber
            ):
                out.append(
                    CaliberCandidate(
                        apply="constrain",
                        card={
                            "label": caliber.label,
                            "summary": caliber.summary or "",
                            "fragment": dict(caliber.contract_fragment or {}),
                        },
                        asset_id=int(caliber.id),
                        lineage_id=caliber.lineage_id,
                        trust_tier=caliber.trust_tier,
                    )
                )
            else:
                out.append(
                    CaliberCandidate(
                        apply="drop",
                        asset_id=int(caliber.id),
                        lineage_id=caliber.lineage_id,
                        trust_tier=caliber.trust_tier,
                        drop_reason=(
                            "not_certified"
                            if not caliber.certified
                            else "policy_forbid_constrain"
                        ),
                    )
                )
            continue
        score = _relevance_score(caliber, question)
        if score <= 0:
            out.append(
                CaliberCandidate(
                    apply="drop",
                    asset_id=int(caliber.id),
                    lineage_id=caliber.lineage_id,
                    trust_tier=caliber.trust_tier,
                    drop_reason="no_relevance",
                )
            )
            continue
        scored.append((score, caliber))

    scored.sort(key=lambda item: (-item[0], -(item[1].update_time.timestamp() if item[1].update_time else 0)))
    for idx, (_score, caliber) in enumerate(scored):
        assert caliber.id is not None
        if idx >= bind_limit:
            out.append(
                CaliberCandidate(
                    apply="drop",
                    asset_id=int(caliber.id),
                    lineage_id=caliber.lineage_id,
                    trust_tier=caliber.trust_tier,
                    drop_reason="bind_limit",
                )
            )
            continue
        bound = BoundCaliber(
            caliber_id=int(caliber.id),
            lineage_id=caliber.lineage_id,
            label=caliber.label,
            fragment=dict(caliber.contract_fragment or {}),
            field_targets=list(caliber.field_targets or []),
            trust_tier=caliber.trust_tier,
        )
        out.append(
            CaliberCandidate(
                apply="bind",
                bound=bound,
                asset_id=int(caliber.id),
                lineage_id=caliber.lineage_id,
                trust_tier=caliber.trust_tier,
            )
        )
    return out
