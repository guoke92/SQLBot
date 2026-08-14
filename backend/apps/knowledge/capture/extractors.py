"""Turn capture extractors for QueryIntent v1 knowledge assets."""

from __future__ import annotations

from typing import Any

from apps.chat.intent_defaults import parse_intent_default_fragment
from apps.chat.query_intent import IntentRevision
from apps.knowledge.capture.snapshot import (
    TurnSnapshot,
    has_user_answer_requirements,
)
from apps.knowledge.natural_key import predicate_looks_ephemeral

_CAPTURE_OK_OUTCOMES = frozenset({"success", "accepted", "completed", "ok", "degraded"})


def extract_v_t1_caliber(snapshot: TurnSnapshot) -> dict[str, Any] | None:
    """Capture only intent items explicitly supported by clarification evidence."""
    if snapshot.outcome not in _CAPTURE_OK_OUTCOMES or snapshot.ds_id is None:
        return None
    if not has_user_answer_requirements(snapshot.intent_revision):
        return None
    try:
        revision = IntentRevision.model_validate(snapshot.intent_revision)
    except ValueError:
        return None
    if revision.status != "accepted" or revision.execution_mode != "verified":
        return None

    defaults: list[dict[str, Any]] = []
    for item_key, value in revision.item_catalog.items():
        refs = revision.evidence_map.get(item_key, ())
        if not any(str(ref).startswith("user:answer:") for ref in refs):
            continue
        parts = item_key.split(":", 3)
        if len(parts) < 3 or not parts[0].startswith("d"):
            continue
        dataset_index = int(parts[0][1:])
        kind = parts[1]
        if kind not in {"output", "group", "filter", "time", "order"}:
            continue
        if kind == "filter" and predicate_looks_ephemeral(value):
            continue
        defaults.append(
            {
                "dataset_subject": revision.intent.datasets[dataset_index].subject,
                "kind": kind,
                "value": value,
            }
        )
    if not defaults:
        return None
    fragment = {"version": 1, "intent_defaults": defaults}
    try:
        parse_intent_default_fragment(fragment)
    except ValueError:
        return None
    return {
        "kind": "caliber",
        "trigger_id": "V-T1",
        "label": str(defaults[0]["value"].get("business_name") or "业务口径")[:255],
        "summary": f"Captured from clarification on record {snapshot.record_id}",
        "contract_fragment": fragment,
        "field_targets": [],
        "scope": {"ds_id": snapshot.ds_id, "assistant_id": snapshot.assistant_id},
        "suggested_trust_tier": "admitted",
    }


def extract_process_episode(snapshot: TurnSnapshot) -> dict[str, Any] | None:
    if snapshot.outcome not in _CAPTURE_OK_OUTCOMES:
        return None
    return {
        "kind": "process",
        "trigger_id": "V-T9",
        "question_norm": (snapshot.original_question or "")[:512],
        "episode": {
            "status": snapshot.contract_status,
            "clarification_answered": snapshot.clarification_answered,
            "sql_count": len(snapshot.sql_list),
            "knowledge_apply": snapshot.knowledge_apply[:8],
        },
        "scope": {"ds_id": snapshot.ds_id},
        "suggested_trust_tier": "published",
    }


def staging_payload_from_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "label": candidate.get("label"),
        "summary": candidate.get("summary"),
        "contract_fragment": candidate.get("contract_fragment")
        or candidate.get("fragment")
        or {},
        "field_targets": list(candidate.get("field_targets") or []),
    }
