from __future__ import annotations

import json
from datetime import datetime
from typing import Any

import pytest

from _fake_store import FakeStore as _BaseFakeStore
from apps.datasource.models.datasource import CoreDatasource, CoreField, CoreTable
from apps.knowledge.graph import governance
from apps.knowledge.graph.assembly import assemble_composition
from apps.knowledge.graph.decompose import (
    assemble_entry,
    fidelity_hash,
    persist_plan,
    plan_decomposition,
)
from apps.knowledge.graph.models import (
    CompositionBinding,
    CompositionDeployment,
    KnowledgeEdge,
    KnowledgeMergeConflict,
    KnowledgeNode,
    KnowledgeNodeIndex,
    KnowledgeNodeVersion,
    UnitComposition,
)
from apps.knowledge.semantic.schema import KnowledgePackageV2


def _dataset(dataset_id: str, name: str, fields: list[dict], **extra: Any) -> dict:
    return {"dataset_id": dataset_id, "name": name, "fields": fields, **extra}


def _field(field_id: str, name: str, **extra: Any) -> dict:
    return {"field_id": field_id, "name": name, **extra}


def _package(units: list[dict]) -> KnowledgePackageV2:
    return KnowledgePackageV2.model_validate(
        {
            "schema_version": "2.0",
            "package": {
                "package_id": "gov",
                "revision": 1,
                "title": "gov",
                "namespace": "gov",
            },
            "sources": [{"source_id": "src", "kind": "source_code"}],
            "evidence": [
                {
                    "evidence_id": "ev-1",
                    "source_id": "src",
                    "evidence_kind": "code_path",
                    "locator": "X.java",
                }
            ],
            "knowledge_units": units,
        }
    )


def _unit(unit_id: str, datasets: list[dict]) -> dict:
    return {
        "unit_id": unit_id,
        "revision": 1,
        "title": f"{unit_id}-title",
        "domain": "enterprise",
        "description": "d",
        "content": {
            "concepts": [],
            "processes": [
                {
                    "stage_id": "s1",
                    "name": "阶段",
                    "data_effects": [
                        {
                            "operation": "update",
                            "dataset": datasets[0]["dataset_id"],
                            "fields": [datasets[0]["fields"][0]["field_id"]],
                        }
                    ],
                }
            ],
            "datasets": datasets,
            "relationships": [],
            "metrics": [
                {
                    "metric_id": "m1",
                    "name": "计数",
                    "aggregation": "COUNT",
                    "field": {
                        "dataset": datasets[0]["dataset_id"],
                        "field": datasets[0]["fields"][0]["field_id"],
                    },
                }
            ],
            "calibers": [],
            "domain_rules": [],
            "verified_query_patterns": [],
        },
        "evidence_refs": ["ev-1"],
    }


_ENTITIES = {
    KnowledgeNode: "nodes",
    KnowledgeNodeVersion: "versions",
    KnowledgeEdge: "edges",
    UnitComposition: "compositions",
    CompositionBinding: "bindings",
    CompositionDeployment: "deployments",
    KnowledgeNodeIndex: "index_rows",
    KnowledgeMergeConflict: "conflicts",
    CoreDatasource: "datasources",
    CoreTable: "core_tables",
    CoreField: "core_fields",
}


class FakeStore(_BaseFakeStore):
    def __init__(self) -> None:
        super().__init__(_ENTITIES)


def _seed(package: KnowledgePackageV2) -> tuple[FakeStore, list[UnitComposition]]:
    store = FakeStore()
    session = store.session()
    plan = plan_decomposition(package)
    persist_plan(session, oid=1, plan=plan, package_row_id=5)
    return store, list(store.compositions)


def _seed_catalog(store: FakeStore) -> int:
    now = datetime.utcnow()
    ds = CoreDatasource(id=9, oid=1, name="demo", create_time=now, update_time=now)
    store.datasources.append(ds)
    table = CoreTable(
        id=90,
        ds_id=9,
        oid=1,
        table_name="t_company",
        database_name="",
        create_time=now,
        update_time=now,
    )
    store.core_tables.append(table)
    store.core_fields.append(
        CoreField(
            id=900,
            ds_id=9,
            table_id=90,
            field_name="id",
            field_type="bigint",
            checked=True,
            create_time=now,
            update_time=now,
        )
    )
    return 9


def _simple_composition() -> tuple[FakeStore, UnitComposition]:
    package = _package(
        [
            _unit(
                "onboarding",
                [_dataset("company", "t_company", [_field("id", "id")])],
            )
        ]
    )
    store, compositions = _seed(package)
    return store, compositions[0]


