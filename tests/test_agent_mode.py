"""Peer Query/Analyze modes behind the loop-facing AgentMode interface."""

from __future__ import annotations

from apps.chat.agent.close import close_kind
from apps.chat.agent.init import ensure_agent_turn_route
from apps.chat.agent.mode import (
    AnalyzeMode,
    QueryMode,
    resolve_agent_mode,
    route_task_kind,
)
from apps.chat.agent.prompt import (
    _SYSTEM_PROMPT_TEMPLATE,
    compose_mode_prompt,
)
from apps.chat.graphs.turn_snapshot import record_snapshot_values
from apps.chat.turn_contracts import AnalysisTurnAnswer, TurnRoute
from apps.conversation.outcome import successful_outcome


def test_resolve_agent_mode_defaults_to_query() -> None:
    assert isinstance(resolve_agent_mode({}), QueryMode)
    assert isinstance(resolve_agent_mode({"route_hint": "query"}), QueryMode)
    assert isinstance(resolve_agent_mode({"route_hint": "prediction"}), QueryMode)
    assert isinstance(resolve_agent_mode({"agent_mode": "query"}), QueryMode)


def test_resolve_agent_mode_reads_analysis_hints() -> None:
    assert isinstance(resolve_agent_mode({"route_hint": "analysis"}), AnalyzeMode)
    assert isinstance(resolve_agent_mode({"route_hint": "analyze"}), AnalyzeMode)
    assert isinstance(
        resolve_agent_mode({"turn_route": {"task_kind": "analysis"}}), AnalyzeMode
    )


def test_route_task_kind_maps_hints() -> None:
    assert route_task_kind(None) == "query"
    assert route_task_kind("analyze") == "analysis"
    assert route_task_kind("analysis") == "analysis"
    assert route_task_kind("prediction") == "query"
    assert route_task_kind("nope") == "query"


def test_query_compose_matches_shipped_prompt() -> None:
    text = QueryMode().compose_rules()
    expected = _SYSTEM_PROMPT_TEMPLATE.format(execution_limit=5)
    assert text == expected
    assert "取数则 `execute_sql_sandbox(purpose=delivery)`" in text
    assert "禁止**用旁白代替取数" in text
    assert "profile_sql_result" not in text


def test_analyze_compose_is_peer_not_overlay() -> None:
    text = AnalyzeMode().compose_rules()
    assert "默认 `purpose=probe`" in text
    assert "完整分析报告" in text
    assert "### 核心发现" in text
    assert "### 分析路径" in text
    assert "profile_sql_result" in text
    assert "能探明的不要问人" in text
    assert "报告是产品" in text
    assert "取证计划" in text
    assert "一两句结论" not in text
    assert "禁止**用旁白代替取数" not in text
    assert "get_table_schema" in text
    assert "用户可见文案" in text


def test_legacy_full_prompt_is_stripped_to_shared_kernel() -> None:
    from apps.chat.agent.prompt import strip_mode_sections

    kernel = strip_mode_sections(_SYSTEM_PROMPT_TEMPLATE)
    assert "## 0. 工作流" not in kernel
    assert "## 6. 最终回答" not in kernel
    assert "## 1. 全局大纲" in kernel
    rebuilt = compose_mode_prompt(
        workflow="## 0. 工作流\nX",
        tail="## 4. 增量修改\nY\n## 6. 最终回答\nZ",
        config=_config(kernel),
    )
    assert rebuilt.startswith("你是 AI智能问数")
    assert "## 0. 工作流\nX" in rebuilt
    assert "## 6. 最终回答\nZ" in rebuilt


def _config(prompt: str):
    from apps.chat.agent_config.defaults import LOOP_PARAM_DEFAULTS, default_tools
    from apps.chat.agent_config.loader import AgentRuntimeConfig

    return AgentRuntimeConfig(
        prompt_template=prompt,
        prompt_version="t",
        tools={name: dict(cfg) for name, cfg in default_tools().items()},
        loop_params=dict(LOOP_PARAM_DEFAULTS),
    )


def test_independent_analysis_route_is_valid() -> None:
    route = TurnRoute(
        task_kind="analysis",
        relation="independent",
        reference_record_ids=(),
        source="hint",
        confidence=1.0,
    )
    assert route.task_kind == "analysis"
    built = ensure_agent_turn_route(
        {"route_hint": "analysis"}, reference_record_ids=[]
    )
    assert built["task_kind"] == "analysis"
    assert built["relation"] == "independent"


