#!/usr/bin/env python3
"""Step B: entry-point call-graph substrate (E1 — structural skeleton).

Upgrades the old dormant-table reachability check into a full call-graph
substrate for domain penetration (Step D): for every entry class we record
its transitively reachable files, so the LLM reads whole call chains instead
of keyword fragments. Tables are merged through DO -> Mapper -> @TableName.

Outputs (tmp substrate, never wiki corpus):
  callgraph.yaml
    entry_points:            sorted entry class list
    domains:                 per-domain {entries, reachable_files, tables}
    classes:                 class -> {file, refs:[direct class refs]}
    tables:                  table -> {do, mapper, reachable, entry_points}
    dormant_candidates:      tables with no entry reachability

Domain clustering: entries are grouped by their java package root segment
(business package under the controller/service tree), matching how the
routing docs name domains; the LLM refines boundaries in Step A/D.

Usage::

    backend/venv/bin/python .cursor/skills/knowledge-extraction/scripts/extract-callgraph.py \
        <repo> [-o callgraph.yaml] [--exclude-glob ...] [--domain-of ClassA,ClassB=domain]
"""

from __future__ import annotations

import argparse
import fnmatch
import re
from collections import deque
from pathlib import Path

import yaml

_ENTRY_ANNOTATIONS = (
    "@RestController",
    "@Controller",
    "@RequestMapping",
    "@DubboService",
    "@MessageMapping",
    "@XxlJob",
    "@KafkaListener",
    "@RabbitListener",
)
_ENTRY_SUFFIXES = (
    "Facade",
    "Controller",
    "Application",
    "Listener",
    "Consumer",
    "Provider",
    "Job",
)
_TOKEN = re.compile(r"\b[A-Z][A-Za-z0-9_]*\b")
# Types that propagate the BFS (the service chain). Non-structural types
# (DTO/VO/Enum/Constant/Util) are recorded as reachable leaves but do not
# expand — otherwise every entry "reaches" the whole shared apaas/common
# layer through DTO imports and the penetration context drowns.
_STRUCTURAL = re.compile(
    r"(Service|Impl|Manager|Dao|Mapper|DO|Application|Controller|Provider|"
    r"Facade|Job|Listener|Consumer|Processor|Handler|Repository|Helper)$"
)
# Default logic-irrelevant globs (Step A may extend; keep scanners fast/clean).
_DEFAULT_EXCLUDES = (
    "*/target/*",
    "*/build/*",
    "*/test/*",
    "*/tests/*",
    "*/gen/*",
    "*/generated/*",
    "*/resources/static/*",
    "*/resources/templates/*",
    "*/node_modules/*",
    "*/.dev-standards/*",
    "*/doc/*",
    "*/docs/*",
)


def strip_schema(tbl: str) -> str:
    m = re.match(r"^[a-z_]+\.([a-z_]+)$", tbl)
    return m.group(1) if m else tbl


def primary_type_name(text: str) -> str | None:
    m = re.search(
        r"\b(?:public\s+)?(?:abstract\s+|final\s+)?(?:class|interface|enum)\s+([A-Z]\w*)",
        text,
    )
    return m.group(1) if m else None


def package_of(path: Path, repo: Path) -> str:
    parts = path.relative_to(repo).parts
    src = next((i for i, p in enumerate(parts) if p == "java"), None)
    if src is None:
        return parts[0]
    segs = parts[src + 1 :]
    # skip leading com/lls/lowcode-style prefixes: keep last 3 segments
    return "/".join(segs[-3:]) if len(segs) > 3 else "/".join(segs)


def domain_key(pkg: str) -> str:
    """Business domain from package tail: .../cust/controller/X → 'cust'."""
    leaf = pkg.split("/")[-2] if "/" in pkg else pkg
    return leaf or pkg


def scan(repo: Path, excludes: tuple[str, ...]) -> tuple[dict[str, str], dict[str, Path]]:
    """DO class -> table; every primary type -> defining file (excludes applied)."""

    def excluded(p: Path) -> bool:
        rel = p.as_posix()
        return any(fnmatch.fnmatch(rel, pat) for pat in excludes)

    do_index: dict[str, str] = {}
    class_index: dict[str, Path] = {}
    for path in repo.rglob("*.java"):
        if excluded(path):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        name = primary_type_name(text)
        if name:
            class_index.setdefault(name, path)
        if "@TableName" in text:
            cls = re.search(r"class\s+(\w+)", text)
            tbl = re.search(r'@TableName\(\s*"([^"]+)"\s*\)', text)
            if cls and tbl:
                do_index[cls.group(1)] = strip_schema(tbl.group(1))
    return do_index, class_index


def entry_classes(
    classes: dict[str, Path], excludes: tuple[str, ...]
) -> set[str]:
    entries: set[str] = set()
    for name, path in classes.items():
        if any(fnmatch.fnmatch(path.as_posix(), pat) for pat in excludes):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if any(ann in text for ann in _ENTRY_ANNOTATIONS):
            entries.add(name)
        elif name.endswith(_ENTRY_SUFFIXES):
            entries.add(name)
    return entries


