from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from apps.datasource.profiling.models import (  # noqa: E402
    RelationStatus,
)
from apps.datasource.profiling.relation_candidates import (  # noqa: E402
    admit_relation_candidate,
)
from apps.knowledge.importing.scanner import (  # noqa: E402
    load_knowledge_package,
    normalize_item,
    scan_knowledge_documents,
    scan_knowledge_payload,
)
from apps.knowledge.importing.schema import (  # noqa: E402
    EvidencePackageItem,
    ExamplePackageItem,
    KnowledgePackage,
)
from apps.knowledge.importing.service import (  # noqa: E402
    apply_knowledge_package,
    preview_knowledge_package,
)


def test_scanner_infers_all_runtime_and_evidence_kinds() -> None:
    payload = [
        {"item_id": "t", "word": "建档", "description": "企业建档过程"},
        {
            "item_id": "c",
            "label": "有效企业",
            "contract_fragment": {
                "version": 3,
                "requirements": [
                    {
                        "clause": "predicate",
                        "requirement_id": "enabled",
                        "business_label": "启用记录",
                        "field": {"resource": "company", "field": "enable"},
                        "operator": "eq",
                        "values": ["Y"],
                    }
                ],
            },
        },
        {"item_id": "r", "left": "company.id", "right": "person.company_id"},
        {"item_id": "q", "question": "查询企业", "sql": "select * from company"},
        {"item_id": "c-rule", "label": "不可混用", "content": "处理成功不等于审核成功"},
        {"item_id": "f", "subject": "建档", "predicate": "updates", "object": "状态"},
    ]

    package = scan_knowledge_payload(payload, package_id="mixed")

    assert [item.kind for item in package.items] == [
        "terminology",
        "caliber",
        "relation",
        "example",
        "rule",
        "evidence",
    ]


def test_legacy_scan_retains_untyped_caliber_as_reviewable_draft() -> None:
    package = scan_knowledge_payload(
        {
            "k3_terminology_candidates": [
                {
                    "candidate_id": "TERM-1",
                    "term": "建档",
                    "description": "企业建档过程",
                    "status": "needs_review",
                }
            ],
            "k2_caliber_candidates": [
                {
                    "candidate_id": "CAL-BAD",
                    "label": "旧口径",
                    "requirements": ["enable='Y'"],
                }
            ],
        },
        package_id="legacy",
    )

    assert [item.item_id for item in package.items] == ["TERM-1", "CAL-BAD"]
    assert package.items[1].kind == "caliber"
    assert package.items[1].status == "candidate"
    assert package.items[1].contract_fragment == {}  # type: ignore[union-attr]


def test_generated_item_identity_is_stable() -> None:
    record = {"word": "建档", "description": "企业建档过程"}
    first = normalize_item(record)
    second = normalize_item(dict(record))

    assert first.item_id == second.item_id
    assert first.item_id.startswith("auto-terminology-")


def test_scanner_accepts_yaml_document_text() -> None:
    package = scan_knowledge_payload(
        """
        schema_version: '1.0'
        package_id: yaml-package
        items:
          - kind: terminology
            item_id: term-1
            word: 建档
            description: 企业建档过程
        """
    )

    assert package.package_id == "yaml-package"
    assert package.items[0].kind == "terminology"


def test_canonical_package_rejects_duplicate_item_ids() -> None:
    with pytest.raises(ValueError, match="item_id must be unique"):
        KnowledgePackage.model_validate(
            {
                "schema_version": "1.0",
                "package_id": "duplicates",
                "items": [
                    {
                        "kind": "terminology",
                        "item_id": "same",
                        "word": "A",
                        "description": "A",
                    },
                    {
                        "kind": "terminology",
                        "item_id": "same",
                        "word": "B",
                        "description": "B",
                    },
                ],
            }
        )


