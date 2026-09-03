#!/usr/bin/env python
"""一次性语料迁移：wiki 页面围栏 scope.datasources（ds_id）→ scope.databases（物理库名）。

背景：ds_id 是环境内自增主键，跨环境（本地→远程）不通用；物理库名才是
稳定的围栏身份（数据源是知识来源、不是使用限制）。本脚本：

1. 从 db-catalog.yaml 顶层 ``database:`` 读物理库名（可用 --database 覆盖）；
2. 删除 frontmatter 里的旧形态：块式 ``scope:\\n  datasources: [...]``、
   点式 ``scope.datasources: [...]``、平铺 ``datasources: [...]``（冗余形态）；
3. 写入 ``scope:\\n  databases: [<库名>]``（幂等：已是新形态的页原样跳过）；
4. 每页写前用 parse_page 复验（坏页不写、报错退出）。

用法（repo 根）：
    python scripts/migrate_wiki_scope.py                     # 默认 pplatform 语料
    python scripts/migrate_wiki_scope.py --dry-run           # 只报告不写
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

_REPO = Path(__file__).resolve().parent.parent
_DEFAULT_PAGES = _REPO / "docs/wiki-knowledge/pplatform/wiki-pages"
_DEFAULT_CATALOG = _REPO / "docs/wiki-knowledge/pplatform/db/db-catalog.yaml"

_FM_RE = re.compile(r"\A(---\n)([\s\S]*?)(\n---\n)")
_LEGACY_LINE_RES = (
    re.compile(r"^scope:\n[ \t]+datasources:[^\n]*\n?", re.M),
    re.compile(r"^scope\.datasources:[^\n]*\n?", re.M),
    re.compile(r"^datasources:[^\n]*\n?", re.M),
)


def catalog_database(catalog_path: Path) -> str:
    data = yaml.safe_load(catalog_path.read_text(encoding="utf-8")) or {}
    return str(data.get("database") or "").strip()


def migrate(content: str, database: str) -> tuple[str, str]:
    """返回 (新内容, 动作)。动作 ∈ {none, rewrote, dropped-scope}。"""
    fm = _FM_RE.match(content)
    if not fm:
        return content, "none"
    front = fm.group(2)
    if re.search(r"^scope:\n[ \t]+databases:", front, re.M):
        has_legacy = any(rx.search(front) for rx in _LEGACY_LINE_RES)
        if not has_legacy:
            return content, "none"
    updated = front
    for rx in _LEGACY_LINE_RES:
        updated = rx.sub("", updated)
    updated = updated.rstrip("\n")
    if database:
        updated += f"\nscope:\n  databases: [{database}]"
    if updated == front:
        return content, "none"
    return f"{fm.group(1)}{updated}{fm.group(3)}{content[fm.end() :]}", "rewrote"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pages", type=Path, default=_DEFAULT_PAGES)
    parser.add_argument("--catalog", type=Path, default=_DEFAULT_CATALOG)
    parser.add_argument("--database", default="", help="覆盖库名（默认读 catalog）")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    database = args.database or catalog_database(args.catalog)
    if not database:
        print(
            "未确定库名：catalog 缺顶层 database 键且未传 --database", file=sys.stderr
        )
        return 1

    rewritten = kept = failed = 0
    for path in sorted(args.pages.rglob("*.md")):
        if path.name.startswith("_") or ".runs" in path.parts:
            continue
        original = path.read_text(encoding="utf-8")
        updated, action = migrate(original, database)
        if action == "none":
            kept += 1
            continue
        try:
            sys.path.insert(0, str(_REPO / "backend"))
            from apps.knowledge.wiki.contract import parse_page

            page = parse_page(updated, page_key=path.stem)
        except Exception as exc:  # noqa: BLE001 — 坏页不写，人工处理
            print(f"FAIL {path.relative_to(args.pages)}: {exc}", file=sys.stderr)
            failed += 1
            continue
        rewritten += 1
        if not args.dry_run:
            path.write_text(updated, encoding="utf-8")
        legacy_left = "datasources" in updated
        print(
            f"{'[dry] ' if args.dry_run else ''}{path.relative_to(args.pages)} "
            f"→ {page.databases or '(无围栏)'}"
            + ("  ⚠ 仍有 datasources 残留" if legacy_left else "")
        )

    print(
        f"\n共 {rewritten + kept + failed} 页：改写 {rewritten}，"
        f"无需变化 {kept}，失败 {failed}（库名={database}）"
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
