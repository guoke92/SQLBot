"""Write L0 draft wiki pages. Never emits status: published."""

from __future__ import annotations

import datetime as dt
import shutil
from pathlib import Path
from typing import Any

import yaml

from tools.wiki_extract.instance_index import packed_instance_index
from tools.wiki_extract.overlap import sync_overlap_from_relations


class _FlowList(list):
    """Scalar lists dumped inline: [id, code]."""


class _FlowMap(dict):
    """Small maps dumped inline: { trust: proposed }."""


def _represent_flow_list(dumper: yaml.SafeDumper, data: _FlowList) -> yaml.Node:
    return dumper.represent_sequence(
        "tag:yaml.org,2002:seq", list(data), flow_style=True
    )


def _represent_flow_map(dumper: yaml.SafeDumper, data: _FlowMap) -> yaml.Node:
    return dumper.represent_mapping(
        "tag:yaml.org,2002:map", dict(data), flow_style=True
    )


class _Dumper(yaml.SafeDumper):
    pass


_Dumper.add_representer(_FlowList, _represent_flow_list)
_Dumper.add_representer(_FlowMap, _represent_flow_map)


def emit(
    model: dict[str, Any],
    out: Path,
    *,
    catalog: dict[str, Any] | None = None,
    profile: dict[str, Any] | None = None,
    profile_instance: dict[str, Any] | None = None,
    overlap: dict[str, Any] | None = None,
) -> dict[str, int]:
    out = out.resolve()
    _assert_isolated(out)
    today = str(model.get("generated_at") or dt.date.today().isoformat())
    tables_dir = out / "tables"
    dicts_dir = out / "dicts"
    raw_dir = out / "_raw"
    runs_dir = out / ".runs" / "l0"
    for path in (tables_dir, dicts_dir, raw_dir, runs_dir):
        path.mkdir(parents=True, exist_ok=True)

    _clear_markdown(tables_dir)
    _clear_markdown(dicts_dir)
    _clear_legacy(out)

    if catalog is not None:
        _write_yaml(raw_dir / "catalog.yaml", catalog)
    if profile is not None:
        _write_yaml(raw_dir / "profile.yaml", profile)
    if profile_instance is not None:
        _write_yaml(raw_dir / "profile_instance.yaml", profile_instance)
    packed_overlap = overlap if overlap is not None else model.get("_overlap")
    if packed_overlap is not None:
        _write_yaml(
            raw_dir / "overlap.yaml",
            sync_overlap_from_relations(model, packed_overlap),
        )
    if model.get("_llm_judge") is not None:
        _write_yaml(raw_dir / "llm_judge.yaml", model["_llm_judge"])

    table_count = 0
    neighbors = _relation_neighbors(model.get("tables") or {})
    for tname in model.get("table_order") or (model.get("tables") or {}).keys():
        compiled = (model.get("tables") or {}).get(tname)
        if not compiled:
            continue
        (tables_dir / f"{tname}.md").write_text(
            render_table_page(
                compiled,
                today,
                neighbors=neighbors.get(tname) or [],
                dicts=model.get("dicts") or {},
            ),
            encoding="utf-8",
        )
        table_count += 1

    dict_count = 0
    for key, item in (model.get("dicts") or {}).items():
        (dicts_dir / f"{key}.md").write_text(
            render_dict_page(item, today), encoding="utf-8"
        )
        dict_count += 1

    reviews = _number_reviews(list(model.get("reviews") or []), today)
    _write_yaml(runs_dir / "reviews.yaml", {"generated_at": today, "items": reviews})
    _write_yaml(out / "instance_index.yaml", packed_instance_index(model))
    (out / "_index.md").write_text(_index_markdown(model, today), encoding="utf-8")
    (out / "_log.md").write_text(_log_markdown(model, today), encoding="utf-8")
    return {"tables": table_count, "dicts": dict_count, "reviews": len(reviews)}


