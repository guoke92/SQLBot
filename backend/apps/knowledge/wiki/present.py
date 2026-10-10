"""Turn wiki ground fences into reader-facing markdown.

Authoring pages keep `````ground:<kind>`` as the contract. The browser
must still show what those fences hold: enum values, columns, joins,
process stages, calibers, metrics, rules, and scenarios.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

import yaml

_FENCE_RE = re.compile(
    r"```ground:(?P<kind>[a-z-]+)\s*\n(?P<yaml>.*?)\n```",
    re.S,
)
_REVIEW_RE = re.compile(
    r"---REVIEW:\s*(?P<type>[\w-]+)\s*\|\s*(?P<title>.+?)\s*---\n"
    r"(?P<body>.*?)---END REVIEW---",
    re.S,
)
_FRONTMATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.S)


def present_page_body(body: str) -> str:
    """Replace contract fences with the content a person should read."""
    text = _FRONTMATTER_RE.sub("", str(body or ""))
    text = _FENCE_RE.sub(
        lambda match: _render_fence(match.group("kind"), match.group("yaml")), text
    )
    text = _REVIEW_RE.sub(_render_review, text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _render_fence(kind: str, raw: str) -> str:
    try:
        loaded = yaml.safe_load(raw)
    except yaml.YAMLError:
        return _yaml_block(raw)
    if not isinstance(loaded, dict):
        return _yaml_block(raw)
    rendered = _RENDERERS.get(kind, _render_generic)(loaded)
    return rendered.strip() or _yaml_block(raw)


def _render_review(match: re.Match[str]) -> str:
    title = match.group("title").strip()
    kind = match.group("type").strip()
    body = match.group("body").strip().replace("\n", "\n> ")
    return f"> **{title}**（{kind}）\n>\n> {body}"


def _render_dict(data: dict[str, Any]) -> str:
    lines: list[str] = []
    fields = _as_list(data.get("fields"))
    if fields:
        lines.append("物理列：" + "、".join(_col_link(item) for item in fields))
    triage = str(data.get("triage") or "").strip()
    if triage:
        lines.append(f"处置：{triage}")
    rows: list[list[str]] = []
    values = data.get("values")
    if isinstance(values, dict):
        for code, meta in values.items():
            info = meta if isinstance(meta, dict) else {"label": meta}
            rows.append(
                [
                    str(code),
                    str(info.get("label") or ""),
                    str(info.get("trust") or ""),
                    str(info.get("evidence") or ""),
                ]
            )
    else:
        for item in _as_list(values):
            if isinstance(item, dict):
                code = item.get("value") or item.get("code") or item.get("name") or ""
                rows.append(
                    [
                        str(code),
                        str(item.get("label") or ""),
                        str(item.get("trust") or ""),
                        str(item.get("evidence") or ""),
                    ]
                )
            else:
                rows.append([str(item), "", "", ""])
    table = _table(["取值", "含义", "可信度", "依据"], rows)
    if table:
        lines.append(table)
    return "\n\n".join(lines)


def _render_table(data: dict[str, Any]) -> str:
    lines: list[str] = []
    desc = str(data.get("desc") or "").strip()
    if desc:
        lines.append(desc)
    database = str(data.get("database") or "").strip()
    if database:
        lines.append(f"库：{database}")
    grain = str(data.get("grain") or "").strip()
    if grain:
        lines.append(f"粒度：{grain}")
    keys = _as_list(data.get("primary_key"))
    if keys:
        lines.append("主键：" + "、".join(keys))
    anchors = _as_list(data.get("name_anchors"))
    if anchors:
        lines.append("名称列：" + "、".join(anchors))
    if data.get("inactive") is True:
        lines.append("业务休眠")
    rows: list[list[str]] = []
    for field in data.get("fields") or []:
        if not isinstance(field, dict):
            continue
        nullable = field.get("nullable")
        null_text = "否" if nullable is False else "是" if nullable is True else ""
        rows.append(
            [
                str(field.get("name") or ""),
                str(field.get("type") or ""),
                str(field.get("desc") or ""),
                _enum_text(field),
                null_text,
                "、".join(_as_list(field.get("written_with"))),
            ]
        )
    table = _table(["字段", "类型", "说明", "取值", "可空", "同写"], rows)
    if table:
        lines.append(table)
    return "\n\n".join(lines)


def _render_relation(data: dict[str, Any]) -> str:
    left = str(data.get("left") or "")
    right = str(data.get("right") or "")
    meta = [
        str(data.get(key))
        for key in (
            "type",
            "cardinality",
            "trust",
            "authenticity",
            "join_role",
            "priority",
        )
        if data.get(key)
    ]
    lines = [f"{_col_link(left)} → {_col_link(right)}"]
    if meta:
        lines[0] += " · " + " · ".join(meta)
    note = str(data.get("authenticity_note") or "").strip()
    if note:
        lines.append(note)
    evidence = str(data.get("evidence") or "").strip()
    if evidence:
        lines.append(f"依据：{evidence}")
    return "\n\n".join(lines)


def _render_process(data: dict[str, Any]) -> str:
    lines: list[str] = []
    field = str(data.get("field") or "").strip()
    if field:
        lines.append(f"状态列：{_col_link(field)}")
    entry = str(data.get("entry") or "").strip()
    if entry:
        lines.append(f"入口：{entry}")
    rows: list[list[str]] = []
    for stage in data.get("stages") or []:
        if not isinstance(stage, dict):
            continue
        name = str(stage.get("stage") or "")
        transitions = stage.get("transitions") or []
        if not isinstance(transitions, list) or not transitions:
            rows.append([name, "", "", "", ""])
            continue
        for item in transitions:
            if not isinstance(item, dict):
                continue
            rows.append(
                [
                    name,
                    str(item.get("from") or ""),
                    str(item.get("event") or ""),
                    str(item.get("to") or ""),
                    str(item.get("evidence") or ""),
                ]
            )
    table = _table(["阶段", "从", "事件", "到", "依据"], rows)
    if table:
        lines.append(table)
    return "\n\n".join(lines)


def _render_caliber(data: dict[str, Any]) -> str:
    lines: list[str] = []
    predicate = str(data.get("predicate") or "").strip()
    if predicate:
        lines.append("条件：\n\n```\n" + predicate + "\n```")
    scope = str(data.get("scope") or "").strip()
    if scope:
        lines.append(f"范围：{scope}")
    boundary = str(data.get("boundary") or "").strip()
    if boundary:
        lines.append(boundary)
    targets = _as_list(data.get("field_targets"))
    if targets:
        lines.append("字段：" + "、".join(_col_link(item) for item in targets))
    relations = _relation_lines(data.get("using_relations"))
    if relations:
        lines.append("关系：\n\n" + "\n".join(f"- {item}" for item in relations))
    evidence = str(data.get("evidence") or "").strip()
    if evidence:
        lines.append(f"依据：{evidence}")
    return "\n\n".join(lines)


def _render_metric(data: dict[str, Any]) -> str:
    caliber = str(data.get("caliber") or "").strip()
    grain = str(data.get("grain_table") or "").strip()
    rows = [
        ["口径", f"[[calibers/{caliber}]]" if caliber else ""],
        ["粒度", f"[[tables/{grain}|{grain}]]" if grain else ""],
        ["聚合", str(data.get("aggregation") or "")],
        ["字段", _col_link(str(data.get("field") or ""))],
        ["依据", str(data.get("evidence") or "")],
    ]
    lines = [_table(["项", "内容"], rows)]
    relations = _relation_lines(data.get("using_relations"))
    if relations:
        lines.append("关系：\n\n" + "\n".join(f"- {item}" for item in relations))
    return "\n\n".join(line for line in lines if line)


def _render_rule(data: dict[str, Any]) -> str:
    lines: list[str] = []
    content = str(data.get("content") or "").strip()
    if content:
        lines.append(content)
    impact = str(data.get("impact") or "").strip()
    if impact:
        lines.append(f"影响：{impact}")
    targets = _as_list(data.get("field_targets"))
    if targets:
        lines.append("字段：" + "、".join(_col_link(item) for item in targets))
    evidence = str(data.get("evidence") or "").strip()
    if evidence:
        lines.append(f"依据：{evidence}")
    return "\n\n".join(lines)


def _render_scenario(data: dict[str, Any]) -> str:
    lines: list[str] = []
    hubs = _role_lines(data.get("hubs"), "tables")
    if hubs:
        lines.append("主表：\n\n" + "\n".join(f"- {item}" for item in hubs))
    shared = _role_lines(data.get("shared"), "tables")
    if shared:
        lines.append("相关表：\n\n" + "\n".join(f"- {item}" for item in shared))
    cycles: list[str] = []
    for item in data.get("lifecycle") or []:
        if not isinstance(item, dict):
            continue
        dict_key = str(item.get("dict") or "").strip()
        process_key = str(item.get("process") or "").strip()
        parts = []
        if dict_key:
            parts.append(f"[[dicts/{dict_key}]]")
        if process_key:
            parts.append(f"[[processes/{process_key}]]")
        if parts:
            cycles.append(" · ".join(parts))
    if cycles:
        lines.append("生命周期：\n\n" + "\n".join(f"- {item}" for item in cycles))
    return "\n\n".join(lines)


def _render_generic(data: dict[str, Any]) -> str:
    lines: list[str] = []
    for key, value in data.items():
        if value in (None, "", [], {}):
            continue
        if isinstance(value, list | dict):
            dumped = yaml.safe_dump(value, allow_unicode=True, sort_keys=False).strip()
            lines.append(f"{key}：\n\n```\n{dumped}\n```")
        else:
            lines.append(f"{key}：{value}")
    return "\n\n".join(lines)


def _enum_text(field: dict[str, Any]) -> str:
    codes = field.get("dict")
    labels = field.get("label")
    if not isinstance(codes, list):
        return ""
    parts: list[str] = []
    for index, code in enumerate(codes):
        label = ""
        if isinstance(labels, dict):
            label = str(labels.get(code) or labels.get(str(code)) or "")
        elif isinstance(labels, list) and index < len(labels):
            label = str(labels[index] or "")
        text = f"{code} {label}".strip() if label else str(code)
        parts.append(text)
    return "、".join(parts)


def _relation_lines(value: object) -> list[str]:
    lines: list[str] = []
    for item in _items(value):
        if isinstance(item, dict):
            left = str(item.get("left") or "")
            right = str(item.get("right") or "")
            if left or right:
                lines.append(f"{_col_link(left)} → {_col_link(right)}")
        elif str(item).strip():
            lines.append(str(item).strip())
    return lines


def _role_lines(value: object, belong: str) -> list[str]:
    lines: list[str] = []
    for item in _items(value):
        if isinstance(item, dict):
            name = str(
                item.get("table") or item.get("dict") or item.get("name") or ""
            ).strip()
            role = str(item.get("role") or "").strip()
            if not name:
                continue
            label = f"[[{belong}/{name}]]"
            if role:
                label += f"（{role}）"
            lines.append(label)
        elif str(item).strip():
            lines.append(str(item).strip())
    return lines


def _items(value: object) -> list[object]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return list(value)
    return [value]


def _col_link(ref: str) -> str:
    text = ref.strip()
    if not text:
        return ""
    table, dot, _field = text.partition(".")
    if dot and table:
        return f"[[tables/{table}|{text}]]"
    return text


def _as_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def _table(headers: list[str], rows: list[list[str]]) -> str:
    if not rows:
        return ""
    width = len(headers)
    padded = [row + [""] * (width - len(row)) for row in rows]
    keep = [
        index for index in range(width) if any(row[index].strip() for row in padded)
    ]
    if not keep:
        return ""
    used_headers = [headers[index] for index in keep]
    used_rows = [[row[index] for index in keep] for row in padded]
    head = "| " + " | ".join(used_headers) + " |"
    rule = "| " + " | ".join("---" for _ in used_headers) + " |"
    body = "\n".join(
        "| " + " | ".join(_cell(cell) for cell in row) + " |" for row in used_rows
    )
    return "\n".join([head, rule, body])


def _cell(value: str) -> str:
    return " ".join(value.replace("|", "\\|").split())


def _yaml_block(raw: str) -> str:
    return "```yaml\n" + raw.strip() + "\n```"


_RENDERERS: dict[str, Callable[[dict[str, Any]], str]] = {
    "dict": _render_dict,
    "table": _render_table,
    "relation": _render_relation,
    "process": _render_process,
    "caliber": _render_caliber,
    "metric": _render_metric,
    "rule": _render_rule,
    "scenario": _render_scenario,
}
