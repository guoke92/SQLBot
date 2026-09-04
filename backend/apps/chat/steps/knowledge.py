"""Knowledge compilation and retrieval stub (legacy unit path retired)."""

from __future__ import annotations

from typing import Any, Sequence
from sqlmodel import Session
from apps.datasource.access import AccessScope

def match_knowledge(
    llm_service: Any,
    session: Session,
    oid: int | None = None,
    ds_id: int | None = None,
    access_scope: AccessScope | None = None,
    *,
    stage: str = "assess",
    include_examples: bool = False,
    seed_revision_ids: Sequence[int] = (),
    seed_policy: str = "none",
) -> list[Any]:
    return []

def get_compiled_knowledge(llm_service: Any) -> Any | None:
    return None
