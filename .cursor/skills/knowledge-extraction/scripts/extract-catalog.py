#!/usr/bin/env python3
"""Extract a complete table/field catalog from a MyBatis-Plus Java codebase.

Enumerates every ``@TableName`` DO class: table name, fields (physical column,
Java type, ``@ApiModelProperty`` comment), and FK candidates. The catalog is the
offline baseline against which the knowledge package's semantic coverage is
linted — it is a reference/working artifact, not part of the KnowledgePackageV2
import and not recalled at runtime.

Usage::

    backend/venv/bin/python .cursor/skills/knowledge-extraction/scripts/extract-catalog.py <repo> [-o catalog.yaml]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

_TYPE_MAP = {
    "String": "varchar",
    "Long": "bigint",
    "Integer": "int",
    "int": "int",
    "BigDecimal": "decimal",
    "Date": "datetime",
    "LocalDateTime": "datetime",
    "LocalDate": "date",
    "Boolean": "boolean",
    "boolean": "boolean",
    "Double": "double",
    "Float": "float",
}

# 工程/运维/租户样板字段：目录里保留但标记，提取语义时跳过
_BOILERPLATE = {
    "id",
    "create_by",
    "create_user",
    "update_by",
    "update_user",
    "create_time",
    "update_time",
    "remark",
    "deleted",
    "act_procinst_id",
    "act_procinst_no",
    "act_procinst_status",
    "act_procinst_date",
    "app_tenant_code",
    "db_tenant_code",
    "organization_id",
}

# FK 候选：外键字段后缀（*_id / *_code，对应 reference.md §3.2/§3.3 的 FK 判定）
_FK_SUFFIXES = ("_id", "_code")


def snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def parse_do(path: Path) -> tuple[str, list[dict]]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r'@TableName\(\s*"([^"]+)"\s*\)', text)
    if not match:
        return "", []
    table = match.group(1)

    fields: list[dict] = []
    # @ApiModelProperty 注释紧跟其后的字段声明
    pending_comment = ""
    for line in text.splitlines():
        cm = re.search(r'@ApiModelProperty\([^)]*value\s*=\s*"([^"]*)"', line)
        if cm:
            pending_comment = cm.group(1).strip()
            continue
        fm = re.search(r"private\s+([A-Za-z0-9_<>,.\s]+?)\s+([a-z][A-Za-z0-9]*)\s*;", line)
        if not fm:
            continue
        java_type = fm.group(1).strip().split("<")[0].strip()
        java_type = java_type.split(".")[-1]
        name = fm.group(2)
        column = snake(name)
        fields.append(
            {
                "column": column,
                "type": _TYPE_MAP.get(java_type, java_type.lower()),
                "comment": pending_comment,
                "boilerplate": column in _BOILERPLATE,
                "fk_candidate": (
                    column not in _BOILERPLATE
                    and column.endswith(_FK_SUFFIXES)
                ),
            }
        )
        pending_comment = ""
    return table, fields


def main() -> None:
    parser = argparse.ArgumentParser(description="extract table/field catalog from DO classes")
    parser.add_argument("repo", help="path to the target Java repository")
    parser.add_argument("-o", "--output", help="write YAML catalog to this path")
    args = parser.parse_args()

    repo = Path(args.repo)
    tables: dict[str, list[dict]] = {}
    for path in sorted(repo.rglob("*.java")):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if "@TableName" not in text:
            continue
        table, fields = parse_do(path)
        if table:
            tables[table] = fields

    catalog = {
        "schema_version": "1.0",
        "repository": repo.name,
        "table_source": "@TableName DO + @ApiModelProperty",
        "tables": {
            name: {
                "fields": fields,
                "field_count": len(fields),
            }
            for name, fields in sorted(tables.items())
        },
    }

    if args.output:
        Path(args.output).write_text(
            yaml.safe_dump(catalog, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        print(f"wrote {args.output}")
    else:
        print(json.dumps(catalog, ensure_ascii=False, indent=2))

    total_fields = sum(len(v["fields"]) for v in catalog["tables"].values())
    fk = sum(
        1
        for t in catalog["tables"].values()
        for f in t["fields"]
        if f["fk_candidate"]
    )
    commented = sum(
        1
        for t in catalog["tables"].values()
        for f in t["fields"]
        if f["comment"]
    )
    print(
        f"tables={len(catalog['tables'])} fields={total_fields} "
        f"fk_candidates={fk} commented={commented}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