def render_table_page(
    compiled: dict[str, Any],
    today: str,
    *,
    neighbors: list[str] | None = None,
    fallback_links: list[tuple[str, str]] | None = None,
    dicts: dict[str, Any] | None = None,
) -> str:
    tname = str(compiled["table"])
    database = str(compiled.get("database") or "")
    title = str(compiled.get("description") or tname).replace(":", "：")
    front: dict[str, Any] = {
        "type": "table",
        "title": title,
        "page_key": tname,
        "belong": "tables",
        "status": "draft",
        "anchors": _FlowList([tname]),
        "sources": _FlowList([f"database_schema:{database}.{tname}"]),
        "created": today,
        "updated": today,
        "contract_version": "0.1",
    }
    if database:
        front["databases"] = _FlowList([database])
    related = _table_related(compiled, neighbors or [])
    if related:
        front["related"] = _FlowList(related)
    ground_table = {
        "table": tname,
        "database": database,
        "desc": compiled.get("desc") or compiled.get("description") or tname,
        "inactive": bool(compiled.get("inactive") or False),
        "primary_key": _FlowList(list(compiled.get("primary_key") or [])),
        "grain": compiled.get("grain"),
        "name_anchors": _FlowList(list(compiled.get("name_anchors") or [])),
        "fields": _emit_fields(
            compiled.get("fields") or [], dicts or {}, table=tname
        ),
    }
    default_filter = compiled.get("default_filter")
    if isinstance(default_filter, dict) and default_filter.get("predicate"):
        ground_table["default_filter"] = {
            "predicate": default_filter["predicate"],
            "trust": default_filter.get("trust") or "proposed",
        }
        if default_filter.get("evidence"):
            ground_table["default_filter"]["evidence"] = default_filter["evidence"]
        sources = list(front.get("sources") or [])
        evidence = str(default_filter.get("evidence") or "")
        if evidence and evidence not in sources:
            sources.append(evidence)
            front["sources"] = _FlowList(sources)
    l1_note = bool(compiled.get("default_filter") or compiled.get("l1_enhanced"))
    blurb = (
        "L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。"
        if l1_note
        else "L0 库侧合同（draft）。grain / 身份束关系均为 proposed，不得当认证 JOIN。"
    )
    parts = [
        "---",
        _dump(front).rstrip(),
        "---",
        "",
        f"# {title}",
        "",
        blurb,
        "",
        "## 字段",
        "",
        "```ground:table",
        _dump(ground_table).rstrip(),
        "```",
        "",
    ]
    rels = list(compiled.get("relations") or [])
    if rels:
        parts.extend(["## 关联关系", ""])
        groups = _group_relations(rels)
        for heading, bucket in groups:
            if not bucket:
                continue
            parts.extend([f"### {heading}", ""])
            for rel in bucket:
                parts.extend(
                    [
                        "```ground:relation",
                        _dump(_emit_relation(rel)).rstrip(),
                        "```",
                        "",
                    ]
                )
    links = _table_link_section(
        compiled, neighbors or [], fallback_links=fallback_links
    )
    if links:
        parts.extend(["## 页面链接", "", links, ""])
    return "\n".join(parts).rstrip() + "\n"


