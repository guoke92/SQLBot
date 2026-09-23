"""OpenAI-compatible provider bridges for langchain-openai 0.3.

1. DeepSeek Responses streams CoT on ``response.reasoning_text.delta``; langchain
   0.3 only converts OpenAI ``response.reasoning_summary_text.delta``.
2. DeepSeek Chat Completions with tools requires ``reasoning_content`` to be
   echoed on subsequent assistant messages; langchain's converter drops it.
3. DeepSeek Responses input accepts plaintext ``reasoning.content[].reasoning_text``
   only — OpenAI ``summary`` / ``encrypted_content`` are ignored on echo.
4. Some compatible gateways emit ``response.output_item.*`` with ``item`` as a
   plain dict. langchain reads ``item.type`` / ``item.model_dump``.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from langchain_core.messages import AIMessage


class _ReasoningTextDeltaAlias:
    """Present a DeepSeek reasoning_text delta as an OpenAI summary-text delta."""

    __slots__ = ("_inner",)

    def __init__(self, inner: Any) -> None:
        self._inner = inner

    @property
    def type(self) -> str:
        return "response.reasoning_summary_text.delta"

    @property
    def summary_index(self) -> int:
        value = _chunk_attr(self._inner, "content_index")
        if value is None:
            value = _chunk_attr(self._inner, "summary_index")
        try:
            return int(value or 0)
        except (TypeError, ValueError):
            return 0

    @property
    def delta(self) -> str:
        value = _chunk_attr(self._inner, "delta")
        if value is None:
            value = _chunk_attr(self._inner, "text")
        return str(value or "")

    def __getattr__(self, name: str) -> Any:
        inner = self._inner
        if isinstance(inner, Mapping):
            if name in inner:
                return inner[name]
            raise AttributeError(name)
        return getattr(inner, name)


def _chunk_attr(chunk: Any, name: str) -> Any:
    if isinstance(chunk, Mapping):
        return chunk.get(name)
    return getattr(chunk, name, None)


def _chunk_type(chunk: Any) -> str:
    return str(_chunk_attr(chunk, "type") or "")


def alias_reasoning_text_delta(chunk: Any) -> Any:
    """Map DeepSeek CoT deltas onto the converter branch langchain already handles."""
    if _chunk_type(chunk) != "response.reasoning_text.delta":
        return chunk
    return _ReasoningTextDeltaAlias(chunk)


class _MappingView:
    """Attribute access for a provider dict, including ``model_dump``."""

    __slots__ = ("_data",)

    def __init__(self, data: Mapping[str, Any]) -> None:
        object.__setattr__(self, "_data", data)

    def __getattr__(self, name: str) -> Any:
        data = object.__getattribute__(self, "_data")
        if name not in data:
            return None
        value = data[name]
        if isinstance(value, Mapping):
            return _MappingView(value)
        return value

    def model_dump(
        self,
        *,
        exclude_none: bool = False,
        mode: str = "python",
        **_: Any,
    ) -> dict[str, Any]:
        del mode
        return _dump_mapping(object.__getattribute__(self, "_data"), exclude_none)


def _dump_mapping(value: Any, exclude_none: bool) -> Any:
    if isinstance(value, Mapping):
        dumped: dict[str, Any] = {}
        for key, item in value.items():
            if exclude_none and item is None:
                continue
            dumped[str(key)] = _dump_mapping(item, exclude_none)
        return dumped
    if isinstance(value, Sequence) and not isinstance(value, str | bytes):
        return [_dump_mapping(item, exclude_none) for item in value]
    return value


class _ChunkWithItem:
    """Expose a dict ``item`` as an object without copying the event."""

    __slots__ = ("_inner", "_item")

    def __init__(self, inner: Any, item: _MappingView) -> None:
        self._inner = inner
        self._item = item

    @property
    def item(self) -> _MappingView:
        return self._item

    def __getattr__(self, name: str) -> Any:
        inner = self._inner
        if isinstance(inner, Mapping):
            if name in inner:
                return inner[name]
            raise AttributeError(name)
        return getattr(inner, name)


def coerce_responses_stream_chunk(chunk: Any) -> Any:
    """Make Responses stream events safe for langchain's attribute converter."""
    chunk = alias_reasoning_text_delta(chunk)
    if isinstance(chunk, Mapping):
        return _MappingView(chunk)
    item = _chunk_attr(chunk, "item")
    if isinstance(item, Mapping):
        return _ChunkWithItem(chunk, _MappingView(item))
    return chunk


