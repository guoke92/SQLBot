"""Discrete L1 intermediate YAML kinds and load-time normalization.

Coding agents write one kind per file. The platform never reads wiki Markdown
as IR. Unknown top-level keys are kept (forward compatible) but required
fields are asserted here so step 2 fails closed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

KIND_TABLE_ENHANCEMENTS = "table_enhancements"
KIND_PROCESSES = "processes"
KIND_CALIBERS_RULES = "calibers_rules"
KIND_RELATIONS_DICTS = "relations_dicts"
KIND_SCENARIOS = "scenarios"
KIND_TRACE = "trace"
KIND_CONCEPTS = "concepts"
KIND_METRICS = "metrics"
KIND_DISPLAY = "display"
KIND_PATTERNS = "patterns"

CODE_KINDS = {
    KIND_TABLE_ENHANCEMENTS,
    KIND_PROCESSES,
    KIND_CALIBERS_RULES,
    KIND_RELATIONS_DICTS,
    KIND_SCENARIOS,
    KIND_TRACE,
    KIND_PATTERNS,
}
DOC_KINDS = {KIND_CONCEPTS, KIND_METRICS, KIND_DISPLAY}
ALL_KINDS = CODE_KINDS | DOC_KINDS

_FILENAME_KIND = {
    "table_enhancements.yaml": KIND_TABLE_ENHANCEMENTS,
    "processes.yaml": KIND_PROCESSES,
    "calibers_rules.yaml": KIND_CALIBERS_RULES,
    "relations_dicts.yaml": KIND_RELATIONS_DICTS,
    "scenarios.yaml": KIND_SCENARIOS,
    "patterns.yaml": KIND_PATTERNS,
}

EVIDENCE_PREFIXES = (
    "code_path:",
    "database_schema:",
    "database_profile:",
    "document_claim:",
)

PAGE_TYPES = (
    "table",
    "dict",
    "concept",
    "process",
    "caliber",
    "metric",
    "rule",
    "scenario",
    "pattern",
)


class IrError(ValueError):
    """A single intermediate file failed schema checks."""


def classify_path(path: Path) -> str | None:
    name = path.name
    if name in _FILENAME_KIND:
        return _FILENAME_KIND[name]
    if name.endswith(".trace.yaml") or name.endswith(".trace.yml"):
        return KIND_TRACE
    if name.endswith("_concepts.yaml") or name.endswith("_concepts.yml"):
        return KIND_CONCEPTS
    if name.endswith("_metrics.yaml") or name.endswith("_metrics.yml"):
        return KIND_METRICS
    if name.endswith("_display.yaml") or name.endswith("_display.yml"):
        return KIND_DISPLAY
    return None


def normalize_document(path: Path, raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise IrError(f"{path}: root must be a mapping")
    kind = str(raw.get("kind") or classify_path(path) or "").strip()
    if kind not in ALL_KINDS:
        raise IrError(f"{path}: unknown kind {kind!r}")
    doc = dict(raw)
    doc["kind"] = kind
    doc["_path"] = str(path)
    _require_kind(path, doc, kind)
    return doc


def _require_kind(path: Path, doc: dict[str, Any], kind: str) -> None:
    if kind == KIND_TABLE_ENHANCEMENTS:
        _require_map(path, doc, "tables")
        for table, body in (doc.get("tables") or {}).items():
            if not isinstance(body, dict):
                raise IrError(f"{path}: tables.{table} must be a mapping")
            filt = body.get("default_filter")
            if filt is not None:
                if not isinstance(filt, dict) or not str(filt.get("predicate") or "").strip():
                    raise IrError(f"{path}: tables.{table}.default_filter.predicate required")
                _check_evidence(path, filt.get("evidence"))
            for group in body.get("written_with_groups") or []:
                if not isinstance(group, dict) or not group.get("fields"):
                    raise IrError(f"{path}: written_with_groups need fields")
                _check_evidence(path, group.get("evidence"))
    elif kind == KIND_PROCESSES:
        items = _require_list(path, doc, "processes")
        for item in items:
            for key in ("process_key", "table", "field"):
                if not str(item.get(key) or "").strip():
                    raise IrError(f"{path}: process missing {key}")
            if not item.get("stages"):
                raise IrError(f"{path}: process {item.get('process_key')} needs stages")
    elif kind == KIND_CALIBERS_RULES:
        for item in doc.get("calibers") or []:
            for key in ("caliber_key", "predicate"):
                if not str(item.get(key) or "").strip():
                    raise IrError(f"{path}: caliber missing {key}")
            if not item.get("field_targets"):
                raise IrError(f"{path}: caliber {item.get('caliber_key')} needs field_targets")
            _check_evidence(path, item.get("evidence"))
        for item in doc.get("rules") or []:
            for key in ("rule_key", "content", "impact"):
                if not str(item.get(key) or "").strip():
                    raise IrError(f"{path}: rule missing {key}")
            if not item.get("field_targets"):
                raise IrError(f"{path}: rule {item.get('rule_key')} needs field_targets")
            _check_evidence(path, item.get("evidence"))
    elif kind == KIND_RELATIONS_DICTS:
        for rel in doc.get("confirmed_relations") or []:
            for key in ("left", "right"):
                if not str(rel.get(key) or "").strip():
                    raise IrError(f"{path}: relation missing {key}")
            _check_evidence(path, rel.get("evidence"))
        labels = doc.get("dict_labels") or {}
        if labels and not isinstance(labels, dict):
            raise IrError(f"{path}: dict_labels must be a mapping")
        for key, body in labels.items():
            if not isinstance(body, dict):
                raise IrError(f"{path}: dict_labels.{key} must be a mapping")
            if not body.get("table") or not body.get("column"):
                raise IrError(f"{path}: dict_labels.{key} needs table and column")
            values = body.get("values") or {}
            if not isinstance(values, dict) or not values:
                raise IrError(f"{path}: dict_labels.{key} needs values")
            for code, meta in values.items():
                if not isinstance(meta, dict) or not meta.get("label"):
                    raise IrError(f"{path}: dict_labels.{key}.{code} needs label")
                _check_evidence(path, meta.get("evidence"))
    elif kind == KIND_SCENARIOS:
        items = _require_list(path, doc, "scenarios")
        for item in items:
            if not str(item.get("scenario_key") or "").strip():
                raise IrError(f"{path}: scenario missing scenario_key")
            if not item.get("hubs"):
                raise IrError(f"{path}: scenario {item.get('scenario_key')} needs hubs")
    elif kind == KIND_TRACE:
        if not str(doc.get("trace_key") or path.stem or "").strip():
            raise IrError(f"{path}: trace missing trace_key")
    elif kind == KIND_CONCEPTS:
        items = _require_list(path, doc, "concepts")
        for item in items:
            if not str(item.get("concept_key") or "").strip():
                raise IrError(f"{path}: concept missing concept_key")
            if not str(item.get("maps_to") or "").strip():
                raise IrError(f"{path}: concept {item.get('concept_key')} needs maps_to")
            _check_evidence(path, item.get("evidence"), allow_document=True)
    elif kind == KIND_METRICS:
        items = _require_list(path, doc, "metrics")
        for item in items:
            for key in ("metric_key", "caliber", "grain_table", "aggregation", "field"):
                if not str(item.get(key) or "").strip():
                    raise IrError(f"{path}: metric missing {key}")
            _check_evidence(path, item.get("evidence"))
    elif kind == KIND_DISPLAY:
        items = doc.get("items") or doc.get("display") or []
        if not isinstance(items, list):
            raise IrError(f"{path}: display items must be a list")
        for item in items:
            if not isinstance(item, dict) or not str(item.get("title") or "").strip():
                raise IrError(f"{path}: display item needs title")
    elif kind == KIND_PATTERNS:
        items = _require_list(path, doc, "patterns")
        for item in items:
            for key in ("pattern_key", "question", "sql"):
                if not str(item.get(key) or "").strip():
                    raise IrError(f"{path}: pattern missing {key}")


def _require_map(path: Path, doc: dict[str, Any], key: str) -> dict[str, Any]:
    value = doc.get(key)
    if not isinstance(value, dict) or not value:
        raise IrError(f"{path}: {key} must be a non-empty mapping")
    return value


def _require_list(path: Path, doc: dict[str, Any], key: str) -> list[Any]:
    value = doc.get(key)
    if not isinstance(value, list) or not value:
        raise IrError(f"{path}: {key} must be a non-empty list")
    for item in value:
        if not isinstance(item, dict):
            raise IrError(f"{path}: {key} items must be mappings")
    return value


def _check_evidence(
    path: Path, evidence: Any, *, allow_document: bool = False
) -> None:
    if evidence is None or evidence == "":
        return
    text = str(evidence).strip()
    if not text.startswith(EVIDENCE_PREFIXES):
        raise IrError(f"{path}: illegal evidence {text!r}")
    if text.startswith("code_path:") or text.startswith("database_"):
        return
    if text.startswith("document_claim:") and not allow_document:
        # code IR may cite documents, but confirmed upgrades still need code_path
        return


def parse_code_path(evidence: str) -> tuple[str, int | None] | None:
    text = str(evidence or "").strip()
    if not text.startswith("code_path:"):
        return None
    rest = text[len("code_path:") :].strip()
    if not rest:
        return None
    if ":" in rest:
        file_part, maybe_line = rest.rsplit(":", 1)
        if maybe_line.isdigit():
            return file_part.strip(), int(maybe_line)
    return rest, None


def physical_pair(endpoint: str) -> tuple[str, str]:
    text = str(endpoint or "").strip()
    if "." not in text:
        return text, ""
    table, column = text.split(".", 1)
    return table.strip(), column.strip()


def dict_page_key(table: str, column: str, explicit: str | None = None) -> str:
    if explicit:
        return str(explicit).strip()
    return f"{table}__{column}"
