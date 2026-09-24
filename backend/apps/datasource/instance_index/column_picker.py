"""LLM column picker for the instance index. Code only hard-skips and samples."""

from __future__ import annotations

import json
from collections.abc import Callable, Sequence
from typing import Any

from common.utils.json_utils import extract_nested_json
from common.utils.utils import SQLBotLogUtil

_SAMPLE_PREVIEW = 8

_PICK_PROMPT = """你在为问数系统挑选「实例索引」列。索引用于把用户说的开放实例（人名、部门、企业名、业务码、审批号等）反查到表.字段。

规则：
- 优先收录开放业务实例列（人名/部门/企业名/业务编码/审批号/项目名等）。
- 枚举码列收进去可以接受，不要因为像枚举就排除。
- 同语义多列可以都收。
- 可排除：纯无语义的长 ID 噪声、时间戳、日志自由文本。不确定则 exclude。

只返回 JSON：{{"include": ["列名", ...], "exclude": ["列名", ...]}}

表：{table}
候选列：
{columns}
"""


def pick_instance_columns(
    table_name: str,
    columns: Sequence[dict[str, Any]],
    *,
    invoke: Callable[[str], str] | None = None,
) -> set[str] | None:
    """Return included field names, or None if the picker failed.

    ``None`` means the caller should keep every sampled column (no nominate fallback).
    """
    names = {
        str(item.get("name") or "").strip()
        for item in columns
        if str(item.get("name") or "").strip()
    }
    if not names:
        return set()
    caller = invoke or _invoke_default_llm
    prompt = _PICK_PROMPT.format(
        table=table_name,
        columns=_format_columns(columns),
    )
    try:
        raw = caller(prompt)
    except Exception as exc:
        SQLBotLogUtil.warning("instance-index LLM pick %s failed: %s", table_name, exc)
        return None
    parsed = _parse_include(raw)
    if parsed is None:
        SQLBotLogUtil.warning(
            "instance-index LLM pick %s returned unusable output", table_name
        )
        return None
    include = {name for name in parsed if name in names}
    return include


def _format_columns(columns: Sequence[dict[str, Any]]) -> str:
    lines: list[str] = []
    for item in columns:
        name = str(item.get("name") or "").strip()
        if not name:
            continue
        comment = str(item.get("comment") or "").strip()
        samples = [
            str(value).strip()
            for value in (item.get("samples") or [])
            if str(value).strip()
        ][:_SAMPLE_PREVIEW]
        preview = "、".join(samples) if samples else "(无样本)"
        label = f"{name} {comment}".strip()
        lines.append(f"- {label}: {preview}")
    return "\n".join(lines)


def _parse_include(raw: str) -> set[str] | None:
    text = str(raw or "").strip()
    if not text:
        return None
    blob = extract_nested_json(text) or text
    try:
        loaded = json.loads(blob)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(loaded, dict):
        return None
    include = loaded.get("include")
    if include is None and "columns" in loaded:
        include = loaded.get("columns")
    if not isinstance(include, list):
        return None
    return {str(item).strip() for item in include if str(item).strip()}


def _invoke_default_llm(prompt: str) -> str:
    import asyncio
    from concurrent.futures import ThreadPoolExecutor

    from apps.ai_model.model_factory import LLMFactory, get_default_config

    async def _run() -> str:
        config = await get_default_config()
        llm = LLMFactory.create_llm(config)
        result = llm.generate(prompt)
        return str(result or "")

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(_run())
    with ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(lambda: asyncio.run(_run())).result(timeout=90)
