"""Knowledge Conversation plane admin APIs (staging / certify / lineage)."""

import json
from collections import Counter
from datetime import datetime
from typing import Any, Literal

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from sqlmodel import col, select

from apps.data_training.models.data_training_model import DataTraining
from apps.datasource.models.datasource import CoreField, CoreTable
from apps.datasource.profiling.models import FieldRelation, RelationStatus
from apps.knowledge.assets.caliber import (
    certify_staging_caliber,
    demote_caliber,
    disable_caliber,
)
from apps.knowledge.assets.rule import certify_staging_rule
from apps.knowledge.db_models import (
    KnowledgeAsset,
    KnowledgePackageItemRegistry,
    KnowledgePackageRegistry,
    KnowledgeStaging,
)
from apps.knowledge.importing.registry import (
    list_package_items,
    materialize_registered_package,
)
from apps.knowledge.importing.scanner import (
    scan_knowledge_documents,
    scan_knowledge_payload,
)
from apps.knowledge.importing.schema import (
    KnowledgeImportItemResult,
    KnowledgeImportReport,
    KnowledgeImportRequest,
    KnowledgeIssue,
    knowledge_issue_from_message,
)
from apps.knowledge.importing.service import (
    apply_knowledge_package,
    preview_knowledge_package,
)
from apps.knowledge.lineage import append_event, list_lineage_events, new_lineage_id
from apps.knowledge.policy import get_knowledge_policy
from apps.knowledge.staging.service import list_pending_staging
from apps.system.schemas.permission import SqlbotPermission, require_permissions
from apps.terminology.models.terminology_model import Terminology
from common.audit.models.log_model import OperationModules, OperationType
from common.audit.schemas.logger_decorator import LogConfig, system_log
from common.core.deps import CurrentUser, SessionDep, Trans

router = APIRouter(tags=["Knowledge"], prefix="/knowledge")


def _scan_import_request(body: KnowledgeImportRequest):
    package_id = body.package_id or "scanned-package"
    if body.documents:
        return scan_knowledge_documents(
            [(document.name, document.content) for document in body.documents],
            package_id=body.package_id,
        )
    assert body.package is not None
    return scan_knowledge_payload(body.package, package_id=package_id)