class TestAssemblyFromStore:
    def test_db_assembly_matches_plan_assembly(self) -> None:
        package = _package(
            [
                _unit(
                    "onboarding",
                    [_dataset("company", "t_company", [_field("id", "id")])],
                ),
                _unit(
                    "signing",
                    [_dataset("c", "t_company", [_field("id", "id")])],
                ),
            ]
        )
        store, compositions = _seed(package)
        session = store.session()
        plan = plan_decomposition(package)
        for comp, row in zip(plan.compositions, compositions):
            from_db = assemble_composition(session, row)
            from_plan = assemble_entry(plan, comp)
            assert fidelity_hash(from_db) == fidelity_hash(from_plan)
            assert fidelity_hash(from_db) == row.content_hash


class TestLifecycle:
    def test_validation_gate_blocks_review(self) -> None:
        store, comp = _simple_composition()
        session = store.session()
        with pytest.raises(ValueError, match="pass validation"):
            governance.transition_composition(
                session, oid=1, composition_id=comp.id, target="IN_REVIEW", actor_user_id=None
            )

    def test_binding_gate_blocks_approval(self) -> None:
        store, comp = _simple_composition()
        session = store.session()
        comp.validation_status = "PASS"
        governance.transition_composition(
            session, oid=1, composition_id=comp.id, target="IN_REVIEW", actor_user_id=None
        )
        with pytest.raises(ValueError, match="binding"):
            governance.transition_composition(
                session, oid=1, composition_id=comp.id, target="APPROVED", actor_user_id=None
            )

    def test_happy_path_to_approved_records_review_note(self) -> None:
        store, comp = _simple_composition()
        session = store.session()
        ds_id = _seed_catalog(store)
        governance.bind_and_validate_composition(
            session, oid=1, composition_id=comp.id, datasource_id=ds_id
        )
        governance.transition_composition(
            session,
            oid=1,
            composition_id=comp.id,
            target="IN_REVIEW",
            actor_user_id=7,
        )
        governance.transition_composition(
            session,
            oid=1,
            composition_id=comp.id,
            target="APPROVED",
            actor_user_id=7,
            reason="ok",
        )
        assert comp.lifecycle_status == "APPROVED"
        notes = (comp.refs or {}).get("review_notes") or []
        assert notes and notes[-1]["reason"] == "ok"


class TestBind:
    def test_missing_table_fails_but_stays_bound(self) -> None:
        store, comp = _simple_composition()
        session = store.session()
        now = datetime.utcnow()
        store.datasources.append(
            CoreDatasource(id=9, oid=1, name="demo", create_time=now, update_time=now)
        )
        binding = governance.bind_and_validate_composition(
            session, oid=1, composition_id=comp.id, datasource_id=9
        )
        assert binding.status == "BOUND"  # 不蒸发
        assert comp.validation_status == "FAIL"
        codes = {i["code"] for i in binding.validation_result["issues"]}
        assert "DATASET_NOT_FOUND" in codes

    def test_mapping_keyed_by_node_keys(self) -> None:
        store, comp = _simple_composition()
        session = store.session()
        ds_id = _seed_catalog(store)
        binding = governance.bind_and_validate_composition(
            session, oid=1, composition_id=comp.id, datasource_id=ds_id
        )
        assert comp.validation_status == "PASS"
        assert list(binding.mapping["datasets"]) == ["t_company"]
        assert binding.mapping["fields"]["t_company.id"]["field_name"] == "id"