def test_close_kind_empty_is_mode_agnostic() -> None:
    assert close_kind({"turn_route": {"task_kind": "query"}}, has_cards=False) == "empty"
    assert (
        close_kind({"turn_route": {"task_kind": "analysis"}}, has_cards=False) == "empty"
    )
    assert (
        close_kind(
            {
                "final_text": "开通率在上升。",
                "turn_route": {"task_kind": "analysis", "relation": "independent"},
            },
            has_cards=False,
        )
        == "text"
    )


def test_snapshot_kind_follows_analysis_route() -> None:
    snapshot = record_snapshot_values(
        [],
        analysis_text="趋势向上",
        finish=True,
        outcome=successful_outcome(),
        execution_mode="agent",
        kind="analysis",
    )
    answer = AnalysisTurnAnswer.model_validate(
        {**snapshot["answer"], "answer_revision": 1, "source_run_id": "r1"}
    )
    assert answer.kind == "analysis"
    assert answer.content == "趋势向上"
    assert answer.datasets == ()


def test_analyze_incomplete_copy_differs_from_query() -> None:
    query = QueryMode().incomplete_message({})
    analyze = AnalyzeMode().incomplete_message({})
    assert "查出结果" in query
    assert "完成分析" in analyze


def test_analyze_probe_override() -> None:
    assert AnalyzeMode().loop_param_overrides()["probe_sql_limit"] == 8
    assert AnalyzeMode().loop_param_overrides()["execution_round_limit"] == 8
    assert QueryMode().loop_param_overrides() == {}
    assert "profile_sql_result" not in QueryMode().tool_names()
    assert "profile_sql_result" in AnalyzeMode().tool_names()


def _executed_analyze_state(**extra: object) -> dict:
    from apps.chat.agent.workspace import SqlWorkspace

    workspace = SqlWorkspace()
    item = workspace.add_revision("SELECT 1", status="executed", dataset_id="d1")
    workspace.mark_executed(item.rev, dataset_id="d1", purpose="probe")
    return {
        "route_hint": "analysis",
        "sql_workspace": workspace.model_dump(mode="json"),
        **extra,
    }


def test_analyze_evidence_nudge_once() -> None:
    state = _executed_analyze_state()
    first = AnalyzeMode().evidence_nudge(state)
    assert "profile_sql_result" in first
    assert AnalyzeMode().evidence_nudge({**state, "analyze_evidence_nudged": True}) == ""
    assert QueryMode().evidence_nudge(state) == ""


def test_analyze_defer_clarification_until_warehouse_stats() -> None:
    state = _executed_analyze_state()
    assert "profile_sql_result" in AnalyzeMode().defer_clarification(state)
    profiled = _executed_analyze_state(
        tool_steps=[{"ok": True, "name": "profile_sql_result"}]
    )
    assert AnalyzeMode().defer_clarification(profiled) == ""
    assert QueryMode().defer_clarification(state) == ""


def test_analyze_skips_clarification_until_warehouse_stats(monkeypatch) -> None:
    from unittest.mock import MagicMock

    from langchain_core.messages import AIMessage

    from apps.chat.agent.tools.runtime import execute_tools_node

    tool = MagicMock()
    tool.name = "request_clarification"
    tool.invoke.side_effect = AssertionError("must explore data before asking")
    monkeypatch.setattr(
        "apps.chat.agent.tools.runtime.open_process_span", lambda **_k: None
    )
    monkeypatch.setattr(
        "apps.chat.agent.tools.runtime.attach_process_span", lambda *_a, **_k: None
    )
    monkeypatch.setattr(
        "apps.chat.agent.tools.runtime.attach_running_tool_span",
        lambda **_k: None,
    )
    result = execute_tools_node(
        {
            **_executed_analyze_state(),
            "messages": [
                AIMessage(
                    content="",
                    tool_calls=[
                        {
                            "id": "c1",
                            "name": "request_clarification",
                            "args": {"questions": []},
                        }
                    ],
                )
            ],
            "bound_tools": [tool],
            "sink": "json",
        }
    )
    step = result["tool_steps"][0]
    assert step["outcome"]["signals"]["skipped"] is True
    assert step["outcome"]["payload"]["reason"] == "explore_first"
