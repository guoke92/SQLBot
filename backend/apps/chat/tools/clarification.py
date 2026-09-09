"""Clarification interrupt tool for resolving critical ambiguities."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from apps.chat.semantic_planning import (
    ClarificationCard,
    coerce_clarification_questions,
)
from apps.chat.tools.base import failure_result, success_result
from apps.conversation.tooling import ToolResult


def _norm(value: Any) -> str:
    return str(value or "").strip()


def _option_grounded(
    option: Mapping[str, Any], catalog: Mapping[str, set[str]]
) -> bool:
    """True when the option cites a real table/field in ``catalog``."""
    table = _norm(option.get("table") or option.get("table_name"))
    field = _norm(option.get("field") or option.get("field_name"))
    refs: list[tuple[str, str]] = []
    raw_fields = option.get("fields")
    if isinstance(raw_fields, list):
        for item in raw_fields:
            if not isinstance(item, Mapping):
                continue
            refs.append(
                (
                    _norm(item.get("table") or item.get("table_name") or table),
                    _norm(
                        item.get("name") or item.get("field") or item.get("field_name")
                    ),
                )
            )
    if table or field:
        refs.append((table, field))
    if not refs:
        return False
    lower_catalog = {
        key.casefold(): {item.casefold() for item in values}
        for key, values in catalog.items()
    }
    matched = False
    for tbl, fname in refs:
        if not tbl and not fname:
            continue
        if tbl:
            fields_set = lower_catalog.get(tbl.casefold())
            if fields_set is None:
                return False
            if fname and fname.casefold() not in fields_set:
                return False
            matched = True
            continue
        if fname and any(
            fname.casefold() in values for values in lower_catalog.values()
        ):
            matched = True
            continue
        return False
    return matched


def _ground_questions(
    questions: Sequence[dict[str, Any]], catalog: Mapping[str, set[str]]
) -> list[dict[str, Any]]:
    grounded: list[dict[str, Any]] = []
    for question in questions:
        options = [
            option
            for option in (question.get("options") or [])
            if isinstance(option, dict) and _option_grounded(option, catalog)
        ]
        if len(options) < 2:
            continue
        grounded.append({**question, "options": options})
    return grounded


def request_clarification(
    questions: Sequence[dict[str, Any]],
    *,
    catalog: Mapping[str, set[str]] | None = None,
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
                if o.get("table") is None:
                    o["table"] = o.get("table_name") or ""
                if o.get("field") is None:
                    o["field"] = o.get("field_name") or ""
                norm_opts.append(o)
            item["options"] = norm_opts
            normalized_questions.append(item)

        if catalog is not None:
            normalized_questions = _ground_questions(normalized_questions, catalog)
            if not normalized_questions:
                return failure_result(
                    "Clarification options must map to real tables or fields; "
                    "invented products or objects were dropped.",
                    retryable=True,
                )

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
