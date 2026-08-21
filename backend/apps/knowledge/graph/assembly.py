"""Assemble a composition row into the KnowledgeUnitEntry view.

One code path (ADR v3.1 P2): the review view and the publish snapshot both
call :func:`assemble_composition`, so what the reviewer sees is exactly
what gets pinned.
"""

from __future__ import annotations

from typing import Any

from sqlmodel import Session, col, select

from apps.knowledge.graph.decompose import (
    BucketNodeRef,
    CompositionDraft,
    DatasetRefDraft,
    FieldRefDraft,
    assemble_entry,
    fidelity_hash,
)
from apps.knowledge.graph.models import KnowledgeNode, KnowledgeNodeVersion


class _NodeView:
    __slots__ = ("node", "version")

    def __init__(self, node: KnowledgeNode, version: KnowledgeNodeVersion) -> None:
        self.node = node
        self.version = version


def composition_draft_from_refs(refs: dict[str, Any]) -> CompositionDraft:
    """Rebuild a CompositionDraft from the persisted refs JSON."""
    unit = refs.get("unit") or {}
    comp = CompositionDraft(
        unit_id=str(unit.get("unit_id") or ""),
        unit_key="",
        domain="",
        title="",
        applicability="",
        description=str(unit.get("description") or ""),
        aliases=list(unit.get("aliases") or []),
        assumptions=list(unit.get("assumptions") or []),
        conflicts=list(unit.get("conflicts") or []),
        unit_links=list(refs.get("unit_links") or []),
        evidence_refs=list(unit.get("evidence_refs") or []),
        confidence=float(unit.get("confidence") or 0.5),
    )
    for dataset_ref in refs.get("datasets") or []:
        draft = DatasetRefDraft(
            unit_dataset_id=str(dataset_ref.get("unit_dataset_id") or ""),
            dataset_key=str(dataset_ref.get("dataset_key") or ""),
        )
        for field_ref in dataset_ref.get("fields") or []:
            draft.fields.append(
                FieldRefDraft(
                    unit_field_id=str(field_ref.get("unit_field_id") or ""),
                    field_key=str(field_ref.get("field_key") or ""),
                )
            )
        comp.dataset_refs.append(draft)
    for bucket, node_refs in (refs.get("buckets") or {}).items():
        comp.bucket_nodes[str(bucket)] = [
            BucketNodeRef(
                local_id=str(item.get("local_id") or ""),
                node_key=str(item.get("node_key") or ""),
            )
            for item in node_refs or []
        ]
    comp.relationships = list(refs.get("relationships") or [])
    return comp


class _NodeProxy:
    __slots__ = ("payload",)

    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload


class _NodeMap:
    __slots__ = ("_views",)

    def __init__(self, views: dict[str, _NodeView]) -> None:
        self._views = views

    def __getitem__(self, key: str) -> _NodeProxy:
        return _NodeProxy(self._views[key].version.payload)

    def __contains__(self, key: str) -> bool:
        return key in self._views


class _PlanView:
    """Minimal plan-like object satisfying assemble_entry's needs."""

    def __init__(self, nodes: dict[str, _NodeView]) -> None:
        self.nodes = _NodeMap(nodes)


def load_current_versions(session: Session, keys: list[str]) -> dict[str, _NodeView]:
    """Current node + version rows for the given natural keys."""
    keys = [key for key in keys if key]
    if not keys:
        return {}
    nodes = session.exec(
        select(KnowledgeNode).where(col(KnowledgeNode.natural_key).in_(keys))
    ).all()
    by_key = {node.natural_key: node for node in nodes}
    versions: dict[int, KnowledgeNodeVersion] = {}
    if nodes:
        rows = session.exec(
            select(KnowledgeNodeVersion).where(
                col(KnowledgeNodeVersion.node_id).in_(
                    [int(node.id or 0) for node in nodes]
                )
            )
        ).all()
        for row in rows:
            current = versions.get(row.node_id)
            if current is None or row.version > current.version:
                versions[row.node_id] = row
    result: dict[str, _NodeView] = {}
    for key, node in by_key.items():
        version = versions.get(int(node.id or 0))
        if version is not None:
            result[key] = _NodeView(node, version)
    return result


def composition_node_keys(refs: dict[str, Any]) -> list[str]:
    """Every node key a composition references."""
    keys: list[str] = []
    for dataset_ref in refs.get("datasets") or []:
        keys.append(str(dataset_ref.get("dataset_key") or ""))
        for field_ref in dataset_ref.get("fields") or []:
            keys.append(str(field_ref.get("field_key") or ""))
    for node_refs in (refs.get("buckets") or {}).values():
        for item in node_refs or []:
            keys.append(str(item.get("node_key") or ""))
    return [key for key in keys if key]


def assemble_composition(session: Session, composition: Any) -> dict[str, Any]:
    """Entry view from the persisted composition row (single code path)."""
    refs = dict(composition.refs or {})
    comp = composition_draft_from_refs(refs)
    comp.unit_key = composition.unit_key
    comp.domain = composition.domain
    comp.title = composition.title
    comp.applicability = composition.applicability
    plan_view = _PlanView(load_current_versions(session, composition_node_keys(refs)))
    return assemble_entry(plan_view, comp)  # type: ignore[arg-type]


def composition_fidelity_hash(entry: dict[str, Any]) -> str:
    return fidelity_hash(entry)