def render_dict_page(item: dict[str, Any], today: str) -> str:
    key = str(item.get("dict") or item.get("enum") or "")
    table = str(item.get("table") or "")
    column = str(item.get("column") or "")
    source = (
        f"database_profile:{table}.{column}"
        if table and column
        else f"database_profile:{key}"
    )
    physical = f"{table}.{column}" if table and column else key
    front = {
        "type": "dict",
        "title": physical,
        "page_key": key,
        "belong": "dicts",
        "status": "draft",
        "anchors": _FlowList([physical]),
        "sources": _FlowList([source]),
        "created": today,
        "updated": today,
        "contract_version": "0.1",
    }
    if table:
        front["related"] = _FlowList([table])
    values = _emit_dict_values(item.get("values") or {})
    ground: dict[str, Any] = {
        "dict": key,
        "fields": _FlowList(list(item.get("fields") or [])),
        "values": values,
    }
    if item.get("mixed") or item.get("ambiguous"):
        ground["mixed"] = True
    triage = str(item.get("triage") or "").strip()
    if triage:
        ground["triage"] = triage
    if item.get("needs_review"):
        ground["needs_review"] = True
    has_label = any(
        isinstance(meta, dict) and meta.get("label")
        for meta in (item.get("values") or {}).values()
    )
    has_confirmed_label = any(
        isinstance(meta, dict)
        and meta.get("label")
        and str(meta.get("trust") or "") == "confirmed"
        for meta in (item.get("values") or {}).values()
    )
    if has_confirmed_label:
        blurb = "L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。"
    elif has_label:
        blurb = (
            "L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。"
        )
    else:
        blurb = "L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。"
    if item.get("needs_review") or triage == "hold":
        blurb += " 初审 hold：证据不足，保留待人工确认。"
    if has_label and table and column:
        front["sources"] = _FlowList([source, f"database_schema:{table}.{column}"])
    extra_src: list[str] = []
    for meta in (item.get("values") or {}).values():
        ev = str((meta or {}).get("evidence") or "") if isinstance(meta, dict) else ""
        if ev.startswith("code_path:") and ev not in extra_src:
            extra_src.append(ev)
    if extra_src:
        sources = list(front.get("sources") or [])
        for ev in extra_src:
            if ev not in sources:
                sources.append(ev)
        front["sources"] = _FlowList(sources)
    return (
        "---\n"
        + _dump(front).rstrip()
        + "\n---\n\n"
        + f"# {physical}\n\n"
        + blurb
        + (f"\n物理列 `{physical}`，表页 [[tables/{table}]]。\n" if table else "\n")
        + "\n## 取值\n\n"
        + "```ground:dict\n"
        + _dump(ground).rstrip()
        + "\n```\n"
    )


