"""Write L0 draft wiki pages. Never emits status: published."""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

import yaml


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
    overlap: dict[str, Any] | None = None,
) -> dict[str, int]:
    out = out.resolve()
    _assert_isolated(out)
    today = str(model.get("generated_at") or dt.date.today().isoformat())
    tables_dir = out / "tables"
    enums_dir = out / "enums"
    raw_dir = out / "_raw"
    runs_dir = out / ".runs" / "l0"
    for path in (tables_dir, enums_dir, raw_dir, runs_dir):
        path.mkdir(parents=True, exist_ok=True)

    _clear_markdown(tables_dir)
    _clear_markdown(enums_dir)

    if catalog is not None:
        _write_yaml(raw_dir / "catalog.yaml", catalog)
    if overlap is not None:
        _write_yaml(raw_dir / "overlap.yaml", overlap)
    elif model.get("_overlap") is not None:
        _write_yaml(raw_dir / "overlap.yaml", model["_overlap"])
    if model.get("_llm_judge") is not None:
        _write_yaml(raw_dir / "llm_judge.yaml", model["_llm_judge"])

    table_count = 0
    neighbors = _relation_neighbors(model.get("tables") or {})
    for tname in model.get("table_order") or (model.get("tables") or {}).keys():
        compiled = (model.get("tables") or {}).get(tname)
        if not compiled:
            continue
        (tables_dir / f"{tname}.md").write_text(
            render_table_page(compiled, today, neighbors=neighbors.get(tname) or []),
            encoding="utf-8",
        )
        table_count += 1

    enum_count = 0
    for key, enum in (model.get("enums") or {}).items():
        (enums_dir / f"{key}.md").write_text(
            render_enum_page(enum, today), encoding="utf-8"
        )
        enum_count += 1

    reviews = _number_reviews(list(model.get("reviews") or []), today)
    _write_yaml(runs_dir / "reviews.yaml", {"generated_at": today, "items": reviews})
    _write_yaml(
        out / "value_index.yaml",
        {
            "generated_at": today,
            "database": model.get("database"),
            "entries": model.get("value_index") or [],
        },
    )
    (out / "_index.md").write_text(_index_markdown(model, today), encoding="utf-8")
    (out / "_log.md").write_text(_log_markdown(model, today), encoding="utf-8")
    return {"tables": table_count, "enums": enum_count, "reviews": len(reviews)}


