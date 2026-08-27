"""Compile active semantic knowledge into the sole Query Agent knowledge bundle."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Literal

from sqlmodel import Session, col, select

from apps.knowledge.compile.bundle import ApplyHit, BusinessDataBundle, CompileStage
from apps.knowledge.db_models import (
    KnowledgeBinding,
    KnowledgeDeployment,
    KnowledgeUnit,
    KnowledgeUnitRevision,
)
from apps.knowledge.models import KnowledgeBundle
from apps.knowledge.policy import KnowledgePolicy, get_knowledge_policy
from apps.knowledge.providers import DictionaryProvider
from apps.knowledge.semantic.schema import KnowledgeUnitEntry
from apps.knowledge.service import recall_knowledge
from apps.terminology.curd.terminology import select_terminology_by_word
from common.core.config import settings

SeedPolicy = Literal["none", "reuse", "fallback"]

_STATE_TOKENS = (
    "状态",
    "阶段",
    "审核",
    "通过",
    "失败",
    "成功",
    "待",
    "中",
    "完成",
    "提交",
    "建档",
    "生效",
    "驳回",
)

_UnitHit = tuple[
    KnowledgeUnit, KnowledgeUnitRevision, KnowledgeUnitEntry, dict[str, Any]
]


def _normalise(value: str) -> str:
    return "".join(value.casefold().split())


def _intersects(question: str, *values: str) -> bool:
    needle = _normalise(question)
    return any(
        (normalised := _normalise(value)) and normalised in needle
        for value in values
        if value
    )


def _relevance(question: str, entry: KnowledgeUnitEntry) -> int:
    names = [entry.title, *entry.aliases]
    names.extend(item.name for item in entry.content.concepts)
    names.extend(alias for item in entry.content.concepts for alias in item.aliases)
    return sum(
        1
        for name in names
        if (normalised := _normalise(name)) and normalised in _normalise(question)
    )


def unit_seed_policy(relation: str) -> SeedPolicy:
    """Turn relation → how referenced revisions seed this compile."""
    if relation == "revise":
        return "reuse"
    if relation == "continue":
        return "fallback"
    return "none"


def matched_revision_ids(knowledge: Mapping[str, Any] | None) -> list[int]:
    ids: list[int] = []
    for item in (knowledge or {}).get("matched_units") or []:
        if not isinstance(item, dict):
            continue
        raw = item.get("revision_id")
        try:
            revision_id = int(raw)
        except (TypeError, ValueError):
            continue
        if revision_id > 0 and revision_id not in ids:
            ids.append(revision_id)
    return ids


def seed_revisions_for_turn(
    relation: str,
    referenced_turns: Sequence[Mapping[str, Any]] | None = None,
) -> tuple[list[int], SeedPolicy]:
    policy = unit_seed_policy(relation)
    if policy == "none":
        return [], policy
    ids: list[int] = []
    for turn in referenced_turns or []:
        for raw in turn.get("revision_ids") or []:
            try:
                revision_id = int(raw)
            except (TypeError, ValueError):
                continue
            if revision_id > 0 and revision_id not in ids:
                ids.append(revision_id)
    return ids, policy


def _mapping_table_names(
    mapping: Mapping[str, Any],
    entry: KnowledgeUnitEntry,
) -> list[str]:
    names: list[str] = []
    datasets = (
        mapping.get("datasets") if isinstance(mapping.get("datasets"), dict) else {}
    )
    for dataset in entry.content.datasets:
        mapped = (
            datasets.get(dataset.dataset_id) if isinstance(datasets, dict) else None
        )
        name = ""
        if isinstance(mapped, dict):
            name = str(mapped.get("table_name") or "").strip()
        if not name:
            name = dataset.name.strip()
        if name and name not in names:
            names.append(name)
    return names


def _semantic_unit_matches(
    session: Session,
    *,
    question: str,
    oid: int,
    datasource_id: int | None,
) -> dict[int, float]:
    """Resolve terminology hits to their active unit revisions."""
    terms = select_terminology_by_word(
        session,
        question,
        oid,
        datasource_id,
    )
    matches: dict[int, float] = {}
    for term in terms:
        meta = term.get("knowledge_meta")
        if not isinstance(meta, dict):
            continue
        revision_id = meta.get("unit_revision_id")
        if not isinstance(revision_id, int):
            continue
        matches[revision_id] = max(
            matches.get(revision_id, 0.0),
            float(term.get("score") or 0.0),
        )
    return matches


def active_published_units(
    session: Session,
    *,
    oid: int,
    datasource_id: int,
) -> list[tuple[KnowledgeUnit, KnowledgeUnitRevision]]:
    """All active published units bound to one datasource (identity rows).

    Shared read model for consumers that need the unit inventory rather than
    the expansion pipeline: the planner knowledge map and the recall-top-up
    knowledge index. Deployment must be ACTIVE and the binding BOUND/STALE —
    the same lifecycle fence ``_active_units`` applies.
    """
    statement = (
        select(KnowledgeUnit, KnowledgeUnitRevision)
        .join(
            KnowledgeUnitRevision,
            KnowledgeUnitRevision.id == KnowledgeUnit.active_revision_id,
        )
        .join(
            KnowledgeDeployment,
            KnowledgeDeployment.revision_id == KnowledgeUnitRevision.id,
        )
        .join(KnowledgeBinding, KnowledgeBinding.id == KnowledgeDeployment.binding_id)
        .where(
            KnowledgeUnit.oid == oid,
            KnowledgeUnitRevision.lifecycle_status == "PUBLISHED",
            KnowledgeDeployment.status == "ACTIVE",
            col(KnowledgeBinding.status).in_(["BOUND", "STALE"]),
            KnowledgeBinding.datasource_id == datasource_id,
        )
    )
    return list(session.exec(statement).all())


def _active_units(
    session: Session,
    *,
    oid: int,
    datasource_id: int | None,
    question: str,
    semantic_matches: dict[int, float] | None = None,
    seed_revision_ids: Sequence[int] = (),
    seed_policy: SeedPolicy = "none",
    limit: int = 2,
    extra_revision_ids: Sequence[int] = (),
) -> list[_UnitHit]:
    statement = (
        select(
            KnowledgeUnit, KnowledgeUnitRevision, KnowledgeDeployment, KnowledgeBinding
        )
        .join(
            KnowledgeUnitRevision,
            KnowledgeUnitRevision.id == KnowledgeUnit.active_revision_id,
        )
        .join(
            KnowledgeDeployment,
            KnowledgeDeployment.revision_id == KnowledgeUnitRevision.id,
        )
        .join(KnowledgeBinding, KnowledgeBinding.id == KnowledgeDeployment.binding_id)
        .where(
            KnowledgeUnit.oid == oid,
            KnowledgeUnitRevision.lifecycle_status == "PUBLISHED",
            KnowledgeDeployment.status == "ACTIVE",
            col(KnowledgeBinding.status).in_(["BOUND", "STALE"]),
        )
    )
    if datasource_id is not None:
        statement = statement.where(KnowledgeBinding.datasource_id == datasource_id)
    semantic_matches = semantic_matches or {}
    catalog: dict[int, _UnitHit] = {}
    ranked: list[tuple[tuple[int, float, str], _UnitHit]] = []
    for unit, revision, _deployment, binding in session.exec(statement).all():
        entry = KnowledgeUnitEntry.model_validate(revision.content)
        mapping = dict(binding.mapping or {})
        revision_id = int(revision.id or 0)
        hit: _UnitHit = (unit, revision, entry, mapping)
        if revision_id > 0:
            catalog[revision_id] = hit
        exact = _relevance(question, entry)
        semantic = semantic_matches.get(revision_id, 0.0)
        if exact == 0 and semantic == 0.0:
            continue
        ranked.append(((exact, semantic, unit.unit_key), hit))
    ranked.sort(key=lambda item: (-item[0][0], -item[0][1], item[0][2]))
    question_hits = [hit for _score, hit in ranked[:limit]]

    def from_seeds() -> list[_UnitHit]:
        selected: list[_UnitHit] = []
        for raw in seed_revision_ids:
            try:
                revision_id = int(raw)
            except (TypeError, ValueError):
                continue
            hit = catalog.get(revision_id)
            if hit is None or hit in selected:
                continue
            selected.append(hit)
            if len(selected) >= limit:
                break
        return selected

    if seed_policy == "reuse":
        seeded = from_seeds()
        if seeded:
            selected = seeded
        elif question_hits:
            selected = question_hits
        else:
            selected = from_seeds()
    elif question_hits:
        selected = question_hits
    elif seed_policy in {"reuse", "fallback"}:
        selected = from_seeds()
    else:
        selected = []
    # Evidence-driven top-up: one extra unit beyond the limit, only when the
    # planner/gate named it (e.g. a missing caliber concept).
    for raw in extra_revision_ids:
        try:
            revision_id = int(raw)
        except (TypeError, ValueError):
            continue
        hit = catalog.get(revision_id)
        if hit is not None and hit not in selected and len(selected) <= limit:
            selected.append(hit)
            break
    return selected


def _include_process(question: str, entry: KnowledgeUnitEntry) -> bool:
    if any(token in question for token in _STATE_TOKENS):
        return True
    return any(
        _intersects(question, process.name, process.stage_id, process.description)
        for process in entry.content.processes
    )


def _enrich_node_bundle(
    session: Session,
    bundle: BusinessDataBundle,
    result: Any,
    *,
    question: str,
) -> BusinessDataBundle:
    """Fill unit-level slots that node-plane closure does not carry.

    The pinned deployment snapshot holds the full entry view, so unit metadata,
    assumptions, conflicts and processes come from it directly instead of a
    second join to KnowledgeUnit/Revision. ``bound_resources`` comes from the
    reached dataset nodes' physical names (the same projection the unit path
    derives from its binding mapping).
    """
    from apps.knowledge.graph.models import CompositionDeployment

    deployment_ids = {
        int(row.deployment_id or 0)
        for node_id in result.reached
        if (row := result.index_by_node.get(node_id)) is not None and row.deployment_id
    }
    seen_units: set[str] = set()
    if deployment_ids:
        rows = session.exec(
            select(CompositionDeployment).where(
                col(CompositionDeployment.id).in_(deployment_ids)
            )
        ).all()
        for deployment in rows:
            snapshot = dict(deployment.pinned_snapshot or {})
            entry = snapshot.get("entry") or {}
            meta = snapshot.get("meta") or {}
            unit_key = str(meta.get("unit_key") or entry.get("unit_key") or "")
            if not unit_key or unit_key in seen_units:
                continue
            seen_units.add(unit_key)
            bundle.matched_units.append(
                {
                    "unit_key": unit_key,
                    "title": entry.get("title") or "",
                    "domain": entry.get("domain") or "",
                    "description": entry.get("description") or "",
                    "applicability": entry.get("applicability") or "",
                    "confidence": entry.get("confidence"),
                }
            )
            bundle.assumptions.extend(entry.get("assumptions") or [])
            bundle.ambiguities.extend(entry.get("conflicts") or [])
            entry_obj: KnowledgeUnitEntry | None = None
            if entry:
                try:
                    entry_obj = KnowledgeUnitEntry.model_validate(entry)
                except Exception:  # noqa: BLE001 - malformed snapshot degrades
                    entry_obj = None
            if entry_obj is not None and _include_process(question, entry_obj):
                bundle.scenarios.extend(
                    item.model_dump(mode="json") for item in entry_obj.content.processes
                )
                bundle.data_effects.extend(
                    {**effect.model_dump(mode="json"), "stage_id": process.stage_id}
                    for process in entry_obj.content.processes
                    for effect in process.data_effects
                )
    # Physical table projection from the reached dataset nodes.
    bound: list[str] = []
    for node_id in result.reached:
        row = result.index_by_node.get(node_id)
        if row is None or row.node_kind != "dataset":
            continue
        name = str((dict(row.content or {})).get("name") or "").strip()
        if name and name not in bound:
            bound.append(name)
    bundle.bound_resources = bound
    return bundle


def _compile_node_strategy(
    session: Session,
    *,
    stage: CompileStage,
    question: str,
    oid: int,
    ds_id: int,
    include_matches: bool,
    policy: KnowledgePolicy,
) -> BusinessDataBundle:
    """v3.1 node-plane recall: hybrid seeds + bounded closure + delta slice."""
    from apps.knowledge.graph.recall import assemble_node_bundle, recall_nodes

    matches: list[Any] = []
    if include_matches:
        base = recall_knowledge(
            session,
            question=question,
            oid=oid,
            ds_id=ds_id,
            providers=(DictionaryProvider(),),
        )
        matches = list(base.matches)
    try:
        result = recall_nodes(
            session,
            question=question,
            oid=oid,
            datasource_id=ds_id,
            embedding_enabled=settings.EMBEDDING_ENABLED,
        )
    except Exception as exc:  # noqa: BLE001 - degrade to schema-only, never block
        from common.utils.utils import SQLBotLogUtil

        SQLBotLogUtil.warning(f"node-plane recall unavailable: {type(exc).__name__}")
        return BusinessDataBundle(stage=stage, matches=matches)
    bundle = assemble_node_bundle(result, stage=stage, matches=matches)
    _enrich_node_bundle(session, bundle, result, question=question)
    # Verified query patterns become certified exemplars and gain a real
    # similarity score (fixing the VQR short-circuit that could never fire).
    for example in bundle.verified_examples:
        example["trust_tier"] = "certified"
        example["similarity"] = _exemplar_similarity(
            question, str(example.get("question") or "")
        )
    if stage == "generate" and bundle.verified_examples:
        from apps.knowledge.reuse import try_reuse

        reuse = try_reuse(
            question=question,
            examples=bundle.verified_examples,
            policy=policy,
        )
        if reuse is not None:
            bundle.reuse = reuse.model_dump(mode="json")
    # Dictionary entity bindings keep their own apply_log semantics.
    dictionary_log = [
        ApplyHit(
            asset_kind="dictionary",
            apply="bind",
            trust_tier="trusted",
            reason="published_dictionary_binding",
            meta={"query": match.query, "canonical": match.canonical},
        )
        for match in matches
        if "entity_binding" in match.usages
    ]
    bundle.apply_log = dictionary_log + list(bundle.apply_log)
    bundle.structural_ref = {"channel": "node_closure", "ds_id": ds_id}
    return bundle


def _exemplar_similarity(question: str, exemplar_question: str) -> float:
    """Cosine similarity between the user question and an exemplar question.

    Returns 0.0 when embeddings are disabled or unavailable so VQR degrades
    to normal generation instead of firing on a fabricated score.
    """
    if not exemplar_question.strip() or not settings.EMBEDDING_ENABLED:
        return 0.0
    try:
        from apps.ai_model.embedding import EmbeddingModelCache

        query_vec = EmbeddingModelCache.embed_query(question)
        exemplar_vec = EmbeddingModelCache.embed_query(exemplar_question)
    except Exception:  # noqa: BLE001 - lexical/exact channels still cover
        return 0.0
    if not query_vec or not exemplar_vec or len(query_vec) != len(exemplar_vec):
        return 0.0
    dot = sum(a * b for a, b in zip(query_vec, exemplar_vec, strict=False))
    norm_a = sum(a * a for a in query_vec) ** 0.5
    norm_b = sum(b * b for b in exemplar_vec) ** 0.5
    if not norm_a or not norm_b:
        return 0.0
    return dot / (norm_a * norm_b)


def compile_business_data_bundle(
    session: Session,
    *,
    stage: CompileStage,
    question: str,
    oid: int,
    ds_id: int | None,
    policy: KnowledgePolicy | dict[str, Any] | None = None,
    include_matches: bool = True,
    include_examples: bool = False,
    seed_revision_ids: Sequence[int] = (),
    seed_policy: SeedPolicy = "none",
    extra_revision_ids: Sequence[int] = (),
) -> BusinessDataBundle:
    """Expand at most two active units (plus one evidence-driven top-up).

    ``extra_revision_ids`` lets the plan gate add a single unit beyond the
    limit when the planner named a missing concept that maps to it. Draft and
    staging knowledge never enters NLQ.
    Once a unit is selected, datasets/fields/relationships/calibers/metrics/rules
    are floor slots. Processes follow the question; verified examples stay
    mapping-gated and capped.
    """
    resolved = (
        policy if isinstance(policy, KnowledgePolicy) else get_knowledge_policy(policy)
    )
    if (
        getattr(settings, "KNOWLEDGE_RECALL_STRATEGY", "unit") == "node"
        and ds_id is not None
    ):
        return _compile_node_strategy(
            session,
            stage=stage,
            question=question,
            oid=oid,
            ds_id=ds_id,
            include_matches=include_matches,
            policy=resolved,
        )
    base = (
        recall_knowledge(
            session,
            question=question,
            oid=oid,
            ds_id=ds_id,
            providers=(DictionaryProvider(),),
        )
        if include_matches
        else KnowledgeBundle()
    )
    apply_log = [
        ApplyHit(
            asset_kind="dictionary",
            apply="bind",
            trust_tier="trusted",
            reason="published_dictionary_binding",
            meta={"query": match.query, "canonical": match.canonical},
        )
        for match in base.matches
        if "entity_binding" in match.usages
    ]
    bundle = BusinessDataBundle(
        stage=stage,
        matches=base.matches,
        log_items=base.log_items,
        apply_log=apply_log,
        structural_ref={"channel": "active_knowledge_units", "ds_id": ds_id},
    )
    semantic_matches = _semantic_unit_matches(
        session,
        question=question,
        oid=oid,
        datasource_id=ds_id,
    )
    seen_datasets: set[str] = set()
    seen_fields: set[str] = set()
    seen_calibers: set[str] = set()
    bound_resources: list[str] = []
    for unit, revision, entry, mapping in _active_units(
        session,
        oid=oid,
        datasource_id=ds_id,
        question=question,
        semantic_matches=semantic_matches,
        seed_revision_ids=seed_revision_ids,
        seed_policy=seed_policy,
        extra_revision_ids=extra_revision_ids,
    ):
        revision_id = int(revision.id or 0)
        bundle.matched_units.append(
            {
                "unit_id": int(unit.id or 0),
                "unit_key": unit.unit_key,
                "revision_id": revision_id,
                "revision": revision.revision,
                "title": entry.title,
                "domain": entry.domain,
                "description": entry.description,
                "applicability": entry.applicability,
                "confidence": entry.confidence,
            }
        )
        for table_name in _mapping_table_names(mapping, entry):
            if table_name not in bound_resources:
                bound_resources.append(table_name)
        bundle.concepts.extend(
            item.model_dump(mode="json") for item in entry.content.concepts
        )
        if _include_process(question, entry):
            bundle.scenarios.extend(
                item.model_dump(mode="json") for item in entry.content.processes
            )
            for process in entry.content.processes:
                bundle.data_effects.extend(
                    {
                        **effect.model_dump(mode="json"),
                        "stage_id": process.stage_id,
                        "unit_revision_id": revision_id,
                    }
                    for effect in process.data_effects
                )
        for dataset in entry.content.datasets:
            if dataset.dataset_id not in seen_datasets:
                seen_datasets.add(dataset.dataset_id)
                bundle.datasets.append(dataset.model_dump(mode="json"))
            for field in dataset.fields:
                field_key = f"{dataset.dataset_id}.{field.field_id}"
                if field_key in seen_fields:
                    continue
                seen_fields.add(field_key)
                bundle.fields.append(
                    {**field.model_dump(mode="json"), "dataset_id": dataset.dataset_id}
                )
        bundle.relationships.extend(
            item.model_dump(mode="json") for item in entry.content.relationships
        )
        bundle.metrics.extend(
            item.model_dump(mode="json") for item in entry.content.metrics
        )
        for caliber in entry.content.calibers:
            if caliber.caliber_id in seen_calibers:
                continue
            seen_calibers.add(caliber.caliber_id)
            bundle.calibers.append(caliber.model_dump(mode="json"))
        bundle.rules.extend(
            item.model_dump(mode="json") for item in entry.content.domain_rules
        )
        if include_examples or stage == "generate":
            passed = mapping.get("verified_query_patterns") or {}
            selected = [
                item
                for item in entry.content.verified_query_patterns
                if isinstance(passed.get(item.pattern_id), dict)
                and passed[item.pattern_id].get("passed")
            ][:2]
            bundle.verified_examples.extend(
                {
                    "id": item.pattern_id,
                    "question": item.question,
                    "sql": item.query,
                    # selected 仅含 bind 时对目标库实际执行通过（passed:true）的
                    # 范例，属执行验证后的 certified；try_reuse 要求 certified 才
                    # 允许短路复用，二者必须一致，否则 VQR 复用永远命中不了。
                    "trust_tier": "certified",
                    "knowledge_meta": {"unit_revision_id": revision_id},
                }
                for item in selected
            )
        bundle.assumptions.extend(entry.assumptions)
        bundle.ambiguities.extend(entry.conflicts)
        bundle.apply_log.append(
            ApplyHit(
                asset_kind="knowledge_unit",
                asset_id=revision_id,
                lineage_id=unit.unit_key,
                trust_tier="published",
                apply="constrain",
                reason="active_unit_expanded",
            )
        )
    bundle.bound_resources = bound_resources
    if stage == "generate" and bundle.verified_examples and ds_id is not None:
        from apps.knowledge.reuse import try_reuse

        reuse = try_reuse(
            question=question, examples=bundle.verified_examples, policy=resolved
        )
        if reuse is not None:
            bundle.reuse = reuse.model_dump(mode="json")
    return bundle


def knowledge_prompt_payload(bundle: BusinessDataBundle) -> dict[str, Any]:
    """Compact Query Agent knowledge slots. Keys match the prompt contract.

    Field entries collapse to a single representation (name + dataset_id +
    description + dictionary). Datasets carry no nested fields and no server-
    side evidence ids: the schema block already supplies column structure, so
    knowledge keeps only the semantic delta over raw schema.
    """
    payload: dict[str, Any] = {}

    _SERVER_KEYS = {"evidence_refs", "unit_revision_id"}

    def _no_refs(items: list[Any]) -> list[dict[str, Any]]:
        return [
            {k: v for k, v in item.items() if k not in _SERVER_KEYS}
            for item in items
            if isinstance(item, dict)
        ]

    def _process(item: Any) -> dict[str, Any]:
        # data_effects are flattened into their own slot with a stage_id link,
        # so the nested copy is dropped here (avoids double-serializing them).
        data = item if isinstance(item, dict) else {}
        return {
            k: v
            for k, v in data.items()
            if k not in _SERVER_KEYS and k != "data_effects"
        }

    def _field(item: Any) -> dict[str, Any] | None:
        data = item if isinstance(item, dict) else {}
        if not data.get("name"):
            return None
        out: dict[str, Any] = {"name": data["name"]}
        if data.get("dataset_id"):
            out["dataset_id"] = data["dataset_id"]
        if data.get("description"):
            out["description"] = data["description"]
        dictionary = data.get("dictionary")
        if isinstance(dictionary, dict) and dictionary:
            out["dictionary"] = dictionary
        return out

    def _dataset(item: Any) -> dict[str, Any]:
        data = item if isinstance(item, dict) else {}
        return {
            key: data[key]
            for key in ("name", "dataset_id", "database", "description")
            if data.get(key)
        }

    def _unit(item: Any) -> dict[str, Any]:
        data = item if isinstance(item, dict) else {}
        out: dict[str, Any] = {
            key: data[key]
            for key in ("unit_key", "title", "domain", "description", "applicability")
            if data.get(key)
        }
        if data.get("confidence") is not None:
            out["confidence"] = data["confidence"]
        return out

    def _example(item: Any) -> dict[str, Any]:
        data = item if isinstance(item, dict) else {}
        out: dict[str, Any] = {}
        sql = data.get("sql") or data.get("query")
        if sql:
            out["sql"] = sql
        for key in ("id", "question", "trust_tier"):
            if data.get(key):
                out[key] = data[key]
        return out

    if bundle.matched_units:
        payload["matched_units"] = [_unit(item) for item in bundle.matched_units]
    if bundle.concepts:
        payload["concepts"] = _no_refs(bundle.concepts)
    if bundle.scenarios:
        payload["processes"] = [_process(item) for item in bundle.scenarios]
    if bundle.data_effects:
        payload["data_effects"] = _no_refs(bundle.data_effects)
    if bundle.datasets:
        payload["datasets"] = [_dataset(item) for item in bundle.datasets]
    if bundle.fields:
        compact = [_field(item) for item in bundle.fields]
        payload["fields"] = [item for item in compact if item is not None]
    if bundle.relationships:
        payload["relationships"] = _no_refs(bundle.relationships)
    if bundle.metrics:
        payload["metrics"] = _no_refs(bundle.metrics)
    if bundle.calibers:
        payload["calibers"] = _no_refs(bundle.calibers)
    if bundle.rules:
        payload["rules"] = _no_refs(bundle.rules)
    if bundle.verified_examples:
        payload["verified_examples"] = [
            _example(item) for item in bundle.verified_examples
        ]
    if bundle.ambiguities:
        payload["conflicts"] = _no_refs(bundle.ambiguities)
    if bundle.assumptions:
        payload["assumptions"] = bundle.assumptions
    if bundle.reuse:
        payload["reuse"] = bundle.reuse
    return payload
