"""Schema text for ranking vectors vs NLQ prompts.

Architecture
------------
Two consumers share one renderer but **different purposes**:

* ``SchemaTextPurpose.RANK`` — table / datasource *embedding* text.
  Indexes structural identity only: table name, comments, field name/type
  and field comments. Profile stats, generation counters, indexes, and
  confirmed joins are intentionally omitted so cosine ranking tracks the
  user's language, not mining churn.

* ``SchemaTextPurpose.PROMPT`` — schema injected into the LLM after tables
  are selected. Adds catalog cost signals, index summary, and **READY**
  profile bits (incl. low-ndv topk). STALE/PROFILING/FAILED never inject
  stats. Confirmed relations are assembled by the caller
  (``get_table_schema``) so they stay a post-selection gate.

Embedding refresh follows **RANK fingerprint** changes (catalog sync,
comment edits, checked toggles). Profile publish and relation decisions
do **not** re-embed schema vectors — they only affect PROMPT / Brief.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from sqlmodel import Session

from apps.datasource.models.datasource import CoreField, CoreTable
from apps.datasource.profiling.fingerprint import format_profile_field_bits
from apps.datasource.profiling.models import ProfileStatus


class SchemaTextPurpose(str, Enum):
    RANK = "rank"
    PROMPT = "prompt"


def profile_prompt_allowed(table: CoreTable) -> bool:
    """PROMPT may inject snapshot bits only for a published READY generation."""
    return (
        (table.profile_status or "") == ProfileStatus.READY.value
        and int(table.active_profile_generation or 0) > 0
    )


def render_table_schema_text(
    session: Session,
    *,
    table: CoreTable,
    fields: list[CoreField],
    purpose: SchemaTextPurpose | str = SchemaTextPurpose.PROMPT,
    table_label: str | None = None,
) -> str:
    """Render one table's schema text for ``purpose``."""
    wanted = (
        purpose
        if isinstance(purpose, SchemaTextPurpose)
        else SchemaTextPurpose(str(purpose))
    )
    for_prompt = wanted is SchemaTextPurpose.PROMPT

    label = table_label or table.table_name or ""
    header = f"# Table: {label}"
    meta_bits: list[str] = []
    comment = (table.custom_comment or "").strip()
    if comment:
        meta_bits.append(comment)
    if for_prompt and table.approx_rows is not None:
        meta_bits.append(f"~{int(table.approx_rows)} rows")
    if for_prompt:
        ix = (table.index_summary or "")[:160]
        if ix:
            meta_bits.append("idx: " + ix)
    if meta_bits:
        header += f", {', '.join(meta_bits)}"
    lines = [header + "\n["]

    profiles: dict[int, Any] = {}
    if for_prompt and profile_prompt_allowed(table) and table.id is not None:
        try:
            from apps.datasource.profiling.service import get_active_field_profiles

            profiles = {
                int(p.field_id): p
                for p in get_active_field_profiles(session, table_id=int(table.id))
            }
        except Exception:
            profiles = {}

    field_lines: list[str] = []
    for field in fields:
        bits = [f"{field.field_name}:{field.field_type}"]
        field_comment = (field.custom_comment or "").strip()
        if field_comment:
            bits.append(field_comment)
        snap = profiles.get(int(field.id)) if field.id is not None else None
        if snap is not None:
            bits.extend(
                format_profile_field_bits(
                    null_rate=snap.null_rate,
                    distinct_ratio=snap.distinct_ratio,
                    min_value=snap.min_value,
                    max_value=snap.max_value,
                    top_values=snap.top_values,
                    include_topk=True,
                )
            )
        field_lines.append("(" + ", ".join(bits) + ")")
    if field_lines:
        lines.append(",\n".join(field_lines))
    lines.append("]")
    return "\n".join(lines) + "\n"