def test_unverified_example_is_not_ready_for_import(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    item = ExamplePackageItem(
        item_id="query-1",
        question="查询企业",
        query="select * from company",
    )
    package = KnowledgePackage(package_id="examples", items=[item])
    monkeypatch.setattr(
        "apps.knowledge.importing.service._resolve_datasource",
        lambda *_args, **_kwargs: SimpleNamespace(id=8),
    )

    report = preview_knowledge_package(MagicMock(), oid=1, package=package)

    assert report.readiness_counts == {"review_required": 1}
    assert "executed and passed" in report.items[0].messages[0]


def test_relation_candidate_preserves_reviewer_decision() -> None:
    existing = SimpleNamespace(
        id=9,
        status=RelationStatus.CONFIRMED.value,
        source_field_id=1,
        target_field_id=2,
    )
    fields = {
        1: SimpleNamespace(id=1, ds_id=8, table_id=11),
        2: SimpleNamespace(id=2, ds_id=8, table_id=12),
    }
    session = MagicMock()
    session.get.side_effect = lambda _model, field_id: fields[field_id]
    session.exec.return_value.first.return_value = existing

    row, action = admit_relation_candidate(
        session,
        oid=1,
        ds_id=8,
        source_field_id=1,
        target_field_id=2,
        source="package",
    )

    assert row is existing
    assert action == "kept_confirmed"
    session.add.assert_not_called()


def test_directory_and_canonical_package_have_the_same_complete_inventory() -> None:
    directory = (
        ROOT
        / "docs"
        / "knowledge-extraction"
        / "pplatform-web"
        / "enterprise-onboarding-v1"
    )

    folder_package = load_knowledge_package(directory)
    file_package = load_knowledge_package(directory / "knowledge-package.yaml")

    expected = {
        "terminology": 4,
        "caliber": 3,
        "relation": 7,
        "example": 3,
        "rule": 2,
        "evidence": 32,
    }
    assert len(folder_package.items) == 51
    assert len(file_package.items) == 51
    assert {
        kind: sum(item.kind == kind for item in folder_package.items)
        for kind in expected
    } == expected
    assert [item.item_id for item in folder_package.items] == [
        item.item_id for item in file_package.items
    ]
    assert folder_package.description


def test_multi_document_scan_prefers_canonical_item_and_keeps_extra_items() -> None:
    canonical = """
    schema_version: '1.0'
    package_id: canonical
    title: Canonical
    items:
      - kind: terminology
        item_id: term-1
        status: reviewed
        word: 建档
        description: 规范定义
    """
    legacy = """
    k3_terminology_candidates:
      - candidate_id: term-1
        term: 建档
        description: 旧定义
      - candidate_id: term-2
        term: 生效企业
        description: 企业状态已经生效
    """

    package = scan_knowledge_documents(
        [("knowledge-package.yaml", canonical), ("asset-candidates.yaml", legacy)]
    )

    assert package.package_id == "canonical"
    assert [item.item_id for item in package.items] == ["term-1", "term-2"]
    assert package.items[0].description == "规范定义"  # type: ignore[union-attr]


def test_review_only_package_is_registered_even_without_runtime_projection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package = KnowledgePackage(
        package_id="review-only",
        items=[
            EvidencePackageItem(
                item_id="fact-1",
                subject="建档",
                predicate="updates",
                value="企业状态",
            )
        ],
    )
    registry = SimpleNamespace(id=7, revision=1)
    register = MagicMock(return_value=(registry, "registered"))
    record = MagicMock()
    monkeypatch.setattr(
        "apps.knowledge.importing.service.register_knowledge_package", register
    )
    monkeypatch.setattr(
        "apps.knowledge.importing.service.record_package_runtime_results", record
    )
    session = MagicMock()

    report = apply_knowledge_package(
        session,
        oid=1,
        actor_user_id=2,
        package=package,
        trans=lambda value: value,
    )

    register.assert_called_once()
    record.assert_called_once()
    assert report.total == 1
    assert report.items[0].action == "skipped"
    assert report.items[0].readiness == "retained_only"


def test_apply_rejects_input_changed_after_preview(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package = KnowledgePackage(
        package_id="preview-guard",
        items=[
            EvidencePackageItem(
                item_id="fact-1",
                subject="建档",
                predicate="updates",
                value="企业状态",
            )
        ],
    )
    register = MagicMock()
    monkeypatch.setattr(
        "apps.knowledge.importing.service.register_knowledge_package", register
    )

    with pytest.raises(ValueError, match="changed after preview"):
        apply_knowledge_package(
            MagicMock(),
            oid=1,
            actor_user_id=2,
            package=package,
            trans=lambda value: value,
            expected_preview_fingerprint="stale-preview",
        )

    register.assert_not_called()


def test_apply_accepts_the_exact_preview_fingerprint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package = KnowledgePackage(
        package_id="preview-guard",
        items=[
            EvidencePackageItem(
                item_id="fact-1",
                subject="建档",
                predicate="updates",
                value="企业状态",
            )
        ],
    )
    session = MagicMock()
    preview = preview_knowledge_package(session, oid=1, package=package)
    registry = SimpleNamespace(id=7, revision=1)
    register = MagicMock(return_value=(registry, "registered"))
    monkeypatch.setattr(
        "apps.knowledge.importing.service.register_knowledge_package", register
    )
    monkeypatch.setattr(
        "apps.knowledge.importing.service.record_package_runtime_results", MagicMock()
    )

    report = apply_knowledge_package(
        session,
        oid=1,
        actor_user_id=2,
        package=package,
        trans=lambda value: value,
        expected_preview_fingerprint=preview.package_fingerprint,
    )

    assert report.package_fingerprint == preview.package_fingerprint
    register.assert_called_once()
