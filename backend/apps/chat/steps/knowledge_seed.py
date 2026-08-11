"""Apply certified conversation knowledge to the v3 query specification."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import orjson

from apps.chat.query_specification import (
    QuerySpecification,
    SpecificationRequirement,
    normalize_specification,
    parse_specification_fragment,
    requirement_semantic_material,
    requirement_target_material,
)
from apps.knowledge.compile.bundle import ApplyHit, BoundCaliber


@dataclass(frozen=True)
class KnowledgeSeed:
    caliber_id: int
    lineage_id: str
    label: str
    trust_tier: str
    evidence_ref: str
    requirements: tuple[SpecificationRequirement, ...]

    def as_prompt_context(self) -> dict[str, Any]:
        return {
            "caliber_id": self.caliber_id,
            "label": self.label,
            "evidence_ref": self.evidence_ref,
            "requirements": [
                item.model_dump(mode="json") for item in self.requirements
            ],
        }


@dataclass(frozen=True)
class KnowledgeApplication:
    specification: QuerySpecification
    apply_log: tuple[ApplyHit, ...]
    missing: tuple[str, ...]


def prepare_knowledge_seed(
    bound: BoundCaliber,
    *,
    evidence_ref: str,
) -> KnowledgeSeed:
    """Parse one strongly applicable certified caliber into typed requirements."""
    specification = normalize_specification(
        parse_specification_fragment(bound.fragment)
    )
    requirements: list[SpecificationRequirement] = []
    for requirement in specification.requirements:
        refs = tuple(dict.fromkeys((*requirement.evidence_refs, evidence_ref)))
        requirements.append(
            requirement.model_copy(
                update={
                    "source": "knowledge",
                    "evidence_refs": refs,
                    "confidence": max(requirement.confidence, 0.9),
                }
            )
        )
    return KnowledgeSeed(
        caliber_id=bound.caliber_id,
        lineage_id=bound.lineage_id,
        label=bound.label,
        trust_tier=bound.trust_tier,
        evidence_ref=evidence_ref,
        requirements=tuple(requirements),
    )


def _identity(value: dict[str, Any]) -> bytes:
    return orjson.dumps(value, option=orjson.OPT_SORT_KEYS)


def _has_user_evidence(requirement: SpecificationRequirement) -> bool:
    return any(
        ref == "user:question" or ref.startswith("user:answer:")
        for ref in requirement.evidence_refs
    )


def apply_knowledge_seeds(
    specification: QuerySpecification,
    seeds: list[KnowledgeSeed],
) -> KnowledgeApplication:
    """Protect applicable defaults and derive truthful application decisions.

    Exact semantic matches receive knowledge provenance. A conflicting active
    user clause wins. Omitting a seed without a user conflict is a planner
    defect and is returned as ``missing`` for the existing repair turn.
    """
    current_by_semantic: dict[bytes, SpecificationRequirement] = {}
    user_by_target: dict[bytes, SpecificationRequirement] = {}
    for requirement in specification.requirements:
        current_by_semantic[
            _identity(requirement_semantic_material(requirement, specification))
        ] = requirement
        if _has_user_evidence(requirement):
            user_by_target[
                _identity(requirement_target_material(requirement, specification))
            ] = requirement

    updates: dict[str, SpecificationRequirement] = {}
    missing: list[str] = []
    logs: list[ApplyHit] = []
    for seed in seeds:
        seed_specification = _seed_specification(seed)
        applied: list[str] = []
        overridden: list[str] = []
        for requirement in seed.requirements:
            semantic_key = _identity(
                requirement_semantic_material(
                    requirement,
                    seed_specification,
                )
            )
            current = current_by_semantic.get(semantic_key)
            if current is not None:
                refs = tuple(dict.fromkeys((*current.evidence_refs, seed.evidence_ref)))
                updates[current.requirement_id] = current.model_copy(
                    update={
                        "source": "user"
                        if _has_user_evidence(current)
                        else "knowledge",
                        "evidence_refs": refs,
                        "confidence": max(current.confidence, requirement.confidence),
                    }
                )
                applied.append(requirement.requirement_id)
                continue
            target_key = _identity(
                requirement_target_material(requirement, seed_specification)
            )
            if target_key in user_by_target:
                overridden.append(requirement.requirement_id)
                continue
            missing.append(f"{seed.caliber_id}:{requirement.requirement_id}")

        if applied:
            logs.append(
                ApplyHit(
                    asset_kind="caliber",
                    asset_id=seed.caliber_id,
                    lineage_id=seed.lineage_id,
                    trust_tier=seed.trust_tier,
                    apply="bind",
                    reason=(
                        "certified_seed_applied_with_user_override"
                        if overridden
                        else "certified_seed_applied"
                    ),
                    meta={
                        "label": seed.label,
                        "applied_requirements": applied,
                        "overridden_requirements": overridden,
                    },
                )
            )
        elif overridden:
            logs.append(
                ApplyHit(
                    asset_kind="caliber",
                    asset_id=seed.caliber_id,
                    lineage_id=seed.lineage_id,
                    trust_tier=seed.trust_tier,
                    apply="drop",
                    reason="user_override",
                    meta={
                        "label": seed.label,
                        "overridden_requirements": overridden,
                    },
                )
            )

    rewritten: dict[str, tuple[SpecificationRequirement, ...]] = {}
    for bucket in (
        "outputs",
        "predicates",
        "group_by",
        "time_windows",
        "order_by",
        "business_relations",
    ):
        rewritten[bucket] = tuple(
            updates.get(requirement.requirement_id, requirement)
            for requirement in getattr(specification, bucket)
        )
    updated_specification = QuerySpecification.model_validate(
        {**specification.model_dump(mode="python"), **rewritten}
    )
    return KnowledgeApplication(
        specification=updated_specification,
        apply_log=tuple(logs),
        missing=tuple(missing),
    )


def _seed_specification(seed: KnowledgeSeed) -> QuerySpecification:
    buckets: dict[str, list[SpecificationRequirement]] = {
        "outputs": [],
        "predicates": [],
        "group_by": [],
        "time_windows": [],
        "order_by": [],
        "business_relations": [],
    }
    names = {
        "output": "outputs",
        "predicate": "predicates",
        "group": "group_by",
        "time_window": "time_windows",
        "order": "order_by",
        "business_relation": "business_relations",
    }
    for requirement in seed.requirements:
        buckets[names[requirement.clause]].append(requirement)
    return QuerySpecification.model_validate({"revision": 1, **buckets})
