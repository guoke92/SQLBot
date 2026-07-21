"""Target ChatState — shared state for the unified chat graph.

This is the architecture-draft TypedDict for the target chat graph with
nlq_path + dialogue_path. Currently stubbed for compile-ability only.
"""

from __future__ import annotations

from typing import Any, Dict, Literal, Optional

from apps.conversation.state import RunState
from apps.chat.models.chat_model import ChatFinishStep
from apps.chat.task.llm import LLMService


class ChatState(RunState, total=False):
    """Unified chat run state — nlq + dialogue paths share this TypedDict."""

    # ── common turn ──
    llm_service: LLMService
    finish_step: ChatFinishStep
    return_img: bool
    json_result: Dict[str, Any]
    intent: str  # TurnRouter output: nlq_new / regenerate / explain_… / critique / …
    anchor: Any  # Working Set anchor ref for multi-turn

    # ── nlq_path ──
    plan: Any
    sql: Optional[str]
    format_statement: Optional[str]
    chart_type: Optional[str]
    full_sql_text: str
    dynamic_sql_result: Any
    sqlbot_temp_sql_text: Optional[str]
    assistant_dynamic_sql: Optional[str]
    query_result: Dict[str, Any]
    chart: Dict[str, Any]

    # ── dialogue_path ──
    evidence: Any  # Working Set context block
    diagnosis: Dict[str, Any]  # structured dialogue output
    pending_brief: Optional[str]  # RepairBrief to inject into next NLQ turn
