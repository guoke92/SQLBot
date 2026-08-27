#!/usr/bin/env python3
"""Extract enum dictionaries from Java enum classes.

The target codebase uses ``XxxEnum`` classes with the ``NAME("dictKey", "显示名")``
pattern. This is deterministic (like the catalog), so it belongs to the script
side, not the AI-agent side.

The enum class name maps to its DB field by convention:
``XxxEnum`` -> ``xxx``（去 Enum 后缀 + camelCase 转 snake）。

Usage::

    backend/venv/bin/python .cursor/skills/knowledge-extraction/scripts/extract-enums.py <repo> [-o enums.yaml]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml


def snake(name: str) -> str:
    # XxxEnum -> xxx（去 Enum 后缀；处理连续大写缩写，如 IDType -> id_type）
    return re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])|(?<=[a-z0-9])(?=[A-Z])", "_", name).lower()


def extract(repo: Path) -> list[dict]:
    enums: list[dict] = []
    for path in sorted(repo.rglob("*Enum.java")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        cls = re.search(r"(?:public\s+)?enum\s+(\w+)", text)
        if not cls:
            continue
        name = cls.group(1)
        values: list[dict] = []
        # NAME("dictKey", "显示名") — 枚举常量声明（两个字符串实参）
        for m in re.finditer(r'\b([A-Z][A-Z0-9_]*)\s*\(\s*"([^"]+)"\s*,\s*"([^"]*)"\s*\)', text):
            values.append({"value": m.group(2), "display": m.group(3)})
        if not values:
            continue
        field = snake(name[:-4] if name.endswith("Enum") else name)
        enums.append(
            {
                "enum": name,
                "field": field,
                "path": str(path.relative_to(repo)),
                "values": values,
            }
        )
    return enums


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("-o", "--output")
    args = ap.parse_args()
    repo = Path(args.repo)

    enums = extract(repo)
    total_values = sum(len(e["values"]) for e in enums)

    out = {"schema_version": "1.0", "repository": repo.name, "enums": enums}
    if args.output:
        Path(args.output).write_text(
            yaml.safe_dump(out, allow_unicode=True, sort_keys=False), encoding="utf-8"
        )
        print(f"wrote {args.output}")

    print(f"enums={len(enums)} values={total_values}", file=sys.stderr)
    for e in enums:
        vals = "|".join(v["value"] for v in e["values"][:6])
        more = "…" if len(e["values"]) > 6 else ""
        print(f"  {e['field']:<28} <- {e['enum']}  [{vals}{more}]")


if __name__ == "__main__":
    main()
