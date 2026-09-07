"""Baseline page generator (plan E2.4) — db-first table/enum pages.

基线页 = 存在性真值页：db-catalog（结构权威）∪ 代码 catalog（注释/枚举语义）
→ ``wiki-pages/tables/`` 与 ``wiki-pages/enums/``。语义层页面（Step D 产物）
落同名 page_key 时由 ``merge_pages`` 走 v0 §5.3 确定性块合并——同键碰撞在
源头消解（不再有两堆语料）。

⚠ 重建覆盖契约：``write_pages`` 整页重写会抹掉 enrich 注入的 ``## 关联表``
节（chat 169 复发过一次）。rebuild 之后**必须**再跑
``backend/venv/bin/python scripts/wiki_admin.py enrich --pages <wiki-pages>``
恢复关系节，否则表页缺关联信息、闭包归因少一路来源。

Usage::

    backend/venv/bin/python -m apps.knowledge.wiki.baseline \
        --substrate ../docs/wiki-knowledge/pplatform/substrate \
        --db-dir ../docs/wiki-knowledge/pplatform/db \
        --out ../docs/wiki-knowledge/pplatform/wiki-pages
    backend/venv/bin/python scripts/wiki_admin.py enrich \
        --pages ../docs/wiki-knowledge/pplatform/wiki-pages   # rebuild 后必跑
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
from pathlib import Path
from typing import Any

import yaml

_DS_ID = 15  # 兼容旧引用；围栏已切 scope.databases（库名来自 db-catalog.yaml）
_OID = 1
_DOMAIN = "基线"
_TODAY = None


def _catalog_database(db_dir: Path) -> str:
    """物理库名（scope.databases 围栏值）——db-catalog.yaml 顶层 database 键。"""
    catalog = db_dir / "db-catalog.yaml"
    try:
        data = yaml.safe_load(catalog.read_text()) or {}
    except OSError:
        return "unknown_db"
    name = str(data.get("database") or "").strip()
    return name or "unknown_db"

# MySQL 类型 → v0 类型族（contract §3.1 词表）
_TYPE_FAMILY = {
    "varchar": "string",
    "char": "string",
    "text": "string",
    "mediumtext": "string",
    "longtext": "string",
    "int": "number",
    "integer": "number",
    "bigint": "number",
    "smallint": "number",
    "tinyint": "number",
    "decimal": "number",
    "double": "number",
    "float": "number",
    "date": "temporal",
    "datetime": "temporal",
    "timestamp": "temporal",
    "time": "temporal",
    "bit": "boolean",
    "json": "structured",
    "blob": "structured",
}


def _family(column_type: str) -> str:
    base = column_type.split("(")[0].lower().strip()
    if base.endswith(" unsigned"):
        base = base[:-9]
    return _TYPE_FAMILY.get(base, "string")


def _today() -> str:
    global _TODAY
    if _TODAY is None:
        _TODAY = _dt.date.today().isoformat()
    return _TODAY


def _code_enums(substrate_dir: Path) -> dict[str, dict[str, Any]]:
    """代码枚举基线：field → {value: label}（E3 语义）。

    数据源两段：``enums``（*Enum.java）+ ``constant_enums``（*Constant.java——
    159 病例的 CustBuildTypeConstant 就在这里，漏读会丢"平台录入"权威真值）。"""
    path = substrate_dir / "extract-enums.yaml"
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text()) or {}
    out: dict[str, dict[str, Any]] = {}
    for section in ("enums", "constant_enums"):
        for entry in data.get(section) or []:
            if not isinstance(entry, dict):
                continue
            field = entry.get("field") or ""
            values = {
                v["value"]: (v.get("display") or v["value"])
                for v in entry.get("values") or []
                if isinstance(v, dict)
            }
            if field and values:
                out.setdefault(field, {}).update(values)
    return out


def _dormant_tables(substrate_dir: Path) -> set[str]:
    cg_path = substrate_dir / "callgraph.yaml"
    if not cg_path.exists():
        return set()
    cg = yaml.safe_load(cg_path.read_text()) or {}
    return set(cg.get("dormant_candidates") or [])


def _field_roles(substrate_dir: Path) -> dict[str, dict[str, list[str]]]:
    path = substrate_dir / "field-roles.yaml"
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text()) or {}
    return data.get("roles") or {}


def _field_groups(substrate_dir: Path, table: str) -> dict[str, list[str]]:
    """表 → 强关联字段组（field_roles.extract_groups 的 set 对按表过滤并并组）。
    组名 = 组内首字段派生；跨组重合成员合并（sign_amount_group 含 sign_amount
    与 sign_date 即在两字段行都标 group: sign_amount_group）。"""
    path = substrate_dir / "field-roles.yaml"
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text()) or {}
    member_to_groups: dict[str, set[str]] = {}
    for entries in (data.get("field_groups") or {}).values():
        for entry in entries:
            fields = list(entry.get("fields") or [])
            # 组成员归属哪张表不可靠（set 调用点无表上下文），保守：
            # 字段名出现在本表列集合才绑定
            group = entry.get("group") or f"{fields[0]}_group" if fields else None
            if not group:
                continue
            for f in fields:
                member_to_groups.setdefault(f, set()).add(group)
    return {
        f: sorted(g)
        for f, g in member_to_groups.items()
        if f in _TABLE_COLUMNS.get(table, set())
    }


_TABLE_COLUMNS: dict[str, set[str]] = {}


def _enum_page_for_column(table: str, col: str, carrier_index: dict[str, str]) -> str:
    """表.列 → 权威枚举页 page_key（无绑定返回空）。"""
    return carrier_index.get(f"{table}.{col}", "")


def build_table_pages(*, substrate_dir: Path, db_dir: Path) -> list[tuple[str, str]]:
    """db-catalog ∪ 代码 catalog → table 页（路径, 内容）列表。

    字段行紧凑键（v0.2 契约）：name/type/phys/desc/dict/topk/roles/group。
    列全集不变式（P2）：字段数 == db 列数，生成时断言，不做运行时回退。
    重要关键字段（查询角色/枚举绑定/主键）前置；强关联字段组（同写值点
    set 对，如签收金额↔签收日期）标 group，供规划器同时召回同组字段。"""
    db = yaml.safe_load((db_dir / "db-catalog.yaml").read_text()) or {}
    code = yaml.safe_load((substrate_dir / "extract-catalog.yaml").read_text()) or {}
    db_name = _catalog_database(db_dir)
    db_profile_path = db_dir / "db-profile.yaml"
    profile = (
        yaml.safe_load(db_profile_path.read_text()) if db_profile_path.exists() else {}
    )
    code_tables = code.get("tables") or {}
    if not isinstance(code_tables, dict):
        code_tables = {t["table"]: t for t in code_tables}
    dormant = _dormant_tables(substrate_dir)
    roles_map = _field_roles(substrate_dir)
    # 枚举承载索引（表.列 → 权威枚举页 page_key）——与 build_enum_pages 同源
    _enum_pages, _unbound = build_enum_pages(substrate_dir=substrate_dir, db_dir=db_dir)
    enum_carrier_index: dict[str, str] = {}
    for _rel, content in _enum_pages:
        fm = content.split("\n---\n")[0]
        pk = re.search(r"^page_key: (.+)$", fm, re.M)
        for m in re.finditer(r"^fields: \[(.+)\]$", content, re.M):
            for ref in m.group(1).split(","):
                enum_carrier_index.setdefault(ref.strip(), pk.group(1) if pk else "")
    # db 优先：库里的表全量建页；code-only 表（库里无）跳过——死代码不建页
    pages: list[tuple[str, str]] = []
    for table, meta in sorted((db.get("tables") or {}).items()):
        comment = meta.get("comment") or ""
        code_meta = code_tables.get(table) or {}
        code_fields = code_meta.get("fields") or []
        code_desc = {
            f.get("column"): f.get("comment")
            for f in code_fields
            if isinstance(f, dict)
        }
        is_dormant = table in dormant
        table_roles = roles_map.get(table, {})
        columns = meta.get("columns") or {}
        _TABLE_COLUMNS.clear()
        _TABLE_COLUMNS.update({t: set(c) for t, c in ((table, columns),)})
        groups_map = _field_groups(substrate_dir, table)

        # 闭包捕获按值绑定，避免 B023（循环变量在函数定义后才变化）
        def _importance(
            col: str,
            *,
            _dormant: bool = is_dormant,
            _roles: dict = table_roles,
            _table: str = table,
            _columns: dict = columns,
        ) -> int:
            if _dormant:
                return 0
            r = _roles.get(col) or []
            has_dict = f"{_table}.{col}" in enum_carrier_index
            cinfo = _columns.get(col) or {}
            return (
                2
                if "query" in r
                else (1 if has_dict or cinfo.get("key") == "PRI" else 0)
            )

        rows = [
            "```ground:table",
            f"table: {table}",
            "database: lowcode_pplatform",
            f"desc: {comment or table}",
            f"inactive: {'true' if is_dormant else 'false'}",
        ]
        if not is_dormant:
            # 列全集不变式：table 页字段数必须等于 db 列数——缺失即在生成时
            # 失败（回答"wiki table 确保不缺失字段"：不靠运行时回退，靠生成断言）。
            assert len(columns) > 0, f"{table}: db catalog 无列（底稿损坏，拒绝生成）"
            # db-profile topk（低基数列值集——P2 schema 渲染与枚举翻译共用）
            profile_stats = ((profile.get("tables") or {}).get(table, {}) or {}).get(
                "column_stats"
            ) or {}
            ordered = sorted(
                columns.items(),
                key=lambda kv: (-_importance(kv[0]), kv[0]),
            )
            rows.append("fields:")
            emitted = 0
            for col, cinfo in ordered:
                desc = cinfo.get("comment") or code_desc.get(col) or ""
                phys = str(cinfo.get("type") or "").strip()
                line = f"  - name: {col}\n    type: {_family(phys)}"
                if phys:
                    line += f"\n    phys: {phys}"
                if desc:
                    if ":" in desc or desc.strip() != desc or not desc:
                        desc = json.dumps(desc, ensure_ascii=False)
                    line += f"\n    desc: {desc}"
                # 枚举绑定：强证据归并后的权威枚举页 page_key
                dict_page = _enum_page_for_column(table, col, enum_carrier_index)
                if dict_page:
                    line += f"\n    dict: {dict_page}"
                topk_vals = (profile_stats.get(col) or {}).get("values") or {}
                if topk_vals:
                    # 只保留纯标识符值（JSON 数组形/含特殊字符的样本值是脏数据，
                    # 不是枚举语义）——它们既炸 YAML 也无翻译价值。
                    # 上限 4 值/单值 32 字符/总值 96 字符（chat 167：8 值上限
                    # 让 invoicing_name 这类 7-distinct 测试数据列铺满 prompt）
                    clean_vals: list[str] = []
                    total = 0
                    for v in list(topk_vals.keys())[:8]:
                        text = str(v)
                        if (
                            not text
                            or len(text) > 32
                            or not re.fullmatch(r"[\w\u4e00-\u9fff@.-]+", text)
                        ):
                            continue
                        if len(clean_vals) >= 4 or total + len(text) + 1 > 96:
                            break
                        clean_vals.append(text)
                        total += len(text) + 1
                    if clean_vals:
                        topk = "|".join(clean_vals)
                        line += f"\n    topk: {topk}"
                r = table_roles.get(col) or []
                if r:
                    line += f"\n    roles: [{', '.join(r)}]"
                g = groups_map.get(col) or []
                if g:
                    line += f"\n    group: {', '.join(g)}"
                rows.append(line)
                emitted += 1
            assert emitted == len(columns), (
                f"{table}: 生成字段 {emitted} != db 列 {len(columns)}（列全集被破坏）"
            )
        rows.append("```")
        front = (
            "---\n"
            f"type: table\n"
            f"title: {comment or table}\n"
            f"page_key: {table}\n"
            f"domain: {_DOMAIN}\n"
            "status: draft\n"
            f"anchors: [{table}]\n"
            f"oid: {_OID}\n"
            f"scope:\n  databases: [{db_name}]\n"
            'sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]\n'
            f"created: '{_today()}'\nupdated: '{_today()}'\n"
            'contract_version: "0.1"\n'
            "---\n\n"
        )
        body = (
            f"# {comment or table}\n\n"
            f"（基线页：{len(meta.get('columns') or {})} 字段，"
            f"{'休眠表（无入口调用链）' if is_dormant else '行数估计 ' + str(meta.get('rows_estimate') or 0)}。"
            "行语义/常用过滤待语义摄取增强。）\n\n" + "\n".join(rows) + "\n"
        )
        pages.append((f"tables/{table}.md", front + body))
    return pages


# 泛列名黑名单：这些列名只允许强证据（setter table_bindings）绑定，
# 命名约定/前缀容限匹配会造成灾难性吞吐（19 页挂 .type、14 页挂 .status、
# 3 页挂 .code 的历史教训——ca_fee_block_code 曾同时挂上 73 张表）。
_GENERIC_COLUMNS = {
    "type",
    "status",
    "code",
    "flag",
    "mode",
    "level",
    "source",
    "channel",
    "state",
}
def _column_prefixes(substrate_dir: Path | None = None) -> tuple[str, ...]:
    """Column-name prefixes from settings or substrate config; never hardcoded."""
    from common.core.config import settings

    configured = [
        part.strip()
        for part in str(getattr(settings, "WIKI_COLUMN_PREFIXES", "") or "").split(",")
        if part.strip()
    ]
    if configured:
        return tuple(configured)
    if substrate_dir is None:
        return ()
    path = substrate_dir / "extract-enums.yaml"
    if not path.exists():
        return ()
    data = yaml.safe_load(path.read_text()) or {}
    raw = data.get("column_prefixes") or []
    return tuple(str(item) for item in raw if str(item).strip())


def _clean_display(raw: str) -> str:
    """枚举 display 清洗：剥 // 残留、取 javadoc 首行、去 YAML 危险字符前导。"""
    text = re.sub(r"^//\s*", "", str(raw)).strip()
    text = text.splitlines()[0].strip() if text else text  # 多行 javadoc 粘连取首行
    text = re.sub(r"\s*\*\s*", " ", text)  # 前导 * 是 YAML 别名语法，会炸解析
    text = text.replace("{@code ", "(").replace("{@link ", "(").replace("}", ")")
    return text.strip()


