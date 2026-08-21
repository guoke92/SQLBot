"""Single ingestion, governance, validation and deployment service for knowledge 2.0."""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime
from hashlib import sha256
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import aliased
from sqlmodel import Session, col, select

from apps.ai_model.embedding import EmbeddingModelCache
from apps.data_training.models.data_training_model import DataTraining
from apps.datasource.models.datasource import CoreDatasource, CoreField, CoreTable
from apps.datasource.profiling.models import (
    FieldProfileSnapshot,
    FieldRelation,
)
from apps.knowledge.db_models import (
    KnowledgeAsset,
    KnowledgeBinding,
    KnowledgeDeployment,
    KnowledgeSourceEvidence,
    KnowledgeUnit,
    KnowledgeUnitRevision,
    SemanticKnowledgePackage,
)
from apps.knowledge.semantic.schema import (
    KnowledgePackageV2,
    KnowledgeUnitEntry,
    validate_knowledge_unit,
)
from apps.protocol import QueryPlan, get_protocol_for_ds
from apps.protocol.base import CAP_SQL_DIALECT
from apps.terminology.models.terminology_model import Terminology
from common.core.config import settings

logger = logging.getLogger(__name__)


def _json_hash(value: Any) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str
    )
    return sha256(payload.encode()).hexdigest()


def _now() -> datetime:
    return datetime.utcnow()


def register_package(
    session: Session,
    *,
    oid: int,
    actor_user_id: int | None,
    package: KnowledgePackageV2,
    mode: str = "append",
) -> tuple[SemanticKnowledgePackage, list[KnowledgeUnitRevision], bool]:
    """Register a KnowledgePackage 2.0 import (append or overwrite).

    * ``append`` (default) - repeated imports accumulate. Identical content is
      an idempotent no-op; changed content auto-assigns the next revision
      number (no manual bump, keeps every copy).
    * ``overwrite`` - changed content replaces the existing DRAFT revision in
      place (keeps one copy). Revisions past DRAFT are immutable and raise.
    """
    if mode not in ("append", "overwrite"):
        raise ValueError("mode must be 'append' or 'overwrite'")
    metadata = package.package
    existing = session.exec(
        select(SemanticKnowledgePackage).where(
            SemanticKnowledgePackage.oid == oid,
            SemanticKnowledgePackage.package_id == metadata.package_id,
            SemanticKnowledgePackage.revision == metadata.revision,
        )
    ).one_or_none()
    document = package.model_dump(mode="json")
    content_hash = _json_hash(document)
    if existing is not None and existing.content_hash == content_hash:
        revisions = session.exec(
            select(KnowledgeUnitRevision).where(
                KnowledgeUnitRevision.package_id == int(existing.id or 0)
            )
        ).all()
        return existing, list(revisions), False

    now = _now()
    created = True
    if existing is not None and mode == "overwrite":
        existing.source_document = document
        existing.content_hash = content_hash
        existing.namespace = metadata.namespace
        existing.title = metadata.title
        existing.description = metadata.description
        existing.update_time = now
        session.add(existing)
        package_row = existing
        created = False
    else:
        if existing is not None:  # append: bump past the collision
            next_rev = (
                int(
                    session.scalar(
                        select(func.max(SemanticKnowledgePackage.revision)).where(
                            SemanticKnowledgePackage.oid == oid,
                            SemanticKnowledgePackage.package_id == metadata.package_id,
                        )
                    )
                    or 0
                )
                + 1
            )
            metadata.revision = next_rev
            document = package.model_dump(mode="json")
            content_hash = _json_hash(document)
        package_row = SemanticKnowledgePackage(
            oid=oid,
            package_id=metadata.package_id,
            revision=metadata.revision,
            namespace=metadata.namespace,
            title=metadata.title,
            description=metadata.description,
            content_hash=content_hash,
            source_document=document,
            create_by=actor_user_id,
            create_time=now,
            update_time=now,
        )
        session.add(package_row)
        session.flush()
        assert package_row.id is not None

    source_by_id = {source.source_id: source for source in package.sources}
    evidence_rows = {
        row.evidence_key: row
        for row in session.exec(
            select(KnowledgeSourceEvidence).where(
                KnowledgeSourceEvidence.package_id == int(package_row.id or 0)
            )
        ).all()
    }
    for evidence in package.evidence:
        source = source_by_id[evidence.source_id]
        payload = evidence.model_dump(mode="json")
        row = evidence_rows.get(evidence.evidence_id)
        if row is None:
            session.add(
                KnowledgeSourceEvidence(
                    oid=oid,
                    package_id=int(package_row.id or 0),
                    evidence_key=evidence.evidence_id,
                    source_id=evidence.source_id,
                    evidence_kind=evidence.evidence_kind,
                    locator=evidence.locator or source.locator,
                    content_hash=evidence.content_hash or source.content_hash,
                    payload=payload,
                    create_time=now,
                )
            )
        else:
            row.source_id = evidence.source_id
            row.evidence_kind = evidence.evidence_kind
            row.locator = evidence.locator or source.locator
            row.content_hash = evidence.content_hash or source.content_hash
            row.payload = payload
            session.add(row)

    revision_rows: list[KnowledgeUnitRevision] = []
    for entry in package.knowledge_units:
        unit_key = f"{metadata.namespace}:{entry.unit_id}"
        unit = session.exec(
            select(KnowledgeUnit).where(
                KnowledgeUnit.oid == oid,
                KnowledgeUnit.unit_key == unit_key,
            )
        ).one_or_none()
        if unit is None:
            unit = KnowledgeUnit(
                oid=oid,
                unit_key=unit_key,
                namespace=metadata.namespace,
                domain=entry.domain,
                title=entry.title,
                create_time=now,
                update_time=now,
            )
            session.add(unit)
            session.flush()
        else:
            unit.title = entry.title
            unit.domain = entry.domain
            unit.update_time = now
            session.add(unit)
        assert unit.id is not None
        entry_json = entry.model_dump(mode="json")
        entry_hash = _json_hash(entry_json)
        existing_revision = session.exec(
            select(KnowledgeUnitRevision).where(
                KnowledgeUnitRevision.unit_id == int(unit.id),
                KnowledgeUnitRevision.revision == entry.revision,
            )
        ).one_or_none()
        if (
            existing_revision is not None
            and existing_revision.content_hash == entry_hash
        ):
            revision_rows.append(existing_revision)
            continue
        if existing_revision is not None and mode == "overwrite":
            if existing_revision.lifecycle_status != "DRAFT":
                raise ValueError(
                    f"unit {entry.unit_id} revision {entry.revision} is "
                    f"{existing_revision.lifecycle_status} and cannot be overwritten"
                )
            existing_revision.content = entry_json
            existing_revision.content_hash = entry_hash
            existing_revision.confidence = entry.confidence
            existing_revision.package_id = int(package_row.id or 0)
            existing_revision.update_time = now
            session.add(existing_revision)
            revision_rows.append(existing_revision)
            continue
        if existing_revision is not None:  # append: bump past the collision
            entry.revision = (
                int(
                    session.scalar(
                        select(func.max(KnowledgeUnitRevision.revision)).where(
                            KnowledgeUnitRevision.unit_id == int(unit.id)
                        )
                    )
                    or 0
                )
                + 1
            )
            entry_json = entry.model_dump(mode="json")
            entry_hash = _json_hash(entry_json)
        row = KnowledgeUnitRevision(
            oid=oid,
            unit_id=int(unit.id),
            package_id=int(package_row.id),
            revision=entry.revision,
            content=entry_json,
            validation_summary={
                "issues": [],
                "message": "Semantic knowledge registered; bind a datasource to validate physical data.",
            },
            content_hash=entry_hash,
            confidence=entry.confidence,
            create_by=actor_user_id,
            create_time=now,
            update_time=now,
        )
        session.add(row)
        revision_rows.append(row)

    # v3.1 dual-write: decompose into the node store alongside the legacy
    # revision path. Transition safety - a decomposition failure must not
    # block package registration; it is logged for follow-up.
    try:
        from apps.knowledge.graph.decompose import decompose_package

        decompose_package(
            session,
            oid=oid,
            package=package,
            package_row_id=int(package_row.id or 0),
        )
    except Exception as exc:  # noqa: BLE001 - transition guard
        logger.warning(
            "knowledge decomposition skipped for package %s: %s: %s",
            metadata.package_id,
            type(exc).__name__,
            exc,
        )

    session.commit()
    session.refresh(package_row)
    for row in revision_rows:
        session.refresh(row)
    return package_row, revision_rows, created


