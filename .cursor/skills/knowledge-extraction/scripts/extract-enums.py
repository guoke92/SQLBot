#!/usr/bin/env python3
"""Extract enum dictionaries from Java enum classes — plus setter binding evidence.

Two deterministic outputs:

1. Enum dictionaries: ``XxxEnum`` classes with the ``NAME("dictKey", "显示名")``
pattern. The enum class name maps to its DB field by *convention*
(``XxxEnum`` -> ``xxx``), which is only a candidate — see (2).

1b. Constant-class dictionaries: ``XxxConstant`` classes/interfaces holding
``/** 注释 */ public final static String NAME = "VALUE";`` fields. The class
name maps to its DB field by convention (``XxxConstant`` -> ``xxx``). These
carry status/type vocabularies that never became Java enums (e.g.
``CustBuildTypeConstant``: PC_BUILD=客户端录入, AGW_BUILD=平台录入) — found
missing by the pplatform P1-B source-extraction pilot.

2. Setter binding evidence: call sites like
``setIdentifyStyle(IdentifyStyleEnum.INVITE.getDictKey())`` bind an enum
class to the field the setter writes. This is the evidence-based binding the
AI agent verifies against the write-value inventory during penetration; a
field bound to more than one enum class (``ambiguous_fields``) is a
near-synonym boundary signal that MUST be resolved (reference.md §8).

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


# setter 实参以枚举/常量类限定符开头——常量类（*Constant）是 159 病例真源，
# 只认 *Enum 会漏掉全部常量写值点（setIdentifyStyle(IdentifyTypeConstant.X) 21 处）
_SETTER_ENUM_USE = re.compile(r"\bset([A-Z]\w*)\(\s*([A-Z]\w*(?:Enum|Constant))\s*\.")
# 读点：equals/getDictKey 比较（查询条件/分支判断）
_READ_ENUM_USE = re.compile(r"\b(?:get(\w+)|(\w+))\s*\(\s*\)?\.equals\(\s*([A-Z]\w*(?:Enum|Constant))\s*\.")


def _do_table_index(repo: Path) -> dict[str, str]:
    """DO 类名 → 物理表名（@TableName）——setter 表上下文推断的底座。"""
    index: dict[str, str] = {}
    for path in sorted(repo.rglob("*.java")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "@TableName" not in text:
            continue
        cls = re.search(r"class\s+(\w+)", text)
        tbl = re.search(r'@TableName\(\s*"([^"]+)"\s*\)', text)
        if cls and tbl:
            name = tbl.group(1)
            name = re.match(r"^[a-z_]+\.([a-z_]+)$", name).group(1) if re.match(r"^[a-z_]+\.[a-z_]+$", name) else name
            index[cls.group(1)] = name
    return index


def _method_owner_do(text: str, match_start: int, do_index: dict[str, str]) -> str | None:
    """setter 调用点向上找接收者变量的 DO 类型——推断写值落表。

    接收者 = setter 前最近的 ``<ident>.``（``custRoleInfoDO.setStatus(...)`` →
    custRoleInfoDO）；向上找最近的 ``XxxDO <receiver>`` 同名声明/形参。
    **仅接受 DO 类型**（以 DO 结尾且在 @TableName 索引中）——DTO 接收者
    （OperatorSendEmailProjectDTO.setCheckStatus）是展示层拷贝，不算落库证据。
    找不到同名声明时退化为最近 DO 声明。"""
    prefix = text[max(0, match_start - 200) : match_start]
    m_recv = re.search(r"([A-Za-z_]\w*)\s*\.\s*$", prefix)
    receiver = m_recv.group(1) if m_recv else None
    window = text[max(0, match_start - 4000) : match_start]
    if receiver:
        # 接收者直接以 DO 类型声明
        for dm in reversed(list(re.finditer(rf"\b([A-Z]\w*DO)\s+{re.escape(receiver)}\b", window))):
            if dm.group(1) in do_index:
                return dm.group(1)
        # 接收者是 DTO/其他类型 → 查其声明类型，若非 DO 则返回 None（非落库写值）
        for dm in reversed(list(re.finditer(rf"\b([A-Z]\w+)\s+{re.escape(receiver)}\b", window))):
            decl_type = dm.group(1)
            if decl_type.endswith("DO"):
                return decl_type if decl_type in do_index else None
            if decl_type.endswith(("DTO", "Dto", "VO", "Req", "Res")):
                return None
    m_last = None
    for dm in re.finditer(r"\b([A-Z]\w*DO)\s+\w+\b", window):
        m_last = dm
    if m_last and m_last.group(1) in do_index:
        return m_last.group(1)
    return None


def _do_field_column(repo: Path) -> dict[tuple[str, str], str]:
    """(DO 类, 驼峰字段) → 物理列名——@TableField 显式映射或驼峰转下划线。"""
    mapping: dict[tuple[str, str], str] = {}
    for path in sorted(repo.rglob("*.java")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "@TableName" not in text:
            continue
        cls = re.search(r"class\s+(\w+)", text)
        if not cls:
            continue
        for m in re.finditer(
            r'(?:@TableField\(\s*"([^"]+)"\s*\)\s*)?'
            r"(?:private|protected|public)\s+[\w.<>\[\]]+\s+(\w+)\s*;",
            text,
        ):
            field_name = m.group(2)
            if m.group(1):
                mapping[(cls.group(1), field_name)] = m.group(1)
            else:
                mapping[(cls.group(1), field_name)] = snake(field_name)
    return mapping


def setter_bindings(repo: Path) -> dict[str, list[str]]:
    """field -> enum classes written via setters, from all Java sources."""
    bindings: dict[str, set[str]] = {}
    for path in sorted(repo.rglob("*.java")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for m in _SETTER_ENUM_USE.finditer(text):
            field = snake(m.group(1))
            bindings.setdefault(field, set()).add(m.group(2))
    return {field: sorted(enums) for field, enums in sorted(bindings.items())}


def setter_table_bindings(repo: Path) -> dict[str, list[dict]]:
    """``表.列 -> [{enum, do, path, line}]`` —— setter 写值点带表上下文的强证据。

    这是 dictKey→物理列的权威绑定（identify_type 常量类 →
    cust_company_info.identify_style），命名约定绑定降级为无证据时的候选。
    排除：测试目录（fixture 无业务语义）与 DTO 接收者（展示层拷贝，非落库
    写值——OperatorSendEmailProjectDTO.setCheckStatus 曾把枚举误绑到非 DO 表）。"""
    do_index = _do_table_index(repo)
    do_field = _do_field_column(repo)
    out: dict[str, dict[str, dict]] = {}
    for path in sorted(repo.rglob("*.java")):
        rel = path.as_posix()
        if "/src/test/" in rel or "/test/" in rel or rel.endswith("Test.java"):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for m in _SETTER_ENUM_USE.finditer(text):
            setter_field = m.group(1)
            enum_class = m.group(2)
            do_class = _method_owner_do(text, m.start(), do_index)
            if not do_class:
                continue
            column = do_field.get((do_class, setter_field)) or snake(setter_field)
            table = do_index[do_class]
            key = f"{table}.{column}"
            out.setdefault(key, {}).setdefault(
                enum_class,
                {"enum": enum_class, "do": do_class, "path": str(path.relative_to(repo)), "line": text[: m.start()].count("\n") + 1},
            )
    return {key: sorted(items.values(), key=lambda x: x["enum"]) for key, items in sorted(out.items())}


_CONST_CLASS_RE = re.compile(r"(?:public\s+)?(?:final\s+)?(?:class|interface)\s+(\w*Constant\w*)")
_CONST_FIELD_RE = re.compile(
    r"(?:/\*\*(?P<jdoc>(?:(?!\*/).)*)\*/|(?P<line>//[^\n]*))\s*"
    r"(?:public\s+)?(?:final\s+)?(?:static\s+)?String\s+"
    r"(?P<name>[A-Z][A-Z0-9_]*)\s*=\s*\"(?P<value>[^\"]+)\"",
    re.S,
)


def constant_enums(repo: Path) -> list[dict]:
    """``XxxConstant`` 类/接口的 public static String 常量 → 枚举字典。

    值 = 常量字符串本身（无独立 dictKey），display 取前置 Javadoc/行注释。
    这类常量承载未升级为 Java enum 的状态/类型词汇——159 病例
    （CustBuildTypeConstant：PC_BUILD=客户端录入，AGW_BUILD=平台录入）的
    真源。
    """
    out: list[dict] = []
    for path in sorted(repo.rglob("*Constant.java")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        cls = _CONST_CLASS_RE.search(text)
        if not cls:
            continue
        name = cls.group(1)
        values: list[dict] = []
        for m in _CONST_FIELD_RE.finditer(text):
            comment = (m.group("jdoc") or m.group("line") or "").strip()
            comment = re.sub(r"^\*+\s*|\s*\*/$", "", comment).strip()
            if not comment:
                continue
            values.append({"value": m.group("value"), "display": comment})
        if not values:
            continue
        field = snake(name[: -len("Constant")] if name.endswith("Constant") else name)
        out.append(
            {
                "enum": name,
                "field": field,
                "path": str(path.relative_to(repo)),
                "values": values,
            }
        )
    return out


def extract(repo: Path) -> tuple[list[dict], dict[str, list[str]]]:
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
    return enums, setter_bindings(repo)


def extract_full(repo: Path) -> tuple[list[dict], list[dict], dict[str, list[str]], dict[str, list[dict]]]:
    """全量提取：枚举类 + 常量类 + 字段绑定 + 表.列强证据绑定。"""
    enums, bindings = extract(repo)
    constants = constant_enums(repo)
    table_bindings = setter_table_bindings(repo)
    return enums, constants, bindings, table_bindings


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("-o", "--output")
    args = ap.parse_args()
    repo = Path(args.repo)

    enums, constant_enums_list, bindings, table_bindings = extract_full(repo)
    enum_names = {e["enum"] for e in enums} | {e["enum"] for e in constant_enums_list}
    for entry in enums:
        # 证据绑定：该枚举类被哪些字段的 setter 实际写入
        entry["setter_fields"] = sorted(
            field for field, classes in bindings.items() if entry["enum"] in classes
        )
        entry["convention_mismatch"] = bool(
            entry["setter_fields"]
            and entry["field"] not in entry["setter_fields"]
        )
    # 只保留枚举类真实存在于本仓的绑定；其余引用（外部枚举）对提取无价值
    bindings = {
        field: [cls for cls in classes if cls in enum_names]
        for field, classes in bindings.items()
    }
    bindings = {field: classes for field, classes in bindings.items() if classes}
    ambiguous = {
        field: classes for field, classes in bindings.items() if len(classes) > 1
    }
    total_values = sum(len(e["values"]) for e in enums)

    out = {
        "schema_version": "1.3",
        "repository": repo.name,
        "enums": enums,
        "constant_enums": constant_enums_list,
        "bindings": bindings,
        # 表.列 → [{enum, do, path, line}]：dictKey→物理列的强证据绑定
        "table_bindings": table_bindings,
        "ambiguous_fields": ambiguous,
    }
    if args.output:
        Path(args.output).write_text(
            yaml.safe_dump(out, allow_unicode=True, sort_keys=False), encoding="utf-8"
        )
        print(f"wrote {args.output}")

    const_total = sum(len(e["values"]) for e in constant_enums_list)
    print(
        f"enums={len(enums)} values={total_values} constant_enums={len(constant_enums_list)}"
        f" const_values={const_total} bindings={len(bindings)} table_bindings={len(table_bindings)}",
        file=sys.stderr,
    )
    for key, items in list(table_bindings.items())[:10]:
        print(f"  TABLE-BIND {key} <- {[i['enum'] for i in items]}", file=sys.stderr)


if __name__ == "__main__":
    main()
