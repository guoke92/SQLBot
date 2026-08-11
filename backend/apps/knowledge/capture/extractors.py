"""V-T* extractors — emit candidates for staging admission."""

from __future__ import annotations

from typing import Any

from apps.chat.query_specification import (
    QuerySpecification,
    parse_specification_fragment,
    requirement_fields,
)
from apps.knowledge.capture.snapshot import (
    TurnSnapshot,
    has_user_answer_requirements,
    specification_requirements,
)
from apps.knowledge.natural_key import predicate_looks_ephemeral

# Align with conversation.outcome_is_success (includes degraded partial success).
_CAPTURE_OK_OUTCOMES = frozenset({"success", "accepted", "completed", "ok", "degraded"})


def extract_v_t1_caliber(snapshot: TurnSnapshot) -> dict[str, Any] | None:
    """V-T1: clarification-chain success → caliber candidate (user-confirmed slots only)."""
    if snapshot.outcome not in _CAPTURE_OK_OUTCOMES:
        return None
    if snapshot.contract_status == "needs_clarification":
        return None
    if not has_user_answer_requirements(snapshot.specification):
        return None
    if snapshot.ds_id is None:
        return None

    specification = snapshot.specification
    requirements = specification_requirements(specification)
    confirmed: list[dict[str, Any]] = []
    field_targets: list[dict[str, Any]] = []
    for req in requirements:
        if not isinstance(req, dict):
            continue
        refs = [str(r) for r in (req.get("evidence_refs") or [])]
        if not any(r.startswith("user:answer:") for r in refs):
            continue
        if req.get("clause") == "predicate" or req.get("clause_type") == "predicate":
            if predicate_looks_ephemeral(req):
                continue
        confirmed.append(_clause_only(req))
        if not confirmed[-1].get("requirement_id") or not confirmed[-1].get(
            "business_label"
        ):
            confirmed.pop()
            continue

    if not confirmed:
        return None

    label = _label_from_requirements(confirmed) or snapshot.original_question[:80]
    fragment = {
        "requirements": confirmed,
        "version": specification.get("version"),
    }
    try:
        parsed_fragment = parse_specification_fragment(fragment)
    except ValueError:
        # A partial capture with dangling output/order references cannot be
        # certified or safely reused. Leave it out of staging instead of
        # creating a permanently failing capture job.
        return None
    field_targets = _field_targets_from_specification(
        parsed_fragment,
        snapshot.ds_id,
    )
    # Envelope for runner; staging payload is stripped to V-T3 shape in runner.
    return {
        "kind": "caliber",
        "trigger_id": "V-T1",
        "label": label,
        "summary": f"Captured from clarification on record {snapshot.record_id}",
        "contract_fragment": fragment,
        "field_targets": field_targets,
        "scope": {
            "ds_id": snapshot.ds_id,
            "assistant_id": snapshot.assistant_id,
        },
        "suggested_trust_tier": "admitted",
    }


def extract_process_episode(snapshot: TurnSnapshot) -> dict[str, Any] | None:
    """Weak process episode — never Bind / certify."""
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
    """Normalize capture/V-T3 payloads to the same staging shape."""
    return {
        "label": candidate.get("label"),
        "summary": candidate.get("summary"),
        "contract_fragment": candidate.get("contract_fragment")
        or candidate.get("fragment")
        or {},
        "field_targets": list(candidate.get("field_targets") or []),
    }


def _clause_only(req: dict[str, Any]) -> dict[str, Any]:
    """Persist clause only — drop clause_type / evidence noise for fingerprint SoT."""
    out = dict(req)
    clause = (
        out.pop("clause", None) or out.pop("clause_type", None) or out.pop("type", None)
    )
    if clause:
        out["clause"] = clause
    out.pop("clause_type", None)
    out.pop("type", None)
    # Evidence is turn-local; do not bake into reusable caliber fragment.
    out.pop("evidence_refs", None)
    out.pop("source", None)
    return out


def _field_targets_from_specification(
    specification: QuerySpecification,
    ds_id: int,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for requirement in specification.requirements:
        for ref in requirement_fields(requirement):
            if not ref.field:
                continue
            identity = (ref.resource.casefold(), ref.field.casefold())
            if identity in seen:
                continue
            seen.add(identity)
            out.append(
                {
                    "ds_id": ds_id,
                    "table_name": ref.resource,
                    "field_name": ref.field,
                    "field_id": None,
                    "table_id": None,
                }
            )
    return out


def _label_from_requirements(reqs: list[dict[str, Any]]) -> str:
    for req in reqs:
        if req.get("clause") == "output":
            label = req.get("business_label") or ""
            if label:
                return str(label)[:255]
            field = req.get("field") or req.get("output") or {}
            if isinstance(field, dict) and field.get("field"):
                return str(field["field"])[:255]
    return ""
