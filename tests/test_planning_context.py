from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.planning_context import (  # noqa: E402
    _split_knowledge_payload,
    capture_planning_context,
    execution_schema_resources,
    restore_planning_context,
)
from apps.knowledge.compile import knowledge_prompt_payload  # noqa: E402
from apps.knowledge.compile.bundle import ApplyHit, BusinessDataBundle  # noqa: E402
from apps.knowledge.models import KnowledgeMatch  # noqa: E402
from apps.knowledge.policy import CompileBudgets, get_knowledge_policy  # noqa: E402


def _service(schema: str = "# Table: orders\n(id:int)") -> SimpleNamespace:
    return SimpleNamespace(
        table_name_list=["orders"],
        compiled_knowledge=None,
        chat_question=SimpleNamespace(
            db_schema=schema,
            sample_data="sample",
            terminologies="terms",
            data_training="examples",
            custom_prompt="rules",
        ),
    )


def test_planning_context_round_trips_request_local_retrieval() -> None:
    source = _service()
    snapshot = capture_planning_context(
        source,
        entity_bindings={"研发二部": {"canonical": "研发二部"}},
        temporal_parse={"start": "2026-01-01"},
    )
    restored = _service("")
    restored.table_name_list = []

    result = restore_planning_context(restored, snapshot.model_dump(mode="json"))

    assert result.usable is True
    assert restored.chat_question.db_schema == source.chat_question.db_schema
    assert restored.table_name_list == ["orders"]
    assert result.entity_bindings["研发二部"]["canonical"] == "研发二部"


def test_empty_planning_context_cannot_reach_planner() -> None:
    with pytest.raises(ValueError, match="usable schema"):
        restore_planning_context(
            _service(""),
            {
                "version": 2,
                "schema_text": "",
                "resources": [],
                "fingerprint": "empty",
            },
        )


def test_planning_context_omits_matches_and_log_items() -> None:
    source = _service()
    source.compiled_knowledge = BusinessDataBundle(
        stage="generate",
        log_items=[{"words": ["x"]}],
        matches=[
            KnowledgeMatch(
                source="terminology",
                usages=["prompt"],
                query="q",
                canonical="c",
                match_type="exact",
                score=1.0,
            )
        ],
        calibers=[
            {
                "caliber_id": "done",
                "label": "done",
                "contract_fragment": {"requirements": []},
            }
        ],
        rules=[{"label": "rule", "content": "keep"}],
        scenarios=[{"stage_id": "approved", "name": "审核通过"}],
        ambiguities=[{"topic": "建档成功时间", "summary": "不能用 create_time"}],
        verified_examples=[{"id": 1, "question": "q", "sql": "SELECT 1"}],
        reuse={"exemplar_id": 9},
        apply_log=[
            ApplyHit(
                asset_kind="caliber",
                apply="constrain",
                reason="staging_caliber_hint",
            )
        ],
        structural_ref={"channel": "catalog_prompt"},
    )
    snapshot = capture_planning_context(
        source,
        entity_bindings={},
        temporal_parse={},
    )
    dumped = snapshot.compiled_knowledge
    assert "matches" not in dumped
    assert "log_items" not in dumped
    assert "bound_calibers" not in dumped
    assert "apply_log" not in dumped
    assert dumped["calibers"][0]["caliber_id"] == "done"
    assert dumped["rules"][0]["label"] == "rule"
    assert dumped["processes"][0]["stage_id"] == "approved"
    assert dumped["conflicts"][0]["topic"] == "建档成功时间"
    assert "scenarios" not in dumped
    assert "ambiguities" not in dumped
    assert dumped["reuse"]["exemplar_id"] == 9

    restored = _service("")
    restore_planning_context(restored, snapshot.model_dump(mode="json"))
    compiled = restored.compiled_knowledge
    assert isinstance(compiled, BusinessDataBundle)
    assert compiled.matches == []
    assert compiled.calibers[0]["caliber_id"] == "done"
    assert compiled.rules[0]["label"] == "rule"
    assert compiled.scenarios[0]["stage_id"] == "approved"
    assert compiled.ambiguities[0]["topic"] == "建档成功时间"


def test_compile_budgets_have_no_repair_hints() -> None:
    budgets = CompileBudgets()
    assert budgets.generate_examples == 2
    assert not hasattr(budgets, "repair_hints")
    policy = get_knowledge_policy({"compile_budgets": {"repair_hints": 9}})
    assert not hasattr(policy.compile_budgets, "repair_hints")




