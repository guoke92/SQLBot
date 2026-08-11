"""Retrieve strongly applicable certified calibers for v3 specification seeds."""

from __future__ import annotations

import re
from dataclasses import dataclass

from sqlmodel import Session, col, or_, select

from apps.knowledge.compile.bundle import BoundCaliber
from apps.knowledge.db_models import KnowledgeAsset

# Without embedding ranking: hard cap Bind to one relevant caliber.
_DEFAULT_BIND_LIMIT = 1


@dataclass
class CaliberCandidate:
    apply: str  # bind | drop
    bound: BoundCaliber | None = None
    asset_id: int | None = None
    lineage_id: str | None = None
    trust_tier: str | None = None
    drop_reason: str | None = None


def _is_bindable(asset: KnowledgeAsset) -> bool:
    if not asset.enabled or asset.superseded_by is not None:
        return False
    return bool(asset.certified and asset.trust_tier == "certified")


def _normalized_phrase(value: str) -> str:
    return re.sub(r"[^\w\u3400-\u9fff]+", "", (value or "").casefold())


def _applicability_score(asset: KnowledgeAsset, question: str) -> float:
    """Require an explicit business phrase before a caliber can be protected."""
    q = _normalized_phrase(question)
    if not q:
        return 0.0
    score = 0.0
    label = _normalized_phrase(asset.label)
    if len(label) >= 2 and label in q:
        score = max(score, 10.0 + len(label))
    for syn in (asset.payload or {}).get("synonyms") or []:
        phrase = _normalized_phrase(str(syn))
        if len(phrase) >= 2 and phrase in q:
            score = max(score, 12.0 + len(phrase))
    return score


def recall_bindable_calibers(
    session: Session,
    *,
    oid: int,
    ds_id: int,
    question: str,
    limit: int = _DEFAULT_BIND_LIMIT,
) -> list[CaliberCandidate]:
    """Return caliber candidates for the question.

    Staging is never queried. A protected seed requires an explicit label or
    synonym phrase match and is capped at ``limit`` (default 1). Unrelated or
    uncertified rows are dropped before semantic planning.
    """
    bind_limit = max(1, min(int(limit), 3))
    stmt = (
        select(KnowledgeAsset)
        .where(KnowledgeAsset.kind == "caliber")
        .where(KnowledgeAsset.oid == oid)
        .where(KnowledgeAsset.enabled.is_(True))  # type: ignore[attr-defined]
        .where(KnowledgeAsset.valid_to.is_(None))  # type: ignore[attr-defined]
        .where(KnowledgeAsset.superseded_by.is_(None))  # type: ignore[attr-defined]
        .where(
            or_(
                KnowledgeAsset.datasource_id == ds_id,
                KnowledgeAsset.datasource_id.is_(None),  # type: ignore[attr-defined]
            )
        )
        .order_by(col(KnowledgeAsset.update_time).desc())
        .limit(40)
    )
    rows = list(session.exec(stmt).all())
    scored: list[tuple[float, KnowledgeAsset]] = []
    out: list[CaliberCandidate] = []

    for asset in rows:
        assert asset.id is not None
        if not _is_bindable(asset):
            out.append(
                CaliberCandidate(
                    apply="drop",
                    asset_id=int(asset.id),
                    lineage_id=asset.lineage_id,
                    trust_tier=asset.trust_tier,
                    drop_reason="not_certified",
                )
            )
            continue
        score = _applicability_score(asset, question)
        if score <= 0:
            out.append(
                CaliberCandidate(
                    apply="drop",
                    asset_id=int(asset.id),
                    lineage_id=asset.lineage_id,
                    trust_tier=asset.trust_tier,
                    drop_reason="no_relevance",
                )
            )
            continue
        scored.append((score, asset))

    scored.sort(
        key=lambda item: (
            -item[0],
            -(item[1].update_time.timestamp() if item[1].update_time else 0),
        )
    )
    for idx, (_score, asset) in enumerate(scored):
        assert asset.id is not None
        if idx >= bind_limit:
            out.append(
                CaliberCandidate(
                    apply="drop",
                    asset_id=int(asset.id),
                    lineage_id=asset.lineage_id,
                    trust_tier=asset.trust_tier,
                    drop_reason="bind_limit",
                )
            )
            continue
        payload = asset.payload or {}
        bound = BoundCaliber(
            caliber_id=int(asset.id),
            lineage_id=asset.lineage_id,
            label=asset.label,
            fragment=dict(payload.get("contract_fragment") or {}),
            field_targets=list(payload.get("field_targets") or []),
            trust_tier=asset.trust_tier,
        )
        out.append(
            CaliberCandidate(
                apply="bind",
                bound=bound,
                asset_id=int(asset.id),
                lineage_id=asset.lineage_id,
                trust_tier=asset.trust_tier,
            )
        )
    return out
