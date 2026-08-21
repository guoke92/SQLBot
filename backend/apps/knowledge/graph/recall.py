"""Node-plane recall: hybrid seeds + bounded closure + delta bundle assembly.

ADR v3.1 P3. The runtime reads ONLY the pinned node index (immutable), never
the editable current payload. Pure functions (seed scoring, closure BFS) are
separated from the session wrappers so the graph logic is unit-testable.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from sqlmodel import Session, col, select

from apps.knowledge.compile.bundle import ApplyHit, BusinessDataBundle
from apps.knowledge.graph.models import (
    CompositionBinding,
    CompositionDeployment,
    KnowledgeEdge,
    KnowledgeNodeIndex,
    KnowledgeNodeVersion,
)
from apps.knowledge.graph.node_kinds import slot_for_kind
from apps.knowledge.models import KnowledgeMatch

logger = logging.getLogger(__name__)

# Semantic hops consume the hop budget; structural has_field traversal is
# free (hub expansion), bounded by the field quota instead.
_SEMANTIC_EDGE_KINDS = {
    "concept_of",
    "references_field",
    "reads",
    "writes",
    "relation_endpoint",
    "precedes",
    "validates",
}

_STRUCTURAL_EDGE_KINDS = {"has_field"}

DEFAULT_QUOTAS: dict[str, int] = {
    "dataset": 8,
    "field": 12,
    "concept": 8,
    "stage": 4,
    "caliber": 3,
    "rule": 3,
    "metric": 3,
    "pattern": 2,
}

MAX_SEEDS = 12
MAX_SEMANTIC_HOPS = 2


# ---------------------------------------------------------------------------
# Pure scoring
# ---------------------------------------------------------------------------


def _norm(value: str) -> str:
    return "".join((value or "").casefold().split())


def lexical_score(text_repr: str, question: str) -> float:
    """Substring-based lexical score; 1.0 when any token fully appears."""
    haystack = _norm(text_repr)
    needle = _norm(question)
    if not haystack or not needle:
        return 0.0
    if needle in haystack:
        return 1.0
    # token-level overlap as a fallback signal
    tokens = [token for token in needle.split() if len(token) >= 2]
    if not tokens:
        return 0.0
    hits = sum(1 for token in tokens if token in haystack)
    return 0.5 * (hits / len(tokens))


def physical_match(physical_key: str, question: str) -> bool:
    if not physical_key:
        return False
    key = _norm(physical_key)
    question_norm = _norm(question)
    if not key or not question_norm:
        return False
    if key in question_norm:
        return True
    segments = key.split(".")
    # Any non-database suffix (table or table.field) appearing verbatim.
    for start in (1, 2):
        if start < len(segments):
            if ".".join(segments[start:]) in question_norm:
                return True
    # A meaningful trailing field/table token (length >= 4) counts too.
    return len(segments[-1]) >= 4 and segments[-1] in question_norm


@dataclass
class SeedHit:
    node_version_id: int
    node_id: int
    node_kind: str
    natural_key: str
    physical_key: str
    text_repr: str
    content: dict[str, Any]
    deployment_id: int
    score: float
    sources: list[str] = field(default_factory=list)


def score_seed(
    *,
    text_repr: str,
    physical_key: str,
    question: str,
    vector_similarity: float = 0.0,
    embedding_enabled: bool = True,
) -> tuple[float, list[str]]:
    sources: list[str] = []
    score = 0.0
    exact = physical_match(physical_key, question)
    if exact:
        sources.append("exact")
        score = max(score, 2.0)
    lexical = lexical_score(text_repr, question)
    if lexical > 0:
        sources.append("lexical")
        score = max(score, 1.0 + lexical)
    if embedding_enabled and vector_similarity > 0.4:
        sources.append("vector")
        score = max(score, vector_similarity)
    return score, sources


# ---------------------------------------------------------------------------
# Pure closure (bounded BFS over typed edges)
# ---------------------------------------------------------------------------


@dataclass
class EdgeView:
    src: int
    dst: int
    kind: str
    status: str


@dataclass
class ClosureResult:
    reached: dict[int, int] = field(default_factory=dict)  # node_id -> hop distance
    used_edges: list[EdgeView] = field(default_factory=list)


def expand_closure(
    seed_node_ids: list[int],
    edges: list[EdgeView],
    *,
    node_kind_by_id: dict[int, str],
    quotas: dict[str, int] | None = None,
    max_semantic_hops: int = MAX_SEMANTIC_HOPS,
) -> ClosureResult:
    """Bounded BFS: semantic edges cost a hop, structural (has_field) free.

    Only confirmed edges auto-expand; proposed edges never do. Per-kind quotas
    cap how many nodes of each kind enter the closure (the runtime budget).
    """
    quotas = quotas or dict(DEFAULT_QUOTAS)
    adjacency: dict[int, list[EdgeView]] = {}
    for edge in edges:
        if edge.status != "confirmed":
            continue
        adjacency.setdefault(edge.src, []).append(edge)
        adjacency.setdefault(edge.dst, []).append(
            EdgeView(src=edge.dst, dst=edge.src, kind=edge.kind, status=edge.status)
        )

    result = ClosureResult()
    frontier: list[tuple[int, int]] = []
    kind_counts: dict[str, int] = {}
    for node_id in seed_node_ids:
        result.reached[node_id] = 0
        frontier.append((node_id, 0))

    visited: set[tuple[int, int]] = set()  # (node_id, hop) for semantic edges
    while frontier:
        node_id, hops = frontier.pop(0)
        for edge in adjacency.get(node_id, []):
            peer = edge.dst
            kind = node_kind_by_id.get(peer, "unknown")
            if edge.kind in _STRUCTURAL_EDGE_KINDS:
                if peer not in result.reached:
                    if kind_counts.get(kind, 0) >= quotas.get(kind, 0):
                        continue
                    kind_counts[kind] = kind_counts.get(kind, 0) + 1
                    result.reached[peer] = hops
                    result.used_edges.append(edge)
                    frontier.append((peer, hops))
                continue
            if edge.kind not in _SEMANTIC_EDGE_KINDS:
                continue
            if hops + 1 > max_semantic_hops:
                continue
            marker = (peer, hops + 1)
            if marker in visited:
                continue
            if peer in result.reached:
                continue
            if kind_counts.get(kind, 0) >= quotas.get(kind, 0):
                continue
            visited.add(marker)
            kind_counts[kind] = kind_counts.get(kind, 0) + 1
            result.reached[peer] = hops + 1
            result.used_edges.append(edge)
            frontier.append((peer, hops + 1))
    return result


# ---------------------------------------------------------------------------
# Session wrappers
# ---------------------------------------------------------------------------


def active_index_rows(
    session: Session, *, oid: int, datasource_id: int
) -> list[KnowledgeNodeIndex]:
    """Index rows of ACTIVE deployments bound to the datasource."""
    rows = session.exec(
        select(KnowledgeNodeIndex, CompositionDeployment, CompositionBinding)
        .join(
            CompositionDeployment,
            CompositionDeployment.id == KnowledgeNodeIndex.deployment_id,
        )
        .join(
            CompositionBinding,
            CompositionBinding.id == CompositionDeployment.binding_id,
        )
        .where(
            KnowledgeNodeIndex.oid == oid,
            KnowledgeNodeIndex.active.is_(True),
            CompositionDeployment.status == "ACTIVE",
            CompositionBinding.datasource_id == datasource_id,
        )
    ).all()
    return [index_row for index_row, _deployment, _binding in rows]


def _active_node_edges(session: Session, *, oid: int) -> list[EdgeView]:
    """All edges for the workspace; the closure BFS prunes unreachable ones."""
    edges = session.exec(select(KnowledgeEdge).where(KnowledgeEdge.oid == oid)).all()
    return [
        EdgeView(
            src=e.src_node_id, dst=e.dst_node_id, kind=e.edge_kind, status=e.status
        )
        for e in edges
    ]


@dataclass
class NodeRecallResult:
    seeds: list[SeedHit]
    reached: dict[int, int]
    index_by_node: dict[int, KnowledgeNodeIndex]
    used_edges: list[EdgeView]


def recall_nodes(
    session: Session,
    *,
    question: str,
    oid: int,
    datasource_id: int,
    vector_similarities: dict[int, float] | None = None,
    embedding_enabled: bool = True,
    quotas: dict[str, int] | None = None,
) -> NodeRecallResult:
    """Seed via hybrid retrieval, then expand a bounded confirmed closure."""
    rows = active_index_rows(session, oid=oid, datasource_id=datasource_id)
    # Resolve node_version_id -> node_id (edges reference node ids).
    version_ids = [int(row.node_version_id or 0) for row in rows if row.node_version_id]
    node_id_by_version: dict[int, int] = {}
    if version_ids:
        versions = session.exec(
            select(KnowledgeNodeVersion).where(
                col(KnowledgeNodeVersion.id).in_(version_ids)
            )
        ).all()
        node_id_by_version = {
            int(version.id or 0): int(version.node_id or 0) for version in versions
        }
    index_by_node: dict[int, KnowledgeNodeIndex] = {}
    node_kind_by_id: dict[int, str] = {}
    seeds: list[SeedHit] = []
    for row in rows:
        node_id = node_id_by_version.get(int(row.node_version_id or 0))
        if node_id is None:
            continue
        index_by_node[node_id] = row
        node_kind_by_id[node_id] = row.node_kind
        sim = (vector_similarities or {}).get(int(row.node_version_id or 0), 0.0)
        score, sources = score_seed(
            text_repr=row.text_repr or "",
            physical_key=row.physical_key or "",
            question=question,
            vector_similarity=sim,
            embedding_enabled=embedding_enabled,
        )
        if score <= 0:
            continue
        seeds.append(
            SeedHit(
                node_version_id=int(row.node_version_id or 0),
                node_id=node_id,
                node_kind=row.node_kind,
                natural_key="",
                physical_key=row.physical_key or "",
                text_repr=row.text_repr or "",
                content=dict(row.content or {}),
                deployment_id=int(row.deployment_id or 0),
                score=score,
                sources=sources,
            )
        )
    seeds.sort(key=lambda item: (-item.score, item.node_id))
    seeds = seeds[:MAX_SEEDS]
    seed_ids = [seed.node_id for seed in seeds]
    edges = _active_node_edges(session, oid=oid)
    closure = expand_closure(
        seed_ids,
        edges,
        node_kind_by_id=node_kind_by_id,
        quotas=quotas,
    )
    return NodeRecallResult(
        seeds=seeds,
        reached=closure.reached,
        index_by_node=index_by_node,
        used_edges=closure.used_edges,
    )


def assemble_node_bundle(
    result: NodeRecallResult,
    *,
    stage: str = "generate",
    matches: list[KnowledgeMatch] | None = None,
) -> BusinessDataBundle:
    """Delta slice the reached nodes into BusinessDataBundle slots."""
    bundle = BusinessDataBundle(stage=stage, matches=matches or [])
    seen: dict[str, set[str]] = {}
    apply_log: list[ApplyHit] = []
    for node_id in sorted(result.reached):
        row = result.index_by_node.get(node_id)
        if row is None:
            continue
        content = dict(row.content or {})
        kind = row.node_kind
        slot = slot_for_kind(kind)
        if slot is None:
            continue
        dedupe_key = _dedupe_key(kind, content)
        if dedupe_key in seen.get(slot, set()):
            continue
        seen.setdefault(slot, set()).add(dedupe_key)
        getattr(bundle, slot).append(content)
        apply_log.append(
            ApplyHit(
                asset_kind=f"knowledge_{kind}",
                asset_id=row.node_version_id,
                trust_tier="published",
                apply="constrain",
                reason="node_closure_reached",
                meta={"hop": result.reached[node_id]},
            )
        )
    # Synthesize JOIN relationships from the confirmed relation_endpoint edges
    # that the closure actually traversed, using field slot contents.
    relation_seen: set[tuple[int, int]] = set()
    for edge in result.used_edges:
        if edge.kind != "relation_endpoint":
            continue
        left = result.index_by_node.get(edge.src)
        right = result.index_by_node.get(edge.dst)
        if left is None or right is None:
            continue
        left_content = dict(left.content or {})
        right_content = dict(right.content or {})
        marker = (edge.src, edge.dst)
        if marker in relation_seen:
            continue
        relation_seen.add(marker)
        bundle.relationships.append(
            {
                "relationship_id": f"edge-{edge.src}-{edge.dst}",
                "left": {
                    "dataset": left_content.get("dataset_id"),
                    "field": left_content.get("field_id"),
                },
                "right": {
                    "dataset": right_content.get("dataset_id"),
                    "field": right_content.get("field_id"),
                },
                "status": edge.status,
            }
        )
    bundle.apply_log = apply_log
    return bundle


def _dedupe_key(kind: str, content: dict[str, Any]) -> str:
    return f"{kind}:{content.get('dataset_id') or ''}.{content.get('field_id') or content.get('concept_id') or content.get('stage_id') or content.get('caliber_id') or content.get('rule_id') or content.get('metric_id') or content.get('pattern_id') or ''}"