@router.post("/import/preview", response_model=KnowledgeImportReport)
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def preview_import(
    session: SessionDep,
    user: CurrentUser,
    body: KnowledgeImportRequest,
) -> KnowledgeImportReport:
    """Scan, classify and validate a package without changing runtime assets."""
    try:
        package = _scan_import_request(body)
        return preview_knowledge_package(
            session,
            oid=int(user.oid or 1),
            package=package,
            default_datasource_id=body.default_datasource_id,
            default_datasource_name=body.default_datasource_name,
            include_kinds=set(body.include_kinds) or None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/import/schema", response_model=dict[str, Any])
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def get_import_schema() -> dict[str, Any]:
    """Return the canonical package JSON Schema used by all import channels."""
    from apps.knowledge.importing.schema import KnowledgePackage

    return KnowledgePackage.model_json_schema()


@router.post("/import/apply", response_model=KnowledgeImportReport)
@system_log(
    LogConfig(
        operation_type=OperationType.IMPORT,
        module=OperationModules.KNOWLEDGE,
    )
)
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def apply_import(
    session: SessionDep,
    user: CurrentUser,
    trans: Trans,
    body: KnowledgeImportRequest,
) -> KnowledgeImportReport:
    """Apply ready items through the existing K1-K5 domain write contracts."""
    try:
        package = _scan_import_request(body)
        return apply_knowledge_package(
            session,
            oid=int(user.oid or 1),
            actor_user_id=int(user.id) if user.id is not None else None,
            package=package,
            trans=trans,
            default_datasource_id=body.default_datasource_id,
            default_datasource_name=body.default_datasource_name,
            include_kinds=set(body.include_kinds) or None,
            expected_preview_fingerprint=body.expected_preview_fingerprint,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


class StagingOut(BaseModel):
    id: int
    kind: str
    status: str
    natural_key: str
    trigger_id: str
    lineage_id: str
    source_record_id: int | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    scope: dict[str, Any] = Field(default_factory=dict)
    provenance: dict[str, Any] = Field(default_factory=dict)
    quality_snapshot: dict[str, Any] = Field(default_factory=dict)
    suggested_trust_tier: str | None = None
    create_time: datetime
    update_time: datetime


def _staging_out(row: KnowledgeStaging) -> StagingOut:
    return StagingOut(
        id=int(row.id or 0),
        kind=row.kind,
        status=row.status,
        natural_key=row.natural_key,
        trigger_id=row.trigger_id,
        lineage_id=row.lineage_id,
        source_record_id=row.source_record_id,
        payload=dict(row.payload or {}),
        scope=dict(row.scope or {}),
        provenance=dict(row.provenance or {}),
        quality_snapshot=dict(row.quality_snapshot or {}),
        suggested_trust_tier=row.suggested_trust_tier,
        create_time=row.create_time,
        update_time=row.update_time,
    )


class PackageItemOut(BaseModel):
    registry_item_id: int
    item_id: str
    kind: str
    source_status: str
    readiness: str
    present: bool
    payload: dict[str, Any]
    messages: list[str]
    issues: list[KnowledgeIssue] = Field(default_factory=list)
    runtime_action: str | None = None
    runtime_target_id: int | None = None


class PackageOut(BaseModel):
    package_id: str
    schema_version: str
    title: str
    description: str
    revision: int
    item_count: int
    source_count: int
    update_time: datetime


class PackageDetailOut(BaseModel):
    package: PackageOut
    sources: list[dict[str, Any]] = Field(default_factory=list)
    items: list[PackageItemOut] = Field(default_factory=list)
    total: int
    page: int
    page_size: int
    kind_counts: dict[str, int] = Field(default_factory=dict)
    readiness_counts: dict[str, int] = Field(default_factory=dict)
    action_counts: dict[str, int] = Field(default_factory=dict)


def _package_out(row: KnowledgePackageRegistry) -> PackageOut:
    return PackageOut(
        package_id=row.package_id,
        schema_version=row.schema_version,
        title=row.title,
        description=row.description,
        revision=row.revision,
        item_count=row.item_count,
        source_count=len(row.sources or []),
        update_time=row.update_time,
    )


def _package_item_out(item: KnowledgePackageItemRegistry) -> PackageItemOut:
    return PackageItemOut(
        registry_item_id=int(item.id or 0),
        item_id=item.item_id,
        kind=item.kind,
        source_status=item.source_status,
        readiness=item.readiness,
        present=item.present,
        payload=item.payload,
        messages=item.messages,
        issues=[knowledge_issue_from_message(message) for message in item.messages],
        runtime_action=item.runtime_action,
        runtime_target_id=item.runtime_target_id,
    )


@router.get("/packages", response_model=list[PackageOut])
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def get_packages(
    session: SessionDep,
    user: CurrentUser,
) -> list[PackageOut]:
    rows = session.exec(
        select(KnowledgePackageRegistry)
        .where(KnowledgePackageRegistry.oid == int(user.oid or 1))
        .order_by(col(KnowledgePackageRegistry.update_time).desc())
    ).all()
    return [_package_out(row) for row in rows]


@router.get("/packages/{package_id}", response_model=PackageDetailOut)
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def get_package_detail(
    session: SessionDep,
    user: CurrentUser,
    package_id: str,
    keyword: str = "",
    kind: str | None = None,
    readiness: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> PackageDetailOut:
    try:
        registry, rows = list_package_items(
            session,
            oid=int(user.oid or 1),
            package_id=package_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    needle = keyword.strip().casefold()
    filtered = [
        row
        for row in rows
        if (not kind or row.kind == kind)
        and (not readiness or row.readiness == readiness)
        and (
            not needle
            or needle in row.item_id.casefold()
            or needle
            in json.dumps(row.payload or {}, ensure_ascii=False, default=str).casefold()
        )
    ]
    start = (page - 1) * page_size
    return PackageDetailOut(
        package=_package_out(registry),
        sources=list(registry.sources or []),
        items=[_package_item_out(row) for row in filtered[start : start + page_size]],
        total=len(filtered),
        page=page,
        page_size=page_size,
        kind_counts=dict(Counter(row.kind for row in rows)),
        readiness_counts=dict(Counter(row.readiness for row in rows)),
        action_counts=dict(Counter(row.runtime_action or "registered" for row in rows)),
    )


@router.get("/packages/{package_id}/items", response_model=list[PackageItemOut])
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def get_package_items(
    session: SessionDep,
    user: CurrentUser,
    package_id: str,
    include_absent: bool = False,
) -> list[PackageItemOut]:
    try:
        _registry, items = list_package_items(
            session,
            oid=int(user.oid or 1),
            package_id=package_id,
            present_only=not include_absent,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return [_package_item_out(item) for item in items]


class PackageItemAdvanceIn(BaseModel):
    action: Literal["publish", "approve_publish"]
    default_datasource_id: int | None = None


@router.post(
    "/packages/{package_id}/items/{item_id}/advance",
    response_model=KnowledgeImportItemResult,
)
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def advance_package_item(
    session: SessionDep,
    user: CurrentUser,
    trans: Trans,
    package_id: str,
    item_id: str,
    body: PackageItemAdvanceIn,
) -> KnowledgeImportItemResult:
    """Advance one registered source item through its existing domain adapter."""
    try:
        registry, rows = list_package_items(
            session,
            oid=int(user.oid or 1),
            package_id=package_id,
            present_only=False,
        )
        target = next((row for row in rows if row.item_id == item_id and row.present), None)
        if target is None:
            raise ValueError("knowledge package item not found")
        reviewed_item_id: str | None = None
        if body.action == "approve_publish":
            if target.kind != "terminology" or target.readiness != "review_required":
                raise ValueError("only pending terminology can be approved directly")
            reviewed_item_id = item_id
        elif target.readiness != "ready":
            raise ValueError("only ready knowledge can be published")
        package = materialize_registered_package(
            registry,
            rows,
            reviewed_item_id=reviewed_item_id,
        )
        report = apply_knowledge_package(
            session,
            oid=int(user.oid or 1),
            actor_user_id=int(user.id) if user.id is not None else None,
            package=package,
            trans=trans,
            default_datasource_id=body.default_datasource_id,
            include_item_ids={item_id},
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    result = next((item for item in report.items if item.item_id == item_id), None)
    if result is None:
        raise HTTPException(status_code=400, detail="knowledge item was not processed")
    return result


@router.post(
    "/packages/{package_id}/items/{item_id}/reject",
    response_model=PackageItemOut,
)
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def reject_package_item(
    session: SessionDep,
    user: CurrentUser,
    package_id: str,
    item_id: str,
) -> PackageItemOut:
    try:
        registry, rows = list_package_items(
            session,
            oid=int(user.oid or 1),
            package_id=package_id,
            present_only=False,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    target = next((row for row in rows if row.item_id == item_id and row.present), None)
    if target is None:
        raise HTTPException(status_code=404, detail="knowledge package item not found")
    if target.runtime_action in {"imported", "updated", "staged", "candidate"}:
        raise HTTPException(
            status_code=400,
            detail="published or staged knowledge must be handled in its governance view",
        )
    payload = dict(target.payload or {})
    payload["status"] = "rejected"
    target.payload = payload
    target.source_status = "rejected"
    target.readiness = "invalid"
    target.runtime_action = "skipped"
    target.messages = ["item status is rejected"]
    target.update_time = datetime.utcnow()
    registry.revision += 1
    registry.update_time = datetime.utcnow()
    session.add(target)
    session.add(registry)
    session.commit()
    session.refresh(target)
    return _package_item_out(target)


class CaliberOut(BaseModel):
    id: int
    lineage_id: str
    label: str
    trust_tier: str
    certified: bool
    enabled: bool
    natural_key: str
    summary: str | None = None


class LineageEventOut(BaseModel):
    event_id: str
    action: str
    at: str
    from_tier: str | None = None
    to_tier: str | None = None
    evidence_snapshot: dict[str, Any] | None = None
    actor: dict[str, Any] | None = None


class SaveCaliberIn(BaseModel):
    """V-T3 explicit save — still lands in staging for certify."""

    label: str
    contract_fragment: dict[str, Any]
    field_targets: list[dict[str, Any]] = Field(default_factory=list)
    ds_id: int
    summary: str | None = None
    source_record_id: int | None = None


class DemoteIn(BaseModel):
    to_tier: str = "published"
    reason: str = ""


@router.get("/staging", response_model=list[StagingOut])
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def get_staging(
    session: SessionDep,
    user: CurrentUser,
    kind: str | None = None,
) -> list[StagingOut]:
    rows = list_pending_staging(session, oid=int(user.oid or 1), kind=kind)
    return [_staging_out(row) for row in rows if row.id is not None]


class ReviewItemOut(BaseModel):
    review_key: str
    source: Literal["staging", "relation", "package"]
    id: int
    kind: str
    status: str
    trigger_id: str
    package_id: str | None = None
    item_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    scope: dict[str, Any] = Field(default_factory=dict)
    provenance: dict[str, Any] = Field(default_factory=dict)
    quality_snapshot: dict[str, Any] = Field(default_factory=dict)
    issues: list[KnowledgeIssue] = Field(default_factory=list)
    actions: list[str] = Field(default_factory=list)
    create_time: datetime


class ReviewPageOut(BaseModel):
    items: list[ReviewItemOut]
    total: int
    page: int
    page_size: int
    kind_counts: dict[str, int] = Field(default_factory=dict)


def _resolved_field_ref(
    session: SessionDep,
    *,
    table_id: int,
    field_id: int,
) -> dict[str, Any]:
    table = session.get(CoreTable, table_id)
    field = session.get(CoreField, field_id)
    return {
        "table_id": table_id,
        "field_id": field_id,
        "table_name": table.table_name if table is not None else str(table_id),
        "field_name": field.field_name if field is not None else str(field_id),
    }


@router.get("/reviews", response_model=ReviewPageOut)
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def get_reviews(
    session: SessionDep,
    user: CurrentUser,
    keyword: str = "",
    kind: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> ReviewPageOut:
    oid = int(user.oid or 1)
    rows: list[ReviewItemOut] = []
    for staging in list_pending_staging(session, oid=oid, limit=500):
        if staging.id is None:
            continue
        rows.append(
            ReviewItemOut(
                review_key=f"staging:{staging.id}",
                source="staging",
                id=int(staging.id),
                kind=staging.kind,
                status=staging.status,
                trigger_id=staging.trigger_id,
                payload=dict(staging.payload or {}),
                scope=dict(staging.scope or {}),
                provenance=dict(staging.provenance or {}),
                quality_snapshot=dict(staging.quality_snapshot or {}),
                actions=["approve", "reject"],
                create_time=staging.create_time,
            )
        )
    relations = session.exec(
        select(FieldRelation).where(
            FieldRelation.oid == oid,
            FieldRelation.status == RelationStatus.CANDIDATE.value,
        )
    ).all()
    for relation in relations:
        if relation.id is None:
            continue
        rows.append(
            ReviewItemOut(
                review_key=f"relation:{relation.id}",
                source="relation",
                id=int(relation.id),
                kind="relation",
                status=relation.status,
                trigger_id=relation.source,
                payload={
                    "left": _resolved_field_ref(
                        session,
                        table_id=relation.source_table_id,
                        field_id=relation.source_field_id,
                    ),
                    "right": _resolved_field_ref(
                        session,
                        table_id=relation.target_table_id,
                        field_id=relation.target_field_id,
                    ),
                    "relation_kind": relation.kind,
                    "cardinality": relation.cardinality,
                    "confidence": relation.confidence,
                    "evidence": relation.evidence or {},
                    "datasource_id": relation.ds_id,
                },
                scope={"datasource_id": relation.ds_id},
                provenance={"source": relation.source},
                actions=["approve", "reject"],
                create_time=relation.create_time,
            )
        )
    package_rows = session.exec(
        select(KnowledgePackageItemRegistry, KnowledgePackageRegistry)
        .join(
            KnowledgePackageRegistry,
            KnowledgePackageRegistry.id
            == KnowledgePackageItemRegistry.package_registry_id,
        )
        .where(
            KnowledgePackageRegistry.oid == oid,
            KnowledgePackageItemRegistry.present.is_(True),
            KnowledgePackageItemRegistry.readiness == "review_required",
            KnowledgePackageItemRegistry.kind == "terminology",
        )
    ).all()
    for item, registry in package_rows:
        if item.id is None:
            continue
        rows.append(
            ReviewItemOut(
                review_key=f"package:{registry.package_id}:{item.item_id}",
                source="package",
                id=int(item.id),
                kind=item.kind,
                status=item.readiness,
                trigger_id="PACKAGE_IMPORT",
                package_id=registry.package_id,
                item_id=item.item_id,
                payload=dict(item.payload or {}),
                provenance={
                    **dict((item.payload or {}).get("provenance") or {}),
                    "package_id": registry.package_id,
                },
                issues=[
                    knowledge_issue_from_message(message) for message in item.messages
                ],
                actions=["approve_publish", "reject"],
                create_time=item.create_time,
            )
        )
    needle = keyword.strip().casefold()
    filtered = [
        row
        for row in rows
        if (not kind or row.kind == kind)
        and (
            not needle
            or needle in row.review_key.casefold()
            or needle
            in json.dumps(row.payload, ensure_ascii=False, default=str).casefold()
        )
    ]
    filtered.sort(key=lambda row: row.create_time, reverse=True)
    start = (page - 1) * page_size
    return ReviewPageOut(
        items=filtered[start : start + page_size],
        total=len(filtered),
        page=page,
        page_size=page_size,
        kind_counts=dict(Counter(row.kind for row in rows)),
    )


class RejectIn(BaseModel):
    reason: str = ""


@router.post("/staging/{staging_id}/reject", response_model=StagingOut)
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def reject_staging_api(
    session: SessionDep,
    user: CurrentUser,
    staging_id: int,
    body: RejectIn,
) -> StagingOut:
    from apps.knowledge.gateway import reject_staging

    try:
        staging = reject_staging(
            session,
            staging_id=staging_id,
            oid=int(user.oid or 1),
            actor_user_id=int(user.id) if user.id is not None else None,
            reason=body.reason,
        )
        session.commit()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    assert staging.id is not None
    return _staging_out(staging)


@router.post("/staging/{staging_id}/certify", response_model=CaliberOut)
@system_log(
    LogConfig(
        operation_type=OperationType.CREATE_OR_UPDATE,
        module=OperationModules.DATASOURCE,
        resource_id_expr="staging_id",
    )
)
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def certify_staging(
    session: SessionDep,
    user: CurrentUser,
    staging_id: int,
) -> CaliberOut:
    try:
        staging = session.get(KnowledgeStaging, staging_id)
        if staging is None:
            raise ValueError("staging not found")
        if staging.kind == "rule":
            certify = certify_staging_rule
        elif staging.kind == "caliber":
            certify = certify_staging_caliber
        else:
            raise ValueError(f"staging kind={staging.kind} cannot be certified here")
        caliber = certify(
            session,
            staging_id=staging_id,
            actor_user_id=int(user.id) if user.id is not None else None,
            oid=int(user.oid or 1),
        )
        session.commit()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    assert caliber.id is not None
    return CaliberOut(
        id=int(caliber.id),
        lineage_id=caliber.lineage_id,
        label=caliber.label,
        trust_tier=caliber.trust_tier,
        certified=caliber.certified,
        enabled=caliber.enabled,
        natural_key=caliber.natural_key,
        summary=caliber.summary,
    )


@router.post("/caliber/save", response_model=StagingOut)
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def save_caliber(
    session: SessionDep,
    user: CurrentUser,
    body: SaveCaliberIn,
) -> StagingOut:
    """V-T3: explicit save → staging pending via the write contract (not auto Bind)."""
    from apps.datasource.models.datasource import CoreDatasource
    from apps.knowledge.gateway import (
        KnowledgeCandidate,
        KnowledgeScope,
        submit_candidate,
    )

    oid = int(user.oid or 1)
    ds = session.get(CoreDatasource, body.ds_id)
    if ds is None or int(ds.oid or 0) != oid:
        raise HTTPException(status_code=400, detail="datasource not found in workspace")
    receipt = submit_candidate(
        session,
        KnowledgeCandidate(
            kind="caliber",
            payload={
                "label": body.label,
                "summary": body.summary,
                "contract_fragment": body.contract_fragment,
                "field_targets": body.field_targets,
            },
            scope=KnowledgeScope(oid=oid, datasource_id=body.ds_id),
            provenance={
                "source_type": "manual",
                "trigger_id": "V-T3",
                "record_id": body.source_record_id,
            },
        ),
        source_record_id=body.source_record_id,
        actor_user_id=int(user.id) if user.id is not None else None,
    )
    if receipt.action == "rejected" or receipt.staging_id is None:
        raise HTTPException(status_code=400, detail=receipt.detail or receipt.action)
    session.commit()
    staging = session.get(KnowledgeStaging, receipt.staging_id)
    assert staging is not None and staging.id is not None
    return _staging_out(staging)


@router.post("/caliber/{caliber_id}/demote", response_model=CaliberOut)
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def demote(
    session: SessionDep,
    user: CurrentUser,
    caliber_id: int,
    body: DemoteIn,
) -> CaliberOut:
    try:
        caliber = demote_caliber(
            session,
            caliber_id=caliber_id,
            oid=int(user.oid or 1),
            actor_user_id=int(user.id) if user.id is not None else None,
            to_tier=body.to_tier,
            reason=body.reason,
        )
        session.commit()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    assert caliber.id is not None
    return CaliberOut(
        id=int(caliber.id),
        lineage_id=caliber.lineage_id,
        label=caliber.label,
        trust_tier=caliber.trust_tier,
        certified=caliber.certified,
        enabled=caliber.enabled,
        natural_key=caliber.natural_key,
        summary=caliber.summary,
    )


@router.post("/caliber/{caliber_id}/disable", response_model=CaliberOut)
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def disable(
    session: SessionDep,
    user: CurrentUser,
    caliber_id: int,
) -> CaliberOut:
    try:
        caliber = disable_caliber(
            session,
            caliber_id=caliber_id,
            oid=int(user.oid or 1),
            actor_user_id=int(user.id) if user.id is not None else None,
        )
        session.commit()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    assert caliber.id is not None
    return CaliberOut(
        id=int(caliber.id),
        lineage_id=caliber.lineage_id,
        label=caliber.label,
        trust_tier=caliber.trust_tier,
        certified=caliber.certified,
        enabled=caliber.enabled,
        natural_key=caliber.natural_key,
        summary=caliber.summary,
    )


class SaveRuleIn(BaseModel):
    label: str
    content: str
    ds_id: int | None = None


class RuleOut(BaseModel):
    id: int
    label: str
    content: str
    trust_tier: str
    enabled: bool


@router.post("/rule", response_model=RuleOut)
@system_log(
    LogConfig(
        operation_type=OperationType.CREATE_OR_UPDATE,
        module=OperationModules.DATASOURCE,
    )
)
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def create_rule(
    session: SessionDep,
    user: CurrentUser,
    body: SaveRuleIn,
) -> RuleOut:
    oid = int(user.oid or 1)
    now = datetime.utcnow()
    lineage_id = new_lineage_id()
    asset = KnowledgeAsset(
        kind="rule",
        natural_key=f"rule:{oid}:{body.label}",
        lineage_id=lineage_id,
        version=1,
        oid=oid,
        datasource_id=body.ds_id,
        label=body.label,
        payload={"content": body.content},
        trust_tier="certified",
        certified=True,
        enabled=True,
        create_by=int(user.id) if user.id is not None else None,
        certify_by=int(user.id) if user.id is not None else None,
        certify_at=now,
        create_time=now,
        update_time=now,
    )
    session.add(asset)
    session.flush()
    append_event(
        session,
        lineage_id=lineage_id,
        asset_kind="rule",
        action="created",
        asset_id=asset.id,
        to_tier="certified",
        actor={"user_id": int(user.id) if user.id is not None else None},
        require_evidence=False,
    )
    session.commit()
    assert asset.id is not None
    return RuleOut(
        id=int(asset.id),
        label=asset.label,
        content=body.content,
        trust_tier=asset.trust_tier,
        enabled=asset.enabled,
    )


@router.get("/rules", response_model=list[RuleOut])
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def list_rules(
    session: SessionDep,
    user: CurrentUser,
) -> list[RuleOut]:
    oid = int(user.oid or 1)
    stmt = (
        select(KnowledgeAsset)
        .where(KnowledgeAsset.kind == "rule")
        .where(KnowledgeAsset.oid == oid)
        .where(KnowledgeAsset.valid_to.is_(None))  # type: ignore[attr-defined]
        .order_by(col(KnowledgeAsset.create_time).desc())
    )
    rows = list(session.exec(stmt).all())
    return [
        RuleOut(
            id=int(r.id),  # type: ignore[arg-type]
            label=r.label,
            content=(r.payload or {}).get("content", ""),
            trust_tier=r.trust_tier,
            enabled=r.enabled,
        )
        for r in rows
        if r.id is not None
    ]


@router.post("/rule/{rule_id}/disable", response_model=RuleOut)
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def disable_rule(
    session: SessionDep,
    user: CurrentUser,
    rule_id: int,
) -> RuleOut:
    oid = int(user.oid or 1)
    asset = session.get(KnowledgeAsset, rule_id)
    if asset is None or int(asset.oid) != oid or asset.kind != "rule":
        raise HTTPException(status_code=404, detail="rule not found")
    asset.enabled = False
    asset.update_time = datetime.utcnow()
    session.add(asset)
    session.commit()
    return RuleOut(
        id=int(asset.id),  # type: ignore[arg-type]
        label=asset.label,
        content=(asset.payload or {}).get("content", ""),
        trust_tier=asset.trust_tier,
        enabled=asset.enabled,
    )


@router.post("/rule/{rule_id}/enable", response_model=RuleOut)
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def enable_rule(
    session: SessionDep,
    user: CurrentUser,
    rule_id: int,
) -> RuleOut:
    oid = int(user.oid or 1)
    asset = session.get(KnowledgeAsset, rule_id)
    if asset is None or int(asset.oid) != oid or asset.kind != "rule":
        raise HTTPException(status_code=404, detail="rule not found")
    asset.enabled = True
    asset.update_time = datetime.utcnow()
    session.add(asset)
    session.commit()
    return RuleOut(
        id=int(asset.id),  # type: ignore[arg-type]
        label=asset.label,
        content=(asset.payload or {}).get("content", ""),
        trust_tier=asset.trust_tier,
        enabled=asset.enabled,
    )


@router.post("/caliber/{caliber_id}/promote-trusted", response_model=CaliberOut)
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def promote_trusted(
    session: SessionDep,
    user: CurrentUser,
    caliber_id: int,
) -> CaliberOut:
    """Promote a published caliber to trusted if server-side evidence is sufficient."""
    from apps.knowledge.assets.caliber import promote_to_trusted

    policy = get_knowledge_policy()
    try:
        asset = promote_to_trusted(
            session,
            caliber_id=caliber_id,
            oid=int(user.oid or 1),
            policy_n=policy.reproduce_count_n,
            positive_feedback_n=policy.positive_feedback_count_n,
            actor_user_id=int(user.id) if user.id is not None else None,
        )
        session.commit()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    assert asset.id is not None
    return CaliberOut(
        id=int(asset.id),
        lineage_id=asset.lineage_id,
        label=asset.label,
        trust_tier=asset.trust_tier,
        certified=asset.certified,
        enabled=asset.enabled,
        natural_key=asset.natural_key,
        summary=asset.summary,
    )


class SuggestionOut(BaseModel):
    id: int
    lineage_id: str
    label: str
    trust_tier: str
    reproduce_count: int
    successful_apply_count: int
    positive_feedback_count: int
    negative_feedback_count: int
    requires_review: bool
    recommended_action: str


@router.get("/suggestions", response_model=list[SuggestionOut])
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def list_suggestions(
    session: SessionDep,
    user: CurrentUser,
) -> list[SuggestionOut]:
    """Assets at published tier with enough evidence to upgrade."""
    oid = int(user.oid or 1)
    policy = get_knowledge_policy()
    stmt = (
        select(KnowledgeAsset)
        .where(KnowledgeAsset.oid == oid)
        .where(KnowledgeAsset.trust_tier == "published")
        .where(KnowledgeAsset.enabled.is_(True))  # type: ignore[attr-defined]
        .where(KnowledgeAsset.valid_to.is_(None))  # type: ignore[attr-defined]
    )
    from apps.knowledge.evidence_policy import summarize_asset_evidence

    suggestions: list[SuggestionOut] = []
    for asset in session.exec(stmt).all():
        if asset.id is None:
            continue
        summary = summarize_asset_evidence(
            session, asset_id=int(asset.id), asset_kind=asset.kind
        )
        ready = summary.promotion_ready(
            reproduce_threshold=policy.reproduce_count_n,
            positive_feedback_threshold=policy.positive_feedback_count_n,
        )
        if not ready and not summary.requires_review:
            continue
        suggestions.append(
            SuggestionOut(
                id=int(asset.id),
                lineage_id=asset.lineage_id,
                label=asset.label,
                trust_tier=asset.trust_tier,
                reproduce_count=summary.reproduce_count,
                successful_apply_count=summary.successful_apply_count,
                positive_feedback_count=summary.positive_feedback_count,
                negative_feedback_count=summary.negative_feedback_count,
                requires_review=summary.requires_review,
                recommended_action="review" if summary.requires_review else "promote",
            )
        )
    return suggestions


class AssetOut(BaseModel):
    id: int
    kind: str
    lineage_id: str
    label: str
    summary: str | None = None
    trust_tier: str
    certified: bool
    enabled: bool
    natural_key: str
    datasource_id: int | None = None
    create_time: str | None = None


class RuntimeKnowledgeOut(BaseModel):
    id: int
    kind: str
    label: str
    summary: str = ""
    trust_tier: str
    enabled: bool
    datasource_id: int | None = None
    source: str
    create_time: datetime | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class RuntimeKnowledgePageOut(BaseModel):
    items: list[RuntimeKnowledgeOut]
    total: int
    page: int
    page_size: int
    kind_counts: dict[str, int] = Field(default_factory=dict)


@router.get("/runtime-assets", response_model=RuntimeKnowledgePageOut)
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def list_runtime_knowledge(
    session: SessionDep,
    user: CurrentUser,
    keyword: str = "",
    kind: str | None = None,
    enabled: bool | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> RuntimeKnowledgePageOut:
    """Unified read model of knowledge that can participate in runtime recall."""
    oid = int(user.oid or 1)
    items: list[RuntimeKnowledgeOut] = []
    assets = session.exec(
        select(KnowledgeAsset).where(
            KnowledgeAsset.oid == oid,
            KnowledgeAsset.valid_to.is_(None),  # type: ignore[attr-defined]
        )
    ).all()
    for asset in assets:
        if asset.id is None:
            continue
        items.append(
            RuntimeKnowledgeOut(
                id=int(asset.id),
                kind=asset.kind,
                label=asset.label,
                summary=asset.summary or "",
                trust_tier=asset.trust_tier,
                enabled=asset.enabled,
                datasource_id=asset.datasource_id,
                source="knowledge_asset",
                create_time=asset.create_time,
                payload={
                    **dict(asset.payload or {}),
                    "provenance": asset.provenance or {},
                    "lineage_id": asset.lineage_id,
                },
            )
        )
    terminology_rows = session.exec(
        select(Terminology).where(Terminology.oid == oid)
    ).all()
    aliases: dict[int, list[str]] = {}
    for term in terminology_rows:
        if term.pid is not None and term.word:
            aliases.setdefault(int(term.pid), []).append(term.word)
    for term in terminology_rows:
        if term.id is None or term.pid is not None:
            continue
        datasource_ids = list(term.datasource_ids or [])
        items.append(
            RuntimeKnowledgeOut(
                id=int(term.id),
                kind="terminology",
                label=term.word or "",
                summary=term.description or "",
                trust_tier="published",
                enabled=bool(term.enabled),
                datasource_id=(int(datasource_ids[0]) if len(datasource_ids) == 1 else None),
                source="terminology",
                create_time=term.create_time,
                payload={
                    "word": term.word,
                    "description": term.description,
                    "aliases": aliases.get(int(term.id), []),
                    "specific_ds": term.specific_ds,
                    "datasource_ids": datasource_ids,
                    "assistant_id": term.advanced_application,
                    "knowledge_meta": term.knowledge_meta or {},
                },
            )
        )
    examples = session.exec(select(DataTraining).where(DataTraining.oid == oid)).all()
    for example in examples:
        if example.id is None:
            continue
        items.append(
            RuntimeKnowledgeOut(
                id=int(example.id),
                kind="example",
                label=example.question or "",
                summary=example.description or "",
                trust_tier="published",
                enabled=bool(example.enabled),
                datasource_id=(int(example.datasource) if example.datasource is not None else None),
                source="data_training",
                create_time=example.create_time,
                payload={
                    "question": example.question,
                    "query": example.description,
                    "training_type": example.training_type,
                    "assistant_id": example.advanced_application,
                    "knowledge_meta": example.knowledge_meta or {},
                },
            )
        )
    relations = session.exec(
        select(FieldRelation).where(
            FieldRelation.oid == oid,
            FieldRelation.status == RelationStatus.CONFIRMED.value,
        )
    ).all()
    for relation in relations:
        if relation.id is None:
            continue
        left = _resolved_field_ref(
            session,
            table_id=relation.source_table_id,
            field_id=relation.source_field_id,
        )
        right = _resolved_field_ref(
            session,
            table_id=relation.target_table_id,
            field_id=relation.target_field_id,
        )
        label = (
            f"{left['table_name']}.{left['field_name']} ↔ "
            f"{right['table_name']}.{right['field_name']}"
        )
        items.append(
            RuntimeKnowledgeOut(
                id=int(relation.id),
                kind="relation",
                label=label,
                summary=f"{relation.kind} · {relation.cardinality or '-'}",
                trust_tier="confirmed",
                enabled=True,
                datasource_id=relation.ds_id,
                source="field_relation",
                create_time=relation.create_time,
                payload={
                    "left": left,
                    "right": right,
                    "relation_kind": relation.kind,
                    "cardinality": relation.cardinality,
                    "confidence": relation.confidence,
                    "evidence": relation.evidence or {},
                },
            )
        )
    needle = keyword.strip().casefold()
    searchable = [
        item
        for item in items
        if (enabled is None or item.enabled is enabled)
        and (
            not needle
            or needle in item.label.casefold()
            or needle in item.summary.casefold()
        )
    ]
    kind_counts = dict(Counter(item.kind for item in searchable))
    filtered = [item for item in searchable if not kind or item.kind == kind]
    filtered.sort(key=lambda item: item.create_time or datetime.min, reverse=True)
    start = (page - 1) * page_size
    return RuntimeKnowledgePageOut(
        items=filtered[start : start + page_size],
        total=len(filtered),
        page=page,
        page_size=page_size,
        kind_counts=kind_counts,
    )


@router.get("/assets", response_model=list[AssetOut])
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def list_assets(
    session: SessionDep,
    user: CurrentUser,
    kind: str | None = None,
    trust_tier: str | None = None,
    enabled: bool | None = None,
) -> list[AssetOut]:
    oid = int(user.oid or 1)
    stmt = (
        select(KnowledgeAsset)
        .where(KnowledgeAsset.oid == oid)
        .where(KnowledgeAsset.valid_to.is_(None))  # type: ignore[attr-defined]
        .order_by(col(KnowledgeAsset.create_time).desc())
        .limit(200)
    )
    if kind:
        stmt = stmt.where(KnowledgeAsset.kind == kind)
    if trust_tier:
        stmt = stmt.where(KnowledgeAsset.trust_tier == trust_tier)
    if enabled is not None:
        stmt = stmt.where(KnowledgeAsset.enabled == enabled)
    rows = list(session.exec(stmt).all())
    return [
        AssetOut(
            id=int(r.id),  # type: ignore[arg-type]
            kind=r.kind,
            lineage_id=r.lineage_id,
            label=r.label,
            summary=r.summary,
            trust_tier=r.trust_tier,
            certified=r.certified,
            enabled=r.enabled,
            natural_key=r.natural_key,
            datasource_id=r.datasource_id,
            create_time=r.create_time.isoformat() if r.create_time else None,
        )
        for r in rows
        if r.id is not None
    ]


@router.get("/assets/{kind}/{asset_id}/lineage", response_model=list[LineageEventOut])
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def get_lineage(
    session: SessionDep,
    user: CurrentUser,
    kind: str,
    asset_id: int,
) -> list[LineageEventOut]:
    oid = int(user.oid or 1)
    lineage_id: str | None = None
    if kind == "caliber":
        caliber = session.get(KnowledgeAsset, asset_id)
        if caliber is None or int(caliber.oid) != oid:
            raise HTTPException(status_code=404, detail="asset not found")
        lineage_id = caliber.lineage_id
    elif kind == "staging":
        staging = session.get(KnowledgeStaging, asset_id)
        if staging is None or int(staging.oid) != oid:
            raise HTTPException(status_code=404, detail="asset not found")
        lineage_id = staging.lineage_id
    else:
        raise HTTPException(status_code=404, detail="asset not found")
    events = list_lineage_events(session, lineage_id=lineage_id)
    return [
        LineageEventOut(
            event_id=e.event_id,
            action=e.action,
            at=e.at.isoformat() if e.at else "",
            from_tier=e.from_tier,
            to_tier=e.to_tier,
            evidence_snapshot=e.evidence_snapshot,
            actor=e.actor,
        )
        for e in events
    ]
