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
    render_intent_decisions,
    render_plan_context,
    render_time_intent,
    wrap_plan_context,
)
from apps.chat.plan_policy import render_multi_fact_playbook  # noqa: E402


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


def test_entity_eq_excludes_advisory_alternatives() -> None:
    vals = entity_match_values(
        {
            "canonical": "研发二部",
            "alternatives": ["三中心研发二部（废弃）"],
            "match": "eq",
        }
    )
    assert vals == ["研发二部"]
    body = render_plan_context(
        entity_bindings={
            "resolved": {
                "研发二部": {
                    "canonical": "研发二部",
                    "alternatives": ["三中心研发二部（废弃）"],
                    "match": "eq",
                }
            }
        },
        include_playbook=False,
    )
    assert "不得自动并入 IN" in body


def test_render_forbids_bare_phrase_eq() -> None:
    body = render_plan_context(
        entity_bindings={
            "candidates": ["研发二部"],
            "resolved": {
                "研发二部": {
                    "canonical": "战客研发二部",
                    "alternatives": ["X研发二部"],
                    "match": "in",
                    "targets": [
                        {
                            "table_name": "d_organization",
                            "field_name": "organization_name",
                        }
                    ],
                }
            },
        },
        include_playbook=True,
    )
    assert "IN (" in body
    assert "d_organization.organization_name" in body
    assert "禁止仅写" in body
    assert "multi-fact-staging" in body or "聚合" in body
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
    assert "{multi_fact_rules}" not in text
    assert "multi-fact-staging" in render_multi_fact_playbook()
    assert "不考虑业务逻辑" not in text


def test_multi_fact_policy_avoids_mysql_full_join_emulation() -> None:
    body = render_plan_context(include_playbook=True)
    assert "UNION 去重的共享维键集合" in body
    assert "不得用重复整段聚合查询" in body
    assert "LEFT/RIGHT JOIN + UNION ALL" in body


def test_time_intent_renders_as_mandatory_contract() -> None:
    block = render_time_intent(
        {
            "scope": "default",
            "anchor": "data_max",
            "comparison": "yoy",
            "grain": "month",
            "lookback_months": 24,
            "source": "default_policy",
            "confidence": 0.7,
        }
    )
    assert "必须遵守" in block
    assert "最新有效时间" in block
    assert "24 个自然月" in block
    assert "服务器当前日期" in block


def test_confirmed_intent_is_rendered_once_in_plan_context() -> None:
    intent = {
        "decisions": [
            {
                "key": "scope.department_basis",
                "label": "部门口径",
                "value": {
                    "selected_options": [
                        {
                            "id": "assignee",
                            "label": "任务执行人所属部门",
                            "impact": "按执行人组织过滤",
                        }
                    ]
                },
                "locked": True,
            }
        ]
    }
    body = render_plan_context(intent_context=intent, include_playbook=False)
    assert render_intent_decisions(intent) in body
    assert body.count("已确定查询口径") == 1


def test_related_multi_issue_decision_is_displayed_once() -> None:
    selected = {
        "selected_options": [
            {
                "id": "union_grain",
                "label": "企业并集后按企业-核企展示",
            }
        ]
    }
    intent = {
        "decisions": [
            {
                "key": "relation.population",
                "label": "基础集合与关联粒度",
                "value": selected,
                "locked": True,
            },
            {
                "key": "grain.join_strategy",
                "label": "基础集合与关联粒度",
                "value": selected,
                "locked": True,
            },
        ]
    }

    body = render_plan_context(intent_context=intent, include_playbook=False)

    assert body.count("企业并集后按企业-核企展示") == 1


def test_nlq_no_longer_scatters_multi_query_guidance() -> None:
    text = (_BACKEND / "apps/chat/graphs/nodes/nlq.py").read_text(encoding="utf-8")
    assert "_MULTI_QUERY_GUIDANCE" not in text
    assert "_attach_plan_context_for_generate" in text
    # Probe nodes must not inject SystemMessage for grounding
    ground = text.split("def ground_entities_node")[1].split("def _extract_title")[0]
    assert "sql_message.append" not in ground
