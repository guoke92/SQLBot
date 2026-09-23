"""Sync wiki table pages after EQUI_JOIN edits.

Rebuilds:

1. Frontmatter ``related`` — join-neighbor tables + **preserved soft table peers**
   (tables already listed in ``related`` but not EQUI_JOIN neighbors, e.g. 产融/讯易链
   对等主档、配置灌入非 JOIN) + non-table slugs (dicts / concepts / processes)
2. ``## 页面链接`` / ``### 关联表`` — join neighbors then soft peers
3. Optional mirror of each EQUI_JOIN fence onto the *other* endpoint table page
   (host often only had the child side)

Does not delete fences; only adds missing mirrors and refreshes related/links.
Soft table ``related`` entries are preserved across sync so peer/non-join notes survive.
"""

from __future__ import annotations

import datetime as dt
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

_RELATION_FENCE = re.compile(r"```ground:relation\n([\s\S]*?)\n```")
_FM = re.compile(r"^---\n([\s\S]*?)\n---\n", re.M)
_PAGE_LINKS = re.compile(
    r"\n## 页面链接\n[\s\S]*?(?=\n## [^页]|\Z)",
)
_TODAY = dt.date.today().isoformat()


def run_sync(
    *,
    wiki_dir: Path,
    mirror_fences: bool = True,
    concept_links: bool = True,
) -> dict[str, Any]:
    wiki_dir = Path(wiki_dir)
    tables_dir = wiki_dir / "tables"
    concepts_dir = wiki_dir / "concepts"
    known_tables = {p.stem for p in tables_dir.glob("*.md")}
    known_concepts = {p.stem for p in concepts_dir.glob("*.md")} if concepts_dir.is_dir() else set()

    edges = _load_edges(tables_dir)
    graph: dict[str, set[str]] = defaultdict(set)
    for e in edges:
        lt = e["left"].split(".", 1)[0]
        rt = e["right"].split(".", 1)[0]
        if lt in known_tables and rt in known_tables and lt != rt:
            graph[lt].add(rt)
            graph[rt].add(lt)

    concept_by_table = _concepts_touching_tables(wiki_dir, known_concepts, known_tables)

    mirrored = 0
    if mirror_fences:
        mirrored = _mirror_missing_fences(tables_dir, edges, known_tables)

    # reload edges after mirror
    edges = _load_edges(tables_dir)
    graph = defaultdict(set)
    for e in edges:
        lt = e["left"].split(".", 1)[0]
        rt = e["right"].split(".", 1)[0]
        if lt in known_tables and rt in known_tables and lt != rt:
            graph[lt].add(rt)
            graph[rt].add(lt)

    updated_related = 0
    updated_links = 0
    for path in sorted(tables_dir.glob("*.md")):
        stem = path.stem
        text = path.read_text(encoding="utf-8")
        fm_m = _FM.match(text)
        if not fm_m:
            continue
        front = yaml.safe_load(fm_m.group(1)) or {}
        if not isinstance(front, dict):
            continue

        neighbors = sorted(graph.get(stem) or [])
        old_related = list(front.get("related") or [])
        # Soft peers: tables intentionally related without EQUI_JOIN (preserve).
        soft_peers = sorted(
            x
            for x in old_related
            if x in known_tables and x != stem and x not in neighbors
        )
        # Keep non-table related entries (dicts / processes etc.)
        kept_other = [x for x in old_related if x not in known_tables]
        new_related = list(dict.fromkeys([*neighbors, *soft_peers, *kept_other]))
        changed_fm = new_related != old_related
        if changed_fm:
            front["related"] = new_related
            front["updated"] = _TODAY
            updated_related += 1

        concepts = sorted(concept_by_table.get(stem) or []) if concept_links else []
        link_section = _build_link_section(
            text, stem, neighbors, concepts, soft_peers=soft_peers
        )
        body = text[fm_m.end() :]
        if _PAGE_LINKS.search("\n" + body) or body.strip().endswith("## 页面链接"):
            new_body = _replace_page_links(body, link_section)
        else:
            new_body = body.rstrip() + "\n\n" + link_section
        changed_body = new_body != body
        if changed_body:
            updated_links += 1

        if changed_fm or changed_body:
            dumped = yaml.safe_dump(
                front, allow_unicode=True, sort_keys=False, width=1000
            ).rstrip()
            # Prefer flow-style lists for related like existing pages — keep block ok
            path.write_text(f"---\n{dumped}\n---\n{new_body.lstrip()}", encoding="utf-8")

    stats = {
        "tables": len(known_tables),
        "edges": len(edges),
        "mirrored_fences": mirrored,
        "updated_related": updated_related,
        "updated_page_links": updated_links,
    }
    out = wiki_dir / "_raw" / "join_collide" / "wiki_related_sync.yaml"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        yaml.safe_dump(
            {"generated_at": _TODAY, "source": "sync_wiki_related", "stats": stats},
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return stats


def _load_edges(tables_dir: Path) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    out: list[dict[str, Any]] = []
    for path in sorted(tables_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for m in _RELATION_FENCE.finditer(text):
            try:
                data = yaml.safe_load(m.group(1)) or {}
            except yaml.YAMLError:
                continue
            if str(data.get("type") or "") != "EQUI_JOIN":
                continue
            left = str(data.get("left") or "").strip()
            right = str(data.get("right") or "").strip()
            if not left or not right or "." not in left or "." not in right:
                continue
            key = (left, right)
            if key in seen:
                continue
            seen.add(key)
            packed = dict(data)
            packed["_host"] = path.stem
            packed["_raw"] = m.group(0)
            out.append(packed)
    return out


def _mirror_missing_fences(
    tables_dir: Path,
    edges: list[dict[str, Any]],
    known_tables: set[str],
) -> int:
    """Ensure each oriented edge appears on both endpoint table pages."""
    present: set[tuple[str, str, str]] = set()  # left,right,host
    for path in tables_dir.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        for m in _RELATION_FENCE.finditer(text):
            try:
                data = yaml.safe_load(m.group(1)) or {}
            except yaml.YAMLError:
                continue
            left = str(data.get("left") or "")
            right = str(data.get("right") or "")
            if left and right:
                present.add((left, right, path.stem))

    added = 0
    for edge in edges:
        left = str(edge.get("left") or "")
        right = str(edge.get("right") or "")
        lt, rt = left.split(".", 1)[0], right.split(".", 1)[0]
        for host in (lt, rt):
            if host not in known_tables:
                continue
            if (left, right, host) in present:
                continue
            path = tables_dir / f"{host}.md"
            block = {k: v for k, v in edge.items() if not str(k).startswith("_")}
            if _append_fence(path, block):
                present.add((left, right, host))
                added += 1
    return added


def _append_fence(path: Path, block: dict[str, Any]) -> bool:
    text = path.read_text(encoding="utf-8")
    left = str(block.get("left") or "")
    right = str(block.get("right") or "")
    for m in _RELATION_FENCE.finditer(text):
        try:
            data = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            continue
        if str(data.get("left")) == left and str(data.get("right")) == right:
            return False
    fence = (
        "```ground:relation\n"
        + yaml.safe_dump(block, allow_unicode=True, sort_keys=False).rstrip()
        + "\n```\n"
    )
    marker = "\n## 页面链接"
    if marker in text:
        pos = text.find(marker)
        updated = text[:pos].rstrip() + "\n\n" + fence + text[pos:]
    else:
        heading = "\n## 关联关系\n\n"
        if "## 关联关系" in text:
            updated = text.rstrip() + "\n" + fence
        else:
            updated = text.rstrip() + heading + fence
    path.write_text(updated, encoding="utf-8")
    return True


def _concepts_touching_tables(
    wiki_dir: Path, known_concepts: set[str], known_tables: set[str]
) -> dict[str, set[str]]:
    """Map table → concept page_keys whose field_targets mention the table."""
    out: defaultdict[str, set[str]] = defaultdict(set)
    # From field_semantics.yaml
    sem = wiki_dir / "_raw" / "l1_intermediate" / "docs" / "field_semantics.yaml"
    if sem.exists():
        data = yaml.safe_load(sem.read_text(encoding="utf-8")) or {}
        for row in data.get("same_semantic") or []:
            if not isinstance(row, dict):
                continue
            key = str(row.get("concept_key") or "").strip()
            if key not in known_concepts:
                continue
            for fq in row.get("field_targets") or []:
                table = str(fq).split(".", 1)[0]
                if table in known_tables:
                    out[table].add(key)
        # always link homonym index for channel_code tables
        bundle = "channel_code_homonym_bundle"
        if bundle in known_concepts:
            for row in data.get("homonyms") or []:
                if str(row.get("column_name")) != "channel_code":
                    continue
                for sense in row.get("senses") or []:
                    ck = str(sense.get("concept_key") or "")
                    # find tables from matching same_semantic
                    for s in data.get("same_semantic") or []:
                        if s.get("concept_key") == ck:
                            for fq in s.get("field_targets") or []:
                                t = str(fq).split(".", 1)[0]
                                if t in known_tables:
                                    out[t].add(bundle)
    # From concept frontmatter field_targets
    for path in (wiki_dir / "concepts").glob("*.md"):
        text = path.read_text(encoding="utf-8")
        fm_m = _FM.match(text)
        if not fm_m:
            continue
        front = yaml.safe_load(fm_m.group(1)) or {}
        key = str(front.get("page_key") or path.stem)
        for fq in front.get("field_targets") or []:
            table = str(fq).split(".", 1)[0]
            if table in known_tables:
                out[table].add(key)
        maps = str(front.get("maps_to") or "")
        if "." in maps:
            table = maps.split(".", 1)[0]
            if table in known_tables:
                out[table].add(key)
    return out


def _extract_dict_section(body: str) -> str:
    m = re.search(r"(### 字典\n[\s\S]*?)(?=\n### |\Z)", body)
    return m.group(1).rstrip() if m else ""


def _build_link_section(
    full_text: str,
    stem: str,
    neighbors: list[str],
    concepts: list[str],
    soft_peers: list[str] | None = None,
) -> str:
    dict_sec = _extract_dict_section(full_text)
    lines = ["## 页面链接", ""]
    # Join neighbors first, then soft peers (对等/非 JOIN), de-duped.
    table_links = list(dict.fromkeys([*neighbors, *(soft_peers or [])]))
    if table_links:
        lines.append("### 关联表")
        lines.append("")
        for other in table_links:
            lines.append(f"- [[tables/{other}]]")
        lines.append("")
    if concepts:
        lines.append("### 概念")
        lines.append("")
        for c in concepts:
            lines.append(f"- [[concepts/{c}]]")
        lines.append("")
    if dict_sec:
        lines.append(dict_sec)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _replace_page_links(body: str, new_section: str) -> str:
    idx = body.find("\n## 页面链接\n")
    if idx < 0:
        if body.startswith("## 页面链接\n"):
            return new_section
        return body.rstrip() + "\n\n" + new_section
    return body[: idx + 1] + new_section
