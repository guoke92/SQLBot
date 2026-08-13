"""One idempotent append boundary for the knowledge evidence ledger."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.dialects.postgresql import insert
from sqlmodel import Session, select

from apps.knowledge.db_models import KnowledgeEvidence


def append_evidence_event(
    session: Session,
    *,
    event_key: str,
    asset_id: int | None,
    asset_kind: str,
    signal_kind: str,
    record_id: int | None,
    fact: dict[str, Any],
    natural_key: str | None = None,
) -> KnowledgeEvidence:
    """Append once under database uniqueness and return the canonical row."""
    key = event_key[:255]
    stmt = (
        insert(KnowledgeEvidence)
        .values(
            event_key=key,
            asset_id=asset_id,
            asset_kind=asset_kind,
            natural_key=natural_key,
            signal_kind=signal_kind,
            record_id=record_id,
            fact=fact,
            create_time=datetime.utcnow(),
        )
        .on_conflict_do_nothing(index_elements=["event_key"])
        .returning(KnowledgeEvidence.id)
    )
    inserted_id = session.scalar(stmt)
    if inserted_id is not None:
        row = session.get(KnowledgeEvidence, int(inserted_id))
        if row is not None:
            return row
    existing = session.exec(
        select(KnowledgeEvidence).where(KnowledgeEvidence.event_key == key)
    ).first()
    if existing is None:  # pragma: no cover - protects unusual DB adapters
        raise RuntimeError(f"knowledge evidence append failed for {key}")
    return existing


def reproduce_event_key(natural_key: str, record_id: int) -> str:
    return f"reproduce:{natural_key}:{record_id}"


def apply_event_key(
    record_id: int, asset_kind: str, asset_id: int, apply_action: str
) -> str:
    return f"apply:{record_id}:{asset_kind}:{asset_id}:{apply_action}"


def feedback_event_key(record_id: int, revision: int) -> str:
    return f"feedback:{record_id}:{revision}"


def usage_event_key(
    record_id: int, asset_kind: str, asset_id: int, usage_kind: str
) -> str:
    return f"usage:{record_id}:{asset_kind}:{asset_id}:{usage_kind}"
