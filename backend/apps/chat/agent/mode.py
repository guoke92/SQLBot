"""Peer agent-mode implementations behind one loop-facing interface.

The graph loop, close-plane, workspace, and tools runtime stay mode-agnostic.
Query and Analyze are equal implementations of ``AgentMode``.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, Protocol

from apps.chat.agent.prompt import (
    ANALYZE_TAIL,
    ANALYZE_WORKFLOW,
    QUERY_TAIL,
    QUERY_WORKFLOW,
    compose_mode_prompt,
)
from apps.chat.agent_config.defaults import DEFAULT_TOOL_NAMES, QUERY_TOOL_NAMES

AgentModeId = Literal["query", "analyze"]
RouteTaskKind = Literal["query", "analysis", "unsupported"]


class AgentMode(Protocol):
    id: AgentModeId
    task_kind: Literal["query", "analysis"]

    def compose_rules(self, *, config: Any = None) -> str: ...

    def loop_param_overrides(self) -> Mapping[str, int]: ...

    def incomplete_message(self, state: Mapping[str, Any]) -> str: ...

    def tool_names(self) -> tuple[str, ...]: ...

    def compact_keep_tables(self) -> bool: ...

    def finalizing_instruction(self, reason: str) -> str: ...

    def evidence_nudge(self, state: Mapping[str, Any]) -> str: ...

    def defer_clarification(self, state: Mapping[str, Any]) -> str: ...


def route_task_kind(hint: str | None) -> RouteTaskKind:
    """Map API / UI hints onto TurnRoute.task_kind. Unknown values → query."""
    raw = str(hint or "").strip().lower()
    if raw in {"analysis", "analyze"}:
        return "analysis"
    if raw == "unsupported":
        return "unsupported"
    return "query"


def _hint_from_state(state: Mapping[str, Any] | None) -> str:
    if not state:
        return ""
    route = (
        state.get("turn_route") if isinstance(state.get("turn_route"), Mapping) else {}
    )
    return str(
        (route or {}).get("task_kind")
        or state.get("route_hint")
        or state.get("agent_mode")
        or ""
    )


def resolve_agent_mode(state: Mapping[str, Any] | None = None) -> AgentMode:
    """Registry: analysis/analyze → AnalyzeMode; everything else → QueryMode."""
    if route_task_kind(_hint_from_state(state)) == "analysis":
        return AnalyzeMode()
    return QueryMode()


def translate_agent_copy(state: Mapping[str, Any], key: str, fallback: str) -> str:
    try:
        from apps.chat.graphs.turn_state import llm_service

        trans = getattr(llm_service(state), "trans", None)
        if callable(trans):
            text = str(trans(key) or "").strip()
            if text and text != key:
                return text
    except Exception:
        pass
    return fallback


class QueryMode:
    id: AgentModeId = "query"
    task_kind: Literal["query", "analysis"] = "query"

    def compose_rules(self, *, config: Any = None) -> str:
        return compose_mode_prompt(
            workflow=QUERY_WORKFLOW, tail=QUERY_TAIL, config=config
        )

    def loop_param_overrides(self) -> Mapping[str, int]:
        return {}

    def incomplete_message(self, state: Mapping[str, Any]) -> str:
        return translate_agent_copy(
            state,
            "i18n_chat.agent.incomplete_no_data",
            "这次没能查出结果。请换个问法试试，或确认数据源表结构已同步。",
        )

    def tool_names(self) -> tuple[str, ...]:
        return QUERY_TOOL_NAMES

    def compact_keep_tables(self) -> bool:
        return False

    def finalizing_instruction(self, reason: str) -> str:
        return (
            f"工具调用已关闭（{reason}）。不要再请求任何工具。"
            "按 §6 停手终答：有本轮交付卡则只写口径旁白；"
            "否则直接写结论，不要再提出补检索、目录 SQL 或猜测字段。"
        )

    def evidence_nudge(self, state: Mapping[str, Any]) -> str:
        del state
        return ""

    def defer_clarification(self, state: Mapping[str, Any]) -> str:
        del state
        return ""


class AnalyzeMode:
    id: AgentModeId = "analyze"
    task_kind: Literal["query", "analysis"] = "analysis"

    def compose_rules(self, *, config: Any = None) -> str:
        return compose_mode_prompt(
            workflow=ANALYZE_WORKFLOW, tail=ANALYZE_TAIL, config=config
        )

    def loop_param_overrides(self) -> Mapping[str, int]:
        return {"probe_sql_limit": 8, "execution_round_limit": 8}

    def incomplete_message(self, state: Mapping[str, Any]) -> str:
        return translate_agent_copy(
            state,
            "i18n_chat.agent.incomplete_no_analysis",
            "这次没能完成分析。请换个问法试试，或确认数据源表结构已同步。",
        )

    def tool_names(self) -> tuple[str, ...]:
        return DEFAULT_TOOL_NAMES

    def compact_keep_tables(self) -> bool:
        return True

    def finalizing_instruction(self, reason: str) -> str:
        return (
            f"工具调用已关闭（{reason}）。不要再请求任何工具。"
            "按 §6 写完：开头直接回答，切面用业务标题、小表和表后解读；不要写「分析报告」「核心发现」。若上文已经有正文，保留结论并补上仍缺的全量数字。"
            "禁止交空白，禁止只写「仅展示前 N 条」。"
            "总体数字只能来自不带 LIMIT 的聚合或 <evidence>，禁止用 preview 充当全量。"
        )

    def evidence_nudge(self, state: Mapping[str, Any]) -> str:
        if state.get("analyze_evidence_nudged"):
            return ""
        if not _needs_warehouse_stats(state):
            return ""
        return (
            "已有结果 rev，但本轮还没有不带 LIMIT 的总体聚合，也没有 "
            "profile_sql_result / aggregate_sql_result / compare_results。"
            "先做一条返回很少行的全量聚合，再按 §6 写报告。"
            "报告一旦写完就停，不要为凑剖析把已写好的报告丢掉。"
            "能用数据探明的不要 request_clarification。"
        )

    def defer_clarification(self, state: Mapping[str, Any]) -> str:
        if not _needs_warehouse_stats(state):
            return ""
        return (
            "已有结果 rev。取值分布、哪一维能解释波动、空值/截断是否导致异常，"
            "先 profile_sql_result / aggregate_sql_result。"
            "能探明的不要 request_clarification。"
        )


def _executed_sql_revisions(state: Mapping[str, Any]) -> bool:
    from apps.chat.agent.workspace import SqlWorkspace

    workspace = SqlWorkspace.from_state(state)
    return any(
        item.status in {"executed", "delivered"} or item.row_count is not None
        for item in workspace.revisions.values()
    )


def _this_turn_warehouse_stats(state: Mapping[str, Any]) -> bool:
    from apps.chat.tools.analyze_result import ANALYZE_SQL_TOOLS

    for step in state.get("tool_steps") or []:
        if not isinstance(step, Mapping) or not step.get("ok"):
            continue
        name = str(step.get("name") or step.get("tool") or "")
        if name in ANALYZE_SQL_TOOLS or name == "compare_results":
            return True
    return False


def _needs_warehouse_stats(state: Mapping[str, Any]) -> bool:
    return _executed_sql_revisions(state) and not _this_turn_warehouse_stats(state)