def _emit_dict_values(values: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for raw, meta in values.items():
        key = str(raw or "").strip()
        # Drop empty / SQL-null placeholders only. Keep real enum code "NONE".
        if not key or key in {"null", "None", "<null>", "<NULL>"}:
            continue
        row = meta if isinstance(meta, dict) else {}
        claim = row.get("trust") or row.get("confidence") or "proposed"
        packed: dict[str, Any] = {"trust": claim}
        if row.get("label"):
            packed["label"] = row["label"]
        if row.get("evidence"):
            packed["evidence"] = row["evidence"]
        out[key] = _FlowMap(packed)
    return out


def _emit_relation(rel: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {
        "type": rel.get("type") or "EQUI_JOIN",
        "left": rel.get("left"),
        "right": rel.get("right"),
        "cardinality": rel.get("cardinality"),
        "trust": rel.get("trust") or rel.get("confidence") or "proposed",
        "authenticity": str(rel.get("authenticity") or "unknown"),
        "evidence": rel.get("evidence"),
    }
    source = str(rel.get("source") or "").strip()
    if source:
        out["source"] = source
    role = str(rel.get("join_role") or "").strip()
    if role:
        out["join_role"] = role
    priority = str(rel.get("priority") or "").strip()
    if priority:
        out["priority"] = priority
    name_ev = rel.get("name_evidence")
    if isinstance(name_ev, dict) and any(name_ev.values()):
        out["name_evidence"] = {
            k: name_ev[k]
            for k in ("match", "stem", "comment")
            if name_ev.get(k) not in (None, "")
        }
    overlap = rel.get("overlap")
    if isinstance(overlap, dict) and overlap:
        ov: dict[str, Any] = {}
        if "probed" in overlap:
            ov["probed"] = bool(overlap.get("probed"))
        for key in (
            "ratio",
            "ratio_reverse",
            "sample_size",
            "miss",
            "deepened",
            "query_ok",
            "authenticity",
            "skipped",
            "status",
        ):
            if key in overlap and overlap.get(key) is not None:
                ov[key] = overlap[key]
        if ov:
            out["overlap"] = ov
    note = str(rel.get("authenticity_note") or "").strip()
    if note:
        out["authenticity_note"] = note[:240]
    cast = rel.get("cast")
    if cast not in (None, "", "null"):
        out["cast"] = cast
    sides = rel.get("sides")
    if isinstance(sides, list) and sides:
        packed_sides = []
        for side in sides:
            if isinstance(side, dict):
                packed_sides.append(_FlowMap({k: side[k] for k in side if side.get(k) not in (None, "")}))
            else:
                packed_sides.append(side)
        out["sides"] = packed_sides
    block = str(rel.get("preview_block") or "").strip()
    if block:
        out["preview_block"] = block
    return out


def _group_relations(
    rels: list[dict[str, Any]],
) -> list[tuple[str, list[dict[str, Any]]]]:
    """Group edges: confirmed likely, then disputed conflicts, then remaining L0."""
    order = (
        ("likely — 值域支持且列名/注释有关联语义", "likely"),
        ("disputed — 与已确认边冲突", "disputed"),
        ("unknown — 待复核", "unknown"),
        ("unlikely — 值域不支持或冲突", "unlikely"),
    )
    buckets: dict[str, list[dict[str, Any]]] = {
        "likely": [],
        "disputed": [],
        "unknown": [],
        "unlikely": [],
    }
    for rel in rels:
        if str(rel.get("trust") or "") == "disputed":
            buckets["disputed"].append(rel)
            continue
        auth = str(rel.get("authenticity") or "unknown").lower()
        if auth not in buckets:
            auth = "unknown"
        buckets[auth].append(rel)
    for key in buckets:
        buckets[key].sort(
            key=lambda rel: 0
            if str(rel.get("priority") or "primary") == "primary"
            else 1
        )
    return [(title, buckets[key]) for title, key in order]


def field_dict_page_key(field: dict[str, Any], table: str) -> str:
    """Dict page_key is always 表__字段; field YAML no longer stores that filename."""
    raw = field.get("dictionary")
    if isinstance(raw, str) and raw.strip():
        return raw.strip()
    col = str(field.get("name") or "").strip()
    if isinstance(field.get("dict"), list) and table and col:
        return f"{table}__{col}"
    return ""


def _dict_value_lists(
    page_key: str, dicts: dict[str, Any]
) -> tuple[list[str], list[str]]:
    item = dicts.get(page_key) or {}
    values = item.get("values") or {}
    if not isinstance(values, dict):
        return [], []
    keys: list[str] = []
    labels: list[str] = []
    for key, meta in values.items():
        code = str(key).strip()
        if not code:
            continue
        keys.append(code)
        lab = ""
        if isinstance(meta, dict):
            lab = str(meta.get("label") or "").strip()
            if lab == code:
                lab = ""
        labels.append(lab)
    return keys, labels


def _emit_fields(
    fields: list[dict[str, Any]],
    dicts: dict[str, Any],
    *,
    table: str = "",
) -> list[dict[str, Any]]:
    """Emit compact field rows.

    When a sibling dict page exists for the column, that page is authoritative
    for both ``dict`` codes and ``label`` text. Table fields must not keep a
    stale code-only snapshot after dict labels are upgraded (L1 / re-emit).
    """
    out: list[dict[str, Any]] = []
    for item in fields:
        row: dict[str, Any] = {
            "name": item["name"],
            "type": item.get("type") or item.get("data_type") or "string",
        }
        desc = str(item.get("desc") or item.get("description") or "")
        if desc:
            row["desc"] = desc
        if item.get("nullable") is False:
            row["nullable"] = False
        page_key = field_dict_page_key(item, table)
        page_keys, page_labels = (
            _dict_value_lists(page_key, dicts) if page_key else ([], [])
        )
        raw_dict = item.get("dict")
        if page_keys:
            keys = page_keys
            label_map = {
                code: lab for code, lab in zip(page_keys, page_labels) if lab
            }
        elif isinstance(raw_dict, list) and raw_dict:
            keys = [str(code).strip() for code in raw_dict if str(code).strip()]
            label_map = _field_label_map(item, keys)
        else:
            keys = []
            label_map = {}
        if keys:
            row["dict"] = _FlowList(keys)
            labeled = {code: label_map[code] for code in keys if label_map.get(code)}
            if labeled:
                if len(labeled) == len(keys):
                    row["label"] = _FlowList([labeled[code] for code in keys])
                else:
                    row["label"] = _FlowMap(labeled)
        written = item.get("written_with") or []
        if written:
            row["written_with"] = _FlowList(list(written))
        out.append(row)
    return out


def _field_label_map(item: dict[str, Any], keys: list[str]) -> dict[str, str]:
    raw_labels = item.get("label")
    if isinstance(raw_labels, list):
        return {
            code: str(lab).strip()
            for code, lab in zip(keys, raw_labels)
            if str(lab).strip()
        }
    if isinstance(raw_labels, dict):
        return {
            str(code): str(lab).strip()
            for code, lab in raw_labels.items()
            if str(code).strip() and str(lab).strip()
        }
    return {}


def _table_of(endpoint: str) -> str:
    text = str(endpoint or "")
    return text.split(".", 1)[0] if "." in text else text


def _relation_neighbors(tables: dict[str, Any]) -> dict[str, list[str]]:
    """Undirected table graph for wikilinks. JOIN ground stays on the FK page."""
    graph: dict[str, list[str]] = {}

    def add(src: str, dst: str) -> None:
        if not src or not dst or src == dst:
            return
        bucket = graph.setdefault(src, [])
        if dst not in bucket:
            bucket.append(dst)

    for compiled in tables.values():
        for rel in compiled.get("relations") or []:
            left = _table_of(str(rel.get("left") or ""))
            right = _table_of(str(rel.get("right") or ""))
            add(left, right)
            add(right, left)
    return graph


def _table_related(compiled: dict[str, Any], neighbors: list[str]) -> list[str]:
    seen: list[str] = []
    tname = str(compiled.get("table") or "")

    def add(slug: str) -> None:
        if slug and slug != tname and slug not in seen:
            seen.append(slug)

    for other in neighbors:
        add(other)
    for field in compiled.get("fields") or []:
        if isinstance(field, dict):
            add(field_dict_page_key(field, tname))
    return seen


def _table_link_section(
    compiled: dict[str, Any],
    neighbors: list[str],
    fallback_links: list[tuple[str, str]] | None = None,
) -> str:
    tname = str(compiled.get("table") or "")
    lines: list[str] = []
    if neighbors:
        lines.append("### 关联表")
        lines.append("")
        for other in neighbors:
            lines.append(f"- [[tables/{other}]]")
        lines.append("")
    dicts: list[tuple[str, str]] = []
    for field in compiled.get("fields") or []:
        if not isinstance(field, dict):
            continue
        dictionary = field_dict_page_key(field, tname)
        col = str(field.get("name") or "")
        if dictionary:
            dicts.append((dictionary, f"{tname}.{col}" if col else dictionary))
    if dicts:
        lines.append("### 字典")
        lines.append("")
        for key, physical in dicts:
            lines.append(f"- [[dicts/{key}]]（`{physical}`）")
        lines.append("")
    if not lines:
        for belong, key in fallback_links or []:
            belong = str(belong or "").strip()
            key = str(key or "").strip()
            if belong and key:
                lines.append(f"- [[{belong}/{key}]]")
    return "\n".join(lines).rstrip()


def _number_reviews(items: list[dict[str, Any]], today: str) -> list[dict[str, Any]]:
    numbered: list[dict[str, Any]] = []
    for index, item in enumerate(items, start=1):
        row = dict(item)
        row["id"] = f"rv_l0_{index:04d}"
        row["created"] = today
        numbered.append(row)
    return numbered


def _index_markdown(model: dict[str, Any], today: str) -> str:
    tables = list(model.get("table_order") or (model.get("tables") or {}).keys())
    dicts = list((model.get("dicts") or {}).keys())
    lines = [
        f"# L0 index ({today})",
        "",
        f"- database: `{model.get('database')}`",
        f"- tables: {len(tables)}",
        f"- dict candidates: {len(dicts)}",
        f"- instance index: {len(model.get('instance_index') or [])}",
        f"- reviews: {len(model.get('reviews') or [])}",
        "",
        "## tables",
        "",
    ]
    for name in tables:
        lines.append(f"- [[tables/{name}]]")
    lines.extend(["", "## dicts", ""])
    for name in dicts:
        lines.append(f"- [[dicts/{name}]]")
    lines.append("")
    return "\n".join(lines)


def _log_markdown(model: dict[str, Any], today: str) -> str:
    tables = list(model.get("table_order") or (model.get("tables") or {}).keys())
    stats = model.get("llm_stats") or {}
    join_counts = {"likely": 0, "unlikely": 0, "unknown": 0}
    for compiled in (model.get("tables") or {}).values():
        for rel in compiled.get("relations") or []:
            auth = str(rel.get("authenticity") or "unknown")
            if auth not in join_counts:
                auth = "unknown"
            join_counts[auth] += 1
    llm_line = ""
    if stats:
        llm_line = (
            "\nllm refine: "
            f"keep={stats.get('dict_keep', 0)} "
            f"hold={stats.get('dict_hold', 0)} "
            f"drop={stats.get('dict_drop', 0)} "
            f"auto_drop={stats.get('dict_auto_drop', 0)} "
            f"failed_tables={stats.get('failed', 0)}\n"
        )
    join_line = (
        "\njoin authenticity: "
        f"likely={join_counts['likely']} "
        f"unlikely={join_counts['unlikely']} "
        f"unknown={join_counts['unknown']} "
        f"(all edges kept, no primary)\n"
    )
    ov_stats = dict(model.get("overlap_stats") or {})
    if not ov_stats:
        ov_stats = _overlap_stats_from_relations(model)
    overlap_line = (
        "\noverlap: "
        f"probed={ov_stats.get('probed', 0)} "
        f"likely={ov_stats.get('likely', 0)} "
        f"unlikely={ov_stats.get('unlikely', 0)} "
        f"unknown={ov_stats.get('unknown', 0)} "
        f"llm_added={ov_stats.get('llm_added', 0)} "
        f"overlap_added={ov_stats.get('overlap_added', 0)} "
        f"name_only_unprobed={ov_stats.get('name_only_unprobed', 0)} "
        f"deepened={ov_stats.get('deepened', 0)}\n"
    )
    grain_line = (
        "\ngrain: L0 placeholder 一行一记录（pk）; confirm from source. "
        "inactive left false until source/docs prove dormancy.\n"
    )
    return (
        f"# L0 ingest log ({today})\n\n"
        f"source: tools.wiki_extract compile (database_schema)\n\n"
        f"touched tables ({len(tables)}): "
        + ", ".join(f"`{t}`" for t in tables)
        + "\n"
        + llm_line
        + join_line
        + overlap_line
        + grain_line
        + "\nstatus: all pages draft; no published writes.\n"
    )


def _overlap_stats_from_relations(model: dict[str, Any]) -> dict[str, int]:
    stats = {
        "probed": 0,
        "likely": 0,
        "unlikely": 0,
        "unknown": 0,
        "llm_added": 0,
        "overlap_added": 0,
        "name_only_unprobed": 0,
        "deepened": 0,
    }
    for compiled in (model.get("tables") or {}).values():
        for rel in compiled.get("relations") or []:
            ov = rel.get("overlap") or {}
            if ov.get("probed"):
                stats["probed"] += 1
            elif not ov.get("skipped"):
                stats["name_only_unprobed"] += 1
            if ov.get("deepened"):
                stats["deepened"] += 1
            if str(rel.get("source") or "") == "overlap":
                stats["overlap_added"] += 1
            if str(rel.get("source") or "") == "llm":
                stats["llm_added"] += 1
            auth = str((ov.get("authenticity") or rel.get("authenticity") or "unknown"))
            if auth in {"likely", "unlikely", "unknown"}:
                stats[auth] += 1
    return stats


def _dump(data: Any) -> str:
    return yaml.dump(
        data,
        Dumper=_Dumper,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
    )


def _write_yaml(path: Path, data: Any) -> None:
    path.write_text(_dump(data), encoding="utf-8")


def _clear_markdown(directory: Path) -> None:
    for path in directory.glob("*.md"):
        path.unlink()


def _clear_legacy(out: Path) -> None:
    enums_dir = out / "enums"
    if enums_dir.exists():
        shutil.rmtree(enums_dir)
    legacy_index = out / "value_index.yaml"
    if legacy_index.exists():
        legacy_index.unlink()


def _assert_isolated(out: Path) -> None:
    bits = out.resolve().parts
    banned = {"wiki-pages", "wiki-pages-v2", "wiki-pages-v3"}
    if banned.intersection(bits):
        raise ValueError(
            f"refusing to write under existing wiki corpus dirs {sorted(banned)}"
        )
    if bits[-1] == "db" or (len(bits) >= 2 and bits[-2] == "db"):
        raise ValueError("refusing to write into db substrate")
