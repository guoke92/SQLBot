"""Shared state contract + cross-group helpers for the nlq node package."""

from __future__ import annotations

import re
import traceback
from typing import Any, Literal, TypedDict, cast

from apps.chat.models.chat_model import (
    ChatFinishStep,
)
from apps.chat.plan_facts import sqlglot_dialect_for
from apps.chat.plan_policy import (
    MAX_BATCH_ROUNDS,
    MAX_QUERIES_PER_BATCH,
    ROW_LIMIT,
)
from apps.chat.task.llm import LLMService
from apps.chat.time_intent import TemporalParse
from apps.conversation.outcome import (
    ResultQuality,
    RunOutcome,
    failed_outcome,
    format_error_message,
    public_error_message,
)
from apps.conversation.run_service import (
    ConversationRunCancelled,
)
from apps.conversation.runtime_context import runtime_value
from apps.conversation.state import RunState
from apps.datasource.access import (
    AccessScope,
)
from apps.datasource.models.datasource import CoreDatasource

# ── Constants ────────────────────────────────────────────────────────────────


_MAX_STEPS = MAX_BATCH_ROUNDS


_MAX_BATCH_SIZE = MAX_QUERIES_PER_BATCH


_ROW_LIMIT = ROW_LIMIT


_TEMPORAL_RE = re.compile(r"^\d{4}[-/]\d{1,2}([-/]\d{1,2})?$")


class CandidateBatch(TypedDict, total=False):
    """One plan batch through planning, execution, review and publication."""

    plans: list[dict[str, Any]]
    results: list[dict[str, Any]]
    charts: list[dict[str, Any]]
    steps: list[dict[str, Any]]
    quality: ResultQuality
    outcome: RunOutcome
    plan_validated: bool
    semantic_status: Literal["verified", "partial", "unsupported"]


class NlqState(RunState, total=False):
    """Agentic batch loop state.

    This is the canonical state contract for the production chat graph.
    """

    finish_step: int
    return_img: bool
    turn_route: dict[str, Any]
    referenced_turns: list[dict[str, Any]]
    prior_user_evidence: list[dict[str, Any]]
    source_datasets: list[dict[str, Any]]
    data_strategy: Literal[
        "direct_query", "existing_results", "derived_query", "unavailable"
    ]
    business_now: str
    timezone: str
    context_fingerprint: str
    terminal_answer: dict[str, Any]
    execution_mode: Literal["verified", "unverified"]
    quality_cap: int
    risk_assessment: dict[str, Any]
    semantic_review: dict[str, Any]
    plan_facts: list[dict[str, Any]]
    planning_model_elapsed_sec: float
    json_result: dict[str, Any]

    # recall top-up (deterministic evidence-driven working-set expansion)
    recall_topup_notice: dict[str, Any]
    topup_bounce_count: int
    plan_gate_route: str

    # batch loop
    step_index: int  # current batch iteration (0-based)
    active_candidate: CandidateBatch
    repair_source_plans: list[dict[str, Any]]
    # Candidates move atomically between these lifecycle slots. Individual
    # plans/results/charts are never published or combined across candidates.
    rejected_candidate: CandidateBatch | None
    accepted_candidate: CandidateBatch | None
    analysis_text: str
    max_steps: int
    max_batch_size: int
    decision: str
    decision_reason: str
    repair_hint: str  # plan-validate or execute-quality rewrite brief
    gen_attempts: int  # plan-time generate→validate failures in current slot
    entity_bindings: dict[str, Any]  # NL phrase → canonical dimension values
    knowledge_matches: list[dict[str, Any]]
    compiled_knowledge: dict[str, Any]  # BusinessDataBundle dump; Bind/apply_log
    wiki_context: dict[str, Any]  # wiki backend telemetry (backend/physical_gate_hits)
    wiki_knowledge_text: str  # wiki business recall — prompt-ready semantic text
    temporal_parse: TemporalParse  # deterministic evidence; never executable truth
    planning_decision: Literal["pending", "clarify", "ready", "replan", "unsupported"]
    ambiguity_payload: dict[str, Any]
    unsupported_payload: dict[str, Any]
    outcome: RunOutcome
    tool_steps: list[dict[str, Any]]
    tool_rounds: int
    tool_round_limit: int
    memory_slots: dict[str, Any]
    bound_tools: list[Any]
    final_text: str


def _llm_service(state: NlqState) -> LLMService:
    return cast(LLMService, runtime_value(state, "llm_service"))


def _access_scope(state: NlqState) -> AccessScope | None:
    return cast(AccessScope | None, runtime_value(state, "access_scope"))


def _ds_scope(llm_service: LLMService) -> tuple[int | None, int | None]:
    if not llm_service.ds:
        return None, None
    oid = llm_service.ds.oid if isinstance(llm_service.ds, CoreDatasource) else 1
    ds_id = llm_service.ds.id if isinstance(llm_service.ds, CoreDatasource) else None
    return oid, ds_id


def _ds_databases(llm_service: LLMService) -> list[str]:
    """当前数据源的物理库名（wiki scope.databases 围栏输入）。

    解析失败/REST 等无库名类型 → 空 = 不围栏（wiki 层尽力而为约定）。"""
    from apps.chat.steps.wiki_recall import datasource_databases

    return datasource_databases(llm_service.ds)


def _fail(state: NlqState, _record_id: int | None, exc: BaseException) -> NlqState:
    # This is an internal ownership fence, not a query failure.  Re-raising lets
    # the graph runtime stop a late worker without routing it through the fail
    # node or publishing a second terminal outcome.
    if isinstance(exc, ConversationRunCancelled):
        raise exc
    traceback.print_exc()
    error_msg = format_error_message(exc)
    return {
        **state,
        "error": error_msg,
        "public_error": public_error_message(exc),
        "outcome": failed_outcome(exc),
    }


def _finish_step_value(state: NlqState) -> int:
    fs = state.get("finish_step") or ChatFinishStep.GENERATE_CHART
    try:
        return int(fs.value if hasattr(fs, "value") else fs)
    except Exception:
        return int(ChatFinishStep.GENERATE_CHART.value)


def _generation_question(llm_service: Any) -> str:
    """Read the canonical user request from real or lightweight services."""
    projected = str(getattr(llm_service, "generation_question", "") or "").strip()
    if projected:
        return projected
    question = getattr(llm_service, "chat_question", None)
    return str(
        getattr(question, "generation_question", "")
        or getattr(question, "question", "")
        or ""
    ).strip()


def _sql_dialect(llm_service: LLMService) -> str | None:
    return sqlglot_dialect_for(
        getattr(getattr(llm_service, "protocol", None), "type_key", None)
    )
