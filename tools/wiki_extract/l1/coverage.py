"""Mechanical L1 walk gaps: catalog tables / dicts / FK-like columns vs IR."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from tools.wiki_extract.l1.loader import IntermediateBundle, load_intermediate

_SKIP_ID_COLS = {
    "id",
    "create_by",
    "update_by",
    "create_user",
    "update_user",
    "organization_id",
}


def catalog_tables(catalog: dict[str, Any]) -> dict[str, dict[str, Any]]:
    tables = catalog.get("tables") if isinstance(catalog, dict) else None
    return tables if isinstance(tables, dict) else {}


def catalog_columns(table_meta: dict[str, Any]) -> dict[str, Any]:
    columns = table_meta.get("columns") if isinstance(table_meta, dict) else None
    return columns if isinstance(columns, dict) else {}


def fk_like_columns(columns: dict[str, Any]) -> list[str]:
    out: list[str] = []
    for name in columns:
        if name in _SKIP_ID_COLS:
            continue
        if name.startswith("ref_") or name.endswith("_id"):
            out.append(str(name))
    return out


def coverage_report(
    *,
    l0_dir: Path,
    intermediate_dir: Path | None = None,
    prefix: str = "cust",
    req_index: Path | None = None,
) -> dict[str, Any]:
    l0_dir = l0_dir.resolve()
    catalog_path = l0_dir / "_raw" / "catalog.yaml"
    catalog = yaml.safe_load(catalog_path.read_text(encoding="utf-8")) or {}
    ir_root = (intermediate_dir or (l0_dir / "_raw" / "l1_intermediate")).resolve()
    bundle: IntermediateBundle = load_intermediate(ir_root)

    prefix = prefix.strip()
    tables = {
        name: meta
        for name, meta in catalog_tables(catalog).items()
        if str(name).startswith(prefix)
    }
    enhanced = set(bundle.table_enhancements)
    missing_tables = sorted(name for name in tables if name not in enhanced)

    labeled = set(bundle.dict_labels)
    unlabeled_dicts: list[str] = []
    dict_dir = l0_dir / "dicts"
    if dict_dir.is_dir():
        for path in sorted(dict_dir.glob("*.md")):
            key = path.stem
            host = key.split("__", 1)[0]
            if host in enhanced and key not in labeled and not key.endswith("__enable"):
                unlabeled_dicts.append(key)

    confirmed_rights = {
        str(item.get("right") or "")
        for item in bundle.relations
        if isinstance(item, dict)
    }
    unconfirmed_fks: list[str] = []
    for table, meta in tables.items():
        if table not in enhanced:
            continue
        for col in fk_like_columns(catalog_columns(meta)):
            endpoint = f"{table}.{col}"
            if endpoint not in confirmed_rights:
                unconfirmed_fks.append(endpoint)

    req_files: list[str] = []
    if req_index is not None and req_index.exists():
        concepts = req_index / "concepts"
        if concepts.is_dir():
            req_files = sorted(p.name for p in concepts.glob("*.md"))

    return {
        "prefix": prefix,
        "catalog_tables": sorted(tables),
        "enhanced_tables": sorted(enhanced & set(tables)),
        "missing_tables": missing_tables,
        "unlabeled_dicts_on_enhanced": unlabeled_dicts,
        "unconfirmed_fk_like_on_enhanced": unconfirmed_fks,
        "req_index_concept_files": req_files,
        "req_index_count": len(req_files),
        "counts": {
            "catalog": len(tables),
            "enhanced": len(enhanced & set(tables)),
            "missing_tables": len(missing_tables),
            "unlabeled_dicts": len(unlabeled_dicts),
            "unconfirmed_fks": len(unconfirmed_fks),
        },
    }


def format_coverage(report: dict[str, Any]) -> str:
    counts = report.get("counts") or {}
    lines = [
        f"L1 coverage prefix={report.get('prefix')} "
        f"catalog={counts.get('catalog')} enhanced={counts.get('enhanced')} "
        f"missing_tables={counts.get('missing_tables')} "
        f"unlabeled_dicts={counts.get('unlabeled_dicts')} "
        f"unconfirmed_fks={counts.get('unconfirmed_fks')}",
        "",
        "## missing_tables",
    ]
    missing = report.get("missing_tables") or []
    lines.extend(f"- {name}" for name in missing) if missing else lines.append("- (none)")
    lines.append("")
    lines.append("## unlabeled_dicts_on_enhanced")
    unlabeled = report.get("unlabeled_dicts_on_enhanced") or []
    lines.extend(f"- {name}" for name in unlabeled[:40])
    if len(unlabeled) > 40:
        lines.append(f"- … {len(unlabeled) - 40} more")
    if not unlabeled:
        lines.append("- (none)")
    lines.append("")
    lines.append("## unconfirmed_fk_like_on_enhanced")
    fks = report.get("unconfirmed_fk_like_on_enhanced") or []
    lines.extend(f"- {name}" for name in fks)
    if not fks:
        lines.append("- (none)")
    if report.get("req_index_count"):
        lines.append("")
        lines.append(
            f"## req-index concepts: {report['req_index_count']} files "
            "(walk domain-tagged pages; later version + current code wins)"
        )
    lines.append("")
    return "\n".join(lines)
