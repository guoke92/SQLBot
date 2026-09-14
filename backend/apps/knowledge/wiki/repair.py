"""Repair an extracted wiki corpus without LLM.

Fixes LLM drift against the machine contract:
- stamp page_key/belong (strip ``table.`` / ``concepts/`` prefixes)
- remesh table pages with a fresh baseline ground:table (keep semantic prose)
- rebuild enum pages from extract-enums (quoted keys, stored_as / java_name)
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml

from apps.knowledge.wiki.baseline import build_enum_pages, build_table_pages
from apps.knowledge.wiki.contract import BELONG_DIRS, compact_block, stamp_frontmatter
from apps.knowledge.wiki.pipeline import merge_enum_page, merge_same_key_page


def _rewrite_fields_fence(content: str, table: str) -> str:
    """LLM ``ground:fields`` / ``columns`` 方言 → ``ground:table`` + fields.name。"""
    match = re.search(r"```ground:(fields|table)\n([\s\S]*?)\n```", content)
    if not match:
        return content
    try:
        data = yaml.safe_load(match.group(2)) or {}
    except yaml.YAMLError:
        return content
    if not isinstance(data, dict):
        return content
    data = compact_block(data)
    fields = [
        f for f in (data.get("fields") or []) if isinstance(f, dict) and f.get("name")
    ]
    if not fields:
        return content
    lines = ["```ground:table", f"table: {data.get('table') or table}", "fields:"]
    for field in fields:
        lines.append(f"  - name: {field['name']}")
        if field.get("type"):
            lines.append(f"    type: {field['type']}")
        if field.get("desc"):
            lines.append(f"    desc: {str(field['desc']).strip()}")
        if field.get("dict"):
            lines.append(f"    dict: {field['dict']}")
    lines.append("```")
    fence = "\n".join(lines)
    return re.sub(
        r"```ground:(?:fields|table)\n[\s\S]*?\n```",
        fence.replace("\\", "\\\\"),
        content,
        count=1,
    )


def _table_owner_domains(substrate_dir: Path) -> dict[str, str]:
    """表 → 计划中首次声明该表的主题（后写主题不得覆盖）。"""
    plan_path = substrate_dir / "tmp" / "page-plan.yaml"
    if not plan_path.exists():
        return {}
    plan = yaml.safe_load(plan_path.read_text()) or {}
    owners: dict[str, str] = {}
    for unit in plan.get("plan_units") or []:
        topic = str(unit.get("topic") or "").strip()
        if not topic:
            continue
        for table in unit.get("tables") or []:
            owners.setdefault(str(table), topic)
    return owners


def _patch_frontmatter(content: str, **fields: str) -> str:
    match = re.match(r"\A(---\n)([\s\S]*?)(\n---\n)", content)
    if not match:
        return content
    front = match.group(2)
    domain = fields.get("domain")
    if domain:
        if re.search(r"^domain:", front, re.M):
            front = re.sub(r"^domain:.*$", f"domain: {domain}", front, count=1, flags=re.M)
        else:
            front = f"{front.rstrip()}\ndomain: {domain}"
    database = fields.get("database")
    if database:
        if re.search(r"databases:\s*\[", front):
            front = re.sub(
                r"databases:\s*\[[^\]]*\]",
                f"databases: [{database}]",
                front,
                count=1,
            )
        elif re.search(r"databases:", front):
            front = re.sub(
                r"databases:\s*\n(?:\s*-\s*\S+\n?)+",
                f"databases:\n    - {database}\n",
                front,
                count=1,
            )
        elif re.search(r"^scope:", front, re.M):
            front = f"{front.rstrip()}\n  databases: [{database}]\n"
        else:
            front = f"{front.rstrip()}\nscope:\n  databases: [{database}]"
    return f"{match.group(1)}{front}{match.group(3)}{content[match.end() :]}"


def _dictkey_rewrites(substrate_dir: Path) -> list[tuple[str, str, str]]:
    """(表.列, Java 常量名, dictKey) — LLM 常把 .name() 写成落库谓词。"""
    path = substrate_dir / "extract-enums.yaml"
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    by_enum: dict[str, list[tuple[str, str]]] = {}
    for entry in data.get("enums") or []:
        name = str(entry.get("enum") or "")
        if not name:
            continue
        for value in entry.get("values") or []:
            java_name = str(value.get("java_name") or "")
            dict_key = str(value.get("value") or "")
            if java_name and dict_key and java_name != dict_key:
                by_enum.setdefault(name, []).append((java_name, dict_key))
    out: list[tuple[str, str, str]] = []
    for carrier, binds in (data.get("table_bindings") or {}).items():
        items = binds if isinstance(binds, list) else []
        for bind in items:
            enum_name = str((bind or {}).get("enum") or "") if isinstance(bind, dict) else ""
            for java_name, dict_key in by_enum.get(enum_name, []):
                out.append((str(carrier), java_name, dict_key))
    return out


def _rewrite_java_name_predicates(
    pages_dir: Path, rewrites: list[tuple[str, str, str]]
) -> int:
    """把口径/概念/过程里的 ``表.列 = 'Java名'`` 改成 dictKey。

    不改 ``tables/``（``cust_user_rel.user_type='admin'`` 是另一张旧表的真值）。
    """
    changed = 0
    skip_dirs = {".runs", "tables", "enums"}
    for path in sorted(pages_dir.rglob("*.md")):
        if path.name.startswith("_") or skip_dirs.intersection(path.parts):
            continue
        original = path.read_text(encoding="utf-8")
        text = original
        for carrier, java_name, dict_key in rewrites:
            text = re.sub(
                rf"({re.escape(carrier)}\s*=\s*)['\"]{re.escape(java_name)}['\"]",
                rf"\g<1>'{dict_key}'",
                text,
            )
            column = carrier.partition(".")[2]
            if column and path.parent.name in {"calibers", "concepts", "processes", "rules"}:
                text = re.sub(
                    rf"({re.escape(column)}\s*=\s*)['\"]{re.escape(java_name)}['\"]",
                    rf"\g<1>'{dict_key}'",
                    text,
                )

            def _process_fence(match: re.Match[str], *, _c=carrier, _j=java_name, _k=dict_key) -> str:
                body = match.group(0)
                field_m = re.search(r"^field:\s*(\S+)", body, re.M)
                if not field_m or field_m.group(1) != _c:
                    return body
                body = re.sub(
                    rf"^(\s+(?:- value|from|to):\s*){re.escape(_j)}\s*$",
                    rf"\g<1>{_k}",
                    body,
                    flags=re.M,
                )
                return body

            text = re.sub(r"```ground:process\n[\s\S]*?\n```", _process_fence, text)
        if text != original:
            path.write_text(text, encoding="utf-8")
            changed += 1
    return changed


def repair_corpus(
    pages_dir: Path,
    *,
    substrate_dir: Path,
    db_dir: Path,
    enums: bool = True,
) -> dict[str, int]:
    counts = {"stamped": 0, "tables": 0, "enums": 0, "domains": 0, "predicates": 0}
    catalog = yaml.safe_load((db_dir / "db-catalog.yaml").read_text()) or {}
    database = str(catalog.get("database") or "lowcode_pplatform")
    owners = _table_owner_domains(substrate_dir)
    table_pages = {
        Path(rel).stem: content
        for rel, content in build_table_pages(
            substrate_dir=substrate_dir, db_dir=db_dir
        )
    }
    for path in sorted((pages_dir / "tables").glob("*.md")):
        baseline = table_pages.get(path.stem)
        if not baseline:
            rewritten = _rewrite_fields_fence(
                path.read_text(encoding="utf-8"), path.stem
            )
            rewritten = stamp_frontmatter(rewritten, stem=path.stem, belong="tables")
            if rewritten != path.read_text(encoding="utf-8"):
                path.write_text(rewritten, encoding="utf-8")
                counts["tables"] += 1
            continue
        merged = merge_same_key_page(baseline, path.read_text(encoding="utf-8"))
        if merged != path.read_text(encoding="utf-8"):
            path.write_text(merged, encoding="utf-8")
            counts["tables"] += 1
    for stem, content in table_pages.items():
        target = pages_dir / "tables" / f"{stem}.md"
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                stamp_frontmatter(content, stem=stem, belong="tables"),
                encoding="utf-8",
            )
            counts["tables"] += 1
    for path in sorted((pages_dir / "tables").glob("*.md")):
        original = path.read_text(encoding="utf-8")
        patched = _patch_frontmatter(
            original,
            **{
                k: v
                for k, v in {
                    "domain": owners.get(path.stem, ""),
                    "database": database,
                }.items()
                if v
            },
        )
        if patched != original:
            path.write_text(patched, encoding="utf-8")
            counts["domains"] += 1
    if enums:
        enum_pages, _unbound = build_enum_pages(
            substrate_dir=substrate_dir, db_dir=db_dir
        )
        for rel, content in enum_pages:
            path = pages_dir / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            stamped = stamp_frontmatter(content, stem=path.stem, belong="enums")
            if path.exists():
                stamped = merge_enum_page(stamped, path.read_text(encoding="utf-8"))
            path.write_text(stamped, encoding="utf-8")
            counts["enums"] += 1
    rewrites = _dictkey_rewrites(substrate_dir)
    if rewrites:
        counts["predicates"] = _rewrite_java_name_predicates(pages_dir, rewrites)
    for path in sorted(pages_dir.rglob("*.md")):
        if path.name.startswith("_") or ".runs" in path.parts:
            continue
        belong = path.parent.name if path.parent.name in BELONG_DIRS else ""
        original = path.read_text(encoding="utf-8")
        stamped = stamp_frontmatter(original, stem=path.stem, belong=belong)
        if stamped != original:
            path.write_text(stamped, encoding="utf-8")
            counts["stamped"] += 1
    from apps.knowledge.wiki.baseline import rebuild_index

    rebuild_index(pages_dir)
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, help="wiki-pages 目录")
    parser.add_argument("--substrate", required=True)
    parser.add_argument("--db-dir", required=True)
    parser.add_argument("--skip-enums", action="store_true")
    args = parser.parse_args()
    counts = repair_corpus(
        Path(args.out),
        substrate_dir=Path(args.substrate),
        db_dir=Path(args.db_dir),
        enums=not args.skip_enums,
    )
    print(
        f"repaired tables={counts['tables']} enums={counts['enums']} "
        f"domains={counts.get('domains', 0)} stamped={counts['stamped']} "
        f"predicates={counts.get('predicates', 0)}"
    )


if __name__ == "__main__":
    main()
