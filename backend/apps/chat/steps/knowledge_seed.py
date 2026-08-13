"""Apply certified conversation knowledge to the v3 query specification."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import orjson

from apps.chat.query_specification import (
    OrderRequirement,
    OutputRequirement,
    QuerySpecification,
    SpecificationRequirement,
    is_user_evidence_ref,
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
        is_user_evidence_ref(ref) for ref in requirement.evidence_refs
    )


def _dependency_ids(requirement: SpecificationRequirement) -> tuple[str, ...]:
    if isinstance(requirement, OutputRequirement):
        return requirement.operand_requirement_ids
    if isinstance(requirement, OrderRequirement) and requirement.output_requirement_id:
        return (requirement.output_requirement_id,)
    return ()


def _dependent_closure(
    requirements: list[SpecificationRequirement],
    replaced_ids: set[str],
) -> set[str]:
    closure = set(replaced_ids)
    changed = True
    while changed:
        changed = False
        for requirement in requirements:
            if requirement.requirement_id in closure:
                continue
            if closure.intersection(_dependency_ids(requirement)):
                closure.add(requirement.requirement_id)
                changed = True
    return closure


def apply_knowledge_seeds(
    specification: QuerySpecification,
    seeds: list[KnowledgeSeed],
) -> KnowledgeApplication:
    """Deterministically merge certified defaults into the active specification.

    A caliber is one semantic unit. Any conflicting user-confirmed target drops
    that unit; otherwise its clauses replace weaker model inferences and are
    inserted directly. This keeps user evidence authoritative without relying
    on another LLM turn to remember certified knowledge.
    """
    current = list(specification.requirements)
    logs: list[ApplyHit] = []
    for seed in seeds:
        seed_specification = _seed_specification(seed)
        current_specification = _requirements_specification(
            specification,
            current,
        )
        current_by_semantic = {
            _identity(
                requirement_semantic_material(requirement, current_specification)
            ): requirement
            for requirement in current
        }
        current_by_target: dict[bytes, list[SpecificationRequirement]] = {}
        for requirement in current:
            target = _identity(
                requirement_target_material(requirement, current_specification)
            )
            current_by_target.setdefault(target, []).append(requirement)

        semantic_pairs = [
            (
                requirement,
                _identity(
                    requirement_semantic_material(requirement, seed_specification)
                ),
                _identity(requirement_target_material(requirement, seed_specification)),
            )
            for requirement in seed.requirements
        ]
        user_conflicts: list[str] = []
        knowledge_conflicts: list[str] = []
        for requirement, semantic_key, target_key in semantic_pairs:
            if semantic_key in current_by_semantic:
                continue
            conflicts = current_by_target.get(target_key, [])
            if any(_has_user_evidence(item) for item in conflicts):
                user_conflicts.append(requirement.requirement_id)
            elif any(
                _has_user_evidence(item)
                for item in current
                if item.requirement_id
                in _dependent_closure(
                    current,
                    {conflict.requirement_id for conflict in conflicts},
                )
            ):
                user_conflicts.append(requirement.requirement_id)
            elif any(item.source == "knowledge" for item in conflicts):
                knowledge_conflicts.append(requirement.requirement_id)

        if user_conflicts or knowledge_conflicts:
            logs.append(
                ApplyHit(
                    asset_kind="caliber",
                    asset_id=seed.caliber_id,
                    lineage_id=seed.lineage_id,
                    trust_tier=seed.trust_tier,
                    apply="drop",
                    reason="user_override" if user_conflicts else "knowledge_conflict",
                    meta={
                        "label": seed.label,
                        "conflicting_requirements": user_conflicts
                        or knowledge_conflicts,
                    },
                )
            )
            continue

        replace_ids: set[str] = set()
        updates: dict[str, SpecificationRequirement] = {}
        additions: list[SpecificationRequirement] = []
        applied: list[str] = []
        for requirement, semantic_key, target_key in semantic_pairs:
            match = current_by_semantic.get(semantic_key)
            if match is not None:
                refs = tuple(dict.fromkeys((*match.evidence_refs, seed.evidence_ref)))
                updates[match.requirement_id] = match.model_copy(
                    update={
                        "source": "user" if _has_user_evidence(match) else "knowledge",
                        "evidence_refs": refs,
                        "confidence": max(match.confidence, requirement.confidence),
                    }
                )
            else:
                directly_replaced = {
                    item.requirement_id
                    for item in current_by_target.get(target_key, [])
                    if not _has_user_evidence(item)
                }
                replace_ids.update(_dependent_closure(current, directly_replaced))
                additions.append(requirement)
            applied.append(requirement.requirement_id)
        current = [
            updates.get(item.requirement_id, item)
            for item in current
            if item.requirement_id not in replace_ids
        ]
        current.extend(additions)
        logs.append(
            ApplyHit(
                asset_kind="caliber",
                asset_id=seed.caliber_id,
                lineage_id=seed.lineage_id,
                trust_tier=seed.trust_tier,
                apply="bind",
                reason="certified_seed_applied",
                meta={
                    "label": seed.label,
                    "applied_requirements": applied,
                    "replaced_inferences": sorted(replace_ids),
                },
            )
        )

    updated_specification = normalize_specification(
        _requirements_specification(specification, current)
    )
    return KnowledgeApplication(
        specification=updated_specification,
        apply_log=tuple(logs),
    )


def _seed_specification(seed: KnowledgeSeed) -> QuerySpecification:
    return _requirements_specification(None, list(seed.requirements))


def _requirements_specification(
    base: QuerySpecification | None,
    requirements: list[SpecificationRequirement],
) -> QuerySpecification:
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
    for requirement in requirements:
        buckets[names[requirement.clause]].append(requirement)
    common = (
        {
            "version": base.version,
            "revision": base.revision,
            "limit": base.limit,
            "assumptions": base.assumptions,
            "evidence_refs": base.evidence_refs,
            "confidence": base.confidence,
        }
        if base is not None
        else {"revision": 1}
    )
    return QuerySpecification.model_validate({**common, **buckets})
