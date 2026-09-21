from __future__ import annotations

from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock
from zipfile import ZipFile

import pytest
import yaml
from pydantic import ValidationError

from apps.knowledge.compile.compile import (
    _active_units,
    _relevance,
    compile_business_data_bundle,
    knowledge_prompt_payload,
    seed_revisions_for_turn,
)
from apps.knowledge.db_models import KnowledgeUnitRevision
from apps.knowledge.semantic.scanner import scan_package_files
from apps.knowledge.semantic.schema import (
    KnowledgePackageV2,
    KnowledgeUnitEntry,
    SemanticRelationship,
    VerifiedQueryPattern,
    validate_knowledge_unit,
)
from apps.knowledge.semantic.service import (
    _next_step,
    _retire_superseded_revisions,
    build_embeddings_or_raise,
    bind_and_validate,
    current_package_revisions,
    derive_package_status,
    join_type_severity,
    match_catalog_table,
    prepare_example_sql,
    publish_package,
    save_revision,
    unpublish_package,
    unpublish_revision,
    validation_preview,
)

_FIXTURE = (
    Path(__file__).resolve().parents[2]
    / ".tmp/docs/knowledge-extraction/knowledge-package-2.0.example.yaml"
)


def _package() -> dict:
    return {
        "schema_version": "2.0",
        "package": {
            "package_id": "enterprise-data",
            "revision": 1,
            "title": "企业数据知识",
            "namespace": "enterprise",
        },
        "sources": [{"source_id": "company-service", "kind": "source_code"}],
        "evidence": [
            {
                "evidence_id": "ev-company-status",
                "source_id": "company-service",
                "evidence_kind": "code_path",
                "locator": "CompanyService.java#build",
            }
        ],
        "knowledge_units": [
            {
                "unit_id": "enterprise-onboarding",
                "revision": 1,
                "title": "企业建档",
                "domain": "enterprise",
                "applicability": "企业主数据查询与建档统计",
                "description": "企业资料提交、审核并形成有效企业主数据的过程。",
                "content": {
                    "concepts": [],
                    "datasets": [
                        {
                            "dataset_id": "company",
                            "name": "cust_company_info",
                            "fields": [
                                {
                                    "field_id": "status",
                                    "name": "cust_status",
                                    "evidence_refs": ["ev-company-status"],
                                }
                            ],
                        }
                    ],
                    "processes": [
                        {
                            "stage_id": "approved",
                            "name": "审核通过",
                            "data_effects": [
                                {
                                    "operation": "update",
                                    "dataset": "company",
                                    "fields": ["status"],
                                    "evidence_refs": ["ev-company-status"],
                                }
                            ],
                        }
                    ],
                    "relationships": [],
                    "metrics": [],
                    "calibers": [],
                    "domain_rules": [],
                    "verified_query_patterns": [],
                },
                "evidence_refs": ["ev-company-status"],
                "confidence": 0.9,
            }
        ],
    }


def test_v2_accepts_scene_oriented_business_data_unit() -> None:
    package = KnowledgePackageV2.model_validate(_package())

    assert package.schema_version == "2.0"
    assert package.knowledge_units[0].content.processes[0].data_effects[0].fields == [
        "status"
    ]


def test_nested_evidence_reference_must_exist() -> None:
    payload = _package()
    payload["knowledge_units"][0]["content"]["datasets"][0]["fields"][0][
        "evidence_refs"
    ] = ["missing-evidence"]

    with pytest.raises(ValidationError, match="unknown evidence"):
        KnowledgePackageV2.model_validate(payload)


def test_process_data_effect_must_reference_real_field() -> None:
    payload = _package()
    payload["knowledge_units"][0]["content"]["processes"][0]["data_effects"][0][
        "fields"
    ] = ["invented_field"]

    with pytest.raises(ValidationError, match="unknown fields"):
        KnowledgePackageV2.model_validate(payload)