def mapper_for(do_name: str, classes: dict[str, Path], names: set[str]) -> str | None:
    base = do_name[:-2] if do_name.endswith("DO") else do_name
    candidate = f"{base}Mapper"
    if candidate in names:
        return candidate
    for name, path in classes.items():
        if name == candidate or not name.endswith("Mapper"):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if do_name in text and "interface" in text:
            return name
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo")
    parser.add_argument("-o", "--output", default="callgraph.yaml")
    parser.add_argument(
        "--exclude-glob",
        action="append",
        default=[],
        help="extra repo-rooted globs to exclude (Step A whitelist extension)",
    )
    args = parser.parse_args()

    repo = Path(args.repo)
    excludes = _DEFAULT_EXCLUDES + tuple(args.exclude_glob)
    dos, classes = scan(repo, excludes)
    names = set(classes)
    entries = entry_classes(classes, excludes)

    # class -> direct compile-time class refs
    file_refs: dict[str, set[str]] = {}
    for name, path in classes.items():
        text = path.read_text(encoding="utf-8", errors="ignore")
        file_refs[name] = set(_TOKEN.findall(text)) & names

    # Full BFS per entry: reachable file set (the Step D penetration context).
    # Depth is kept: ring-0/1/2 = the core chain (controller → application →
    # service impl → dao), outer rings = supporting types. Step D reads the
    # core chain whole-file first, outer rings on demand.
    def reachable_from(entry: str) -> dict[str, int]:
        seen = {entry: 0}
        queue = deque([(entry, 0)])
        while queue:
            current, depth = queue.popleft()
            for target in file_refs.get(current, ()):  # noqa: B023
                if target in seen:
                    continue
                seen[target] = depth + 1
                # Only structural types expand the chain; DTOs/enums/constants
                # stay as leaves so their files still enter the context window
                # but do not pull in the entire shared class universe.
                target_path = classes.get(target)
                if target_path and _STRUCTURAL.search(target):
                    queue.append((target, depth + 1))
        return seen

    per_entry_reach = {e: reachable_from(e) for e in sorted(entries)}

    # Domain clustering: entry -> business package segment (two segments past
    # the module root when present: customer-management/{cust,product,role,…}),
    # falling back to the layer package. The business segment, not the layer
    # (controller/facade/impl), is what the routing docs name domains by.
    def domain_of_class(path: Path) -> str:
        parts = path.relative_to(repo).parts
        src = next((i for i, p in enumerate(parts) if p == "java"), None)
        segs = list(parts[src + 1 :]) if src is not None else list(parts)
        # drop the leading java-root package (com/lls/lowcode/...)
        for known in ("com", "lls", "lowcode", "pplatform"):
            while segs and segs[0] in (known,):
                segs.pop(0)
        # first segment = module shortname (customer-management/...); second = business
        if len(segs) >= 2:
            return segs[1]
        return segs[0] if segs else "misc"

    # Domain clustering: entry -> package tail (business package).
    domains: dict[str, dict] = {}
    for entry in sorted(entries):
        pkg = package_of(classes[entry], repo)
        key = domain_of_class(classes[entry])
        dom = domains.setdefault(key, {"entries": [], "reachable_files": {}, "tables": set()})
        dom["entries"].append(entry)
        for cls_name, depth in per_entry_reach[entry].items():
            if cls_name not in classes:
                continue
            rel = str(classes[cls_name].relative_to(repo))
            prev = dom["reachable_files"].get(rel)
            if prev is None or depth < prev:
                dom["reachable_files"][rel] = depth

    # Table merge through DO + Mapper reachability.
    tables: dict[str, dict] = {}
    dormant: list[str] = []
    for do_name, table in sorted(dos.items()):
        mapper = mapper_for(do_name, classes, names)
        entry_hits = sorted(
            e for e, reach in per_entry_reach.items() if do_name in reach or (mapper and mapper in reach)
        )
        reachable = bool(entry_hits)
        tables[table] = {
            "do": do_name,
            "mapper": mapper,
            "reachable": reachable,
            "entry_points": entry_hits,
        }
        if not reachable:
            dormant.append(table)
        for entry, reach in per_entry_reach.items():
            if do_name in reach or (mapper and mapper in reach):
                dom_key = domain_of_class(classes[entry])
                if dom_key in domains:
                    domains[dom_key]["tables"].add(table)

    result = {
        "schema_version": "2.0",
        "repository": repo.name,
        "note": "E1 call-graph substrate (tmp 中间产物) — per-entry layered reach feeds Step D penetration",
        "excludes": list(excludes),
        "entry_points": sorted(entries),
        "domains": {
            key: {
                "entries": d["entries"],
                "tables": sorted(d["tables"]),
                "reachable_files": dict(sorted(d["reachable_files"].items(), key=lambda kv: kv[1])),
            }
            for key, d in sorted(domains.items())
        },
        "per_entry": {
            entry: {
                str(classes[c].relative_to(repo)): depth
                for c, depth in sorted(per_entry_reach[entry].items(), key=lambda kv: kv[1])
                if c in classes
            }
            for entry in sorted(entries)
        },
        "classes": {
            name: {"file": str(path.relative_to(repo)), "refs": sorted(file_refs[name])}
            for name, path in sorted(classes.items())
        },
        "tables": tables,
        "dormant_candidates": dormant,
    }
    Path(args.output).write_text(
        yaml.safe_dump(result, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    n_files = sum(len(d["reachable_files"]) for d in domains.values())
    print(
        f"entries={len(entries)} domains={len(domains)} tables={len(tables)} "
        f"dormant={len(dormant)} reachable_files_total={n_files} -> {args.output}"
    )
    for key, d in sorted(domains.items()):
        print(f"  {key}: entries={len(d['entries'])} files={len(d['reachable_files'])} tables={len(d['tables'])}")


if __name__ == "__main__":
    main()
