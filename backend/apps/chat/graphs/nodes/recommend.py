"""Recommend node implementations for the recommend graph."""

from __future__ import annotations

from apps.chat.models.chat_model import ChatRecord
from apps.chat.steps.recommend import generate_recommend_questions
from apps.chat.task.llm import LLMService
from apps.conversation.outcome import (
    failed_outcome,
    format_error_message,
    successful_outcome,
)
from apps.conversation.session import session_scope
from apps.conversation.sink import StreamSink
from apps.conversation.state import RunState
from common.utils.utils import SQLBotLogUtil


class RecommendState(RunState, total=False):
    llm_service: LLMService
    record: ChatRecord


def generate_node(state: RecommendState) -> RecommendState:
    llm_service = state["llm_service"]
    sink = StreamSink.from_state(state)
    with session_scope() as session:
        try:
            for chunk in generate_recommend_questions(llm_service, session):
                if chunk.get("recommended_question"):
                    sink.event(
                        {
                            "content": chunk.get("recommended_question"),
                            "type": "recommended_question",
                        }
                    )
                else:
                    sink.event(
                        {
                            "content": chunk.get("content"),
                            "reasoning_content": chunk.get("reasoning_content"),
                            "type": "recommended_question_result",
                        }
                    )
            return {
                **state,
                "graph_key": "recommend",
                "mode": "side",
                "record": llm_service.record,
                "outcome": successful_outcome(),
            }
        except Exception as exc:
            error = format_error_message(exc)
            SQLBotLogUtil.warning(f"recommend graph failed: {error}")
            sink.event({"type": "recommended_question_error", "content": error})
            return {
                **state,
                "graph_key": "recommend",
                "mode": "side",
                "error": error,
                "outcome": failed_outcome(exc),
            }
