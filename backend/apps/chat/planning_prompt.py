"""Render planner HumanMessage text from retrieved context.

Sibling of ``planning_context``: that module persists retrieval bags; this one
turns those bags into model input. Prose (schema, rules, examples) is pasted
verbatim so quotes and newlines are not JSON-escaped. Only already-structured
objects are serialized with orjson.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import orjson


@dataclass(frozen=True)
class ProtocolPromptBits:
    type_key: str = ""
    identifier_quote: str = ""
    rules: str = ""


def _identifier_quote(type_key: str) -> str:
    if not type_key:
        return ""
    try:
        from apps.protocol.registry import get_spec

        return str(get_spec(type_key).quote_prefix or "")
    except Exception:
        return ""


def _planner_dialect_rules(
    *,
    type_key: str,
    identifier_quote: str,
    enable_query_limit: bool,
) -> str:
    """Dialect constraints the planner needs — not the legacy SQL system prompt."""
    parts: list[str] = []
    if type_key:
        parts.append(f"目标协议: {type_key}")
    if identifier_quote:
        parts.append(
            f"标识符必须使用 {identifier_quote} 包裹，禁止混用其他引号。"
        )
    try:
        if type_key and type_key not in {"rest", "api"}:
            from apps.template.generate_sql.generator import get_sql_example_template

            template = get_sql_example_template(type_key)
            for key in ("quot_rule", "limit_rule"):
                text = str(template.get(key) or "").strip()
                if text:
                    parts.append(text)
    except Exception:
        pass
    if enable_query_limit:
        from apps.chat.plan_policy import ROW_LIMIT

        parts.append(
            f"用户未要求返回行上限时不要写入 LIMIT；展示窗口由服务端截断（上限 {ROW_LIMIT}）。"
            "分组汇总可能超过该窗口时，必须按主指标 DESC 排序，不要依赖无序截断代表全量。"
        )
    else:
        parts.append("不要因为展示需要自行添加 LIMIT。")
    parts.append("candidates.payload 必须是目标协议原生查询 JSON，不要 Markdown，不要解释。")
    return "\n".join(parts)


def protocol_prompt_bits(llm_service: Any) -> ProtocolPromptBits:
    """Dialect rules for the planner — never the legacy SQL system persona."""
    type_key = getattr(getattr(llm_service, "protocol", None), "type_key", "") or ""
    quote_prefix = _identifier_quote(type_key)
    return ProtocolPromptBits(
        type_key=type_key,
        identifier_quote=quote_prefix,
        rules=_planner_dialect_rules(
            type_key=type_key,
            identifier_quote=quote_prefix,
            enable_query_limit=bool(
                getattr(llm_service, "enable_sql_row_limit", True)
            ),
        ),
    )


def _xml_section(tag: str, body: str) -> str | None:
    text = (body or "").strip()
    if not text:
        return None
    return f"<{tag}>\n{text}\n</{tag}>"


def _json_section(tag: str, value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, Mapping) and not value:
        return None
    if isinstance(value, list | tuple) and not value:
        return None
    if isinstance(value, str) and not value.strip():
        return None
    encoded = orjson.dumps(value, option=orjson.OPT_INDENT_2).decode()
    return f"<{tag}>\n{encoded}\n</{tag}>"


def render_planner_input(
    *,
    schema: str = "",
    sample_data: str = "",
    terminology: str = "",
    query_examples: str = "",
    custom_rules: str = "",
    protocol: ProtocolPromptBits | None = None,
    structured: Mapping[str, Any] | None = None,
) -> str:
    """Assemble one HumanMessage body for semantic planning or physical repair."""
    bits = protocol or ProtocolPromptBits()
    sections: list[str] = []

    for tag, body in (
        ("schema", schema),
        ("sample_data", sample_data),
        ("terminology", terminology),
        ("query_examples", query_examples),
        ("custom_rules", custom_rules),
        ("protocol_rules", bits.rules),
    ):
        section = _xml_section(tag, body)
        if section is not None:
            sections.append(section)

    protocol_meta: dict[str, str] = {}
    if bits.type_key:
        protocol_meta["protocol_type"] = bits.type_key
    if bits.identifier_quote:
        protocol_meta["identifier_quote"] = bits.identifier_quote
    meta_section = _json_section("protocol", protocol_meta)
    if meta_section is not None:
        sections.append(meta_section)

    for key, value in (structured or {}).items():
        section = _json_section(str(key), value)
        if section is not None:
            sections.append(section)

    return "\n\n".join(sections)
