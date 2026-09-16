#!/usr/bin/env python3
"""Remesh wiki-pages-v3 table pages to db-catalog column completeness.

Catalog files are generation input only. Output wiki table pages are the
runtime schema truth: every db column, always-keep fields grouped, scene
windows mirrored onto field.scenes. Vocab (topk / labels / dict) is rebuilt
from db-profile + extract-enums + comment dictionaries.
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

ROOT = next(
    parent
    for parent in Path(__file__).resolve().parents
    if (parent / "backend").is_dir() and (parent / "docs").is_dir()
)
sys.path.insert(0, str(ROOT / "backend"))

from apps.knowledge.wiki.contract import parse_page  # noqa: E402
from apps.knowledge.wiki.field_vocab import (  # noqa: E402
    decide_field_vocab,
    format_labels,
    is_identifier_column,
    parse_comment_labels,
)

PAGES = ROOT / "docs/wiki-knowledge/pplatform/wiki-pages-v3"
DB_CATALOG = ROOT / "docs/wiki-knowledge/pplatform/db/db-catalog.yaml"
DB_PROFILE = ROOT / "docs/wiki-knowledge/pplatform/db/db-profile.yaml"
CODE_CATALOG = ROOT / "docs/wiki-knowledge/pplatform/substrate-v2/extract-catalog.yaml"
EXTRACT_ENUMS = ROOT / "docs/wiki-knowledge/pplatform/substrate-v2/extract-enums.yaml"
FIELD_ROLES = ROOT / "docs/wiki-knowledge/pplatform/substrate-v2/field-roles.yaml"

ALWAYS = [
    "id",
    "code",
    "enable",
    "create_time",
    "update_time",
    "create_by",
    "create_user",
    "update_by",
    "update_user",
]
ALWAYS_WINDOW = ["id", "enable", "create_time", "update_time"]
FIELD_ALIASES = {
    "cust_company_info": {"company_name": "name"},
}
_FLAG_ENUM_CLASSES = {"EnableEnum", "BooleanEnum"}
_GENERIC_ENUM_SLUGS = {"status", "type", "flag", "mode", "state", "code", "enable"}
_TYPE_FAMILY = {
    "varchar": "string",
    "char": "string",
    "text": "string",
    "longtext": "string",
    "mediumtext": "string",
    "tinytext": "string",
    "int": "number",
    "bigint": "number",
    "decimal": "number",
    "numeric": "number",
    "double": "number",
    "float": "number",
    "smallint": "number",
    "tinyint": "number",
    "date": "temporal",
    "datetime": "temporal",
    "timestamp": "temporal",
    "time": "temporal",
    "json": "structured",
    "blob": "structured",
}
_SCENARIO_FENCE = re.compile(r"```ground:scenario\n([\s\S]*?)\n```")
_TABLE_FENCE = re.compile(r"```ground:table\n([\s\S]*?)\n```")
_SPLIT_HEADING = re.compile(
    r"\n## 场景字段划分\n[\s\S]*?(?=\n```ground:table|\n```ground:relation|\Z)"
)
_SLUG = re.compile(r"^[a-z][a-z0-9_]*$")


def family(phys: str) -> str:
    base = str(phys or "").split("(")[0].lower().strip()
    if base.endswith(" unsigned"):
        base = base[:-9]
    return _TYPE_FAMILY.get(base, "string")


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def collect_scene_windows() -> dict[str, dict[str, set[str]]]:
    """table -> field -> set(scenario_key)."""
    used: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for path in sorted((PAGES / "scenarios").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        match = _SCENARIO_FENCE.search(text)
        if not match:
            continue
        data = yaml.safe_load(match.group(1)) or {}
        scene = str(data.get("scenario") or path.stem)
        for group in ("hubs", "shared"):
            for item in data.get(group) or []:
                if not isinstance(item, dict):
                    continue
                table = str(item.get("table") or "")
                aliases = FIELD_ALIASES.get(table, {})
                for raw in item.get("window") or []:
                    field = aliases.get(str(raw), str(raw))
                    used[table][field].add(scene)
    return used


def patch_scenario_windows(db_tables: dict) -> None:
    for path in sorted((PAGES / "scenarios").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        match = _SCENARIO_FENCE.search(text)
        if not match:
            continue
        data = yaml.safe_load(match.group(1)) or {}
        changed = False
        for group in ("hubs", "shared"):
            items = data.get(group) or []
            for item in items:
                if not isinstance(item, dict):
                    continue
                table = str(item.get("table") or "")
                columns = ((db_tables.get(table) or {}).get("columns") or {})
                if not columns:
                    continue
                aliases = FIELD_ALIASES.get(table, {})
                window = [aliases.get(str(x), str(x)) for x in (item.get("window") or [])]
                window = [c for c in window if c in columns]
                always = [c for c in ALWAYS_WINDOW if c in columns]
                rest = [c for c in window if c not in always]
                new_window = always + rest
                if new_window != list(item.get("window") or []):
                    item["window"] = new_window
                    changed = True
            data[group] = items
        if not changed:
            continue
        dumped = yaml.safe_dump(data, allow_unicode=True, sort_keys=False).rstrip()
        text = text[: match.start(1)] + dumped + text[match.end(1) :]
        path.write_text(text, encoding="utf-8")


def wiki_fields(text: str) -> dict[str, dict]:
    match = _TABLE_FENCE.search(text)
    if not match:
        return {}
    payload = re.sub(r"^\.\.\.\s*$", "", match.group(1), flags=re.M)
    try:
        data = yaml.safe_load(payload) or {}
    except yaml.YAMLError:
        data = {}
    out: dict[str, dict] = {}
    for item in data.get("fields") or []:
        if isinstance(item, dict) and item.get("name"):
            out[str(item["name"])] = item
    return out


class VocabIndex:
    def __init__(self) -> None:
        self.profile = load_yaml(DB_PROFILE) if DB_PROFILE.exists() else {}
        self.by_class: dict[str, dict] = {}
        self.bindings: dict[tuple[str, str], list[str]] = {}
        self.existing_pages: set[str] = set()
        self.pending: dict[str, dict[str, Any]] = {}
        if EXTRACT_ENUMS.exists():
            raw = load_yaml(EXTRACT_ENUMS)
            for item in list(raw.get("enums") or []) + list(raw.get("constant_enums") or []):
                if isinstance(item, dict) and item.get("enum"):
                    name = str(item["enum"])
                    if name not in self.by_class or item.get("values"):
                        self.by_class[name] = item
            for key, specs in (raw.get("bindings") or {}).items():
                classes: list[str] = []
                for spec in specs or []:
                    if isinstance(spec, str):
                        classes.append(spec)
                    elif isinstance(spec, dict) and spec.get("enum"):
                        classes.append(str(spec["enum"]))
                if "." in key:
                    table, col = key.split(".", 1)
                    self.bindings.setdefault((table, col), []).extend(classes)
                else:
                    self.bindings.setdefault(("*", key), []).extend(classes)
        enum_dir = PAGES / "enums"
        if enum_dir.exists():
            self.existing_pages = {path.stem for path in enum_dir.glob("*.md")}

    def stats(self, table: str, col: str) -> dict[str, Any]:
        tables = self.profile.get("tables") or {}
        return ((tables.get(table) or {}).get("column_stats") or {}).get(col) or {}

    def classes_for(self, table: str, col: str) -> list[str]:
        seen: list[str] = []
        keys = [(table, col)]
        if col not in _GENERIC_ENUM_SLUGS:
            keys.append(("*", col))
        for key in keys:
            for name in self.bindings.get(key) or []:
                if name not in seen:
                    seen.append(name)
        return seen

    def labels_and_values(self, classes: list[str]) -> tuple[dict[str, str], set[str]]:
        labels: dict[str, str] = {}
        values: set[str] = set()
        for cls in classes:
            meta = self.by_class.get(cls) or {}
            for item in meta.get("values") or []:
                if not isinstance(item, dict) or item.get("value") is None:
                    continue
                val = str(item.get("value"))
                values.add(val)
                display = str(item.get("display") or "").strip()
                if val and display and display != val and not item.get("unlabeled"):
                    if re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", display):
                        continue
                    labels[val] = display
        return labels, values

    def resolve_page(
        self, table: str, col: str, prev_dict: str, classes: list[str], enum_values: set[str]
    ) -> str:
        if prev_dict == "enable" and not (
            enum_values and enum_values <= {"Y", "N", "y", "n"}
        ):
            prev_dict = ""
        if prev_dict and (prev_dict in self.existing_pages or prev_dict in self.pending):
            return prev_dict
        suggested: list[str] = []
        for cls in classes:
            keys = {
                str(item.get("value"))
                for item in (self.by_class.get(cls) or {}).get("values") or []
                if isinstance(item, dict) and item.get("value") is not None
            }
            if cls in _FLAG_ENUM_CLASSES or (keys and keys <= {"Y", "N", "y", "n"}):
                if "enable" in self.existing_pages:
                    suggested.append("enable")
                continue
            field_slug = str((self.by_class.get(cls) or {}).get("field") or "").strip()
            if field_slug in self.existing_pages or field_slug in self.pending:
                suggested.append(field_slug)
            elif col in self.existing_pages or col in self.pending:
                suggested.append(col)
            else:
                alias = self._existing_alias(field_slug) or self._existing_alias(col)
                if alias:
                    suggested.append(alias)
            if not suggested:
                if col not in _GENERIC_ENUM_SLUGS and _SLUG.match(col):
                    suggested.append(col)
                elif (
                    field_slug
                    and field_slug not in _GENERIC_ENUM_SLUGS
                    and _SLUG.match(field_slug)
                ):
                    suggested.append(field_slug)
                elif _SLUG.match(f"{table}__{col}"):
                    suggested.append(f"{table}__{col}")
        if not suggested and enum_values and enum_values <= {"Y", "N", "y", "n"} and "enable" in self.existing_pages:
            return "enable"
        return suggested[0] if suggested else ""

    def _existing_alias(self, slug: str) -> str:
        text = str(slug or "")
        if not text:
            return ""
        if text in self.existing_pages or text in self.pending:
            return text
        for page in sorted(self.existing_pages | set(self.pending), key=len, reverse=True):
            if len(page) < 8:
                continue
            if text.endswith(page) or page.endswith(text):
                return page
        return ""

    def queue_enum(
        self,
        page: str,
        *,
        table: str,
        col: str,
        labels: dict[str, str],
        values: set[str],
        classes: list[str],
    ) -> None:
        if not page or page == "enable" or page in self.existing_pages:
            return
        if not labels:
            return
        source = classes[0] if classes else ""
        path = (self.by_class.get(source) or {}).get("path") or ""
        java = Path(str(path)).name if path else source
        entry = self.pending.setdefault(
            page,
            {
                "labels": dict(labels),
                "values": set(values),
                "fields": set(),
                "source": java or source,
                "title": page,
            },
        )
        entry["fields"].add(f"{table}.{col}")
        entry["values"].update(values)
        for key, label in labels.items():
            entry["labels"][key] = label
        self.existing_pages.add(page)


def apply_vocab(
    *,
    table: str,
    col: str,
    phys: str,
    desc: str,
    prev: dict,
    ctx: VocabIndex,
) -> dict[str, str]:
    fam = family(phys)
    if fam in {"temporal", "structured"}:
        return {}
    stats = ctx.stats(table, col)
    raw_values = stats.get("values") or {}
    stats_keys = {str(k) for k in raw_values if str(k).strip() != ""}
    classes = ctx.classes_for(table, col)
    code_labels, enum_values = ctx.labels_and_values(classes)
    if stats_keys:
        code_labels = {k: v for k, v in code_labels.items() if k in stats_keys}
        enum_values = {v for v in enum_values if v in stats_keys}
    comment_labels = parse_comment_labels(desc)
    merged_labels = {**comment_labels, **code_labels}
    if stats_keys and stats_keys <= {"Y", "N", "y", "n"}:
        prev_dict = "enable"
        page = "enable"
        page_values = {"Y", "N"}
    else:
        prev_dict = str(prev.get("dict") or "").strip()
        page = ctx.resolve_page(table, col, prev_dict, classes, enum_values)
        page_values = set(enum_values)
        if page == "enable":
            page_values = {"Y", "N"}
    cjk_labels = {
        k: v for k, v in merged_labels.items() if re.search(r"[\u4e00-\u9fff]", str(v))
    }
    fallback = ""
    if page and page not in {"enable"} and page not in ctx.existing_pages:
        keep_new = bool(cjk_labels) and len(page_values or merged_labels) <= 20
        if keep_new:
            fallback = page
            ctx.queue_enum(
                page,
                table=table,
                col=col,
                labels={k: merged_labels[k] for k in cjk_labels},
                values=page_values or set(cjk_labels),
                classes=classes,
            )
        else:
            page = ""
    dict_page = page if page in ctx.existing_pages or page == "enable" else ""
    out = decide_field_vocab(
        col=col,
        phys=phys,
        family=fam,
        desc=desc,
        stats=stats,
        dict_page=dict_page,
        enum_values=page_values if dict_page else set(),
        fallback_dict=fallback if dict_page else "",
    )
    keys = [str(k) for k in raw_values if str(k).strip() != ""]
    if merged_labels and not is_identifier_column(
        col, desc=desc, phys=phys, values=raw_values
    ):
        formatted = format_labels(merged_labels, keys or list(merged_labels))
        if formatted:
            out["labels"] = formatted
        if dict_page:
            out["dict"] = dict_page
        elif fallback:
            out["dict"] = fallback
    if (
        dict_page == "enable"
        and "dict" not in out
        and stats_keys
        and stats_keys <= {"Y", "N", "y", "n"}
    ):
        # decide_field_vocab may skip empty stats; Y/N switches still pin enable
        out["dict"] = "enable"
    return out


def emit_field(field: dict) -> str:
    lines = [f"  - name: {field['name']}", f"    type: {field['type']}"]
    if field.get("phys"):
        lines.append(f"    phys: {field['phys']}")
    if field.get("desc"):
        lines.append(f"    desc: {json.dumps(str(field['desc']), ensure_ascii=False)}")
    if field.get("dict"):
        lines.append(f"    dict: {field['dict']}")
    if field.get("topk"):
        lines.append(f'    topk: "{field["topk"]}"')
    if field.get("labels"):
        lines.append(f'    labels: "{field["labels"]}"')
    if field.get("roles"):
        roles = field["roles"]
        if isinstance(roles, str):
            roles = [roles]
        lines.append(f"    roles: [{', '.join(roles)}]")
    if field.get("group"):
        lines.append(f"    group: {field['group']}")
    if field.get("scenes"):
        scenes = field["scenes"]
        lines.append(f"    scenes: [{', '.join(scenes)}]")
    return "\n".join(lines)


def merge_table(
    table: str,
    db_meta: dict,
    code_fields: dict[str, dict],
    existing: dict[str, dict],
    scene_use: dict[str, set[str]],
    roles_map: dict[str, list[str]],
    ctx: VocabIndex,
) -> tuple[list[dict], str]:
    columns = db_meta.get("columns") or {}
    aliases = FIELD_ALIASES.get(table, {})
    overlay = dict(existing)
    for old, new in aliases.items():
        if old in overlay and new not in overlay:
            item = dict(overlay[old])
            item["name"] = new
            overlay[new] = item
        overlay.pop(old, None)

    merged: list[dict] = []
    for col, cinfo in columns.items():
        phys = str(cinfo.get("type") or "").strip()
        code = code_fields.get(col) or {}
        prev = overlay.get(col) or {}
        desc = str(prev.get("desc") or cinfo.get("comment") or code.get("comment") or "").strip()
        field: dict = {
            "name": col,
            "type": family(phys),
        }
        if phys:
            field["phys"] = phys
        if desc:
            field["desc"] = desc
        vocab = apply_vocab(
            table=table, col=col, phys=phys, desc=desc, prev=prev, ctx=ctx
        )
        for key in ("dict", "topk", "labels"):
            if vocab.get(key):
                field[key] = vocab[key]
        roles = prev.get("roles") or roles_map.get(col) or []
        if isinstance(roles, str):
            roles = [roles]
        if roles:
            field["roles"] = list(roles)
        if col in ALWAYS:
            field["group"] = "always"
        scenes = sorted(scene_use.get(col) or [])
        if scenes:
            field["scenes"] = scenes
        merged.append(field)

    order_rank = {}
    for idx, name in enumerate(ALWAYS):
        order_rank[name] = idx

    def sort_key(field: dict) -> tuple:
        name = field["name"]
        if name in order_rank:
            return (0, order_rank[name], name)
        if field.get("scenes") or field.get("dict"):
            return (1, name)
        return (2, name)

    merged.sort(key=sort_key)

    always_present = [c for c in ALWAYS if c in columns]
    by_scene: dict[str, list[str]] = defaultdict(list)
    unassigned: list[str] = []
    for field in merged:
        scenes = field.get("scenes") or []
        if scenes:
            for scene in scenes:
                by_scene[scene].append(field["name"])
        elif field.get("group") != "always":
            unassigned.append(field["name"])
    lines = ["## 场景字段划分", ""]
    lines.append(
        "本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。"
        "未分窗的列仍在本页，问题点到列名时才会展开。"
    )
    lines.append("")
    if always_present:
        lines.append("### always")
        lines.append("")
        lines.append("各场景默认带：`" + "`, `".join(always_present) + "`")
        lines.append("")
    for scene in sorted(by_scene):
        cols = by_scene[scene]
        lines.append(f"### [[{scene}]]")
        lines.append("")
        lines.append("`" + "`, `".join(cols) + "`")
        lines.append("")
    if unassigned:
        lines.append("### 未分窗")
        lines.append("")
        lines.append(
            "仍留表页，待代码证据划入场景：`" + "`, `".join(unassigned) + "`"
        )
        lines.append("")
    return merged, "\n".join(lines)


def rebuild_table_page(
    path: Path,
    db_tables: dict,
    code_tables: dict,
    scene_index: dict[str, dict[str, set[str]]],
    roles_all: dict,
    ctx: VocabIndex,
) -> str | None:
    table = path.stem
    db_meta = db_tables.get(table)
    if not db_meta:
        return f"skip {table}: not in db-catalog"
    text = path.read_text(encoding="utf-8")
    existing = wiki_fields(text)
    code_meta = code_tables.get(table) or {}
    code_fields = {
        f.get("column"): f
        for f in (code_meta.get("fields") or [])
        if isinstance(f, dict)
    }
    merged, heading = merge_table(
        table,
        db_meta,
        code_fields,
        existing,
        scene_index.get(table) or {},
        (roles_all.get(table) or {}),
        ctx,
    )
    comment = (db_meta.get("comment") or code_meta.get("comment") or table).strip()
    ground = [
        "```ground:table",
        f"table: {table}",
        "database: lowcode_pplatform",
        f"desc: {comment or table}",
        "fields:",
    ]
    ground.extend(emit_field(f) for f in merged)
    ground.append("```")
    new_table = "\n".join(ground)

    body = text
    body = _SPLIT_HEADING.sub("\n", body)
    match = _TABLE_FENCE.search(body)
    if not match:
        return f"skip {table}: no ground:table"
    insert_at = match.start()
    prefix = body[:insert_at].rstrip() + "\n\n" + heading + "\n"
    suffix = body[match.end() :]
    body = prefix + new_table + suffix
    path.write_text(body if body.endswith("\n") else body + "\n", encoding="utf-8")
    n_db = len(db_meta.get("columns") or {})
    if len(merged) != n_db:
        return f"ERROR {table}: wiki {len(merged)} != db {n_db}"
    return f"ok {table} fields={len(merged)}"


def _enum_value_lines(labels: dict[str, str], values: set[str]) -> str:
    keys = list(values) if values else list(labels)
    # stable: numeric-looking keys first in numeric order, then alpha
    def key_sort(item: str) -> tuple:
        if re.fullmatch(r"[0-9]+", item):
            return (0, int(item), item)
        return (1, 0, item)

    lines: list[str] = []
    seen: set[str] = set()
    for key in sorted(keys, key=key_sort):
        if key in seen:
            continue
        seen.add(key)
        label = str(labels.get(key) or "").strip()
        quoted = json.dumps(key, ensure_ascii=False)
        if label and label != key:
            lines.append(f"  {quoted}:")
            lines.append(f"    label: {json.dumps(label, ensure_ascii=False)}")
        else:
            lines.append(f"  {quoted}: {{}}")
    return "\n".join(lines)


def write_pending_enums(ctx: VocabIndex) -> list[str]:
    reports: list[str] = []
    for key, meta in sorted(ctx.pending.items()):
        path = PAGES / "enums" / f"{key}.md"
        if path.exists():
            continue
        fields = ", ".join(sorted(meta["fields"]))
        labels: dict[str, str] = meta["labels"]
        values: set[str] = set(meta["values"]) | set(labels)
        source = meta.get("source") or ""
        if key == "data_type":
            body = (
                "[[cust_company_info]] 的 `data_type`：同一企业在本表可同时有主数据行和流程行。\n\n"
                "代码 `CustDataTypeConstant`：`1` 主数据、`0` 流程数据、`2` 编辑过程。"
                "列注释写成「1,主数据，0记录数据」，漏了 `2`，且把 `0` 叫记录数据——"
                "问数以代码为准。主数据行才参与生效/冻结/注销。问有效企业见 [[effective_company]]。"
            )
        else:
            field_list = ", ".join(f"`{item}`" for item in sorted(meta["fields"]))
            body = f"{field_list}。"
        page = (
            "---\n"
            f"type: enum\n"
            f"title: {key}\n"
            f"page_key: {key}\n"
            "domain: 基线\n"
            "status: draft\n"
            "oid: 1\n"
            "scope:\n"
            "  databases: [lowcode_pplatform]\n"
            f"sources: {json.dumps([f'code:{source}'] if source else ['code:extract-enums.yaml'], ensure_ascii=False)}\n"
            "created: '2026-09-14'\n"
            "updated: '2026-09-14'\n"
            'contract_version: "0.3"\n'
            "belong: enums\n"
            "---\n\n"
            f"# {key}\n\n"
            f"{body}\n\n"
            "```ground:enum\n"
            f"enum: {key}\n"
            f"fields: [{fields}]\n"
            "values:\n"
            f"{_enum_value_lines(labels, values)}\n"
            "```\n"
        )
        path.write_text(page, encoding="utf-8")
        reports.append(f"enum {key} fields={len(meta['fields'])}")
    return reports


def rebuild_index() -> None:
    by_type: dict[str, list[tuple[str, str]]] = {}
    for path in sorted(PAGES.rglob("*.md")):
        if path.name.startswith("_") or path.name == "README.md" or ".obsidian" in path.parts:
            continue
        try:
            page = parse_page(path.read_text(encoding="utf-8"), page_key=path.stem)
        except Exception:  # noqa: BLE001
            continue
        by_type.setdefault(page.type, []).append((page.page_key, page.title))
    lines = [
        "# Wiki 页面目录（程序生成，勿手改）",
        "",
        "预览语料 wiki-pages-v3，未接入运行时。纪律见提取规范 §11.4。",
        "",
    ]
    total = 0
    for page_type in sorted(by_type):
        entries = sorted(by_type[page_type])
        total += len(entries)
        lines.append(f"## {page_type} ({len(entries)})")
        for key, title in entries:
            lines.append(f"- [[{key}]] — {title}")
        lines.append("")
    lines.append(f"共 {total} 页。")
    (PAGES / "_index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    db = load_yaml(DB_CATALOG)
    code = load_yaml(CODE_CATALOG)
    roles_all = (load_yaml(FIELD_ROLES).get("roles") or {}) if FIELD_ROLES.exists() else {}
    db_tables = db.get("tables") or {}
    code_tables = code.get("tables") or {}
    if isinstance(code_tables, list):
        code_tables = {t.get("table"): t for t in code_tables if isinstance(t, dict)}

    patch_scenario_windows(db_tables)
    scene_index = collect_scene_windows()
    ctx = VocabIndex()

    reports = []
    for path in sorted((PAGES / "tables").glob("*.md")):
        reports.append(
            rebuild_table_page(path, db_tables, code_tables, scene_index, roles_all, ctx)
        )
    reports.extend(write_pending_enums(ctx))
    rebuild_index()
    print("\n".join(r for r in reports if r))
    errors = [r for r in reports if r and r.startswith("ERROR")]
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
