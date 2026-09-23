"""LLM runtime adapter: wire capabilities and product-level message parts.

Orchestration and the process timeline consume ``content`` / ``reasoning`` only.
Chat Completions vs Responses stays inside factory construction and this module.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal

from apps.conversation.messages import (
    message_content_text,
    message_reasoning_text,
    reasoning_text_from_value,
)

WireKind = Literal["completions", "responses"]
# Product + Responses wire levels (DeepSeek: none/low/high/max).
# Incoming aliases: medium/xhigh → high, minimal → low, ultra → max.
ReasoningEffort = Literal["none", "low", "high", "max"]
ALLOWED_REASONING_EFFORTS: frozenset[str] = frozenset({"none", "low", "high", "max"})
_EFFORT_ALIASES: dict[str, ReasoningEffort] = {
    "minimal": "low",
    "medium": "high",
    "xhigh": "high",
    "ultra": "max",
}


@dataclass(frozen=True)
class LlmCapabilities:
    """Product-facing LLM transport capabilities."""

    wire: WireKind
    reasoning: dict[str, Any] | None = None


@dataclass(frozen=True)
class MessageParts:
    """Visible answer text plus thought text, independent of the wire protocol."""

    content: str
    reasoning: str


def _as_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, int | float) and value in (0, 1):
        return bool(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes"}:
            return True
        if lowered in {"false", "0", "no", ""}:
            return False
    return None


def _as_reasoning_dict(value: Any) -> dict[str, Any] | None:
    if isinstance(value, Mapping):
        return dict(value)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        if stripped[0] == "{":
            try:
                parsed = json.loads(stripped)
            except json.JSONDecodeError:
                return None
            if isinstance(parsed, Mapping):
                return dict(parsed)
    return None


def _as_effort(value: Any) -> str | None:
    if value is None or isinstance(value, bool):
        return None
    text = str(value).strip()
    return text or None


def normalize_reasoning_effort(value: Any) -> ReasoningEffort | None:
    """Accept product effort levels; map known aliases; ignore unknowns."""
    effort = _as_effort(value)
    if effort is None:
        return None
    lowered = effort.lower()
    if lowered in ALLOWED_REASONING_EFFORTS:
        return lowered  # type: ignore[return-value]
    return _EFFORT_ALIASES.get(lowered)


def overlay_reasoning_effort(
    additional_params: Mapping[str, Any] | None, effort: Any
) -> dict[str, Any]:
    """Copy model params and replace ``reasoning_effort`` when a valid override is set."""
    params = dict(additional_params or {})
    normalized = normalize_reasoning_effort(effort)
    if normalized:
        params["reasoning_effort"] = normalized
    return params


def resolve_llm_capabilities(
    additional_params: Mapping[str, Any] | None,
) -> tuple[LlmCapabilities, dict[str, Any]]:
    """Split wire capabilities from remaining ChatOpenAI constructor kwargs.

    ``extra_body.enable_thinking`` is left untouched so Qwen Completions thinking
    does not get rewritten as Responses ``reasoning.effort``.

    ``reasoning_effort=none`` disables thinking. Alone it does not force the
    Responses wire; an explicit ``use_responses_api`` (or a non-none effort)
    still opts into Responses.
    """
    params = dict(additional_params or {})
    raw_flag = params.pop("use_responses_api", None)
    raw_reasoning = params.pop("reasoning", None)
    raw_effort = params.pop("reasoning_effort", None)

    reasoning = _as_reasoning_dict(raw_reasoning)
    if _as_effort(raw_effort):
        reasoning = {**(reasoning or {}), "effort": raw_effort}

    normalized = (
        normalize_reasoning_effort((reasoning or {}).get("effort"))
        if reasoning
        else None
    )
    if reasoning is not None and normalized is not None:
        reasoning = {**reasoning, "effort": normalized}
    elif reasoning is not None and "effort" in reasoning and normalized is None:
        # Drop unknown effort values rather than forwarding them on the wire.
        reasoning = {k: v for k, v in reasoning.items() if k != "effort"} or None

    flag = _as_bool(raw_flag) is True
    # Non-none effort opts into Responses; none alone stays on Completions unless
    # the model already opted into Responses.
    use_responses = flag or (normalized is not None and normalized != "none")
    if use_responses:
        capabilities = LlmCapabilities(wire="responses", reasoning=reasoning)
    elif normalized == "none":
        capabilities = LlmCapabilities(
            wire="completions", reasoning={"effort": "none"}
        )
    else:
        capabilities = LlmCapabilities(wire="completions", reasoning=None)
    return capabilities, params


def apply_openai_ctor_kwargs(
    additional_params: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Constructor kwargs with Completions pinned unless Responses is opted in.

    Responses: ``reasoning.effort`` (``none`` disables thinking per DeepSeek).
    Completions: ``none`` maps to DeepSeek ``thinking.type=disabled`` / Qwen
    ``enable_thinking=false`` without switching wire protocols.
    """
    capabilities, params = resolve_llm_capabilities(additional_params)
    params["use_responses_api"] = capabilities.wire == "responses"
    if capabilities.wire == "responses":
        reasoning = dict(capabilities.reasoning or {})
        effort = normalize_reasoning_effort(reasoning.get("effort"))
        # DeepSeek accepts ``summary`` but never generates one; omit it so the
        # wire payload stays effort-only and echo uses ``reasoning_text``.
        reasoning.pop("summary", None)
        if effort == "none":
            reasoning["effort"] = "none"
        params["reasoning"] = reasoning
    elif (
        capabilities.reasoning
        and normalize_reasoning_effort(capabilities.reasoning.get("effort")) == "none"
    ):
        extra = dict(params.get("extra_body") or {})
        thinking = extra.get("thinking")
        if not isinstance(thinking, Mapping):
            extra["thinking"] = {"type": "disabled"}
        if "enable_thinking" in extra:
            extra["enable_thinking"] = False
        params["extra_body"] = extra
    return params


