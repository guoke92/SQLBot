"""Knowledge Compile — sole apply gate for NLQ knowledge."""

from __future__ import annotations

from typing import Any

from sqlalchemy import or_
from sqlmodel import Session, select

from apps.knowledge.compile.bundle import (
    ApplyHit,
    BoundCaliber,
    CompiledKnowledge,
    CompileStage,
)
from apps.knowledge.db_models import KnowledgeAsset
from apps.knowledge.models import KnowledgeBundle
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
    include_matches: bool = True,
    include_calibers: bool = True,
    include_examples: bool = False,
    training_type: str | None = None,
) -> CompiledKnowledge:
    """Assemble a CompiledKnowledge for the given NLQ stage.

    Phase A: Term + Dict via recall_knowledge (behavior-preserving).
    Phase B+: strongly applicable certified Caliber candidates. The semantic
    planner records Bind only after the final specification absorbs them.
    Phase C+: examples + budgets.

    ``include_matches=False`` skips the Term/Dict recall (with its embedding
    lookups) for callers that already compiled it earlier in the same turn.
    """
    resolved = (
        policy if isinstance(policy, KnowledgePolicy) else get_knowledge_policy(policy)
    )
    budgets = resolved.compile_budgets

    if include_matches:
        base = recall_knowledge(
            session,
            question=question,
            oid=oid,
            ds_id=ds_id,
            advanced_application_id=advanced_application_id,
        )
    else:
        base = KnowledgeBundle()
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
    constraints: list[dict[str, Any]] = []
    if include_calibers and ds_id is not None and advanced_application_id is None:
        from apps.knowledge.retrieval.caliber_provider import (
            recall_bindable_calibers,
            recall_staging_calibers,
        )

        candidates = recall_bindable_calibers(
            session,
            oid=oid,
            ds_id=ds_id,
            question=question,
        )
        for item in candidates:
            if item.apply == "bind" and item.bound is not None:
                bound_calibers.append(item.bound)
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
        for item in recall_staging_calibers(session, oid=oid, ds_id=ds_id):
            label = item.label or ""
            content = item.summary or label
            if label or content:
                constraints.append(
                    {
                        "id": item.staging_id,
                        "lineage_id": item.lineage_id,
                        "label": label,
                        "content": content,
                    }
                )
            apply_log.append(
                ApplyHit(
                    asset_kind="caliber",
                    asset_id=None,
                    lineage_id=item.lineage_id,
                    trust_tier=item.trust_tier,
                    apply="constrain",
                    reason="staging_caliber_hint",
                    meta={"staging_id": item.staging_id, "label": label},
                )
            )

    # ── K5 rules: workspace/datasource-scoped business constraints ──
    # Skipped alongside matches: the planner reads constraints from the
    # assess-stage compile; re-querying at generate would only duplicate hits.
    if include_matches:
        rule_stmt = (
            select(KnowledgeAsset)
            .where(KnowledgeAsset.kind == "rule")
            .where(KnowledgeAsset.enabled.is_(True))  # type: ignore[attr-defined]
            .where(KnowledgeAsset.valid_to.is_(None))  # type: ignore[attr-defined]
            .where(KnowledgeAsset.oid == oid)
            .where(
                KnowledgeAsset.trust_tier.in_(  # type: ignore[attr-defined]
                    ["published", "trusted", "certified"]
                )
            )
        )
        if ds_id is not None:
            rule_stmt = rule_stmt.where(
                or_(
                    KnowledgeAsset.datasource_id == ds_id,
                    KnowledgeAsset.datasource_id.is_(None),  # type: ignore[attr-defined]
                )
            )
        else:
            rule_stmt = rule_stmt.where(
                KnowledgeAsset.datasource_id.is_(None)  # type: ignore[attr-defined]
            )
        for rule in session.exec(rule_stmt).all():
            constraints.append(
                {
                    "id": rule.id,
                    "lineage_id": rule.lineage_id,
                    "label": rule.label,
                    "content": (rule.payload or {}).get("content", ""),
                }
            )
            apply_log.append(
                ApplyHit(
                    asset_kind="rule",
                    asset_id=rule.id,
                    lineage_id=rule.lineage_id,
                    trust_tier=rule.trust_tier,
                    apply="constrain",
                    reason="k5_rule",
                )
            )

    examples: list[dict[str, Any]] = []
    if include_examples and stage == "generate":
        from apps.knowledge.retrieval.example_provider import recall_examples

        raw_examples = recall_examples(
            session,
            question=question,
            oid=oid,
            ds_id=ds_id,
            advanced_application_id=advanced_application_id,
            training_type=training_type,
        )
        limit = budgets.generate_examples
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

    # ── K4 VQR: attempt reuse from certified exemplars ──
    reuse_payload: dict[str, Any] | None = None
    if stage == "generate" and examples and ds_id is not None:
        from apps.knowledge.reuse import try_reuse

        reuse_result = try_reuse(
            question=question,
            examples=examples,
            policy=resolved,
        )
        if reuse_result is not None:
            reuse_payload = reuse_result.model_dump(mode="json")
            # Compile discovers a candidate only. Reuse becomes an applied fact
            # after the shared plan validator accepts it.

    return CompiledKnowledge(
        stage=stage,
        prompt_template=base.prompt_template,
        log_items=base.log_items,
        matches=base.matches,
        bound_calibers=bound_calibers,
        examples=examples,
        constraints=constraints,
        structural_ref={"channel": "catalog_prompt", "ds_id": ds_id},
        reuse=reuse_payload,
        apply_log=apply_log,
    )
