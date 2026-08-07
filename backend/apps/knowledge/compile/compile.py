"""Knowledge Compile — sole apply gate for NLQ knowledge."""

from __future__ import annotations

from typing import Any

from sqlmodel import Session

from apps.knowledge.compile.bundle import (
    ApplyHit,
    BoundCaliber,
    CompiledKnowledge,
    CompileStage,
)
from apps.knowledge.policy import KnowledgePolicy, get_knowledge_policy
from apps.knowledge.service import recall_knowledge


def compile_knowledge_for_turn(
    session: Session,
    *,
    stage: CompileStage,
    question: str,
    oid: int,
    ds_id: int | None,
    advanced_application_id: int | None = None,
    policy: KnowledgePolicy | dict[str, Any] | None = None,
    include_calibers: bool = True,
    include_examples: bool = False,
    training_type: str | None = None,
    has_confirmed_joins: bool | None = None,
) -> CompiledKnowledge:
    """Assemble a CompiledKnowledge for the given NLQ stage.

    Phase A: Term + Dict via recall_knowledge (behavior-preserving).
    Phase B+: certified Caliber Bind; Phase C+: examples + budgets.
    """
    resolved = (
        policy
        if isinstance(policy, KnowledgePolicy)
        else get_knowledge_policy(policy)
    )
    budgets = resolved.compile_budgets

    base = recall_knowledge(
        session,
        question=question,
        oid=oid,
        ds_id=ds_id,
        advanced_application_id=advanced_application_id,
    )
    apply_log: list[ApplyHit] = []
    for match in base.matches:
        if "entity_binding" in match.usages:
            apply_log.append(
                ApplyHit(
                    asset_kind="dictionary",
                    asset_id=None,
                    trust_tier="trusted",
                    apply="bind",
                    reason="entity_binding",
                    meta={"query": match.query, "canonical": match.canonical},
                )
            )
        if "prompt" in match.usages:
            apply_log.append(
                ApplyHit(
                    asset_kind="terminology",
                    asset_id=None,
                    trust_tier="published",
                    apply="constrain",
                    reason="terminology_prompt",
                    meta={"query": match.query, "canonical": match.canonical},
                )
            )

    bound_calibers: list[BoundCaliber] = []
    constraint_cards: list[dict[str, Any]] = []
    if include_calibers and ds_id is not None and advanced_application_id is None:
        from apps.knowledge.retrieval.caliber_provider import recall_bindable_calibers

        candidates = recall_bindable_calibers(
            session,
            oid=oid,
            ds_id=ds_id,
            question=question,
            policy=resolved,
        )
        for item in candidates:
            if item.apply == "bind":
                bound_calibers.append(item.bound)
                apply_log.append(
                    ApplyHit(
                        asset_kind="caliber",
                        asset_id=item.bound.caliber_id,
                        lineage_id=item.bound.lineage_id,
                        trust_tier=item.bound.trust_tier,
                        apply="bind",
                        reason="certified_caliber",
                        meta={"label": item.bound.label},
                    )
                )
            elif item.apply == "constrain":
                if (
                    stage == "assess"
                    and len(constraint_cards) >= budgets.assess_constrain_cards
                ):
                    apply_log.append(
                        ApplyHit(
                            asset_kind="caliber",
                            asset_id=item.asset_id,
                            lineage_id=item.lineage_id,
                            trust_tier=item.trust_tier,
                            apply="drop",
                            reason="assess_constrain_budget",
                        )
                    )
                    continue
                constraint_cards.append(item.card)
                apply_log.append(
                    ApplyHit(
                        asset_kind="caliber",
                        asset_id=item.asset_id,
                        lineage_id=item.lineage_id,
                        trust_tier=item.trust_tier,
                        apply="constrain",
                        reason="uncertified_or_trusted_caliber",
                        meta={"label": item.card.get("label")},
                    )
                )
            else:
                apply_log.append(
                    ApplyHit(
                        asset_kind="caliber",
                        asset_id=item.asset_id,
                        lineage_id=item.lineage_id,
                        trust_tier=item.trust_tier,
                        apply="drop",
                        reason=item.drop_reason or "policy_drop",
                    )
                )

    examples: list[dict[str, Any]] = []
    if include_examples and stage in ("generate", "repair"):
        from apps.knowledge.retrieval.example_provider import recall_examples

        raw_examples = recall_examples(
            session,
            question=question,
            oid=oid,
            ds_id=ds_id,
            advanced_application_id=advanced_application_id,
            training_type=training_type,
        )
        limit = (
            budgets.repair_hints if stage == "repair" else budgets.generate_examples
        )
        for idx, example in enumerate(raw_examples):
            if idx >= limit:
                apply_log.append(
                    ApplyHit(
                        asset_kind="example",
                        asset_id=example.get("id"),
                        trust_tier=example.get("trust_tier"),
                        apply="drop",
                        reason=f"{stage}_example_budget",
                    )
                )
                continue
            examples.append(example)
            apply_log.append(
                ApplyHit(
                    asset_kind="example",
                    asset_id=example.get("id"),
                    lineage_id=(example.get("knowledge_meta") or {}).get("lineage_id"),
                    trust_tier=example.get("trust_tier") or "published",
                    apply="exemplify",
                    reason="training_example",
                )
            )

    clarify_hints: list[str] = []
    if has_confirmed_joins:
        clarify_hints.append(
            "Confirmed joins exist for this datasource; prefer asking about "
            "population/filters over how tables connect."
        )

    return CompiledKnowledge(
        stage=stage,
        prompt_template=base.prompt_template,
        log_items=base.log_items,
        matches=base.matches,
        bound_calibers=bound_calibers,
        constraint_cards=constraint_cards,
        examples=examples,
        clarify_hints=clarify_hints,
        structural_ref={"channel": "catalog_prompt", "ds_id": ds_id},
        apply_log=apply_log,
    )
