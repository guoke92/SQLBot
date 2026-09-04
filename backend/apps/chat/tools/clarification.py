"""Clarification interrupt tool for resolving critical ambiguities."""

from __future__ import annotations

from typing import Any, Sequence
from apps.chat.semantic_planning import ClarificationCard, coerce_clarification_questions
from apps.chat.tools.base import failure_result, success_result
from apps.conversation.tooling import ToolResult


def request_clarification(
    questions: Sequence[dict[str, Any]],
) -> ToolResult:
    """Trigger a clarification interrupt to ask user for confirmation on critical caliber ambiguities."""
    if not questions:
        return failure_result("No clarification questions provided", retryable=False)

    try:
        # Pre-process questions to flexibly adapt LLM parameter variations
        # (e.g. prompt -> question, description -> meaning, text -> question)
        normalized_questions = []
        for q in questions:
            if not isinstance(q, dict):
                continue
            item = dict(q)
            q_text = item.get("question") or item.get("prompt") or item.get("text") or item.get("business_question") or ""
            item["question"] = q_text
            
            raw_opts = item.get("options") or item.get("candidate_resolutions") or []
            norm_opts = []
            for opt in raw_opts:
                if not isinstance(opt, dict):
                    continue
                o = dict(opt)
                label = o.get("label") or o.get("text") or o.get("name") or o.get("meaning") or ""
                desc = o.get("description") or o.get("meaning") or o.get("desc") or label
                o["label"] = label
                o["meaning"] = desc
                norm_opts.append(o)
            item["options"] = norm_opts
            normalized_questions.append(item)

        coerced = coerce_clarification_questions(normalized_questions)
        card = ClarificationCard.model_validate({"questions": coerced})
        return success_result(
            f"Prepared clarification card with {len(card.questions)} questions.",
            data={
                "interrupt_required": True,
                "clarification_card": card.model_dump(mode="json"),
            },
        )
    except Exception as exc:
        return failure_result(f"Failed to build clarification card: {exc}", retryable=True)
