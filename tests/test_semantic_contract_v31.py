from __future__ import annotations

import importlib.util
import pathlib
from typing import Any

import pytest
from pydantic import ValidationError

from apps.knowledge.semantic.lint import lint_package
from apps.knowledge.semantic.schema import (
    KnowledgePackageV2,
    validate_knowledge_unit,
)

_SCRIPTS = pathlib.Path(__file__).resolve().parents[1] / "scripts"


def _load_bridge():
    spec = importlib.util.spec_from_file_location(
        "infer_concept_anchors", _SCRIPTS / "infer_concept_anchors.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _unit(**overrides: Any) -> dict[str, Any]:
    content: dict[str, Any] = {
        "concepts": [],
        "processes": [],
        "datasets": [
            {
                "dataset_id": "company",
                "name": "cust_company_info",
                "fields": [
                    {"field_id": "id", "name": "id"},
                    {
                        "field_id": "build_status",
                        "name": "cust_build_status",
                        "dictionary": {
                            "BUILD_SUCCESS": "认证成功",
                            "BUILD_FAIL": "认证失败",
                        },
                    },
                ],
            }
        ],
        "relationships": [],
        "metrics": [
            {
                "metric_id": "company-count",
                "name": "企业数",
                "aggregation": "COUNT_DISTINCT",
                "field": {"dataset": "company", "field": "id"},
            }
        ],
        "calibers": [],
        "domain_rules": [],
        "verified_query_patterns": [],
    }
    unit: dict[str, Any] = {
        "unit_id": "enterprise-onboarding",
        "revision": 1,
        "title": "企业建档",
        "domain": "enterprise",
        "description": "建档过程。",
        "content": content,
        "evidence_refs": ["ev-status"],
    }
    unit.update(overrides)
    return unit


def _package(*, units: list[dict[str, Any]] | None = None, **overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": "2.0",
        "package": {
            "package_id": "demo",
            "revision": 1,
            "title": "demo",
            "namespace": "demo",
        },
        "sources": [{"source_id": "src", "kind": "source_code"}],
        "evidence": [
            {
                "evidence_id": "ev-status",
                "source_id": "src",
                "evidence_kind": "code_path",
                "locator": "X.java",
            }
        ],
        "knowledge_units": units if units is not None else [_unit()],
    }
    payload.update(overrides)
    return payload


class TestConceptFieldTargets:
    def test_concept_field_targets_accepted(self) -> None:
        unit = _unit()
        unit["content"]["concepts"] = [
            {
                "concept_id": "build-success",
                "name": "建档成功",
                "definition": "认证成功。",
                "field_targets": [{"dataset": "company", "field": "build_status"}],
            }
        ]
        package = KnowledgePackageV2.model_validate(_package(units=[unit]))
        assert package.knowledge_units[0].content.concepts[0].field_targets[
            0
        ].field == "build_status"

    def test_concept_field_targets_unknown_dataset_rejected(self) -> None:
        unit = _unit()
        unit["content"]["concepts"] = [
            {
                "concept_id": "build-success",
                "name": "建档成功",
                "definition": "认证成功。",
                "field_targets": [{"dataset": "nope", "field": "build_status"}],
            }
        ]
        with pytest.raises(ValidationError, match="unknown dataset"):
            KnowledgePackageV2.model_validate(_package(units=[unit]))

    def test_concept_field_targets_unknown_field_rejected(self) -> None:
        unit = _unit()
        unit["content"]["concepts"] = [
            {
                "concept_id": "build-success",
                "name": "建档成功",
                "definition": "认证成功。",
                "field_targets": [{"dataset": "company", "field": "nope"}],
            }
        ]
        with pytest.raises(ValidationError, match="unknown field"):
            KnowledgePackageV2.model_validate(_package(units=[unit]))


class TestPackageRelationships:
    def test_relationships_accepted_without_unit_closure(self) -> None:
        # Physical endpoints are allowed to reference tables no unit declares.
        payload = _package(
            relationships=[
                {
                    "left_table": "authorization_agreement",
                    "left_field": "cust_id",
                    "right_table": "cust_company_info",
                    "right_field": "id",
                    "evidence": "write-flow:X.java",
                }
            ]
        )
        package = KnowledgePackageV2.model_validate(payload)
        assert package.relationships[0].left_table == "authorization_agreement"

    def test_relationship_requires_both_sides(self) -> None:
        with pytest.raises(ValidationError):
            KnowledgePackageV2.model_validate(
                _package(relationships=[{"left_table": "a", "left_field": "b"}])
            )


class TestUnitLinks:
    def _linked_package(self, link: dict[str, Any]) -> dict[str, Any]:
        signing = _unit()
        signing["unit_id"] = "company-product-auth"
        signing["content"]["datasets"] = [
            {
                "dataset_id": "company",
                "name": "cust_company_info",
                "fields": [{"field_id": "build_status", "name": "cust_build_status"}],
            }
        ]
        signing["content"]["metrics"] = [
            {
                "metric_id": "signed-count",
                "name": "签约数",
                "aggregation": "COUNT",
                "field": {"dataset": "company", "field": "build_status"},
            }
        ]
        signing["unit_links"] = [link]
        return _package(units=[_unit(), signing])

    def test_unit_link_accepted(self) -> None:
        payload = self._linked_package(
            {
                "target_unit": "enterprise-onboarding",
                "kind": "prerequisite",
                "via": [{"dataset": "company", "field": "build_status"}],
                "evidence_refs": ["ev-status"],
            }
        )
        package = KnowledgePackageV2.model_validate(payload)
        assert package.knowledge_units[1].unit_links[0].kind == "prerequisite"

    def test_unknown_target_unit_rejected(self) -> None:
        payload = self._linked_package(
            {
                "target_unit": "nope",
                "kind": "validates",
                "via": [],
                "evidence_refs": ["ev-status"],
            }
        )
        with pytest.raises(ValidationError, match="unknown unit"):
            KnowledgePackageV2.model_validate(payload)

    def test_self_link_rejected(self) -> None:
        link = {
            "target_unit": "company-product-auth",
            "kind": "prerequisite",
            "via": [],
            "evidence_refs": ["ev-status"],
        }
        with pytest.raises(ValidationError, match="links to itself"):
            KnowledgePackageV2.model_validate(self._linked_package(link))

    def test_via_unknown_dataset_rejected(self) -> None:
        payload = self._linked_package(
            {
                "target_unit": "enterprise-onboarding",
                "kind": "prerequisite",
                "via": [{"dataset": "nope", "field": "build_status"}],
                "evidence_refs": ["ev-status"],
            }
        )
        with pytest.raises(ValidationError, match="unknown dataset"):
            KnowledgePackageV2.model_validate(payload)

    def test_unknown_evidence_ref_rejected(self) -> None:
        payload = self._linked_package(
            {
                "target_unit": "enterprise-onboarding",
                "kind": "prerequisite",
                "via": [],
                "evidence_refs": ["ev-missing"],
            }
        )
        with pytest.raises(ValidationError, match="unknown evidence"):
            KnowledgePackageV2.model_validate(payload)


class TestNewLintRules:
    def _package_model(self, **overrides: Any) -> KnowledgePackageV2:
        return KnowledgePackageV2.model_validate(_package(**overrides))

    def test_concept_unanchored(self) -> None:
        unit = _unit()
        unit["content"]["concepts"] = [
            {"concept_id": "build-success", "name": "建档成功", "definition": "x"}
        ]
        report = lint_package(self._package_model(units=[unit]))
        assert any(
            issue["code"] == "CONCEPT_UNANCHORED" for issue in report["issues"]
        )

    def test_unit_link_unjustified(self) -> None:
        signing = _unit()
        signing["unit_id"] = "company-product-auth"
        signing["unit_links"] = [
            {
                "target_unit": "enterprise-onboarding",
                "kind": "prerequisite",
                "via": [],
                "evidence_refs": [],
            }
        ]
        report = lint_package(self._package_model(units=[_unit(), signing]))
        assert any(
            issue["code"] == "UNIT_LINK_UNJUSTIFIED" for issue in report["issues"]
        )

    def test_field_declaration_orphan(self) -> None:
        # build_status is declared but nothing references it: orphan.
        report = lint_package(self._package_model())
        assert any(
            issue["code"] == "FIELD_DECLARATION_ORPHAN"
            and "company.build_status" in issue["message"]
            for issue in report["issues"]
        )

    def test_field_declaration_referenced_not_orphan(self) -> None:
        unit = _unit()
        unit["content"]["concepts"] = [
            {
                "concept_id": "build-success",
                "name": "建档成功",
                "definition": "x",
                "field_targets": [{"dataset": "company", "field": "build_status"}],
            }
        ]
        report = lint_package(self._package_model(units=[unit]))
        assert not any(
            issue["code"] == "FIELD_DECLARATION_ORPHAN"
            for issue in report["issues"]
        )

    def test_package_relationship_lints(self) -> None:
        report = lint_package(
            self._package_model(
                relationships=[
                    {
                        "left_table": "undeclared_table",
                        "left_field": "x",
                        "right_table": "cust_company_info",
                        "right_field": "id",
                    }
                ]
            )
        )
        codes = {issue["code"] for issue in report["issues"]}
        assert "RELATION_UNJUSTIFIED" in codes
        assert "RELATION_UNDECLARED_ENDPOINT" in codes

    def test_no_new_rules_fired_on_clean_unit(self) -> None:
        unit = _unit()
        unit["content"]["concepts"] = [
            {
                "concept_id": "build-success",
                "name": "建档成功",
                "definition": "x",
                "field_targets": [{"dataset": "company", "field": "build_status"}],
            }
        ]
        report = lint_package(self._package_model(units=[unit]))
        new_codes = {
            "CONCEPT_UNANCHORED",
            "UNIT_LINK_UNJUSTIFIED",
            "FIELD_DECLARATION_ORPHAN",
            "RELATION_UNDECLARED_ENDPOINT",
        }
        assert not new_codes & {issue["code"] for issue in report["issues"]}


class TestBridgeInference:
    @pytest.fixture()
    def bridge(self):
        return _load_bridge()

    def test_dictionary_partition_spans_two_fields(self, bridge) -> None:
        concept = {
            "concept_id": "building",
            "name": "建档中",
            "dictionary": {
                "CUST_BUILDING": "审核中",
                "CUST_CHECK_INIT": "待运营审核",
            },
        }
        datasets = [
            {
                "dataset_id": "company",
                "name": "cust_company_info",
                "fields": [
                    {"field_id": "build_status", "name": "cust_build_status", "dictionary": {"CUST_BUILDING": "审核中"}},
                    {"field_id": "check_status", "name": "check_status", "dictionary": {"CUST_CHECK_INIT": "待审核"}},
                ],
            }
        ]
        anchor = bridge.infer_anchor(concept, datasets)
        assert anchor is not None
        targets, reason = anchor
        assert reason == "dictionary-key-partition"
        assert {(t["dataset"], t["field"]) for t in targets} == {
            ("company", "build_status"),
            ("company", "check_status"),
        }

    def test_value_mention_anchors_status_field(self, bridge) -> None:
        concept = {
            "concept_id": "onboarding",
            "name": "建档",
            "dictionary": {},
        }
        datasets = [
            {
                "dataset_id": "company",
                "name": "cust_company_info",
                "fields": [
                    {"field_id": "build_status", "name": "cust_build_status", "dictionary": {"TO_BE_BUILD": "未建档", "BUILDING": "建档中"}},
                    {"field_id": "enabled", "name": "enable", "dictionary": {"Y": "启用"}},
                ],
            }
        ]
        anchor = bridge.infer_anchor(concept, datasets)
        assert anchor is not None
        targets, reason = anchor
        assert reason == "dictionary-value-mention"
        assert targets == [{"dataset": "company", "field": "build_status"}]

    def test_dataset_token_match_anchors_entity_concept(self, bridge) -> None:
        concept = {"concept_id": "shareholder", "name": "股东出资", "dictionary": {}}
        datasets = [
            {
                "dataset_id": "company",
                "name": "cust_company_info",
                "fields": [{"field_id": "id", "name": "id"}],
            },
            {
                "dataset_id": "shareholder",
                "name": "cust_shareholder_info",
                "fields": [{"field_id": "id", "name": "id"}],
            },
        ]
        anchor = bridge.infer_anchor(concept, datasets)
        assert anchor is not None
        targets, reason = anchor
        assert reason == "dataset-token-match"
        assert targets == [{"dataset": "shareholder", "field": "id"}]

    def test_annotate_unit_writes_field_targets(self, bridge) -> None:
        unit = {
            "unit_id": "u1",
            "content": {
                "concepts": [
                    {"concept_id": "c1", "name": "建档", "dictionary": {}}
                ],
                "datasets": [
                    {
                        "dataset_id": "company",
                        "name": "cust_company_info",
                        "fields": [
                            {"field_id": "build_status", "name": "cust_build_status", "dictionary": {"BUILDING": "建档中"}}
                        ],
                    }
                ],
            },
        }
        report = bridge.annotate_unit(unit)
        assert report[0]["status"] == "anchored"
        assert unit["content"]["concepts"][0]["field_targets"] == [
            {"dataset": "company", "field": "build_status"}
        ]

    def test_annotated_concept_passes_contract_validation(self, bridge) -> None:
        # The bridge output must remain contract-valid: rerun the unit
        # through the package validator after annotation.
        unit = _unit()
        unit["content"]["concepts"] = [
            {
                "concept_id": "build-success",
                "name": "建档成功",
                "definition": "x",
                "dictionary": {"BUILD_SUCCESS": "认证成功"},
            }
        ]
        bridge.annotate_unit(unit)
        assert unit["content"]["concepts"][0].get("field_targets")
        package = KnowledgePackageV2.model_validate(_package(units=[unit]))
        entry = package.knowledge_units[0]
        validate_knowledge_unit(entry, {"ev-status"})
