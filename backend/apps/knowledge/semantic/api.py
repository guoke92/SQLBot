"""Knowledge 2.0 APIs: package -> unit revision -> binding -> deployment."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlmodel import col, select

from apps.knowledge.db_models import (
    KnowledgeBinding,
    KnowledgeDeployment,
    KnowledgeSourceEvidence,
    KnowledgeUnit,
    KnowledgeUnitRevision,
    SemanticKnowledgePackage,
)
from apps.knowledge.semantic.scanner import (
    scan_package_documents,
    scan_package_files,
    scan_package_payload,
)
from apps.knowledge.semantic.schema import KnowledgePackageV2
from apps.knowledge.semantic.service import (
    _next_step,
    bind_and_validate,
    current_package_entries,
    current_package_revisions,
    delete_package,
    delete_unit,
    derive_package_status,
    get_unit_revision,
    list_packages,
    list_units,
    publish_package,
    publish_revision,
    recommend_datasources,
    refresh_binding_freshness,
    register_package,
    save_revision,
    submit_package_review,
    transition_revision,
    unpublish_package,
    unpublish_revision,
    validation_preview,
)
from apps.system.schemas.permission import SqlbotPermission, require_permissions
from common.core.deps import CurrentUser, SessionDep

router = APIRouter(tags=["Knowledge 2.0"], prefix="/knowledge")


class PackageDocumentIn(BaseModel):
    name: str
    content: str


class PackageImportIn(BaseModel):
    package: dict[str, Any] | str | None = None
    documents: list[PackageDocumentIn] = Field(default_factory=list)

    def parse(self) -> KnowledgePackageV2:
        if self.package is not None and self.documents:
            raise ValueError("package and documents are mutually exclusive")
        if self.documents:
            return scan_package_documents(
                [(document.name, document.content) for document in self.documents]
            )
        if self.package is None:
            raise ValueError("package or documents is required")
        return scan_package_payload(self.package)


class BindIn(BaseModel):
    datasource_id: int


class ReviewDecisionIn(BaseModel):
    reason: str = Field(default="", max_length=2000)


async def _parse_uploads(files: list[UploadFile]) -> KnowledgePackageV2:
    if not files:
        raise HTTPException(status_code=400, detail="select a knowledge package")
    try:
        return scan_package_files(
            [
                (file.filename or "knowledge-package.yaml", await file.read())
                for file in files
            ]
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _package_summary(
    row: SemanticKnowledgePackage,
    unit_count: int,
    status: str | None = None,
) -> dict[str, Any]:
    return {
        "id": int(row.id or 0),
        "package_id": row.package_id,
        "revision": row.revision,
        "schema_version": row.schema_version,
        "namespace": row.namespace,
        "title": row.title,
        "description": row.description,
        "status": status or row.status,
        "unit_count": unit_count,
        "update_time": row.update_time,
    }


def _get_package(
    session: SessionDep,
    *,
    oid: int,
    package_id: str,
    revision: int | None,
) -> SemanticKnowledgePackage:
    statement = select(SemanticKnowledgePackage).where(
        SemanticKnowledgePackage.oid == oid,
        SemanticKnowledgePackage.package_id == package_id,
    )
    if revision is not None:
        statement = statement.where(SemanticKnowledgePackage.revision == revision)
    row = session.exec(
        statement.order_by(col(SemanticKnowledgePackage.revision).desc())
    ).first()
    if row is None:
        raise HTTPException(status_code=404, detail="knowledge package not found")
    return row


@router.post("/packages/upload", response_model=dict[str, Any])
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def import_uploaded_package(
    session: SessionDep,
    user: CurrentUser,
    files: Annotated[list[UploadFile], File()],
) -> dict[str, Any]:
    package = await _parse_uploads(files)
    try:
        row, revisions, created = register_package(
            session,
            oid=int(user.oid or 1),
            actor_user_id=int(user.id) if user.id is not None else None,
            package=package,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "package": _package_summary(row, len(revisions)),
        "created": created,
        "revisions": [int(revision.id or 0) for revision in revisions],
    }


@router.post("/packages", response_model=dict[str, Any])
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def import_package(
    session: SessionDep, user: CurrentUser, body: PackageImportIn
) -> dict[str, Any]:
    try:
        package = body.parse()
        row, revisions, created = register_package(
            session,
            oid=int(user.oid or 1),
            actor_user_id=int(user.id) if user.id is not None else None,
            package=package,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "package": _package_summary(row, len(revisions)),
        "created": created,
        "revisions": [int(revision.id or 0) for revision in revisions],
    }


@router.get("/packages", response_model=dict[str, Any])
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def packages(
    session: SessionDep,
    user: CurrentUser,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> dict[str, Any]:
    rows, total = list_packages(
        session, oid=int(user.oid or 1), page=page, page_size=page_size
    )
    items = []
    for row in rows:
        current = current_package_revisions(session, package_row_id=int(row.id or 0))
        items.append(
            _package_summary(
                row,
                len(current),
                derive_package_status([revision for revision, _unit in current]),
            )
        )
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/packages/{package_id}", response_model=dict[str, Any])
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def package_detail(
    session: SessionDep,
    user: CurrentUser,
    package_id: str,
    revision: int | None = Query(default=None, ge=1),
) -> dict[str, Any]:
    row = _get_package(
        session,
        oid=int(user.oid or 1),
        package_id=package_id,
        revision=revision,
    )
    current = current_package_revisions(session, package_row_id=int(row.id or 0))
    units: list[dict[str, Any]] = []
    for revision, unit in current:
        binding = session.exec(
            select(KnowledgeBinding)
            .where(KnowledgeBinding.revision_id == int(revision.id or 0))
            .order_by(col(KnowledgeBinding.update_time).desc())
        ).first()
        units.append(
            {
                "unit_id": int(unit.id or 0),
                "unit_key": unit.unit_key,
                "title": unit.title,
                "domain": unit.domain,
                "revision": revision.revision,
                "revision_id": int(revision.id or 0),
                "lifecycle_status": revision.lifecycle_status,
                "validation_status": revision.validation_status,
                "binding_status": binding.status if binding else "UNBOUND",
                "datasource_id": binding.datasource_id if binding else None,
                "next_step": _next_step(revision, binding),
                **validation_preview(revision.validation_summary),
            }
        )
    units.sort(key=lambda item: (str(item["domain"]), str(item["title"])))
    return {
        "package": _package_summary(
            row,
            len(current),
            derive_package_status([revision for revision, _unit in current]),
        ),
        "sources": list(row.source_document.get("sources") or []),
        "evidence_count": len(row.source_document.get("evidence") or []),
        "units": units,
    }


@router.get("/packages/{package_id}/binding-candidates", response_model=dict[str, Any])
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def package_binding_candidates(
    session: SessionDep,
    user: CurrentUser,
    package_id: str,
    revision: int | None = Query(default=None, ge=1),
) -> dict[str, Any]:
    row = _get_package(
        session,
        oid=int(user.oid or 1),
        package_id=package_id,
        revision=revision,
    )
    entries = current_package_entries(session, package_row_id=int(row.id or 0))
    return {
        "items": recommend_datasources(session, oid=int(user.oid or 1), entries=entries)
        if entries
        else []
    }


@router.post("/packages/{package_id}/bind", response_model=dict[str, Any])
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def bind_package(
    session: SessionDep,
    user: CurrentUser,
    package_id: str,
    body: BindIn,
    revision: int | None = Query(default=None, ge=1),
) -> dict[str, Any]:
    package = _get_package(
        session,
        oid=int(user.oid or 1),
        package_id=package_id,
        revision=revision,
    )
    revisions = [
        revision_row
        for revision_row, _unit in current_package_revisions(
            session, package_row_id=int(package.id or 0)
        )
    ]
    if not revisions:
        raise HTTPException(status_code=400, detail="package has no active knowledge units")
    entries = current_package_entries(session, package_row_id=int(package.id or 0))
    candidates = recommend_datasources(session, oid=int(user.oid or 1), entries=entries)
    datasource_id = body.datasource_id
    selected = next(
        (
            candidate
            for candidate in candidates
            if candidate["datasource_id"] == datasource_id
        ),
        None,
    )
    if selected is None:
        raise HTTPException(status_code=400, detail="datasource not found")

    results: list[dict[str, Any]] = []
    for revision_row in revisions:
        try:
            binding = bind_and_validate(
                session,
                oid=int(user.oid or 1),
                revision_id=int(revision_row.id or 0),
                datasource_id=datasource_id,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        result = binding.model_dump(mode="json")
        result["unit_revision_id"] = int(revision_row.id or 0)
        result["validation_preview"] = validation_preview(binding.validation_result)
        results.append(result)
    failed = [
        item
        for item in results
        if str((item.get("validation_result") or {}).get("status") or "") == "FAIL"
    ]
    return {
        "package_id": package_id,
        "datasource_id": datasource_id,
        "status": derive_package_status(revisions),
        "bindings": results,
        "package_issue": (
            {
                "code": "DATASOURCE_CATALOG_MISMATCH",
                "severity": "warning" if not failed else "error",
                "message": (
                    "The selected datasource does not contain every declared dataset. "
                    "Binding still ran so each unit can show the missing tables."
                ),
                "missing_datasets": selected["missing"],
            }
            if float(selected["coverage"]) < 1
            else None
        ),
    }


@router.post("/packages/{package_id}/validate", response_model=dict[str, Any])
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def validate_package(
    session: SessionDep,
    user: CurrentUser,
    package_id: str,
    revision: int | None = Query(default=None, ge=1),
) -> dict[str, Any]:
    package = _get_package(
        session,
        oid=int(user.oid or 1),
        package_id=package_id,
        revision=revision,
    )
    revisions = [
        revision
        for revision, _unit in current_package_revisions(
            session, package_row_id=int(package.id or 0)
        )
    ]
    results: list[dict[str, Any]] = []
    skipped: list[int] = []
    for revision_row in revisions:
        binding = session.exec(
            select(KnowledgeBinding)
            .where(KnowledgeBinding.revision_id == int(revision_row.id or 0))
            .order_by(col(KnowledgeBinding.update_time).desc())
        ).first()
        if binding is None or not binding.datasource_id:
            skipped.append(int(revision_row.id or 0))
            continue
        try:
            updated = bind_and_validate(
                session,
                oid=int(user.oid or 1),
                revision_id=int(revision_row.id or 0),
                datasource_id=binding.datasource_id,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        result = updated.model_dump(mode="json")
        result["validation_preview"] = validation_preview(updated.validation_result)
        results.append(result)
    return {
        "package_id": package_id,
        "status": derive_package_status(revisions),
        "bindings": results,
        "skipped_unbound": skipped,
    }


@router.post("/packages/{package_id}/submit-review", response_model=dict[str, Any])
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def submit_package_for_review(
    session: SessionDep,
    user: CurrentUser,
    package_id: str,
    revision: int | None = Query(default=None, ge=1),
) -> dict[str, Any]:
    package = _get_package(
        session,
        oid=int(user.oid or 1),
        package_id=package_id,
        revision=revision,
    )
    try:
        submitted = submit_package_review(
            session,
            oid=int(user.oid or 1),
            package_row_id=int(package.id or 0),
            actor_user_id=int(user.id) if user.id is not None else None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "package_id": package_id,
        "status": "IN_REVIEW",
        "submitted_units": submitted,
    }


@router.post("/packages/{package_id}/publish", response_model=dict[str, Any])
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def publish_package_api(
    session: SessionDep,
    user: CurrentUser,
    package_id: str,
    revision: int | None = Query(default=None, ge=1),
) -> dict[str, Any]:
    package = _get_package(
        session,
        oid=int(user.oid or 1),
        package_id=package_id,
        revision=revision,
    )
    try:
        deployment_ids = publish_package(
            session, oid=int(user.oid or 1), package_row_id=int(package.id or 0)
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "package_id": package_id,
        "status": "PUBLISHED",
        "deployment_ids": deployment_ids,
    }


@router.post("/packages/{package_id}/unpublish", response_model=dict[str, Any])
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def unpublish_package_api(
    session: SessionDep,
    user: CurrentUser,
    package_id: str,
    revision: int | None = Query(default=None, ge=1),
) -> dict[str, Any]:
    package = _get_package(
        session,
        oid=int(user.oid or 1),
        package_id=package_id,
        revision=revision,
    )
    try:
        revision_ids = unpublish_package(
            session, oid=int(user.oid or 1), package_row_id=int(package.id or 0)
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    current = current_package_revisions(session, package_row_id=int(package.id or 0))
    return {
        "package_id": package_id,
        "status": derive_package_status([row for row, _unit in current]),
        "unpublished_revision_ids": revision_ids,
    }


@router.delete("/packages/{package_id}", response_model=dict[str, Any])
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def delete_package_api(
    session: SessionDep,
    user: CurrentUser,
    package_id: str,
    revision: int | None = Query(default=None, ge=1),
) -> dict[str, Any]:
    package = _get_package(
        session,
        oid=int(user.oid or 1),
        package_id=package_id,
        revision=revision,
    )
    try:
        delete_package(
            session, oid=int(user.oid or 1), package_row_id=int(package.id or 0)
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"ok": True, "package_id": package_id}


@router.get("/units", response_model=dict[str, Any])
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def units(
    session: SessionDep,
    user: CurrentUser,
    keyword: str = "",
    lifecycle: str | None = None,
    validation: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> dict[str, Any]:
    rows, total, counts = list_units(
        session,
        oid=int(user.oid or 1),
        keyword=keyword,
        lifecycle=lifecycle,
        validation=validation,
        page=page,
        page_size=page_size,
    )
    return {
        "items": rows,
        "total": total,
        "page": page,
        "page_size": page_size,
        "lifecycle_counts": counts,
    }


@router.get("/units/{unit_id}/revisions/{revision}", response_model=dict[str, Any])
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def unit_revision_detail(
    session: SessionDep, user: CurrentUser, unit_id: int, revision: int
) -> dict[str, Any]:
    try:
        unit, row, bindings, deployments = get_unit_revision(
            session, oid=int(user.oid or 1), unit_id=unit_id, revision=revision
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {
        "unit": {
            "id": int(unit.id or 0),
            "unit_key": unit.unit_key,
            "namespace": unit.namespace,
            "domain": unit.domain,
            "title": unit.title,
        },
        "revision": {
            "id": int(row.id or 0),
            "revision": row.revision,
            "lifecycle_status": row.lifecycle_status,
            "validation_status": row.validation_status,
            "validation_summary": row.validation_summary,
            "confidence": row.confidence,
            "content": row.content,
        },
        "evidence": [
            {
                **evidence.model_dump(mode="json"),
                "reference_id": str(
                    (evidence.payload or {}).get("evidence_id") or evidence.evidence_key
                ),
            }
            for evidence in session.exec(
                select(KnowledgeSourceEvidence).where(
                    KnowledgeSourceEvidence.package_id == int(row.package_id or 0),
                    KnowledgeSourceEvidence.active.is_(True),
                )
            ).all()
        ],
        "bindings": [binding.model_dump(mode="json") for binding in bindings],
        "deployments": [
            deployment.model_dump(mode="json") for deployment in deployments
        ],
    }


class RevisionEditIn(BaseModel):
    content: dict[str, Any]
    fork: bool = False


@router.patch("/units/{unit_id}/revisions/{revision}", response_model=dict[str, Any])
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def edit_revision(
    session: SessionDep,
    user: CurrentUser,
    unit_id: int,
    revision: int,
    body: RevisionEditIn,
) -> dict[str, Any]:
    try:
        row, forked = save_revision(
            session,
            oid=int(user.oid or 1),
            unit_id=unit_id,
            base_revision=revision,
            content=body.content,
            actor_user_id=int(user.id) if user.id is not None else None,
            fork=body.fork,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "revision_id": int(row.id or 0),
        "revision": row.revision,
        "status": row.lifecycle_status,
        "forked": forked,
        "validation_status": row.validation_status,
    }


async def _transition(
    session: SessionDep,
    user: CurrentUser,
    unit_id: int,
    revision: int,
    target: str,
    reason: str = "",
) -> dict[str, Any]:
    try:
        _unit, row, _bindings, _deployments = get_unit_revision(
            session, oid=int(user.oid or 1), unit_id=unit_id, revision=revision
        )
        row = transition_revision(
            session,
            oid=int(user.oid or 1),
            revision_id=int(row.id or 0),
            target=target,
            actor_user_id=int(user.id) if user.id is not None else None,
            reason=reason,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"revision_id": int(row.id or 0), "lifecycle_status": row.lifecycle_status}


@router.delete("/units/{unit_id}", response_model=dict[str, Any])
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def delete_unit_api(
    session: SessionDep, user: CurrentUser, unit_id: int
) -> dict[str, Any]:
    try:
        delete_unit(session, oid=int(user.oid or 1), unit_id=unit_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"ok": True, "unit_id": unit_id}


@router.post("/units/{unit_id}/revisions/{revision}/approve")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def approve(
    session: SessionDep,
    user: CurrentUser,
    unit_id: int,
    revision: int,
    body: ReviewDecisionIn | None = None,
) -> dict[str, Any]:
    return await _transition(
        session, user, unit_id, revision, "APPROVED", body.reason if body else ""
    )


@router.post("/units/{unit_id}/revisions/{revision}/reject")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def reject(
    session: SessionDep,
    user: CurrentUser,
    unit_id: int,
    revision: int,
    body: ReviewDecisionIn | None = None,
) -> dict[str, Any]:
    if body is None or not body.reason.strip():
        raise HTTPException(status_code=400, detail="reject requires a reason")
    return await _transition(session, user, unit_id, revision, "REJECTED", body.reason)


@router.post("/units/{unit_id}/revisions/{revision}/request-changes")
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def request_changes(
    session: SessionDep,
    user: CurrentUser,
    unit_id: int,
    revision: int,
    body: ReviewDecisionIn,
) -> dict[str, Any]:
    if not body.reason.strip():
        raise HTTPException(status_code=400, detail="request changes requires a reason")
    return await _transition(session, user, unit_id, revision, "DRAFT", body.reason)


@router.post(
    "/units/{unit_id}/revisions/{revision}/publish", response_model=dict[str, Any]
)
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def publish(
    session: SessionDep, user: CurrentUser, unit_id: int, revision: int
) -> dict[str, Any]:
    try:
        _unit, row, _bindings, _deployments = get_unit_revision(
            session, oid=int(user.oid or 1), unit_id=unit_id, revision=revision
        )
        deployment = publish_revision(
            session, oid=int(user.oid or 1), revision_id=int(row.id or 0)
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return deployment.model_dump(mode="json")


@router.post(
    "/units/{unit_id}/revisions/{revision}/unpublish", response_model=dict[str, Any]
)
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def unpublish(
    session: SessionDep, user: CurrentUser, unit_id: int, revision: int
) -> dict[str, Any]:
    try:
        _unit, row, _bindings, _deployments = get_unit_revision(
            session, oid=int(user.oid or 1), unit_id=unit_id, revision=revision
        )
        unpublished = unpublish_revision(
            session, oid=int(user.oid or 1), revision_id=int(row.id or 0)
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "revision_id": int(unpublished.id or 0),
        "lifecycle_status": unpublished.lifecycle_status,
    }


@router.get("/deployments", response_model=dict[str, Any])
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def deployments(
    session: SessionDep,
    user: CurrentUser,
    status: Literal["ACTIVE", "ERROR", "RETIRED"] | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> dict[str, Any]:
    statement = (
        select(
            KnowledgeDeployment,
            KnowledgeUnitRevision,
            KnowledgeUnit,
            KnowledgeBinding,
        )
        .join(
            KnowledgeUnitRevision,
            KnowledgeUnitRevision.id == KnowledgeDeployment.revision_id,
        )
        .join(KnowledgeUnit, KnowledgeUnit.id == KnowledgeUnitRevision.unit_id)
        .join(KnowledgeBinding, KnowledgeBinding.id == KnowledgeDeployment.binding_id)
        .where(KnowledgeDeployment.oid == int(user.oid or 1))
    )
    if status:
        statement = statement.where(KnowledgeDeployment.status == status)
    total = int(
        session.scalar(select(func.count()).select_from(statement.subquery())) or 0
    )
    rows = list(
        session.exec(
            statement.order_by(col(KnowledgeDeployment.update_time).desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
    )
    binding_changed = False
    for _deployment, _revision, _unit, binding in rows:
        binding_changed = refresh_binding_freshness(session, binding) or binding_changed
    if binding_changed:
        session.commit()
    return {
        "items": [
            {
                **deployment.model_dump(mode="json"),
                "unit_id": int(unit.id or 0),
                "unit_key": unit.unit_key,
                "unit_title": unit.title,
                "unit_domain": unit.domain,
                "revision": revision.revision,
                "lifecycle_status": revision.lifecycle_status,
                "datasource_id": binding.datasource_id,
                "binding_status": binding.status,
            }
            for deployment, revision, unit, binding in rows
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/deployments/{deployment_id}", response_model=dict[str, Any])
@require_permissions(permission=SqlbotPermission(role=["ws_admin"]))
async def deployment_detail(
    session: SessionDep, user: CurrentUser, deployment_id: int
) -> dict[str, Any]:
    row = session.exec(
        select(
            KnowledgeDeployment,
            KnowledgeUnitRevision,
            KnowledgeUnit,
            KnowledgeBinding,
        )
        .join(
            KnowledgeUnitRevision,
            KnowledgeUnitRevision.id == KnowledgeDeployment.revision_id,
        )
        .join(KnowledgeUnit, KnowledgeUnit.id == KnowledgeUnitRevision.unit_id)
        .join(KnowledgeBinding, KnowledgeBinding.id == KnowledgeDeployment.binding_id)
        .where(
            KnowledgeDeployment.id == deployment_id,
            KnowledgeDeployment.oid == int(user.oid or 1),
        )
    ).one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="knowledge deployment not found")
    deployment, revision, unit, binding = row
    if refresh_binding_freshness(session, binding):
        session.commit()
    return {
        **deployment.model_dump(mode="json"),
        "unit": {
            "id": int(unit.id or 0),
            "unit_key": unit.unit_key,
            "title": unit.title,
            "domain": unit.domain,
        },
        "revision": revision.revision,
        "binding": binding.model_dump(mode="json"),
    }
