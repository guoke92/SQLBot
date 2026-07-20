"""Shared LLM token stream processing (domain utility; **not** SSE framing).

Frame assembly belongs to ``conversation.events`` / ``StreamSink``.
This module only normalizes raw chat-model chunks into content / reasoning pairs.
"""

from __future__ import annotations

from typing import Any, Dict, Iterator

from langchain_core.messages import BaseMessageChunk

from common.core.config import settings
from common.utils.utils import SQLBotLogUtil


def get_token_usage(
    chunk: BaseMessageChunk, token_usage: dict | None = None
) -> None:
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
    token_usage: Dict[str, Any] | None = None,
    enable_tag_parsing: bool = settings.PARSE_REASONING_BLOCK_ENABLED,
    start_tag: str = settings.DEFAULT_REASONING_CONTENT_START,
    end_tag: str = settings.DEFAULT_REASONING_CONTENT_END,
) -> Iterator[Dict[str, Any]]:
    """Yield ``{content, reasoning_content}`` for every model chunk."""
    if token_usage is None:
        token_usage = {}
    in_thinking_block = False
    current_thinking = ""
    pending_start_tag = ""

    for chunk in res:
        SQLBotLogUtil.info(chunk)
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
