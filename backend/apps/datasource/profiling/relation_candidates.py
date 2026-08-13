"""Single domain entry for admitting non-DDL relation candidates."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlmodel import Session, select

from apps.datasource.models.datasource import CoreField
from apps.datasource.profiling.models import (
    FieldRelation,
    RelationKind,
    RelationSource,
    RelationStatus,
)


def admit_relation_candidate(
    session: Session,
    *,
    oid: int,
    ds_id: int,
    source_field_id: int,
    target_field_id: int,
    kind: str = "EQUI_JOIN",
    confidence: float | None = None,
    evidence: dict[str, Any] | None = None,
    cardinality: str | None = None,
    source: str = RelationSource.PROBE.value,
) -> tuple[FieldRelation, str]:
    """Create/update a CANDIDATE without overriding a reviewer decision."""
    src = session.get(CoreField, int(source_field_id))
    dst = session.get(CoreField, int(target_field_id))
    if src is None or dst is None:
        raise ValueError("relation field not found")
    if int(src.ds_id) != ds_id or int(dst.ds_id) != ds_id:
        raise ValueError("relation field outside datasource")
    kind_value = (kind or RelationKind.EQUI_JOIN.value).upper()
    if kind_value not in {member.value for member in RelationKind}:
        raise ValueError(f"unsupported relation kind={kind_value}")
    source_value = (source or RelationSource.PROBE.value).strip()
    now = datetime.now()
    row = session.exec(
        select(FieldRelation).where(
            FieldRelation.ds_id == ds_id,
            FieldRelation.source_field_id == int(source_field_id),
            FieldRelation.target_field_id == int(target_field_id),
            FieldRelation.kind == kind_value,
        )
    ).first()
    if row is not None:
        if row.status in {
            RelationStatus.CONFIRMED.value,
            RelationStatus.REJECTED.value,
            RelationStatus.DISABLED.value,
        }:
            return row, f"kept_{row.status.lower()}"
        row.status = RelationStatus.CANDIDATE.value
        row.confidence = confidence
        row.evidence = evidence
        row.cardinality = cardinality
        row.source = source_value
        row.update_time = now
        session.add(row)
        session.flush()
        return row, "updated"

    row = FieldRelation(
        oid=oid,
        ds_id=ds_id,
        source_table_id=int(src.table_id),
        source_field_id=int(source_field_id),
        target_table_id=int(dst.table_id),
        target_field_id=int(target_field_id),
        kind=kind_value,
        cardinality=cardinality,
        status=RelationStatus.CANDIDATE.value,
        source=source_value,
        confidence=confidence,
        evidence=evidence,
        create_time=now,
        update_time=now,
    )
    session.add(row)
    session.flush()
    return row, "created"
