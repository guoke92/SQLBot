"""Recommend-questions side graph — sole path for /recommend_questions/{id}.

Control flow::

    start → generate → end

Errors are swallowed (historic behaviour): only traceback is printed.
"""

from __future__ import annotations

import traceback
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from apps.chat.models.chat_model import ChatRecord
from apps.chat.steps.recommend import generate_recommend_questions
from apps.chat.task.llm import LLMService
from apps.conversation.registry import register_graph
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
            # Historic path: recommend swallows errors (only prints traceback)
            traceback.print_exc()
            return state


def build_recommend_graph(_ctx: Any = None, **_kwargs: Any):
    g = StateGraph(RecommendState)
    g.add_node("generate", generate_node)
    g.add_edge(START, "generate")
    g.add_edge("generate", END)
    return g.compile()


register_graph("recommend", build_recommend_graph)
