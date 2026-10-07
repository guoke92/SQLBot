"""Pre-execute SQL rules: code defaults, config toggles, closed-code literals."""

from __future__ import annotations

from types import SimpleNamespace

from apps.chat.agent.knowledge import stage_plane, take_working
from apps.chat.agent_config.defaults import SQL_RULE_DEFAULTS
from apps.chat.agent_config.loader import AgentRuntimeConfig, merge_sql_rules
from apps.chat.agent_knowledge import AgentKnowledgePlane
from apps.chat.sql_rules import _closed_columns, enforce_sql_rules
from apps.chat.tools.contract import failure_outcome


def _service() -> SimpleNamespace:
    return SimpleNamespace(ds=SimpleNamespace(id=1, type="mysql"), datasource=None)


def test_closed_columns_ignore_topk_samples() -> None:
    columns = _closed_columns(
        {
            "cust": "name:varchar, 名称, topk=甲|乙\nenable:char, 启用, topk=Y|N, labels=Y:启用|N:停用"
        }
    )
    assert ("cust", "name") not in columns
    assert columns[("cust", "enable")] == {"Y", "N"}


def test_closed_literal_rejects_display_label(monkeypatch) -> None:
    stage_plane(
        AgentKnowledgePlane(
            schema_by_table={
                "cust": "enable:char, 启用, topk=Y|N, labels=Y:启用|N:停用"
            }
        )
    )
    monkeypatch.setattr(
        "apps.chat.agent_config.loader.load_agent_config_for_run",
        lambda: AgentRuntimeConfig(
            prompt_template="x",
            prompt_version="t",
            tools={},
            loop_params={},
            sql_rules=merge_sql_rules(None),
        ),
    )
    blocked = enforce_sql_rules(
        "SELECT id FROM cust WHERE enable = '启用'",
        _service(),
    )
    assert blocked is not None
    assert blocked["ok"] is False
    assert "启用" in blocked["error"]

    allowed = enforce_sql_rules(
        "SELECT id FROM cust WHERE enable = 'Y'",
        _service(),
    )
    assert allowed is None
    take_working()


def test_disabled_catalog_rule_does_not_block(monkeypatch) -> None:
    rules = merge_sql_rules({"catalog_probe": {"enabled": False}})
    assert rules["catalog_probe"]["enabled"] is False
    assert rules["closed_literal"]["enabled"] is True
    monkeypatch.setattr(
        "apps.chat.agent_config.loader.load_agent_config_for_run",
        lambda: AgentRuntimeConfig(
            prompt_template="x",
            prompt_version="t",
            tools={},
            loop_params={},
            sql_rules=rules,
        ),
    )
    assert (
        enforce_sql_rules("SHOW COLUMNS FROM cust", _service()) is None
    )
    monkeypatch.setattr(
        "apps.chat.agent_config.loader.load_agent_config_for_run",
        lambda: AgentRuntimeConfig(
            prompt_template="x",
            prompt_version="t",
            tools={},
            loop_params={},
            sql_rules=merge_sql_rules(SQL_RULE_DEFAULTS),
        ),
    )
    blocked = enforce_sql_rules("SHOW COLUMNS FROM cust", _service())
    assert blocked is not None
    assert blocked["failure"]["retryable"] is False


def test_unknown_rule_kind_is_dropped() -> None:
    merged = merge_sql_rules({"not_a_rule": {"enabled": False}})
    assert "not_a_rule" not in merged
    assert set(merged) == set(SQL_RULE_DEFAULTS)


def test_failure_outcome_shape_stays_the_contract() -> None:
    failed = failure_outcome("nope", name="execute_sql_sandbox", retryable=True)
    assert failed["ok"] is False
    assert failed["failure"]["retryable"] is True