def _enum_source_entries(substrate_dir: Path) -> list[dict[str, Any]]:
    """枚举源条目（enum 类 + constant 类统一），带 field/values/display。"""
    path = substrate_dir / "extract-enums.yaml"
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text()) or {}
    entries: list[dict[str, Any]] = []
    for section in ("enums", "constant_enums"):
        for entry in data.get(section) or []:
            if not isinstance(entry, dict):
                continue
            values = [
                # display 清洗：剥注释残留 + 去多行 javadoc 粘连（YAML 别名/前导 * 会炸解析）
                {
                    "value": v["value"],
                    "display": _clean_display(v.get("display") or v["value"]),
                }
                for v in entry.get("values") or []
                if isinstance(v, dict)
            ]
            if entry.get("field") and values:
                entries.append(
                    {
                        "enum": entry.get("enum"),
                        "field": entry["field"],
                        "values": values,
                    }
                )
    return entries


def _table_bindings(substrate_dir: Path) -> dict[str, list[dict[str, Any]]]:
    """表.列 → [{enum, do, path, line}]（setter 写值点强证据）。"""
    path = substrate_dir / "extract-enums.yaml"
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text()) or {}
    return data.get("table_bindings") or {}


def _carrier_for_factory(
    column_index: dict[str, list[str]],
    real_columns: dict[str, set[str]],
    table_bindings: dict[str, list[dict]],
    entries: list[dict],
    prefixes: tuple[str, ...] = (),
) -> Any:
    """可测试的承载列判定器（build_enum_pages 内部逻辑的纯函数提取）。"""

    def _carrier_for(field: str) -> tuple[list[str], str]:
        strong: dict[str, set[str]] = {}
        for entry in entries:
            if entry["field"] != field or not entry.get("enum"):
                continue
            for key, items in table_bindings.items():
                if any(i.get("enum") == entry["enum"] for i in items):
                    t, _, c = key.partition(".")
                    if t in real_columns and c in real_columns[t]:
                        strong.setdefault(key, set()).add(entry["enum"])
        if strong:
            return sorted(strong.keys()), "setter-evidence"
        if field not in _GENERIC_COLUMNS and column_index.get(field):
            return column_index[field], "exact-name"
        for prefix in prefixes:
            if field.startswith(prefix):
                stripped = field[len(prefix) :]
                if (
                    stripped
                    and stripped not in _GENERIC_COLUMNS
                    and column_index.get(stripped)
                ):
                    return column_index[stripped], "prefix-strip"
        return [], "unbound"

    return _carrier_for


