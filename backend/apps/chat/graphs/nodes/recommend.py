"""Recommend node implementations for the recommend graph.

Extracted from ``apps.chat.graphs.recommend``.
"""

from __future__ import annotations

import traceback
from typing import Any, TypedDict

from apps.chat.models.chat_model import ChatRecord
from apps.chat.steps.recommend import generate_recommend_questions
from apps.chat.task.llm import LLMService
from apps.conversation.session import session_scope
from apps.conversation.sink import StreamSink
from apps.conversation.state import RunState


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
            }
        except Exception:
            traceback.print_exc()
            return state
