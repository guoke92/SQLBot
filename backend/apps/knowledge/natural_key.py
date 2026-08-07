"""Stable natural keys for Conversation knowledge assets."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def clause_of(req: dict[str, Any]) -> str:
    """Canonical clause name (QueryContract uses ``clause``)."""
    return str(req.get("clause") or req.get("clause_type") or req.get("type") or "")


def _normalize_value(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, list):
        return [_normalize_value(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _normalize_value(v) for k, v in sorted(value.items())}
    return str(value)


def _slot_parts(fragment: dict[str, Any]) -> list[dict[str, Any]]:
    requirements = fragment.get("requirements") or fragment.get("slots") or []
    if isinstance(fragment.get("contract"), dict):
        requirements = fragment["contract"].get("requirements") or requirements
    parts: list[dict[str, Any]] = []
    for req in requirements if isinstance(requirements, list) else []:
        if not isinstance(req, dict):
            continue
        field = ""
        ref = req.get("field") or req.get("output") or {}
        if isinstance(ref, dict):
            field = f"{ref.get('resource', '')}.{ref.get('field', '')}"
        elif isinstance(ref, str):
            field = ref
        op = req.get("operation") or req.get("operator") or ""
        value = req.get("value", req.get("values"))
        parts.append(
            {
                "clause": clause_of(req),
                "field": field,
                "op": str(op),
                "value": _normalize_value(value),
            }
        )
    parts.sort(
        key=lambda item: (
            item["clause"],
            item["field"],
            item["op"],
            json.dumps(item["value"], sort_keys=True, default=str),
        )
    )
    return parts


def canonical_slot_fingerprint(fragment: dict[str, Any]) -> str:
    """Fingerprint slots including normalized values (same slot ≠ same caliber)."""
    parts = _slot_parts(fragment)
    blob = json.dumps(parts, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:32]


def caliber_natural_key(
    *,
    oid: int,
    datasource_id: int | None,
    field_targets: list[Any],
    fragment: dict[str, Any],
) -> str:
    field_ids: list[int] = []
    field_names: list[str] = []
    for target in field_targets or []:
        if isinstance(target, dict):
            if target.get("field_id") is not None:
                field_ids.append(int(target["field_id"]))
            name = f"{target.get('table_name') or ''}.{target.get('field_name') or ''}"
            if name.strip("."):
                field_names.append(name.casefold())
        elif hasattr(target, "field_id") and target.field_id is not None:
            field_ids.append(int(target.field_id))
    field_ids = sorted(set(field_ids))
    field_names = sorted(set(field_names))
    material = {
        "oid": oid,
        "ds": datasource_id,
        "fields": field_ids,
        "field_names": field_names,
        "slots": canonical_slot_fingerprint(fragment),
    }
    raw = json.dumps(material, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def fragments_equivalent(a: dict[str, Any], b: dict[str, Any]) -> bool:
    """Equivalence ignores evidence_refs / slot_id / clause_type aliases — fingerprint SoT."""
    return canonical_slot_fingerprint(a) == canonical_slot_fingerprint(b)