def test_governance_instruction_cannot_be_imported_as_domain_rule() -> None:
    payload = _package()
    payload["knowledge_units"][0]["content"]["domain_rules"] = [
        {
            "rule_id": "review-before-publish",
            "label": "发布前人工审核",
            "content": "知识发布前必须人工审核",
            "applicability": "知识治理",
            "query_impact": "无业务查询影响",
            "field_targets": [],
        }
    ]

    with pytest.raises(
        ValidationError, match="governance instructions are not knowledge"
    ):
        KnowledgePackageV2.model_validate(payload)


def test_zip_and_manifest_use_the_same_scanner() -> None:
    content = yaml.safe_dump(_package(), allow_unicode=True).encode()
    buffer = BytesIO()
    with ZipFile(buffer, "w") as archive:
        archive.writestr("enterprise/knowledge-package.yaml", content)

    package = scan_package_files([("enterprise.zip", buffer.getvalue())])

    assert package.package.package_id == "enterprise-data"


def test_directory_relative_path_finds_nested_manifest() -> None:
    content = yaml.safe_dump(_package(), allow_unicode=True).encode()

    package = scan_package_files(
        [
            ("system-knowledge-v3/README.md", b"# ignored"),
            ("system-knowledge-v3/knowledge-package.yaml", content),
        ]
    )

    assert package.package.package_id == "enterprise-data"


def test_manifest_units_split_assembles_to_same_package() -> None:
    inline = _package()
    unit_entry = inline["knowledge_units"][0]
    manifest = {key: value for key, value in inline.items() if key != "knowledge_units"}
    manifest["units"] = ["units/onboarding.yaml"]

    package = scan_package_files(
        [
            (
                "pkg/knowledge-package.yaml",
                yaml.safe_dump(manifest, allow_unicode=True).encode(),
            ),
            (
                "pkg/units/onboarding.yaml",
                yaml.safe_dump(unit_entry, allow_unicode=True).encode(),
            ),
        ]
    )

    assert package.package.package_id == "enterprise-data"
    assert len(package.knowledge_units) == 1
    assert package.knowledge_units[0].unit_id == "enterprise-onboarding"


def test_manifest_units_missing_file_raises() -> None:
    manifest = _package()
    manifest.pop("knowledge_units")
    manifest["units"] = ["units/missing.yaml"]

    with pytest.raises(ValueError, match="unit file not found"):
        scan_package_files(
            [
                (
                    "pkg/knowledge-package.yaml",
                    yaml.safe_dump(manifest, allow_unicode=True).encode(),
                )
            ]
        )


def test_manifest_cannot_mix_units_and_inline() -> None:
    manifest = _package()
    manifest["units"] = ["units/onboarding.yaml"]

    with pytest.raises(ValueError, match="cannot define both"):
        scan_package_files(
            [
                (
                    "pkg/knowledge-package.yaml",
                    yaml.safe_dump(manifest, allow_unicode=True).encode(),
                )
            ]
        )


def test_same_basename_manifests_keep_relative_paths_and_stay_ambiguous() -> None:
    content = yaml.safe_dump(_package(), allow_unicode=True).encode()

    with pytest.raises(ValueError, match="v2/knowledge-package.yaml"):
        scan_package_files(
            [
                ("v2/knowledge-package.yaml", content),
                ("v3/knowledge-package.yaml", content),
            ]
        )


def test_hidden_and_macos_paths_are_not_treated_as_package_documents() -> None:
    content = yaml.safe_dump(_package(), allow_unicode=True).encode()
    buffer = BytesIO()
    with ZipFile(buffer, "w") as archive:
        archive.writestr("__MACOSX/knowledge-package.yaml", b"not-a-package")
        archive.writestr("enterprise/knowledge-package.yaml", content)

    package = scan_package_files([("enterprise.zip", buffer.getvalue())])

    assert package.package.package_id == "enterprise-data"


def test_revision_edit_reuses_package_reference_closure_validation() -> None:
    entry = KnowledgeUnitEntry.model_validate(_package()["knowledge_units"][0])
    entry.content.processes[0].data_effects[0].fields = ["invented_field"]

    with pytest.raises(ValueError, match="unknown fields"):
        validate_knowledge_unit(entry, {"ev-company-status"})


