"""Shared LLM token stream processing (domain utility; **not** SSE framing).

Frame assembly belongs to ``conversation.events`` / ``StreamSink``.
This module only normalizes raw chat-model chunks into content / reasoning pairs.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass, field
from typing import Any

from langchain_core.messages import AIMessage, AIMessageChunk, BaseMessageChunk

from apps.ai_model.runtime import (
    has_reasoning_payload,
    has_structured_content,
    normalize_message_parts,
)
from apps.conversation.usage import usage_from_response
from common.core.config import settings
from common.utils.utils import SQLBotLogUtil

_NON_RETRYABLE_STATUS = frozenset({400, 401, 403, 404, 409, 422})
_RETRYABLE_STATUS = frozenset({408, 425, 429, 500, 502, 503, 504, 529})
_RETRYABLE_NAME_TOKENS = (
    "ratelimit",
    "timeout",
    "connection",
    "unavailable",
    "internalserver",
    "apiconnection",
    "apistatus",
)
_RETRYABLE_TEXT_TOKENS = (
    "rate limit",
    "ratelimit",
    "too many requests",
    "tpm",
    "timeout",
    "temporar",
    "connection reset",
    "econnreset",
    "service unavailable",
    "429",
    "502",
    "503",
    "529",
)
_NON_RETRYABLE_TEXT_TOKENS = (
    "invalid_request",
    "invalid request",
    "context length",
    "maximum context",
    "context_length_exceeded",
    "authentication",
    "unauthorized",
    "permission denied",
)


def get_token_usage(chunk: BaseMessageChunk, token_usage: dict | None = None) -> None:
    try:
        if chunk.usage_metadata:
            if token_usage is None:
                return
            token_usage["input_tokens"] = chunk.usage_metadata.get("input_tokens")
            token_usage["output_tokens"] = chunk.usage_metadata.get("output_tokens")
            token_usage["total_tokens"] = chunk.usage_metadata.get("total_tokens")
    except Exception:
        pass


def process_stream(
    res: Iterator[BaseMessageChunk],
    token_usage: dict[str, Any] | None = None,
    enable_tag_parsing: bool = settings.PARSE_REASONING_BLOCK_ENABLED,
    start_tag: str = settings.DEFAULT_REASONING_CONTENT_START,
    end_tag: str = settings.DEFAULT_REASONING_CONTENT_END,
) -> Iterator[dict[str, Any]]:
    """Yield ``{content, reasoning_content}`` for every model chunk."""
    if token_usage is None:
        token_usage = {}
    in_thinking_block = False
    current_thinking = ""
    pending_start_tag = ""

    for chunk in res:
        parts = normalize_message_parts(chunk)
        reasoning_content_chunk = parts.reasoning
        content = parts.content
        output_content = ""

        if reasoning_content_chunk:
            current_thinking += reasoning_content_chunk

        has_reasoning = bool(reasoning_content_chunk) or has_reasoning_payload(chunk)
        if not in_thinking_block and current_thinking.strip() != "":
            yield {
                "content": content,
                "reasoning_content": reasoning_content_chunk,
                "has_reasoning": has_reasoning,
            }
            get_token_usage(chunk, token_usage)
            continue

        if pending_start_tag:
            content = pending_start_tag + content
            pending_start_tag = ""

        if enable_tag_parsing and not in_thinking_block and start_tag:
            if start_tag in content:
                start_idx = content.index(start_tag)
                if start_idx == 0 or content[:start_idx].strip() == "":
                    output_content += content[:start_idx]
                    content = content[start_idx + len(start_tag) :]
                    in_thinking_block = True
                else:
                    output_content += content
                    content = ""
            else:
                for i in range(1, len(start_tag)):
                    if content.endswith(start_tag[:i]):
                        if content[:-i].strip() == "":
                            pending_start_tag = start_tag[:i]
                            content = content[:-i]
                            output_content += content
                            content = ""
                        break

        if enable_tag_parsing and in_thinking_block and end_tag:
            if end_tag in content:
                end_idx = content.index(end_tag)
                current_thinking += content[:end_idx]
                reasoning_content_chunk += current_thinking
                content = content[end_idx + len(end_tag) :]
                current_thinking = ""
                in_thinking_block = False
                output_content += content
            else:
                current_thinking += content
                reasoning_content_chunk += content
                content = ""
        else:
            output_content += content

        yield {
            "content": output_content,
            "reasoning_content": reasoning_content_chunk,
            "has_reasoning": bool(reasoning_content_chunk)
            or has_reasoning_payload(chunk),
        }
        get_token_usage(chunk, token_usage)


@dataclass(frozen=True)
class LlmCallResult:
    """One completed model exchange assembled from stream chunks or invoke."""

    message: Any
    content: str
    reasoning: str
    usage: dict[str, Any] = field(default_factory=dict)


def _attach_reasoning(message: Any, reasoning: str) -> Any:
    if not reasoning:
        return message
    extra = dict(getattr(message, "additional_kwargs", None) or {})
    extra["reasoning_content"] = reasoning
    copier = getattr(message, "model_copy", None)
    if callable(copier):
        return copier(update={"additional_kwargs": extra})
    try:
        message.additional_kwargs = extra
    except Exception:
        pass
    return message


def _message_from_gathered(
    gathered: Any,
    content: str,
    reasoning: str,
    token_usage: dict[str, Any],
) -> Any:
    extra = dict(getattr(gathered, "additional_kwargs", None) or {})
    if reasoning:
        extra["reasoning_content"] = reasoning
    tool_calls = list(getattr(gathered, "tool_calls", None) or [])
    invalid_tool_calls = list(getattr(gathered, "invalid_tool_calls", None) or [])
    usage = token_usage or getattr(gathered, "usage_metadata", None)
    if gathered is not None and has_structured_content(gathered):
        if isinstance(gathered, AIMessage) and not isinstance(gathered, AIMessageChunk):
            updates: dict[str, Any] = {"additional_kwargs": extra}
            if usage:
                updates["usage_metadata"] = usage
            copier = getattr(gathered, "model_copy", None)
            if callable(copier):
                return copier(update=updates)
        return AIMessage(
            content=getattr(gathered, "content", content),
            additional_kwargs=extra,
            tool_calls=tool_calls,
            invalid_tool_calls=invalid_tool_calls,
            usage_metadata=usage,
            response_metadata=dict(getattr(gathered, "response_metadata", None) or {}),
            id=getattr(gathered, "id", None),
        )
    message_kwargs: dict[str, Any] = {
        "content": content,
        "additional_kwargs": extra,
        "usage_metadata": usage,
    }
    if tool_calls:
        message_kwargs["tool_calls"] = tool_calls
    if invalid_tool_calls:
        message_kwargs["invalid_tool_calls"] = invalid_tool_calls
    return AIMessage(**message_kwargs)


def _llm_retry_limit() -> int:
    try:
        return max(0, min(int(settings.LLM_MAX_RETRIES), 5))
    except Exception:
        return 2


def _llm_retry_backoff_sec() -> float:
    try:
        return max(0.2, min(float(settings.LLM_RETRY_BACKOFF_SEC), 15.0))
    except Exception:
        return 1.0


def _status_code_from_exc(exc: BaseException) -> int | None:
    for attr in ("status_code", "http_status"):
        raw = getattr(exc, attr, None)
        if isinstance(raw, int) and 100 <= raw <= 599:
            return raw
        if isinstance(raw, str) and raw.isdigit():
            code = int(raw)
            if 100 <= code <= 599:
                return code
    response = getattr(exc, "response", None)
    raw = getattr(response, "status_code", None)
    if isinstance(raw, int) and 100 <= raw <= 599:
        return raw
    return None


def _retry_after_sec(exc: BaseException) -> float | None:
    response = getattr(exc, "response", None)
    headers = getattr(response, "headers", None)
    if headers is None:
        return None
    try:
        raw = headers.get("Retry-After") or headers.get("retry-after")
    except Exception:
        return None
    if raw is None:
        return None
    try:
        return max(0.2, min(float(raw), 30.0))
    except (TypeError, ValueError):
        return None


def llm_error_is_retryable(exc: BaseException) -> bool:
    """True for provider rate-limit / timeout / transient transport failures."""
    from apps.conversation.run_service import ConversationRunCancelled

    if isinstance(exc, ConversationRunCancelled):
        return False
    status = _status_code_from_exc(exc)
    if status in _NON_RETRYABLE_STATUS:
        return False
    if status in _RETRYABLE_STATUS:
        return True
    text = str(exc).lower()
    if any(token in text for token in _NON_RETRYABLE_TEXT_TOKENS):
        return False
    name = type(exc).__name__.lower()
    if any(token in name for token in _RETRYABLE_NAME_TOKENS):
        return True
    return any(token in text for token in _RETRYABLE_TEXT_TOKENS)


def consume_llm(
    llm: Any,
    messages: Sequence[Any],
    *,
    on_chunk: Callable[[dict[str, str]], None] | None = None,
) -> LlmCallResult:
    """Prefer streaming so reasoning can be forwarded before the call ends.

    Providers without ``stream`` (and tests that only stub ``invoke``) fall
    back to a single blocking response. Storage is always the assembled
    assistant message plus reasoning text — never the raw chunk list.
    Transient provider errors (429 / timeout / connection) are retried a
    bounded number of times using ``LLM_MAX_RETRIES``.
    """
    retries = _llm_retry_limit()
    attempt = 0
    while True:
        try:
            return _consume_llm_once(llm, messages, on_chunk=on_chunk)
        except Exception as exc:
            if attempt >= retries or not llm_error_is_retryable(exc):
                raise
            delay = _retry_after_sec(exc)
            if delay is None:
                delay = min(_llm_retry_backoff_sec() * (2**attempt), 30.0)
            SQLBotLogUtil.warning(
                "LLM call retry %s/%s after %.1fs: %s",
                attempt + 1,
                retries,
                delay,
                exc,
            )
            time.sleep(delay)
            attempt += 1


def _consume_llm_once(
    llm: Any,
    messages: Sequence[Any],
    *,
    on_chunk: Callable[[dict[str, str]], None] | None = None,
) -> LlmCallResult:
    from apps.conversation.run_service import (
        lease_renew_interval_sec,
        renew_owned_run_lease,
    )

    interval = float(lease_renew_interval_sec())
    last_renew = time.monotonic()

    def _maybe_renew() -> None:
        nonlocal last_renew
        now = time.monotonic()
        if now - last_renew < interval:
            return
        last_renew = now
        renew_owned_run_lease()

    stream_fn = getattr(llm, "stream", None)
    if callable(stream_fn):
        token_usage: dict[str, Any] = {}
        content_parts: list[str] = []
        reasoning_parts: list[str] = []
        gathered_box: list[Any] = [None]

        def _raw_stream() -> Iterator[Any]:
            for raw in stream_fn(messages):
                current = gathered_box[0]
                if current is None:
                    gathered_box[0] = raw
                else:
                    try:
                        gathered_box[0] = current + raw
                    except Exception:
                        gathered_box[0] = raw
                yield raw

        for chunk in process_stream(_raw_stream(), token_usage):
            _maybe_renew()
            content = str(chunk.get("content") or "")
            reasoning = str(chunk.get("reasoning_content") or "")
            has_reasoning = bool(chunk.get("has_reasoning") or reasoning)
            if content:
                content_parts.append(content)
            if reasoning:
                reasoning_parts.append(reasoning)
            if on_chunk and (content or reasoning or has_reasoning):
                gathered = gathered_box[0]
                has_tool_calls = bool(
                    getattr(gathered, "tool_calls", None)
                    or getattr(gathered, "tool_call_chunks", None)
                )
                on_chunk(
                    {
                        "content": content,
                        "reasoning_content": reasoning,
                        "has_tool_calls": has_tool_calls,
                        "has_reasoning": has_reasoning,
                    }
                )
        content = "".join(content_parts)
        reasoning = "".join(reasoning_parts)
        gathered = gathered_box[0]
        message = _message_from_gathered(gathered, content, reasoning, token_usage)
        return LlmCallResult(
            message=message,
            content=content,
            reasoning=reasoning,
            usage=dict(token_usage),
        )

    response = llm.invoke(messages)
    parts = normalize_message_parts(response)
    content = parts.content
    reasoning = parts.reasoning
    response = _attach_reasoning(response, reasoning)
    if on_chunk and (content or reasoning):
        on_chunk(
            {
                "content": content,
                "reasoning_content": reasoning,
                "has_tool_calls": bool(getattr(response, "tool_calls", None)),
            }
        )
    _maybe_renew()
    return LlmCallResult(
        message=response,
        content=content,
        reasoning=reasoning,
        usage=usage_from_response(response),
    )
