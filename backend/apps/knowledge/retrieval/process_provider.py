"""Process episode weak retrieval — never Bind / certify."""

from __future__ import annotations

from typing import Any

from sqlmodel import Session, col, select

from apps.knowledge.db_models import ProcessEpisode


def recall_process_episodes(
    session: Session,
    *,
    oid: int,
    ds_id: int | None,
    limit: int = 3,
) -> list[dict[str, Any]]:
    stmt = (
        select(ProcessEpisode)
        .where(ProcessEpisode.oid == oid)
        .where(ProcessEpisode.enabled.is_(True))  # type: ignore[attr-defined]
        .order_by(col(ProcessEpisode.create_time).desc())
        .limit(limit)
    )
    if ds_id is not None:
        stmt = stmt.where(ProcessEpisode.datasource_id == ds_id)
    rows = list(session.exec(stmt).all())
    return [
        {
            "id": row.id,
            "lineage_id": row.lineage_id,
            "question_norm": row.question_norm,
            "episode": row.episode,
            "trust_tier": row.trust_tier,
            "apply": "exemplify",  # weak only; Compile may Drop
        }
        for row in rows
    ]
