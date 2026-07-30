"""Provider-neutral token usage normalization for conversation model calls."""

from __future__ import annotations

from typing import Any, Dict


def usage_from_response(response: Any) -> Dict[str, Any]:
    """Normalize token usage from a non-streaming LangChain response."""
    usage = getattr(response, "usage_metadata", None) or {}
    if isinstance(usage, dict) and usage:
        return {
            "input_tokens": usage.get("input_tokens"),
            "output_tokens": usage.get("output_tokens"),
            "total_tokens": usage.get("total_tokens"),
        }

    metadata = getattr(response, "response_metadata", None) or {}
    if not isinstance(metadata, dict):
        return {}
    token_usage = metadata.get("token_usage") or metadata.get("usage") or {}
    if not isinstance(token_usage, dict):
        return {}
    return {
        "input_tokens": token_usage.get("prompt_tokens")
        or token_usage.get("input_tokens"),
        "output_tokens": token_usage.get("completion_tokens")
        or token_usage.get("output_tokens"),
        "total_tokens": token_usage.get("total_tokens")
        or token_usage.get("total_token_count"),
    }


def merge_usage(*items: Dict[str, Any]) -> Dict[str, int]:
    """Sum normalized usage for multiple calls recorded as one graph span."""
    merged = {
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
    }
    for item in items:
        for key in merged:
            value = item.get(key)
            if isinstance(value, (int, float)):
                merged[key] += int(value)
    return merged