class TestPublish:
    def test_publish_pins_snapshot_and_builds_index(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        store, comp = _simple_composition()
        session = store.session()
        ds_id = _seed_catalog(store)
        governance.bind_and_validate_composition(
            session, oid=1, composition_id=comp.id, datasource_id=ds_id
        )
        comp.lifecycle_status = "APPROVED"
        monkeypatch.setattr(governance, "build_embeddings_or_raise", lambda texts: None)
        deployment = governance.publish_composition(
            session, oid=1, composition_id=comp.id
        )
        assert deployment.status == "ACTIVE"
        assert deployment.pinned_snapshot["entry"]["unit_id"] == "onboarding"
        assert deployment.pinned_snapshot["meta"]["content_hash"] == comp.content_hash
        assert comp.lifecycle_status == "PUBLISHED"
        assert comp.active_deployment_id == deployment.id
        assert len(store.index_rows) >= 2  # dataset + field (+ stage/metric)
        assert all(row.deployment_id == deployment.id for row in store.index_rows)

    def test_embedding_failure_marks_deployment_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        store, comp = _simple_composition()
        session = store.session()
        ds_id = _seed_catalog(store)
        governance.bind_and_validate_composition(
            session, oid=1, composition_id=comp.id, datasource_id=ds_id
        )
        comp.lifecycle_status = "APPROVED"

        def _boom(texts: list[str]) -> Any:
            raise ValueError("embedding down")

        monkeypatch.setattr(governance, "build_embeddings_or_raise", _boom)
        with pytest.raises(ValueError, match="deployment build failed"):
            governance.publish_composition(session, oid=1, composition_id=comp.id)
        assert comp.lifecycle_status == "APPROVED"  # unchanged
        failed = [
            d for d in store.deployments if d.status == "ERROR"
        ]
        assert failed and "embedding down" in (failed[0].error or "")

    def test_unpublish_retires_deployment_and_index(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        store, comp = _simple_composition()
        session = store.session()
        ds_id = _seed_catalog(store)
        governance.bind_and_validate_composition(
            session, oid=1, composition_id=comp.id, datasource_id=ds_id
        )
        comp.lifecycle_status = "APPROVED"
        monkeypatch.setattr(governance, "build_embeddings_or_raise", lambda texts: None)
        governance.publish_composition(session, oid=1, composition_id=comp.id)
        governance.unpublish_composition(session, oid=1, composition_id=comp.id)
        assert comp.lifecycle_status == "RETIRED"
        assert comp.active_deployment_id is None
        assert all(d.status == "RETIRED" for d in store.deployments)
        assert all(r.active is False for r in store.index_rows)


class TestNodeMaintenance:
    def test_edit_node_marks_referencing_compositions_for_revalidate(self) -> None:
        package = _package(
            [
                _unit(
                    "onboarding",
                    [
                        _dataset(
                            "company",
                            "t_company",
                            [_field("id", "id"), _field("st", "status")],
                        )
                    ],
                ),
                _unit(
                    "signing",
                    [_dataset("c", "t_company", [_field("st", "status")])],
                ),
            ]
        )
        store, compositions = _seed(package)
        session = store.session()
        target = next(
            n
            for n in store.nodes
            if n.natural_key == "t_company.status"
        )
        for comp in compositions:
            comp.lifecycle_status = "PUBLISHED"
        result = governance.edit_node(
            session,
            oid=1,
            node_id=target.id,
            payload_patch={"description": "新的字段说明"},
        )
        assert result["changed"] is True
        affected_keys = {item["unit_key"] for item in result["affected_compositions"]}
        assert len(result["affected_compositions"]) == 2
        for comp in compositions:
            assert comp.validation_status == "NEEDS_REVALIDATE"

    def test_node_impact_lists_compositions_and_edges(self) -> None:
        store, comp = _simple_composition()
        session = store.session()
        target = next(n for n in store.nodes if n.natural_key == "t_company")
        impact = governance.node_impact(session, oid=1, node_id=target.id)
        assert len(impact["compositions"]) == 1
        assert impact["edge_counts"].get("has_field") == 1


class TestDrift:
    def test_drift_marks_referencing_composition(self) -> None:
        store, comp = _simple_composition()
        session = store.session()
        marked = governance.mark_compositions_stale_for_drift(
            session,
            oid=1,
            ds_id=9,
            changed_field_names=[("t_company", "id")],
            changed_table_names=[],
        )
        assert marked == 1
        assert comp.validation_status == "NEEDS_REVALIDATE"


class TestConflictQueue:
    def test_resolve_accept_claim_updates_node_and_marks_compositions(self) -> None:
        package = _package(
            [
                _unit(
                    "onboarding",
                    [_dataset("company", "t_company", [_field("id", "id")])],
                )
            ]
        )
        store, compositions = _seed(package)
        session = store.session()
        comp = compositions[0]
        comp.lifecycle_status = "PUBLISHED"
        node = next(n for n in store.nodes if n.natural_key == "t_company")
        store.conflicts.append(
            KnowledgeMergeConflict(
                id=500,
                oid=1,
                node_id=node.id,
                claim={
                    "new_payload": {"name": "t_company", "description": "新说明"},
                    "old_payload": {"name": "t_company"},
                },
                status="open",
                create_time=datetime.utcnow(),
                update_time=datetime.utcnow(),
            )
        )
        outcome = governance.resolve_merge_conflict(
            session, oid=1, conflict_id=500, action="accept_claim"
        )
        assert outcome["node_changed"] is True
        assert comp.validation_status == "NEEDS_REVALIDATE"
        assert store.conflicts[0].status == "resolved"
