#!/usr/bin/env python3
"""Normalize wiki-pages: belong + legal page_key + identical-body dedup + link rewrite.

Usage::

    backend/venv/bin/python scripts/normalize_wiki_corpus.py \\
        --pages docs/wiki-knowledge/pplatform/wiki-pages [--dry-run]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.knowledge.wiki.contract import (  # noqa: E402
    BELONG_DIRS,
    TYPE_TO_BELONG,
    WikiPage,
    parse_page,
)
from apps.knowledge.wiki.corpus_store import iter_page_files  # noqa: E402

_WIKILINK_RE = re.compile(r"\[\[(?P<target>[^\]|]+)(?P<alias>\|[^\]]+)?\]\]")
_RELATED_RE = re.compile(r"^related:\s*\[(.*?)\]\s*$", re.M)
_KEEP_ORDER = [
    "tables",
    "dicts",
    "concepts",
    "processes",
    "calibers",
    "rules",
    "metrics",
    "patterns",
    "queries",
    "sources",
    "scenarios",
]


def _split_frontmatter(content: str) -> tuple[str, str]:
    if not content.startswith("---\n"):
        raise ValueError("missing frontmatter")
    end = content.find("\n---\n", 4)
    if end < 0:
        raise ValueError("unclosed frontmatter")
    return content[4:end], content[end + 5 :]


def _yaml_scalar(value: str) -> str:
    if re.fullmatch(r"[\w.-]+", value, flags=re.U):
        return value
    return json.dumps(value, ensure_ascii=False)


def _set_fm_field(front: str, key: str, value: str) -> str:
    line = f"{key}: {_yaml_scalar(value)}"
    pattern = re.compile(rf"^{re.escape(key)}:\s*.*$", re.M)
    if pattern.search(front):
        return pattern.sub(line, front, count=1)
    for anchor in ("page_key", "type", "title"):
        lines = front.splitlines()
        for index, existing in enumerate(lines):
            if existing.startswith(f"{anchor}:"):
                lines.insert(index + 1, line)
                return "\n".join(lines)
    return front.rstrip() + "\n" + line


def _rewrite_related(front: str, mapping: dict[str, str]) -> str:
    match = _RELATED_RE.search(front)
    if not match:
        return front
    inner = match.group(1).strip()
    if not inner:
        return front
    items = [item.strip().strip("'\"") for item in inner.split(",") if item.strip()]
    rewritten: list[str] = []
    seen: set[str] = set()
    for item in items:
        dest = mapping.get(item) or mapping.get(item.lower()) or item
        if dest in seen:
            continue
        seen.add(dest)
        rewritten.append(dest)
    return _RELATED_RE.sub(f"related: [{', '.join(rewritten)}]", front, count=1)


def _rewrite_links(body: str, mapping: dict[str, str]) -> str:
    def repl(match: re.Match[str]) -> str:
        target = match.group("target").strip()
        alias = match.group("alias") or ""
        dest = mapping.get(target) or mapping.get(target.lower())
        if dest is None:
            return match.group(0)
        return f"[[{dest}{alias}]]"

    return _WIKILINK_RE.sub(repl, body)


def _keep_rank(belong: str) -> int:
    try:
        return _KEEP_ORDER.index(belong)
    except ValueError:
        return len(_KEEP_ORDER)


def normalize_tree(pages_dir: Path, *, dry_run: bool) -> dict[str, int]:
    stats = {
        "scanned": 0,
        "rewritten": 0,
        "renamed": 0,
        "deleted": 0,
        "failed": 0,
        "links": 0,
    }
    pending: list[tuple[Path, Path, WikiPage, str, str]] = []
    for path in iter_page_files(pages_dir):
        stats["scanned"] += 1
        try:
            raw = path.read_text(encoding="utf-8")
            belong = path.parent.name if path.parent.name in BELONG_DIRS else ""
            page = parse_page(raw, page_key=path.stem, belong=belong or None)
        except Exception as exc:  # noqa: BLE001
            print(f"FAIL {path}: {exc}")
            stats["failed"] += 1
            continue
        front, body = _split_frontmatter(raw)
        new_front = _set_fm_field(front, "page_key", page.page_key)
        new_front = _set_fm_field(
            new_front, "belong", page.belong or TYPE_TO_BELONG.get(page.type, "")
        )
        new_raw = f"---\n{new_front}\n---\n{body}"
        dest = path.with_name(f"{page.page_key}.md")
        pending.append(
            (path, dest, page, new_raw, hashlib.sha256(body.encode()).hexdigest())
        )

    written: list[tuple[Path, WikiPage, str, str]] = []
    for src, dest, page, new_raw, body_sha in pending:
        target = dest
        if dest != src and dest.exists():
            print(f"SKIP rename {src.name} -> {dest.name} (exists)")
            target = src
        original = src.read_text(encoding="utf-8") if src.exists() else ""
        if target != src:
            stats["renamed"] += 1
            if not dry_run:
                target.write_text(new_raw, encoding="utf-8")
                if src.exists():
                    src.unlink()
            if new_raw != original:
                stats["rewritten"] += 1
        elif new_raw != original:
            stats["rewritten"] += 1
            if not dry_run:
                src.write_text(new_raw, encoding="utf-8")
        written.append((target, page, new_raw, body_sha))

    by_body: dict[str, list[tuple[Path, WikiPage]]] = defaultdict(list)
    for path, page, _raw, body_sha in written:
        by_body[body_sha].append((path, page))

    mapping: dict[str, str] = {}
    deleted: set[Path] = set()
    for group in by_body.values():
        if len(group) < 2:
            continue
        ordered = sorted(
            group, key=lambda item: (_keep_rank(item[1].belong), str(item[0]))
        )
        keep_path, keep_page = ordered[0]
        keep_id = keep_page.store_key
        print(f"DEDUP keep {keep_path.relative_to(pages_dir)}")
        for path, page in ordered[1:]:
            print(f"  drop {path.relative_to(pages_dir)}")
            mapping[page.page_key] = keep_id
            mapping[page.store_key] = keep_id
            deleted.add(path)
            stats["deleted"] += 1

    by_ident: dict[tuple[str, str], list[tuple[Path, WikiPage, str]]] = defaultdict(
        list
    )
    for path, page, raw, _sha in written:
        if path in deleted:
            continue
        by_ident[(page.belong, page.page_key)].append((path, page, raw))
    for ident, group in by_ident.items():
        if len(group) < 2:
            continue
        ordered = sorted(group, key=lambda item: (-len(item[2]), str(item[0])))
        _keep_path, keep_page, _raw = ordered[0]
        for path, page, _raw in ordered[1:]:
            mapping[page.store_key] = keep_page.store_key
            deleted.add(path)
            stats["deleted"] += 1
            print(f"DUP ident {ident} drop {path}")

    if not dry_run:
        for path in deleted:
            if path.exists():
                path.unlink()

    for path, page, raw, _sha in written:
        if path in deleted:
            continue
        front, body = _split_frontmatter(raw)
        new_body = _rewrite_links(body, mapping)
        new_front = _rewrite_related(front, mapping)
        new_raw = f"---\n{new_front}\n---\n{new_body}"
        if new_raw != raw:
            stats["links"] += 1
            if not dry_run:
                path.write_text(new_raw, encoding="utf-8")

    return stats


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pages", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    pages_dir = args.pages.expanduser().resolve()
    if not pages_dir.is_dir():
        print(f"not a directory: {pages_dir}", file=sys.stderr)
        return 1
    stats = normalize_tree(pages_dir, dry_run=args.dry_run)
    print(stats)
    return 0 if stats["failed"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
