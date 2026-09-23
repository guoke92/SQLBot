"""Surgical scrub of published L1 wiki trees.

Applies current dict_triage + comment_fk rules onto existing table pages without
re-emitting L0 (preserves L1 grain / code_path fences / prose).

1. Drop polluted ``dict:`` / ``label:`` from ground:table fields
2. Detach frontmatter related + 页面链接 dict entries for those keys
3. Delete orphaned ``dicts/*.md`` pages
4. Nominate missing comment_fk EQUI_JOIN fences (``table#column`` in desc)
5. Optional AI binary Y/N|0/1 fill when chat is provided
"""

from __future__ import annotations

import datetime as dt
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

import yaml

from tools.wiki_extract.dict_triage import (
    DEST_DICT_KEEP,
    apply_llm_triage,
    collect_candidates,
    mechanical_suggestion,
)
from tools.wiki_extract.dict_triage import _candidate_to_dict
from tools.wiki_extract.emit import _Dumper, _FlowList, render_dict_page
from tools.wiki_extract.heuristics import dict_page_key, parse_comment_fk
from tools.wiki_extract.join_policy import TENANT_FIELDS, stamp_join_meta

ChatFn = Callable[[str, str], dict[str, Any]]

_FM = re.compile(r"^---\n([\s\S]*?)\n---\n", re.M)
_TABLE_FENCE = re.compile(r"```ground:table\n([\s\S]*?)\n```")
_RELATION_FENCE = re.compile(r"```ground:relation\n([\s\S]*?)\n```")
_DICT_LINK = re.compile(
    r"^- \[\[dicts/([^\]]+)\]\](?:（`[^`]+`）)?\s*$",
    re.M,
)
_TODAY = dt.date.today().isoformat()


