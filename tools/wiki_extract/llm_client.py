"""OpenAI-compatible chat for L0 refine. Isolated from apps.knowledge.wiki."""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin

import httpx

_ENV_KEY = "WIKI_EXTRACT_LLM_API_KEY"
_ENV_BASE = "WIKI_EXTRACT_LLM_BASE_URL"
_ENV_MODEL = "WIKI_EXTRACT_LLM_MODEL"


@dataclass(frozen=True)
class LlmConfig:
    api_key: str
    base_url: str
    model: str
    timeout_sec: float = 120.0

    def masked(self) -> str:
        return f"{self.model} @ {self.base_url}"


def resolve_llm_config(
    *,
    api_key: str = "",
    base_url: str = "",
    model: str = "",
) -> LlmConfig | None:
    key = (
        (api_key or "").strip()
        or os.environ.get(_ENV_KEY, "").strip()
        or os.environ.get("OPENAI_API_KEY", "").strip()
    )
    base = (
        (base_url or "").strip()
        or os.environ.get(_ENV_BASE, "").strip()
        or os.environ.get("OPENAI_BASE_URL", "").strip()
        or os.environ.get("OPENAI_API_BASE", "").strip()
    )
    name = (
        (model or "").strip()
        or os.environ.get(_ENV_MODEL, "").strip()
        or os.environ.get("OPENAI_MODEL", "").strip()
    )
    if not (key and base and name):
        return None
    return LlmConfig(api_key=key, base_url=base.rstrip("/"), model=name)


def chat_json(config: LlmConfig, *, system: str, user: str) -> dict[str, Any]:
    payload = {
        "model": config.model,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    url = _chat_url(config.base_url)
    headers = {
        "Authorization": f"Bearer {config.api_key}",
        "Content-Type": "application/json",
    }
    last_error: Exception | None = None
    body: dict[str, Any] = {}
    for attempt in range(6):
        try:
            with httpx.Client(timeout=config.timeout_sec) as client:
                response = client.post(url, headers=headers, json=payload)
                if response.status_code == 429:
                    time.sleep(min(32.0, 2.0**attempt))
                    last_error = httpx.HTTPStatusError(
                        "429 Too Many Requests",
                        request=response.request,
                        response=response,
                    )
                    continue
                response.raise_for_status()
                parsed = response.json()
        except httpx.HTTPError as exc:
            last_error = exc
            time.sleep(min(32.0, 2.0**attempt))
            continue
        if isinstance(parsed, dict):
            body = parsed
            last_error = None
            break
        last_error = ValueError("LLM JSON HTTP body is not an object")
    if last_error is not None:
        raise last_error
    content = (
        ((body.get("choices") or [{}])[0].get("message") or {}).get("content")
    ) or ""
    return parse_json_object(str(content))


def parse_json_object(text: str) -> dict[str, Any]:
    raw = (text or "").strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    start = raw.find("{")
    end = raw.rfind("}")
    if start < 0 or end < start:
        raise ValueError("LLM response is not a JSON object")
    data = json.loads(raw[start : end + 1])
    if not isinstance(data, dict):
        raise ValueError("LLM JSON is not an object")
    return data


def _chat_url(base: str) -> str:
    if base.endswith("/chat/completions"):
        return base
    if base.endswith("/v1"):
        return base + "/chat/completions"
    return urljoin(base.rstrip("/") + "/", "v1/chat/completions")
