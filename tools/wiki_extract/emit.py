"""Write L0 draft wiki pages. Never emits status: published."""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

import yaml


def emit(
    model: dict[str, Any],
    out: Path,
    *,
    catalog: dict[str, Any] | None = None,
    profile: dict[str, Any] | None = None,
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
    if profile is not None:
        _write_yaml(raw_dir / "profile.yaml", profile)
    if model.get("_llm_judge") is not None:
        _write_yaml(raw_dir / "llm_judge.yaml", model["_llm_judge"])

    table_count = 0
    for tname in model.get("table_order") or (model.get("tables") or {}).keys():
        compiled = (model.get("tables") or {}).get(tname)
        if not compiled:
            continue
        (tables_dir / f"{tname}.md").write_text(
            render_table_page(compiled, today), encoding="utf-8"
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


def render_table_page(compiled: dict[str, Any], today: str) -> str:
    tname = str(compiled["table"])
    database = str(compiled.get("database") or "")
    title = str(compiled.get("description") or tname).replace(":", "：")
    front = {
        "type": "table",
        "title": title,
        "page_key": tname,
        "belong": "tables",
        "status": "draft",
        "aliases": [],
        "anchors": [tname],
        "sources": [f"database_schema:{database}.{tname}"],
        "created": today,
        "updated": today,
        "contract_version": "0.1",
        "databases": [database] if database else [],
        "recall": True,
    }
    ground_table = {
        "table": tname,
        "database": database,
        "description": compiled.get("description") or tname,
        "inactive": False,
        "primary_key": compiled.get("primary_key") or [],
        "grain": compiled.get("grain"),
        "name_anchors": compiled.get("name_anchors") or [],
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
        "L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。",
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
                    _dump(rel).rstrip(),
                    "```",
                    "",
                ]
            )
    return "\n".join(parts).rstrip() + "\n"


def render_enum_page(enum: dict[str, Any], today: str) -> str:
    key = str(enum["enum"])
    front = {
        "type": "enum",
        "title": key,
        "page_key": key,
        "belong": "enums",
        "status": "draft",
        "aliases": [],
        "anchors": [key],
        "sources": [f"database_profile:{enum.get('table')}.{enum.get('column')}"],
        "created": today,
        "updated": today,
        "contract_version": "0.1",
        "recall": True,
    }
    ground = {
        "enum": key,
        "fields": enum.get("fields") or [],
        "values": enum.get("values") or {},
        "ambiguous": False,
    }
    return (
        "---\n"
        + _dump(front).rstrip()
        + "\n---\n\n"
        + f"# {key}\n\n"
        + "L0 枚举候选：仅 profile 代码值，无代码 label。\n\n"
        + "## 取值\n\n"
        + "```ground:enum\n"
        + _dump(ground).rstrip()
        + "\n```\n"
    )


def _emit_clusters(clusters: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in clusters:
        row: dict[str, Any] = {
            "key": item["key"],
            "title": item.get("title") or item["key"],
        }
        if item.get("include"):
            row["include"] = item["include"]
        if item.get("confidence"):
            row["confidence"] = item["confidence"]
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
            "description": item.get("description") or "",
            "nullable": bool(item.get("nullable", True)),
        }
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
        lines.append(f"- [[{name}]]")
    lines.extend(["", "## enums", ""])
    for name in enums:
        lines.append(f"- [[enums/{name}]]")
    lines.append("")
    return "\n".join(lines)


def _log_markdown(model: dict[str, Any], today: str) -> str:
    tables = list(model.get("table_order") or (model.get("tables") or {}).keys())
    stats = model.get("llm_stats") or {}
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
    return (
        f"# L0 ingest log ({today})\n\n"
        f"source: tools.wiki_extract compile (database_schema)\n\n"
        f"touched tables ({len(tables)}): "
        + ", ".join(f"`{t}`" for t in tables)
        + "\n"
        + llm_line
        + "\nstatus: all pages draft; no published writes.\n"
    )


def _dump(data: Any) -> str:
    return yaml.safe_dump(
        data,
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
