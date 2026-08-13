"""Preview and apply typed packages through existing K1-K5 domain services."""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Callable
from hashlib import sha256
from typing import Any

from sqlalchemy import func
from sqlmodel import Session, select

from apps.chat.query_specification import parse_specification_fragment
from apps.data_training.curd.data_training import create_training, update_training
from apps.data_training.models.data_training_model import DataTraining, DataTrainingInfo
from apps.datasource.models.datasource import CoreDatasource, CoreField, CoreTable
from apps.datasource.profiling.relation_candidates import admit_relation_candidate
from apps.knowledge.db_models import KnowledgeAsset
from apps.knowledge.gateway import KnowledgeCandidate, KnowledgeScope, submit_candidate
from apps.knowledge.importing.registry import (
    record_package_runtime_results,
    register_knowledge_package,
)
from apps.knowledge.importing.schema import (
    CaliberPackageItem,
    EvidencePackageItem,
    ExamplePackageItem,
    KnowledgeImportItemResult,
    KnowledgeImportReport,
    KnowledgePackage,
    KnowledgePackageItem,
    PackageFieldRef,
    RelationPackageItem,
    RulePackageItem,
    TerminologyPackageItem,
)
from apps.knowledge.staging.service import admit_candidate
from apps.terminology.curd.terminology import create_terminology, update_terminology
from apps.terminology.models.terminology_model import Terminology, TerminologyInfo

Trans = Callable[[str], str]


def _resolve_datasource(
    session: Session,
    *,
    oid: int,
    item: KnowledgePackageItem,
    package: KnowledgePackage,
    default_datasource_id: int | None,
    default_datasource_name: str | None,
) -> CoreDatasource | None:
    ds_id = (
        item.datasource_id or package.defaults.datasource_id or default_datasource_id
    )
    ds_name = (
        item.datasource_name
        or package.defaults.datasource_name
        or default_datasource_name
    )
    if ds_id is not None:
        ds = session.get(CoreDatasource, int(ds_id))
        if ds is None or int(ds.oid or 0) != oid:
            raise ValueError(f"datasource id={ds_id} not found in workspace")
        if ds_name and ds.name != ds_name:
            raise ValueError(
                f"datasource id/name mismatch: id={ds_id}, name={ds_name!r}"
            )
        return ds
    if ds_name:
        rows = list(
            session.exec(
                select(CoreDatasource).where(
                    CoreDatasource.oid == oid,
                    CoreDatasource.name == ds_name,
                )
            ).all()
        )
        if len(rows) != 1:
            raise ValueError(f"datasource name={ds_name!r} is not uniquely resolved")
        return rows[0]
    return None


def _resolve_field(
    session: Session,
    *,
    ds_id: int,
    ref: PackageFieldRef,
) -> tuple[CoreTable, CoreField]:
    stmt = select(CoreTable).where(
        CoreTable.ds_id == ds_id,
        func.lower(CoreTable.table_name) == ref.table_name.casefold(),
    )
    if ref.database_name:
        stmt = stmt.where(
            func.lower(CoreTable.database_name) == ref.database_name.casefold()
        )
    tables = list(session.exec(stmt).all())
    if len(tables) != 1:
        raise ValueError(
            f"table {ref.database_name + '.' if ref.database_name else ''}{ref.table_name} "
            f"resolved {len(tables)} times"
        )
    table = tables[0]
    fields = list(
        session.exec(
            select(CoreField).where(
                CoreField.ds_id == ds_id,
                CoreField.table_id == int(table.id),
                func.lower(CoreField.field_name) == ref.field_name.casefold(),
            )
        ).all()
    )
    if len(fields) != 1:
        raise ValueError(
            f"field {ref.table_name}.{ref.field_name} resolved {len(fields)} times"
        )
    return table, fields[0]


