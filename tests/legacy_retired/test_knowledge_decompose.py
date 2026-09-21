from __future__ import annotations

import pathlib
from typing import Any
from unittest.mock import MagicMock

import pytest

from apps.knowledge.graph.decompose import (
    DecompositionPlan,
    assemble_entry,
    fidelity_hash,
    persist_plan,
    plan_decomposition,
)
from apps.knowledge.graph.identity import dataset_key, field_key
from apps.knowledge.graph.models import (
    KnowledgeEdge,
    KnowledgeMergeConflict,
    KnowledgeNode,
    KnowledgeNodeVersion,
    UnitComposition,
)
from apps.knowledge.semantic.schema import KnowledgePackageV2

_V4_DIR = (
    pathlib.Path(__file__).resolve().parents[2]
    / ".tmp/docs/knowledge-extraction/pplatform-web/system-knowledge-v4"
)


def _dataset(dataset_id: str, name: str, fields: list[dict], **extra: Any) -> dict:
    return {"dataset_id": dataset_id, "name": name, "fields": fields, **extra}


def _field(field_id: str, name: str, **extra: Any) -> dict:
    return {"field_id": field_id, "name": name, **extra}


def _package(units: list[dict[str, Any]], **extra: Any) -> KnowledgePackageV2:
    payload: dict[str, Any] = {
        "schema_version": "2.0",
        "package": {
            "package_id": "demo",
            "revision": 1,
            "title": "demo",
            "namespace": "pp",
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
    payload.update(extra)
    return KnowledgePackageV2.model_validate(payload)


def _unit(
    unit_id: str,
    datasets: list[dict],
    *,
    concepts: list[dict] | None = None,
    processes: list[dict] | None = None,
    unit_links: list[dict] | None = None,
) -> dict[str, Any]:
    return {
        "unit_id": unit_id,
        "revision": 1,
        "title": f"{unit_id}-title",
        "domain": "enterprise",
        "description": "desc",
        "content": {
            "concepts": concepts or [],
            "processes": processes or [],
            "datasets": datasets,
            "relationships": [],
            "metrics": [
                {
                    "metric_id": "default-count",
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
        "unit_links": unit_links or [],
    }


def _bridge_concepts_in_memory(package: KnowledgePackageV2) -> None:
    """Run the anchor bridge on a scanned package model (no file writes)."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "infer_concept_anchors",
        pathlib.Path(__file__).resolve().parents[1]
        / "scripts"
        / "infer_concept_anchors.py",
    )
    bridge = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bridge)
    from apps.knowledge.semantic.schema import SemanticFieldRef

    for unit in package.knowledge_units:
        datasets = [ds.model_dump(mode="json") for ds in unit.content.datasets]
        for concept in unit.content.concepts:
            if concept.field_targets:
                continue
            anchor = bridge.infer_anchor(concept.model_dump(mode="json"), datasets)
            if anchor is None:
                continue
            targets, _reason = anchor
            concept.field_targets = [
                SemanticFieldRef(dataset=t["dataset"], field=t["field"])
                for t in targets
            ]


class TestRoundTripFidelity:
    def test_single_unit_round_trips_exactly(self) -> None:
        unit = _unit(
            "onboarding",
            [
                _dataset(
                    "company",
                    "cust_company_info",
                    [
                        _field("id", "id"),
                        _field(
                            "build_status",
                            "cust_build_status",
                            description="建档状态",
                            dictionary={"Y": "是"},
                            evidence_refs=["ev-1"],
                        ),
                    ],
                    database="db1",
                    description="企业主数据",
                    evidence_refs=["ev-1"],
                )
            ],
            concepts=[
                {
                    "concept_id": "onboarding",
                    "name": "建档",
                    "definition": "建档过程",
                    "field_targets": [{"dataset": "company", "field": "build_status"}],
                }
            ],
            processes=[
                {
                    "stage_id": "submit",
                    "name": "提交",
                    "data_effects": [
                        {
                            "operation": "update",
                            "dataset": "company",
                            "fields": ["build_status"],
                            "evidence_refs": ["ev-1"],
                        }
                    ],
                }
            ],
        )
        package = _package([unit])
        plan = plan_decomposition(package)
        comp = plan.compositions[0]
        rebuilt = assemble_entry(plan, comp)
        original = package.knowledge_units[0].model_dump(mode="json")
        assert fidelity_hash(original) == fidelity_hash(rebuilt)

    def test_shared_table_identical_declarations_merge_and_round_trip(self) -> None:
        fields = [
            _field("id", "id"),
            _field("code", "code", description="企业业务键"),
        ]
        unit_a = _unit(
            "onboarding",
            [_dataset("company", "cust_company_info", fields, database="db1")],
        )
        # second unit redeclares the same physical table identically
        unit_b = _unit(
            "signing",
            [_dataset("enterprise", "cust_company_info", fields, database="db1")],
        )
        package = _package([unit_a, unit_b])
        plan = plan_decomposition(package)
        key = dataset_key("db1", "cust_company_info")
        assert plan.stats["dataset_declarations"][key] == 2
        assert plan.stats["nodes_by_kind"]["dataset"] == 1
        for unit, comp in zip(package.knowledge_units, plan.compositions):
            original = unit.model_dump(mode="json")
            rebuilt = assemble_entry(plan, comp)
            assert fidelity_hash(original) == fidelity_hash(rebuilt)

    def test_dictionary_superset_is_enrichment_not_conflict(self) -> None:
        thin = [_field("status", "status", dictionary={"Y": "启用"})]
        rich = [_field("flag", "status", dictionary={"Y": "启用", "N": "停用"})]
        unit_a = _unit(
            "onboarding", [_dataset("t", "shared_table", thin, database="db1")]
        )
        unit_b = _unit("signing", [_dataset("s", "shared_table", rich, database="db1")])
        plan = plan_decomposition(_package([unit_a, unit_b]))
        assert len(plan.enrichments) == 1
        assert not plan.merge_conflicts
        node = plan.nodes[field_key(dataset_key("db1", "shared_table"), "status")]
        assert node.payload["dictionary"] == {"Y": "启用", "N": "停用"}

    def test_divergent_claims_record_conflict_with_diff_keys(self) -> None:
        a = [_field("code", "code", description="业务键甲")]
        b = [_field("code", "code", description="业务键乙")]
        unit_a = _unit("onboarding", [_dataset("t", "shared_table", a, database="db1")])
        unit_b = _unit("signing", [_dataset("s", "shared_table", b, database="db1")])
        plan = plan_decomposition(_package([unit_a, unit_b]))
        assert len(plan.merge_conflicts) == 1
        conflict = plan.merge_conflicts[0]
        assert conflict["node_kind"] == "field"
        assert conflict["diff_keys"] == ["description"]
        assert conflict["node_key"] == field_key(
            dataset_key("db1", "shared_table"), "code"
        )


class TestEdgeGeneration:
    def test_concept_reads_writes_relation_edges(self) -> None:
        unit = _unit(
            "onboarding",
            [
                _dataset(
                    "company", "t_company", [_field("id", "id"), _field("st", "status")]
                ),
                _dataset("rec", "t_record", [_field("cid", "company_id")]),
            ],
            concepts=[
                {
                    "concept_id": "c1",
                    "name": "状态",
                    "definition": "d",
                    "field_targets": [{"dataset": "company", "field": "st"}],
                }
            ],
            processes=[
                {
                    "stage_id": "s1",
                    "name": "阶段一",
                    "next_stages": ["s2"],
                    "data_effects": [
                        {"operation": "read", "dataset": "company", "fields": ["st"]},
                        {"operation": "insert", "dataset": "rec", "fields": ["cid"]},
                    ],
                },
                {"stage_id": "s2", "name": "阶段二"},
            ],
        )
        unit["content"]["relationships"] = [
            {
                "relationship_id": "r1",
                "left": {"dataset": "rec", "field": "cid"},
                "right": {"dataset": "company", "field": "id"},
            }
        ]
        plan = plan_decomposition(_package([unit]))
        by_kind = plan.stats["edges_by_kind"]
        assert by_kind["concept_of"] == 1
        assert by_kind["reads"] == 1
        assert by_kind["writes"] == 1
        assert by_kind["precedes"] == 1
        assert by_kind["relation_endpoint"] == 1
        assert by_kind["has_field"] == 3

    def test_package_relationships_create_stub_nodes(self) -> None:
        unit = _unit(
            "onboarding",
            [_dataset("company", "t_company", [_field("id", "id")])],
        )
        package = _package(
            [unit],
            relationships=[
                {
                    "left_table": "t_other",
                    "left_field": "oid",
                    "right_table": "t_company",
                    "right_field": "id",
                    "evidence": "write-flow:X.java",
                }
            ],
        )
        plan = plan_decomposition(package)
        assert plan.stats["stub_nodes"] == 2  # stub dataset + stub field
        stub_field = plan.nodes[field_key("t_other", "oid")]
        assert stub_field.stub is True
        edges = [e for e in plan.edges if e.edge_kind == "relation_endpoint"]
        assert len(edges) == 1
        assert edges[0].status == "proposed"

    def test_shared_key_package_relationship_emits_no_join_edge(self) -> None:
        unit = _unit(
            "onboarding",
            [_dataset("company", "t_company", [_field("id", "id")])],
        )
        package = _package(
            [unit],
            relationships=[
                {
                    "left_table": "t_cert",
                    "left_field": "ref_cust_company_info",
                    "right_table": "t_account",
                    "right_field": "ref_cust_company_info",
                    "evidence": "write-flow:X.java",
                    "relationship_type": "SHARED_KEY",
                }
            ],
        )
        plan = plan_decomposition(package)
        join_edges = [e for e in plan.edges if e.edge_kind == "relation_endpoint"]
        assert join_edges == []
        assert plan.stats["stub_nodes"] == 0

    def test_shared_key_unit_relationship_emits_no_join_edge(self) -> None:
        unit = _unit(
            "onboarding",
            [
                _dataset("company", "t_company", [_field("id", "id")]),
                _dataset("acct", "t_account", [_field("ref", "ref_cust_company_info")]),
            ],
        )
        unit["content"]["relationships"] = [
            {
                "relationship_id": "r1",
                "left": {"dataset": "company", "field": "id"},
                "right": {"dataset": "acct", "field": "ref"},
                "relationship_type": "SHARED_KEY",
            }
        ]
        plan = plan_decomposition(_package([unit]))
        join_edges = [e for e in plan.edges if e.edge_kind == "relation_endpoint"]
        assert join_edges == []

    def test_unit_links_derive_cross_unit_edges(self) -> None:
        target = _unit(
            "onboarding",
            [
                _dataset(
                    "company",
                    "t_company",
                    [_field("st", "build_status")],
                    database="db1",
                )
            ],
            processes=[
                {
                    "stage_id": "approve",
                    "name": "审核通过",
                    "data_effects": [
                        {"operation": "update", "dataset": "company", "fields": ["st"]}
                    ],
                }
            ],
        )
        declaring = _unit(
            "signing",
            [
                _dataset(
                    "company",
                    "t_company",
                    [_field("st", "build_status")],
                    database="db1",
                )
            ],
            processes=[
                {
                    "stage_id": "sign",
                    "name": "签署",
                    "data_effects": [
                        {"operation": "read", "dataset": "company", "fields": ["st"]}
                    ],
                }
            ],
            unit_links=[
                {
                    "target_unit": "onboarding",
                    "kind": "prerequisite",
                    "via": [{"dataset": "company", "field": "st"}],
                    "evidence_refs": ["ev-1"],
                }
            ],
        )
        plan = plan_decomposition(_package([target, declaring]))
        cross = [
            e
            for e in plan.edges
            if e.edge_kind == "precedes" and e.status == "proposed"
        ]
        assert len(cross) == 1
        assert cross[0].src_key.endswith("signing:sign")
        assert cross[0].dst_key.endswith("onboarding:approve")

    def test_bare_table_declaration_merges_with_qualified_key(self) -> None:
        unit_a = _unit(
            "onboarding",
            [_dataset("company", "t_company", [_field("id", "id")], database="db1")],
        )
        unit_b = _unit(
            "signing",
            [_dataset("c", "t_company", [_field("id", "id")])],
        )
        plan = plan_decomposition(_package([unit_a, unit_b]))
        assert plan.stats["nodes_by_kind"]["dataset"] == 1
        assert dataset_key("db1", "t_company") in plan.nodes


class _ExecResult:
    def __init__(self, items: list[Any]) -> None:
        self._items = items

    def all(self) -> list[Any]:
        return list(self._items)

    def first(self) -> Any:
        return self._items[0] if self._items else None


class _FakeStore:
    """Dispatch exec() by selected entity, keeping per-entity row lists."""

    def __init__(self) -> None:
        self.nodes: list[KnowledgeNode] = []
        self.versions: list[KnowledgeNodeVersion] = []
        self.edges: list[KnowledgeEdge] = []
        self.compositions: list[UnitComposition] = []
        self.conflicts: list[KnowledgeMergeConflict] = []
        self.added: list[Any] = []

    def exec(self, stmt: Any) -> _ExecResult:
        entity = stmt.column_descriptions[0]["entity"]
        if entity is KnowledgeNode:
            return _ExecResult(self.nodes)
        if entity is KnowledgeNodeVersion:
            return _ExecResult(self.versions)
        if entity is KnowledgeEdge:
            return _ExecResult(self.edges)
        if entity is UnitComposition:
            return _ExecResult(self.compositions)
        return _ExecResult([])

    def flush(self) -> None:
        for index, obj in enumerate(self.added):
            if getattr(obj, "id", None) is None:
                obj.id = index + 1

    def session(self) -> MagicMock:
        session = MagicMock()
        session.exec.side_effect = self.exec
        session.flush.side_effect = self.flush
        session.add.side_effect = self.added.append
        return session


def _seed_store_from_plan(store: _FakeStore, plan: DecompositionPlan) -> None:
    for index, (key, draft) in enumerate(sorted(plan.nodes.items()), start=1):
        node = KnowledgeNode(
            id=index,
            oid=1,
            node_kind=draft.node_kind,
            natural_key=draft.natural_key,
            namespace=draft.namespace,
            current_version_id=index,
            create_time=__import__("datetime").datetime.utcnow(),
            update_time=__import__("datetime").datetime.utcnow(),
        )
        version = KnowledgeNodeVersion(
            id=index,
            node_id=index,
            version=1,
            payload=dict(draft.payload),
            evidence_refs=list(draft.evidence_refs),
            confidence=draft.confidence,
            content_hash=draft.content_hash,
            stub=draft.stub,
            origin_package_id=7,
        )
        store.nodes.append(node)
        store.versions.append(version)


class TestPersistPlan:
    def _simple_plan(self) -> DecompositionPlan:
        unit = _unit(
            "onboarding",
            [_dataset("company", "t_company", [_field("id", "id")])],
        )
        return plan_decomposition(_package([unit]))

    def test_fresh_persist_creates_nodes_edges_compositions(self) -> None:
        store = _FakeStore()
        session = store.session()
        plan = self._simple_plan()
        report = persist_plan(session, oid=1, plan=plan, package_row_id=7)
        assert report.created_nodes == len(plan.nodes)
        assert report.created_edges == len(plan.edges)
        assert report.upserted_compositions == 1
        node_objs = [o for o in store.added if isinstance(o, KnowledgeNode)]
        assert len({id(obj) for obj in node_objs}) == len(plan.nodes)
        assert any(isinstance(o, UnitComposition) for o in store.added)

    def test_idempotent_rerun_is_unchanged(self) -> None:
        plan = self._simple_plan()
        store = _FakeStore()
        _seed_store_from_plan(store, plan)
        session = store.session()
        report = persist_plan(session, oid=1, plan=plan, package_row_id=7)
        assert report.unchanged_nodes == len(plan.nodes)
        assert report.created_nodes == 0
        assert report.updated_nodes == 0
        assert report.conflicts_queued == 0

    def test_divergent_dictionary_from_other_package_queues_conflict(self) -> None:
        from apps.knowledge.graph.decompose import _json_hash

        plan = self._simple_plan()
        store = _FakeStore()
        _seed_store_from_plan(store, plan)
        # Diverge the stored field payload AND its hash (persist compares hashes).
        node = next(n for n in store.nodes if n.natural_key == "t_company.id")
        version = next(v for v in store.versions if v.node_id == node.id)
        diverged = {**version.payload, "dictionary": {"X": "旧"}}
        version.payload = diverged
        version.content_hash = _json_hash(
            {"kind": node.node_kind, "key": node.natural_key, "payload": diverged}
        )
        session = store.session()
        report = persist_plan(session, oid=1, plan=plan, package_row_id=99)
        assert report.updated_nodes >= 1
        assert report.conflicts_queued == 1


class TestV4RealPackage:
    """P1 acceptance against the real v4 extraction package."""

    @pytest.fixture()
    def v4_package(self) -> KnowledgePackageV2:
        docs = [
            (str(p.relative_to(_V4_DIR)), p.read_text(encoding="utf-8"))
            for p in sorted(_V4_DIR.rglob("*"))
            if p.is_file() and p.suffix in (".yaml", ".yml", ".json", ".jsonl")
        ]
        from apps.knowledge.semantic.scanner import scan_package_documents

        package = scan_package_documents(docs)
        _bridge_concepts_in_memory(package)
        return package

    @pytest.fixture()
    def v4_plan(self, v4_package) -> DecompositionPlan:
        return plan_decomposition(v4_package)

    def test_company_table_merges_to_one_node(self, v4_plan) -> None:
        key = dataset_key("lowcode_pplatform", "cust_company_info")
        assert v4_plan.stats["dataset_declarations"][key] == 13
        assert key in v4_plan.nodes

    def test_concept_of_edges_generated(self, v4_plan) -> None:
        assert v4_plan.stats["edges_by_kind"].get("concept_of", 0) >= 44

    def test_round_trip_diffs_fully_explained(self, v4_plan, v4_package) -> None:
        package = v4_package
        explained = {c["node_key"] for c in v4_plan.merge_conflicts} | {
            e["node_key"] for e in v4_plan.enrichments
        }
        exact = 0

        def _semantic(payload: dict) -> dict:
            # evidence_refs is provenance and legitimately differs across units;
            # the shared node is the single truth for everything else.
            return {k: v for k, v in payload.items() if k != "evidence_refs"}

        for unit, comp in zip(package.knowledge_units, v4_plan.compositions):
            original = unit.model_dump(mode="json")
            rebuilt = assemble_entry(v4_plan, comp)
            if fidelity_hash(original) == fidelity_hash(rebuilt):
                exact += 1
                continue
            for od, rd in zip(
                original["content"]["datasets"], rebuilt["content"]["datasets"]
            ):
                if _semantic(od) != _semantic(rd):
                    dk = dataset_key(od.get("database", ""), od["name"])
                    assert dk in explained
                    for of, rf in zip(od.get("fields", []), rd.get("fields", [])):
                        if _semantic(of) != _semantic(rf):
                            assert field_key(dk, of["name"]) in explained
        assert exact >= 1  # at least one unit reproduces byte-for-byte
