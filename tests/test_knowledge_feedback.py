from __future__ import annotations

import importlib
from datetime import datetime
from typing import Any

import pytest

from _fake_store import FakeStore as _BaseFakeStore
from apps.datasource.models.datasource import CoreField, CoreTable
from apps.datasource.profiling.models import FieldRelation
from apps.knowledge.db_models import KnowledgeLineageEvent, KnowledgeStaging
from apps.knowledge.graph import feedback
from apps.knowledge.graph.models import (
    KnowledgeEdge,
    KnowledgeNode,
    KnowledgeNodeVersion,
)


_ENTITIES = {
    KnowledgeStaging: "staging",
    KnowledgeNode: "nodes",
    KnowledgeNodeVersion: "versions",
    KnowledgeEdge: "edges",
    KnowledgeLineageEvent: "lineage",
    FieldRelation: "relations",
    CoreField: "core_fields",
    CoreTable: "core_tables",
}


class FakeStore(_BaseFakeStore):
    def __init__(self) -> None:
        super().__init__(_ENTITIES)


def _staging(store: FakeStore, kind: str = "caliber", status: str = "pending") -> KnowledgeStaging:
    row = KnowledgeStaging(
        id=200,
        oid=1,
        kind=kind,
        status=status,
        natural_key="nk",
        scope={"ds_id": 9},
        payload={"label": "签收额含税", "contract_fragment": {"version": 1}},
        trigger_id="V-T1",
        lineage_id="lin_1",
    )
    store.staging.append(row)
    return row


class TestInboxPromote:
    def test_promote_creates_capture_node_and_marks_promoted(self) -> None:
        store = FakeStore()
        session = store.session()
        row = _staging(store)
        result = feedback.promote_inbox_candidate(
            session, oid=1, staging_id=200, actor_user_id=7
        )
        assert result["natural_key"] == "capture:caliber:200"
        node = next(n for n in store.nodes if n.node_kind == "caliber")
        assert node.namespace == "capture"
        assert row.status == "promoted"
        assert any(e.action == "promoted" for e in store.lineage)

    def test_promote_requires_pending(self) -> None:
        store = FakeStore()
        session = store.session()
        _staging(store, status="promoted")
        with pytest.raises(ValueError, match="not pending"):
            feedback.promote_inbox_candidate(
                session, oid=1, staging_id=200, actor_user_id=None
            )

    def test_promote_rejects_non_promotable_kind(self) -> None:
        store = FakeStore()
        session = store.session()
        _staging(store, kind="entity")
        with pytest.raises(ValueError, match="not promotable"):
            feedback.promote_inbox_candidate(
                session, oid=1, staging_id=200, actor_user_id=None
            )

    def test_reject_records_reason(self) -> None:
        store = FakeStore()
        session = store.session()
        row = _staging(store)
        feedback.reject_inbox_candidate(
            session, oid=1, staging_id=200, actor_user_id=7, reason="重复口径"
        )
        assert row.status == "rejected"
        assert row.reject_reason == "重复口径"
        assert any(e.action == "rejected" for e in store.lineage)

    def test_list_inbox_only_pending(self) -> None:
        store = FakeStore()
        session = store.session()
        _staging(store)
        _staging(store, status="rejected")
        items = feedback.list_inbox_candidates(session, oid=1)
        assert len(items) == 1
        assert items[0]["promotable"] is True


class TestJoinEdgeIngestion:
    def _catalog(self, store: FakeStore, field_id: int, table_id: int, name: str, table_name: str) -> None:
        store.core_fields.append(
            CoreField(
                id=field_id,
                ds_id=9,
                table_id=table_id,
                field_name=name,
                field_type="varchar",
                checked=True,
                create_time=datetime.utcnow(),
                update_time=datetime.utcnow(),
            )
        )
        store.core_tables.append(
            CoreTable(
                id=table_id,
                ds_id=9,
                oid=1,
                table_name=table_name,
                database_name="db1",
                create_time=datetime.utcnow(),
                update_time=datetime.utcnow(),
            )
        )

    def test_creates_proposed_relation_edge(self) -> None:
        store = FakeStore()
        session = store.session()
        self._catalog(store, field_id=1, table_id=10, name="cust_id", table_name="agreement")
        self._catalog(store, field_id=2, table_id=11, name="id", table_name="company")
        store.relations.append(
            FieldRelation(
                id=300,
                oid=1,
                ds_id=9,
                source_table_id=10,
                source_field_id=1,
                target_table_id=11,
                target_field_id=2,
                kind="EQUI_JOIN",
                status="CANDIDATE",
                create_time=datetime.utcnow(),
                update_time=datetime.utcnow(),
            )
        )
        created = feedback.ingest_join_candidates_as_edges(
            session, oid=1, ds_id=9
        )
        assert created == 1
        edge = next(
            e for e in store.edges if e.edge_kind == "relation_endpoint"
        )
        assert edge.status == "proposed"
        field_nodes = {n.natural_key for n in store.nodes if n.node_kind == "field"}
        assert "db1.agreement.cust_id" in field_nodes
        assert "db1.company.id" in field_nodes

    def test_idempotent_rerun(self) -> None:
        store = FakeStore()
        session = store.session()
        self._catalog(store, field_id=1, table_id=10, name="cust_id", table_name="agreement")
        self._catalog(store, field_id=2, table_id=11, name="id", table_name="company")
        store.relations.append(
            FieldRelation(
                id=300,
                oid=1,
                ds_id=9,
                source_table_id=10,
                source_field_id=1,
                target_table_id=11,
                target_field_id=2,
                kind="EQUI_JOIN",
                status="CANDIDATE",
                create_time=datetime.utcnow(),
                update_time=datetime.utcnow(),
            )
        )
        assert feedback.ingest_join_candidates_as_edges(session, oid=1, ds_id=9) == 1
        assert feedback.ingest_join_candidates_as_edges(session, oid=1, ds_id=9) == 0
