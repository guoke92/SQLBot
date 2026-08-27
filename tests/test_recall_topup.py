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


def _catalog_entry(name: str, comment: str = "", table_id: int = 1) -> rt._CatalogTable:
    return rt._CatalogTable(table_id=table_id, name=name, comment=comment)


def _service(tables: list[str]) -> SimpleNamespace:
    return SimpleNamespace(
        table_name_list=list(tables),
        record=SimpleNamespace(id=1),
        current_user=None,
        ds=SimpleNamespace(id=8),
        out_ds_instance=None,
        retrieval_question="q",
        protocol=None,
        chat_question=SimpleNamespace(db_schema="old", sample_data=""),
    )


def test_signals_from_evidence_projects_structured_and_text() -> None:
    option = SimpleNamespace(
        kind="clarification_option",
        content="团队 organization_id",
        structured_value={
            "table": "d_project",
            "fields": [
                {"name": "organization_id", "table": "d_project"},
                {"name": "create_time", "table": "d_task"},
            ],
        },
    )
    custom = SimpleNamespace(
        kind="clarification_custom",
        content="你自行查找研发二部对应的组织id",
        structured_value={"question_id": "q2"},
    )
    correction = SimpleNamespace(
        kind="user_correction",
        content="改成研发一部",
        structured_value={"fields": [{"name": "org", "table": "d_organization"}]},
    )
    unrelated = SimpleNamespace(
        kind="prior_question",
        content="历史问题",
        structured_value={},
    )

    signals = rt.signals_from_evidence([option, custom, correction, unrelated])

    assert signals.evidence_tables == ("d_project", "d_task", "d_organization")
    assert "你自行查找研发二部对应的组织id" in signals.evidence_texts
    assert "改成研发一部" in signals.evidence_texts
    assert "历史问题" not in signals.evidence_texts


def test_topup_allowlist_gate(monkeypatch) -> None:
    from common.core.config import settings

    monkeypatch.setattr(settings, "RECALL_TOUP_ENABLED", True)
    monkeypatch.setattr(settings, "RECALL_TOUP_DS_ALLOWLIST", "")
    assert rt.topup_enabled_for(8) is True

    monkeypatch.setattr(settings, "RECALL_TOUP_DS_ALLOWLIST", "1, 9")
    assert rt.topup_enabled_for(9) is True
    assert rt.topup_enabled_for(8) is False
    assert rt.topup_enabled_for(None) is True  # 无 ds 上下文不拦截

    monkeypatch.setattr(settings, "RECALL_TOUP_ENABLED", False)
    assert rt.topup_enabled_for(9) is False


def test_resolver_unions_value_hits_and_relations(monkeypatch) -> None:
    service = _service(["d_task", "d_project"])
    catalog = {
        "d_task": _catalog_entry("d_task", table_id=1),
        "d_project": _catalog_entry("d_project", "项目", table_id=2),
        "d_organization": _catalog_entry("d_organization", "机构/组织", table_id=3),
    }
    monkeypatch.setattr(rt, "_catalog", lambda session, *, ds_id: catalog)
    monkeypatch.setattr(rt, "_match_knowledge_units", lambda *args, **kwargs: [])
    monkeypatch.setattr(
        rt,
        "_relation_neighbors",
        lambda session, *, ds_id, anchor_table_ids, catalog, working_set: [
            {
                "table": "d_user",
                "table_id": 9,
                "reason": "relation-neighbor",
                "status": "CONFIRMED",
            }
        ],
    )
    monkeypatch.setattr(
        rt,
        "match_values",
        lambda session, text, *, oid, ds_id, allowed_tables=None: [
            ValueHit(
                table_name="d_organization",
                field_name="organization_name",
                value="研发二部",
                source="profile",
                matched_text="研发二部",
            )
        ],
    )

    manifest = rt.resolve_recall_topup(
        object(),
        service,
        rt.TopupSignals(question_text="研发二部每月task数"),
        oid=1,
        access_scope=None,
    )

    assert manifest.tables == ("d_organization",)
    assert manifest.value_hits[0]["field"] == "organization_name"
    assert manifest.advisory_tables[0]["table"] == "d_user"
    assert manifest.misses == ()


def test_resolver_reports_misses_for_unmatched_concepts(monkeypatch) -> None:
    service = _service(["d_task"])
    catalog = {"d_task": _catalog_entry("d_task", table_id=1)}
    monkeypatch.setattr(rt, "_catalog", lambda session, *, ds_id: catalog)
    monkeypatch.setattr(rt, "_match_knowledge_units", lambda *args, **kwargs: [])
    monkeypatch.setattr(rt, "_relation_neighbors", lambda *args, **kwargs: [])
    monkeypatch.setattr(rt, "match_values", lambda *args, **kwargs: [])

    manifest = rt.resolve_recall_topup(
        object(),
        service,
        rt.TopupSignals(question_text="x", missing_concepts=("卫星遥感数据",)),
        oid=1,
    )
    assert manifest.tables == ()
    assert manifest.misses == ("卫星遥感数据",)
    assert manifest.has_additions is False


