"""Proposed field glosses from profile shape.

Existing column comments stay authoritative. This only fills weak comments
(empty, or a bare 「编码」). An optional LLM hook may rewrite the mechanical
sentence; callers pass a chat function, this module does not open a network
connection by itself.
"""

from __future__ import annotations

from typing import Any, Callable, Mapping, Sequence

from tools.wiki_extract.value_sketch import WEAK_COMMENTS, FieldSketch

ChatFn = Callable[[str, str], Mapping[str, Any]]


def mechanical_gloss(field: FieldSketch, *, samples: Sequence[str] = ()) -> dict[str, str] | None:
    if field.has_comment:
        return None
    shape = field.shape or {}
    if not shape and not samples:
        return None
    bits: list[str] = []
    mode = int(shape.get("len_mode") or 0)
    ratio = float(shape.get("len_mode_ratio") or 0)
    if mode and ratio >= 0.8:
        bits.append(f"长度多为 {mode}")
    if float(shape.get("numeric_ratio") or 0) >= 0.9:
        bits.append("值看起来全是数字")
    prefix = str(shape.get("common_prefix") or "")
    if len(prefix) >= 2:
        bits.append(f"公共前缀 {prefix}")
    sample_text = "、".join(str(item) for item in list(samples)[:5] if str(item).strip())
    if sample_text:
        bits.append(f"样例 {sample_text}")
    if not bits:
        return None
    gloss = f"{field.fq}：" + "，".join(bits) + "。"
    return {
        "fq": field.fq,
        "gloss": gloss,
        "trust": "proposed",
        "source": "shape",
        "comment": str(field.comment or ""),
    }


def apply_llm_glosses(
    chat: ChatFn,
    glosses: Sequence[Mapping[str, str]],
) -> list[dict[str, str]]:
    """Ask ``chat(system, user)`` for short labels. Mechanical gloss is the fallback."""
    if not glosses:
        return []
    payload = {
        "items": [
            {"fq": item.get("fq"), "gloss": item.get("gloss"), "samples": item.get("samples")}
            for item in glosses
        ]
    }
    import json

    try:
        parsed = chat(
            "Rewrite each field gloss into one short Chinese sentence about meaning and value format. "
            "Return JSON {items:[{fq,gloss}]}. Do not invent codes that are not in the input.",
            json.dumps(payload, ensure_ascii=False),
        )
    except Exception:
        return [dict(item) for item in glosses]
    rows = parsed.get("items") if isinstance(parsed, Mapping) else None
    if not isinstance(rows, list):
        return [dict(item) for item in glosses]
    by_fq = {
        str(row.get("fq")): str(row.get("gloss") or "").strip()
        for row in rows
        if isinstance(row, Mapping)
    }
    out: list[dict[str, str]] = []
    for item in glosses:
        packed = dict(item)
        rewritten = by_fq.get(str(item.get("fq") or ""))
        if rewritten:
            packed["gloss"] = rewritten
            packed["source"] = "shape+llm"
        out.append(packed)
    return out


def weak_comment(comment: str) -> bool:
    return str(comment or "").strip() in WEAK_COMMENTS