def render_table_page(
    compiled: dict[str, Any],
    today: str,
    *,
    neighbors: list[str] | None = None,
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
        "description": compiled.get("description") or tname,
        "inactive": False,
        "primary_key": _FlowList(list(compiled.get("primary_key") or [])),
        "grain": compiled.get("grain"),
        "name_anchors": _FlowList(list(compiled.get("name_anchors") or [])),
        "clusters": _emit_clusters(compiled.get("clusters") or []),
        "fields": _emit_fields(compiled.get("fields") or []),
    }
    parts = [
        "---",
        _dump(front).rstrip(),
        "---",
        "",
        f"# {title}",
        "",
        "L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。",
        "",
        "## 字段簇",
        "",
        _cluster_index(compiled),
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
        for rel in rels:
            parts.extend(
                [
                    "```ground:relation",
                    _dump(_emit_relation(rel)).rstrip(),
                    "```",
                    "",
                ]
            )
    links = _table_link_section(compiled, neighbors or [])
    if links:
        parts.extend(["## 页面链接", "", links, ""])
    return "\n".join(parts).rstrip() + "\n"


def render_enum_page(enum: dict[str, Any], today: str) -> str:
    key = str(enum["enum"])
    table = str(enum.get("table") or "")
    column = str(enum.get("column") or "")
    source = (
        f"database_profile:{table}.{column}"
        if table and column
        else f"database_profile:{key}"
    )
    physical = f"{table}.{column}" if table and column else key
    front = {
        "type": "enum",
        "title": physical,
        "page_key": key,
        "belong": "enums",
        "status": "draft",
        "anchors": _FlowList([physical]),
        "sources": _FlowList([source]),
        "created": today,
        "updated": today,
        "contract_version": "0.1",
    }
    if table:
        front["related"] = _FlowList([table])
    values = _emit_enum_values(enum.get("values") or {})
    ground: dict[str, Any] = {
        "enum": key,
        "fields": _FlowList(list(enum.get("fields") or [])),
        "values": values,
    }
    if enum.get("mixed") or enum.get("ambiguous"):
        ground["mixed"] = True
    has_label = any(
        isinstance(meta, dict) and meta.get("label")
        for meta in (enum.get("values") or {}).values()
    )
    blurb = (
        "L0 枚举候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。"
        if has_label
        else "L0 枚举候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。"
    )
    if has_label and table and column:
        front["sources"] = _FlowList([source, f"database_schema:{table}.{column}"])
    return (
        "---\n"
        + _dump(front).rstrip()
        + "\n---\n\n"
        + f"# {physical}\n\n"
        + blurb
        + (f"\n物理列 `{physical}`，表页 [[tables/{table}]]。\n" if table else "\n")
        + "\n## 取值\n\n"
        + "```ground:enum\n"
        + _dump(ground).rstrip()
        + "\n```\n"
    )


def _emit_enum_values(values: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for raw, meta in values.items():
        key = str(raw or "").strip()
        if not key or key.lower() in {"none", "null"}:
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
    return {
        "type": rel.get("type") or "EQUI_JOIN",
        "left": rel.get("left"),
        "right": rel.get("right"),
        "cardinality": rel.get("cardinality"),
        "trust": rel.get("trust") or rel.get("confidence") or "proposed",
        "evidence": rel.get("evidence"),
    }


def _emit_clusters(clusters: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in clusters:
        row: dict[str, Any] = {
            "key": item["key"],
            "title": item.get("title") or item["key"],
        }
        if item.get("include"):
            row["include"] = item["include"]
        trust = item.get("trust") or item.get("confidence")
        if trust:
            row["trust"] = trust
        if item.get("evidence"):
            row["evidence"] = item["evidence"]
        out.append(row)
    return out


def _emit_fields(fields: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in fields:
        row: dict[str, Any] = {
            "name": item["name"],
            "data_type": item.get("data_type") or "string",
        }
        desc = str(item.get("description") or "")
        if desc:
            row["description"] = desc
        if item.get("nullable") is False:
            row["nullable"] = False
        if item.get("cluster"):
            row["cluster"] = item["cluster"]
        if item.get("dictionary"):
            row["dictionary"] = item["dictionary"]
        out.append(row)
    return out


def _cluster_index(compiled: dict[str, Any]) -> str:
    lines: list[str] = []
    by_cluster: dict[str, list[str]] = {}
    unassigned: list[str] = []
    for field in compiled.get("fields") or []:
        cluster = str(field.get("cluster") or "")
        name = str(field.get("name") or "")
        if cluster:
            by_cluster.setdefault(cluster, []).append(name)
        else:
            unassigned.append(name)
    for cluster in compiled.get("clusters") or []:
        key = str(cluster.get("key") or "")
        members = by_cluster.get(key) or []
        lines.append(f"### {key}")
        lines.append("")
        lines.append(", ".join(f"`{c}`" for c in members) if members else "（空）")
        lines.append("")
    if unassigned:
        lines.append("### 未归簇")
        lines.append("")
        lines.append(", ".join(f"`{c}`" for c in unassigned))
        lines.append("")
    return "\n".join(lines).rstrip()


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
        dictionary = str(field.get("dictionary") or "")
        if dictionary:
            add(dictionary)
    return seen


def _table_link_section(compiled: dict[str, Any], neighbors: list[str]) -> str:
    tname = str(compiled.get("table") or "")
    lines: list[str] = []
    if neighbors:
        lines.append("### 关联表")
        lines.append("")
        for other in neighbors:
            lines.append(f"- [[tables/{other}]]")
        lines.append("")
    enums: list[tuple[str, str]] = []
    for field in compiled.get("fields") or []:
        dictionary = str(field.get("dictionary") or "")
        col = str(field.get("name") or "")
        if dictionary:
            enums.append((dictionary, f"{tname}.{col}" if col else dictionary))
    if enums:
        lines.append("### 字典")
        lines.append("")
        for key, physical in enums:
            lines.append(f"- [[enums/{key}]]（`{physical}`）")
        lines.append("")
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
    enums = list((model.get("enums") or {}).keys())
    lines = [
        f"# L0 index ({today})",
        "",
        f"- database: `{model.get('database')}`",
        f"- tables: {len(tables)}",
        f"- enum candidates: {len(enums)}",
        f"- reviews: {len(model.get('reviews') or [])}",
        "",
        "## tables",
        "",
    ]
    for name in tables:
        lines.append(f"- [[tables/{name}]]")
    lines.extend(["", "## enums", ""])
    for name in enums:
        lines.append(f"- [[enums/{name}]]")
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
            f"keep={stats.get('enum_keep', 0)} "
            f"instance={stats.get('enum_instance', 0)} "
            f"reject={stats.get('enum_reject', 0)} "
            f"auto_reject={stats.get('enum_auto_reject', 0)} "
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


def _assert_isolated(out: Path) -> None:
    bits = out.resolve().parts
    banned = {"wiki-pages", "wiki-pages-v2", "wiki-pages-v3"}
    if banned.intersection(bits):
        raise ValueError(
            f"refusing to write under existing wiki corpus dirs {sorted(banned)}"
        )
    if bits[-1] == "db" or (len(bits) >= 2 and bits[-2] == "db"):
        raise ValueError("refusing to write into db substrate")