def test_knowledge_payload_is_compact() -> None:
    bundle = BusinessDataBundle(
        stage="generate",
        matched_units=[
            {
                "unit_id": 26,
                "unit_key": "pplatform:survey",
                "revision_id": 53,
                "revision": 2,
                "title": "企业调研",
                "domain": "survey",
                "description": "desc",
                "applicability": "applies",
                "confidence": 0.91,
            }
        ],
        datasets=[
            {
                "name": "cust_company_survey_whitelist",
                "dataset_id": "whitelist",
                "database": "lowcode_pplatform",
                "description": "白名单",
                "evidence_refs": ["ev-whitelist-model"],
                "fields": [
                    {"name": "company_id", "field_id": "company_id"}
                ],
            }
        ],
        fields=[
            {
                "name": "company_id",
                "field_id": "company_id",
                "data_type": "bigint",
                "dataset_id": "whitelist",
                "description": "企业ID",
                "dictionary": {},
                "evidence_refs": [],
            },
            {
                "name": "enable",
                "field_id": "enable",
                "data_type": "varchar",
                "dataset_id": "whitelist",
                "description": "启用标记",
                "dictionary": {"Y": "启用", "N": "停用"},
                "evidence_refs": ["ev-x"],
            },
        ],
        verified_examples=[
            {
                "id": "count-participating-companies",
                "question": "q",
                "sql": "SELECT 1",
                "description": "SELECT 1",
                "knowledge_meta": {"unit_revision_id": 53},
            }
        ],
        calibers=[{"caliber_id": "c", "label": "l", "evidence_refs": ["ev"]}],
    )
    payload = knowledge_prompt_payload(bundle)

    # datasets: no nested fields, no evidence_refs
    assert "fields" not in payload["datasets"][0]
    assert "evidence_refs" not in payload["datasets"][0]
    # fields: no field_id/data_type/evidence_refs; empty dictionary dropped
    company = next(f for f in payload["fields"] if f["name"] == "company_id")
    assert company == {
        "name": "company_id",
        "dataset_id": "whitelist",
        "description": "企业ID",
    }
    enable = next(f for f in payload["fields"] if f["name"] == "enable")
    assert enable["dictionary"] == {"Y": "启用", "N": "停用"}
    assert "data_type" not in enable and "evidence_refs" not in enable
    # matched_units: no server-side ids
    unit = payload["matched_units"][0]
    assert "unit_id" not in unit and "revision_id" not in unit and "revision" not in unit
    assert unit["unit_key"] == "pplatform:survey"
    # verified_examples: description + knowledge_meta dropped, sql kept
    assert payload["verified_examples"][0] == {
        "id": "count-participating-companies",
        "question": "q",
        "sql": "SELECT 1",
    }
    # calibers: evidence_refs stripped
    assert "evidence_refs" not in payload["calibers"][0]


def test_split_knowledge_payload_orders_by_value() -> None:
    compact = {
        "calibers": [{"caliber_id": "c"}],
        "matched_units": [{"title": "t"}],
        "processes": [{"stage_id": "s"}],
        "fields": [{"name": "f"}],
    }
    groups = _split_knowledge_payload(compact)
    names = [name for name, _content in groups]
    assert names.index("core") < names.index("context")
    assert names.index("context") < names.index("meta")
    assert names.index("meta") < names.index("process")
    by_name = {name: content for name, content in groups}
    assert by_name["core"]["calibers"] == [{"caliber_id": "c"}]
    assert by_name["context"]["fields"] == [{"name": "f"}]
    assert by_name["meta"]["matched_units"] == [{"title": "t"}]
    assert by_name["process"]["processes"] == [{"stage_id": "s"}]





def test_knowledge_payload_flattens_data_effects() -> None:
    bundle = BusinessDataBundle(
        stage="generate",
        scenarios=[
            {
                "stage_id": "approved",
                "name": "审核通过",
                "data_effects": [
                    {
                        "operation": "update",
                        "dataset": "cust_company_info",
                        "fields": ["status"],
                        "evidence_refs": ["ev"],
                    }
                ],
                "evidence_refs": ["ev-stage"],
            }
        ],
        data_effects=[
            {
                "operation": "update",
                "dataset": "cust_company_info",
                "fields": ["status"],
                "stage_id": "approved",
                "unit_revision_id": 53,
                "evidence_refs": ["ev"],
            }
        ],
    )
    payload = knowledge_prompt_payload(bundle)
    process = payload["processes"][0]
    assert "data_effects" not in process
    assert "evidence_refs" not in process
    assert process["stage_id"] == "approved"
    effect = payload["data_effects"][0]
    assert effect["stage_id"] == "approved"
    assert "unit_revision_id" not in effect
    assert "evidence_refs" not in effect



def test_execution_schema_keeps_planned_projection() -> None:
    resources = execution_schema_resources(
        ["cust_company_info", "cust_build_record"],
        [{"tables": ["cust_company_info"]}],
    )
    assert resources == ["cust_company_info", "cust_build_record"]
    assert execution_schema_resources([], [{"tables": ["orders"]}]) == ["orders"]
    assert execution_schema_resources([], [{}]) is None
