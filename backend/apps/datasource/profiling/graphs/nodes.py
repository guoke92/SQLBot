"""LangGraph nodes for the metadata cognition mining graph."""

from __future__ import annotations

from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from sqlmodel import Session

from apps.conversation.llm import get_chat_model, get_default_chat_config
from apps.conversation.outcome import running_outcome
from apps.conversation.state import RunState
from apps.datasource.profiling.models import MetadataScanRun, ScanRunMode
from apps.datasource.profiling.service import build_profile_brief
from apps.datasource.profiling.tools import build_mining_tools
from common.utils.utils import SQLBotLogUtil

_MAX_TOOL_ROUNDS = 10

_SYSTEM_PROMPT = """You are a metadata cognition mining agent for SQLBot.
You analyze database catalog briefs and may call tools to discover semantic
relationships, validate candidates, and write CANDIDATE knowledge.

Hard rules:
1. Never invent statistics — call probe tools for evidence (facts are pre-collected).
2. Never confirm relations (confirm_* unavailable). extract_ddl_constraints is read-only;
   only upsert CANDIDATE via upsert_* tools.
3. Do not request all-pairs scans. Propose at most 50 column pairs per turn.
4. Prefer reading get_profile_brief / list_tables_brief before probing.
5. Prefer name_similarity → overlap/fanout for joins; cooccurrence/binding for 1:1;
   formula_probe / hierarchy_probe when formulas or path codes are likely.
6. For EQUI_JOIN candidates: only upsert when overlap_probe reports suggest_candidate=true
   (high containment AND target key_likelihood high/medium). Put inclusion_score and
   suggested_direction into evidence. Prefer source=inclusion when scoring gates pass.
7. If mine_query_log_joins is available, call it once to seed candidates from history;
   never treat those as confirmed.
8. Respect soft_signals in the brief (key_likelihood, temporal_role, domain_role, table_role).
9. draft_* descriptions never auto-apply; only propose text for human confirm.
10. When finished, stop calling tools and summarize findings briefly.
"""


class MetadataState(RunState, total=False):
    scan_run_id: int
    lease_owner: str
    ds_id: int
    table_id: int | None
    run_mode: str
    oid: int
    bound_tools: list[Any]
    llm: Any
    tool_rounds: int
    tool_round_limit: int
    tool_steps: list[dict[str, Any]]
    last_tool_failure_signature: str
    consecutive_tool_failures: int
    tool_stop_reason: str
    tool_grounding_retry: bool
    tool_free_completion_marker: str
    final_text: str
    skip_agent: bool


def _renew_scan_lease(state: MetadataState | dict[str, Any]) -> None:
    """Best-effort lease heartbeat so long agent/tool rounds are not double-claimed."""
    run_id = state.get("scan_run_id")
    owner = (state.get("lease_owner") or "").strip()
    if not run_id or not owner:
        return
    try:
        from apps.conversation.session import session_scope
        from apps.datasource.profiling.service import renew_run_lease

        with session_scope() as session:
            renew_run_lease(
                session, run_id=int(run_id), worker_id=owner
            )
    except Exception as exc:  # pragma: no cover
        SQLBotLogUtil.warning(f"metadata lease renew skipped: {exc}")


def build_metadata_state(
    session: Session,
    *,
    run: MetadataScanRun,
    mode: str | None = None,
) -> MetadataState:
    """Build graph state for an existing scan run (worker / API)."""
    from apps.datasource.models.datasource import CoreDatasource, CoreTable
    from apps.datasource.profiling.service import resolve_table_mining_policy

    run_mode = (mode or run.run_mode or ScanRunMode.SEMANTIC.value).strip()
    # Worker never invokes the graph for facts_only; keep guard for safety.
    skip_agent = run_mode == ScanRunMode.FACTS_ONLY.value
    caps: frozenset[str] | None = None
    if run.table_id is not None:
        ds = session.get(CoreDatasource, int(run.ds_id))
        table = session.get(CoreTable, int(run.table_id))
        if ds is not None and table is not None:
            policy = resolve_table_mining_policy(session, ds=ds, table=table)
            caps = policy.capabilities
            if not policy.has_agent_work():
                skip_agent = True
    brief = build_profile_brief(
        session,
        ds_id=int(run.ds_id),
        table_ids=[int(run.table_id)] if run.table_id is not None else None,
        include_top_values=False,
    )
    tools = (
        []
        if skip_agent
        else build_mining_tools(
            oid=int(run.oid),
            ds_id=int(run.ds_id),
            table_id=int(run.table_id) if run.table_id is not None else None,
            run_mode=run_mode,
            allow_confirm=False,
            capabilities=caps,
        )
    )
    llm = None
    if not skip_agent:
        model_config = _sync_default_chat_config()
        llm = get_chat_model(model_config)

    messages = [
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f"run_mode={run_mode}\n"
                f"ds_id={run.ds_id} table_id={run.table_id}\n"
                f"targets={run.targets}\n"
                f"profile_brief={brief}\n"
                "Discover useful candidate relations / bindings if evidence supports them."
            )
        ),
    ]
    return MetadataState(
        graph_key="metadata",
        chat_id=0,
        record_id=None,
        messages=messages,
        current_user=None,
        scan_run_id=int(run.id) if run.id is not None else 0,
        lease_owner=(run.lease_owner or "").strip(),
        ds_id=int(run.ds_id),
        table_id=int(run.table_id) if run.table_id is not None else None,
        run_mode=run_mode,
        oid=int(run.oid),
        bound_tools=tools,
        llm=llm,
        tool_rounds=0,
        tool_round_limit=_MAX_TOOL_ROUNDS,
        tool_steps=[],
        tool_free_completion_marker="",
        skip_agent=skip_agent,
        outcome=running_outcome(),
        sink="json",
        in_chat=False,
        stream=False,
    )


def _sync_default_chat_config() -> Any:
    import asyncio

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(get_default_chat_config())
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(get_default_chat_config())
    finally:
        loop.close()


def prepare_node(state: MetadataState) -> dict[str, Any]:
    _renew_scan_lease(state)
    return {
        "tool_rounds": int(state.get("tool_rounds") or 0),
        "tool_round_limit": int(state.get("tool_round_limit") or _MAX_TOOL_ROUNDS),
        "skip_agent": bool(state.get("skip_agent")),
    }


def route_after_prepare(state: MetadataState) -> str:
    return "finalize" if state.get("skip_agent") else "agent"


def agent_node(state: MetadataState) -> dict[str, Any]:
    """Wrap shared agent node with a scan-run lease heartbeat."""
    _renew_scan_lease(state)
    from apps.conversation.agent import agent_node as shared_agent_node

    return shared_agent_node(state)


def execute_tools_node(state: MetadataState) -> dict[str, Any]:
    """Wrap shared tool executor with a scan-run lease heartbeat."""
    _renew_scan_lease(state)
    from apps.conversation.tooling import execute_tools_node as shared_execute_tools

    return shared_execute_tools(state)


def finalize_node(state: MetadataState) -> dict[str, Any]:
    _renew_scan_lease(state)
    SQLBotLogUtil.info(
        f"metadata graph finalize scan_run={state.get('scan_run_id')} "
        f"mode={state.get('run_mode')} tools={len(state.get('tool_steps') or [])}"
    )
    return {
        "final_text": state.get("final_text")
        or f"metadata mining finished mode={state.get('run_mode')}",
    }
