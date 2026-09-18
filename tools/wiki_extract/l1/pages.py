"""Parse L0 draft markdown pages into structured dicts (zero-trust YAML fences)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from tools.wiki_extract.l1.schema import dict_page_key

_FENCE = re.compile(r"^```ground:(?P<kind>[a-z]+)\s*$")


def parse_page(text: str) -> dict[str, Any]:
    front, body = _split_frontmatter(text)
    grounds = _parse_grounds(body)
    return {"front": front, "body": body, "grounds": grounds}


def load_l0_corpus(l0_dir: Path) -> dict[str, Any]:
    l0_dir = l0_dir.resolve()
    tables: dict[str, dict[str, Any]] = {}
    dicts: dict[str, dict[str, Any]] = {}
    for path in sorted((l0_dir / "tables").glob("*.md")):
        page = parse_page(path.read_text(encoding="utf-8"))
        compiled = table_from_page(page)
        if compiled.get("table"):
            tables[str(compiled["table"])] = compiled
    for path in sorted((l0_dir / "dicts").glob("*.md")):
        page = parse_page(path.read_text(encoding="utf-8"))
        item = dict_from_page(page)
        key = str(item.get("dict") or path.stem)
        dicts[key] = item
    return {"tables": tables, "dicts": dicts, "root": l0_dir}


def table_from_page(page: dict[str, Any]) -> dict[str, Any]:
    front = page.get("front") or {}
    table_block = next((g["data"] for g in page["grounds"] if g["kind"] == "table"), {})
    relations = [g["data"] for g in page["grounds"] if g["kind"] == "relation"]
    compiled = dict(table_block)
    compiled.setdefault("table", front.get("page_key"))
    if compiled.get("desc") and not compiled.get("description"):
        compiled["description"] = compiled["desc"]
    compiled.setdefault("description", front.get("title"))
    compiled.setdefault("database", (front.get("databases") or [None])[0] if front.get("databases") else None)
    compiled["relations"] = relations
    compiled["front"] = front
    compiled.pop("clusters", None)
    tname = str(compiled.get("table") or "")
    for field in compiled.get("fields") or []:
        if not isinstance(field, dict):
            continue
        field.pop("cluster", None)
        if field.get("type") and not field.get("data_type"):
            field["data_type"] = field["type"]
        if field.get("desc") and not field.get("description"):
            field["description"] = field["desc"]
        raw_dict = field.get("dict")
        if isinstance(raw_dict, list):
            col = str(field.get("name") or "")
            if tname and col:
                field.setdefault("dictionary", dict_page_key(tname, col))
        elif isinstance(raw_dict, str) and raw_dict.strip():
            field.setdefault("dictionary", raw_dict.strip())
    return compiled


def dict_from_page(page: dict[str, Any]) -> dict[str, Any]:
    front = page.get("front") or {}
    block = next((g["data"] for g in page["grounds"] if g["kind"] == "dict"), {})
    item = dict(block)
    item.setdefault("dict", front.get("page_key"))
    fields = item.get("fields") or front.get("anchors") or []
    if fields:
        physical = str(fields[0])
        if "." in physical:
            table, column = physical.split(".", 1)
            item.setdefault("table", table)
            item.setdefault("column", column)
    item["front"] = front
    return item


def _split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    rest = text[3:]
    end = rest.find("\n---")
    if end < 0:
        return {}, text
    raw = rest[:end]
    body = rest[end + 4 :].lstrip("\n")
    loaded = yaml.safe_load(raw) or {}
    if not isinstance(loaded, dict):
        return {}, body
    return loaded, body


def _parse_grounds(body: str) -> list[dict[str, Any]]:
    lines = body.splitlines()
    out: list[dict[str, Any]] = []
    index = 0
    while index < len(lines):
        match = _FENCE.match(lines[index])
        if not match:
            index += 1
            continue
        kind = match.group("kind")
        index += 1
        chunk: list[str] = []
        while index < len(lines) and lines[index].strip() != "```":
            chunk.append(lines[index])
            index += 1
        if index < len(lines):
            index += 1
        loaded = yaml.safe_load("\n".join(chunk)) or {}
        if isinstance(loaded, dict):
            out.append({"kind": kind, "data": loaded})
    return out