def run_scrub(
    *,
    wiki_dir: Path,
    raw_dir: Path | None = None,
    chat: ChatFn | None = None,
    write: bool = True,
) -> dict[str, Any]:
    wiki_dir = Path(wiki_dir)
    raw_dir = Path(raw_dir) if raw_dir else wiki_dir / "_raw"
    catalog = _read_yaml(raw_dir / "catalog.yaml")
    profile = _read_yaml(raw_dir / "profile.yaml")
    if not catalog or not profile:
        raise FileNotFoundError(f"need catalog.yaml + profile.yaml under {raw_dir}")

    tables_meta = catalog.get("tables") or {}
    profile_tables = (profile.get("tables") or {})
    known_tables = {p.stem for p in (wiki_dir / "tables").glob("*.md")}

    # Build mechanical decisions from catalog+profile (not from polluted wiki dicts).
    decisions: dict[tuple[str, str], dict[str, Any]] = {}
    model_for_fill: dict[str, Any] = {
        "tables": {},
        "dict_candidates": [],
        "dicts": {},
    }
    for tname, tmeta in tables_meta.items():
        if tname not in known_tables:
            continue
        compiled = {
            "table": tname,
            "primary_key": list(tmeta.get("primary_key") or []),
            "fields": [
                {
                    "name": cname,
                    "description": str((cinfo or {}).get("comment") or ""),
                    "data_type": str((cinfo or {}).get("type") or ""),
                }
                for cname, cinfo in (tmeta.get("columns") or {}).items()
            ],
        }
        stats = (profile_tables.get(tname) or {}).get("column_stats") or {}
        cands = collect_candidates(compiled, stats)
        model_for_fill["tables"][tname] = {"fields": compiled["fields"]}
        for cand in cands:
            dest, reason = mechanical_suggestion(cand)
            cand["dest"] = dest
            cand["dest_source"] = "mechanical"
            cand["mechanical_dest"] = dest
            cand["mechanical_reason"] = reason
            decisions[(tname, str(cand["column"]))] = cand
            model_for_fill["dict_candidates"].append(cand)

    binary_fills = 0
    if chat is not None:
        stats: dict[str, int] = {}
        # Only keep candidates are fillable; drop already set.
        apply_llm_triage(model_for_fill, {}, chat, stats)
        binary_fills = int(stats.get("dict_binary_fill") or 0)
        for cand in model_for_fill.get("dict_candidates") or []:
            decisions[(str(cand["table"]), str(cand["column"]))] = cand

    drop_keys: set[str] = set()
    keep_updates: dict[str, dict[str, Any]] = {}
    for (tname, col), cand in decisions.items():
        key = dict_page_key(tname, col)
        dest = str(cand.get("dest") or DEST_DROP)
        if dest != DEST_DICT_KEEP:
            # hold or drop → never attach to table field dict
            drop_keys.add(key)
        else:
            keep_updates[key] = cand

    # Also drop wiki fields that still show dict but are comment_fk / ref / etc.
    # even when profile had no values (not in candidates).
    for tname, tmeta in tables_meta.items():
        for cname, cinfo in (tmeta.get("columns") or {}).items():
            comment = str((cinfo or {}).get("comment") or "")
            if cname.lower().startswith("ref_") or parse_comment_fk(comment):
                drop_keys.add(dict_page_key(tname, cname))

    report = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "wiki": str(wiki_dir),
        "dict_drop_keys": sorted(drop_keys),
        "dict_keep_keys": sorted(keep_updates),
        "binary_fills": binary_fills,
        "tables_patched": [],
        "fences_added": [],
        "dicts_deleted": [],
        "dicts_restored": [],
        "fields_dict_cleared": 0,
        "fields_dict_filled": 0,
    }

    for path in sorted((wiki_dir / "tables").glob("*.md")):
        changed, detail = _scrub_table_page(
            path,
            drop_keys=drop_keys,
            keep_updates=keep_updates,
            known_tables=known_tables,
            tables_meta=tables_meta,
            write=write,
        )
        if changed:
            report["tables_patched"].append(path.stem)
            report["fields_dict_cleared"] += detail["cleared"]
            report["fields_dict_filled"] += detail["filled"]
            report["fences_added"].extend(detail["fences"])

    deleted = _delete_orphan_dicts(wiki_dir / "dicts", drop_keys, write=write)
    report["dicts_deleted"] = deleted

    restored_pages = _restore_keep_dict_pages(
        wiki_dir / "dicts", keep_updates, write=write
    )
    report["dicts_restored"] = restored_pages

    if write:
        out = raw_dir / "scrub_wiki.yaml"
        out.write_text(
            yaml.safe_dump(report, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        (raw_dir / "scrub_wiki.md").write_text(_report_md(report), encoding="utf-8")
    return report


def _scrub_table_page(
    path: Path,
    *,
    drop_keys: set[str],
    keep_updates: dict[str, dict[str, Any]],
    known_tables: set[str],
    tables_meta: dict[str, Any],
    write: bool,
) -> tuple[bool, dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    fm_m = _FM.match(text)
    table_m = _TABLE_FENCE.search(text)
    if not fm_m or not table_m:
        return False, {"cleared": 0, "filled": 0, "fences": []}

    front = yaml.safe_load(fm_m.group(1)) or {}
    ground = yaml.safe_load(table_m.group(1)) or {}
    if not isinstance(front, dict) or not isinstance(ground, dict):
        return False, {"cleared": 0, "filled": 0, "fences": []}

    tname = str(ground.get("table") or path.stem)
    fields = list(ground.get("fields") or [])
    cleared = 0
    filled = 0
    new_fields: list[dict[str, Any]] = []
    for field in fields:
        if not isinstance(field, dict):
            continue
        col = str(field.get("name") or "")
        key = dict_page_key(tname, col)
        row = dict(field)
        if key in drop_keys and ("dict" in row or "label" in row):
            row.pop("dict", None)
            row.pop("label", None)
            cleared += 1
        cand = keep_updates.get(key)
        if cand and str(cand.get("dest")) == DEST_DICT_KEEP:
            values = [str(v) for v in (cand.get("values") or {}).keys()]
            existing = [str(x) for x in (row.get("dict") or [])]
            if values and (
                not existing
                or (
                    cand.get("binary_fill", {}).get("supplement")
                    and set(existing) != set(values)
                )
            ):
                row["dict"] = _FlowList(values)
                comment_labels = cand.get("comment_labels") or {}
                if comment_labels:
                    labeled = [str(comment_labels.get(c) or "").strip() for c in values]
                    if labeled and all(labeled):
                        row["label"] = _FlowList(labeled)
                filled += 1
        new_fields.append(row)
    ground["fields"] = new_fields

    # Frontmatter related: drop dict page keys we cleared.
    related = list(front.get("related") or [])
    new_related = [x for x in related if x not in drop_keys]
    fm_changed = new_related != related
    if fm_changed:
        front["related"] = new_related

    # Rebuild ### 字典 link block from remaining field dicts.
    keep_dict_links = []
    for field in new_fields:
        col = str(field.get("name") or "")
        if not field.get("dict"):
            continue
        key = dict_page_key(tname, col)
        if key in drop_keys:
            continue
        keep_dict_links.append(f"- [[dicts/{key}]]（`{tname}.{col}`）")

    body = text[fm_m.end() :]
    body2, dict_links_changed = _replace_dict_links(body, keep_dict_links)

    # Comment-FK fences.
    existing = {
        (str(yaml.safe_load(m.group(1)).get("left") or ""),
         str(yaml.safe_load(m.group(1)).get("right") or ""))
        for m in _RELATION_FENCE.finditer(text)
    }
    fences: list[str] = []
    fence_meta: list[str] = []
    tmeta = tables_meta.get(tname) or {}
    cols = tmeta.get("columns") or {}
    for field in new_fields:
        col = str(field.get("name") or "")
        if col in TENANT_FIELDS:
            continue
        desc = str(field.get("desc") or "")
        comment = str((cols.get(col) or {}).get("comment") or desc)
        for target, target_col in parse_comment_fk(comment or desc):
            if target not in known_tables or target == tname:
                continue
            peer_cols = (tables_meta.get(target) or {}).get("columns") or {}
            if target_col not in peer_cols:
                continue
            left = f"{target}.{target_col}"
            right = f"{tname}.{col}"
            if (left, right) in existing:
                continue
            rel = {
                "type": "EQUI_JOIN",
                "left": left,
                "right": right,
                "cardinality": "one_to_many",
                "trust": "proposed",
                "authenticity": "unknown",
                "source": "comment_fk",
                "join_role": "business_code"
                if left.split(".", 1)[-1] == right.split(".", 1)[-1]
                else "identity",
                "priority": "primary",
                "name_evidence": {
                    "match": "comment_fk",
                    "stem": target,
                    "comment": (comment or desc)[:80],
                },
                "evidence": f"database_schema:{tname}.{col}#comment_fk:{target}#{target_col}",
            }
            stamp_join_meta({"relations": [rel]})
            block = (
                "```ground:relation\n"
                + yaml.dump(rel, Dumper=_Dumper, allow_unicode=True, sort_keys=False).rstrip()
                + "\n```\n"
            )
            fences.append(block)
            fence_meta.append(f"{left}->{right}")
            existing.add((left, right))

    body3 = body2
    if fences:
        body3 = _insert_relation_fences(body2, fences)

    new_table_yaml = yaml.dump(
        ground, Dumper=_Dumper, allow_unicode=True, sort_keys=False
    ).rstrip()
    new_body = _TABLE_FENCE.sub(
        f"```ground:table\n{new_table_yaml}\n```", body3, count=1
    )

    changed = (
        cleared > 0
        or filled > 0
        or fm_changed
        or dict_links_changed
        or bool(fences)
        or new_body != body
    )
    if not changed:
        return False, {"cleared": 0, "filled": 0, "fences": []}

    front["updated"] = _TODAY
    new_text = (
        "---\n"
        + yaml.dump(front, Dumper=_Dumper, allow_unicode=True, sort_keys=False).rstrip()
        + "\n---\n"
        + new_body
    )
    if not new_text.endswith("\n"):
        new_text += "\n"
    if write:
        path.write_text(new_text, encoding="utf-8")
    return True, {"cleared": cleared, "filled": filled, "fences": fence_meta}


def _replace_dict_links(body: str, keep_lines: list[str]) -> tuple[str, bool]:
    """Replace ### 字典 bullet list; remove section if empty."""
    section = re.search(
        r"(### 字典\n\n)((?:- \[\[dicts/[^\]]+\]\].*\n)+)",
        body,
    )
    if not section:
        # also handle missing blank line variants
        section = re.search(
            r"(### 字典\n)((?:- \[\[dicts/[^\]]+\]\].*\n)+)",
            body,
        )
    if not section:
        return body, False
    if not keep_lines:
        # drop whole ### 字典 section including heading
        start = section.start()
        # include preceding newline
        new_body = body[:start] + body[section.end() :]
        new_body = re.sub(r"\n{3,}", "\n\n", new_body)
        return new_body, True
    new_block = section.group(1) + "\n".join(keep_lines) + "\n"
    if section.group(0) == new_block:
        return body, False
    return body[: section.start()] + new_block + body[section.end() :], True


def _insert_relation_fences(body: str, fences: list[str]) -> str:
    if not fences:
        return body
    block = "\n".join(fences) + "\n"
    # Prefer insert before ## 页面链接
    m = re.search(r"\n## 页面链接\n", body)
    if m:
        return body[: m.start()] + "\n" + block + body[m.start() :]
    # Or after existing 关联关系 section
    m2 = re.search(r"\n## 关联关系\n", body)
    if m2:
        # append at end of relation area = before 页面链接 or EOF
        m3 = re.search(r"\n## 页面链接\n", body)
        at = m3.start() if m3 else len(body)
        return body[:at] + "\n" + block + body[at:]
    # Create section before 页面链接 or at end
    m4 = re.search(r"\n## 页面链接\n", body)
    section = "## 关联关系\n\n### comment_fk（schema 注释）\n\n" + block
    if m4:
        return body[: m4.start()] + "\n" + section + body[m4.start() :]
    return body.rstrip() + "\n\n" + section


def _delete_orphan_dicts(
    dicts_dir: Path, drop_keys: set[str], *, write: bool
) -> list[str]:
    deleted: list[str] = []
    if not dicts_dir.is_dir():
        return deleted
    for key in sorted(drop_keys):
        path = dicts_dir / f"{key}.md"
        if path.exists():
            deleted.append(key)
            if write:
                path.unlink()
    return deleted


def _restore_keep_dict_pages(
    dicts_dir: Path,
    keep_updates: dict[str, dict[str, Any]],
    *,
    write: bool,
) -> list[str]:
    """Recreate missing dict pages for KEEP columns (e.g. after a too-aggressive scrub)."""
    restored: list[str] = []
    dicts_dir.mkdir(parents=True, exist_ok=True)
    for key, cand in sorted(keep_updates.items()):
        if str(cand.get("dest")) != DEST_DICT_KEEP:
            continue
        path = dicts_dir / f"{key}.md"
        if path.exists():
            continue
        item = _candidate_to_dict(cand, key, DEST_DICT_KEEP)
        if write:
            path.write_text(render_dict_page(item, _TODAY), encoding="utf-8")
        restored.append(key)
    return restored


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _report_md(report: dict[str, Any]) -> str:
    lines = [
        "# Wiki scrub",
        "",
        f"- generated_at: `{report.get('generated_at')}`",
        f"- tables_patched: {len(report.get('tables_patched') or [])}",
        f"- fields_dict_cleared: {report.get('fields_dict_cleared')}",
        f"- fields_dict_filled: {report.get('fields_dict_filled')}",
        f"- binary_fills: {report.get('binary_fills')}",
        f"- comment_fk fences: {len(report.get('fences_added') or [])}",
        f"- dicts_deleted: {len(report.get('dicts_deleted') or [])}",
        f"- dicts_restored: {len(report.get('dicts_restored') or [])}",
        "",
        "## Comment-FK fences added",
        "",
    ]
    for item in report.get("fences_added") or []:
        lines.append(f"- `{item}`")
    lines.extend(["", "## Sample dropped dict keys", ""])
    for key in (report.get("dict_drop_keys") or [])[:40]:
        lines.append(f"- `{key}`")
    if len(report.get("dict_drop_keys") or []) > 40:
        lines.append(f"- … +{len(report['dict_drop_keys']) - 40} more")
    lines.append("")
    return "\n".join(lines)
