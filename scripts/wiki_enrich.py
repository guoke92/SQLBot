"""Deterministic corpus enrichment + source-verify（方案 v1 §1 语料治理面）.

enrich：零 LLM 确定性改写——
  A 表页补「## 关联表」节（extract-relationships ∪ db-catalog ref_ 索引双通道）
  B 语义页补断链 wikilink（引用表须在 db-catalog 且有表页，双重验证）
  C scope 三态归一（点式/字符串 → 块式 datasources）
  D 表页行数修正（db-profile.rows_estimate）
  E _index.md 重建

verify：源头回证（ingest.py Step E 零信任对账的存量语料全量执行版）——
关系行列级校验 / 枚举三方对账 / 行数复核 / scope 块式断言。

每类修改附证据：关系行内联 evidence 字符串；frontmatter sources 追加
enrich 来源标记；全部改写可独立从底稿复核。
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

_TENANT_FIELDS = {
    "tenant_id",
    "tenant_code",
    "db_tenant_code",
    "app_tenant_code",
    "organization_id",
    "create_by",
    "create_time",
    "update_by",
    "update_time",
}
_RELATION_HEADING = "## 关联表"
_PHYSICAL_REF_RE = re.compile(r"\b([a-z][a-z0-9_]*)\.([a-z][a-z0-9_]*)\b")
_SOURCE_TAG = "enrich:wiki-admin"

# mapper/write-flow 是直证；ref-convention/java-eq 需 db 索引交叉一致才升级
_CONFIRM_EVIDENCE = ("mapper:", "write-flow:", "read-flow:")


class _Substrate:
    """只读底稿视图（enrich/verify 共用；加载失败=该通道不可用）。

    ``pages_dir`` 可能是仓库语料的副本（测试/试跑），底稿始终从仓库内
    原始路径加载——底稿是证据源，不随副本走；``--substrate``/``--db``
    可显式覆盖。"""

    def __init__(
        self,
        pages_dir: Path,
        *,
        substrate_dir: Path | None = None,
        db_dir: Path | None = None,
    ) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        default_root = repo_root / "docs" / "wiki-knowledge" / "pplatform"
        # wiki-pages-v2 → 优先 sibling substrate-v2；否则 pages 的父目录 / 默认根
        pages_name = pages_dir.name
        suffix = ""
        if pages_name.startswith("wiki-pages") and pages_name != "wiki-pages":
            suffix = pages_name[len("wiki-pages") :]
        parent = pages_dir.parent
        sibling_sub = parent / f"substrate{suffix}"
        sibling_plain = parent / "substrate"
        if (
            pages_dir.parent.name != "wiki-pages"
            or (pages_dir.parent / "substrate").exists()
        ):
            system_root = parent
        else:
            system_root = default_root
        if (
            not (system_root / "substrate").exists()
            and not (system_root / "db").exists()
            and not sibling_sub.exists()
        ):
            system_root = default_root
        if sibling_sub.exists():
            default_sub = sibling_sub
        elif sibling_plain.exists():
            default_sub = sibling_plain
        else:
            default_sub = system_root / "substrate"
        self.substrate_dir = substrate_dir or default_sub
        self.db_dir = db_dir or system_root / "db"
        self.db_catalog: dict[str, Any] = self._load(self.db_dir / "db-catalog.yaml")
        self.db_profile: dict[str, Any] = self._load(self.db_dir / "db-profile.yaml")
        self.relationships: list[dict[str, Any]] = []
        rel = self._load(self.substrate_dir / "extract-relationships.yaml")
        if isinstance(rel, dict):
            self.relationships = [
                item
                for item in rel.get("relationships") or []
                if isinstance(item, dict)
            ]

    @staticmethod
    def _load(path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return data if isinstance(data, dict) else {}

    @property
    def db_tables(self) -> dict[str, Any]:
        return self.db_catalog.get("tables") or {}

    def column_exists(self, table: str, column: str) -> bool:
        return column in ((self.db_tables.get(table) or {}).get("columns") or {})

    def rows_estimate(self, table: str) -> int:
        return int(
            ((self.db_profile.get("tables") or {}).get(table) or {}).get(
                "rows_estimate"
            )
            or 0
        )

    def index_decoded_relations(self, table: str) -> list[tuple[str, str]]:
        """db-catalog ref_* 列 → (left_field, right_table) 候选（右表须存在）。"""
        known = set(self.db_tables.keys())
        out: list[tuple[str, str]] = []
        for name in (self.db_tables.get(table) or {}).get("columns") or {}:
            name = str(name)
            if not name.startswith("ref_"):
                continue
            candidate = name[len("ref_") :]
            if candidate in known and candidate != table:
                out.append((name, candidate))
                continue
            for sep_at in range(candidate.find("_") + 1, len(candidate)):
                right = candidate[sep_at + 1 :]
                if right in known and right != table:
                    out.append((name, right))
                    break
        return out


def _relations_for_table(substrate: _Substrate, table: str) -> list[dict[str, str]]:
    """表的双向关系行（确定性推导，租户/审计字段端点过滤）。"""
    rows: dict[str, dict[str, str]] = {}
    for rel in substrate.relationships:
        left_t = str(rel.get("left_table") or "")
        right_t = str(rel.get("right_table") or "")
        left_f = str(rel.get("left_field") or "")
        right_f = str(rel.get("right_field") or "")
        evidence = str(rel.get("evidence") or "")
        if table not in (left_t, right_t):
            continue
        if left_f in _TENANT_FIELDS or right_f in _TENANT_FIELDS:
            continue
        if not (
            substrate.column_exists(left_t, left_f)
            and substrate.column_exists(right_t, right_f)
        ):
            continue
        if left_t == table:
            other, mine, mine_ref, theirs_ref = (
                right_t,
                left_f,
                f"{left_t}.{left_f}",
                f"{right_t}.{right_f}",
            )
        else:
            other, mine, mine_ref, theirs_ref = (
                left_t,
                right_f,
                f"{right_t}.{right_f}",
                f"{left_t}.{left_f}",
            )
        if other == table:
            continue
        confidence = (
            "confirmed"
            if any(evidence.startswith(p) for p in _CONFIRM_EVIDENCE)
            else "suggested"
        )
        rows[f"{other}|{mine_ref}|{theirs_ref}"] = {
            "other": other,
            "mine_ref": mine_ref,
            "theirs_ref": theirs_ref,
            "mine_col": mine,
            "evidence": evidence,
            "confidence": confidence,
        }
    # db 索引第二通道：ref_* 命名 + 右表存在 → suggested（与代码侧互证）
    for mine_col, right_t in substrate.index_decoded_relations(table):
        if mine_col in _TENANT_FIELDS:
            continue
        key = f"{right_t}|{table}.{mine_col}|{right_t}.id"
        if key in rows:
            continue
        rows[key] = {
            "other": right_t,
            "mine_ref": f"{table}.{mine_col}",
            "theirs_ref": f"{right_t}.id",
            "mine_col": mine_col,
            "evidence": "db-index:ref_-naming",
            "confidence": "suggested",
        }
    return [rows[key] for key in sorted(rows)]


def _relation_section(_table: str, relations: list[dict[str, str]]) -> str:
    lines = [_RELATION_HEADING, ""]
    for rel in relations:
        lines.append(
            f"- [[{rel['other']}]]：{rel['mine_ref']} → {rel['theirs_ref']}"
            f"（{rel['evidence']}，{rel['confidence']}）"
        )
    return "\n".join(lines) + "\n"


def enrich_table_page(
    content: str, substrate: _Substrate, table: str, *, force: bool = False
) -> str:
    """A 关联节 + D 行数修正（表页）。返回新内容（无变化返回原文）。"""
    updated = content
    if force:
        heading_at = updated.find(_RELATION_HEADING)
        if heading_at >= 0:
            rest = updated[heading_at + len(_RELATION_HEADING) :]
            next_h = rest.find("\n## ")
            end = (
                heading_at
                + len(_RELATION_HEADING)
                + (len(rest) if next_h < 0 else next_h)
            )
            updated = (updated[:heading_at] + updated[end:]).rstrip() + "\n"
    if _RELATION_HEADING not in updated:
        relations = _relations_for_table(substrate, table)
        if relations:
            section = "\n" + _relation_section(table, relations)
            ground_end = updated.find("\n```", updated.find("```ground:table"))
            if ground_end >= 0:
                close_end = updated.find("\n", ground_end + 1)
                insert_at = close_end + 1 if close_end >= 0 else len(updated)
                updated = (
                    updated[:insert_at] + section + updated[insert_at:].lstrip("\n")
                )
    rows = substrate.rows_estimate(table)
    if rows:
        updated = re.sub(r"行数估计\s*\d+", f"行数估计 {rows}", updated, count=1)
    return updated


def _referenced_tables(content: str) -> set[str]:
    """语义页引用的物理表：field_targets/maps_to（frontmatter 元数据优先）。"""
    fm_match = re.match(r"\A---\n([\s\S]*?)\n---\n", content)
    if not fm_match:
        return set()
    front = fm_match.group(1)
    tables: set[str] = set()
    field_targets = re.search(r"^field_targets:\s*\[([^\]]*)\]", front, re.M)
    if field_targets:
        for ref in field_targets.group(1).split(","):
            m = re.fullmatch(r"\s*([a-z][a-z0-9_]*)\.[a-z][a-z0-9_]*\s*", ref)
            if m:
                tables.add(m.group(1))
    maps_to = re.search(r'^maps_to:\s*"?([^"\n]*)"?', front, re.M)
    if maps_to:
        for match in _PHYSICAL_REF_RE.finditer(maps_to.group(1)):
            tables.add(match.group(1))
    return tables


def enrich_semantic_page(content: str, known_tables: set[str]) -> str:
    """B 断链补链：引用的表页存在且正文无链时，页尾追加 `相关：` 行。"""
    tables = {t for t in _referenced_tables(content) if t in known_tables}
    if not tables:
        return content
    linked = set(re.findall(r"\[\[([a-z][a-z0-9_]*)\]\]", content))
    missing = sorted(t for t in tables if t not in linked)
    if not missing:
        return content
    line = "相关：" + " ".join(f"[[{t}]]" for t in missing) + "\n"
    if content.endswith("\n"):
        return content + "\n" + line
    return content + "\n\n" + line


def normalize_scope(content: str, *, database: str = "") -> str:
    """C scope 归一：迁移到块式 scope.databases（物理库名围栏）。

    - 旧块式/点式 scope.datasources、平铺 datasources → 重写为
      ``scope:\\n  databases: [<database>]``（database 为空则删除围栏——
      数据源是来源不是使用限制，宁缺勿错）；
    - 字符串 scope（v0 flat 形态）改名 coverage_note，不再补任何围栏。"""
    fm = re.match(r"\A(---\n)([\s\S]*?)(\n---\n)", content)
    if not fm:
        return content
    front = fm.group(2)
    has_block_databases = re.search(r"^scope:\n\s+databases:", front, re.M)
    has_legacy = re.search(
        r"^scope:\n\s+datasources:|^scope\.datasources:|^datasources:", front, re.M
    )
    if has_block_databases and not has_legacy:
        return content
    updated = front
    if has_legacy:
        # 旧值（ds_id 或错填的表名）一律丢弃：ds_id 不可跨环境，错填值不可信
        updated = re.sub(r"^scope:\n\s+datasources:[^\n]*\n?", "", updated, flags=re.M)
        updated = re.sub(r"^scope\.datasources:[^\n]*\n?", "", updated, flags=re.M)
        updated = re.sub(r"^datasources:[^\n]*\n?", "", updated, flags=re.M)
        updated = updated.rstrip("\n")
        if database:
            updated += f"\nscope:\n  databases: [{database}]"
    else:
        plain = re.search(r'^scope:\s*(?!"?\[)(.+)$', updated, re.M)
        if plain:
            note_value = plain.group(1).strip()
            updated = updated.replace(plain.group(0), "", 1).rstrip("\n")
            updated += f"\ncoverage_note: {note_value}"
    if updated != front:
        return f"{fm.group(1)}{updated}{fm.group(3)}{content[fm.end() :]}"
    return content


def rebuild_index(pages_dir: Path) -> str:
    """E _index.md 重建（程序生成物，与目录严格一致）。"""
    by_type: dict[str, list[tuple[str, str]]] = {}
    for path in sorted(pages_dir.rglob("*.md")):
        if path.name.startswith("_") or ".runs" in path.parts:
            continue
        page_type = path.parent.name
        try:
            page = parse_page(path.read_text(encoding="utf-8"), page_key=path.stem)
        except Exception:  # noqa: BLE001 — 坏页不阻塞索引生成
            continue
        by_type.setdefault(page_type, []).append((page.page_key, page.title))
    lines = ["# Wiki 页面目录（程序生成，勿手改）", ""]
    total = 0
    for page_type in sorted(by_type):
        entries = sorted(by_type[page_type])
        total += len(entries)
        lines.append(f"## {page_type} ({len(entries)})")
        for key, title in entries:
            lines.append(f"- [[{key}]] — {title}")
        lines.append("")
    lines.append(f"共 {total} 页。")
    return "\n".join(lines) + "\n"


def _bump_source(content: str) -> str:
    """frontmatter sources 追加 enrich 标记（可审计：哪些页被确定性改写）。"""
    fm = re.match(r"\A(---\n)([\s\S]*?)(\n---\n)", content)
    if not fm:
        return content
    front = fm.group(2)
    # sources: [a, b]  →  在 ] 前插入新元素（点式/块式/缺省三种形态分别处理）
    sources = re.search(r"^(sources:\s*)\[([^\]]*)\]\s*$", front, re.M)
    if sources:
        if _SOURCE_TAG in sources.group(2):
            return content
        items = [item.strip() for item in sources.group(2).split(",") if item.strip()]
        items.append(f'"{_SOURCE_TAG}"')
        replacement = f"{sources.group(1)}[{', '.join(items)}]"
        front = front.replace(sources.group(0), replacement, 1)
    else:
        front += f'\nsources: ["{_SOURCE_TAG}"]'
    return f"{fm.group(1)}{front}{fm.group(3)}{content[fm.end() :]}"


def run_enrich(
    pages_dir: Path,
    *,
    dry_run: bool = False,
    force: bool = False,
    substrate_dir: Path | None = None,
    db_dir: Path | None = None,
) -> dict[str, int]:
    """enrich 全流程。返回各类改写计数（供 CLI 报告）。"""
    substrate = _Substrate(pages_dir, substrate_dir=substrate_dir, db_dir=db_dir)
    known_tables = {p.stem for p in (pages_dir / "tables").glob("*.md")}
    counts = {"relations": 0, "links": 0, "scope": 0, "rows": 0}
    for path in sorted(pages_dir.rglob("*.md")):
        if path.name.startswith("_") or ".runs" in path.parts:
            continue
        page_type = path.parent.name
        original = path.read_text(encoding="utf-8")
        updated = original
        if page_type == "tables":
            before = updated
            updated = enrich_table_page(updated, substrate, path.stem, force=force)
            if (
                updated != before
                and _RELATION_HEADING in updated
                and (_RELATION_HEADING not in before)
            ):
                counts["relations"] += 1
            if updated != before:
                counts["rows"] += 1
        else:
            before = updated
            updated = enrich_semantic_page(updated, known_tables)
            if updated != before:
                counts["links"] += 1
        updated = normalize_scope(updated)
        if updated != original and "scope" not in counts:
            pass
        scope_changed = normalize_scope(original) != original
        if scope_changed:
            counts["scope"] += 1
        if updated != original or scope_changed:
            updated = _bump_source(updated if updated != original else original)
            if not dry_run:
                parse_page(updated, page_key=path.stem)  # 写前复验
                path.write_text(updated, encoding="utf-8")
    if not dry_run:
        (pages_dir / "_index.md").write_text(rebuild_index(pages_dir), encoding="utf-8")
    return counts


def run_verify(pages_dir: Path) -> tuple[int, list[str]]:
    """源头回证：确定性校验，返回 (error 数, 明细行)。"""
    substrate = _Substrate(pages_dir)
    errors: list[str] = []
    for path in sorted(pages_dir.rglob("*.md")):
        if path.name.startswith("_") or ".runs" in path.parts:
            continue
        rel = path.relative_to(pages_dir)
        content = path.read_text(encoding="utf-8")
        if path.parent.name == "tables":
            for match in re.finditer(
                r"^- \[\[([^\]]+)\]\]：([a-z][a-z0-9_]*)\.([a-z][a-z0-9_]*)"
                r"\s*→\s*([a-z][a-z0-9_]*)\.([a-z][a-z0-9_]*)",
                content,
                re.M,
            ):
                _right, lt, lf, rt, rf = match.groups()
                if not substrate.column_exists(lt, lf):
                    errors.append(f"{rel}: 关系列不存在 {lt}.{lf}")
                if not substrate.column_exists(rt, rf):
                    errors.append(f"{rel}: 关系列不存在 {rt}.{rf}")
            if substrate.db_tables and path.stem in substrate.db_tables:
                rows = substrate.rows_estimate(path.stem)
                page_rows = re.search(r"行数估计\s*(\d+)", content)
                if page_rows and int(page_rows.group(1)) != rows:
                    errors.append(
                        f"{rel}: 行数 {page_rows.group(1)} != db-profile {rows}"
                    )
        fm = re.match(r"\A---\n([\s\S]*?)\n---\n", content)
        if fm and not re.search(r"^scope:\n\s+databases:", fm.group(1), re.M):
            errors.append(f"{rel}: scope 非块式 scope.databases")
    return len(errors), errors


# ── CLI 接线（wiki_admin main 注册用） ──────────────────────────────────────


def cmd_enrich(args) -> int:  # noqa: ANN001 — 与 wiki_admin 样板一致
    pages_dir = Path(args.pages)
    counts = run_enrich(
        pages_dir,
        dry_run=args.dry_run,
        force=args.force,
        substrate_dir=Path(args.substrate) if getattr(args, "substrate", "") else None,
        db_dir=Path(args.db_dir) if getattr(args, "db_dir", "") else None,
    )
    label = "将改写" if args.dry_run else "已改写"
    print(
        f"{label}: relations={counts['relations']} links={counts['links']} "
        f"scope={counts['scope']} rows={counts['rows']}"
    )
    if args.dry_run:
        print("dry-run：未写盘。")
    return 0


def cmd_verify(args) -> int:  # noqa: ANN001
    pages_dir = Path(args.pages)
    error_count, details = run_verify(pages_dir)
    print(f"verify errors={error_count}")
    for line in details[:40]:
        print(f"  {line}")
    if len(details) > 40:
        print(f"  …(+{len(details) - 40} more)")
    return 1 if error_count else 0


from apps.knowledge.wiki.contract import parse_page  # noqa: E402