def build_enum_pages(
    *, substrate_dir: Path, db_dir: Path
) -> tuple[list[tuple[str, str]], list[dict[str, str]]]:
    """强证据绑定 → enum 页（同物理列归并为一页）。

    绑定优先级（杜绝泛列吞吐）：
    1. **强证据**：setter 写值点的 表.列 绑定（table_bindings）——权威；
    2. **专有列**：dictKey == 列名，或 dictKey == 业务前缀+列名 且列名非泛列；
    3. 都没有 → 不建页，落 ``ENUM_UNBOUND`` REVIEW（比错挂好）。

    同物理列多枚举类归一为一页（page_key = 物理列名）；label 裁决序 =
    常量类 display > 枚举类 display > db 分布 > 值本身；同值次要说法进
    aliases。返回 (pages, review_items)。"""
    db_profile_path = db_dir / "db-profile.yaml"
    profile = (
        yaml.safe_load(db_profile_path.read_text()) if db_profile_path.exists() else {}
    )
    db_catalog = yaml.safe_load((db_dir / "db-catalog.yaml").read_text()) or {}
    db_name = _catalog_database(db_dir)
    entries = _enum_source_entries(substrate_dir)
    table_bindings = _table_bindings(substrate_dir)

    # db 列索引（验证承载列真实存在）
    real_columns: dict[str, set[str]] = {}
    for table, meta in (db_catalog.get("tables") or {}).items():
        real_columns[table] = set((meta.get("columns") or {}).keys())
    column_index: dict[str, list[str]] = {}
    for table, cols in real_columns.items():
        for col in cols:
            column_index.setdefault(col, []).append(f"{table}.{col}")

    _carrier_for = _carrier_for_factory(
        column_index,
        real_columns,
        table_bindings,
        entries,
        prefixes=_column_prefixes(substrate_dir),
    )

    # 同物理列归并：anchor = 完整 表.列（主 carrier）——不同表的 .status 列是
    # 不同业务列，不因列名相同而同页（cust_group_rel.status ≠ cust_role_info.status）。
    # 页 page_key 用主列名，冲突时带表前缀消歧。
    column_pages: dict[str, dict[str, Any]] = {}
    unbound: list[dict[str, str]] = []
    seen_fields: set[str] = set()
    for entry in sorted(
        entries,
        key=lambda e: (
            0 if str(e.get("enum", "")).endswith("Constant") else 1,
            str(e.get("enum")),
        ),
    ):
        field = entry["field"]
        carriers, binding = _carrier_for(field)
        if not carriers:
            if field not in seen_fields:
                unbound.append(
                    {
                        "code": "ENUM_UNBOUND",
                        "field": field,
                        "enum": str(entry.get("enum")),
                    }
                )
            seen_fields.add(field)
            continue
        seen_fields.add(field)
        primary = carriers[0]  # 强证据的主 carrier（setter 第一落点）
        # 弱↔强同列合并（双向）：弱绑定的 carriers 与已有强证据页重叠 → 并入强页；
        # 强绑定后到、已有弱页占同列 → 迁移弱页内容进强页并废弃旧键。
        if binding != "setter-evidence":
            for existing_primary, existing in column_pages.items():
                if (
                    existing["binding"] == "setter-evidence"
                    and set(carriers) & existing["carriers"]
                ):
                    primary = existing_primary
                    carriers = sorted(
                        set(carriers) | existing["carriers"] | {existing_primary}
                    )
                    break
        elif (
            primary in column_pages
            and column_pages[primary]["binding"] != "setter-evidence"
        ):
            pass  # 同 primary 覆盖：defaultdict 语义下直接合并进现有条目
        page = column_pages.setdefault(
            primary,
            {
                "field": primary,
                "carriers": set(),
                "values": {},
                "aliases": {},
                "binding": binding,
            },
        )
        if binding == "setter-evidence":
            page["binding"] = "setter-evidence"
            # 清理与强页 carriers 重叠的其它弱页（单向并入本强页）
            stale = [
                k
                for k, other in column_pages.items()
                if k != primary
                and other["binding"] != "setter-evidence"
                and (other["carriers"] & set(carriers))
            ]
            for k in stale:
                merged = column_pages.pop(k)
                page["carriers"].update(merged["carriers"] | {k})
                for v, d in merged["values"].items():
                    if v not in page["values"] or page["values"][v] == v:
                        page["values"][v] = d
                for v, alts in merged["aliases"].items():
                    page["aliases"].setdefault(v, []).extend(alts)
        page["carriers"].update(carriers)
        is_constant = str(entry.get("enum", "")).endswith("Constant")
        for v in entry["values"]:
            value, display = v["value"], v["display"]
            if value not in page["values"] or (
                is_constant and page["values"][value] == value
            ):
                page["values"][value] = display
            elif display and display != page["values"].get(value):
                page["aliases"].setdefault(value, []).append(display)

    pages: list[tuple[str, str]] = []
    # page_key 分配：主列名；同名冲突（不同表同名列各成一页）带表前缀消歧
    used_keys: set[str] = set()
    for anchor, page in sorted(column_pages.items()):
        carriers = sorted(page["carriers"])
        values: dict[str, str] = page["values"]
        primary_col = anchor.partition(".")[2]
        page_key = primary_col
        if sum(1 for a in column_pages if a.partition(".")[2] == primary_col) > 1:
            page_key = anchor.replace(".", "__")
        used_keys.add(page_key)
        # db 分布佐证与基线外值
        dist: dict[str, Any] = {}
        for carrier in carriers:
            table_name, _, col = carrier.partition(".")
            stats = (
                (profile.get("tables") or {}).get(table_name, {}).get("column_stats")
                or {}
            ).get(col)
            if stats:
                dist = stats.get("values") or {}
                break
        extra = {v: (dist.get(v, 0)) for v in map(str, dist) if v and v not in values}
        # 同值集扩绑（chat 168：legal_certification_type 枚举页只绑了 2 表，
        # cust_company_info 同名同值集列拿不到 dict 指针 → schema 渲染裸 topk）。
        # 判据：同名列 + 值集高重合。db 分布是超集（含低频基线外值），用
        # "候选值被页值覆盖"方向：候选非空值中 ≥0.7 已在页 values → 同义值集。
        known = set(values) | set(extra)
        if known and primary_col:
            for table_name, cols in real_columns.items():
                carrier_ref = f"{table_name}.{primary_col}"
                if carrier_ref in carriers or primary_col not in cols:
                    continue
                candidate = (
                    (profile.get("tables") or {}).get(table_name, {}) or {}
                ).get("column_stats", {}).get(primary_col) or {}
                cand_vals = {str(v) for v in (candidate.get("values") or {}) if v}
                page_vals = {str(v) for v in known if v}
                if not cand_vals or not page_vals:
                    continue
                coverage = len(cand_vals & page_vals) / len(cand_vals)
                if coverage >= 0.7:
                    carriers.append(carrier_ref)
        rows = [
            "```ground:enum",
            f"enum: {page_key}",
            f"fields: [{', '.join(carriers)}]",
            "values:",
        ]
        for value, label in values.items():
            rows.append(f"  {value}:\n    label: {str(label).strip()}")
        for value in sorted(extra):
            key = (
                value
                if value.replace("_", "").replace("-", "").isalnum()
                else json.dumps(value, ensure_ascii=False)
            )
            rows.append(
                f"  {key}:\n    label: {json.dumps(value, ensure_ascii=False)}\n    note: db 分布存在但代码枚举未声明（REVIEW）"
            )
        alias_labels = sorted(
            {a for alts in page["aliases"].values() for a in alts if 0 < len(a) <= 8}
        )
        rows.append("```")
        front = (
            "---\n"
            f"type: enum\n"
            f"title: {primary_col}\n"
            f"page_key: {page_key}\n"
            f"domain: {_DOMAIN}\n"
            "status: draft\n"
            f"aliases: [{', '.join(alias_labels[:8])}]\n"
            f"oid: {_OID}\n"
            f"scope:\n  databases: [{db_name}]\n"
            'sources: ["code:extract-enums.yaml", "db:db-profile.yaml"]\n'
            f"created: '{_today()}'\nupdated: '{_today()}'\n"
            'contract_version: "0.1"\n'
            "---\n\n"
        )
        body = (
            f"# {primary_col}\n\n"
            f"（权威枚举页：{len(values)} 值，绑定方式 {page['binding']}，主承载 {anchor}；db 实测分布"
            + (f"，基线外 {len(extra)} 值" if extra else "")
            + "。）\n\n"
            + "\n".join(rows)
            + "\n"
        )
        if page["aliases"]:
            diff_lines = [
                f"- {v}: 权威「{values.get(v, v)}」；另有表述 {sorted(set(alts))}"
                for v, alts in sorted(page["aliases"].items())
                if values.get(v) and any(a != values[v] for a in alts)
            ]
            if diff_lines:
                body += "\n## 表述差异\n\n" + "\n".join(diff_lines) + "\n"
        pages.append((f"enums/{page_key}.md", front + body))
    return pages, unbound


