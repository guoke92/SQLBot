"""Decompose a KnowledgePackage 2.0 into layered nodes, typed edges and unit compositions.

Three layers, per ADR v3.1:

* **plan_decomposition** - pure function: package -> node/edge/composition
  drafts. No DB, fully testable, deterministic ordering.
* **assemble_entry** - pure function: plan + composition draft -> the
  KnowledgeUnitEntry-shaped snapshot. One code path shared by round-trip
  fidelity checks (P1), the review view (P2) and publish pinning (P2).
* **persist_plan / decompose_package** - idempotent session persistence
  with M2 merge conflicts queued, never silently merged.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from hashlib import sha256
from typing import Any

from sqlmodel import Session, col, select

from apps.knowledge.graph.identity import (
    concept_key,
    dataset_key,
    field_key,
    norm,
    stage_key,
    unit_key_for,
    unit_scoped_key,
)
from apps.knowledge.graph.models import (
    KnowledgeEdge,
    KnowledgeMergeConflict,
    KnowledgeNode,
    KnowledgeNodeVersion,
    UnitComposition,
)
from apps.knowledge.graph.node_kinds import BUCKET_ID_FIELDS
from apps.knowledge.semantic.schema import KnowledgePackageV2

logger = logging.getLogger(__name__)

EDGE_KINDS = (
    "has_field",
    "concept_of",
    "references_field",
    "reads",
    "writes",
    "relation_endpoint",
    "precedes",
    "validates",
    "exemplar_scope",
)

_WRITE_OPERATIONS = {"insert", "update", "delete", "upsert"}


def _is_join_relationship(relationship_type: str | None) -> bool:
    """True when a relationship is an executable JOIN (not a shared-key hint).

    SHARED_KEY (n:n / shared key / transitive) relationships are scope hints,
    not joins: they must not emit a relation_endpoint edge, or recall would
    synthesize a JOIN between tables that should each join their own primary.
    """
    rel_type = (relationship_type or "").strip().upper()
    return rel_type in ("", "EQUI_JOIN")


def _json_hash(value: Any) -> str:
    blob = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
    return sha256(blob.encode("utf-8")).hexdigest()


def node_content_hash(node_kind: str, natural_key: str, payload: dict[str, Any]) -> str:
    """Single canonical content hash for a node version.

    The canonicalization (sort_keys=True, default separators) is fixed: changing
    it would invalidate every persisted content_hash and churn node versions.
    """
    return _json_hash({"kind": node_kind, "key": natural_key, "payload": payload})


def append_node_version(
    session: Session,
    *,
    node: KnowledgeNode,
    current: KnowledgeNodeVersion | None,
    payload: dict[str, Any],
    evidence_refs: list[Any],
    confidence: float | None,
    stub: bool | None,
    origin_package_id: int | None,
    now: datetime,
) -> tuple[KnowledgeNodeVersion, bool]:
    """Append a version to *node* iff content changed; returns (version, changed).

    The single writer for node truth: hash comparison, version increment,
    supersede back-pointer and current_version_id are defined exactly once here,
    shared by decompose (persist), governance (edit) and feedback (promote).
    """
    content_hash = node_content_hash(node.node_kind, node.natural_key, payload)
    if current is not None and current.content_hash == content_hash:
        return current, False
    version = KnowledgeNodeVersion(
        node_id=int(node.id or 0),
        version=(current.version + 1) if current is not None else 1,
        payload=payload,
        evidence_refs=list(evidence_refs),
        confidence=confidence if confidence is not None else 0.5,
        content_hash=content_hash,
        stub=stub if stub is not None else False,
        create_time=now,
    )
    if origin_package_id is not None:
        version.origin_package_id = origin_package_id
    session.add(version)
    session.flush()
    if current is not None:
        current.superseded_by = int(version.id or 0)
        session.add(current)
    node.current_version_id = int(version.id or 0)
    node.update_time = now
    session.add(node)
    return version, True


def _payload(model: Any, *, strip: tuple[str, ...]) -> dict[str, Any]:
    data = model.model_dump(mode="json")
    for key in strip:
        data.pop(key, None)
    return data


# --------------------------------------------------------------------------
# Drafts
# --------------------------------------------------------------------------


@dataclass
class NodeDraft:
    node_kind: str
    natural_key: str
    namespace: str
    payload: dict[str, Any]
    evidence_refs: list[str] = field(default_factory=list)
    confidence: float = 0.5
    stub: bool = False

    @property
    def content_hash(self) -> str:
        return node_content_hash(self.node_kind, self.natural_key, self.payload)


@dataclass
class EdgeDraft:
    src_key: str
    dst_key: str
    edge_kind: str
    status: str = "proposed"
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass
class FieldRefDraft:
    unit_field_id: str
    field_key: str


@dataclass
class DatasetRefDraft:
    unit_dataset_id: str
    dataset_key: str
    fields: list[FieldRefDraft] = field(default_factory=list)


@dataclass
class BucketNodeRef:
    local_id: str
    node_key: str


@dataclass
class CompositionDraft:
    unit_id: str
    unit_key: str
    domain: str
    title: str
    applicability: str
    description: str
    aliases: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    conflicts: list[dict[str, Any]] = field(default_factory=list)
    unit_links: list[dict[str, Any]] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    confidence: float = 0.5
    dataset_refs: list[DatasetRefDraft] = field(default_factory=list)
    bucket_nodes: dict[str, list[BucketNodeRef]] = field(default_factory=dict)
    relationships: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class DecompositionPlan:
    nodes: dict[str, NodeDraft] = field(default_factory=dict)
    edges: list[EdgeDraft] = field(default_factory=list)
    compositions: list[CompositionDraft] = field(default_factory=list)
    merge_conflicts: list[dict[str, Any]] = field(default_factory=list)
    enrichments: list[dict[str, Any]] = field(default_factory=list)
    stats: dict[str, Any] = field(default_factory=dict)


# --------------------------------------------------------------------------
# Pure planning
# --------------------------------------------------------------------------


class _PlanBuilder:
    def __init__(self, package: KnowledgePackageV2) -> None:
        self.package = package
        self.namespace = package.package.namespace
        self.plan = DecompositionPlan()
        self._edge_keys: set[tuple[str, str, str]] = set()
        self.enrichments = 0
        self._dataset_declarations: dict[str, int] = {}
        self._dataset_by_table: dict[str, str] = {}
        self.units_by_id: dict[str, Any] = {
            unit.unit_id: unit for unit in package.knowledge_units
        }

    # -- node/edge helpers -------------------------------------------------

    def add_node(self, draft: NodeDraft) -> None:
        existing = self.plan.nodes.get(draft.natural_key)
        if existing is None:
            self.plan.nodes[draft.natural_key] = draft
            return
        if existing.content_hash == draft.content_hash:
            return
        if self._same_semantics(existing, draft):
            # Same meaning, only provenance (evidence_refs) differs across
            # units - each unit legitimately cites the evidence it used.
            # Keep the newest claim, no conflict.
            self.plan.nodes[draft.natural_key] = draft
            return
        if self._enriches(existing, draft):
            # A strictly richer dictionary claim (same shared values, more
            # keys) enriches the shared truth instead of conflicting.
            self.plan.nodes[draft.natural_key] = draft
            self.enrichments += 1
            self.plan.enrichments.append(
                {
                    "node_key": draft.natural_key,
                    "node_kind": draft.node_kind,
                    "from_hash": existing.content_hash,
                    "to_hash": draft.content_hash,
                }
            )
            return
        self.plan.merge_conflicts.append(
            {
                "node_key": draft.natural_key,
                "node_kind": draft.node_kind,
                "kept_hash": existing.content_hash,
                "dropped_hash": draft.content_hash,
                "diff_keys": sorted(
                    {
                        key
                        for key in set(existing.payload) | set(draft.payload)
                        if key != "evidence_refs"
                        and existing.payload.get(key) != draft.payload.get(key)
                    }
                ),
                "reason": "intra-package payload divergence",
            }
        )

    def _same_semantics(self, kept: NodeDraft, incoming: NodeDraft) -> bool:
        def semantic(payload: dict[str, Any]) -> dict[str, Any]:
            return {
                key: value for key, value in payload.items() if key != "evidence_refs"
            }

        return semantic(kept.payload) == semantic(incoming.payload)

    def _enriches(self, kept: NodeDraft, incoming: NodeDraft) -> bool:
        kept_dict = kept.payload.get("dictionary") or {}
        new_dict = incoming.payload.get("dictionary") or {}
        if not isinstance(kept_dict, dict) or not isinstance(new_dict, dict):
            return False
        if not set(kept_dict) < set(new_dict):
            return False
        if any(kept_dict[key] != new_dict.get(key) for key in kept_dict):
            return False
        # Only the dictionary may grow; any other semantic divergence is a
        # real conflict (provenance excluded).
        other_keys = (set(kept.payload) | set(incoming.payload)) - {
            "dictionary",
            "evidence_refs",
        }
        return all(
            kept.payload.get(key) == incoming.payload.get(key) for key in other_keys
        )

    def add_edge(self, draft: EdgeDraft) -> None:
        marker = (draft.src_key, draft.dst_key, draft.edge_kind)
        if marker in self._edge_keys:
            return
        self._edge_keys.add(marker)
        self.plan.edges.append(draft)

    def declare_dataset(
        self,
        database: str,
        name: str,
        description: str,
        evidence: list[str],
        inactive: bool = False,
    ) -> str:
        table = norm(name)
        key = dataset_key(database, name)
        if not norm(database):
            # D6 alias rule: a bare-table declaration merges with the
            # db-qualified node when one already exists for that table.
            existing_key = self._dataset_by_table.get(table)
            if existing_key is not None:
                key = existing_key
        self._dataset_declarations[key] = self._dataset_declarations.get(key, 0) + 1
        self._dataset_by_table.setdefault(table, key)
        self.add_node(
            NodeDraft(
                node_kind="dataset",
                natural_key=key,
                namespace=self.namespace,
                payload={
                    "name": name,
                    "database": database,
                    "description": description,
                    "inactive": inactive,
                    "evidence_refs": list(evidence),
                },
                evidence_refs=list(evidence),
            )
        )
        return key

    def declare_field(self, dataset_natural_key: str, field_model: Any) -> str:
        key = field_key(dataset_natural_key, field_model.name)
        self.add_node(
            NodeDraft(
                node_kind="field",
                natural_key=key,
                namespace=self.namespace,
                payload=_payload(field_model, strip=("field_id",)),
                evidence_refs=list(field_model.evidence_refs),
            )
        )
        self.add_edge(
            EdgeDraft(
                src_key=dataset_natural_key,
                dst_key=key,
                edge_kind="has_field",
                status="confirmed",
            )
        )
        return key

    def stub_dataset(self, table: str) -> str:
        key = norm(table)
        if key not in self.plan.nodes:
            self.add_node(
                NodeDraft(
                    node_kind="dataset",
                    natural_key=key,
                    namespace=self.namespace,
                    payload={"name": table, "database": "", "description": ""},
                    stub=True,
                )
            )
        return key

    def stub_field(self, dataset_natural_key: str, field_name: str) -> str:
        key = field_key(dataset_natural_key, field_name)
        if key not in self.plan.nodes:
            self.add_node(
                NodeDraft(
                    node_kind="field",
                    natural_key=key,
                    namespace=self.namespace,
                    payload={"name": field_name},
                    stub=True,
                )
            )
            self.add_edge(
                EdgeDraft(
                    src_key=dataset_natural_key,
                    dst_key=key,
                    edge_kind="has_field",
                    status="confirmed",
                )
            )
        return key

    # -- unit decomposition -------------------------------------------------

    def build_unit(self, unit: Any) -> CompositionDraft:
        unit_key = unit_key_for(self.namespace, unit.unit_id)
        comp = CompositionDraft(
            unit_id=unit.unit_id,
            unit_key=unit_key,
            domain=unit.domain,
            title=unit.title,
            applicability=unit.applicability,
            description=unit.description,
            aliases=list(unit.aliases),
            assumptions=list(unit.assumptions),
            conflicts=[dict(item) for item in unit.conflicts],
            unit_links=[link.model_dump(mode="json") for link in unit.unit_links],
            evidence_refs=list(unit.evidence_refs),
            confidence=unit.confidence,
        )
        field_map: dict[tuple[str, str], str] = {}

        for dataset in unit.content.datasets:
            ds_key = self.declare_dataset(
                dataset.database,
                dataset.name,
                dataset.description,
                list(dataset.evidence_refs),
                inactive=dataset.inactive,
            )
            ref = DatasetRefDraft(
                unit_dataset_id=dataset.dataset_id, dataset_key=ds_key
            )
            for field_model in dataset.fields:
                f_key = self.declare_field(ds_key, field_model)
                ref.fields.append(
                    FieldRefDraft(unit_field_id=field_model.field_id, field_key=f_key)
                )
                field_map[(dataset.dataset_id, field_model.field_id)] = f_key
            comp.dataset_refs.append(ref)

        def resolve(ref: Any) -> str:
            key = field_map.get((ref.dataset, ref.field))
            if key is None:
                raise ValueError(
                    f"unresolvable field ref {ref.dataset}.{ref.field} in unit {unit.unit_id}"
                )
            return key

        for concept in unit.content.concepts:
            node_key = concept_key(self.namespace, concept.concept_id)
            self.add_node(
                NodeDraft(
                    node_kind="concept",
                    natural_key=node_key,
                    namespace=self.namespace,
                    payload=_payload(concept, strip=("concept_id",)),
                    evidence_refs=list(concept.evidence_refs),
                )
            )
            comp.bucket_nodes.setdefault("concepts", []).append(
                BucketNodeRef(local_id=concept.concept_id, node_key=node_key)
            )
            for target in concept.field_targets:
                self.add_edge(
                    EdgeDraft(
                        src_key=node_key,
                        dst_key=resolve(target),
                        edge_kind="concept_of",
                        status="confirmed",
                        evidence={"source": "concept_field_targets"},
                    )
                )

        stage_keys: dict[str, str] = {}
        for stage in unit.content.processes:
            node_key = stage_key(unit_key, stage.stage_id)
            stage_keys[stage.stage_id] = node_key
            self.add_node(
                NodeDraft(
                    node_kind="stage",
                    natural_key=node_key,
                    namespace=self.namespace,
                    payload=_payload(stage, strip=("stage_id",)),
                    evidence_refs=list(stage.evidence_refs),
                )
            )
            comp.bucket_nodes.setdefault("processes", []).append(
                BucketNodeRef(local_id=stage.stage_id, node_key=node_key)
            )
            for effect in stage.data_effects:
                edge_kind = (
                    "writes" if effect.operation in _WRITE_OPERATIONS else "reads"
                )
                for field_id in effect.fields:
                    target = field_map.get((effect.dataset, field_id))
                    if target is None:
                        continue
                    self.add_edge(
                        EdgeDraft(
                            src_key=node_key,
                            dst_key=target,
                            edge_kind=edge_kind,
                            status="confirmed",
                            evidence={"refs": list(effect.evidence_refs)},
                        )
                    )
        for stage in unit.content.processes:
            for next_stage in stage.next_stages:
                dst = stage_keys.get(next_stage)
                if dst is not None:
                    self.add_edge(
                        EdgeDraft(
                            src_key=stage_keys[stage.stage_id],
                            dst_key=dst,
                            edge_kind="precedes",
                            status="confirmed",
                        )
                    )

        for relationship in unit.content.relationships:
            comp.relationships.append(relationship.model_dump(mode="json"))
            if _is_join_relationship(relationship.relationship_type):
                self.add_edge(
                    EdgeDraft(
                        src_key=resolve(relationship.left),
                        dst_key=resolve(relationship.right),
                        edge_kind="relation_endpoint",
                        status=relationship.status,
                        evidence={"refs": list(relationship.evidence_refs)},
                    )
                )

        for caliber in unit.content.calibers:
            node_key = unit_scoped_key(unit_key, caliber.caliber_id)
            self._add_bucket_node(
                comp, "calibers", "caliber", caliber.caliber_id, node_key, caliber
            )
            for target in caliber.field_targets:
                self._reference_field(node_key, resolve(target))

        for rule in unit.content.domain_rules:
            node_key = unit_scoped_key(unit_key, rule.rule_id)
            self._add_bucket_node(
                comp, "domain_rules", "rule", rule.rule_id, node_key, rule
            )
            for target in rule.field_targets:
                self._reference_field(node_key, resolve(target))

        for metric in unit.content.metrics:
            node_key = unit_scoped_key(unit_key, metric.metric_id)
            self._add_bucket_node(
                comp, "metrics", "metric", metric.metric_id, node_key, metric
            )
            if metric.field is not None:
                self._reference_field(node_key, resolve(metric.field))
            for grain in metric.grain:
                self._reference_field(node_key, resolve(grain))

        for pattern in unit.content.verified_query_patterns:
            node_key = unit_scoped_key(unit_key, pattern.pattern_id)
            self._add_bucket_node(
                comp,
                "verified_query_patterns",
                "pattern",
                pattern.pattern_id,
                node_key,
                pattern,
            )

        self._build_unit_link_edges(unit, comp, field_map)
        return comp

    def _add_bucket_node(
        self,
        comp: CompositionDraft,
        bucket: str,
        node_kind: str,
        local_id: str,
        node_key: str,
        model: Any,
    ) -> None:
        self.add_node(
            NodeDraft(
                node_kind=node_kind,
                natural_key=node_key,
                namespace=self.namespace,
                payload=_payload(model, strip=(f"{node_kind}_id",)),
                evidence_refs=list(model.evidence_refs),
            )
        )
        comp.bucket_nodes.setdefault(bucket, []).append(
            BucketNodeRef(local_id=local_id, node_key=node_key)
        )

    def _reference_field(self, src_key: str, field_natural_key: str) -> None:
        self.add_edge(
            EdgeDraft(
                src_key=src_key,
                dst_key=field_natural_key,
                edge_kind="references_field",
                status="confirmed",
            )
        )

    def _build_unit_link_edges(
        self,
        unit: Any,
        comp: CompositionDraft,
        field_map: dict[tuple[str, str], str],
    ) -> None:
        """Derive cross-unit precedes/validates edges from unit_links.

        The declaring unit's stages that touch a via field connect to the
        target unit's stages that write the same field; evidence comes from
        the link's evidence_refs. Bounded by the small via set.
        """
        if not unit.unit_links:
            return
        unit_key = unit_key_for(self.namespace, unit.unit_id)
        for link in unit.unit_links:
            target_unit = self.units_by_id.get(link.target_unit)
            if target_unit is None:
                continue
            edge_kind = "precedes" if link.kind == "prerequisite" else "validates"
            via_keys = [field_map.get((ref.dataset, ref.field)) for ref in link.via]
            via_keys = [key for key in via_keys if key]
            if not via_keys:
                continue
            target_key = unit_key_for(self.namespace, target_unit.unit_id)
            for target_stage in target_unit.content.processes:
                target_stage_key = stage_key(target_key, target_stage.stage_id)
                writes_via = any(
                    effect.operation in _WRITE_OPERATIONS
                    and effect.dataset in {ref.dataset for ref in link.via}
                    for effect in target_stage.data_effects
                )
                if not writes_via:
                    continue
                for stage in unit.content.processes:
                    touches = any(
                        field_map.get((effect.dataset, field_id)) in via_keys
                        for effect in stage.data_effects
                        for field_id in effect.fields
                    )
                    if not touches:
                        continue
                    self.add_edge(
                        EdgeDraft(
                            src_key=stage_key(unit_key, stage.stage_id),
                            dst_key=target_stage_key,
                            edge_kind=edge_kind,
                            status="proposed",
                            evidence={
                                "refs": list(link.evidence_refs),
                                "unit_link": f"{link.kind}:{link.target_unit}",
                            },
                        )
                    )

    # -- package relationships ------------------------------------------------

    def build_package_relationships(self) -> None:
        for relationship in self.package.relationships:
            if not _is_join_relationship(relationship.relationship_type):
                # SHARED_KEY (and future non-join types) is a scope hint, not a
                # JOIN: retain it in package.relationships, emit no endpoint edge.
                continue
            left_ds = self._dataset_by_table.get(norm(relationship.left_table))
            if left_ds is None:
                left_ds = self.stub_dataset(relationship.left_table)
            right_ds = self._dataset_by_table.get(norm(relationship.right_table))
            if right_ds is None:
                right_ds = self.stub_dataset(relationship.right_table)
            left_field = self._ensure_field_node(left_ds, relationship.left_field)
            right_field = self._ensure_field_node(right_ds, relationship.right_field)
            self.add_edge(
                EdgeDraft(
                    src_key=left_field,
                    dst_key=right_field,
                    edge_kind="relation_endpoint",
                    status="proposed",
                    evidence={"source": relationship.evidence or "package"},
                )
            )

    def _ensure_field_node(self, dataset_natural_key: str, field_name: str) -> str:
        key = field_key(dataset_natural_key, field_name)
        if key not in self.plan.nodes:
            self.stub_field(dataset_natural_key, field_name)
        return key

    # -- stats ---------------------------------------------------------------

    def finalize(self) -> DecompositionPlan:
        kind_counts: dict[str, int] = {}
        for node in self.plan.nodes.values():
            kind_counts[node.node_kind] = kind_counts.get(node.node_kind, 0) + 1
        edge_counts: dict[str, int] = {}
        for edge in self.plan.edges:
            edge_counts[edge.edge_kind] = edge_counts.get(edge.edge_kind, 0) + 1
        self.plan.stats = {
            "units": len(self.plan.compositions),
            "node_count": len(self.plan.nodes),
            "nodes_by_kind": kind_counts,
            "edge_count": len(self.plan.edges),
            "edges_by_kind": edge_counts,
            "dataset_declarations": dict(self._dataset_declarations),
            "dataset_node_count": kind_counts.get("dataset", 0),
            "stub_nodes": sum(1 for node in self.plan.nodes.values() if node.stub),
            "merge_conflicts": len(self.plan.merge_conflicts),
            "enrichments": self.enrichments,
        }
        return self.plan


def plan_decomposition(package: KnowledgePackageV2) -> DecompositionPlan:
    """Pure package -> plan decomposition (deterministic, no DB)."""
    builder = _PlanBuilder(package)
    for unit in package.knowledge_units:
        builder.plan.compositions.append(builder.build_unit(unit))
    builder.build_package_relationships()
    return builder.finalize()


# --------------------------------------------------------------------------
# Pure assembly (round-trip / review view / publish snapshot)
# --------------------------------------------------------------------------


def assemble_entry(plan: DecompositionPlan, comp: CompositionDraft) -> dict[str, Any]:
    """Rebuild the KnowledgeUnitEntry-shaped dict from plan + composition."""
    content: dict[str, Any] = {
        "concepts": [],
        "processes": [],
        "datasets": [],
        "relationships": [],
        "metrics": [],
        "calibers": [],
        "domain_rules": [],
        "verified_query_patterns": [],
    }
    for dataset_ref in comp.dataset_refs:
        dataset_node = plan.nodes[dataset_ref.dataset_key]
        dataset_payload = dict(dataset_node.payload)
        dataset_payload["dataset_id"] = dataset_ref.unit_dataset_id
        dataset_payload["fields"] = []
        for field_ref in dataset_ref.fields:
            field_payload = dict(plan.nodes[field_ref.field_key].payload)
            field_payload["field_id"] = field_ref.unit_field_id
            dataset_payload["fields"].append(field_payload)
        content["datasets"].append(dataset_payload)
    for bucket, id_field in BUCKET_ID_FIELDS.items():
        for ref in comp.bucket_nodes.get(bucket, []):
            payload = dict(plan.nodes[ref.node_key].payload)
            payload[id_field] = ref.local_id
            content[bucket].append(payload)
    content["relationships"] = [dict(item) for item in comp.relationships]
    return {
        "unit_id": comp.unit_id,
        "title": comp.title,
        "aliases": list(comp.aliases),
        "domain": comp.domain,
        "applicability": comp.applicability,
        "description": comp.description,
        "content": content,
        "evidence_refs": list(comp.evidence_refs),
        "unit_links": [dict(link) for link in comp.unit_links],
        "assumptions": list(comp.assumptions),
        "conflicts": [dict(item) for item in comp.conflicts],
        "confidence": comp.confidence,
    }


def fidelity_hash(entry: dict[str, Any]) -> str:
    """Hash of an entry dict ignoring 'revision' (per-import bookkeeping)."""
    material = {key: value for key, value in entry.items() if key != "revision"}
    return _json_hash(material)


# --------------------------------------------------------------------------
# Persistence (idempotent, M2 conflicts queued)
# --------------------------------------------------------------------------


@dataclass
class PersistReport:
    created_nodes: int = 0
    updated_nodes: int = 0
    unchanged_nodes: int = 0
    created_edges: int = 0
    updated_edges: int = 0
    upserted_compositions: int = 0
    conflicts_queued: int = 0


def persist_plan(
    session: Session,
    *,
    oid: int,
    plan: DecompositionPlan,
    package_row_id: int | None,
) -> PersistReport:
    """Idempotently persist a plan; divergent claims queue as conflicts."""
    report = PersistReport()
    now = datetime.utcnow()
    node_ids: dict[str, int] = {}

    existing_nodes = {
        (row.node_kind, row.natural_key): row
        for row in session.exec(
            select(KnowledgeNode).where(KnowledgeNode.oid == oid)
        ).all()
    }
    existing_version_rows: dict[int, KnowledgeNodeVersion] = {}
    if existing_nodes:
        version_rows = session.exec(
            select(KnowledgeNodeVersion).where(
                col(KnowledgeNodeVersion.node_id).in_(
                    [int(row.id or 0) for row in existing_nodes.values()]
                )
            )
        ).all()
        for row in version_rows:
            current = existing_version_rows.get(row.node_id)
            if current is None or row.version > current.version:
                existing_version_rows[row.node_id] = row

    def protected_differs(old: dict[str, Any], new: dict[str, Any]) -> bool:
        return any(
            old.get(key) != new.get(key) for key in ("name", "data_type", "dictionary")
        )

    for natural_key in sorted(plan.nodes):
        draft = plan.nodes[natural_key]
        node = existing_nodes.get((draft.node_kind, draft.natural_key))
        created = node is None
        if node is None:
            node = KnowledgeNode(
                oid=oid,
                node_kind=draft.node_kind,
                natural_key=draft.natural_key,
                namespace=draft.namespace,
                create_time=now,
                update_time=now,
            )
            session.add(node)
            session.flush()
        current = existing_version_rows.get(int(node.id or 0))
        _version, changed = append_node_version(
            session,
            node=node,
            current=current,
            payload=draft.payload,
            evidence_refs=draft.evidence_refs,
            confidence=draft.confidence,
            stub=draft.stub,
            origin_package_id=package_row_id,
            now=now,
        )
        if created:
            report.created_nodes += 1
        elif not changed:
            report.unchanged_nodes += 1
        else:
            report.updated_nodes += 1
            if (
                current is not None
                and current.origin_package_id is not None
                and package_row_id is not None
                and current.origin_package_id != package_row_id
                and current.payload is not None
                and protected_differs(current.payload, draft.payload)
            ):
                session.add(
                    KnowledgeMergeConflict(
                        oid=oid,
                        node_id=int(node.id or 0),
                        claim={
                            "new_payload": draft.payload,
                            "old_payload": current.payload,
                            "package_row_id": package_row_id,
                        },
                        source_authority="import-merge",
                        status="open",
                        create_time=now,
                        update_time=now,
                    )
                )
                report.conflicts_queued += 1
        node_ids[draft.natural_key] = int(node.id or 0)

    existing_edges: dict[tuple[int, int, str], KnowledgeEdge] = {}
    if node_ids:
        edges = session.exec(
            select(KnowledgeEdge).where(
                KnowledgeEdge.oid == oid,
                col(KnowledgeEdge.src_node_id).in_(list(node_ids.values())),
            )
        ).all()
        for edge in edges:
            existing_edges[(edge.src_node_id, edge.dst_node_id, edge.edge_kind)] = edge
    for draft in plan.edges:
        src_id = node_ids.get(draft.src_key)
        dst_id = node_ids.get(draft.dst_key)
        if src_id is None or dst_id is None:
            continue
        edge = existing_edges.get((src_id, dst_id, draft.edge_kind))
        if edge is None:
            session.add(
                KnowledgeEdge(
                    oid=oid,
                    src_node_id=src_id,
                    dst_node_id=dst_id,
                    edge_kind=draft.edge_kind,
                    status=draft.status,
                    evidence=draft.evidence,
                    create_time=now,
                    update_time=now,
                )
            )
            report.created_edges += 1
        elif edge.status != draft.status or edge.evidence != draft.evidence:
            edge.status = draft.status
            edge.evidence = draft.evidence
            edge.update_time = now
            session.add(edge)
            report.updated_edges += 1

    for comp in plan.compositions:
        existing = session.exec(
            select(UnitComposition).where(
                UnitComposition.oid == oid,
                UnitComposition.unit_key == comp.unit_key,
            )
        ).first()
        refs_payload = {
            "unit": {
                "unit_id": comp.unit_id,
                "description": comp.description,
                "aliases": list(comp.aliases),
                "assumptions": list(comp.assumptions),
                "conflicts": list(comp.conflicts),
                "evidence_refs": list(comp.evidence_refs),
                "confidence": comp.confidence,
            },
            "datasets": [
                {
                    "unit_dataset_id": ref.unit_dataset_id,
                    "dataset_key": ref.dataset_key,
                    "fields": [
                        {"unit_field_id": f.unit_field_id, "field_key": f.field_key}
                        for f in ref.fields
                    ],
                }
                for ref in comp.dataset_refs
            ],
            "buckets": {
                bucket: [
                    {"local_id": ref.local_id, "node_key": ref.node_key} for ref in refs
                ]
                for bucket, refs in comp.bucket_nodes.items()
            },
            "unit_links": comp.unit_links,
            "relationships": comp.relationships,
        }
        entry = assemble_entry(plan, comp)
        comp_hash = fidelity_hash(entry)
        if existing is None:
            session.add(
                UnitComposition(
                    oid=oid,
                    unit_key=comp.unit_key,
                    package_id=package_row_id,
                    domain=comp.domain,
                    title=comp.title,
                    applicability=comp.applicability,
                    refs=refs_payload,
                    content_hash=comp_hash,
                    create_time=now,
                    update_time=now,
                )
            )
        else:
            existing.package_id = package_row_id
            existing.domain = comp.domain
            existing.title = comp.title
            existing.applicability = comp.applicability
            existing.refs = refs_payload
            existing.content_hash = comp_hash
            existing.update_time = now
            session.add(existing)
        report.upserted_compositions += 1

    session.flush()
    return report


@dataclass
class DecomposeReport:
    plan: DecompositionPlan
    persist: PersistReport | None = None
    fidelity: dict[str, str] = field(default_factory=dict)


def decompose_package(
    session: Session,
    *,
    oid: int,
    package: KnowledgePackageV2,
    package_row_id: int | None = None,
) -> DecomposeReport:
    """Plan + persist + fidelity hashes (one call for the register hook)."""
    plan = plan_decomposition(package)
    report = DecomposeReport(plan=plan)
    report.persist = persist_plan(
        session, oid=oid, plan=plan, package_row_id=package_row_id
    )
    for comp in plan.compositions:
        entry = assemble_entry(plan, comp)
        report.fidelity[comp.unit_key] = fidelity_hash(entry)
    return report
