"""Feedback plane (ADR v3.1 P4): close the write-only inbox and ingest L-3 joins.

The capture plane produced staging candidates with no exit; this module gives
them read/reject/promote exits into the node store, and turns mined join
candidates (field_relation CANDIDATE) into proposed relation_endpoint edges.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlmodel import Session, col, select

from apps.knowledge.db_models import KnowledgeStaging
from apps.knowledge.graph.decompose import append_node_version
from apps.knowledge.graph.identity import dataset_key, field_key
from apps.knowledge.graph.models import (
    KnowledgeEdge,
    KnowledgeNode,
    KnowledgeNodeVersion,
)
from apps.knowledge.lineage import append_event

_PROMOTABLE_KINDS = {"caliber", "rule"}


def _now() -> datetime:
    return datetime.utcnow()


# ---------------------------------------------------------------------------
# Inbox (staging candidates)
# ---------------------------------------------------------------------------


def list_inbox_candidates(
    session: Session, *, oid: int, kind: str | None = None, limit: int = 100
) -> list[dict[str, Any]]:
    statement = (
        select(KnowledgeStaging)
        .where(KnowledgeStaging.oid == oid, KnowledgeStaging.status == "pending")
        .order_by(col(KnowledgeStaging.create_time).desc())
        .limit(limit)
    )
    if kind:
        statement = statement.where(KnowledgeStaging.kind == kind)
    rows = session.exec(statement).all()
    return [
        {
            "id": int(row.id or 0),
            "kind": row.kind,
            "trigger_id": row.trigger_id,
            "source_record_id": row.source_record_id,
            "suggested_trust_tier": row.suggested_trust_tier,
            "payload": row.payload,
            "create_time": row.create_time,
            "promotable": row.kind in _PROMOTABLE_KINDS,
        }
        for row in rows
    ]


def reject_inbox_candidate(
    session: Session,
    *,
    oid: int,
    staging_id: int,
    actor_user_id: int | None,
    reason: str,
) -> dict[str, Any]:
    staging = session.get(KnowledgeStaging, staging_id)
    if staging is None or staging.oid != oid:
        raise ValueError("staging candidate not found")
    staging.status = "rejected"
    staging.reject_reason = reason
    staging.update_time = _now()
    session.add(staging)
    append_event(
        session,
        lineage_id=staging.lineage_id,
        asset_kind=staging.kind,
        action="rejected",
        asset_id=staging.id,
        actor={"user_id": actor_user_id},
        evidence_snapshot={"reason": reason},
        require_evidence=True,
    )
    session.commit()
    return {"id": staging_id, "status": "rejected"}


def _upsert_node(
    session: Session,
    *,
    oid: int,
    node_kind: str,
    natural_key: str,
    namespace: str,
    payload: dict[str, Any],
    evidence_refs: list[str],
) -> tuple[KnowledgeNode, KnowledgeNodeVersion]:
    node = session.exec(
        select(KnowledgeNode).where(
            KnowledgeNode.oid == oid,
            KnowledgeNode.node_kind == node_kind,
            KnowledgeNode.natural_key == natural_key,
        )
    ).first()
    now = _now()
    if node is None:
        node = KnowledgeNode(
            oid=oid,
            node_kind=node_kind,
            natural_key=natural_key,
            namespace=namespace,
            create_time=now,
            update_time=now,
        )
        session.add(node)
        session.flush()
    current = session.exec(
        select(KnowledgeNodeVersion)
        .where(KnowledgeNodeVersion.node_id == int(node.id or 0))
        .order_by(col(KnowledgeNodeVersion.version).desc())
    ).first()
    version, _changed = append_node_version(
        session,
        node=node,
        current=current,
        payload=payload,
        evidence_refs=evidence_refs,
        confidence=None,
        stub=None,
        origin_package_id=None,
        now=now,
    )
    return node, version


def promote_inbox_candidate(
    session: Session,
    *,
    oid: int,
    staging_id: int,
    actor_user_id: int | None,
) -> dict[str, Any]:
    staging = session.get(KnowledgeStaging, staging_id)
    if staging is None or staging.oid != oid:
        raise ValueError("staging candidate not found")
    if staging.status != "pending":
        raise ValueError("staging candidate is not pending")
    if staging.kind not in _PROMOTABLE_KINDS:
        raise ValueError(f"staging kind {staging.kind!r} is not promotable to a node")
    payload = dict(staging.payload or {})
    natural_key = f"capture:{staging.kind}:{staging.id}"
    node, version = _upsert_node(
        session,
        oid=oid,
        node_kind=staging.kind,
        natural_key=natural_key,
        namespace="capture",
        payload=payload,
        evidence_refs=[str(staging.trigger_id or "")],
    )
    staging.status = "promoted"
    staging.update_time = _now()
    session.add(staging)
    append_event(
        session,
        lineage_id=staging.lineage_id,
        asset_kind=staging.kind,
        action="promoted",
        asset_id=staging.id,
        actor={"user_id": actor_user_id},
        evidence_snapshot={
            "node_id": int(node.id or 0),
            "node_version": version.version,
        },
        require_evidence=True,
    )
    session.commit()
    return {
        "staging_id": staging_id,
        "node_id": int(node.id or 0),
        "natural_key": natural_key,
        "node_version": version.version,
    }


# ---------------------------------------------------------------------------
# L-3: mined join candidates -> proposed relation_endpoint edges
# ---------------------------------------------------------------------------


def _field_node_key(session: Session, field_id: int) -> str | None:
    from apps.datasource.models.datasource import CoreField, CoreTable

    field = session.get(CoreField, field_id)
    if field is None:
        return None
    table = session.get(CoreTable, field.table_id)
    if table is None:
        return None
    ds_key = dataset_key(table.database_name or "", table.table_name)
    return field_key(ds_key, field.field_name)


def _ensure_field_node(
    session: Session, *, oid: int, field_natural_key: str
) -> KnowledgeNode:
    node = session.exec(
        select(KnowledgeNode).where(
            KnowledgeNode.oid == oid,
            KnowledgeNode.node_kind == "field",
            KnowledgeNode.natural_key == field_natural_key,
        )
    ).first()
    if node is not None:
        return node
    # stub field node + stub dataset node + has_field edge
    parent_key = field_natural_key.rsplit(".", 1)[0]
    parent = session.exec(
        select(KnowledgeNode).where(
            KnowledgeNode.oid == oid,
            KnowledgeNode.node_kind == "dataset",
            KnowledgeNode.natural_key == parent_key,
        )
    ).first()
    now = _now()
    if parent is None:
        parent = KnowledgeNode(
            oid=oid,
            node_kind="dataset",
            natural_key=parent_key,
            namespace="catalog",
            create_time=now,
            update_time=now,
        )
        session.add(parent)
        session.flush()
        append_node_version(
            session,
            node=parent,
            current=None,
            payload={"name": parent_key.rsplit(".", 1)[-1]},
            evidence_refs=[],
            confidence=None,
            stub=True,
            origin_package_id=None,
            now=now,
        )
        session.flush()
    field_name = field_natural_key.rsplit(".", 1)[-1]
    node = KnowledgeNode(
        oid=oid,
        node_kind="field",
        natural_key=field_natural_key,
        namespace="catalog",
        create_time=now,
        update_time=now,
    )
    session.add(node)
    session.flush()
    append_node_version(
        session,
        node=node,
        current=None,
        payload={"name": field_name},
        evidence_refs=[],
        confidence=None,
        stub=True,
        origin_package_id=None,
        now=now,
    )
    session.flush()
    session.add(
        KnowledgeEdge(
            oid=oid,
            src_node_id=int(parent.id or 0),
            dst_node_id=int(node.id or 0),
            edge_kind="has_field",
            status="confirmed",
            evidence={},
            create_time=now,
            update_time=now,
        )
    )
    return node


def ingest_join_candidates_as_edges(session: Session, *, oid: int, ds_id: int) -> int:
    """Turn CANDIDATE field_relation rows into proposed relation_endpoint edges."""
    from apps.datasource.profiling.models import FieldRelation

    candidates = session.exec(
        select(FieldRelation).where(
            FieldRelation.oid == oid,
            FieldRelation.ds_id == ds_id,
            FieldRelation.status == "CANDIDATE",
        )
    ).all()
    created = 0
    for relation in candidates:
        left_key = _field_node_key(session, int(relation.source_field_id or 0))
        right_key = _field_node_key(session, int(relation.target_field_id or 0))
        if left_key is None or right_key is None:
            continue
        left_node = _ensure_field_node(session, oid=oid, field_natural_key=left_key)
        right_node = _ensure_field_node(session, oid=oid, field_natural_key=right_key)
        existing = session.exec(
            select(KnowledgeEdge).where(
                KnowledgeEdge.oid == oid,
                KnowledgeEdge.src_node_id == int(left_node.id or 0),
                KnowledgeEdge.dst_node_id == int(right_node.id or 0),
                KnowledgeEdge.edge_kind == "relation_endpoint",
            )
        ).first()
        if existing is not None:
            continue
        now = _now()
        session.add(
            KnowledgeEdge(
                oid=oid,
                src_node_id=int(left_node.id or 0),
                dst_node_id=int(right_node.id or 0),
                edge_kind="relation_endpoint",
                status="proposed",
                evidence={
                    "source": "query_log_join_mining",
                    "relation_id": relation.id,
                },
                create_time=now,
                update_time=now,
            )
        )
        created += 1
    if created:
        session.commit()
    return created