def _fragment_refs(fragment: dict[str, Any]) -> list[PackageFieldRef]:
    specification = parse_specification_fragment(fragment)
    refs: dict[tuple[str, str], PackageFieldRef] = {}
    for requirement in specification.requirements:
        raw = requirement.model_dump(mode="json")
        candidates: list[dict[str, Any]] = []
        if isinstance(raw.get("field"), dict):
            candidates.append(raw["field"])
        candidates.extend(
            value for value in (raw.get("fields") or []) if isinstance(value, dict)
        )
        for pair in raw.get("pairs") or []:
            if isinstance(pair, dict):
                candidates.extend(
                    value
                    for value in (pair.get("left"), pair.get("right"))
                    if isinstance(value, dict)
                )
        for candidate in candidates:
            resource = str(candidate.get("resource") or "")
            field = str(candidate.get("field") or "")
            if resource and field:
                refs[(resource.casefold(), field.casefold())] = PackageFieldRef(
                    table_name=resource,
                    field_name=field,
                )
    return list(refs.values())


def _preview_item(
    session: Session,
    *,
    oid: int,
    package: KnowledgePackage,
    item: KnowledgePackageItem,
    default_datasource_id: int | None,
    default_datasource_name: str | None,
) -> KnowledgeImportItemResult:
    messages: list[str] = []
    if item.status == "rejected":
        return KnowledgeImportItemResult(
            item_id=item.item_id,
            kind=item.kind,
            readiness="invalid",
            messages=["item status is rejected"],
        )
    try:
        ds = _resolve_datasource(
            session,
            oid=oid,
            item=item,
            package=package,
            default_datasource_id=default_datasource_id,
            default_datasource_name=default_datasource_name,
        )
        normalized: dict[str, Any] = item.model_dump(mode="json")
        if isinstance(item, EvidencePackageItem):
            return KnowledgeImportItemResult(
                item_id=item.item_id,
                kind=item.kind,
                readiness="retained_only",
                messages=["evidence is provenance input and is not a runtime asset"],
                normalized=normalized,
            )
        if isinstance(item, TerminologyPackageItem):
            if not item.word.strip() or not item.description.strip():
                raise ValueError("terminology requires word and description")
            if item.status not in {"reviewed", "verified"}:
                return KnowledgeImportItemResult(
                    item_id=item.item_id,
                    kind=item.kind,
                    readiness="review_required",
                    messages=["terminology must be reviewed before direct publication"],
                    normalized=normalized,
                )
            if (
                ds is None
                and item.assistant_id is None
                and package.defaults.assistant_id is None
            ):
                messages.append("terminology will be global to the workspace")
        elif isinstance(item, CaliberPackageItem):
            if ds is None:
                raise ValueError("caliber requires datasource scope")
            if not item.contract_fragment:
                return KnowledgeImportItemResult(
                    item_id=item.item_id,
                    kind=item.kind,
                    readiness="review_required",
                    messages=[
                        "caliber draft must be converted to a QuerySpecification v3 fragment"
                    ],
                    normalized=normalized,
                )
            refs = {
                ref.table_name.casefold() + "." + ref.field_name.casefold(): ref
                for ref in item.field_targets
            }
            for ref in _fragment_refs(item.contract_fragment):
                refs.setdefault(
                    ref.table_name.casefold() + "." + ref.field_name.casefold(), ref
                )
            resolved = []
            for ref in refs.values():
                table, field = _resolve_field(session, ds_id=int(ds.id), ref=ref)
                resolved.append(
                    {
                        "table_name": table.table_name,
                        "field_name": field.field_name,
                        "table_id": int(table.id),
                        "field_id": int(field.id),
                    }
                )
            normalized["field_targets"] = resolved
        elif isinstance(item, RelationPackageItem):
            if ds is None:
                raise ValueError("relation requires datasource scope")
            left_table, left_field = _resolve_field(
                session, ds_id=int(ds.id), ref=item.left
            )
            right_table, right_field = _resolve_field(
                session, ds_id=int(ds.id), ref=item.right
            )
            normalized["resolved"] = {
                "source_table_id": int(left_table.id),
                "source_field_id": int(left_field.id),
                "target_table_id": int(right_table.id),
                "target_field_id": int(right_field.id),
            }
            messages.append("relation will enter CANDIDATE and requires confirmation")
        elif isinstance(item, ExamplePackageItem):
            if ds is None:
                raise ValueError("example requires datasource scope")
            if not item.query.strip():
                return KnowledgeImportItemResult(
                    item_id=item.item_id,
                    kind=item.kind,
                    readiness="review_required",
                    messages=[
                        "query example has an intended specification but no executable plan"
                    ],
                    normalized=normalized,
                )
            if not item.verification.executed or not item.verification.passed:
                return KnowledgeImportItemResult(
                    item_id=item.item_id,
                    kind=item.kind,
                    readiness="review_required",
                    messages=[
                        "query example requires executed and passed verification"
                    ],
                    normalized=normalized,
                )
            if item.verification.datasource_id is not None and int(
                item.verification.datasource_id
            ) != int(ds.id):
                raise ValueError("example verification datasource does not match scope")
        elif isinstance(item, RulePackageItem):
            if not item.label.strip() or not item.content.strip():
                raise ValueError("rule requires label and content")
            messages.append(
                "rule will enter staging and requires explicit certification"
            )
        if ds is not None:
            normalized["resolved_datasource_id"] = int(ds.id)
        return KnowledgeImportItemResult(
            item_id=item.item_id,
            kind=item.kind,
            readiness="ready",
            messages=messages,
            normalized=normalized,
        )
    except Exception as exc:
        return KnowledgeImportItemResult(
            item_id=item.item_id,
            kind=item.kind,
            readiness="invalid",
            messages=[str(exc)],
        )


