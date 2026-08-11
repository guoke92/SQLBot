"""Stable natural keys for Conversation knowledge assets."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_fragment_fingerprint(fragment: dict[str, Any]) -> str:
    """Fingerprint the complete typed v3 clause semantics."""
    from apps.chat.query_specification import (
        parse_specification_fragment,
        specification_semantic_material,
    )

    specification = parse_specification_fragment(fragment)
    material = specification_semantic_material(specification)
    blob = json.dumps(
        material,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
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
        "fragment": canonical_fragment_fingerprint(fragment),
    }
    raw = json.dumps(
        material, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def fragments_equivalent(a: dict[str, Any], b: dict[str, Any]) -> bool:
    """Equivalence ignores turn-local evidence and presentation metadata.

    Legacy or malformed rows (pre-v3 flat slots, empty fragments) are treated as
    non-equivalent instead of aborting admit/merge — newer typed material wins.
    """
    try:
        return canonical_fragment_fingerprint(a) == canonical_fragment_fingerprint(b)
    except (TypeError, ValueError):
        return False


def looks_ephemeral(value: str) -> bool:
    """True for turn-local literals (order ids, long hex) that must not persist."""
    text = value.strip()
    if len(text) >= 16 and text.replace("-", "").isalnum():
        return True
    if text.isdigit() and len(text) >= 8:
        return True
    return False


def predicate_looks_ephemeral(req: dict[str, Any]) -> bool:
    """True when any predicate literal in *req* looks turn-local."""
    candidates: list[Any] = []
    for key in ("values", "value"):
        raw = req.get(key)
        if raw is None:
            continue
        if isinstance(raw, list | tuple):
            candidates.extend(raw)
        else:
            candidates.append(raw)
    return any(isinstance(v, str) and looks_ephemeral(v) for v in candidates)
