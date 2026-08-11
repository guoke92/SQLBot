"""Example retrieval adapting data_training (sole Exemplify channel)."""

from __future__ import annotations

from typing import Any

from sqlmodel import Session

from apps.data_training.curd.data_training import get_training_template


def recall_examples(
    session: Session,
    *,
    question: str,
    oid: int,
    ds_id: int | None,
    advanced_application_id: int | None = None,
    training_type: str | None = None,
) -> list[dict[str, Any]]:
    """Return example dicts; Compile applies budget / Exemplify.

    Single retrieval entry — callers must not bypass with get_training_template.
    """
    if advanced_application_id is not None:
        _template, example_list = get_training_template(
            session,
            question,
            oid,
            None,
            advanced_application_id,
            training_type=training_type,
        )
    else:
        _template, example_list = get_training_template(
            session,
            question,
            oid,
            ds_id,
            training_type=training_type,
        )
    del _template
    examples: list[dict[str, Any]] = []
    for item in example_list or []:
        if not isinstance(item, dict):
            continue
        meta = item.get("knowledge_meta") or {}
        examples.append(
            {
                "id": item.get("id"),
                "question": item.get("question"),
                "sql": item.get("suggestion-answer"),
                "similarity": item.get("similarity"),
                "trust_tier": meta.get("trust_tier") or "published",
                "knowledge_meta": meta,
            }
        )
    return examples
