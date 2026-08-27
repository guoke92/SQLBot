"""Clarify-resume top-up: evidence → resolver → manifest (deterministic chain)."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.steps import recall_topup as rt  # noqa: E402
from apps.datasource.recall.value_index import ValueHit  # noqa: E402


def _catalog_entry(name: str, table_id: int) -> rt._CatalogTable:
    return rt._CatalogTable(table_id=table_id, name=name, comment="")


def _service() -> SimpleNamespace:
    return SimpleNamespace(
        table_name_list=["d_task", "d_project"],
        ds=SimpleNamespace(id=8),
    )


def _wire(monkeypatch, value_hits, catalog) -> None:
    monkeypatch.setattr(rt, "_catalog", lambda session, *, ds_id: catalog)
    monkeypatch.setattr(rt, "_match_knowledge_units", lambda *args, **kwargs: [])
    monkeypatch.setattr(rt, "_relation_neighbors", lambda *args, **kwargs: [])
    monkeypatch.setattr(rt, "match_values", lambda *args, **kwargs: value_hits)


def test_option_answer_names_table_structurally(monkeypatch) -> None:
    """v1 三选一答案直接点名 d_project.organization_id — 无需任何索引即命中."""
    catalog = {
        "d_task": _catalog_entry("d_task", 1),
        "d_project": _catalog_entry("d_project", 2),
        "d_organization": _catalog_entry("d_organization", 3),
    }
    _wire(monkeypatch, [], catalog)
    evidence = [
        SimpleNamespace(
            kind="clarification_option",
            content="团队 organization_id",
            structured_value={
                "question_id": "q1",
                "option_id": "o1",
                "table": "d_project",
                "fields": [{"name": "organization_id", "table": "d_project"}],
            },
        )
    ]

    signals = rt.signals_from_evidence(evidence)
    manifest = rt.resolve_recall_topup(object(), _service(), signals, oid=1)

    # d_project 已在工作集，结构化信号不再重复添加；无新增
    assert "d_project" not in manifest.tables
    assert manifest.has_additions is False


def test_custom_answer_value_hits_missing_table(monkeypatch) -> None:
    """v2 自定义答案"你自行查找研发二部对应的组织id" — 值索引补齐组织表."""
    catalog = {
        "d_task": _catalog_entry("d_task", 1),
        "d_project": _catalog_entry("d_project", 2),
        "d_organization": _catalog_entry("d_organization", 3),
    }
    hits = [
        ValueHit(
            table_name="d_organization",
            field_name="organization_name",
            value="研发二部",
            source="profile",
            matched_text="研发二部",
        )
    ]
    _wire(monkeypatch, hits, catalog)
    evidence = [
        SimpleNamespace(
            kind="clarification_custom",
            content="你自行查找研发二部对应的组织id",
            structured_value={"question_id": "q2"},
        )
    ]

    signals = rt.signals_from_evidence(evidence)
    manifest = rt.resolve_recall_topup(object(), _service(), signals, oid=1)

    assert manifest.tables == ("d_organization",)
    assert manifest.value_hits[0]["value"] == "研发二部"


def test_correction_carries_both_table_and_text_signals(monkeypatch) -> None:
    catalog = {
        "d_task": _catalog_entry("d_task", 1),
        "d_organization": _catalog_entry("d_organization", 3),
    }
    _wire(monkeypatch, [], catalog)
    evidence = [
        SimpleNamespace(
            kind="user_correction",
            content="应该是研发一部",
            structured_value={
                "fields": [{"name": "org", "table": "d_organization"}],
                "supersedes": "e1",
            },
        )
    ]

    signals = rt.signals_from_evidence(evidence)
    assert "应该是研发一部" in signals.evidence_texts

    manifest = rt.resolve_recall_topup(object(), _service(), signals, oid=1)
    assert manifest.tables == ("d_organization",)


def test_access_scope_fences_structured_table_claims(monkeypatch) -> None:
    from apps.datasource.access import AccessScope

    catalog = {
        "d_task": _catalog_entry("d_task", 1),
        "d_organization": _catalog_entry("d_organization", 3),
    }
    _wire(monkeypatch, [], catalog)
    evidence = [
        SimpleNamespace(
            kind="clarification_option",
            content="组织表",
            structured_value={"table": "d_organization"},
        )
    ]
    scope = AccessScope(resource_names=("d_task",))

    signals = rt.signals_from_evidence(evidence)
    manifest = rt.resolve_recall_topup(
        object(), _service(), signals, oid=1, access_scope=scope
    )
    # 无权限的表不进工作集（证据仍留在账本，但被 AccessScope 拦截）
    assert manifest.tables == ()
