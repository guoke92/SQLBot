"""Structured package loader and conservative legacy-shape classifier."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any

import yaml
from pydantic import TypeAdapter, ValidationError

from apps.knowledge.importing.schema import KnowledgePackage, KnowledgePackageItem

_ITEM_ADAPTER = TypeAdapter(KnowledgePackageItem)
_KIND_ALIASES = {
    "term": "terminology",
    "terminology": "terminology",
    "k3": "terminology",
    "caliber": "caliber",
    "metric": "caliber",
    "semantic": "caliber",
    "k2": "caliber",
    "relation": "relation",
    "field_relation": "relation",
    "k1": "relation",
    "example": "example",
    "query": "example",
    "exemplar": "example",
    "k4": "example",
    "rule": "rule",
    "k5": "rule",
    "evidence": "evidence",
    "fact": "evidence",
}


def _status(value: Any) -> str:
    raw = str(value or "candidate").strip().lower()
    if raw in {"verified", "certified", "approved"}:
        return "verified"
    if raw in {"reviewed", "ready", "accepted"}:
        return "reviewed"
    if raw in {"rejected", "invalid"}:
        return "rejected"
    if raw in {"draft"}:
        return "draft"
    return "candidate"


def _field_ref(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        if "table_name" in value and "field_name" in value:
            return dict(value)
        if "resource" in value and "field" in value:
            return {
                "table_name": value.get("resource"),
                "field_name": value.get("field"),
                "database_name": value.get("database_name") or "",
            }
    if isinstance(value, str) and "." in value:
        table_name, field_name = value.rsplit(".", 1)
        return {"table_name": table_name, "field_name": field_name}
    raise ValueError(f"field reference must be table.field or object, got {value!r}")


def infer_item_kind(record: dict[str, Any], *, hint: str | None = None) -> str:
    explicit = str(record.get("kind") or hint or "").strip().lower()
    if explicit:
        kind = _KIND_ALIASES.get(explicit)
        if kind:
            return kind
        raise ValueError(f"unsupported knowledge kind={explicit!r}")
    if record.get("word") or record.get("term"):
        return "terminology"
    if record.get("contract_fragment") or (
        record.get("label") and record.get("requirements")
    ):
        return "caliber"
    if (record.get("left") and record.get("right")) or (
        record.get("source_field") and record.get("target_field")
    ):
        return "relation"
    if record.get("question") and (
        record.get("query")
        or record.get("sql")
        or record.get("description")
        or record.get("intended_contract")
        or record.get("intended_specification")
    ):
        return "example"
    if record.get("label") and (record.get("content") or record.get("rule")):
        return "rule"
    if record.get("fact_id") or {
        "subject",
        "predicate",
        "object",
    }.issubset(record):
        return "evidence"
    raise ValueError("knowledge kind is ambiguous; provide explicit kind")


def normalize_item(
    record: dict[str, Any], *, hint: str | None = None
) -> KnowledgePackageItem:
    kind = infer_item_kind(record, hint=hint)
    explicit_id = (
        record.get("item_id")
        or record.get("candidate_id")
        or record.get("relation_id")
        or record.get("fact_id")
    )
    if not explicit_id:
        identity_material = json.dumps(
            {"kind": kind, "record": record},
            ensure_ascii=False,
            sort_keys=True,
            default=str,
            separators=(",", ":"),
        )
        explicit_id = (
            f"auto-{kind}-{sha256(identity_material.encode()).hexdigest()[:16]}"
        )
    common = {
        "kind": kind,
        "item_id": str(explicit_id),
        "status": _status(record.get("status")),
        "confidence": float(record.get("confidence") or 0.5),
        "evidence_refs": list(record.get("evidence_refs") or []),
        "provenance": dict(record.get("provenance") or {}),
        "datasource_id": record.get("datasource_id") or record.get("ds_id"),
        "datasource_name": record.get("datasource_name"),
        "assistant_id": record.get("assistant_id"),
    }
    if kind == "terminology":
        payload = {
            **common,
            "word": record.get("word") or record.get("term"),
            "aliases": record.get("aliases") or record.get("other_words") or [],
            "description": record.get("description") or record.get("summary") or "",
            "enabled": record.get("enabled", True),
            "knowledge_meta": record.get("knowledge_meta") or {},
        }
    elif kind == "caliber":
        fragment = record.get("contract_fragment")
        if fragment is None and isinstance(record.get("requirements"), list):
            if all(isinstance(value, dict) for value in record["requirements"]):
                fragment = {"version": 3, "requirements": record["requirements"]}
        payload = {
            **common,
            "label": record.get("label"),
            "summary": record.get("summary") or "",
            "contract_fragment": fragment or {},
            "draft_definition": record.get("draft_definition")
            or {
                key: record[key]
                for key in (
                    "business_subject",
                    "grain",
                    "requirements",
                    "time_field",
                    "caveat",
                )
                if key in record
            },
            "field_targets": [
                _field_ref(value) for value in (record.get("field_targets") or [])
            ],
        }
    elif kind == "relation":
        raw_evidence = record.get("evidence") or {}
        evidence_refs = common["evidence_refs"]
        if isinstance(raw_evidence, list):
            evidence_refs = [*evidence_refs, *[str(value) for value in raw_evidence]]
            raw_evidence = {"source_locations": [str(value) for value in raw_evidence]}
        payload = {
            **common,
            "evidence_refs": evidence_refs,
            "left": _field_ref(record.get("left") or record.get("source_field")),
            "right": _field_ref(record.get("right") or record.get("target_field")),
            "relation_kind": record.get("relation_kind")
            or record.get("kind_name")
            or "EQUI_JOIN",
            "cardinality": record.get("cardinality"),
            "evidence": raw_evidence,
        }
    elif kind == "example":
        verification = record.get("verification") or {}
        legacy_status = str(record.get("status") or "")
        if "verified" in legacy_status and not verification:
            verification = {"executed": True, "passed": True}
        payload = {
            **common,
            "question": record.get("question"),
            "query": record.get("query")
            or record.get("sql")
            or record.get("description")
            or "",
            "intended_specification": record.get("intended_specification")
            or record.get("intended_contract")
            or {},
            "training_type": record.get("training_type") or "sql",
            "enabled": record.get("enabled", True),
            "verification": verification,
            "knowledge_meta": record.get("knowledge_meta") or {},
        }
    elif kind == "rule":
        payload = {
            **common,
            "label": record.get("label"),
            "content": record.get("content") or record.get("rule"),
        }
    else:
        payload = {
            **common,
            "subject": record.get("subject"),
            "predicate": record.get("predicate"),
            "value": record.get("value", record.get("object")),
            "evidence": record.get("evidence") or [],
        }
    return _ITEM_ADAPTER.validate_python(payload)


def _legacy_records(payload: dict[str, Any]) -> list[tuple[dict[str, Any], str | None]]:
    groups = {
        "k3_terminology_candidates": "terminology",
        "k2_caliber_candidates": "caliber",
        "k1_relation_candidates": "relation",
        "k4_exemplar_candidates": "example",
        "k5_rule_candidates": "rule",
        "facts": "evidence",
        "relations": "relation",
    }
    records: list[tuple[dict[str, Any], str | None]] = []
    for key, hint in groups.items():
        values = payload.get(key) or []
        if not isinstance(values, list):
            continue
        for value in values:
            if isinstance(value, dict):
                records.append((value, hint))
    if records:
        return records
    return [(payload, None)]


def _scan_records(
    records: list[tuple[dict[str, Any], str | None]],
) -> tuple[list[KnowledgePackageItem], list[str]]:
    items: list[KnowledgePackageItem] = []
    warnings: list[str] = []
    for index, (record, hint) in enumerate(records):
        try:
            items.append(normalize_item(record, hint=hint))
        except (ValueError, ValidationError, TypeError) as exc:
            identity = (
                record.get("item_id")
                or record.get("candidate_id")
                or record.get("fact_id")
                or f"index={index}"
            )
            warnings.append(f"{identity}: {exc}")
    return items, warnings


def scan_knowledge_payload(
    payload: dict[str, Any] | list[Any] | str,
    *,
    package_id: str = "scanned-package",
) -> KnowledgePackage:
    if isinstance(payload, str):
        try:
            decoded = yaml.safe_load(payload)
        except yaml.YAMLError as exc:
            raise ValueError(f"package document is not valid YAML/JSON: {exc}") from exc
        if not isinstance(decoded, dict | list):
            raise ValueError("package document root must be an object or list")
        payload = decoded
    if not isinstance(payload, dict | list):
        raise ValueError("package document root must be an object or list")
    if isinstance(payload, dict) and payload.get("schema_version") == "1.0":
        return KnowledgePackage.model_validate(payload)
    if isinstance(payload, list):
        records = [(value, None) for value in payload if isinstance(value, dict)]
    else:
        records = _legacy_records(payload)
    items, warnings = _scan_records(records)
    if not items:
        detail = "; ".join(warnings) or "no recognizable knowledge items"
        raise ValueError(detail)
    return KnowledgePackage(
        package_id=package_id,
        items=items,
        generator={"scanner_warnings": warnings},
    )


def _load_file(path: Path) -> Any:
    suffix = path.suffix.lower()
    text = path.read_text(encoding="utf-8")
    if suffix == ".jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    if suffix == ".json":
        return json.loads(text)
    if suffix in {".yaml", ".yml"}:
        return yaml.safe_load(text)
    raise ValueError(f"unsupported package file: {path}")


def scan_knowledge_documents(
    documents: list[tuple[str, str]],
    *,
    package_id: str | None = None,
) -> KnowledgePackage:
    """Aggregate selected files or a browser-selected directory into one package."""
    items: list[KnowledgePackageItem] = []
    sources: list[dict[str, Any]] = []
    warnings: list[str] = []
    canonical: list[tuple[str, KnowledgePackage]] = []
    manifest: dict[str, Any] = {}
    for name, content in sorted(documents, key=lambda value: value[0]):
        suffix = Path(name).suffix.lower()
        if suffix not in {".json", ".jsonl", ".yaml", ".yml"}:
            warnings.append(f"{name}: unsupported document type skipped")
            continue
        try:
            if suffix == ".jsonl":
                value: Any = [
                    json.loads(line) for line in content.splitlines() if line.strip()
                ]
            elif suffix == ".json":
                value = json.loads(content)
            else:
                value = yaml.safe_load(content)
            basename = Path(name).name
            if basename == "source-catalog.jsonl" and isinstance(value, list):
                for entry in value:
                    if not isinstance(entry, dict):
                        continue
                    sources.append(
                        {
                            "source_id": entry.get("source_id"),
                            "kind": entry.get("kind") or "unknown",
                            "uri": entry.get("path") or "",
                            "fingerprint": entry.get("sha256") or "",
                            "metadata": {
                                key: val
                                for key, val in entry.items()
                                if key not in {"source_id", "kind", "path", "sha256"}
                            },
                        }
                    )
                continue
            if basename in {"manifest.yaml", "manifest.yml", "manifest.json"}:
                if isinstance(value, dict):
                    manifest = {**manifest, **value}
                continue
            scanned = scan_knowledge_payload(value, package_id=Path(name).stem)
            if basename in {
                "knowledge-package.yaml",
                "knowledge-package.yml",
                "knowledge-package.json",
            }:
                canonical.append((name, scanned))
            else:
                items.extend(scanned.items)
            warnings.extend(
                f"{name}: {warning}"
                for warning in scanned.generator.get("scanner_warnings", [])
            )
        except (ValueError, ValidationError, TypeError, json.JSONDecodeError) as exc:
            warnings.append(f"{name}: {exc}")

    if canonical:
        if len(canonical) > 1:
            warnings.append(
                "multiple canonical packages selected; non-conflicting items were merged"
            )
        for name, package in canonical:
            sources.extend(source.model_dump(mode="json") for source in package.sources)
            warnings.extend(
                f"{name}: {warning}"
                for warning in package.generator.get("scanner_warnings", [])
            )

    # Canonical packages are maintained representations, so they win over
    # legacy siblings with the same stable item ID.
    ordered_items = [
        item for _name, package in canonical for item in package.items
    ] + items
    canonical_ids = {
        item.item_id for _name, package in canonical for item in package.items
    }
    deduplicated: dict[str, KnowledgePackageItem] = {}
    for item in ordered_items:
        previous = deduplicated.get(item.item_id)
        if previous is None:
            deduplicated[item.item_id] = item
        elif (
            item.item_id not in canonical_ids
            and previous.model_dump(mode="json") != item.model_dump(mode="json")
        ):
            # The canonical package is the maintained representation; legacy
            # siblings remain evidence but must not replace it silently.
            warnings.append(
                f"duplicate item_id={item.item_id} differs; kept the first selected representation"
            )
    if not deduplicated:
        raise ValueError("; ".join(warnings) or "no recognizable knowledge items")
    source_by_id: dict[str, dict[str, Any]] = {}
    for source in sources:
        source_id = str(source.get("source_id") or "")
        if source_id:
            source_by_id.setdefault(source_id, source)
    primary = canonical[0][1] if len(canonical) == 1 else None
    resolved_package_id = (
        primary.package_id
        if primary is not None
        else package_id or str(manifest.get("package_id") or "scanned-package")
    )
    generated_warnings = list(warnings)
    generator = dict(primary.generator) if primary is not None else {}
    generator["scanner_warnings"] = generated_warnings
    if manifest:
        generator.setdefault(
            "extraction_manifest",
            {
                key: value
                for key, value in manifest.items()
                if key not in {"package_id", "title", "purpose", "generated_at"}
            },
        )
    generated_at = manifest.get("generated_at") or (
        primary.generated_at if primary is not None else None
    )
    if generated_at is not None and not isinstance(generated_at, str):
        generated_at = generated_at.isoformat()
    return KnowledgePackage(
        package_id=resolved_package_id,
        title=str(manifest.get("title") or "")
        or (primary.title if primary is not None else "")
        or resolved_package_id,
        description=str(manifest.get("purpose") or "")
        or (primary.description if primary is not None else ""),
        generated_at=generated_at,
        defaults=primary.defaults if primary is not None else {},
        sources=list(source_by_id.values()),
        items=list(deduplicated.values()),
        generator=generator,
    )


def load_knowledge_package(path: str | Path) -> KnowledgePackage:
    source = Path(path)
    if source.is_file():
        return scan_knowledge_payload(_load_file(source), package_id=source.stem)
    if not source.is_dir():
        raise FileNotFoundError(source)
    documents = [
        (
            candidate.relative_to(source).as_posix(),
            candidate.read_text(encoding="utf-8"),
        )
        for candidate in source.rglob("*")
        if candidate.is_file()
        and candidate.suffix.lower() in {".json", ".jsonl", ".yaml", ".yml"}
    ]
    return scan_knowledge_documents(documents, package_id=source.name)
