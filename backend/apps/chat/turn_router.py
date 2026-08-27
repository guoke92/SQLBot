"""Cheap conversation-turn routing; never performs semantic query planning.

Routing ladder: deterministic rules → model router (one call) → payload
repair for structurally-defective model output → conservative anaphora
rescue → independent fallback. The conservative rescue matters because an
anaphoric message ("第一列…") is meaningless without its referenced turn:
losing the context (as a plain independent fallback does) derails the whole
planner, while referencing the latest turn has a far smaller blast radius.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Sequence
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
# Presentation-shaping and anaphoric wording: meaningless without the
# referenced turn, so a failed model route must not degrade to independent.
_PRESENTATION_HINTS = (
    "第一列",
    "首列",
    "第一项",
    "排在",
    "排序",
    "展示",
    "图表",
    "格式",
    "列名",
    "别名",
)
_ANAPHORA_HINTS = ("上述", "刚才", "上次", "之前", "这个", "那个", "以上")

_TASK_KINDS = frozenset({"query", "analysis", "prediction", "unsupported"})
_RELATIONS = frozenset({"independent", "continue", "revise"})
_MAX_REFERENCES = 3


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


def _coerce_references(raw: Any, allowed: Sequence[int]) -> list[int]:
    if not isinstance(raw, list | tuple):
        return []
    allowed_set = set(allowed)
    refs: list[int] = []
    for item in raw:
        try:
            rid = int(item)
        except (TypeError, ValueError):
            continue
        if rid in refs:
            continue
        if allowed_set and rid not in allowed_set:
            continue
        refs.append(rid)
    return refs[:_MAX_REFERENCES]


def _coerce_confidence(raw: Any) -> float:
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return 0.6
    return min(1.0, max(0.0, value))


def repair_route_payload(
    raw: dict[str, Any], *, candidate_record_ids: Sequence[int] = ()
) -> dict[str, Any] | None:
    """Normalize a structurally-defective model route into a valid payload.

    Repairs stay honest to what the model decided: illegal enums degrade to
    safe values, references are clipped to the candidate history, and a
    relation that requires references attaches the latest candidate only when
    the model actually asked to continue/revise. ``None`` means the payload
    carries no routing signal at all and must fall through to the rescue.
    """
    if not isinstance(raw, dict):
        return None
    if (
        str(raw.get("task_kind") or "") not in _TASK_KINDS
        and str(raw.get("relation") or "") not in _RELATIONS
    ):
        return None

    payload = dict(raw)
    task = str(payload.get("task_kind") or "").strip().lower()
    if task not in _TASK_KINDS:
        task = "query"
    payload["task_kind"] = task

    allowed = [int(item) for item in candidate_record_ids]
    refs = _coerce_references(payload.get("reference_record_ids"), allowed)
    relation = str(payload.get("relation") or "").strip().lower()
    if relation not in _RELATIONS:
        relation = "continue" if refs else "independent"

    if task == "unsupported":
        refs = []
        relation = "independent"
    elif relation in {"continue", "revise"} and not refs and allowed:
        refs = [allowed[-1]]
    elif relation == "independent" and refs:
        relation = "continue"

    if task == "analysis" and relation == "independent":
        if allowed:
            relation = "continue"
            refs = [allowed[-1]]
        else:
            task = "query"
            payload["task_kind"] = task

    payload["relation"] = relation
    payload["reference_record_ids"] = refs
    payload["confidence"] = _coerce_confidence(payload.get("confidence"))
    payload["source"] = "model"
    return payload


def _conservative_rescue(
    message: str, *, candidate_record_ids: Sequence[int]
) -> TurnRoute | None:
    """Anaphoric messages must keep their referenced turn, model or not."""
    text = " ".join(message.split())
    revision_like = any(
        word in text for word in (*_REVISION_HINTS, *_PRESENTATION_HINTS)
    )
    continuation_like = any(
        word in text for word in (*_CONTINUE_HINTS, *_ANAPHORA_HINTS)
    )
    if not (revision_like or continuation_like):
        return None
    latest = int(candidate_record_ids[-1])
    return TurnRoute(
        task_kind="query",
        relation="revise" if revision_like else "continue",
        reference_record_ids=(latest,),
        source="deterministic",
        confidence=0.6,
    )


def route_turn(
    message: str,
    *,
    reference_record_ids: tuple[int, ...] = (),
    candidate_record_ids: tuple[int, ...] = (),
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
    raw_payload: Any = None
    if model_router is not None:
        try:
            raw_payload = model_router(message)
            return TurnRoute.model_validate(raw_payload)
        except Exception:
            pass
        repaired = repair_route_payload(
            raw_payload if isinstance(raw_payload, dict) else {},
            candidate_record_ids=candidate_record_ids,
        )
        if repaired is not None:
            try:
                return TurnRoute.model_validate(repaired)
            except Exception:
                pass
    if candidate_record_ids:
        rescued = _conservative_rescue(
            message, candidate_record_ids=candidate_record_ids
        )
        if rescued is not None:
            return rescued
    # Routing failure must not block a real query.
    return TurnRoute(
        task_kind="query",
        relation="independent",
        source="fallback",
        confidence=0.35,
    )
