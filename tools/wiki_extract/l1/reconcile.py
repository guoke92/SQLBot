"""Aggregate L1 IR onto L0 pages: inject structure, upgrade confirmed claims."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import yaml

from tools.wiki_extract.l1.emitter import emit_l1
from tools.wiki_extract.l1.loader import IntermediateBundle, load_intermediate
from tools.wiki_extract.l1.pages import load_l0_corpus
from tools.wiki_extract.l1.schema import dict_page_key, parse_code_path, physical_pair
from tools.wiki_extract.l1.validator import (
    ReviewItem,
    ValidationReport,
    catalog_columns,
    catalog_tables,
    validate_bundle,
)


def compile_l1(
    *,
    l0_dir: Path,
    intermediate_dir: Path,
    out_dir: Path,
    catalog: dict[str, Any] | None = None,
    code_root: Path | None = None,
    skip_code_check: bool = False,
    copy_untouched: bool = True,
) -> dict[str, Any]:
    l0_dir = l0_dir.resolve()
    intermediate_dir = intermediate_dir.resolve()
    out_dir = out_dir.resolve()
    catalog = catalog or _load_catalog(l0_dir)
    bundle = load_intermediate(intermediate_dir)
    report = validate_bundle(
        bundle, catalog, code_root=code_root, skip_code_check=skip_code_check
    )
    fatal_targets = {item.target for item in report.errors}
    model = load_l0_corpus(l0_dir)
    enhance_model(model, bundle, catalog, report, fatal_targets)
    reviews = _reviews_from(report, bundle)
    model["reviews"] = reviews
    model["database"] = catalog.get("database") or model.get("database")
    model["_catalog"] = catalog
    model["l1_files"] = bundle.files
    model["domains"] = sorted(bundle.domains)
    stats = emit_l1(
        model,
        out_dir,
        l0_dir=l0_dir,
        copy_untouched=copy_untouched,
        extra_reviews=reviews,
    )
    copy_raw_intermediate(intermediate_dir, out_dir)
    catalog_src = l0_dir / "_raw" / "catalog.yaml"
    if catalog_src.exists():
        dest = out_dir / "_raw" / "catalog.yaml"
        if not dest.exists():
            shutil.copy2(catalog_src, dest)
    stats["files"] = len(bundle.files)
    stats["errors"] = len(report.errors)
    stats["warnings"] = len(report.warnings)
    return stats


def enhance_model(
    model: dict[str, Any],
    bundle: IntermediateBundle,
    catalog: dict[str, Any],
    report: ValidationReport,
    fatal_targets: set[str],
) -> dict[str, Any]:
    tables = model.setdefault("tables", {})
    dicts = model.setdefault("dicts", {})
    catalog_map = catalog_tables(catalog)

    for table, body in bundle.table_enhancements.items():
        if table not in catalog_map:
            continue
        compiled = tables.setdefault(table, {"table": table, "fields": [], "relations": []})
        _enhance_table(compiled, body, catalog_columns(catalog_map[table]), fatal_targets)

    upgraded_tables: set[str] = set(bundle.table_enhancements)
    for rel in bundle.relations:
        if _is_fatal(fatal_targets, f"{rel.get('left')}={rel.get('right')}"):
            continue
        if not parse_code_path(str(rel.get("evidence") or "")):
            report.add(
                "JOIN_NO_CODE_PATH",
                f"{rel.get('left')}={rel.get('right')}",
                "relation lacks code_path; left proposed",
                evidence=str(rel.get("evidence") or ""),
                severity="warning",
            )
            continue
        host = _upgrade_or_insert_relation(tables, rel, report)
        if host:
            upgraded_tables.add(host)

    for key, body in bundle.dict_labels.items():
        if key in fatal_targets:
            continue
        page_key = dict_page_key(str(body.get("table") or ""), str(body.get("column") or ""), body.get("dict") or key)
        item = dicts.get(page_key) or dicts.get(key)
        if item is None:
            item = {
                "dict": page_key,
                "table": body.get("table"),
                "column": body.get("column"),
                "fields": [f"{body.get('table')}.{body.get('column')}"],
                "values": {},
            }
            dicts[page_key] = item
        _upgrade_dict(item, body, fatal_targets)

    model["processes"] = [
        item for item in bundle.processes if str(item.get("process_key") or "") not in fatal_targets
    ]
    model["calibers"] = [
        item for item in bundle.calibers if str(item.get("caliber_key") or "") not in fatal_targets
    ]
    model["rules"] = [
        item for item in bundle.rules if str(item.get("rule_key") or "") not in fatal_targets
    ]
    model["concepts"] = [
        item for item in bundle.concepts if str(item.get("concept_key") or "") not in fatal_targets
    ]
    model["metrics"] = [
        item for item in bundle.metrics if str(item.get("metric_key") or "") not in fatal_targets
    ]
    model["scenarios"] = bundle.scenarios
    model["patterns"] = bundle.patterns
    model["display"] = bundle.display
    model["enhanced_tables"] = sorted(upgraded_tables)
    model["enhanced_dicts"] = sorted(
        dict_page_key(str(b.get("table") or ""), str(b.get("column") or ""), b.get("dict") or k)
        for k, b in bundle.dict_labels.items()
    )
    for compiled in tables.values():
        _strip_clusters(compiled)
    return model


def _strip_clusters(compiled: dict[str, Any]) -> None:
    compiled.pop("clusters", None)
    for field in compiled.get("fields") or []:
        if isinstance(field, dict):
            field.pop("cluster", None)


def _enhance_table(
    compiled: dict[str, Any],
    body: dict[str, Any],
    columns: set[str],
    fatal_targets: set[str],
) -> None:
    table = str(compiled.get("table") or "")
    if f"tables.{table}" in fatal_targets:
        return
    filt = body.get("default_filter")
    if isinstance(filt, dict) and filt.get("predicate"):
        compiled["default_filter"] = {
            "predicate": filt["predicate"],
            "trust": "confirmed" if parse_code_path(str(filt.get("evidence") or "")) else "proposed",
            "evidence": filt.get("evidence"),
        }
    if body.get("grain"):
        compiled["grain"] = body["grain"]
    if body.get("inactive") is not None:
        compiled["inactive"] = bool(body["inactive"])

    compiled.pop("clusters", None)
    fields_by_name = {
        str(f.get("name")): f for f in compiled.get("fields") or [] if isinstance(f, dict)
    }
    for field in fields_by_name.values():
        field.pop("cluster", None)

    for group in body.get("written_with_groups") or []:
        names = [str(n) for n in (group.get("fields") or []) if str(n) in columns]
        if len(names) < 2:
            continue
        evidence = group.get("evidence")
        for name in names:
            field = fields_by_name.get(name)
            if field is None:
                continue
            companions = [n for n in names if n != name]
            merged = list(field.get("written_with") or [])
            for other in companions:
                if other not in merged:
                    merged.append(other)
            field["written_with"] = merged
            if parse_code_path(str(evidence or "")):
                field["written_with_evidence"] = evidence


def _upgrade_or_insert_relation(
    tables: dict[str, Any], rel: dict[str, Any], report: ValidationReport
) -> str | None:
    left = str(rel.get("left") or "")
    right = str(rel.get("right") or "")
    fk_table, _ = physical_pair(right)
    host = tables.get(fk_table)
    if host is None:
        left_table, _ = physical_pair(left)
        host = tables.get(left_table)
        fk_table = left_table
    if host is None:
        report.add("JOIN_HOST_MISSING", f"{left}={right}", "neither endpoint table is in L0 pages")
        return None
    relations = list(host.get("relations") or [])
    match = _find_relation(relations, left, right)
    payload = {
        "type": rel.get("type") or "EQUI_JOIN",
        "left": left,
        "right": right,
        "cardinality": rel.get("cardinality") or "one_to_many",
        "trust": "confirmed",
        "authenticity": "likely",
        "evidence": rel.get("evidence"),
        "join_role": rel.get("join_role") or "identity",
        "priority": rel.get("priority") or "primary",
        "source": "l1_code",
    }
    if rel.get("note"):
        payload["authenticity_note"] = str(rel["note"])[:240]
    if rel.get("cast"):
        payload["cast"] = rel["cast"]
    if match is None:
        relations.append(payload)
        confirmed_rel = relations[-1]
    else:
        match.update(payload)
        confirmed_rel = match
    host["relations"] = relations
    _maybe_review_conflicting_id_edge(relations, confirmed_rel, report)
    _touch_related(tables, left, right)
    return fk_table


def _maybe_review_conflicting_id_edge(
    relations: list[dict[str, Any]], confirmed: dict[str, Any], report: ValidationReport
) -> None:
    """Same FK column, different other end → L0 proposed is a fake pairing."""
    confirmed_ends = {
        str(confirmed.get("left") or "").strip(),
        str(confirmed.get("right") or "").strip(),
    }
    confirmed_ends.discard("")
    for rel in relations:
        if rel is confirmed:
            continue
        if str(rel.get("trust") or "") in {"confirmed", "disputed"}:
            continue
        rel_ends = {
            str(rel.get("left") or "").strip(),
            str(rel.get("right") or "").strip(),
        }
        rel_ends.discard("")
        shared = confirmed_ends & rel_ends
        if len(shared) != 1:
            continue
        rel["trust"] = "disputed"
        rel["sides"] = [
            {
                "source": str(confirmed.get("source") or "l1_code"),
                "left": confirmed.get("left"),
                "right": confirmed.get("right"),
                "trust": "confirmed",
            },
            {
                "source": str(rel.get("source") or "l0"),
                "left": rel.get("left"),
                "right": rel.get("right"),
                "trust": "proposed",
            },
        ]
        report.add(
            "JOIN_CONFLICT",
            f"{rel.get('left')}={rel.get('right')}",
            f"L0 proposed edge conflicts with confirmed {confirmed.get('left')}={confirmed.get('right')}",
            evidence=str(confirmed.get("evidence") or ""),
            severity="warning",
        )


def _find_relation(
    relations: list[dict[str, Any]], left: str, right: str
) -> dict[str, Any] | None:
    pair = {left, right}
    for rel in relations:
        if {str(rel.get("left") or ""), str(rel.get("right") or "")} == pair:
            return rel
    return None


def _touch_related(tables: dict[str, Any], left: str, right: str) -> None:
    lt, _ = physical_pair(left)
    rt, _ = physical_pair(right)
    for name, other in ((lt, rt), (rt, lt)):
        compiled = tables.get(name)
        if not compiled or not other:
            continue
        related = list(compiled.get("related_tables") or [])
        if other not in related:
            related.append(other)
        compiled["related_tables"] = related


def _upgrade_dict(item: dict[str, Any], body: dict[str, Any], fatal_targets: set[str]) -> None:
    values = dict(item.get("values") or {})
    for code, meta in (body.get("values") or {}).items():
        if not isinstance(meta, dict):
            continue
        if f"{body.get('dict') or item.get('dict')}.{code}" in fatal_targets:
            continue
        row = dict(values.get(code) or {})
        if isinstance(values.get(code), dict):
            row = dict(values[code])
        row["label"] = meta.get("label")
        if parse_code_path(str(meta.get("evidence") or "")):
            row["trust"] = "confirmed"
            row["evidence"] = meta.get("evidence")
        else:
            row.setdefault("trust", "proposed")
        values[str(code)] = row
    item["values"] = values
    item["l1_confirmed"] = True


def _is_fatal(fatal: set[str], target: str) -> bool:
    return target in fatal or any(target.endswith(item) or item.endswith(target) for item in fatal)


def _reviews_from(report: ValidationReport, bundle: IntermediateBundle) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for index, item in enumerate(report.errors + report.warnings, start=1):
        packed = _review_dict(item)
        packed["id"] = f"rv_l1_{index:04d}"
        items.append(packed)
    for concept in bundle.concepts:
        if not parse_code_path(str(concept.get("evidence") or "")):
            items.append(
                {
                    "id": f"rv_l1_doc_{concept.get('concept_key')}",
                    "kind": "DOC_UNBRIDGED",
                    "target": f"concepts/{concept.get('concept_key')}",
                    "message": "document concept has no code_path; keep proposed / REVIEW",
                    "evidence": str(concept.get("evidence") or ""),
                    "severity": "warning",
                }
            )
    return items


def _review_dict(item: ReviewItem) -> dict[str, Any]:
    return {
        "kind": item.kind,
        "target": item.target,
        "message": item.message,
        "evidence": item.evidence,
        "severity": item.severity,
    }


def _load_catalog(l0_dir: Path) -> dict[str, Any]:
    path = l0_dir / "_raw" / "catalog.yaml"
    if not path.exists():
        raise FileNotFoundError(f"L0 catalog missing: {path}")
    loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(loaded, dict):
        raise ValueError(f"catalog is not a mapping: {path}")
    return loaded


def copy_raw_intermediate(src: Path, out_dir: Path) -> None:
    dest = out_dir / "_raw" / "l1_intermediate"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
