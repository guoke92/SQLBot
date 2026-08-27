#!/usr/bin/env python3
"""Extract REAL relationships from code, not from field-name guessing.

Three code facts (authority order 代码读写 > 文档主张):

1. ``ref_<target_table>`` FK convention — the codebase names its foreign-key
   columns ``ref_<target_table>``, embedding the target table name in the column
   name.
2. Mapper XML ``JOIN ... ON a.col = b.col`` clauses.
3. Service/DAO MyBatis-Plus FK usage ``.eq(XxxDO::getFkField, var.getKey())``
   for the ``*_id`` / ``*_code`` FKs that do NOT follow the ``ref_*`` convention.

Noise (tenant isolation, enum matching, id-copy sync) is filtered out.

Usage::

    backend/venv/bin/python .cursor/skills/knowledge-extraction/scripts/extract-relationships.py <repo> [-o relationships.yaml]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

# 租户/流程样板字段：作为关联键时一律跳过
_TENANT = {
    "db_tenant_code",
    "app_tenant_code",
    "organization_id",
    "act_procinst_id",
    "act_procinst_no",
    "act_procinst_status",
    "act_procinst_date",
}


def snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def strip_schema(tbl: str) -> str:
    m = re.match(r"^[a-z_]+\.([a-z_]+)$", tbl)
    return m.group(1) if m else tbl


def do_index(repo: Path) -> dict[str, str]:
    """Java DO class name -> physical table name."""
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


def _is_fk(field: str) -> bool:
    return field.startswith("ref_") or field.endswith("_id") or field.endswith("_code")


def extract_ref_convention(repo: Path, tables: set[str]) -> list[dict]:
    """ref_<target_table> 列名内嵌目标表，目标字段默认为 code。"""
    rels: list[dict] = []
    for path in repo.rglob("*.java"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "ref_" not in text and "ref" not in text:
            continue
        tbl_m = re.search(r'@TableName\(\s*"([^"]+)"\s*\)', text)
        if not tbl_m:
            continue
        table = strip_schema(tbl_m.group(1))
        for col in re.findall(r"private\s+\w+\s+([a-zA-Z]+);", text):
            if not col.startswith("ref"):
                continue
            column = snake(col)
            hits = [t for t in tables if t != table and column.endswith(t)]
            if not hits:
                continue
            target = max(hits, key=len)
            rels.append(
                {"left_table": table, "left_field": column, "right_table": target, "right_field": "code",
                 "evidence": f"ref-convention:{path.name}"}
            )
    return rels


def extract_mapper_joins(repo: Path) -> list[dict]:
    rels: list[dict] = []
    for xml in repo.rglob("*.xml"):
        text = xml.read_text(encoding="utf-8", errors="ignore")
        for sel in re.findall(r"<select.*?</select>", text, flags=re.S):
            alias: dict[str, str] = {}
            for m in re.finditer(r"(?:from|join)\s+([a-zA-Z_][\w.]*)\s+([a-z]\w*)", sel, flags=re.I):
                alias[m.group(2).lower()] = strip_schema(m.group(1).lower())
            for m in re.finditer(r"on\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)", sel, flags=re.I):
                lt, lf, rt, rf = (g.lower() for g in m.groups())
                if lt not in alias or rt not in alias or lt == rt:
                    continue
                if lf in _TENANT or rf in _TENANT:
                    continue
                # 把外键字段放在左侧（fk -> 主键）
                if _is_fk(lf) or rf in ("id", "code"):
                    rels.append({"left_table": alias[lt], "left_field": lf,
                                 "right_table": alias[rt], "right_field": rf,
                                 "evidence": f"mapper:{xml.name}"})
                elif _is_fk(rf) or lf in ("id", "code"):
                    rels.append({"left_table": alias[rt], "left_field": rf,
                                 "right_table": alias[lt], "right_field": lf,
                                 "evidence": f"mapper:{xml.name}"})
    return rels


def extract_java_fk(repo: Path, do_table: dict[str, str]) -> list[dict]:
    rels: list[dict] = []
    for path in repo.rglob("*.java"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if ".eq(" not in text:
            continue
        var_type: dict[str, str] = {}
        for m in re.finditer(r"\b([A-Z]\w*(?:DO|Info|VO|DTO))\s+([a-z]\w*)\b", text):
            if m.group(1) in do_table:
                var_type.setdefault(m.group(2), m.group(1))
        for m in re.finditer(r"\.eq\(\s*(\w+)::get(\w+)\s*,\s*([a-z]\w*)\.get(\w+)\(\)", text):
            target_do, tf, src_var, sf = m.groups()
            if target_do not in do_table or src_var not in var_type:
                continue
            t_tbl, t_f = do_table[target_do], snake(tf)
            s_tbl, s_f = do_table[var_type[src_var]], snake(sf)
            if t_tbl == s_tbl or t_f in _TENANT or s_f in _TENANT:
                continue
            if _is_fk(t_f) and s_f in ("id", "code"):
                rels.append({"left_table": t_tbl, "left_field": t_f,
                             "right_table": s_tbl, "right_field": s_f,
                             "evidence": f"java-eq:{path.name}"})
            elif _is_fk(s_f) and t_f in ("id", "code"):
                rels.append({"left_table": s_tbl, "left_field": s_f,
                             "right_table": t_tbl, "right_field": t_f,
                             "evidence": f"java-eq:{path.name}"})
    return rels


def _file_var_types(text: str, do_table: dict[str, str]) -> dict[str, str]:
    """文件级 var -> DO 类型索引（字段/局部声明/形参，含 List<XxxDO>）。"""
    var_type: dict[str, str] = {}
    for m in re.finditer(r"\b([A-Z]\w*(?:DO|Info|VO|DTO))\b\s*[>,]?\s*([a-z]\w*)\b", text):
        if m.group(1) in do_table:
            var_type.setdefault(m.group(2), m.group(1))
    return var_type


def extract_write_flow(repo: Path, do_table: dict[str, str]) -> list[dict]:
    """写流转：child.setFk(parent.getKey()) — 上一表的查询/创建结果喂给下一表的写入。"""
    rels: list[dict] = []
    for path in repo.rglob("*.java"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if ".set" not in text:
            continue
        var_type = _file_var_types(text, do_table)
        for m in re.finditer(r"(\w+)\.set(\w+)\(\s*([a-z]\w*)\.get(\w+)\(\)", text):
            child_var, field, parent_var, parent_field = m.groups()
            if child_var not in var_type or parent_var not in var_type:
                continue
            child = do_table[var_type[child_var]]
            parent = do_table[var_type[parent_var]]
            if child == parent:
                continue
            f, pf = snake(field), snake(parent_field)
            # 租户隔离 / 字段拷贝（两边同名字段）不是关联
            if f in _TENANT or pf in _TENANT or f in ("tenant_id", "tenant_code") or f == pf:
                continue
            # 只收外键型字段：ref_* / *_id / *_code（排除 Name/Status/Type 等纯拷贝）
            if f.startswith("ref_") or f.endswith("_id") or f.endswith("_code"):
                rels.append({"left_table": child, "left_field": f,
                             "right_table": parent, "right_field": pf,
                             "evidence": f"write-flow:{path.name}"})
    return rels


def extract_read_flow(repo: Path, do_table: dict[str, str]) -> list[dict]:
    """读流转：xxx.getById(yyy.getFk()) / xxx.selectByXxxId(yyy.getFk()) — 上表结果作下表条件。"""
    rels: list[dict] = []
    for path in repo.rglob("*.java"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if ".getBy" not in text and "selectBy" not in text and ".get(" not in text:
            continue
        var_type = _file_var_types(text, do_table)
        for m in re.finditer(r"(\w+)\.(?:getById|getByCode|selectById|selectBy[A-Z]\w*)\(\s*([a-z]\w*)\.get(\w+)\(\)", text):
            callee, src_var, src_field = m.groups()
            if src_var not in var_type:
                continue
            src_table = do_table[var_type[src_var]]
            src_f = snake(src_field)
            if src_f in _TENANT or src_f in ("tenant_id", "tenant_code"):
                continue
            # callee 变量名以实体为前缀（如 xxxService/xxxMapper -> xxx_xxx）
            cand = [do_table[c] for c in do_table if do_table[c].replace("_", "").startswith(
                callee.lower().replace("service", "").replace("mapper", "").replace("query", "").replace("_", ""))]
            if len(cand) == 1 and cand[0] != src_table and src_f in ("id", "code") or (
                    src_f.endswith("_id") or src_f.endswith("_code") or src_f.startswith("ref_")):
                if len(cand) == 1 and cand[0] != src_table:
                    rels.append({"left_table": src_table, "left_field": src_f,
                                 "right_table": cand[0], "right_field": "id" if src_f.endswith("_id") else "code",
                                 "evidence": f"read-flow:{path.name}"})
    return rels


def dedup(rels: list[dict]) -> list[dict]:
    seen: dict[tuple, dict] = {}
    for r in rels:
        key = (r["left_table"], r["left_field"], r["right_table"], r["right_field"])
        if key not in seen:
            seen[key] = r
    return sorted(seen.values(), key=lambda r: (r["left_table"], r["left_field"]))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("-o", "--output")
    args = ap.parse_args()
    repo = Path(args.repo)

    do_table = do_index(repo)
    tables = set(do_table.values())
    rels = dedup(
        extract_ref_convention(repo, tables)
        + extract_mapper_joins(repo)
        + extract_java_fk(repo, do_table)
        + extract_write_flow(repo, do_table)
        + extract_read_flow(repo, do_table)
    )

    out = {"schema_version": "1.0", "repository": repo.name, "relationships": rels}
    if args.output:
        Path(args.output).write_text(
            yaml.safe_dump(out, allow_unicode=True, sort_keys=False), encoding="utf-8"
        )
        print(f"wrote {args.output}")
    print(f"relationships={len(rels)}", file=sys.stderr)
    for r in rels:
        print(f"  {r['left_table']}.{r['left_field']} -> {r['right_table']}.{r['right_field']}  [{r['evidence']}]")


if __name__ == "__main__":
    main()