def test_fulfill_expands_working_set_via_exact_projection(monkeypatch) -> None:
    monkeypatch.setattr(
        rt,
        "log_span",
        lambda **kwargs: SimpleNamespace(
            __enter__=lambda self: SimpleNamespace(
                set_detail=lambda *a, **k: None,
                set_summary=lambda *a, **k: None,
                mark_degraded=lambda *a, **k: None,
            ),
            __exit__=lambda *a: False,
        ),
    )
    protocol_calls: list[list[str]] = []

    def fake_retrieve_schema(**kwargs):
        names = list(kwargs["resource_names"])
        protocol_calls.append(names)
        return SimpleNamespace(
            schema_text="SCHEMA " + ",".join(names),
            resource_names=names,
            sample_data="samples",
        )

    service = _service(["d_task"])
    service.protocol = SimpleNamespace(retrieve_schema=fake_retrieve_schema)
    manifest = rt.TopupManifest(
        tables=("d_organization",),
        value_hits=(
            {
                "table": "d_organization",
                "field": "organization_name",
                "value": "研发二部",
                "source": "profile",
                "in_text": "研发二部",
            },
        ),
    )

    result = rt.fulfill_recall_topup(object(), service, manifest, audit=False)

    assert result.changed is True
    assert result.added_tables == ("d_organization",)
    assert protocol_calls == [["d_task", "d_organization"]]
    assert service.table_name_list == ["d_task", "d_organization"]
    assert (
        "研发二部 ≈ d_organization.organization_name" in service.chat_question.db_schema
    )


def test_fulfill_short_circuits_without_additions() -> None:
    service = _service(["d_task"])
    result = rt.fulfill_recall_topup(object(), service, rt.TopupManifest(), audit=False)
    assert result.changed is False
    assert service.table_name_list == ["d_task"]
    assert service.chat_question.db_schema == "old"


def test_fulfill_attaches_evidence_when_tables_already_present() -> None:
    service = _service(["d_organization"])
    manifest = rt.TopupManifest(
        value_hits=(
            {
                "table": "d_organization",
                "field": "organization_name",
                "value": "研发二部",
                "source": "profile",
                "in_text": "研发二部",
            },
        ),
    )
    result = rt.fulfill_recall_topup(object(), service, manifest, audit=False)
    assert result.changed is True
    assert "Value evidence" in service.chat_question.db_schema
    assert service.table_name_list == ["d_organization"]


def test_value_evidence_block_renders_hits() -> None:
    block = rt.value_evidence_block(
        [{"table": "t", "field": "f", "value": "v", "source": "dictionary"}]
    )
    assert block.startswith("【Value evidence】")
    assert "v ≈ t.f (dictionary)" in block
    assert rt.value_evidence_block([]) == ""


def test_tables_from_clarify_card_extracts_option_refs() -> None:
    card = {
        "questions": [
            {
                "question": "用哪个字段过滤",
                "options": [
                    {
                        "label": "团队",
                        "table": "d_project",
                        "fields": [
                            {"name": "organization_id", "table": "d_organization"}
                        ],
                    },
                    {"label": "无字段选项"},
                ],
            }
        ]
    }
    assert rt.tables_from_clarify_card(card) == ("d_project", "d_organization")
    assert rt.tables_from_clarify_card(None) == ()
    assert rt.tables_from_clarify_card({"questions": []}) == ()


def test_apply_knowledge_topup_recompiles_with_extras(monkeypatch) -> None:
    from apps.knowledge import compile as compile_pkg

    calls: dict = {}

    def fake_compile(_session, **kwargs):
        calls["extra"] = tuple(kwargs["extra_revision_ids"])
        calls["ds_id"] = kwargs["ds_id"]
        return "BUNDLE"

    monkeypatch.setattr(compile_pkg, "compile_business_data_bundle", fake_compile)
    service = _service(["d_task"])

    ok = rt.apply_knowledge_topup(
        object(),
        service,
        rt.TopupManifest(knowledge_units=({"unit_key": "u", "revision_id": 77},)),
        oid=1,
    )
    assert ok is True
    assert service.compiled_knowledge == "BUNDLE"
    assert calls["extra"] == (77,)
    assert calls["ds_id"] == 8

    # 无知识命中 → False, 不重编译
    service.compiled_knowledge = None
    assert (
        rt.apply_knowledge_topup(object(), service, rt.TopupManifest(), oid=1) is False
    )
    assert service.compiled_knowledge is None
