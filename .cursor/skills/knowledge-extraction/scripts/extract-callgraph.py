#!/usr/bin/env python3
"""Dormant-table reachability baseline (text-based, deterministic).

Judges the skill's "休眠表" rule (SKILL.md §7.14) mechanically: which
@TableName tables are NOT reached by any entry point through static,
compile-time class references. Entry points are Controller / Facade /
DubboService / listener-style classes.

This is a *baseline*, not a compiler call graph. It intentionally ignores
reflection and dynamic routing (matching the skill's DFS rule), so a table
flagged here is a "dormant candidate" for the AI agent to confirm by reading
the call chain — never a final verdict.

Usage::

    backend/venv/bin/python .cursor/skills/knowledge-extraction/scripts/extract-callgraph.py <repo> [-o callgraph.yaml]
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml

_ENTRY_ANNOTATIONS = ("@RestController", "@Controller", "@RequestMapping", "@DubboService")
_ENTRY_SUFFIXES = (
    "Facade",
    "Controller",
    "Application",
    "Listener",
    "Consumer",
    "Provider",
    "Job",
)
_TOKEN = re.compile(r"\b[A-Z][A-Za-z0-9_]*\b")


def strip_schema(tbl: str) -> str:
    m = re.match(r"^[a-z_]+\.([a-z_]+)$", tbl)
    return m.group(1) if m else tbl


def primary_type_name(text: str) -> str | None:
    m = re.search(
        r"\b(?:public\s+)?(?:abstract\s+|final\s+)?(?:class|interface|enum)\s+([A-Z]\w*)",
        text,
    )
    return m.group(1) if m else None


def do_index(repo: Path) -> dict[str, str]:
    """DO class name -> physical table name (from @TableName)."""
    index: dict[str, str] = {}
    for path in repo.rglob("*.java"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "@TableName" not in text:
            continue
        cls = re.search(r"class\s+(\w+)", text)
        tbl = re.search(r'@TableName\(\s*"([^"]+)"\s*\)', text)
        if cls and tbl:
            index[cls.group(1)] = strip_schema(tbl.group(1))
    return index


def class_index(repo: Path) -> dict[str, Path]:
    """Every primary Java type name -> its defining file."""
    index: dict[str, Path] = {}
    for path in repo.rglob("*.java"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        name = primary_type_name(text)
        if name:
            index.setdefault(name, path)
    return index


def entry_classes(classes: dict[str, Path]) -> set[str]:
    entries: set[str] = set()
    for name, path in classes.items():
        text = path.read_text(encoding="utf-8", errors="ignore")
        if any(ann in text for ann in _ENTRY_ANNOTATIONS):
            entries.add(name)
        elif name.endswith(_ENTRY_SUFFIXES):
            entries.add(name)
    return entries


def mapper_for(do_name: str, classes: dict[str, Path], names: set[str]) -> str | None:
    base = do_name[:-2] if do_name.endswith("DO") else do_name
    candidate = f"{base}Mapper"
    if candidate in names:
        return candidate
    # fallback: an interface whose file references the DO type
    for name, path in classes.items():
        if name == candidate:
            continue
        if not name.endswith("Mapper"):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if do_name in text and "interface" in text:
            return name
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo")
    parser.add_argument("-o", "--output", default="callgraph.yaml")
    args = parser.parse_args()

    repo = Path(args.repo)
    dos = do_index(repo)
    classes = class_index(repo)
    names = set(classes)
    entries = entry_classes(classes)

    # class -> set of class names its file references (compile-time tokens)
    file_refs: dict[str, set[str]] = {}
    for name, path in classes.items():
        text = path.read_text(encoding="utf-8", errors="ignore")
        file_refs[name] = set(_TOKEN.findall(text)) & names

    # BFS from entry classes through static references
    reachable: set[str] = set(entries)
    queue: list[str] = list(entries)
    while queue:
        current = queue.pop()
        for target in file_refs.get(current, ()) - reachable:
            reachable.add(target)
            queue.append(target)

    tables: dict[str, dict] = {}
    dormant: list[str] = []
    for do_name, table in sorted(dos.items()):
        mapper = mapper_for(do_name, classes, names)
        do_reachable = do_name in reachable
        mapper_reachable = mapper is not None and mapper in reachable
        via = sorted(
            e for e in entries if e in reachable and (do_name in file_refs.get(e, ()) or (mapper and mapper in file_refs.get(e, ())))
        )
        tables[table] = {
            "do": do_name,
            "mapper": mapper,
            "reachable": do_reachable or mapper_reachable,
            "entry_points": via,
        }
        if not (do_reachable or mapper_reachable):
            dormant.append(table)

    result = {
        "schema_version": "1.0",
        "repository": repo.name,
        "entry_points": sorted(entries),
        "dormant_candidates": dormant,
        "tables": tables,
    }
    Path(args.output).write_text(
        yaml.safe_dump(result, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    print(
        f"tables={len(tables)} dormant_candidates={len(dormant)} "
        f"entry_points={len(entries)} -> {args.output}"
    )
    for table in dormant:
        print(f"  DORMANT {table}: {tables[table]['do']} / {tables[table]['mapper']}")


if __name__ == "__main__":
    main()
