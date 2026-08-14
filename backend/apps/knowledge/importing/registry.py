"""Persistent package registry for reviewable extracted knowledge."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlmodel import Session, select

from apps.knowledge.db_models import (
    KnowledgePackageItemRegistry,
    KnowledgePackageRegistry,
)
from apps.knowledge.importing.schema import KnowledgeImportReport, KnowledgePackage


def register_knowledge_package(
    session: Session,
    *,
    oid: int,
    actor_user_id: int | None,
    package: KnowledgePackage,
    report: KnowledgeImportReport,
) -> tuple[KnowledgePackageRegistry, str]:
    """Upsert every item; absent items are retained and marked not present."""
    now = datetime.utcnow()
    registry = session.exec(
        select(KnowledgePackageRegistry).where(
            KnowledgePackageRegistry.oid == oid,
            KnowledgePackageRegistry.package_id == package.package_id,
        ).with_for_update()
    ).first()
    action = "updated"
    if registry is None:
        registry = KnowledgePackageRegistry(
            oid=oid,
            package_id=package.package_id,
            schema_version=package.schema_version,
            create_by=actor_user_id,
            create_time=now,
            update_time=now,
        )
        session.add(registry)
        session.flush()
        action = "registered"
    else:
        registry.revision += 1
    registry.title = package.title
    registry.description = package.description
    registry.item_count = len(package.items)
    registry.defaults = package.defaults.model_dump(mode="json")
    registry.sources = [source.model_dump(mode="json") for source in package.sources]
    registry.generator = package.generator
    registry.update_time = now
    session.add(registry)
    session.flush()
    assert registry.id is not None

    existing = {
        row.item_id: row
        for row in session.exec(
            select(KnowledgePackageItemRegistry).where(
                KnowledgePackageItemRegistry.package_registry_id == int(registry.id)
            )
        ).all()
    }
    package_items = {item.item_id: item for item in package.items}
    report_items = {item.item_id: item for item in report.items}
    for item_id, item in package_items.items():
        result = report_items[item_id]
        row = existing.get(item_id)
        if row is None:
            row = KnowledgePackageItemRegistry(
                package_registry_id=int(registry.id),
                item_id=item_id,
                kind=item.kind,
                source_status=item.status,
                readiness=result.readiness,
                create_time=now,
                update_time=now,
            )
        row.kind = item.kind
        row.source_status = item.status
        row.readiness = result.readiness
        row.present = True
        row.payload = item.model_dump(mode="json")
        row.messages = result.messages
        if not report.dry_run and result.action != "previewed":
            row.runtime_action = result.action
        if result.target_id is not None:
            row.runtime_target_id = result.target_id
        row.update_time = now
        session.add(row)
    for item_id, row in existing.items():
        if item_id not in package_items:
            row.present = False
            row.update_time = now
            session.add(row)
    session.flush()
    return registry, action


def record_package_runtime_results(
    session: Session,
    *,
    registry_id: int,
    report: KnowledgeImportReport,
) -> None:
    """Attach projection outcomes without creating another package revision."""
    rows = {
        row.item_id: row
        for row in session.exec(
            select(KnowledgePackageItemRegistry).where(
                KnowledgePackageItemRegistry.package_registry_id == registry_id
            )
        ).all()
    }
    now = datetime.utcnow()
    for result in report.items:
        row = rows.get(result.item_id)
        if row is None:
            continue
        row.readiness = result.readiness
        row.messages = result.messages
        row.runtime_action = result.action if result.action != "previewed" else None
        if result.target_id is not None:
            row.runtime_target_id = result.target_id
        row.update_time = now
        session.add(row)
    session.flush()


def list_package_items(
    session: Session,
    *,
    oid: int,
    package_id: str,
    present_only: bool = True,
) -> tuple[KnowledgePackageRegistry, list[KnowledgePackageItemRegistry]]:
    registry = session.exec(
        select(KnowledgePackageRegistry).where(
            KnowledgePackageRegistry.oid == oid,
            KnowledgePackageRegistry.package_id == package_id,
        )
    ).first()
    if registry is None or registry.id is None:
        raise ValueError("knowledge package not found")
    statement = select(KnowledgePackageItemRegistry).where(
        KnowledgePackageItemRegistry.package_registry_id == int(registry.id)
    )
    if present_only:
        statement = statement.where(KnowledgePackageItemRegistry.present.is_(True))
    statement = statement.order_by(
        KnowledgePackageItemRegistry.kind,
        KnowledgePackageItemRegistry.item_id,
    )
    return registry, list(session.exec(statement).all())


def materialize_registered_package(
    registry: KnowledgePackageRegistry,
    items: list[KnowledgePackageItemRegistry],
    *,
    reviewed_item_id: str | None = None,
) -> KnowledgePackage:
    """Rebuild the canonical transport package for a targeted governance action."""
    payloads: list[dict[str, Any]] = []
    for item in items:
        if not item.present:
            continue
        payload = dict(item.payload or {})
        if reviewed_item_id == item.item_id:
            payload["status"] = "reviewed"
        payloads.append(payload)
    return KnowledgePackage.model_validate(
        {
            "schema_version": registry.schema_version,
            "package_id": registry.package_id,
            "title": registry.title,
            "description": registry.description,
            "generator": registry.generator or {},
            "defaults": registry.defaults or {},
            "sources": registry.sources or [],
            "items": payloads,
        }
    )
