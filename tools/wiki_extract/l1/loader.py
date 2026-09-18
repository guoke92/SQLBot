"""Recursively load and merge L1 intermediate YAML files."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from tools.wiki_extract.l1.schema import (
    KIND_CALIBERS_RULES,
    KIND_CONCEPTS,
    KIND_DISPLAY,
    KIND_METRICS,
    KIND_PATTERNS,
    KIND_PROCESSES,
    KIND_RELATIONS_DICTS,
    KIND_SCENARIOS,
    KIND_TABLE_ENHANCEMENTS,
    KIND_TRACE,
    IrError,
    classify_path,
    normalize_document,
)


@dataclass
class IntermediateBundle:
    files: list[str] = field(default_factory=list)
    table_enhancements: dict[str, dict[str, Any]] = field(default_factory=dict)
    processes: list[dict[str, Any]] = field(default_factory=list)
    calibers: list[dict[str, Any]] = field(default_factory=list)
    rules: list[dict[str, Any]] = field(default_factory=list)
    relations: list[dict[str, Any]] = field(default_factory=list)
    dict_labels: dict[str, dict[str, Any]] = field(default_factory=dict)
    scenarios: list[dict[str, Any]] = field(default_factory=list)
    traces: list[dict[str, Any]] = field(default_factory=list)
    concepts: list[dict[str, Any]] = field(default_factory=list)
    metrics: list[dict[str, Any]] = field(default_factory=list)
    display: list[dict[str, Any]] = field(default_factory=list)
    patterns: list[dict[str, Any]] = field(default_factory=list)
    domains: set[str] = field(default_factory=set)


def load_intermediate(root: Path) -> IntermediateBundle:
    root = root.resolve()
    if not root.exists():
        raise FileNotFoundError(f"l1 intermediate root missing: {root}")
    bundle = IntermediateBundle()
    for path in sorted(root.rglob("*.yaml")):
        if path.name.startswith("."):
            continue
        if "/.obsidian/" in path.as_posix():
            continue
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        if raw is None:
            continue
        kind = classify_path(path)
        if kind is None and not (isinstance(raw, dict) and raw.get("kind")):
            raise IrError(f"{path}: cannot classify file; set kind: or use a standard name")
        doc = normalize_document(path, raw)
        _ingest(bundle, doc)
        bundle.files.append(str(path.relative_to(root)))
    for path in sorted(root.rglob("*.yml")):
        if path.with_suffix(".yaml").exists():
            continue
        raise IrError(f"{path}: use .yaml (not .yml) for L1 intermediate files")
    return bundle


def _ingest(bundle: IntermediateBundle, doc: dict[str, Any]) -> None:
    domain = str(doc.get("domain") or "").strip()
    if domain:
        bundle.domains.add(domain)
    kind = doc["kind"]
    if kind == KIND_TABLE_ENHANCEMENTS:
        for table, body in (doc.get("tables") or {}).items():
            merged = bundle.table_enhancements.setdefault(str(table), {})
            _merge_table(merged, dict(body), domain)
    elif kind == KIND_PROCESSES:
        for item in doc.get("processes") or []:
            bundle.processes.append(_with_domain(item, domain))
    elif kind == KIND_CALIBERS_RULES:
        for item in doc.get("calibers") or []:
            bundle.calibers.append(_with_domain(item, domain))
        for item in doc.get("rules") or []:
            bundle.rules.append(_with_domain(item, domain))
    elif kind == KIND_RELATIONS_DICTS:
        for item in doc.get("confirmed_relations") or []:
            bundle.relations.append(_with_domain(item, domain))
        for key, body in (doc.get("dict_labels") or {}).items():
            packed = dict(body)
            packed.setdefault("dict", key)
            if domain and "domain" not in packed:
                packed["domain"] = domain
            existing = bundle.dict_labels.get(str(key))
            if existing:
                values = dict(existing.get("values") or {})
                values.update(packed.get("values") or {})
                packed["values"] = values
            bundle.dict_labels[str(key)] = packed
    elif kind == KIND_SCENARIOS:
        for item in doc.get("scenarios") or []:
            bundle.scenarios.append(_with_domain(item, domain))
    elif kind == KIND_TRACE:
        bundle.traces.append(doc)
        scenario = doc.get("scenario")
        if isinstance(scenario, dict) and scenario.get("scenario_key"):
            bundle.scenarios.append(_with_domain(scenario, domain))
    elif kind == KIND_CONCEPTS:
        source = str(doc.get("doc_source") or "").strip()
        for item in doc.get("concepts") or []:
            packed = _with_domain(item, domain)
            if source and not packed.get("doc_source"):
                packed["doc_source"] = source
            bundle.concepts.append(packed)
    elif kind == KIND_METRICS:
        for item in doc.get("metrics") or []:
            bundle.metrics.append(_with_domain(item, domain))
    elif kind == KIND_DISPLAY:
        source = str(doc.get("doc_source") or "").strip()
        for item in doc.get("items") or doc.get("display") or []:
            packed = _with_domain(item, domain)
            packed.setdefault("recall", False)
            if source and not packed.get("doc_source"):
                packed["doc_source"] = source
            bundle.display.append(packed)
    elif kind == KIND_PATTERNS:
        for item in doc.get("patterns") or []:
            bundle.patterns.append(_with_domain(item, domain))


def _with_domain(item: dict[str, Any], domain: str) -> dict[str, Any]:
    packed = dict(item)
    if domain and not packed.get("domain"):
        packed["domain"] = domain
    return packed


def _merge_table(dst: dict[str, Any], src: dict[str, Any], domain: str) -> None:
    if domain:
        domains = list(dst.get("domains") or [])
        if domain not in domains:
            domains.append(domain)
        dst["domains"] = domains
    if src.get("default_filter"):
        dst["default_filter"] = src["default_filter"]
    if src.get("grain"):
        dst["grain"] = src["grain"]
    groups = list(dst.get("written_with_groups") or [])
    groups.extend(list(src.get("written_with_groups") or []))
    if groups:
        dst["written_with_groups"] = groups
    if src.get("inactive") is not None:
        dst["inactive"] = src["inactive"]
