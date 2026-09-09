"""Wiki-backend schema rendering (P2) — table pages as schema authority.

wiki 后端下 planner 的 schema_text 改由 wiki table 页渲染：物理类型(phys)、
注释(desc)、值集(topk)、枚举页(dict)、**表间关联(relation 段)** 一并呈现；
字段行格式与 ``presentation.schema_field_labels`` 的正则兼容
（``(field:type, comment)``）——关联行以 ``关联:`` 开头、非整行括号形态，
不进入 label 候选池。

列全集不变式在生成侧保证（baseline 断言 字段数==db 列数），本渲染器不做
运行时回退——某表 wiki 页缺失时该表用 db catalog 直渲并记
``SCHEMA_PAGE_MISSING`` 遥测（update.py 增量触发下轮补齐）。
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from common.utils.utils import SQLBotLogUtil

# schema_field_labels 兼容行格式：(field:type, comment[, topk=...])
_FIELD_LINE = "({field}:{type}, {comment}{topk})"
# 关联段行（enrich 生成）：`- [[t2]]：t1.fk → t2.pk（evidence，confirmed）`
# 供渲染层确定性解析；不是整行括号形态，schema_field_labels 不消费。
_RELATION_ROW_RE = re.compile(
    r"^- \[\[(?P<right>[^\]]+)\]\]："
    r"(?P<left_ref>[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*)\s*→\s*"
    r"(?P<right_ref>[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*)"
    r"(?:\s*（(?P<note>[^）]*)）)?",
    re.M,
)
_RELATION_HEADING = "## 关联表"


def _lookup_store_page(
    store: Any,
    slug: str,
    *,
    belong: str | None = None,
    page_type: str | None = None,
) -> Any | None:
    if store is None:
        return None
    pages = getattr(store, "pages", {}) or {}
    if belong:
        prefixed = pages.get(f"{belong}/{slug}")
        if prefixed is not None:
            return prefixed
    page = pages.get(slug)
    if page is not None:
        actual = getattr(page, "type", None)
        if page_type and actual not in (page_type, None, ""):
            return None
        return page
    getter = getattr(store, "get_page", None)
    if not callable(getter):
        return None
    page = getter(slug)
    if page is None:
        return None
    actual = getattr(page, "type", None)
    if page_type and actual not in (page_type, None, ""):
        return None
    return page


def _wiki_table_block(page_text: str) -> dict[str, Any] | None:
    """解析 table 页的 ground:table 块（已发布的权威字段清单）。"""
    m = re.search(r"```ground:table\n([\s\S]*?)\n```", page_text)
    if not m:
        return None
    try:
        import yaml

        data = yaml.safe_load(m.group(1)) or {}
        return data if isinstance(data, dict) else None
    except yaml.YAMLError:
        return None


class WikiSchemaRenderer:
    """把 working set 的表渲染成 schema_text（wiki 权威 + db 直渲兜底）。"""

    def __init__(
        self,
        store: Any,
        db_catalog: dict[str, Any] | None = None,
        pages_root: Path | None = None,
        missing_tables: list[str] | None = None,
        live_tables: dict[str, Any] | None = None,
    ) -> None:
        self._store = store
        self._db_catalog = db_catalog or {}
        self._pages_root = pages_root
        self._missing: list[str] = missing_tables if missing_tables is not None else []
        # 活元数据第二兜底源（chat 172）：{table_name: (desc, [(name, type, comment)])}。
        # 语料根的 db-catalog.yaml 只覆盖语料所属数据源；其它 ds（如 AIO）的表
        # 走 wiki 接缝时 catalog 不命中，只渲表头零字段 → planner 必然 unsupported。
        # core_table/core_field 就在手边（同步产物），零额外连库。
        self._live_tables = live_tables or {}

    @property
    def missing(self) -> list[str]:
        """本轮 render 中缺 wiki 页、走 db 直渲兜底的表(公开投影)。"""
        return list(self._missing)

    @classmethod
    def from_store(
        cls,
        store: Any,
        live_tables: dict[str, Any] | None = None,
    ) -> WikiSchemaRenderer | None:
        """从 wiki store 构建；db catalog 从语料根旁的 db/ 目录装载。"""
        if store is None:
            return None
        db_catalog: dict[str, Any] = {}
        root = getattr(store, "_pages_root", None)
        if root is not None:
            catalog_path = Path(root).parent / "db" / "db-catalog.yaml"
            if catalog_path.exists():
                import yaml

                db_catalog = yaml.safe_load(catalog_path.read_text()) or {}
        return cls(store, db_catalog, root, [], live_tables=live_tables)

    def render(self, tables: list[str]) -> str:
        """渲染 working set 的 schema 段。"""
        sections: list[str] = []
        for table in tables:
            page = _lookup_store_page(
                self._store, table, belong="tables", page_type="table"
            )
            block = _wiki_table_block(page.body) if page else None
            if block is not None:
                sections.append(self._render_wiki_table(table, block, page.body))
            else:
                if table not in self._missing:
                    self._missing.append(table)
                sections.append(self._render_db_table(table))
        if self._missing:
            SQLBotLogUtil.warning(
                "SCHEMA_PAGE_MISSING: %s —— wiki 页缺失的表本轮用 db 直渲（update 增量将补页）",
                self._missing,
            )
        return "\n".join(sections)

    # ── wiki 页渲染（权威） ──────────────────────────────────────────────

    def _enum_label_map(self, dict_key: str) -> dict[str, str]:
        """dict 指针 → 权威枚举页的 value→label 映射（页缺失/无块返回空）。

        与 enum_maps_for 同源的宽松语义（不查 published）：schema 呈现的
        是已进 working set 的表页自带的绑定，锚点块即证据。"""
        if not dict_key or not self._store:
            return {}
        page = _lookup_store_page(
            self._store, dict_key, belong="enums", page_type="enum"
        )
        if page is None:
            return {}
        for anchor in getattr(page, "ground_blocks", ()) or ():
            if anchor.kind != "enum":
                continue
            values = anchor.data.get("values") or {}
            return {
                str(value): str((meta or {}).get("label") or value)
                for value, meta in values.items()
                if isinstance(meta, dict) or meta is None
            }
        return {}

    def _wiki_relations(self, page_text: str) -> list[str]:
        """表页「## 关联表」节 → 渲染行（关系通道：JOIN 路径进 schema）。"""
        relations: list[str] = []
        heading_at = page_text.find(_RELATION_HEADING)
        if heading_at < 0:
            return relations
        section = page_text[heading_at + len(_RELATION_HEADING) :]
        # 节边界 = 下一个二级标题或文末
        next_heading = section.find("\n## ", 1)
        if next_heading >= 0:
            section = section[:next_heading]
        for match in _RELATION_ROW_RE.finditer(section):
            right = match.group("right").strip()
            left_ref = match.group("left_ref")
            right_ref = match.group("right_ref")
            note = (match.group("note") or "").strip()
            tail = f" [{note}]" if note else ""
            relations.append(f"关联: {left_ref} → {right_ref} ({right}){tail}")
        return relations

    def _render_wiki_table(
        self, table: str, block: dict[str, Any], page_text: str = ""
    ) -> str:
        desc = str(block.get("desc") or table)
        lines = [f"## {desc} ({table})"]
        for f in block.get("fields") or []:
            if not isinstance(f, dict):
                continue
            name = str(f.get("name") or "")
            ftype = str(f.get("phys") or f.get("type") or "string")
            comment = str(f.get("desc") or "").strip()
            topk = str(f.get("topk") or "").strip()
            # 枚举语义内联（schema_field_labels 兼容）：dict 指针指向权威枚举页时,
            # 值集带 label 呈现——"SIMPLE" → "SIMPLE(简易认证)",planner/clarifier/
            # reviewer 三方在同一份值语义上工作,不再靠 LLM 猜枚举含义。
            labels = self._enum_label_map(str(f.get("dict") or "").strip())
            if labels and topk:
                topk = "|".join(
                    f"{value}({labels[value]})" if value in labels else value
                    for value in topk.split("|")
                    if value
                )
            tail = f", topk={topk}" if topk else ""
            lines.append(
                _FIELD_LINE.format(
                    field=name, type=ftype, comment=comment or name, topk=tail
                )
            )
        lines.extend(self._wiki_relations(page_text))
        return "\n".join(lines)

    # ── db 直渲（页缺失兜底——非常态路径） ────────────────────────────────

    def _db_ref_relations(self, table: str) -> list[str]:
        """db-catalog 索引推导关系（第二通道）：ref_* 命名索引/列 → 候选右表。

        右表靠命名解码（ref_<left>_<right> 双段式或 ref_<right> 单段式），
        仅当解码出的表在 db catalog 中真实存在才产出——宁缺勿错。"""
        meta = (self._db_catalog.get("tables") or {}).get(table) or {}
        known_tables = set((self._db_catalog.get("tables") or {}).keys())
        relations: list[str] = []
        seen: set[str] = set()
        for name in meta.get("columns") or {}:
            candidate = name[len("ref_") :] if str(name).startswith("ref_") else ""
            if not candidate:
                continue
            # 单段（ref_tenant_project → tenant_project）与双段（ref_a_b → a.b
            # 或 a_b）都试：右表必须在 catalog 中存在
            right = candidate
            if right in known_tables and right != table and right not in seen:
                seen.add(right)
                relations.append(
                    f"关联: {table}.{name} → {right}.id [db-index, suggested]"
                )
                continue
            for sep_at in range(candidate.find("_") + 1, len(candidate)):
                r = candidate[sep_at + 1 :]
                if r in known_tables and r != table and r not in seen:
                    seen.add(r)
                    relations.append(
                        f"关联: {table}.{name} → {r}.id [db-index, suggested]"
                    )
                    break
        return relations

    def _render_db_table(self, table: str) -> str:
        meta = (self._db_catalog.get("tables") or {}).get(table)
        if meta is None and table in self._live_tables:
            # 活元数据兜底（chat 172）：catalog 只覆盖语料根所属数据源，
            # 其它 ds 的表用 core_field 同步产物渲染全列——否则零字段
            # schema 使 planner 必然 unsupported。
            return self._render_live_table(table)
        meta = meta or {}
        columns = meta.get("columns") or {}
        desc = str(meta.get("comment") or table)
        lines = [f"## {desc} ({table}) [db]"]
        for name, cinfo in columns.items():
            lines.append(
                _FIELD_LINE.format(
                    field=name,
                    type=str(cinfo.get("type") or "string"),
                    comment=str(cinfo.get("comment") or name),
                    topk="",
                )
            )
        lines.extend(self._db_ref_relations(table))
        return "\n".join(lines)

    def _render_live_table(self, table: str) -> str:
        """活元数据渲染（core_table/core_field 同步产物，非 wiki 语料）。"""
        entry = self._live_tables.get(table) or {}
        desc = str(entry.get("comment") or table)
        lines = [f"## {desc} ({table}) [db]"]
        for name, ftype, comment in entry.get("fields") or []:
            lines.append(
                _FIELD_LINE.format(
                    field=name, type=ftype, comment=comment or name, topk=""
                )
            )
        lines.extend(self._db_ref_relations(table))
        lines.extend(self._live_fk_relations(table))
        return "\n".join(lines)

    def _live_fk_relations(self, table: str) -> list[str]:
        """活元数据命名关系（chat 172 问题 1）：`<right>_id` 列 → 右表.id。

        命名解码含 d_ 前缀约定（story_id → d_story）；右表必须真实存在于
        活元数据投影——宁缺勿错，与 _db_ref_relations 同语义。"""
        entry = self._live_tables.get(table) or {}
        known = set(self._live_tables.keys())
        relations: list[str] = []
        seen: set[str] = set()
        for name, _ftype, _comment in entry.get("fields") or []:
            name = str(name)
            if not name.endswith("_id") or name == "id":
                continue
            candidate = name[: -len("_id")]
            for right in (candidate, f"d_{candidate}"):
                if right in known and right != table and right not in seen:
                    seen.add(right)
                    relations.append(
                        f"关联: {table}.{name} → {right}.id [db-naming, suggested]"
                    )
                    break
        return relations
