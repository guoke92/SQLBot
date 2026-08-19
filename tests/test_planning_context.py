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
    capture_planning_context,
    execution_schema_resources,
    restore_planning_context,
)
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


def test_execution_schema_keeps_planned_projection() -> None:
    resources = execution_schema_resources(
        ["cust_company_info", "cust_build_record"],
        [{"tables": ["cust_company_info"]}],
    )
    assert resources == ["cust_company_info", "cust_build_record"]
    assert execution_schema_resources([], [{"tables": ["orders"]}]) == ["orders"]
    assert execution_schema_resources([], [{}]) is None
