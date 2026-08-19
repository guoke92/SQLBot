"""Capture verified v7 business resolutions and query patterns."""

from __future__ import annotations

from typing import Any

from apps.knowledge.capture.snapshot import TurnSnapshot

_CAPTURE_OK_OUTCOMES = frozenset({"success", "accepted", "completed", "ok", "degraded"})


def _eligible(snapshot: TurnSnapshot) -> bool:
    return (
        snapshot.outcome in _CAPTURE_OK_OUTCOMES
        and snapshot.validation_status == "verified"
        and snapshot.ds_id is not None
        and bool(snapshot.sql_list)
    )


def extract_business_resolution(snapshot: TurnSnapshot) -> dict[str, Any] | None:
    if not _eligible(snapshot) or not snapshot.clarification_resolutions:
        return None
    resolutions = [
        item for item in snapshot.clarification_resolutions if isinstance(item, dict)
    ]
    if not resolutions:
        return None
    return {
        "kind": "caliber",
        "trigger_id": "V7-BUSINESS-RESOLUTION",
        "label": str(
            resolutions[0].get("question")
            or resolutions[0].get("business_question")
            or "已确认业务口径"
        )[:255],
        "summary": f"Business resolution captured from record {snapshot.record_id}",
        "contract_fragment": {
            "version": 1,
            "asset_type": "business_resolution",
            "resolutions": resolutions,
        },
        "field_targets": [],
        "scope": {"ds_id": snapshot.ds_id, "assistant_id": snapshot.assistant_id},
        "suggested_trust_tier": "admitted",
    }


def extract_query_pattern(snapshot: TurnSnapshot) -> dict[str, Any] | None:
    if not _eligible(snapshot):
        return None
    return {
        "kind": "rule",
        "trigger_id": "V7-QUERY-PATTERN",
        "label": (snapshot.original_question or "查询模式")[:255],
        "summary": f"Verified query pattern from record {snapshot.record_id}",
        "contract_fragment": {
            "version": 1,
            "asset_type": "query_pattern",
            "question": snapshot.original_question,
            "queries": snapshot.sql_list,
            "plan_facts": snapshot.plan_facts,
        },
        "field_targets": [],
        "scope": {"ds_id": snapshot.ds_id, "assistant_id": snapshot.assistant_id},
        "suggested_trust_tier": "published",
    }


def extract_process_episode(snapshot: TurnSnapshot) -> dict[str, Any] | None:
    if snapshot.outcome not in _CAPTURE_OK_OUTCOMES:
        return None
    return {
        "kind": "process",
        "trigger_id": "V-T9",
        "question_norm": (snapshot.original_question or "")[:512],
        "episode": {
            "status": snapshot.validation_status,
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
        "contract_fragment": candidate.get("contract_fragment") or {},
        "field_targets": list(candidate.get("field_targets") or []),
    }
