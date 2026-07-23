"""Unit tests for plan-time PlanContext (no DB / no LLM)."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

# test_conversation_core intentionally installs lightweight ``apps`` stubs
# during collection. Remove only those pathless stubs before normal imports.
_apps_module = sys.modules.get("apps")
if _apps_module is not None and not getattr(_apps_module, "__path__", None):
    for _module_name in list(sys.modules):
        if _module_name == "apps" or _module_name.startswith("apps."):
            sys.modules.pop(_module_name, None)

from apps.chat.plan_context import (  # noqa: E402
    entity_match_values,
    infer_entity_match,
    render_plan_context,
    wrap_plan_context,
)
from apps.chat.plan_policy import render_multi_fact_rule_xml  # noqa: E402


def test_infer_match_eq_when_exact_unique() -> None:
    assert infer_entity_match("研发二部", "研发二部", []) == "eq"


def test_infer_match_in_when_longer_canonical() -> None:
    assert infer_entity_match("研发二部", "战客研发二部", []) == "in"


def test_entity_in_includes_alts() -> None:
    vals = entity_match_values(
        {
            "canonical": "战客研发二部",
            "alternatives": ["A研发二部", "战客研发二部"],
            "match": "in",
        }
    )
    assert vals[0] == "战客研发二部"
    assert "A研发二部" in vals


def test_render_forbids_bare_phrase_eq() -> None:
    body = render_plan_context(
        entity_bindings={
            "candidates": ["研发二部"],
            "resolved": {
                "研发二部": {
                    "canonical": "战客研发二部",
                    "alternatives": ["X研发二部"],
                    "match": "in",
                    "column_hint": "organization_name",
                }
            },
        },
        query_bindings={
            "_notes": ["- 表 `d_task` 主键下界可用"],
            "d_task.id_ge": 100,
        },
        include_playbook=True,
    )
    assert "IN (" in body
    assert "禁止仅写" in body
    assert "multi-fact-staging" in body or "聚合" in body
    assert "主键下界" in body
    wrapped = wrap_plan_context(body)
    assert wrapped.startswith("<plan-context>")
    assert "</plan-context>" in wrapped
    from apps.chat.plan_context import normalize_plan_context_block

    again = normalize_plan_context_block(wrapped)
    assert again.startswith("<plan-context>")
    assert again.count("<plan-context>") == 1


def test_template_user_has_plan_context_placeholder() -> None:
    text = (_BACKEND / "templates" / "template.yaml").read_text(encoding="utf-8")
    assert "{plan_context}" in text
    assert "{multi_fact_rules}" in text
    assert "multi-fact-staging" in render_multi_fact_rule_xml()
    assert "不考虑业务逻辑" not in text


def test_multi_fact_policy_avoids_mysql_full_join_emulation() -> None:
    body = render_plan_context(include_playbook=True)
    assert "UNION 去重的共享维键集合" in body
    assert "不得用重复整段聚合查询" in body
    assert "LEFT/RIGHT JOIN + UNION ALL" in body


def test_nlq_no_longer_scatters_multi_query_guidance() -> None:
    text = (_BACKEND / "apps/chat/graphs/nodes/nlq.py").read_text(encoding="utf-8")
    assert "_MULTI_QUERY_GUIDANCE" not in text
    assert "_attach_plan_context_for_generate" in text
    # Probe nodes must not inject SystemMessage for grounding
    ground = text.split("def ground_entities_node")[1].split("def _extract_title")[0]
    assert "sql_message.append" not in ground
