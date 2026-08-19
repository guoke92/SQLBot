"""Rule staging certification using the shared knowledge lifecycle."""

from __future__ import annotations

from sqlmodel import Session

from apps.knowledge.db_models import KnowledgeAsset


def certify_staging_rule(
    session: Session,
    *,
    staging_id: int,
    actor_user_id: int | None,
    oid: int,
) -> KnowledgeAsset:
    del session, staging_id, actor_user_id, oid
    raise ValueError(
        "runtime knowledge must be published from a 2.0 knowledge unit; "
        "staging is evidence only"
    )
