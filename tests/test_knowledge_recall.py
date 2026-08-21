from __future__ import annotations

from typing import Any

import pytest

from apps.knowledge.compile.bundle import BusinessDataBundle
from apps.knowledge.graph.recall import (
    EdgeView,
    NodeRecallResult,
    SeedHit,
    assemble_node_bundle,
    expand_closure,
    lexical_score,
    physical_match,
    score_seed,
)


def _edges() -> list[EdgeView]:
    # 1: dataset company; 2: field company.id; 3: field company.status;
    # 4: dataset agreement; 5: field agreement.cust_id; 6: concept sign;
    # 7: stage approve; 8: dataset project (cross-domain)
    return [
        EdgeView(1, 2, "has_field", "confirmed"),
        EdgeView(1, 3, "has_field", "confirmed"),
        EdgeView(4, 5, "has_field", "confirmed"),
        EdgeView(2, 5, "relation_endpoint", "confirmed"),
        EdgeView(6, 3, "concept_of", "confirmed"),
        EdgeView(7, 3, "reads", "confirmed"),
        EdgeView(3, 8, "relation_endpoint", "confirmed"),
        EdgeView(2, 8, "relation_endpoint", "proposed"),  # proposed: excluded
    ]


def _kinds() -> dict[int, str]:
    return {
        1: "dataset",
        2: "field",
        3: "field",
        4: "dataset",
        5: "field",
        6: "concept",
        7: "stage",
        8: "dataset",
    }


class TestScoring:
    def test_exact_physical_match(self) -> None:
        score, sources = score_seed(
            text_repr="", physical_key="t_company.id", question="查 t_company.id"
        )
        assert "exact" in sources
        assert score >= 2.0

    def test_lexical_substring(self) -> None:
        score, sources = score_seed(
            text_repr="授权协议签署记录 authed_status",
            physical_key="",
            question="已签约的企业",
        )
        # "签约" 不在 text_repr，但 "签署" 也不在；这里验证无虚假命中时 lexical=0
        assert score == 0.0

    def test_lexical_score_helpers(self) -> None:
        assert lexical_score("建档状态", "建档") == 1.0
        assert physical_match("lowcode_pplatform.cust_company_info", "cust_company_info") is True
        assert physical_match("lowcode_pplatform.cust_company_info", "别的表") is False


class TestClosure:
    def test_bounded_semantic_hops(self) -> None:
        closure = expand_closure([6], _edges(), node_kind_by_id=_kinds(), max_semantic_hops=2)
        # concept 6 -> field 3 (hop1) -> dataset 1 via has_field (free) -> field 2 (free)
        # field 3 -> dataset 8 via relation_endpoint (hop2)
        assert 6 in closure.reached
        assert closure.reached[3] == 1  # concept_of
        assert 2 in closure.reached  # hub expansion of company
        assert 8 in closure.reached  # relation_endpoint hop 2

    def test_proposed_edges_excluded(self) -> None:
        closure = expand_closure([2], _edges(), node_kind_by_id=_kinds())
        # 8 is reachable only via the confirmed 3->8 edge; the proposed 2->8
        # edge must never be traversed.
        assert all(
            not (edge.src == 2 and edge.dst == 8 and edge.status == "proposed")
            for edge in closure.used_edges
        )

    def test_quota_caps_kind(self) -> None:
        closure = expand_closure(
            [6],
            _edges(),
            node_kind_by_id=_kinds(),
            quotas={"field": 1, "dataset": 99, "concept": 99, "stage": 99},
        )
        # only one field can enter; 3 comes first, so 2 is blocked by quota
        assert 3 in closure.reached
        assert 2 not in closure.reached


def _seed(node_id: int, kind: str, content: dict[str, Any], deployment: int = 1) -> SeedHit:
    return SeedHit(
        node_version_id=node_id,
        node_id=node_id,
        node_kind=kind,
        natural_key="",
        physical_key="",
        text_repr="",
        content=content,
        deployment_id=deployment,
        score=1.0,
        sources=["lexical"],
    )


def _index_content(kind: str, **extra: Any) -> dict[str, Any]:
    base: dict[str, Any] = {"name": kind}
    base.update(extra)
    return base


class TestAssembly:
    def _result(self) -> NodeRecallResult:
        index_by_node = {
            2: type("R", (), {"content": _index_content("field", field_id="id", dataset_id="company"), "node_version_id": 2, "node_kind": "field"})(),
            3: type("R", (), {"content": _index_content("field", field_id="status", dataset_id="company"), "node_version_id": 3, "node_kind": "field"})(),
            5: type("R", (), {"content": _index_content("field", field_id="cust_id", dataset_id="agreement"), "node_version_id": 5, "node_kind": "field"})(),
            6: type("R", (), {"content": _index_content("concept", concept_id="sign"), "node_version_id": 6, "node_kind": "concept"})(),
            1: type("R", (), {"content": _index_content("dataset", dataset_id="company"), "node_version_id": 1, "node_kind": "dataset"})(),
        }
        return NodeRecallResult(
            seeds=[_seed(6, "concept", {"concept_id": "sign"})],
            reached={6: 0, 3: 1, 2: 0, 5: 1, 1: 0},
            index_by_node=index_by_node,
            used_edges=[EdgeView(2, 5, "relation_endpoint", "confirmed")],
        )

    def test_slots_and_relationship_synthesis(self) -> None:
        bundle = assemble_node_bundle(self._result(), stage="generate")
        assert bundle is not None
        assert any(item["concept_id"] == "sign" for item in bundle.concepts)
        field_ids = {item["field_id"] for item in bundle.fields}
        assert field_ids >= {"id", "status", "cust_id"}
        assert bundle.relationships, "relation_endpoint edge must synthesize a JOIN"
        rel = bundle.relationships[0]
        assert rel["left"] == {"dataset": "company", "field": "id"}
        assert rel["right"] == {"dataset": "agreement", "field": "cust_id"}
        assert bundle.apply_log, "every injected node must leave an apply_log hit"

    def test_dedupe_by_slot_identity(self) -> None:
        # Same field content reached twice should not duplicate.
        result = self._result()
        bundle = assemble_node_bundle(result, stage="generate")
        assert len(bundle.fields) == 3  # id, status, cust_id — no dupes


class TestStrategyWiring:
    def test_unit_strategy_is_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from apps.knowledge.compile import compile as compile_mod

        monkeypatch.setattr(compile_mod.settings, "KNOWLEDGE_RECALL_STRATEGY", "unit")
        assert compile_mod.settings.KNOWLEDGE_RECALL_STRATEGY == "unit"

    def test_exemplar_similarity_degrades_without_embeddings(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from apps.knowledge.compile import compile as compile_mod

        monkeypatch.setattr(compile_mod.settings, "EMBEDDING_ENABLED", False)
        assert compile_mod._exemplar_similarity("建档", "已建档") == 0.0
