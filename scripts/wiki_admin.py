#!/usr/bin/env python3
"""wiki_admin — 最小管理面 CLI（plan E2.7）。

子命令，只做管理闭环必需的事（不做服务化/UI/多租户）：

  lint                 全量 lint 报告（按 code 汇总 + 每页明细）
  reviews              列出待处置 REVIEW 项（.runs/**/_review_*.yaml + _reconcile_*.yaml）
  adjudicate           裁决一个 REVIEW 项（create-page|skip），归档处置结果
  publish              发布门禁：页面引用闭包 lint 零 error 才 draft→published
  enrich               语料确定性增强（关系节/断链补链/scope 归一/行数修正，零 LLM）
  verify               源头回证：底稿对账全量校验（关系列级/行数/scope）

⚠ baseline rebuild 整页重写会抹掉 enrich 的 ``## 关联表`` 节：rebuild 后
必须再跑一次 ``enrich``（见 apps/knowledge/wiki/baseline.py 模块头）。

Usage::

    backend/venv/bin/python scripts/wiki_admin.py lint --pages ../docs/wiki-knowledge/pplatform/wiki-pages
    backend/venv/bin/python scripts/wiki_admin.py reviews --pages ...
    backend/venv/bin/python scripts/wiki_admin.py adjudicate --id <slug> --action skip --pages ...
    backend/venv/bin/python scripts/wiki_admin.py publish --page tables/cust_company_info.md --pages ...
    backend/venv/bin/python scripts/wiki_admin.py enrich --pages ... [--dry-run] [--force]
    backend/venv/bin/python scripts/wiki_admin.py verify --pages ...
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from apps.knowledge.wiki.contract import lint_page, parse_page  # noqa: E402

_ERROR_CODES = {
    # 契约结构错误（lint_page 产出）
    "GROUND_PARSE_FAILED",
    "DUPLICATE_GROUND_BLOCK",
    "CONCEPT_UNANCHORED",
    "REF_TARGET_MISSING",
    "ENUM_GENERIC_COLUMN",  # 泛列多表承载（历史吞吐教训：.type/.status/.code）
    # 对账错误（reconcile_page 产出——单一权威码表，见 ingest.reconcile_page docstring）
    "PAGE_CONTRACT_FAILED",
    "TABLE_NOT_IN_DB",
    "FIELD_NOT_IN_DB",
    "FIELD_MALFORMED",
    "ENUM_VALUE_NOT_IN_DB",
    "EVIDENCE_FILE_MISSING",
    "EVIDENCE_LINE_OUT_OF_RANGE",
}


def _iter_pages(pages_dir: Path):
    for path in sorted(pages_dir.rglob("*.md")):
        if path.name.startswith("_") or ".runs" in path.parts:
            continue
        yield path


def cmd_lint(args: argparse.Namespace) -> int:
    pages_dir = Path(args.pages)
    known = {p.stem for p in _iter_pages(pages_dir)}
    catalog = None
    catalog_path = pages_dir.parent / "db" / "db-catalog.yaml"
    if catalog_path.exists():
        data = yaml.safe_load(catalog_path.read_text()) or {}
        # lint_page 期望 {tables: {t: {fields: {列名: {family...}}}}}——
        # db-catalog 列带 type，映射成 family 供 TYPE_FAMILY_MISMATCH 校验
        _families = {
            "char": "string",
            "varchar": "string",
            "text": "string",
            "int": "number",
            "bigint": "number",
            "smallint": "number",
            "decimal": "number",
            "numeric": "number",
            "float": "number",
            "double": "number",
            "date": "temporal",
            "datetime": "temporal",
            "timestamp": "temporal",
            "time": "temporal",
            "json": "structured",
            "jsonb": "structured",
        }

        def _family(phys: str) -> str:
            base = str(phys).split("(")[0].strip().lower()
            return _families.get(base, "")

        catalog = {
            "tables": {
                name: {
                    "fields": {
                        col: {"family": _family(str(info.get("type") or ""))}
                        for col, info in (meta.get("columns") or {}).items()
                    }
                }
                for name, meta in (data.get("tables") or {}).items()
            }
        }
    by_code: dict[str, int] = {}
    hard = 0
    details: list[str] = []
    for path in _iter_pages(pages_dir):
        try:
            page = parse_page(path.read_text(), page_key=path.stem)
        except Exception as exc:  # noqa: BLE001
            hard += 1
            details.append(f"PARSE-FAIL {path.name}: {str(exc)[:120]}")
            continue
        for finding in lint_page(page, known_keys=known, catalog=catalog):
            by_code[finding.code] = by_code.get(finding.code, 0) + 1
            if finding.code in _ERROR_CODES:
                hard += 1
                details.append(
                    f"ERROR {path.name}: {finding.code} {finding.message[:100]}"
                )
    print(f"pages={len(known)} hard_errors={hard}")
    for code, count in sorted(by_code.items(), key=lambda kv: -kv[1]):
        print(f"  {code}: {count}")
    for line in details[:20]:
        print(f"  {line}")
    return 1 if hard else 0


def _iter_reviews(pages_dir: Path):
    for path in sorted((pages_dir / ".runs").rglob("*.yaml")):
        if path.name.startswith("_review_") or path.name.startswith("_reconcile_"):
            yield path


def cmd_reviews(args: argparse.Namespace) -> int:
    pages_dir = Path(args.pages)
    items = list(_iter_reviews(pages_dir))
    if not items:
        print("无待处置 REVIEW 项。")
        return 0
    print(f"待处置 {len(items)} 项：")
    for path in items:
        data = yaml.safe_load(path.read_text()) or {}
        kind = "REVIEW" if path.name.startswith("_review_") else "对账"
        title = data.get("title") or data.get("code") or ""
        print(f"  [{kind}] {path.name} | {str(title)[:60]} | {path.parent.name}")
    return 0


def cmd_adjudicate(args: argparse.Namespace) -> int:
    pages_dir = Path(args.pages)
    matches = [p for p in _iter_reviews(pages_dir) if args.id in p.name]
    if not matches:
        print(f"未找到 REVIEW 项：{args.id}")
        return 1
    if args.action not in ("create-page", "skip"):
        print("action 必须是 create-page | skip")
        return 1
    for path in matches:
        done = path.with_name(
            path.name.replace("_review_", "_done_").replace("_reconcile_", "_done_")
        )
        data = yaml.safe_load(path.read_text()) or {}
        data["adjudicated"] = args.action
        done.write_text(yaml.safe_dump(data, allow_unicode=True))
        path.unlink()
        print(f"已裁决 {path.name} → {args.action}（归档 {done.name}）")
    return 0


def cmd_publish(args: argparse.Namespace) -> int:
    pages_dir = Path(args.pages)
    page_path = pages_dir / args.page
    if not page_path.exists():
        print(f"页面不存在：{page_path}")
        return 1
    content = page_path.read_text()
    page = parse_page(content, page_key=page_path.stem)
    known = {p.stem for p in _iter_pages(pages_dir)}
    findings = lint_page(page, known_keys=known)
    errors = [f for f in findings if f.code in _ERROR_CODES]
    if errors:
        print(f"发布门禁未过（{len(errors)} error）：")
        for f in errors:
            print(f"  {f.code}: {f.message[:100]}")
        return 1
    if page.status == "published":
        print("已是 published。")
        return 0
    updated = content.replace("status: draft", "status: published", 1)
    if updated == content:
        print("未找到 'status: draft' 行——检查 frontmatter。")
        return 1
    page_path.write_text(updated)
    print(f"已发布：{args.page}")
    return 0


# enrich/verify 实现位于 scripts/wiki_enrich.py（确定性语料治理面）
sys.path.insert(0, str(Path(__file__).resolve().parent))
from wiki_enrich import cmd_enrich, cmd_verify  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name, fn in (
        ("lint", cmd_lint),
        ("reviews", cmd_reviews),
        ("adjudicate", cmd_adjudicate),
        ("publish", cmd_publish),
        ("enrich", cmd_enrich),
        ("verify", cmd_verify),
    ):
        p = sub.add_parser(name)
        p.add_argument("--pages", required=True)
        if name == "adjudicate":
            p.add_argument("--id", required=True)
            p.add_argument("--action", required=True)
        if name == "publish":
            p.add_argument("--page", required=True)
        if name == "enrich":
            p.add_argument(
                "--dry-run", action="store_true", help="只打印将改写的页面清单，不写盘"
            )
            p.add_argument(
                "--force", action="store_true", help="已有关联节的表页也重建"
            )
            p.add_argument(
                "--substrate",
                default="",
                help="底稿目录（wiki-pages-v2 默认 sibling substrate-v2）",
            )
            p.add_argument("--db-dir", default="", help="db-catalog/profile 目录")
        p.set_defaults(fn=fn)
    args = parser.parse_args()
    raise SystemExit(args.fn(args))


if __name__ == "__main__":
    main()