def write_pages(out_dir: Path, pages: list[tuple[str, str]]) -> int:
    count = 0
    for rel, content in pages:
        path = out_dir / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        count += 1
    return count


def rebuild_index(out_dir: Path) -> None:
    """程序生成 _index.md（knowledge_map 渲染源）。"""
    from apps.knowledge.wiki.contract import parse_page

    groups: dict[str, list[str]] = {}
    for path in sorted(out_dir.rglob("*.md")):
        if path.name.startswith("_"):
            continue
        page = parse_page(path.read_text(), page_key=path.stem)
        groups.setdefault(page.type, []).append(f"- [[{page.page_key}]] — {page.title}")
    lines = ["# Wiki 页面目录（程序生成，勿手改）", ""]
    for type_ in sorted(groups):
        lines.append(f"## {type_} ({len(groups[type_])})")
        lines.extend(groups[type_])
        lines.append("")
    (out_dir / "_index.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--substrate", required=True)
    parser.add_argument("--db-dir", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    substrate_dir = Path(args.substrate)
    db_dir = Path(args.db_dir)
    out_dir = Path(args.out)

    tables = build_table_pages(substrate_dir=substrate_dir, db_dir=db_dir)
    enum_pages, unbound = build_enum_pages(substrate_dir=substrate_dir, db_dir=db_dir)
    n = write_pages(out_dir, tables + enum_pages)
    rebuild_index(out_dir)
    if unbound:
        review_dir = substrate_dir / "tmp"
        review_dir.mkdir(parents=True, exist_ok=True)
        (review_dir / "enum-unbound.yaml").write_text(
            yaml.safe_dump(unbound, allow_unicode=True, sort_keys=False)
        )
    print(
        f"baseline pages: {n} (tables={len(tables)} enums={len(enum_pages)})"
        f" unbound-enums={len(unbound)} -> {out_dir}"
    )


if __name__ == "__main__":
    main()
