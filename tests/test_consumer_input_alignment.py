"""Consumer input alignment: repair sees confirmed semantics, review sees calibers."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.steps import query_agent as qa  # noqa: E402


def _evidence(kind: str, content: str, structured: dict | None = None):
    return SimpleNamespace(
        evidence_id=f"e-{kind}",
        kind=kind,
        content=content,
        structured_value=structured or {},
    )


def test_confirmed_semantics_projects_option_answers() -> None:
    evidence = [
        _evidence("user_question", "原始问题"),
        _evidence(
            "clarification_option",
            "项目名称",
            {
                "question_id": "q1",
                "option_id": "o1",
                "meaning": "以 d_project.project_name 作为系统维度",
                "fields": [
                    {
                        "name": "project_name",
                        "table": "d_project",
                        "comment": "项目名称",
                    },
                    {"name": "create_time", "table": "d_task"},
                ],
                "why": "为什么",
            },
        ),
        _evidence("clarification_custom", "你自行查找研发二部", {"question_id": "q2"}),
    ]

    payload = qa._confirmed_semantics_payload(
        evidence, prior_user_evidence=[{"kind": "user_question", "content": "历史口径"}]
    )

    assert payload[0] == {"kind": "user_question", "content": "原始问题"}
    option = payload[1]
    assert option["content"] == "项目名称"
    assert option["meaning"] == "以 d_project.project_name 作为系统维度"
    assert option["fields"] == [
        {"table": "d_project", "name": "project_name"},
        {"table": "d_task", "name": "create_time"},
    ]
    assert "why" not in option and "option_id" not in option  # 低信噪字段剔除
    assert payload[2] == {
        "kind": "clarification_custom",
        "content": "你自行查找研发二部",
    }
    assert payload[-1]["content"] == "历史口径"


def test_reviewer_knowledge_subset_keeps_calibers_rules() -> None:
    knowledge = {
        "calibers": [{"unit": "时间"}],
        "rules": [{"rule": "R1"}],
        "metrics": [{"name": "及时率"}],
        "concepts": [{"term": "术语"}],
        "datasets": [{"name": "ds"}],
        "verified_examples": [{"question": "示例"}],
        "relationships": [{"a": "t1"}],
    }
    subset = qa._reviewer_knowledge_payload(knowledge)
    assert set(subset) == {"calibers", "rules", "metrics"}
    assert qa._reviewer_knowledge_payload({}) == {}
    assert qa._reviewer_knowledge_payload(None) == {}
    assert qa._reviewer_knowledge_payload({"concepts": [{"t": 1}]}) == {}


def test_planner_context_section_is_allow_listed() -> None:
    context = {
        "target_task": "query",
        "entity_bindings": {},
        "resources": ["t1"],
        "business_now": "2026-08-26",
        "referenced_turns": [{"record_id": 1}],
        "context_fingerprint": "internal-only",
        "schema_fingerprint": "internal-only",
        "context_truncation": [{"section": "sample_data"}],
        "certified_knowledge": {},
        "prior_user_evidence": [],
        "schema_map": "",
        "knowledge_map": "",
    }
    section = qa._planner_context_section(context)
    assert set(section) == {
        "target_task",
        "entity_bindings",
        "resources",
        "business_now",
        "referenced_turns",
    }  # 指纹/截断/知识/地图均不进 context 段（空白名单键仍在，空值渲染层省略）
    assert "context_fingerprint" not in section
    assert "schema_fingerprint" not in section


def test_truncation_notice_lists_dropped_sections() -> None:
    notice = qa._truncation_notice(
        [
            {
                "section": "sample_data",
                "estimated_tokens": 500,
                "reason": "context_budget",
            }
        ]
    )
    assert notice.startswith("以下上下文经过预算截断")
    assert "sample_data" in notice and "500" in notice
    assert qa._truncation_notice([]) == ""