def list_packages(
    session: Session, *, oid: int, page: int, page_size: int
) -> tuple[list[SemanticKnowledgePackage], int]:
    filters = [
        SemanticKnowledgePackage.oid == oid,
        SemanticKnowledgePackage.status != "RETIRED",
    ]
    total = int(
        session.scalar(
            select(func.count()).select_from(SemanticKnowledgePackage).where(*filters)
        )
        or 0
    )
    rows = session.exec(
        select(SemanticKnowledgePackage)
        .where(*filters)
        .order_by(col(SemanticKnowledgePackage.update_time).desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return list(rows), total


def _next_step(
    revision: KnowledgeUnitRevision, binding: KnowledgeBinding | None
) -> str:
    return next_step_for(
        validation_status=revision.validation_status,
        lifecycle_status=revision.lifecycle_status,
        binding_status=binding.status if binding is not None else None,
    )


def validation_preview(summary: dict[str, Any] | None) -> dict[str, Any]:
    payload = summary if isinstance(summary, dict) else {}
    issues = [
        issue for issue in (payload.get("issues") or []) if isinstance(issue, dict)
    ]
    errors = [issue for issue in issues if issue.get("severity") != "warning"]
    warnings = [issue for issue in issues if issue.get("severity") == "warning"]
    return {
        "validation_summary_text": str(
            payload.get("summary") or payload.get("message") or ""
        ),
        "validation_error_count": len(errors),
        "validation_warning_count": len(warnings),
        "validation_issue_count": len(issues),
        "validation_issues": issues,
    }


def match_catalog_table(
    tables: list[CoreTable],
    *,
    table_name: str,
    database_name: str = "",
) -> CoreTable | None:
    """Resolve a dataset to a catalog table without requiring a new revision.

    MySQL catalogs often leave ``database_name`` empty because the datasource
    already selects one schema. A knowledge unit may still record the physical
    schema name; unique table-name matches are accepted in that case.
    """
    name = table_name.casefold()
    database = database_name.casefold()
    named = [table for table in tables if table.table_name.casefold() == name]
    if not named:
        return None
    exact = [
        table for table in named if (table.database_name or "").casefold() == database
    ]
    if len(exact) == 1:
        return exact[0]
    if database:
        compatible = [
            table
            for table in named
            if (table.database_name or "").casefold() in {database, ""}
        ]
        if len(compatible) == 1:
            return compatible[0]
    if len(named) == 1:
        return named[0]
    return None


def current_package_revisions(
    session: Session, *, package_row_id: int
) -> list[tuple[KnowledgeUnitRevision, KnowledgeUnit]]:
    """Latest revision per unit currently attached to a package.

    Superseded revisions stay ``RETIRED`` and lose to a newer draft. The current
    revision may itself be ``RETIRED`` after unpublish, and must remain visible
    so it can be republished.
    """
    rows = list(
        session.exec(
            select(KnowledgeUnitRevision, KnowledgeUnit)
            .join(KnowledgeUnit, KnowledgeUnit.id == KnowledgeUnitRevision.unit_id)
            .where(KnowledgeUnitRevision.package_id == package_row_id)
        ).all()
    )
    latest: dict[int, tuple[KnowledgeUnitRevision, KnowledgeUnit]] = {}
    for revision, unit in rows:
        current = latest.get(int(unit.id or 0))
        if current is None or revision.revision > current[0].revision:
            latest[int(unit.id or 0)] = (revision, unit)
    return sorted(
        latest.values(),
        key=lambda item: (item[1].domain, item[1].title),
    )


def derive_package_status(revisions: list[KnowledgeUnitRevision]) -> str:
    statuses = {row.lifecycle_status for row in revisions}
    if not statuses:
        return "REGISTERED"
    if statuses <= {"RETIRED"}:
        return "RETIRED"
    if statuses <= {"PUBLISHED"}:
        return "PUBLISHED"
    if statuses <= {"APPROVED", "PUBLISHED"}:
        return "APPROVED"
    if statuses <= {"APPROVED", "PUBLISHED", "RETIRED"}:
        return "APPROVED" if "APPROVED" in statuses else "PUBLISHED"
    if "IN_REVIEW" in statuses:
        return "IN_REVIEW"
    return "REGISTERED"


def current_package_entries(
    session: Session, *, package_row_id: int
) -> list[KnowledgeUnitEntry]:
    entries: list[KnowledgeUnitEntry] = []
    for revision, _unit in current_package_revisions(
        session, package_row_id=package_row_id
    ):
        entries.append(KnowledgeUnitEntry.model_validate(revision.content))
    return entries


def list_units(
    session: Session,
    *,
    oid: int,
    keyword: str,
    lifecycle: str | None,
    validation: str | None,
    page: int,
    page_size: int,
) -> tuple[list[dict[str, Any]], int, dict[str, int]]:
    previous = aliased(KnowledgeUnitRevision)
    latest_revision = (
        select(func.max(previous.revision))
        .where(previous.unit_id == KnowledgeUnitRevision.unit_id)
        .correlate(KnowledgeUnitRevision)
        .scalar_subquery()
    )
    statement = (
        select(KnowledgeUnitRevision, KnowledgeUnit)
        .join(KnowledgeUnit, KnowledgeUnit.id == KnowledgeUnitRevision.unit_id)
        .where(
            KnowledgeUnitRevision.oid == oid,
            KnowledgeUnitRevision.revision == latest_revision,
        )
    )
    needle = keyword.strip()
    if needle:
        statement = statement.where(
            col(KnowledgeUnit.title).ilike(f"%{needle}%")
            | col(KnowledgeUnit.unit_key).ilike(f"%{needle}%")
        )
    if validation:
        statement = statement.where(
            KnowledgeUnitRevision.validation_status == validation
        )
    count_statement = (
        select(KnowledgeUnitRevision.lifecycle_status, func.count())
        .join(KnowledgeUnit, KnowledgeUnit.id == KnowledgeUnitRevision.unit_id)
        .where(
            KnowledgeUnitRevision.oid == oid,
            KnowledgeUnitRevision.revision == latest_revision,
        )
    )
    if validation:
        count_statement = count_statement.where(
            KnowledgeUnitRevision.validation_status == validation
        )
    if needle:
        count_statement = count_statement.where(
            col(KnowledgeUnit.title).ilike(f"%{needle}%")
            | col(KnowledgeUnit.unit_key).ilike(f"%{needle}%")
        )
    counts = {
        str(status): int(count)
        for status, count in session.exec(
            count_statement.group_by(KnowledgeUnitRevision.lifecycle_status)
        ).all()
    }
    if lifecycle:
        statement = statement.where(KnowledgeUnitRevision.lifecycle_status == lifecycle)
    total = int(
        session.scalar(select(func.count()).select_from(statement.subquery())) or 0
    )
    selected = session.exec(
        statement.order_by(col(KnowledgeUnitRevision.update_time).desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    results: list[dict[str, Any]] = []
    binding_changed = False
    for revision_row, unit in selected:
        binding = session.exec(
            select(KnowledgeBinding)
            .where(KnowledgeBinding.revision_id == int(revision_row.id or 0))
            .order_by(col(KnowledgeBinding.update_time).desc())
        ).first()
        if binding is not None:
            binding_changed = (
                refresh_binding_freshness(session, binding) or binding_changed
            )
        deployment = session.exec(
            select(KnowledgeDeployment)
            .where(KnowledgeDeployment.revision_id == int(revision_row.id or 0))
            .order_by(col(KnowledgeDeployment.update_time).desc())
        ).first()
        results.append(
            {
                "unit_id": int(unit.id or 0),
                "unit_key": unit.unit_key,
                "title": unit.title,
                "domain": unit.domain,
                "revision_id": int(revision_row.id or 0),
                "revision": revision_row.revision,
                "lifecycle_status": revision_row.lifecycle_status,
                "validation_status": revision_row.validation_status,
                "binding_status": binding.status if binding else "UNBOUND",
                "datasource_id": binding.datasource_id if binding else None,
                "deployment_status": deployment.status
                if deployment
                else "NOT_PUBLISHED",
                "confidence": revision_row.confidence,
                "next_step": _next_step(revision_row, binding),
                "update_time": revision_row.update_time,
                **validation_preview(revision_row.validation_summary),
            }
        )
    if binding_changed:
        session.commit()
    return results, total, counts


def recommend_datasources(
    session: Session, *, oid: int, entries: list[KnowledgeUnitEntry]
) -> list[dict[str, Any]]:
    required: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for entry in entries:
        for dataset in entry.content.datasets:
            key = (dataset.database.casefold(), dataset.name.casefold())
            if key in seen:
                continue
            seen.add(key)
            required.append((dataset.database, dataset.name))
    datasources = list(
        session.exec(select(CoreDatasource).where(CoreDatasource.oid == oid)).all()
    )
    results: list[dict[str, Any]] = []
    for datasource in datasources:
        tables = list(
            session.exec(
                select(CoreTable).where(CoreTable.ds_id == int(datasource.id or 0))
            ).all()
        )
        missing = [
            f"{database + '.' if database else ''}{table}"
            for database, table in required
            if match_catalog_table(tables, table_name=table, database_name=database)
            is None
        ]
        matched_count = len(required) - len(missing)
        results.append(
            {
                "datasource_id": int(datasource.id or 0),
                "datasource_name": datasource.name,
                "required_count": len(required),
                "matched_count": matched_count,
                "coverage": (matched_count / len(required)) if required else 1.0,
                "missing": missing,
            }
        )
    return sorted(results, key=lambda item: item["coverage"], reverse=True)


def get_unit_revision(
    session: Session, *, oid: int, unit_id: int, revision: int
) -> tuple[
    KnowledgeUnit,
    KnowledgeUnitRevision,
    list[KnowledgeBinding],
    list[KnowledgeDeployment],
]:
    unit = session.get(KnowledgeUnit, unit_id)
    if unit is None or unit.oid != oid:
        raise ValueError("knowledge unit not found")
    revision_row = session.exec(
        select(KnowledgeUnitRevision).where(
            KnowledgeUnitRevision.unit_id == unit_id,
            KnowledgeUnitRevision.revision == revision,
        )
    ).one_or_none()
    if revision_row is None:
        raise ValueError("knowledge unit revision not found")
    bindings = list(
        session.exec(
            select(KnowledgeBinding).where(
                KnowledgeBinding.revision_id == int(revision_row.id or 0)
            )
        ).all()
    )
    bindings.sort(
        key=lambda item: (
            item.status == "UNBOUND",
            -(item.update_time.timestamp() if item.update_time else 0),
        )
    )
    binding_changed = False
    for binding in bindings:
        binding_changed = refresh_binding_freshness(session, binding) or binding_changed
    if binding_changed:
        session.commit()
    deployments = list(
        session.exec(
            select(KnowledgeDeployment).where(
                KnowledgeDeployment.revision_id == int(revision_row.id or 0)
            )
        ).all()
    )
    return unit, revision_row, bindings, deployments


def _catalog_fingerprint(tables: list[CoreTable], fields: list[CoreField]) -> str:
    material = {
        "tables": sorted(
            (
                table.database_name or "",
                table.table_name,
                table.schema_fingerprint or "",
            )
            for table in tables
        ),
        "fields": sorted(
            (field.table_id, field.field_name, field.field_type or "")
            for field in fields
        ),
    }
    return _json_hash(material)


def _mapped_fingerprint(
    tables: list[CoreTable],
    fields: list[CoreField],
    mapping: dict[str, Any],
) -> str:
    table_ids = {
        int(item["table_id"])
        for item in (mapping.get("datasets") or {}).values()
        if isinstance(item, dict) and item.get("table_id") is not None
    }
    field_ids = {
        int(item["field_id"])
        for item in (mapping.get("fields") or {}).values()
        if isinstance(item, dict) and item.get("field_id") is not None
    }
    return _catalog_fingerprint(
        [table for table in tables if int(table.id or 0) in table_ids],
        [field for field in fields if int(field.id or 0) in field_ids],
    )


def _type_family(value: str | None) -> str:
    normalized = (value or "").strip().casefold().split("(", 1)[0]
    if not normalized:
        return ""
    if any(token in normalized for token in ("char", "text", "string", "clob")):
        return "string"
    if any(
        token in normalized
        for token in ("int", "decimal", "numeric", "number", "float", "double", "real")
    ):
        return "number"
    if any(token in normalized for token in ("date", "time", "timestamp")):
        return "temporal"
    if any(token in normalized for token in ("bool", "bit")):
        return "boolean"
    if any(token in normalized for token in ("json", "map", "array", "struct")):
        return "structured"
    return normalized


def _types_compatible(expected: str | None, actual: str | None) -> bool:
    expected_family = _type_family(expected)
    actual_family = _type_family(actual)
    return not expected_family or expected_family == actual_family


_CASTABLE_FAMILIES = {("string", "number"), ("number", "string")}
_NAMED_SQL_PARAM = re.compile(r"(?<!:):[A-Za-z_][A-Za-z0-9_]*")


def join_type_severity(left_type: str | None, right_type: str | None) -> str | None:
    """None if compatible; warning for CAST-able string/number joins; else error."""
    if _types_compatible(left_type, right_type) or _types_compatible(
        right_type, left_type
    ):
        return None
    left_family = _type_family(left_type)
    right_family = _type_family(right_type)
    if not left_family or not right_family:
        return None
    if (left_family, right_family) in _CASTABLE_FAMILIES:
        return "warning"
    return "error"


def prepare_example_sql(sql: str) -> str:
    """Replace named bind parameters so catalog checks can parse example SQL."""
    return _NAMED_SQL_PARAM.sub("'1'", sql.strip())


def _issue(**fields: Any) -> dict[str, Any]:
    return {key: value for key, value in fields.items() if value not in (None, "")}


def _table_locator(dataset: Any) -> str:
    return ".".join(part for part in (dataset.database, dataset.name) if part) or str(
        dataset.dataset_id
    )


def _field_locator(dataset: Any, field: Any | None, fallback: str) -> str:
    table = _table_locator(dataset)
    if field is None:
        return f"{table}.{fallback}" if table else fallback
    return f"{table}.{field.name}"


def _resolve_field(datasets: dict[str, Any], ref: Any) -> tuple[Any | None, Any | None]:
    dataset = datasets.get(ref.dataset)
    if dataset is None:
        return None, None
    field = next(
        (
            item
            for item in dataset.fields
            if item.field_id == ref.field or item.name == ref.field
        ),
        None,
    )
    return dataset, field


def _query_issue_message(raw: str) -> str:
    text = (raw or "").strip()
    lowered = text.casefold()
    if "unauthorized tables" in lowered:
        return "查询引用了当前数据源目录中不存在的表"
    if "identifier validation failed" in lowered:
        return "查询语法无法解析，请检查方言或示例 SQL"
    if "safety check failed" in lowered:
        return "查询未通过只读安全检查"
    return text[:400]


def refresh_binding_freshness(session: Session, binding: KnowledgeBinding) -> bool:
    """Mark a previously valid binding stale when its datasource catalog changes."""
    if binding.status != "BOUND":
        return False
    tables = list(
        session.exec(
            select(CoreTable).where(CoreTable.ds_id == binding.datasource_id)
        ).all()
    )
    fields = list(
        session.exec(
            select(CoreField).where(CoreField.ds_id == binding.datasource_id)
        ).all()
    )
    mapping = binding.mapping if isinstance(binding.mapping, dict) else {}
    if binding.catalog_fingerprint == _mapped_fingerprint(tables, fields, mapping):
        return False
    binding.status = "STALE"
    binding.update_time = _now()
    session.add(binding)
    return True


def bind_and_validate(
    session: Session,
    *,
    oid: int,
    revision_id: int,
    datasource_id: int,
) -> KnowledgeBinding:
    revision = session.get(KnowledgeUnitRevision, revision_id)
    datasource = session.get(CoreDatasource, datasource_id)
    if revision is None or revision.oid != oid:
        raise ValueError("knowledge revision not found")
    if datasource is None or int(datasource.oid or 0) != oid:
        raise ValueError("datasource not found in workspace")
    entry = KnowledgeUnitEntry.model_validate(revision.content)
    tables = list(
        session.exec(select(CoreTable).where(CoreTable.ds_id == datasource_id)).all()
    )
    fields = list(
        session.exec(select(CoreField).where(CoreField.ds_id == datasource_id)).all()
    )
    field_index = {
        (field.table_id, field.field_name.casefold()): field for field in fields
    }
    profile_rows = list(
        session.exec(
            select(FieldProfileSnapshot).where(
                FieldProfileSnapshot.ds_id == datasource_id,
                FieldProfileSnapshot.window_code == "ALL",
                FieldProfileSnapshot.status == "READY",
            )
        ).all()
    )
    latest_profile: dict[int, FieldProfileSnapshot] = {}
    for profile in profile_rows:
        current = latest_profile.get(profile.field_id)
        if current is None or profile.generation > current.generation:
            latest_profile[profile.field_id] = profile
    issues: list[dict[str, Any]] = []
    mapping: dict[str, Any] = {"datasets": {}, "fields": {}, "relationships": {}}
    datasets_by_id = {dataset.dataset_id: dataset for dataset in entry.content.datasets}
    for dataset in entry.content.datasets:
        table = match_catalog_table(
            tables, table_name=dataset.name, database_name=dataset.database
        )
        if table is None:
            issues.append(
                _issue(
                    code="DATASET_NOT_FOUND",
                    severity="error",
                    knowledge_kind="dataset",
                    knowledge_id=dataset.dataset_id,
                    title=dataset.description or dataset.name,
                    dataset=_table_locator(dataset),
                    message=f"当前数据源中找不到表 {_table_locator(dataset)}",
                )
            )
            continue
        mapping["datasets"][dataset.dataset_id] = {
            "table_id": int(table.id),
            "database_name": table.database_name or "",
            "table_name": table.table_name,
        }
        for semantic_field in dataset.fields:
            field = field_index.get((int(table.id), semantic_field.name.casefold()))
            if field is None:
                issues.append(
                    _issue(
                        code="FIELD_NOT_FOUND",
                        severity="error",
                        knowledge_kind="field",
                        knowledge_id=semantic_field.field_id,
                        title=semantic_field.description or semantic_field.name,
                        dataset=_table_locator(dataset),
                        field=semantic_field.name,
                        message=(
                            f"表 {_table_locator(dataset)} 中找不到字段 "
                            f"{semantic_field.name}"
                        ),
                    )
                )
                continue
            mapping["fields"][f"{dataset.dataset_id}.{semantic_field.field_id}"] = {
                "field_id": int(field.id),
                "table_id": int(table.id),
                "field_name": field.field_name,
                "field_type": field.field_type,
            }
            profile = latest_profile.get(int(field.id))
            if profile is not None:
                mapping["fields"][f"{dataset.dataset_id}.{semantic_field.field_id}"][
                    "profile"
                ] = {
                    "generation": profile.generation,
                    "row_count": profile.row_count,
                    "null_rate": profile.null_rate,
                    "approx_distinct": profile.approx_distinct,
                    "distinct_ratio": profile.distinct_ratio,
                    "profiled_at": profile.profiled_at.isoformat(),
                }
            if not _types_compatible(semantic_field.data_type, field.field_type):
                issues.append(
                    _issue(
                        code="FIELD_TYPE_MISMATCH",
                        severity="error",
                        knowledge_kind="field",
                        knowledge_id=semantic_field.field_id,
                        title=semantic_field.description or semantic_field.name,
                        dataset=_table_locator(dataset),
                        field=semantic_field.name,
                        expected_type=semantic_field.data_type,
                        actual_type=field.field_type,
                        message=(
                            f"{_field_locator(dataset, semantic_field, semantic_field.name)} "
                            f"声明为 {semantic_field.data_type}，数据源中是 {field.field_type}"
                        ),
                    )
                )
    for relationship in entry.content.relationships:
        left_key = f"{relationship.left.dataset}.{relationship.left.field}"
        right_key = f"{relationship.right.dataset}.{relationship.right.field}"
        left_dataset, left_field = _resolve_field(datasets_by_id, relationship.left)
        right_dataset, right_field = _resolve_field(datasets_by_id, relationship.right)
        left_locator = (
            _field_locator(left_dataset, left_field, relationship.left.field)
            if left_dataset is not None
            else left_key
        )
        right_locator = (
            _field_locator(right_dataset, right_field, relationship.right.field)
            if right_dataset is not None
            else right_key
        )
        title = relationship.business_meaning or relationship.relationship_id
        left = mapping["fields"].get(left_key)
        right = mapping["fields"].get(right_key)
        if not isinstance(left, dict) or not isinstance(right, dict):
            issues.append(
                _issue(
                    code="RELATIONSHIP_NOT_BOUND",
                    severity="error",
                    knowledge_kind="relationship",
                    knowledge_id=relationship.relationship_id,
                    title=title,
                    left_locator=left_locator,
                    right_locator=right_locator,
                    message="关系两端字段未能绑定到当前数据源，无法确认 JOIN",
                )
            )
            continue
        type_severity = join_type_severity(
            str(left.get("field_type") or ""), str(right.get("field_type") or "")
        )
        if type_severity:
            issues.append(
                _issue(
                    code="RELATIONSHIP_TYPE_MISMATCH",
                    severity=type_severity,
                    knowledge_kind="relationship",
                    knowledge_id=relationship.relationship_id,
                    title=title,
                    left_locator=left_locator,
                    right_locator=right_locator,
                    left_type=left.get("field_type"),
                    right_type=right.get("field_type"),
                    message=(
                        "两端类型不同，JOIN 时需要 CAST"
                        if type_severity == "warning"
                        else "两端类型不兼容，无法直接等值连接"
                    ),
                )
            )
            if type_severity == "error":
                continue
        if relationship.status != "confirmed":
            issues.append(
                _issue(
                    code="RELATIONSHIP_PROPOSED",
                    severity="warning",
                    knowledge_kind="relationship",
                    knowledge_id=relationship.relationship_id,
                    title=title,
                    left_locator=left_locator,
                    right_locator=right_locator,
                    message="关系尚未人工确认，审核时请核对 JOIN 字段",
                )
            )
        mapping["relationships"][relationship.relationship_id] = {
            "left": left,
            "right": right,
            "kind": relationship.relationship_type,
            "cardinality": relationship.cardinality,
            "confidence": relationship.confidence,
            "status": relationship.status,
        }
    protocol = get_protocol_for_ds(datasource)
    query_verifications: dict[str, Any] = {}
    for pattern in entry.content.verified_query_patterns:
        if not protocol.supports(CAP_SQL_DIALECT):
            issues.append(
                _issue(
                    code="QUERY_PROTOCOL_UNSUPPORTED",
                    severity="warning",
                    knowledge_kind="query",
                    knowledge_id=pattern.pattern_id,
                    title=pattern.question,
                    message="当前数据源不是 SQL 协议，无法校验该查询示例",
                )
            )
            continue
        example_sql = prepare_example_sql(pattern.query)
        plan = QueryPlan(
            success=True,
            statement=example_sql,
            payload={"sql": example_sql},
        )
        validated = protocol.validate_plan(
            datasource,
            plan,
            [table.table_name for table in tables],
        )
        if not validated.success:
            issues.append(
                _issue(
                    code="QUERY_VALIDATION_FAILED",
                    severity="warning",
                    knowledge_kind="query",
                    knowledge_id=pattern.pattern_id,
                    title=pattern.question,
                    message=_query_issue_message(
                        validated.message or "Query validation failed"
                    ),
                )
            )
            continue
        try:
            result = protocol.execute(datasource, validated, max_rows=1)
        except Exception as exc:
            issues.append(
                _issue(
                    code="QUERY_EXECUTION_FAILED",
                    severity="warning",
                    knowledge_kind="query",
                    knowledge_id=pattern.pattern_id,
                    title=pattern.question,
                    message=_query_issue_message(str(exc)),
                )
            )
            continue
        query_verifications[pattern.pattern_id] = {
            "executed": True,
            "passed": True,
            "fields": list(result.fields),
            "sample_rows": min(len(result.data), 1),
            "verified_at": _now().isoformat(),
        }
    mapping["verified_query_patterns"] = query_verifications
    has_error = any(issue["severity"] == "error" for issue in issues)
    has_warning = any(issue["severity"] == "warning" for issue in issues)
    validation_status = "FAIL" if has_error else "WARNING" if has_warning else "PASS"
    now = _now()
    binding = session.exec(
        select(KnowledgeBinding).where(
            KnowledgeBinding.revision_id == revision_id,
            KnowledgeBinding.datasource_id == datasource_id,
        )
    ).one_or_none()
    if binding is None:
        binding = KnowledgeBinding(
            oid=oid,
            revision_id=revision_id,
            datasource_id=datasource_id,
            create_time=now,
            update_time=now,
        )
    binding.catalog_fingerprint = _mapped_fingerprint(tables, fields, mapping)
    binding.status = "BOUND"
    binding.mapping = mapping
    binding.validation_result = {
        "status": validation_status,
        "issues": issues,
        "summary": (
            "Physical binding validated"
            if not issues
            else f"Datasource binding has {len(issues)} unresolved physical references"
        ),
    }
    binding.update_time = now
    revision.validation_status = validation_status
    revision.validation_summary = binding.validation_result
    revision.update_time = now
    session.add(binding)
    session.add(revision)
    others = list(
        session.exec(
            select(KnowledgeBinding).where(
                KnowledgeBinding.revision_id == revision_id,
                KnowledgeBinding.datasource_id != datasource_id,
            )
        ).all()
    )
    for other in others:
        if other.status != "UNBOUND":
            other.status = "UNBOUND"
            other.update_time = now
            session.add(other)
    session.commit()
    session.refresh(binding)
    return binding


LIFECYCLE_TRANSITIONS: dict[str, set[str]] = {
    "DRAFT": {"IN_REVIEW"},
    "IN_REVIEW": {"APPROVED", "REJECTED", "DRAFT"},
    "APPROVED": {"PUBLISHED", "DRAFT"},
    "PUBLISHED": {"RETIRED"},
    "REJECTED": {"DRAFT"},
    "RETIRED": set(),
}

NEEDS_REVALIDATE = "NEEDS_REVALIDATE"


def next_step_for(
    *,
    validation_status: str | None,
    lifecycle_status: str | None,
    binding_status: str | None,
) -> str:
    """Single decision chain for the next governance action.

    Shared by the revision plane and the node/composition plane.  The
    NEEDS_REVALIDATE branch is a no-op for the revision plane, which has no
    such validation status.
    """
    if binding_status is None or binding_status == "UNBOUND":
        return "BIND_DATASOURCE"
    if binding_status == "STALE":
        return "REVALIDATE"
    if validation_status == NEEDS_REVALIDATE:
        return "REVALIDATE"
    if validation_status == "FAIL":
        return "REVIEW_ISSUES"
    if validation_status == "NOT_RUN":
        return "VALIDATE"
    if lifecycle_status == "DRAFT":
        return "SUBMIT_REVIEW"
    if lifecycle_status == "IN_REVIEW":
        return "REVIEW"
    if lifecycle_status == "APPROVED":
        return "PUBLISH"
    if lifecycle_status == "PUBLISHED":
        return "VIEW_RUNTIME"
    if lifecycle_status == "RETIRED":
        return "REPUBLISH"
    return "NONE"


def transition_revision(
    session: Session,
    *,
    oid: int,
    revision_id: int,
    target: str,
    actor_user_id: int | None,
    reason: str = "",
) -> KnowledgeUnitRevision:
    row = session.get(KnowledgeUnitRevision, revision_id)
    if row is None or row.oid != oid:
        raise ValueError("knowledge revision not found")
    if target not in LIFECYCLE_TRANSITIONS.get(row.lifecycle_status, set()):
        raise ValueError(
            f"illegal lifecycle transition {row.lifecycle_status} -> {target}"
        )
    if target in {"IN_REVIEW", "APPROVED"} and row.validation_status not in {
        "PASS",
        "WARNING",
    }:
        raise ValueError("knowledge must pass validation before review or approval")
    if target == "APPROVED":
        binding = session.exec(
            select(KnowledgeBinding).where(
                KnowledgeBinding.revision_id == revision_id,
                col(KnowledgeBinding.status).in_(["BOUND", "STALE"]),
            )
        ).one_or_none()
        if binding is None:
            raise ValueError(
                "knowledge must have a current datasource binding before approval"
            )
    now = _now()
    row.lifecycle_status = target
    row.update_time = now
    if target in {"APPROVED", "REJECTED"}:
        row.review_by = actor_user_id
        row.reviewed_at = now
    if reason.strip():
        summary = dict(row.validation_summary or {})
        notes = list(summary.get("review_notes") or [])
        notes.append(
            {
                "action": target,
                "reason": reason.strip(),
                "actor_user_id": actor_user_id,
                "created_at": now.isoformat(),
            }
        )
        summary["review_notes"] = notes
        row.validation_summary = summary
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def create_revision(
    session: Session,
    *,
    oid: int,
    unit_id: int,
    base_revision: int,
    content: dict[str, Any],
    actor_user_id: int | None,
) -> KnowledgeUnitRevision:
    unit, base, _bindings, _deployments = get_unit_revision(
        session, oid=oid, unit_id=unit_id, revision=base_revision
    )
    entry = KnowledgeUnitEntry.model_validate(content)
    base_entry = KnowledgeUnitEntry.model_validate(base.content)
    if entry.unit_id != base_entry.unit_id:
        raise ValueError("unit_id is a stable identity and cannot be changed")
    known_evidence = set(
        session.exec(
            select(KnowledgeSourceEvidence.evidence_key).where(
                KnowledgeSourceEvidence.package_id == base.package_id
            )
        ).all()
    )
    validate_knowledge_unit(entry, known_evidence)
    next_revision = (
        int(
            session.scalar(
                select(func.max(KnowledgeUnitRevision.revision)).where(
                    KnowledgeUnitRevision.unit_id == unit_id
                )
            )
            or 0
        )
        + 1
    )
    entry.revision = next_revision
    now = _now()
    payload = entry.model_dump(mode="json")
    row = KnowledgeUnitRevision(
        oid=oid,
        unit_id=unit_id,
        package_id=base.package_id,
        revision=next_revision,
        content=payload,
        validation_summary={
            "issues": [],
            "message": "Edited revision requires validation",
        },
        content_hash=_json_hash(payload),
        confidence=entry.confidence,
        create_by=actor_user_id,
        create_time=now,
        update_time=now,
    )
    unit.title = entry.title
    unit.domain = entry.domain
    unit.update_time = now
    session.add(row)
    session.add(unit)
    session.flush()
    _retire_superseded_revisions(
        session, unit_id=unit_id, keep_revision_id=int(row.id or 0)
    )
    session.commit()
    session.refresh(row)
    return row


_MUTABLE_CONTENT_STATUSES = {"DRAFT", "REJECTED"}


def _retire_superseded_revisions(
    session: Session, *, unit_id: int, keep_revision_id: int
) -> None:
    now = _now()
    rows = list(
        session.exec(
            select(KnowledgeUnitRevision).where(
                KnowledgeUnitRevision.unit_id == unit_id,
                KnowledgeUnitRevision.id != keep_revision_id,
                KnowledgeUnitRevision.lifecycle_status != "RETIRED",
            )
        ).all()
    )
    for row in rows:
        row.lifecycle_status = "RETIRED"
        row.update_time = now
        session.add(row)
        deployments = list(
            session.exec(
                select(KnowledgeDeployment).where(
                    KnowledgeDeployment.revision_id == int(row.id or 0),
                    KnowledgeDeployment.status == "ACTIVE",
                )
            ).all()
        )
        for deployment in deployments:
            _deactivate_projection_manifest(
                session, deployment.projection_manifest, keep_manifest={}
            )
            deployment.status = "RETIRED"
            deployment.update_time = now
            session.add(deployment)


def save_revision(
    session: Session,
    *,
    oid: int,
    unit_id: int,
    base_revision: int,
    content: dict[str, Any],
    actor_user_id: int | None,
    fork: bool = False,
) -> tuple[KnowledgeUnitRevision, bool]:
    """Edit content in place for mutable drafts; fork only when the revision is frozen."""
    _unit, base, _bindings, _deployments = get_unit_revision(
        session, oid=oid, unit_id=unit_id, revision=base_revision
    )
    if not fork and base.lifecycle_status in _MUTABLE_CONTENT_STATUSES:
        entry = KnowledgeUnitEntry.model_validate(content)
        base_entry = KnowledgeUnitEntry.model_validate(base.content)
        if entry.unit_id != base_entry.unit_id:
            raise ValueError("unit_id is a stable identity and cannot be changed")
        known_evidence = set(
            session.exec(
                select(KnowledgeSourceEvidence.evidence_key).where(
                    KnowledgeSourceEvidence.package_id == base.package_id
                )
            ).all()
        )
        validate_knowledge_unit(entry, known_evidence)
        entry.revision = base.revision
        now = _now()
        payload = entry.model_dump(mode="json")
        base.content = payload
        base.content_hash = _json_hash(payload)
        base.confidence = entry.confidence
        base.validation_status = "NOT_RUN"
        base.validation_summary = {
            "issues": [],
            "message": "Content updated; revalidate against the current datasource",
        }
        if base.lifecycle_status == "REJECTED":
            base.lifecycle_status = "DRAFT"
        base.update_time = now
        unit = session.get(KnowledgeUnit, unit_id)
        if unit is not None:
            unit.title = entry.title
            unit.domain = entry.domain
            unit.update_time = now
            session.add(unit)
        session.add(base)
        session.commit()
        session.refresh(base)
        return base, False
    return (
        create_revision(
            session,
            oid=oid,
            unit_id=unit_id,
            base_revision=base_revision,
            content=content,
            actor_user_id=actor_user_id,
        ),
        True,
    )


def delete_unit(session: Session, *, oid: int, unit_id: int) -> None:
    unit = session.get(KnowledgeUnit, unit_id)
    if unit is None or unit.oid != oid:
        raise ValueError("knowledge unit not found")
    revisions = list(
        session.exec(
            select(KnowledgeUnitRevision).where(
                KnowledgeUnitRevision.unit_id == unit_id
            )
        ).all()
    )
    now = _now()
    for revision in revisions:
        deployments = list(
            session.exec(
                select(KnowledgeDeployment).where(
                    KnowledgeDeployment.revision_id == int(revision.id or 0),
                    KnowledgeDeployment.status == "ACTIVE",
                )
            ).all()
        )
        for deployment in deployments:
            _deactivate_projection_manifest(
                session, deployment.projection_manifest, keep_manifest={}
            )
            deployment.status = "RETIRED"
            deployment.update_time = now
            session.add(deployment)
    session.flush()
    unit.active_revision_id = None
    session.add(unit)
    session.flush()
    session.delete(unit)
    session.commit()


def delete_package(session: Session, *, oid: int, package_row_id: int) -> None:
    package = session.get(SemanticKnowledgePackage, package_row_id)
    if package is None or package.oid != oid:
        raise ValueError("knowledge package not found")
    revisions = list(
        session.exec(
            select(KnowledgeUnitRevision).where(
                KnowledgeUnitRevision.package_id == package_row_id
            )
        ).all()
    )
    unit_ids = {int(row.unit_id) for row in revisions}
    revision_ids = {int(row.id or 0) for row in revisions if row.id is not None}
    now = _now()
    for revision in revisions:
        deployments = list(
            session.exec(
                select(KnowledgeDeployment).where(
                    KnowledgeDeployment.revision_id == int(revision.id or 0),
                    KnowledgeDeployment.status == "ACTIVE",
                )
            ).all()
        )
        for deployment in deployments:
            _deactivate_projection_manifest(
                session, deployment.projection_manifest, keep_manifest={}
            )
            deployment.status = "RETIRED"
            deployment.update_time = now
            session.add(deployment)
    session.flush()
    for unit_id in unit_ids:
        unit = session.get(KnowledgeUnit, unit_id)
        if unit is not None and unit.active_revision_id in revision_ids:
            unit.active_revision_id = None
            session.add(unit)
    session.flush()
    for revision in revisions:
        session.delete(revision)
    session.flush()
    session.delete(package)
    session.flush()
    for unit_id in unit_ids:
        remaining = int(
            session.scalar(
                select(func.count())
                .select_from(KnowledgeUnitRevision)
                .where(KnowledgeUnitRevision.unit_id == unit_id)
            )
            or 0
        )
        if remaining == 0:
            unit = session.get(KnowledgeUnit, unit_id)
            if unit is not None:
                session.delete(unit)
    session.commit()


def submit_package_review(
    session: Session, *, oid: int, package_row_id: int, actor_user_id: int | None
) -> list[str]:
    package = session.get(SemanticKnowledgePackage, package_row_id)
    if package is None or package.oid != oid:
        raise ValueError("knowledge package not found")
    rows = current_package_revisions(session, package_row_id=package_row_id)
    if not rows:
        raise ValueError("package has no active knowledge units")
    blocked: list[str] = []
    for revision, unit in rows:
        if revision.lifecycle_status == "IN_REVIEW":
            continue
        if revision.lifecycle_status != "DRAFT":
            blocked.append(f"{unit.title} is {revision.lifecycle_status}")
        elif revision.validation_status not in {"PASS", "WARNING"}:
            blocked.append(f"{unit.title} validation is {revision.validation_status}")
    if blocked:
        raise ValueError("cannot submit package for review: " + "; ".join(blocked))
    submitted: list[str] = []
    for revision, unit in rows:
        if revision.lifecycle_status == "DRAFT":
            transition_revision(
                session,
                oid=oid,
                revision_id=int(revision.id or 0),
                target="IN_REVIEW",
                actor_user_id=actor_user_id,
            )
            submitted.append(unit.unit_key)
    return submitted


def publish_revision(
    session: Session, *, oid: int, revision_id: int
) -> KnowledgeDeployment:
    revision = session.get(KnowledgeUnitRevision, revision_id)
    if revision is None or revision.oid != oid:
        raise ValueError("knowledge revision not found")
    if revision.lifecycle_status not in {
        "APPROVED",
        "RETIRED",
    } or revision.validation_status not in {"PASS", "WARNING"}:
        raise ValueError(
            "only approved or unpublished revisions that passed validation can be published"
        )
    unit = session.exec(
        select(KnowledgeUnit)
        .where(KnowledgeUnit.id == revision.unit_id)
        .with_for_update()
    ).one_or_none()
    if unit is None:
        raise ValueError("knowledge unit not found")
    binding = session.exec(
        select(KnowledgeBinding).where(
            KnowledgeBinding.revision_id == revision_id,
            KnowledgeBinding.status == "BOUND",
        )
    ).one_or_none()
    if binding is None:
        raise ValueError("knowledge revision has no valid datasource binding")
    if refresh_binding_freshness(session, binding):
        session.commit()
        raise ValueError("datasource schema changed; revalidate the knowledge binding")
    now = _now()
    deployment = session.exec(
        select(KnowledgeDeployment).where(
            KnowledgeDeployment.revision_id == revision_id,
            KnowledgeDeployment.binding_id == int(binding.id or 0),
        )
    ).one_or_none()
    if deployment is None:
        deployment = KnowledgeDeployment(
            oid=oid,
            revision_id=revision_id,
            binding_id=int(binding.id or 0),
            status="BUILDING",
            projection_manifest={},
            create_time=now,
            update_time=now,
        )
    else:
        deployment.status = "BUILDING"
        deployment.error = None
        deployment.update_time = now
    session.add(deployment)
    session.flush()
    try:
        entry = KnowledgeUnitEntry.model_validate(revision.content)
        projection_meta = {
            "unit_id": int(unit.id or 0),
            "unit_key": unit.unit_key,
            "unit_revision_id": revision_id,
            "unit_revision": revision.revision,
            "deployment_id": int(deployment.id or 0),
        }
        manifest = _build_runtime_projections(
            session,
            oid=oid,
            datasource_id=binding.datasource_id,
            entry=entry,
            mapping=binding.mapping,
            meta=projection_meta,
            now=now,
        )
        manifest.update(
            {
                "unit_revision_id": revision_id,
                "binding_id": int(binding.id or 0),
            }
        )
        previous_active = session.exec(
            select(KnowledgeDeployment).where(
                KnowledgeDeployment.oid == oid,
                KnowledgeDeployment.status == "ACTIVE",
                KnowledgeDeployment.revision_id != revision_id,
            )
        ).all()
        for active in previous_active:
            active_revision = session.get(KnowledgeUnitRevision, active.revision_id)
            if (
                active_revision is not None
                and active_revision.unit_id == revision.unit_id
            ):
                _deactivate_projection_manifest(
                    session,
                    active.projection_manifest,
                    keep_manifest=manifest,
                )
                active.status = "RETIRED"
                active.update_time = now
                session.add(active)
        deployment.projection_manifest = manifest
        deployment.status = "ACTIVE"
        deployment.activated_at = now
        deployment.update_time = now
        revision.lifecycle_status = "PUBLISHED"
        revision.update_time = now
        unit.active_revision_id = revision_id
        unit.update_time = now
        session.add(deployment)
        session.add(revision)
        session.add(unit)
        session.commit()
    except Exception as exc:
        session.rollback()
        failed = session.exec(
            select(KnowledgeDeployment).where(
                KnowledgeDeployment.revision_id == revision_id,
                KnowledgeDeployment.binding_id == int(binding.id or 0),
            )
        ).one_or_none()
        if failed is None:
            failed = KnowledgeDeployment(
                oid=oid,
                revision_id=revision_id,
                binding_id=int(binding.id or 0),
                status="ERROR",
                projection_manifest={},
                create_time=now,
                update_time=now,
            )
        failed.status = "ERROR"
        failed.error = str(exc)[:4000]
        failed.update_time = _now()
        session.add(failed)
        session.commit()
        raise ValueError(f"deployment build failed: {exc}") from exc
    session.refresh(deployment)
    return deployment


def publish_package(session: Session, *, oid: int, package_row_id: int) -> list[int]:
    rows = current_package_revisions(session, package_row_id=package_row_id)
    to_publish = [
        revision
        for revision, _unit in rows
        if revision.lifecycle_status in {"APPROVED", "RETIRED"}
    ]
    if not to_publish:
        raise ValueError(
            "package has no approved or unpublished knowledge units to publish"
        )
    deployment_ids: list[int] = []
    for revision in to_publish:
        deployment = publish_revision(
            session, oid=oid, revision_id=int(revision.id or 0)
        )
        deployment_ids.append(int(deployment.id or 0))
    return deployment_ids


def _deactivate_projection_manifest(
    session: Session,
    manifest: dict[str, Any] | None,
    *,
    keep_manifest: dict[str, Any] | None = None,
) -> None:
    """Disable disposable projections when their unit deployment is retired."""
    if not manifest:
        return
    keep_k1 = {int(item) for item in (keep_manifest or {}).get("K1", [])}
    for relation_id in manifest.get("K1", []):
        if int(relation_id) in keep_k1:
            continue
        relation = session.get(FieldRelation, int(relation_id))
        if relation is not None and relation.source == "package":
            relation.status = "RETIRED"
            relation.update_time = _now()
            session.add(relation)
    for asset_id in manifest.get("K2", []):
        row = session.get(KnowledgeAsset, int(asset_id))
        if row is not None:
            row.enabled = False
            row.valid_to = _now()
            row.update_time = _now()
            session.add(row)
    for asset_id in manifest.get("K3", []):
        row = session.get(Terminology, int(asset_id))
        if row is not None:
            row.enabled = False
            session.add(row)
    for asset_id in manifest.get("K4", []):
        row = session.get(DataTraining, int(asset_id))
        if row is not None:
            row.enabled = False
            session.add(row)
    for asset_id in manifest.get("K5", []):
        row = session.get(KnowledgeAsset, int(asset_id))
        if row is not None:
            row.enabled = False
            row.valid_to = _now()
            row.update_time = _now()
            session.add(row)


def _retire_active_deployments(session: Session, *, revision_id: int) -> None:
    now = _now()
    deployments = list(
        session.exec(
            select(KnowledgeDeployment).where(
                KnowledgeDeployment.revision_id == revision_id,
                KnowledgeDeployment.status == "ACTIVE",
            )
        ).all()
    )
    for deployment in deployments:
        _deactivate_projection_manifest(
            session, deployment.projection_manifest, keep_manifest={}
        )
        deployment.status = "RETIRED"
        deployment.update_time = now
        session.add(deployment)


def unpublish_revision(
    session: Session, *, oid: int, revision_id: int
) -> KnowledgeUnitRevision:
    """Take a published unit off the runtime path without deleting it."""
    revision = session.get(KnowledgeUnitRevision, revision_id)
    if revision is None or revision.oid != oid:
        raise ValueError("knowledge revision not found")
    if revision.lifecycle_status != "PUBLISHED":
        raise ValueError("only published revisions can be unpublished")
    unit = session.get(KnowledgeUnit, revision.unit_id)
    if unit is None:
        raise ValueError("knowledge unit not found")
    now = _now()
    _retire_active_deployments(session, revision_id=revision_id)
    revision.lifecycle_status = "RETIRED"
    revision.update_time = now
    if unit.active_revision_id == revision_id:
        unit.active_revision_id = None
        unit.update_time = now
        session.add(unit)
    session.add(revision)
    session.commit()
    session.refresh(revision)
    return revision


def unpublish_package(session: Session, *, oid: int, package_row_id: int) -> list[int]:
    rows = current_package_revisions(session, package_row_id=package_row_id)
    published = [
        revision for revision, _unit in rows if revision.lifecycle_status == "PUBLISHED"
    ]
    if not published:
        raise ValueError("package has no published knowledge units to unpublish")
    revision_ids: list[int] = []
    for revision in published:
        unpublished = unpublish_revision(
            session, oid=oid, revision_id=int(revision.id or 0)
        )
        revision_ids.append(int(unpublished.id or 0))
    return revision_ids


def _build_runtime_projections(
    session: Session,
    *,
    oid: int,
    datasource_id: int,
    entry: KnowledgeUnitEntry,
    mapping: dict[str, Any],
    meta: dict[str, Any],
    now: datetime,
) -> dict[str, list[int]]:
    """Publish only K3 locators. Unit JSON remains the source of truth."""
    del mapping
    projection: dict[str, list[int]] = {
        key: [] for key in ("K1", "K2", "K3", "K4", "K5")
    }
    terminology_rows: list[tuple[str, str, dict[str, Any]]] = []
    terminology_rows.extend(
        (word, entry.description, {**meta, "locator_kind": "unit_identity"})
        for word in [entry.title, *entry.aliases]
        if word.strip()
    )
    for concept in entry.content.concepts:
        terminology_rows.extend(
            (
                word,
                concept.definition,
                {
                    **meta,
                    "locator_kind": "concept",
                    "concept_id": concept.concept_id,
                },
            )
            for word in [concept.name, *concept.aliases]
            if word.strip()
        )
    unique_terminology: list[tuple[str, str, dict[str, Any]]] = []
    seen_words: set[str] = set()
    for word, description, knowledge_meta in terminology_rows:
        normalised = "".join(word.casefold().split())
        if not normalised or normalised in seen_words:
            continue
        seen_words.add(normalised)
        unique_terminology.append((word, description, knowledge_meta))
    terminology_vectors = build_embeddings_or_raise(
        [word for word, _description, _knowledge_meta in unique_terminology]
    )
    for index, (word, description, knowledge_meta) in enumerate(unique_terminology):
        row = Terminology(
            oid=oid,
            create_time=now,
            word=word,
            description=description,
            embedding=(
                terminology_vectors[index] if terminology_vectors is not None else None
            ),
            specific_ds=True,
            datasource_ids=[datasource_id],
            enabled=True,
            knowledge_meta=knowledge_meta,
        )
        session.add(row)
        session.flush()
        projection["K3"].append(int(row.id or 0))
    return projection


def build_embeddings_or_raise(texts: list[str]) -> list[list[float]] | None:
    """Build projection vectors before activation.

    Embeddings are part of the deployable runtime index.  When vector recall is
    enabled, a failed embedding build aborts this deployment so the previous
    active revision remains intact instead of exposing a partially searchable
    revision.
    """
    if not texts or not settings.EMBEDDING_ENABLED:
        return None
    try:
        vectors = EmbeddingModelCache.get_model().embed_documents(texts)
    except Exception as exc:
        raise ValueError("runtime projection embedding build failed") from exc
    if len(vectors) != len(texts) or any(not vector for vector in vectors):
        raise ValueError("runtime projection embedding build is incomplete")
    return vectors
