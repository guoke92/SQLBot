"""Dictionary catalog eligibility and schema identity."""

from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from apps.datasource.models.datasource import CoreField, CoreTable


_STRING_TYPES = ("char", "text", "string", "varchar", "nvarchar", "nchar", "enum")


def is_string_field_type(field_type: str) -> bool:
    normalized = (field_type or "").strip().lower()
    return any(normalized.startswith(prefix) for prefix in _STRING_TYPES)


def schema_fingerprint(table: CoreTable | Any, field: CoreField | Any) -> str:
    """Identify the physical extraction target, excluding descriptive metadata."""
    from apps.datasource.models.datasource import table_identity_key

    db_name, table_name = table_identity_key(table)
    raw = "\x1f".join(
        [
            db_name,
            table_name,
            field.field_name or "",
            field.field_type or "",
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
