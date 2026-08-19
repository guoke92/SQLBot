"""Shared LLM token stream processing (domain utility; **not** SSE framing).

Frame assembly belongs to ``conversation.events`` / ``StreamSink``.
This module only normalizes raw chat-model chunks into content / reasoning pairs.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass, field
from typing import Any

from langchain_core.messages import AIMessage, BaseMessageChunk

from apps.conversation.messages import message_content_text
from apps.conversation.usage import usage_from_response
from common.core.config import settings


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
        reasoning_content_chunk = ""
        content = chunk.content
        output_content = ""

        if "reasoning_content" in chunk.additional_kwargs:
            reasoning_content = chunk.additional_kwargs.get("reasoning_content", "")
            if reasoning_content is None:
                reasoning_content = ""
            current_thinking += reasoning_content
            reasoning_content_chunk = reasoning_content

        if not in_thinking_block and current_thinking.strip() != "":
            output_content = content
            yield {
                "content": output_content,
                "reasoning_content": reasoning_content_chunk,
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
        }
        get_token_usage(chunk, token_usage)


@dataclass(frozen=True)
class LlmCallResult:
    """One completed model exchange assembled from stream chunks or invoke."""

    message: Any
    content: str
    reasoning: str
    usage: dict[str, Any] = field(default_factory=dict)


def _reasoning_from(response: Any) -> str:
    extra = getattr(response, "additional_kwargs", None) or {}
    if not isinstance(extra, dict):
        return ""
    return str(extra.get("reasoning_content") or extra.get("reasoning") or "")


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
    """
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
        for chunk in process_stream(stream_fn(messages), token_usage):
            _maybe_renew()
            content = str(chunk.get("content") or "")
            reasoning = str(chunk.get("reasoning_content") or "")
            if content:
                content_parts.append(content)
            if reasoning:
                reasoning_parts.append(reasoning)
            if on_chunk and (content or reasoning):
                on_chunk({"content": content, "reasoning_content": reasoning})
        content = "".join(content_parts)
        reasoning = "".join(reasoning_parts)
        extra = {"reasoning_content": reasoning} if reasoning else {}
        message = AIMessage(
            content=content,
            additional_kwargs=extra,
            usage_metadata=token_usage or None,
        )
        return LlmCallResult(
            message=message,
            content=content,
            reasoning=reasoning,
            usage=dict(token_usage),
        )

    response = llm.invoke(messages)
    content = message_content_text(getattr(response, "content", response))
    reasoning = _reasoning_from(response)
    if on_chunk and (content or reasoning):
        on_chunk({"content": content, "reasoning_content": reasoning})
    _maybe_renew()
    return LlmCallResult(
        message=response,
        content=content,
        reasoning=reasoning,
        usage=usage_from_response(response),
    )
