"""Cheap conversation-turn routing; never performs semantic query planning."""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

from apps.chat.turn_contracts import TurnRoute

_GREETING = re.compile(
    r"^\s*(你好|您好|嗨|hi|hello|谢谢|感谢|再见)[!！,.，。\s]*$",
    re.IGNORECASE,
)
_ANALYSIS_HINTS = ("分析", "解释", "为什么", "对比", "比较", "洞察")
_PREDICTION_HINTS = ("预测", "预估", "趋势", "未来")
_REVISION_HINTS = ("改成", "改为", "不要", "换成", "修正", "重新按")
_CONTINUE_HINTS = ("继续", "再加", "另外", "基于", "其中", "再看", "然后")


def deterministic_route(
    message: str,
    *,
    reference_record_ids: tuple[int, ...] = (),
    route_hint: str | None = None,
    has_history: bool = False,
) -> TurnRoute | None:
    """Resolve explicit and obvious routes without spending a model call."""
    text = " ".join(message.split()).strip()
    if route_hint:
        hint = route_hint.strip().casefold()
        task = {
            "query": "query",
            "analysis": "analysis",
            "predict": "prediction",
            "prediction": "prediction",
            "unsupported": "unsupported",
        }.get(hint)
        if task is None:
            raise ValueError(f"Unsupported route hint: {route_hint}")
        relation = "continue" if reference_record_ids else "independent"
        return TurnRoute(
            task_kind=task,
            relation=relation,
            reference_record_ids=reference_record_ids,
            source="hint",
        )
    if _GREETING.fullmatch(text):
        return TurnRoute(
            task_kind="unsupported",
            relation="independent",
            source="deterministic",
        )
    if not has_history:
        # First-turn uncertainty is conservatively routed to query.  A greeting
        # prefix cannot hide a real data request because only full-match short
        # greetings are rejected above.
        task = (
            "prediction" if any(word in text for word in _PREDICTION_HINTS) else "query"
        )
        return TurnRoute(
            task_kind=task,
            relation="independent",
            reference_record_ids=reference_record_ids,
            source="deterministic",
        )
    if reference_record_ids:
        task = (
            "prediction"
            if any(word in text for word in _PREDICTION_HINTS)
            else "analysis"
            if any(word in text for word in _ANALYSIS_HINTS)
            else "query"
        )
        relation = (
            "revise" if any(word in text for word in _REVISION_HINTS) else "continue"
        )
        return TurnRoute(
            task_kind=task,
            relation=relation,
            reference_record_ids=reference_record_ids,
            source="deterministic",
            confidence=0.9,
        )
    if any(word in text for word in (*_REVISION_HINTS, *_CONTINUE_HINTS)):
        # The caller must resolve concrete history references before accepting
        # a continuation.  Returning None delegates only this relation choice.
        return None
    return None


def route_turn(
    message: str,
    *,
    reference_record_ids: tuple[int, ...] = (),
    route_hint: str | None = None,
    has_history: bool = False,
    model_router: Callable[[str], dict[str, Any]] | None = None,
) -> TurnRoute:
    route = deterministic_route(
        message,
        reference_record_ids=reference_record_ids,
        route_hint=route_hint,
        has_history=has_history,
    )
    if route is not None:
        return route
    if model_router is not None:
        try:
            return TurnRoute.model_validate(model_router(message))
        except Exception:
            pass
    # Routing failure must not block a real query.
    return TurnRoute(
        task_kind="query",
        relation="independent",
        source="fallback",
        confidence=0.35,
    )