def _echo_reasoning_content(message: Any, payload: dict[str, Any]) -> dict[str, Any]:
    """Keep DeepSeek Completions tool rounds valid by echoing reasoning_content."""
    if not isinstance(message, AIMessage):
        return payload
    if payload.get("role") != "assistant":
        return payload
    if payload.get("reasoning_content") not in (None, ""):
        return payload
    extra = getattr(message, "additional_kwargs", None) or {}
    if not isinstance(extra, Mapping):
        return payload
    reasoning = extra.get("reasoning_content")
    if isinstance(reasoning, str) and reasoning:
        payload["reasoning_content"] = reasoning
    return payload


def _text_parts_from_value(value: Any) -> list[str]:
    if isinstance(value, str) and value.strip():
        return [value]
    if isinstance(value, Mapping):
        text = value.get("text")
        if isinstance(text, str) and text.strip():
            return [text]
        return []
    if isinstance(value, Sequence) and not isinstance(value, str | bytes):
        parts: list[str] = []
        for item in value:
            parts.extend(_text_parts_from_value(item))
        return parts
    return []


def extract_reasoning_plaintext(item: Mapping[str, Any]) -> str:
    """Collect DeepSeek-usable CoT text from a Responses reasoning item."""
    content = item.get("content")
    if isinstance(content, str) and content.strip():
        return content
    parts: list[str] = []
    if isinstance(content, Sequence) and not isinstance(content, str | bytes):
        for part in content:
            if not isinstance(part, Mapping):
                parts.extend(_text_parts_from_value(part))
                continue
            part_type = str(part.get("type") or "")
            if part_type in {"reasoning_text", "summary_text", "text", ""}:
                parts.extend(_text_parts_from_value(part))
    if parts:
        return "".join(parts)
    # Fallback: langchain stores DeepSeek deltas under OpenAI summary blocks.
    return "".join(_text_parts_from_value(item.get("summary")))


def normalize_responses_reasoning_item(
    item: Mapping[str, Any],
) -> dict[str, Any] | None:
    """Rewrite one reasoning input item into DeepSeek's supported shape.

    DeepSeek merges plaintext ``content[].reasoning_text`` into the adjacent
    assistant message. ``summary`` and ``encrypted_content`` are not supported
    on input and must not be echoed as the CoT carrier.
    """
    if str(item.get("type") or "") != "reasoning":
        return dict(item)
    text = extract_reasoning_plaintext(item)
    if not text.strip():
        return None
    normalized: dict[str, Any] = {
        "type": "reasoning",
        "status": "completed",
        "content": [{"type": "reasoning_text", "text": text}],
    }
    item_id = item.get("id")
    if isinstance(item_id, str) and item_id:
        normalized["id"] = item_id
    return normalized


def normalize_responses_api_input(items: Sequence[Any]) -> list[Any]:
    """Normalize Responses ``input`` items for DeepSeek-compatible providers."""
    result: list[Any] = []
    for item in items:
        if not isinstance(item, Mapping):
            result.append(item)
            continue
        if str(item.get("type") or "") != "reasoning":
            result.append(dict(item) if isinstance(item, dict) else item)
            continue
        normalized = normalize_responses_reasoning_item(item)
        if normalized is not None:
            result.append(normalized)
    return result


def install_openai_compat() -> None:
    """Patch langchain Responses + Completions converters once per process."""
    from langchain_openai.chat_models import base as openai_base

    original_chunk = openai_base._convert_responses_chunk_to_generation_chunk
    if not getattr(original_chunk, "_sqlbot_reasoning_text_compat", False):

        def wrapped_chunk(
            chunk: Any,
            current_index: int,
            current_output_index: int,
            current_sub_index: int,
            **kwargs: Any,
        ) -> Any:
            return original_chunk(
                coerce_responses_stream_chunk(chunk),
                current_index,
                current_output_index,
                current_sub_index,
                **kwargs,
            )

        wrapped_chunk._sqlbot_reasoning_text_compat = True  # type: ignore[attr-defined]
        openai_base._convert_responses_chunk_to_generation_chunk = wrapped_chunk

    original_message = openai_base._convert_message_to_dict
    if not getattr(original_message, "_sqlbot_reasoning_echo_compat", False):

        def wrapped_message(message: Any) -> dict[str, Any]:
            return _echo_reasoning_content(message, original_message(message))

        wrapped_message._sqlbot_reasoning_echo_compat = True  # type: ignore[attr-defined]
        openai_base._convert_message_to_dict = wrapped_message

    original_input = openai_base._construct_responses_api_input
    if not getattr(original_input, "_sqlbot_reasoning_input_compat", False):

        def wrapped_input(messages: Any) -> list[Any]:
            return normalize_responses_api_input(original_input(messages))

        wrapped_input._sqlbot_reasoning_input_compat = True  # type: ignore[attr-defined]
        openai_base._construct_responses_api_input = wrapped_input