def _package_fingerprint(
    package: KnowledgePackage,
    *,
    default_datasource_id: int | None,
    default_datasource_name: str | None,
    include_kinds: set[str] | None,
) -> str:
    material = {
        "package": package.model_dump(mode="json"),
        "default_datasource_id": default_datasource_id,
        "default_datasource_name": default_datasource_name,
        "include_kinds": sorted(include_kinds or []),
    }
    encoded = json.dumps(
        material, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode()
    return sha256(encoded).hexdigest()


def _report(
    package: KnowledgePackage,
    *,
    dry_run: bool,
    items: list[KnowledgeImportItemResult],
    default_datasource_id: int | None,
    default_datasource_name: str | None,
    include_kinds: set[str] | None,
) -> KnowledgeImportReport:
    return KnowledgeImportReport(
        package_id=package.package_id,
        package_fingerprint=_package_fingerprint(
            package,
            default_datasource_id=default_datasource_id,
            default_datasource_name=default_datasource_name,
            include_kinds=include_kinds,
        ),
        dry_run=dry_run,
        total=len(items),
        kind_counts=dict(Counter(item.kind for item in items)),
        readiness_counts=dict(Counter(item.readiness for item in items)),
        action_counts={} if dry_run else dict(Counter(item.action for item in items)),
        items=items,
    )


def _external_identity(
    package: KnowledgePackage, item: KnowledgePackageItem
) -> dict[str, str]:
    return {"package_id": package.package_id, "item_id": item.item_id}


def _find_managed_row(
    session: Session,
    model: type[Terminology] | type[DataTraining],
    *,
    oid: int,
    package: KnowledgePackage,
    item: KnowledgePackageItem,
) -> Terminology | DataTraining | None:
    identity = _external_identity(package, item)
    statement = select(model).where(
        model.oid == oid,
        model.knowledge_meta.contains(identity),  # type: ignore[union-attr]
    )
    if model is Terminology:
        statement = statement.where(Terminology.pid.is_(None))
    return session.exec(statement).first()


def preview_knowledge_package(
    session: Session,
    *,
    oid: int,
    package: KnowledgePackage,
    default_datasource_id: int | None = None,
    default_datasource_name: str | None = None,
    include_kinds: set[str] | None = None,
) -> KnowledgeImportReport:
    items = [
        _preview_item(
            session,
            oid=oid,
            package=package,
            item=item,
            default_datasource_id=default_datasource_id,
            default_datasource_name=default_datasource_name,
        )
        for item in package.items
        if not include_kinds or item.kind in include_kinds
    ]
    report = _report(
        package,
        dry_run=True,
        items=items,
        default_datasource_id=default_datasource_id,
        default_datasource_name=default_datasource_name,
        include_kinds=include_kinds,
    )
    report.warnings = list(package.generator.get("scanner_warnings") or [])
    return report


def apply_knowledge_package(
    session: Session,
    *,
    oid: int,
    actor_user_id: int | None,
    package: KnowledgePackage,
    trans: Trans,
    default_datasource_id: int | None = None,
    default_datasource_name: str | None = None,
    include_kinds: set[str] | None = None,
    expected_preview_fingerprint: str | None = None,
) -> KnowledgeImportReport:
    full_preview = preview_knowledge_package(
        session,
        oid=oid,
        package=package,
        default_datasource_id=default_datasource_id,
        default_datasource_name=default_datasource_name,
    )
    selected_ids = {
        item.item_id
        for item in package.items
        if not include_kinds or item.kind in include_kinds
    }
    preview = full_preview.model_copy(
        update={
            "total": len(selected_ids),
            "package_fingerprint": _package_fingerprint(
                package,
                default_datasource_id=default_datasource_id,
                default_datasource_name=default_datasource_name,
                include_kinds=include_kinds,
            ),
            "kind_counts": dict(
                Counter(
                    item.kind
                    for item in full_preview.items
                    if item.item_id in selected_ids
                )
            ),
            "readiness_counts": dict(
                Counter(
                    item.readiness
                    for item in full_preview.items
                    if item.item_id in selected_ids
                )
            ),
            "items": [
                item for item in full_preview.items if item.item_id in selected_ids
            ],
        }
    )
    if (
        expected_preview_fingerprint is not None
        and expected_preview_fingerprint != preview.package_fingerprint
    ):
        raise ValueError("import input changed after preview; run preview again")
    # Import means registering the complete extraction package. Runtime assets
    # are projections of ready items and may be published independently below.
    registry, registry_action = register_knowledge_package(
        session,
        oid=oid,
        actor_user_id=actor_user_id,
        package=package,
        report=full_preview,
    )
    session.commit()
    assert registry.id is not None
    by_id = {item.item_id: item for item in package.items}
    results: list[KnowledgeImportItemResult] = []
    for checked in preview.items:
        item = by_id[checked.item_id]
        if checked.readiness != "ready":
            checked.action = "skipped"
            results.append(checked)
            continue
        normalized = checked.normalized or {}
        ds_id = normalized.get("resolved_datasource_id")
        try:
            if isinstance(item, TerminologyPackageItem):
                info = TerminologyInfo(
                    word=item.word,
                    description=item.description,
                    other_words=item.aliases,
                    specific_ds=ds_id is not None,
                    datasource_ids=[int(ds_id)] if ds_id is not None else [],
                    advanced_application=item.assistant_id
                    or package.defaults.assistant_id,
                    enabled=item.enabled,
                )
                managed = _find_managed_row(
                    session,
                    Terminology,
                    oid=oid,
                    package=package,
                    item=item,
                )
                if isinstance(managed, Terminology) and managed.id is not None:
                    info.id = int(managed.id)
                    terminology_id = update_terminology(session, info, oid, trans)
                    checked.action = "updated"
                else:
                    terminology_id = create_terminology(session, info, oid, trans)
                    checked.action = "imported"
                row = session.get(Terminology, terminology_id)
                if row is not None:
                    row.knowledge_meta = {
                        **item.knowledge_meta,
                        **_external_identity(package, item),
                        "evidence_refs": item.evidence_refs,
                    }
                    session.add(row)
                    session.commit()
                checked.target_id = int(terminology_id)
            elif isinstance(item, CaliberPackageItem):
                receipt = submit_candidate(
                    session,
                    KnowledgeCandidate(
                        kind="caliber",
                        payload={
                            "label": item.label,
                            "summary": item.summary,
                            "contract_fragment": item.contract_fragment,
                            "field_targets": normalized["field_targets"],
                        },
                        scope=KnowledgeScope(
                            oid=oid,
                            datasource_id=int(ds_id),
                            assistant_id=item.assistant_id
                            or package.defaults.assistant_id,
                        ),
                        provenance={
                            **item.provenance,
                            "source_type": "package",
                            "trigger_id": "PACKAGE_IMPORT",
                            "package_id": package.package_id,
                            "package_item_id": item.item_id,
                            "evidence_refs": item.evidence_refs,
                        },
                    ),
                    actor_user_id=actor_user_id,
                )
                if receipt.action == "existing":
                    checked.action = "unchanged"
                    results.append(checked)
                    continue
                if receipt.staging_id is None:
                    raise ValueError(receipt.detail or receipt.action)
                session.commit()
                checked.action = "staged"
                checked.target_id = int(receipt.staging_id)
            elif isinstance(item, RelationPackageItem):
                resolved = normalized["resolved"]
                relation, action = admit_relation_candidate(
                    session,
                    oid=oid,
                    ds_id=int(ds_id),
                    source_field_id=resolved["source_field_id"],
                    target_field_id=resolved["target_field_id"],
                    kind=item.relation_kind,
                    confidence=item.confidence,
                    cardinality=item.cardinality,
                    source="package",
                    evidence={
                        **item.evidence,
                        "package_id": package.package_id,
                        "item_id": item.item_id,
                        "evidence_refs": item.evidence_refs,
                    },
                )
                session.commit()
                checked.action = (
                    "candidate" if action in {"created", "updated"} else action
                )
                checked.target_id = (
                    int(relation.id) if relation.id is not None else None
                )
            elif isinstance(item, ExamplePackageItem):
                info = DataTrainingInfo(
                    question=item.question,
                    description=item.query,
                    datasource=int(ds_id),
                    advanced_application=item.assistant_id
                    or package.defaults.assistant_id,
                    enabled=item.enabled,
                    training_type=item.training_type,
                )
                managed = _find_managed_row(
                    session,
                    DataTraining,
                    oid=oid,
                    package=package,
                    item=item,
                )
                if isinstance(managed, DataTraining) and managed.id is not None:
                    info.id = int(managed.id)
                    training_id = update_training(session, info, oid, trans)
                    checked.action = "updated"
                else:
                    training_id = create_training(session, info, oid, trans)
                    checked.action = "imported"
                training = session.get(DataTraining, training_id)
                if training is not None:
                    training.knowledge_meta = {
                        **item.knowledge_meta,
                        **_external_identity(package, item),
                        "evidence_refs": item.evidence_refs,
                        "verification": item.verification.model_dump(mode="json"),
                    }
                    session.add(training)
                    session.commit()
                checked.target_id = int(training_id)
            elif isinstance(item, RulePackageItem):
                natural_key = (
                    f"rule:{oid}:{int(ds_id) if ds_id is not None else 0}:{item.label}"
                )
                existing_rule = session.exec(
                    select(KnowledgeAsset).where(
                        KnowledgeAsset.oid == oid,
                        KnowledgeAsset.kind == "rule",
                        KnowledgeAsset.natural_key == natural_key,
                        KnowledgeAsset.enabled.is_(True),  # type: ignore[attr-defined]
                        KnowledgeAsset.valid_to.is_(None),  # type: ignore[attr-defined]
                    )
                ).first()
                if (
                    existing_rule is not None
                    and str((existing_rule.payload or {}).get("content") or "").strip()
                    == item.content.strip()
                ):
                    checked.action = "unchanged"
                    checked.target_id = (
                        int(existing_rule.id) if existing_rule.id is not None else None
                    )
                    results.append(checked)
                    continue
                staging, action = admit_candidate(
                    session,
                    oid=oid,
                    kind="rule",
                    trigger_id="PACKAGE_IMPORT",
                    payload={
                        "natural_key": natural_key,
                        "label": item.label,
                        "content": item.content,
                    },
                    scope={
                        "oid": oid,
                        "datasource_id": int(ds_id) if ds_id is not None else None,
                        "assistant_id": item.assistant_id
                        or package.defaults.assistant_id,
                    },
                    source_record_id=None,
                    suggested_trust_tier="admitted",
                    provenance={
                        **item.provenance,
                        "source_type": "package",
                        "package_id": package.package_id,
                        "package_item_id": item.item_id,
                        "evidence_refs": item.evidence_refs,
                    },
                )
                session.commit()
                checked.action = (
                    "staged" if action in {"admitted", "merged"} else action
                )
                checked.target_id = int(staging.id) if staging.id is not None else None
            results.append(checked)
        except Exception as exc:
            session.rollback()
            checked.readiness = "invalid"
            checked.action = "rejected"
            checked.messages.append(str(exc))
            results.append(checked)
    report = _report(
        package,
        dry_run=False,
        items=results,
        default_datasource_id=default_datasource_id,
        default_datasource_name=default_datasource_name,
        include_kinds=include_kinds,
    )
    report.warnings = list(package.generator.get("scanner_warnings") or [])
    record_package_runtime_results(
        session,
        registry_id=int(registry.id),
        report=report,
    )
    session.commit()
    report.registry_id = int(registry.id)
    report.registry_revision = registry.revision
    report.registry_action = registry_action
    return report
