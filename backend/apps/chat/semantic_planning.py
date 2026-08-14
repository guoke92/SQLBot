"""Business ambiguity and semantic planning decision contracts."""

from __future__ import annotations

import hashlib
from typing import Any, Literal, Self

import orjson
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, model_validator

from apps.chat.query_intent import QueryIntent


def stable_id(prefix: str, *parts: str) -> str:
    body = "\x1f".join(part.strip().casefold() for part in parts if part)
    return f"{prefix}_{hashlib.sha256(body.encode()).hexdigest()[:16]}"


class CandidateResolution(BaseModel):
    model_config = ConfigDict(extra="forbid")
    option_id: str = ""
    label: str
    description: str = ""
    impact: str = ""
    resolution: dict[str, Any] = Field(default_factory=dict)
    evidence_refs: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_resolution(self) -> Self:
        if not self.resolution:
            raise ValueError("Clarification option requires a structured resolution")
        return self


class Ambiguity(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ambiguity_id: str = ""
    business_question: str
    reason: str = ""
    impact_level: Literal["low", "medium", "high"] = "medium"
    candidate_resolutions: list[CandidateResolution] = Field(min_length=2, max_length=3)
    recommended_candidate_id: str | None = None
    recommendation_reason: str = ""
    can_assume: bool = False

    @model_validator(mode="after")
    def validate_candidates(self) -> Self:
        # IDs belong to the service, not to model wording or a model-invented
        # axis name. The mutually exclusive structured resolutions are the
        # semantic identity of the business decision.
        resolution_identities = sorted(
            orjson.dumps(
                candidate.resolution,
                option=orjson.OPT_SORT_KEYS,
                default=str,
            ).decode()
            for candidate in self.candidate_resolutions
        )
        self.ambiguity_id = stable_id("amb", *resolution_identities)
        supplied_to_stable: dict[str, str] = {}
        for candidate in self.candidate_resolutions:
            supplied_id = candidate.option_id
            candidate.option_id = stable_id(
                "opt",
                self.ambiguity_id,
                orjson.dumps(
                    candidate.resolution,
                    option=orjson.OPT_SORT_KEYS,
                    default=str,
                ).decode(),
            )
            if supplied_id:
                supplied_to_stable[supplied_id] = candidate.option_id
        if self.recommended_candidate_id in supplied_to_stable:
            self.recommended_candidate_id = supplied_to_stable[
                self.recommended_candidate_id
            ]
        ids = [item.option_id for item in self.candidate_resolutions]
        if len(ids) != len(set(ids)):
            raise ValueError("Ambiguity candidate IDs must be unique")
        if self.recommended_candidate_id and self.recommended_candidate_id not in ids:
            raise ValueError("Recommended candidate must exist")
        return self


class AmbiguitySet(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ambiguities: list[Ambiguity] = Field(min_length=1, max_length=2)
    summary: str = ""


def public_ambiguity_payload(ambiguity_set: AmbiguitySet) -> dict[str, Any]:
    """Return the complete, business-facing clarification card payload."""
    payload = ambiguity_set.model_dump(mode="json")
    compact: list[dict[str, Any]] = []
    for item in payload.get("ambiguities") or []:
        if not isinstance(item, dict):
            continue
        options = []
        for option in item.get("candidate_resolutions") or []:
            if not isinstance(option, dict):
                continue
            options.append(
                {
                    "option_id": option.get("option_id") or "",
                    "label": option.get("label") or "",
                    "description": option.get("description") or "",
                    "impact": option.get("impact") or "",
                    "resolution": option.get("resolution") or {},
                }
            )
        compact.append(
            {
                "ambiguity_id": item.get("ambiguity_id") or "",
                "business_question": item.get("business_question") or "",
                "reason": item.get("reason") or "",
                "impact_level": item.get("impact_level") or "medium",
                "candidate_resolutions": options,
                "recommended_candidate_id": item.get("recommended_candidate_id"),
                "recommendation_reason": item.get("recommendation_reason") or "",
                "can_assume": bool(item.get("can_assume")),
            }
        )
    return {"summary": payload.get("summary") or "", "ambiguities": compact}


def enforce_clarification_policy(
    ambiguity_set: AmbiguitySet,
    *,
    resolved_ambiguity_ids: set[str] | None = None,
) -> AmbiguitySet:
    """Accept only unresolved, result-changing business questions.

    The model discovers ambiguities; this deterministic boundary decides
    whether they are allowed to pause a run. Non-blocking uncertainty belongs
    in ``QueryIntent.assumptions`` and must never become an optional
    interrupt that the API cannot meaningfully complete.
    """
    resolved = {item.strip() for item in resolved_ambiguity_ids or set()}
    identities = [item.ambiguity_id for item in ambiguity_set.ambiguities]
    if len(identities) != len(set(identities)):
        raise ValueError("Clarification questions must be semantically unique")
    repeated = set(identities) & resolved
    if repeated:
        raise ValueError(
            "Planner repeated resolved ambiguities: " + ", ".join(sorted(repeated))
        )
    non_blocking = [
        item.business_question
        for item in ambiguity_set.ambiguities
        if item.can_assume or item.impact_level == "low"
    ]
    if non_blocking:
        raise ValueError(
            "Non-blocking uncertainty must be recorded as assumptions: "
            + ", ".join(non_blocking)
        )
    return ambiguity_set


class QueryPlanCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    plan_id: str = ""
    dataset_index: int = Field(ge=0)
    payload: dict[str, Any]
    grounding_manifest: list[dict[str, Any]] = Field(default_factory=list)

    @model_validator(mode="after")
    def assign_id(self) -> Self:
        # Physical candidate identity is service-owned and content-addressed.
        # A model-provided ID could alias a repaired payload to stale results.
        self.plan_id = stable_id(
            "plan",
            str(self.dataset_index),
            orjson.dumps(
                self.payload,
                option=orjson.OPT_SORT_KEYS,
                default=str,
            ).decode(),
        )
        return self


class NeedClarification(BaseModel):
    model_config = ConfigDict(extra="forbid")
    decision: Literal["needs_clarification"] = "needs_clarification"
    ambiguity_set: AmbiguitySet
    draft_intent: QueryIntent | None = None
    held_candidates: list[QueryPlanCandidate] = Field(default_factory=list)
    can_proceed_with_assumptions: bool = False


class Ready(BaseModel):
    model_config = ConfigDict(extra="forbid")
    decision: Literal["ready"] = "ready"
    intent: QueryIntent
    candidates: list[QueryPlanCandidate] = Field(min_length=1)
    evidence_bindings: list[dict[str, Any]] = Field(default_factory=list)
    summary: str = ""

    @model_validator(mode="after")
    def validate_candidate_datasets(self) -> Self:
        upper = len(self.intent.datasets)
        indices = [item.dataset_index for item in self.candidates]
        if len(indices) != len(set(indices)):
            raise ValueError("Each intent dataset must have exactly one plan candidate")
        invalid = [
            item.dataset_index
            for item in self.candidates
            if item.dataset_index >= upper
        ]
        if invalid:
            raise ValueError("Plan candidate references an unknown intent dataset")
        covered = {item.dataset_index for item in self.candidates}
        required = {
            index
            for index, dataset in enumerate(self.intent.datasets)
            if dataset.required
        }
        if not required.issubset(covered):
            raise ValueError("Every required intent dataset needs a plan candidate")
        return self


class QueryUnsupported(BaseModel):
    """A query-shaped turn that cannot be answered by the selected context."""

    model_config = ConfigDict(extra="forbid")
    decision: Literal["unsupported"] = "unsupported"
    message: str
    reason_code: str = "QUERY_NOT_SUPPORTED"

    @model_validator(mode="after")
    def validate_message(self) -> Self:
        self.message = " ".join(self.message.split()).strip()
        self.reason_code = self.reason_code.strip().upper() or "QUERY_NOT_SUPPORTED"
        if not self.message:
            raise ValueError(
                "Unsupported query decision requires a user-facing message"
            )
        return self


PlanningDecision = NeedClarification | Ready | QueryUnsupported
PLANNING_DECISION_ADAPTER = TypeAdapter(PlanningDecision)