def test_revision_edit_rejects_unknown_evidence() -> None:
    entry = KnowledgeUnitEntry.model_validate(_package()["knowledge_units"][0])
    entry.content.datasets[0].fields[0].evidence_refs = ["ev-unknown"]

    with pytest.raises(ValueError, match="unknown evidence"):
        validate_knowledge_unit(entry, {"ev-company-status"})


def test_projection_embeddings_are_atomic_when_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from apps.knowledge.semantic import service

    model = MagicMock()
    model.embed_documents.return_value = [[0.1, 0.2]]
    monkeypatch.setattr(service.settings, "EMBEDDING_ENABLED", True)
    monkeypatch.setattr(service.EmbeddingModelCache, "get_model", lambda: model)

    assert build_embeddings_or_raise(["企业建档"]) == [[0.1, 0.2]]


def test_projection_embeddings_reject_partial_runtime_index(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from apps.knowledge.semantic import service

    model = MagicMock()
    model.embed_documents.return_value = [[0.1]]
    monkeypatch.setattr(service.settings, "EMBEDDING_ENABLED", True)
    monkeypatch.setattr(service.EmbeddingModelCache, "get_model", lambda: model)

    with pytest.raises(ValueError, match="embedding build is incomplete"):
        build_embeddings_or_raise(["企业建档", "建档成功"])


def test_projection_embeddings_abort_provider_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from apps.knowledge.semantic import service

    model = MagicMock()
    model.embed_documents.side_effect = RuntimeError("403 Forbidden")
    monkeypatch.setattr(service.settings, "EMBEDDING_ENABLED", True)
    monkeypatch.setattr(service.EmbeddingModelCache, "get_model", lambda: model)

    with pytest.raises(ValueError, match="embedding build failed"):
        build_embeddings_or_raise(["企业建档"])


def test_derive_package_status_follows_unit_lifecycle() -> None:
    draft = SimpleNamespace(lifecycle_status="DRAFT")
    reviewing = SimpleNamespace(lifecycle_status="IN_REVIEW")
    approved = SimpleNamespace(lifecycle_status="APPROVED")
    published = SimpleNamespace(lifecycle_status="PUBLISHED")
    retired = SimpleNamespace(lifecycle_status="RETIRED")

    assert derive_package_status([]) == "REGISTERED"
    assert derive_package_status([draft]) == "REGISTERED"
    assert derive_package_status([reviewing, approved]) == "IN_REVIEW"
    assert derive_package_status([approved, published]) == "APPROVED"
    assert derive_package_status([published, published]) == "PUBLISHED"
    assert derive_package_status([retired, retired]) == "RETIRED"
    assert derive_package_status([published, retired]) == "PUBLISHED"
    assert derive_package_status([approved, retired]) == "APPROVED"


def test_semantic_recall_only_resolves_published_unit_locators(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from apps.knowledge.compile import compile as compiler

    monkeypatch.setattr(
        compiler,
        "select_terminology_by_word",
        lambda *_args, **_kwargs: [
            {"score": 0.99, "knowledge_meta": None},
            {
                "score": 0.88,
                "knowledge_meta": {"unit_revision_id": 42},
            },
            {
                "score": 0.91,
                "knowledge_meta": {"unit_revision_id": 42},
            },
        ],
    )

    assert compiler._semantic_unit_matches(  # noqa: SLF001
        MagicMock(), question="建档", oid=1, datasource_id=8
    ) == {42: 0.91}


def _fixture_package() -> KnowledgePackageV2:
    payload = yaml.safe_load(_FIXTURE.read_text(encoding="utf-8"))
    return KnowledgePackageV2.model_validate(payload)


def test_enterprise_onboarding_fixture_is_a_closed_scene_unit() -> None:
    package = _fixture_package()
    unit = package.knowledge_units[0]

    assert package.package.namespace == "customer"
    assert unit.unit_id == "enterprise-onboarding"
    assert unit.domain == "enterprise"
    assert "建档" in unit.aliases
    assert unit.content.concepts
    assert unit.content.processes
    assert {dataset.dataset_id for dataset in unit.content.datasets} >= {
        "company",
        "build_record",
        "project_rel",
    }
    open_status = next(
        field
        for dataset in unit.content.datasets
        if dataset.dataset_id == "project_rel"
        for field in dataset.fields
        if field.field_id == "open_status"
    )
    assert set(open_status.dictionary) == {"Y", "N", "P"}
    assert all(item.status == "proposed" for item in unit.content.relationships)
    assert unit.content.calibers
    query = unit.content.verified_query_patterns[0]
    assert query.verification == {}
    assert "executed" not in query.verification
    assert any("create_time" in str(item) for item in unit.conflicts)


def test_relationship_defaults_to_proposed() -> None:
    relation = SemanticRelationship.model_validate(
        {
            "relationship_id": "company-build-record",
            "left": {"dataset": "company", "field": "id"},
            "right": {"dataset": "build_record", "field": "company_id"},
        }
    )
    assert relation.status == "proposed"


def test_query_pattern_does_not_require_execution_proof() -> None:
    pattern = VerifiedQueryPattern.model_validate(
        {
            "pattern_id": "count-built",
            "question": "有效已建档企业有多少",
            "query": "SELECT 1",
        }
    )
    assert pattern.verification == {}


def test_next_step_matrix() -> None:
    draft = SimpleNamespace(lifecycle_status="DRAFT", validation_status="PASS")
    assert _next_step(draft, None) == "BIND_DATASOURCE"
    stale = SimpleNamespace(status="STALE")
    assert _next_step(draft, stale) == "REVALIDATE"
    bound = SimpleNamespace(status="BOUND")
    fail = SimpleNamespace(lifecycle_status="DRAFT", validation_status="FAIL")
    assert _next_step(fail, bound) == "REVIEW_ISSUES"
    published = SimpleNamespace(
        lifecycle_status="PUBLISHED", validation_status="WARNING"
    )
    assert _next_step(published, bound) == "VIEW_RUNTIME"
    retired = SimpleNamespace(lifecycle_status="RETIRED", validation_status="PASS")
    assert _next_step(retired, bound) == "REPUBLISH"


def test_missing_dataset_keeps_binding_bound(monkeypatch: pytest.MonkeyPatch) -> None:
    from apps.knowledge.semantic import service as svc

    entry = _fixture_package().knowledge_units[0]
    revision = SimpleNamespace(
        id=1,
        oid=1,
        content=entry.model_dump(mode="json"),
        validation_status="NOT_RUN",
        validation_summary={},
        update_time=None,
    )
    datasource = SimpleNamespace(id=8, oid=1)

    class _Result:
        def all(self) -> list[Any]:
            return []

        def one_or_none(self) -> None:
            return None

        def first(self) -> None:
            return None

    session = MagicMock()
    session.get.side_effect = (
        lambda model, _ident: revision if model is KnowledgeUnitRevision else datasource
    )
    session.exec.return_value = _Result()
    monkeypatch.setattr(
        svc,
        "get_protocol_for_ds",
        lambda _ds: SimpleNamespace(
            supports=lambda *_args, **_kwargs: False,
        ),
    )

    binding = bind_and_validate(
        session, oid=1, revision_id=1, datasource_id=8
    )

    assert binding.status == "BOUND"
    assert revision.validation_status == "FAIL"
    assert any(
        issue["code"] == "DATASET_NOT_FOUND"
        for issue in binding.validation_result["issues"]
    )




def test_non_referenced_missing_dataset_degrades_to_warning(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from apps.knowledge.semantic import service as svc
    from apps.knowledge.semantic.schema import KnowledgeUnitEntry

    entry = KnowledgeUnitEntry.model_validate(
        {
            "unit_id": "dormant-unit",
            "title": "休眠单元",
            "domain": "test",
            "description": "只声明休眠表，无维度引用",
            "content": {
                "datasets": [
                    {
                        "dataset_id": "dormant",
                        "name": "dormant_table",
                        "description": "休眠表",
                        "fields": [
                            {"field_id": "id", "name": "id", "data_type": "bigint"}
                        ],
                    }
                ],
                "processes": [{"stage_id": "s1", "name": "阶段1"}],
            },
        }
    )
    revision = SimpleNamespace(
        id=1,
        oid=1,
        content=entry.model_dump(mode="json"),
        validation_status="NOT_RUN",
        validation_summary={},
        update_time=None,
    )
    datasource = SimpleNamespace(id=8, oid=1)

    class _Result:
        def all(self) -> list[Any]:
            return []

        def one_or_none(self) -> None:
            return None

        def first(self) -> None:
            return None

    session = MagicMock()
    session.get.side_effect = (
        lambda model, _ident: revision if model is KnowledgeUnitRevision else datasource
    )
    session.exec.return_value = _Result()
    monkeypatch.setattr(
        svc,
        "get_protocol_for_ds",
        lambda _ds: SimpleNamespace(supports=lambda *_args, **_kwargs: False),
    )

    binding = bind_and_validate(session, oid=1, revision_id=1, datasource_id=8)

    assert binding.status == "BOUND"
    assert revision.validation_status == "WARNING"
    issue = next(
        i for i in binding.validation_result["issues"] if i["code"] == "DATASET_NOT_FOUND"
    )
    assert issue["severity"] == "warning"



def test_active_units_keep_stale_bindings() -> None:
    entry = _fixture_package().knowledge_units[0]
    onboarding = MagicMock(id=1, unit_key="enterprise-onboarding", oid=1)
    published = MagicMock(
        id=10,
        revision=1,
        lifecycle_status="PUBLISHED",
        content=entry.model_dump(mode="json"),
    )
    stale = MagicMock(status="STALE", mapping={}, datasource_id=8)
    session = MagicMock()
    session.exec.return_value.all.return_value = [
        (onboarding, published, MagicMock(status="ACTIVE"), stale),
    ]

    ranked = _active_units(
        session, oid=1, datasource_id=8, question="建档企业有多少"
    )

    assert len(ranked) == 1
    assert ranked[0][0].unit_key == "enterprise-onboarding"
    assert _relevance("建档企业有多少", entry) >= 1


def test_same_question_same_unit_order() -> None:
    entry = _fixture_package().knowledge_units[0]
    first = MagicMock(id=1, unit_key="alpha-unit", oid=1)
    second = MagicMock(id=2, unit_key="beta-unit", oid=1)
    content = entry.model_dump(mode="json")
    revision_a = MagicMock(id=10, revision=1, content=content)
    revision_b = MagicMock(id=11, revision=1, content=content)
    binding = MagicMock(status="BOUND", mapping={}, datasource_id=8)
    session = MagicMock()
    session.exec.return_value.all.return_value = [
        (second, revision_b, MagicMock(status="ACTIVE"), binding),
        (first, revision_a, MagicMock(status="ACTIVE"), binding),
    ]

    first_rank = [
        unit.unit_key
        for unit, _revision, _entry, _mapping in _active_units(
            session, oid=1, datasource_id=8, question="建档"
        )
    ]
    second_rank = [
        unit.unit_key
        for unit, _revision, _entry, _mapping in _active_units(
            session, oid=1, datasource_id=8, question="建档"
        )
    ]
    assert first_rank == second_rank == ["alpha-unit", "beta-unit"]


def test_revise_reuses_seed_revision_when_question_has_no_locator() -> None:
    entry = _fixture_package().knowledge_units[0]
    unit = MagicMock(id=1, unit_key="customer:enterprise-onboarding", oid=1)
    revision = MagicMock(
        id=10,
        revision=1,
        lifecycle_status="PUBLISHED",
        content=entry.model_dump(mode="json"),
    )
    binding = MagicMock(
        status="BOUND",
        mapping={
            "datasets": {
                "company": {"table_name": "cust_company_info"},
                "build_record": {"table_name": "cust_build_record"},
            }
        },
        datasource_id=8,
    )
    session = MagicMock()
    session.exec.return_value.all.return_value = [
        (unit, revision, MagicMock(status="ACTIVE"), binding),
    ]

    ranked = _active_units(
        session,
        oid=1,
        datasource_id=8,
        question="只统计今年的，按月",
        seed_revision_ids=[10],
        seed_policy="reuse",
    )
    assert len(ranked) == 1
    assert ranked[0][0].unit_key == "customer:enterprise-onboarding"


def test_continue_falls_back_to_seed_when_current_question_misses() -> None:
    entry = _fixture_package().knowledge_units[0]
    unit = MagicMock(id=1, unit_key="customer:enterprise-onboarding", oid=1)
    revision = MagicMock(
        id=10,
        revision=1,
        lifecycle_status="PUBLISHED",
        content=entry.model_dump(mode="json"),
    )
    binding = MagicMock(status="BOUND", mapping={}, datasource_id=8)
    session = MagicMock()
    session.exec.return_value.all.return_value = [
        (unit, revision, MagicMock(status="ACTIVE"), binding),
    ]

    ranked = _active_units(
        session,
        oid=1,
        datasource_id=8,
        question="只统计今年的，按月",
        seed_revision_ids=[10],
        seed_policy="fallback",
    )
    assert [item[0].unit_key for item in ranked] == [
        "customer:enterprise-onboarding"
    ]


def test_independent_does_not_use_seed_revisions() -> None:
    entry = _fixture_package().knowledge_units[0]
    unit = MagicMock(id=1, unit_key="customer:enterprise-onboarding", oid=1)
    revision = MagicMock(
        id=10,
        revision=1,
        lifecycle_status="PUBLISHED",
        content=entry.model_dump(mode="json"),
    )
    session = MagicMock()
    session.exec.return_value.all.return_value = [
        (unit, revision, MagicMock(status="ACTIVE"), MagicMock(status="BOUND", mapping={}, datasource_id=8)),
    ]

    ranked = _active_units(
        session,
        oid=1,
        datasource_id=8,
        question="只统计今年的，按月",
        seed_revision_ids=[10],
        seed_policy="none",
    )
    assert ranked == []


def test_seed_revisions_for_turn_splits_relation_policy() -> None:
    turns = [{"revision_ids": [10, 10, 0, "x"]}]
    assert seed_revisions_for_turn("revise", turns) == ([10], "reuse")
    assert seed_revisions_for_turn("continue", turns) == ([10], "fallback")
    assert seed_revisions_for_turn("independent", turns) == ([], "none")


def test_compile_keeps_caliber_floor_and_bound_tables(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entry = _fixture_package().knowledge_units[0]
    unit = MagicMock(id=3, unit_key="customer:enterprise-onboarding", oid=1)
    revision = MagicMock(
        id=5,
        revision=1,
        lifecycle_status="PUBLISHED",
        content=entry.model_dump(mode="json"),
    )
    binding = MagicMock(
        status="BOUND",
        mapping={
            "datasets": {
                "company": {"table_name": "cust_company_info"},
                "build_record": {"table_name": "cust_build_record"},
            }
        },
        datasource_id=8,
    )
    session = MagicMock()
    session.exec.return_value.all.return_value = [
        (unit, revision, MagicMock(status="ACTIVE"), binding),
    ]
    monkeypatch.setattr(
        "apps.knowledge.compile.compile.select_terminology_by_word",
        lambda *_a, **_k: [],
    )

    compiled = compile_business_data_bundle(
        session,
        stage="generate",
        question="只统计今年的，按月",
        oid=1,
        ds_id=8,
        include_matches=False,
        seed_revision_ids=[5],
        seed_policy="reuse",
    )

    assert compiled.bound_resources[:2] == ["cust_company_info", "cust_build_record"]
    assert compiled.calibers
    assert any(item.get("caliber_id") == "active-built-company" for item in compiled.calibers)
    assert compiled.rules
    payload = knowledge_prompt_payload(compiled)
    assert "bound_resources" not in payload
    assert "calibers" in payload
    assert "rules" in payload


def test_match_catalog_table_accepts_unqualified_mysql_catalog() -> None:
    table = SimpleNamespace(table_name="cust_company_info", database_name=None)
    matched = match_catalog_table(
        [table],  # type: ignore[list-item]
        table_name="cust_company_info",
        database_name="lowcode_pplatform",
    )
    assert matched is table


def test_save_revision_updates_draft_in_place(monkeypatch: pytest.MonkeyPatch) -> None:
    from apps.knowledge.semantic import service as svc

    entry = _fixture_package().knowledge_units[0]
    payload = entry.model_dump(mode="json")
    unit = SimpleNamespace(id=1, title="企业建档", domain="enterprise", update_time=None)
    base = SimpleNamespace(
        id=10,
        oid=1,
        unit_id=1,
        package_id=3,
        revision=1,
        lifecycle_status="DRAFT",
        content=payload,
        validation_status="FAIL",
        validation_summary={"issues": [{"code": "DATASET_NOT_FOUND"}]},
        confidence=0.9,
        update_time=None,
    )

    class _Result:
        def all(self) -> list[Any]:
            return [item.evidence_id for item in _fixture_package().evidence]

        def one_or_none(self) -> None:
            return None

        def first(self) -> None:
            return None

    session = MagicMock()
    session.exec.return_value = _Result()
    session.get.return_value = unit
    monkeypatch.setattr(
        svc,
        "get_unit_revision",
        lambda *_args, **_kwargs: (unit, base, [], []),
    )

    row, forked = save_revision(
        session,
        oid=1,
        unit_id=1,
        base_revision=1,
        content=payload,
        actor_user_id=1,
    )

    assert forked is False
    assert row.revision == 1
    assert row.lifecycle_status == "DRAFT"
    assert row.validation_status == "NOT_RUN"
    session.commit.assert_called()


def test_validation_preview_splits_failures_and_warnings() -> None:
    preview = validation_preview(
        {
            "summary": "mixed",
            "issues": [
                {"code": "DATASET_NOT_FOUND", "severity": "error"},
                {"code": "DATASET_NOT_FOUND"},
                {"code": "RELATIONSHIP_PROPOSED", "severity": "warning"},
                {"code": "QUERY_VALIDATION_FAILED", "severity": "warning"},
            ],
        }
    )

    assert preview["validation_error_count"] == 2
    assert preview["validation_warning_count"] == 2
    assert preview["validation_issue_count"] == 4
    assert len(preview["validation_issues"]) == 4


def test_current_package_revisions_ignore_retired_and_keep_latest() -> None:
    unit_a = SimpleNamespace(id=1, domain="enterprise", title="A-企业建档")
    unit_b = SimpleNamespace(id=2, domain="enterprise", title="B-企业关联租户项目")
    retired = SimpleNamespace(id=11, revision=1, lifecycle_status="RETIRED")
    current_a = SimpleNamespace(id=12, revision=2, lifecycle_status="DRAFT")
    current_b = SimpleNamespace(id=21, revision=1, lifecycle_status="DRAFT")

    class _Result:
        def all(self) -> list[Any]:
            return [
                (retired, unit_a),
                (current_a, unit_a),
                (current_b, unit_b),
            ]

    session = MagicMock()
    session.exec.return_value = _Result()

    rows = current_package_revisions(session, package_row_id=9)

    assert [(item[1].id, item[0].id, item[0].revision) for item in rows] == [
        (1, 12, 2),
        (2, 21, 1),
    ]


def test_current_package_revisions_keep_unpublished_latest() -> None:
    unit = SimpleNamespace(id=1, domain="enterprise", title="企业建档")
    superseded = SimpleNamespace(id=11, revision=1, lifecycle_status="RETIRED")
    unpublished = SimpleNamespace(id=12, revision=2, lifecycle_status="RETIRED")

    class _Result:
        def all(self) -> list[Any]:
            return [(superseded, unit), (unpublished, unit)]

    session = MagicMock()
    session.exec.return_value = _Result()

    rows = current_package_revisions(session, package_row_id=9)

    assert len(rows) == 1
    assert rows[0][0].id == 12
    assert rows[0][0].lifecycle_status == "RETIRED"


def test_unpublish_revision_clears_active_runtime(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from apps.knowledge.semantic import service as svc

    revision = SimpleNamespace(
        id=12, oid=1, unit_id=3, lifecycle_status="PUBLISHED", update_time=None
    )
    unit = SimpleNamespace(id=3, active_revision_id=12, update_time=None)
    session = MagicMock()
    session.get.side_effect = (
        lambda model, ident: revision if model is KnowledgeUnitRevision else unit
    )
    monkeypatch.setattr(svc, "_retire_active_deployments", lambda *_args, **_kwargs: None)

    result = unpublish_revision(session, oid=1, revision_id=12)

    assert result.lifecycle_status == "RETIRED"
    assert unit.active_revision_id is None
    session.commit.assert_called()


def test_unpublish_revision_rejects_non_published() -> None:
    revision = SimpleNamespace(id=12, oid=1, lifecycle_status="APPROVED")
    session = MagicMock()
    session.get.return_value = revision
    with pytest.raises(ValueError, match="only published"):
        unpublish_revision(session, oid=1, revision_id=12)


def test_publish_package_republishes_retired_units(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from apps.knowledge.semantic import service as svc

    retired = SimpleNamespace(id=1, lifecycle_status="RETIRED")
    published = SimpleNamespace(id=2, lifecycle_status="PUBLISHED")
    monkeypatch.setattr(
        svc,
        "current_package_revisions",
        lambda *_args, **_kwargs: [
            (retired, SimpleNamespace()),
            (published, SimpleNamespace()),
        ],
    )
    monkeypatch.setattr(
        svc,
        "publish_revision",
        lambda *_args, **_kwargs: SimpleNamespace(id=99),
    )

    assert publish_package(MagicMock(), oid=1, package_row_id=9) == [99]


def test_unpublish_package_targets_published_units(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from apps.knowledge.semantic import service as svc

    retired = SimpleNamespace(id=1, lifecycle_status="RETIRED")
    published = SimpleNamespace(id=2, lifecycle_status="PUBLISHED")
    monkeypatch.setattr(
        svc,
        "current_package_revisions",
        lambda *_args, **_kwargs: [
            (retired, SimpleNamespace()),
            (published, SimpleNamespace()),
        ],
    )
    monkeypatch.setattr(
        svc,
        "unpublish_revision",
        lambda *_args, **_kwargs: SimpleNamespace(id=2, lifecycle_status="RETIRED"),
    )

    assert unpublish_package(MagicMock(), oid=1, package_row_id=9) == [2]


def test_retire_superseded_marks_old_revision_retired() -> None:
    old = SimpleNamespace(id=1, lifecycle_status="DRAFT", update_time=None)

    class _Result:
        def __init__(self, rows: list[Any]) -> None:
            self._rows = rows

        def all(self) -> list[Any]:
            return self._rows

    session = MagicMock()
    session.exec.side_effect = [_Result([old]), _Result([])]

    _retire_superseded_revisions(session, unit_id=1, keep_revision_id=2)

    assert old.lifecycle_status == "RETIRED"
    session.add.assert_called()


def test_submit_package_review_rejects_failed_current_units(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from apps.knowledge.semantic import service as svc

    package = SimpleNamespace(id=9, oid=1, status="REGISTERED", update_time=None)
    unit = SimpleNamespace(title="企业建档", unit_key="enterprise-onboarding")
    revision = SimpleNamespace(
        id=12, lifecycle_status="DRAFT", validation_status="FAIL"
    )
    session = MagicMock()
    session.get.return_value = package
    monkeypatch.setattr(
        svc,
        "current_package_revisions",
        lambda *_args, **_kwargs: [(revision, unit)],
    )

    with pytest.raises(ValueError, match="validation is FAIL"):
        svc.submit_package_review(session, oid=1, package_row_id=9, actor_user_id=1)


def test_join_type_severity_treats_string_number_as_warning() -> None:
    assert join_type_severity("varchar", "bigint") == "warning"
    assert join_type_severity("bigint", "varchar(64)") == "warning"
    assert join_type_severity("varchar", "text") is None
    assert join_type_severity("date", "boolean") == "error"


def test_prepare_example_sql_replaces_named_parameters() -> None:
    sql = "SELECT id FROM tenant_project WHERE id = :project_id AND CAST(id AS CHAR) = :code"
    prepared = prepare_example_sql(sql)
    assert ":project_id" not in prepared
    assert ":code" not in prepared
    assert "CAST(id AS CHAR)" in prepared
    assert "'1'" in prepared