def _kwargs_reasoning_value(message: Any) -> Any:
    extra = getattr(message, "additional_kwargs", None) or {}
    if not isinstance(extra, Mapping):
        extra = {}
    for key in ("reasoning_content", "reasoning"):
        if extra.get(key) not in (None, ""):
            return extra.get(key)
    return getattr(message, "reasoning_content", None)


def normalize_message_parts(message: Any) -> MessageParts:
    """Extract visible content and thought from a LangChain message or chunk."""
    raw_content = getattr(message, "content", message)
    visible = message_content_text(raw_content)
    kwargs_text = reasoning_text_from_value(_kwargs_reasoning_value(message))
    block_reasoning = message_reasoning_text(raw_content)
    return MessageParts(content=visible, reasoning=f"{kwargs_text}{block_reasoning}")


def has_reasoning_payload(message: Any) -> bool:
    """True when this chunk carries a reasoning item, even without visible text."""
    if normalize_message_parts(message).reasoning.strip():
        return True
    value = _kwargs_reasoning_value(message)
    if isinstance(value, Mapping) and (
        str(value.get("type") or "") == "reasoning"
        or "encrypted_content" in value
        or "summary" in value
    ):
        return True
    content = getattr(message, "content", None)
    if isinstance(content, Mapping) and (
        str(content.get("type") or "") == "reasoning" or "encrypted_content" in content
    ):
        return True
    if isinstance(content, list | tuple):
        for item in content:
            if isinstance(item, Mapping) and (
                str(item.get("type") or "") == "reasoning"
                or "encrypted_content" in item
            ):
                return True
    return False


def has_structured_content(message: Any) -> bool:
    """True when the assembled message must keep provider content blocks."""
    if message is None:
        return False
    content = getattr(message, "content", None)
    if isinstance(content, list | tuple):
        return True
    metadata = getattr(message, "response_metadata", None) or {}
    if isinstance(metadata, Mapping):
        ident = str(metadata.get("id") or "")
        if ident.startswith("resp_"):
            return True
    return False
