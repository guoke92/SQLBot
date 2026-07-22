"""Target ChatState — shared state for the unified chat graph.

NLQ path uses the agentic batch-loop fields (same contract as
``apps.chat.graphs.nodes.nlq.NlqState``). Dialogue path adds intent/evidence.
Single-query fields (plan/sql/chart/query_result) are intentionally absent.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from apps.chat.models.chat_model import ChatFinishStep
from apps.chat.task.llm import LLMService
from apps.conversation.state import RunState


class ChatState(RunState, total=False):
    """Unified chat run state — nlq batch loop + dialogue path."""

    # ── common turn ──
    llm_service: LLMService
    finish_step: ChatFinishStep
    return_img: bool
    json_result: Dict[str, Any]
    intent: str  # TurnRouter: nlq_new / explain / critique / …
    anchor: Any

    # ── nlq agentic batch loop (canonical; see nodes.nlq.NlqState) ──
    step_index: int
    batch_plans: List[Dict[str, Any]]
    batch_results: List[Dict[str, Any]]
    batch_charts: List[Dict[str, Any]]
    all_steps: List[Dict[str, Any]]
    analysis_text: str
    max_steps: int
    max_batch_size: int
    decision: str
    repair_hint: str
    gen_attempts: int
    entity_bindings: Dict[str, Any]
    query_bindings: Dict[str, Any]

    # ── dialogue_path ──
    evidence: Any
    diagnosis: Dict[str, Any]
    pending_brief: Optional[str]
