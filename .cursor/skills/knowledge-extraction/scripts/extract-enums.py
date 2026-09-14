#!/usr/bin/env python3
"""Extract enum dictionaries from Java enum classes — plus setter binding evidence.

Two deterministic outputs:

1. Enum dictionaries: ``XxxEnum`` classes with the ``NAME("dictKey", "显示名")``
pattern. The enum class name maps to its DB field by *convention*
(``XxxEnum`` -> ``xxx``), which is only a candidate — see (2).

1b. Constant / interface dictionaries: not only ``*Enum.java``. Vocabulary
often lives in ``interface`` / ``class`` holders (``*Constant``, ``*Constants``,
files under ``constant(s)/``) as ``String NAME = "VALUE"`` (or int), with the
**label taken from the preceding Javadoc / ``//`` comment**. Uncommented
constants are still extracted (``unlabeled: true``) so an LLM can fill labels
from write-sites. This extract is a **baseline only** — actual ``setXxx`` /
``.eq`` / literals can disagree with the declaration.

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
from typing import Any

import yaml


def snake(name: str) -> str:
    # XxxEnum -> xxx（去 Enum 后缀；处理连续大写缩写，如 IDType -> id_type）
    return re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])|(?<=[a-z0-9])(?=[A-Z])", "_", name).lower()


def _is_prod_java(path: Path) -> bool:
    rel = path.as_posix()
    return "/src/test/" not in rel and "/test/" not in rel and not rel.endswith("Test.java")


# setter 实参以枚举/常量类限定符开头——常量类（*Constant / *Constants / 接口）
# 是词汇真源，只认 *Enum 会漏掉写值点（setIdentifyStyle(IdentifyTypeConstant.X)）
_TYPE_SUFFIX = r"(?:Enum|Constants?)"
_SETTER_ENUM_USE = re.compile(rf"\bset([A-Z]\w*)\(\s*([A-Z]\w*{_TYPE_SUFFIX})\s*\.")
# 读点：equals/getDictKey 比较（查询条件/分支判断）
_READ_ENUM_USE = re.compile(
    rf"\b(?:get(\w+)|(\w+))\s*\(\s*\)?\.equals\(\s*([A-Z]\w*{_TYPE_SUFFIX})\s*\."
)


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
        # 接收者已声明且不是 DO → 非落库（DataSource/DTO/Builder 等）
        for dm in reversed(list(re.finditer(rf"\b([A-Z]\w+)\s+{re.escape(receiver)}\b", window))):
            decl_type = dm.group(1)
            if decl_type.endswith("DO"):
                return decl_type if decl_type in do_index else None
            return None
    # 无接收者声明时才退化到最近 DO——有接收者但类型不是 DO 时不要误绑
    if receiver:
        return None
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


_TYPE_DECL_RE = re.compile(
    r"(?:public\s+)?(?:final\s+)?(?:static\s+)?(?P<kind>class|interface)\s+(?P<name>\w+)"
)
# 注释可选：无注释仍提取（unlabeled），描述留给 LLM 从写值点/注释补
_CONST_FIELD_RE = re.compile(
    r"(?:/\*\*(?P<jdoc>(?:(?!\*/).){0,400}?)\*/|(?P<line>//[^\n]*))?[ \t]*\n?[ \t]*"
    r"(?:public\s+)?(?:static\s+)?(?:final\s+)*(?:public\s+)?"
    r"(?:String|Integer|int|long|Long)\s+"
    r"(?P<name>[A-Z][A-Z0-9_]*)\s*=\s*"
    r"(?:\"(?P<svalue>[^\"]+)\"|(?P<ivalue>-?\d+))",
    re.S,
)
_SKIP_CONST_NAME = re.compile(
    r"(Redis|Color|Url|Https?|Template|PageRedirect|ShortLink|Notify|"
    r"ApiConstants?|KeyConstants?|MeidaConstants|MediaConstants)",
    re.I,
)
_VOCAB_NAME = re.compile(
    r"(Constant|Constants|Dict|Status|Type|Code|Style|Mode|Kind|"
    r"Identify|Build|Cert|Role|Scale|Source|Scene|Channel|Action)",
    re.I,
)


def _field_from_type(name: str) -> str:
    for suffix in ("Constants", "Constant", "Enum", "Dict"):
        if name.endswith(suffix) and len(name) > len(suffix):
            name = name[: -len(suffix)]
            break
    return snake(name)


def _clean_const_comment(raw: str) -> str:
    comment = re.sub(r"^\*+\s*|\s*\*/$", "", (raw or "").strip()).strip()
    comment = re.sub(r"^//\s*", "", comment).strip()
    return comment.splitlines()[0].strip() if comment else ""


def _is_vocab_literal(value: str) -> bool:
    if not value or len(value) > 64:
        return False
    if "://" in value:
        return False
    if "{" in value or value.count(":") >= 2:
        return False
    return True


def _is_const_candidate_file(path: Path) -> bool:
    if not _is_prod_java(path):
        return False
    name = path.name
    parts = {p.lower() for p in path.parts}
    if name.endswith(("Constant.java", "Constants.java")):
        return True
    if "constant" in parts or "constants" in parts:
        return name.endswith(".java")
    return False


def constant_enums(repo: Path) -> list[dict]:
    """接口 / 常量类 / *Constants 的字段 → 枚举字典基线。

    值 = 字面量本身（无独立 dictKey 时）；display 取前置 Javadoc/行注释。
    无注释仍保留（``unlabeled: true``）。机械提取可被写值点推翻。
    """
    out: list[dict] = []
    seen: set[str] = set()
    for path in sorted(p for p in repo.rglob("*.java") if _is_const_candidate_file(p)):
        text = path.read_text(encoding="utf-8", errors="ignore")
        decl = _TYPE_DECL_RE.search(text)
        if not decl:
            continue
        name = decl.group("name")
        kind = decl.group("kind")
        if _SKIP_CONST_NAME.search(name):
            continue
        if not _VOCAB_NAME.search(name) and not path.name.endswith(
            ("Constant.java", "Constants.java")
        ):
            continue
        values: list[dict] = []
        for m in _CONST_FIELD_RE.finditer(text):
            raw = m.group("svalue") if m.group("svalue") is not None else m.group("ivalue")
            if raw is None or not _is_vocab_literal(raw):
                continue
            comment = _clean_const_comment(m.group("jdoc") or m.group("line") or "")
            item: dict[str, Any] = {
                "value": str(raw),
                "java_name": m.group("name"),
                "display": comment or str(raw),
            }
            if not comment:
                item["unlabeled"] = True
            values.append(item)
        if len(values) < 2:
            continue
        key = f"{path}:{name}"
        if key in seen:
            continue
        seen.add(key)
        out.append(
            {
                "enum": name,
                "kind": kind,
                "field": _field_from_type(name),
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
        # 常量区止于首个分号或枚举体结束。常量名可以是小写
        # （UserTypeEnum.admin），不能扫全文件，否则会误吃方法调用。
        block_m = re.search(r"enum\s+\w+[^{]*\{([\s\S]*?)(?:;|\n\})", text)
        block = block_m.group(1) if block_m else ""
        # NAME("dictKey", "显示名") — 枚举常量声明（两个字符串实参）
        for m in re.finditer(
            r'\b([A-Za-z_][A-Za-z0-9_]*)\s*\(\s*"([^"]+)"\s*,\s*"([^"]*)"\s*\)',
            block,
        ):
            values.append(
                {
                    "value": m.group(2),
                    "java_name": m.group(1),
                    "display": m.group(3),
                }
            )
        if not values:
            continue
        field = _field_from_type(name)
        enums.append(
            {
                "enum": name,
                "kind": "enum",
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


_ACCESSOR_RE = re.compile(
    rf"\b([A-Z]\w*{_TYPE_SUFFIX})\s*\.\s*([A-Za-z_][A-Za-z0-9_]*)\s*\.\s*"
    r"(name|getDictKey|getDictParam|getCode|getValue|getDisplayName)\s*\(\s*\)"
)
_DICTKEY_ACCESSORS = frozenset({"getDictKey", "getCode", "getValue"})
_NAME_ACCESSORS = frozenset({"name", "getDictParam"})


def scan_accessors(repo: Path) -> dict[tuple[str, str], dict[str, int]]:
    """(EnumClass, JAVA_NAME) → {accessor: count}。"""
    counts: dict[tuple[str, str], dict[str, int]] = {}
    for path in repo.rglob("*.java"):
        if not _is_prod_java(path):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for m in _ACCESSOR_RE.finditer(text):
            key = (m.group(1), m.group(2))
            bucket = counts.setdefault(key, {})
            bucket[m.group(3)] = bucket.get(m.group(3), 0) + 1
    return counts


def _stored_as(accessors: dict[str, int], java_name: str, dict_key: str) -> str:
    dk = sum(accessors.get(name, 0) for name in _DICTKEY_ACCESSORS)
    nm = sum(accessors.get(name, 0) for name in _NAME_ACCESSORS)
    if java_name == dict_key:
        return "same"
    if dk == 0 and nm == 0:
        return "dictKey"
    if nm and dk and min(nm, dk) * 2 >= max(nm, dk):
        return "mixed"
    if nm > dk:
        return "name"
    return "dictKey"


def attach_accessors(
    repo: Path, enums: list[dict], constants: list[dict]
) -> None:
    """就地写入 values[].accessors / stored_as（name vs getDictKey 分轨）。"""
    counts = scan_accessors(repo)
    for entry in (*enums, *constants):
        enum_name = str(entry.get("enum") or "")
        for value in entry.get("values") or []:
            java_name = str(value.get("java_name") or "")
            dict_key = str(value.get("value") or "")
            accessors = dict(counts.get((enum_name, java_name)) or {})
            value["accessors"] = accessors
            value["stored_as"] = _stored_as(accessors, java_name, dict_key)


class _QuotedDumper(yaml.SafeDumper):
    """数字形态字符串必须带引号，否则 01 会被读成整数 1。"""


def _quoted_str(dumper: yaml.SafeDumper, data: str) -> Any:
    looks_numeric = bool(re.match(r"^[\d.]+$", data)) or (
        data[:1].isdigit() if data else False
    )
    reserved = data.lower() in {
        "y",
        "n",
        "yes",
        "no",
        "true",
        "false",
        "on",
        "off",
        "null",
    }
    style = '"' if looks_numeric or reserved or data != data.strip() else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=style)


_QuotedDumper.add_representer(str, _quoted_str)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("-o", "--output")
    args = ap.parse_args()
    repo = Path(args.repo)

    enums, constant_enums_list, bindings, table_bindings = extract_full(repo)
    attach_accessors(repo, enums, constant_enums_list)
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
        if any(cls in enum_names for cls in classes)
    }
    bindings = {field: classes for field, classes in bindings.items() if classes}
    ambiguous = {
        field: classes for field, classes in bindings.items() if len(classes) > 1
    }
    total_values = sum(len(e["values"]) for e in enums)
    mixed = sum(
        1
        for e in (*enums, *constant_enums_list)
        for v in e.get("values") or []
        if v.get("stored_as") in {"name", "mixed"}
    )

    out = {
        "schema_version": "1.5",
        "extract_role": "baseline",
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
            yaml.dump(out, Dumper=_QuotedDumper, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        print(f"wrote {args.output}")

    const_total = sum(len(e["values"]) for e in constant_enums_list)
    print(
        f"enums={len(enums)} values={total_values} constant_enums={len(constant_enums_list)}"
        f" const_values={const_total} bindings={len(bindings)} table_bindings={len(table_bindings)}"
        f" name_or_mixed={mixed}",
        file=sys.stderr,
    )
    for key, items in list(table_bindings.items())[:10]:
        print(f"  TABLE-BIND {key} <- {[i['enum'] for i in items]}", file=sys.stderr)


if __name__ == "__main__":
    main()
