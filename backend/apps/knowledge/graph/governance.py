"""Composition governance: bind, review transitions, publish pinning, node edits.

Mirrors the proven lifecycle semantics of the revision plane (094) on the
node store: four-state lifecycle, BOUND-not-evaporating bindings, atomic
ACTIVE pointer switch, embedding failure aborts the deployment.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from sqlmodel import Session, col, select

from apps.datasource.models.datasource import CoreDatasource, CoreField, CoreTable
from apps.datasource.profiling.models import FieldProfileSnapshot
from apps.knowledge.graph.assembly import (
    assemble_composition,
    composition_node_keys,
)
from apps.knowledge.graph.decompose import append_node_version, fidelity_hash
from apps.knowledge.graph.models import (
    CompositionBinding,
    CompositionDeployment,
    KnowledgeEdge,
    KnowledgeMergeConflict,
    KnowledgeNode,
    KnowledgeNodeIndex,
    KnowledgeNodeVersion,
    UnitComposition,
)
from apps.knowledge.graph.node_kinds import (
    BUCKET_ID_FIELDS,
    id_field_for_kind,
    text_fields_for_kind,
)
from apps.knowledge.semantic.schema import KnowledgeUnitEntry
from apps.knowledge.semantic.service import (
    LIFECYCLE_TRANSITIONS,
    NEEDS_REVALIDATE,
    _mapped_fingerprint,
    _query_issue_message,
    _type_family,
    build_embeddings_or_raise,
    join_type_severity,
    match_catalog_table,
    next_step_for,
    prepare_example_sql,
)

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.utcnow()


# ---------------------------------------------------------------------------
# Listing / detail
# ---------------------------------------------------------------------------


def next_step(composition: UnitComposition, binding: CompositionBinding | None) -> str:
    return next_step_for(
        validation_status=composition.validation_status,
        lifecycle_status=composition.lifecycle_status,
        binding_status=binding.status if binding is not None else None,
    )


def list_compositions(
    session: Session,
    *,
    oid: int,
    keyword: str = "",
    lifecycle: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[dict[str, Any]], int]:
    statement = select(UnitComposition).where(UnitComposition.oid == oid)
    if lifecycle:
        statement = statement.where(UnitComposition.lifecycle_status == lifecycle)
    needle = keyword.strip()
    if needle:
        statement = statement.where(
            col(UnitComposition.title).icontains(needle)
            | col(UnitComposition.unit_key).icontains(needle)
        )
    total = len(session.exec(statement).all())
    rows = session.exec(
        statement.order_by(col(UnitComposition.update_time).desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    results: list[dict[str, Any]] = []
    for row in rows:
        binding = _latest_binding(session, composition_id=int(row.id or 0))
        deployment = _latest_deployment(session, composition_id=int(row.id or 0))
        results.append(
            {
                "id": int(row.id or 0),
                "unit_key": row.unit_key,
                "title": row.title,
                "domain": row.domain,
                "lifecycle_status": row.lifecycle_status,
                "validation_status": row.validation_status,
                "binding_status": binding.status if binding else "UNBOUND",
                "datasource_id": binding.datasource_id if binding else None,
                "deployment_status": deployment.status if deployment else None,
                "next_step": next_step(row, binding),
                "content_hash": row.content_hash,
                "update_time": row.update_time,
            }
        )
    return results, total


def _latest_binding(
    session: Session, *, composition_id: int
) -> CompositionBinding | None:
    return session.exec(
        select(CompositionBinding)
        .where(CompositionBinding.composition_id == composition_id)
        .order_by(col(CompositionBinding.update_time).desc())
    ).first()


def _latest_deployment(
    session: Session, *, composition_id: int
) -> CompositionDeployment | None:
    return session.exec(
        select(CompositionDeployment)
        .where(CompositionDeployment.composition_id == composition_id)
        .order_by(col(CompositionDeployment.update_time).desc())
    ).first()


def node_summary(node: KnowledgeNode, version: KnowledgeNodeVersion) -> dict[str, Any]:
    return {
        "id": int(node.id or 0),
        "node_kind": node.node_kind,
        "natural_key": node.natural_key,
        "version": version.version,
        "stub": version.stub,
        "payload": version.payload,
        "evidence_refs": version.evidence_refs,
        "confidence": version.confidence,
        "update_time": version.create_time,
    }


def get_composition_detail(
    session: Session, *, oid: int, composition_id: int
) -> dict[str, Any]:
    row = session.get(UnitComposition, composition_id)
    if row is None or row.oid != oid:
        raise ValueError("knowledge composition not found")
    entry = assemble_composition(session, row)
    refs = dict(row.refs or {})
    nodes = _composition_nodes(session, refs)
    bindings = session.exec(
        select(CompositionBinding).where(
            CompositionBinding.composition_id == composition_id
        )
    ).all()
    deployments = session.exec(
        select(CompositionDeployment).where(
            CompositionDeployment.composition_id == composition_id
        )
    ).all()
    return {
        "id": int(row.id or 0),
        "unit_key": row.unit_key,
        "title": row.title,
        "domain": row.domain,
        "applicability": row.applicability,
        "lifecycle_status": row.lifecycle_status,
        "validation_status": row.validation_status,
        "content_hash": row.content_hash,
        "refs": {
            "datasets": refs.get("datasets") or [],
            "buckets": refs.get("buckets") or {},
            "unit": refs.get("unit") or {},
        },
        "nodes": [node_summary(node, version) for node, version in nodes],
        "entry": entry,
        "bindings": [
            {
                "id": int(b.id or 0),
                "datasource_id": b.datasource_id,
                "status": b.status,
                "validation_result": b.validation_result,
                "update_time": b.update_time,
            }
            for b in bindings
        ],
        "deployments": [
            {
                "id": int(d.id or 0),
                "status": d.status,
                "activated_at": d.activated_at,
                "error": d.error,
            }
            for d in deployments
        ],
        "next_step": next_step(
            row, _latest_binding(session, composition_id=composition_id)
        ),
    }


def _composition_nodes(
    session: Session, refs: dict[str, Any]
) -> list[tuple[KnowledgeNode, KnowledgeNodeVersion]]:
    from apps.knowledge.graph.assembly import load_current_versions

    views = load_current_versions(session, composition_node_keys(refs))
    return [(view.node, view.version) for view in views.values()]


# ---------------------------------------------------------------------------
# Unit-field editing on the composition
# ---------------------------------------------------------------------------

_UNIT_FIELDS = ("title", "domain", "applicability")


def update_composition_unit_fields(
    session: Session,
    *,
    oid: int,
    composition_id: int,
    patch: dict[str, Any],
) -> UnitComposition:
    row = session.get(UnitComposition, composition_id)
    if row is None or row.oid != oid:
        raise ValueError("knowledge composition not found")
    refs = dict(row.refs or {})
    unit = dict(refs.get("unit") or {})
    for key in ("description", "aliases", "assumptions", "conflicts", "applicability"):
        if key in patch:
            unit[key] = patch[key]
    refs["unit"] = unit
    row.refs = refs
    for key in _UNIT_FIELDS:
        if key in patch and key != "applicability":
            setattr(row, key, str(patch[key]))
    if "applicability" in patch:
        row.applicability = str(patch["applicability"])
    entry = assemble_composition(session, row)
    row.content_hash = fidelity_hash(entry)
    row.update_time = _now()
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------


def transition_composition(
    session: Session,
    *,
    oid: int,
    composition_id: int,
    target: str,
    actor_user_id: int | None,
    reason: str = "",
) -> UnitComposition:
    row = session.get(UnitComposition, composition_id)
    if row is None or row.oid != oid:
        raise ValueError("knowledge composition not found")
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
            select(CompositionBinding).where(
                CompositionBinding.composition_id == composition_id,
                col(CompositionBinding.status).in_(["BOUND", "STALE"]),
            )
        ).first()
        if binding is None:
            raise ValueError(
                "knowledge must have a current datasource binding before approval"
            )
    row.lifecycle_status = target
    row.update_time = _now()
    if reason.strip() or target in {"APPROVED", "REJECTED"}:
        refs = dict(row.refs or {})
        notes = list(refs.get("review_notes") or [])
        notes.append(
            {
                "action": target,
                "reason": reason.strip(),
                "actor_user_id": actor_user_id,
                "at": _now().isoformat(),
            }
        )
        refs["review_notes"] = notes
        row.refs = refs
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


# ---------------------------------------------------------------------------
# Bind & validate against the live catalog
# ---------------------------------------------------------------------------


def refresh_composition_binding_freshness(
    session: Session, binding: CompositionBinding
) -> bool:
    """Mark a previously valid composition binding stale on catalog drift."""
    if binding.status != "BOUND":
        return False
    composition = session.get(UnitComposition, binding.composition_id)
    if composition is None:
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
    if binding.catalog_fingerprint == _mapped_fingerprint(
        tables, fields, binding.mapping
    ):
        return False
    binding.status = "STALE"
    binding.update_time = _now()
    session.add(binding)
    return True


def bind_and_validate_composition(
    session: Session,
    *,
    oid: int,
    composition_id: int,
    datasource_id: int,
) -> CompositionBinding:
    composition = session.get(UnitComposition, composition_id)
    datasource = session.get(CoreDatasource, datasource_id)
    if composition is None or composition.oid != oid:
        raise ValueError("knowledge composition not found")
    if datasource is None or int(datasource.oid or 0) != oid:
        raise ValueError("datasource not found in workspace")
    entry = KnowledgeUnitEntry.model_validate(
        assemble_composition(session, composition)
    )
    refs = dict(composition.refs or {})
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

    def dataset_key_to_local(payload: dict[str, Any]) -> str:
        return f"{payload.get('database') or ''}.{payload.get('name') or ''}".strip(".")

    from apps.knowledge.graph.assembly import load_current_versions

    node_keys = composition_node_keys(refs)
    node_by_key = {
        view.node.natural_key: view
        for view in load_current_versions(session, node_keys).values()
    }

    local_dataset_by_key: dict[str, str] = {}
    local_field_by_key: dict[str, tuple[str, str]] = {}
    for dataset_ref in refs.get("datasets") or []:
        ds_key = str(dataset_ref.get("dataset_key") or "")
        view = node_by_key.get(ds_key)
        if view is None:
            continue
        local_dataset_by_key[ds_key] = str(dataset_ref.get("unit_dataset_id") or "")
        for field_ref in dataset_ref.get("fields") or []:
            f_key = str(field_ref.get("field_key") or "")
            local_field_by_key[f_key] = (
                local_dataset_by_key[ds_key],
                str(field_ref.get("unit_field_id") or ""),
            )

    for dataset_ref in refs.get("datasets") or []:
        ds_key = str(dataset_ref.get("dataset_key") or "")
        view = node_by_key.get(ds_key)
        if view is None:
            continue
        payload = dict(view.version.payload)
        table = match_catalog_table(
            tables,
            table_name=str(payload.get("name") or ""),
            database_name=str(payload.get("database") or ""),
        )
        if table is None:
            issues.append(
                {
                    "code": "DATASET_NOT_FOUND",
                    "severity": "error",
                    "locator": ds_key,
                    "message": f"当前数据源中找不到表 {payload.get('name')}",
                }
            )
            continue
        mapping["datasets"][ds_key] = {
            "table_id": int(table.id or 0),
            "database_name": table.database_name or "",
            "table_name": table.table_name,
        }
        for field_ref in dataset_ref.get("fields") or []:
            f_key = str(field_ref.get("field_key") or "")
            f_view = node_by_key.get(f_key)
            if f_view is None:
                continue
            f_payload = dict(f_view.version.payload)
            f_name = str(f_payload.get("name") or "")
            field = field_index.get((int(table.id or 0), f_name.casefold()))
            if field is None:
                issues.append(
                    {
                        "code": "FIELD_NOT_FOUND",
                        "severity": "error",
                        "locator": f_key,
                        "message": f"表 {payload.get('name')} 中找不到字段 {f_name}",
                    }
                )
                continue
            mapping["fields"][f_key] = {
                "field_id": int(field.id or 0),
                "table_id": int(table.id or 0),
                "field_name": field.field_name,
                "field_type": field.field_type,
            }
            profile = latest_profile.get(int(field.id or 0))
            if profile is not None:
                mapping["fields"][f_key]["profile"] = {
                    "generation": profile.generation,
                    "row_count": profile.row_count,
                    "approx_distinct": profile.approx_distinct,
                }
            declared_type = str(f_payload.get("data_type") or "")
            declared_family = _type_family(declared_type)
            actual_family = _type_family(field.field_type)
            if declared_family and actual_family and declared_family != actual_family:
                issues.append(
                    {
                        "code": "FIELD_TYPE_MISMATCH",
                        "severity": "error",
                        "locator": f_key,
                        "expected_type": declared_type,
                        "actual_type": field.field_type,
                        "message": f"{f_key} 声明为 {declared_type}，数据源中是 {field.field_type}",
                    }
                )

    for relationship in entry.content.relationships:
        left_key = _field_key_for_ref(refs, relationship.left)
        right_key = _field_key_for_ref(refs, relationship.right)
        left = mapping["fields"].get(left_key or "")
        right = mapping["fields"].get(right_key or "")
        if not isinstance(left, dict) or not isinstance(right, dict):
            issues.append(
                {
                    "code": "RELATIONSHIP_NOT_BOUND",
                    "severity": "error",
                    "locator": relationship.relationship_id,
                    "message": "关系两端字段未能绑定到当前数据源",
                }
            )
            continue
        severity = join_type_severity(
            str(left.get("field_type") or ""), str(right.get("field_type") or "")
        )
        if severity:
            issues.append(
                {
                    "code": "RELATIONSHIP_TYPE_MISMATCH",
                    "severity": severity,
                    "locator": relationship.relationship_id,
                    "message": (
                        "两端类型不同，JOIN 时需要 CAST"
                        if severity == "warning"
                        else "两端类型不兼容，无法直接等值连接"
                    ),
                }
            )
        mapping["relationships"][relationship.relationship_id] = {
            "left": left,
            "right": right,
            "status": relationship.status,
        }

    # Verified query patterns: same read-only execution proof as the
    # revision plane; only passed patterns become certified exemplars.
    pattern_refs = list(
        (refs.get("buckets") or {}).get("verified_query_patterns") or []
    )
    if pattern_refs:
        try:
            from apps.protocol import get_protocol_for_ds
            from apps.protocol.base import CAP_SQL_DIALECT
            from apps.protocol.sql.protocol import QueryPlan

            protocol = get_protocol_for_ds(datasource)
        except (ImportError, ValueError) as exc:  # noqa: BLE001
            issues.append(
                {
                    "code": "QUERY_PROTOCOL_UNSUPPORTED",
                    "severity": "warning",
                    "locator": None,
                    "message": f"无法构建查询协议以校验范例: {exc}",
                }
            )
            protocol = None
        for pattern_ref in pattern_refs:
            pattern_key = str(pattern_ref.get("node_key") or "")
            p_view = node_by_key.get(pattern_key)
            if p_view is None:
                continue
            query = str(p_view.version.payload.get("query") or "")
            if not query.strip():
                continue
            if protocol is None or not protocol.supports(CAP_SQL_DIALECT):
                issues.append(
                    {
                        "code": "QUERY_PROTOCOL_UNSUPPORTED",
                        "severity": "warning",
                        "locator": pattern_key,
                        "message": "当前数据源不是 SQL 协议，无法校验该查询示例",
                    }
                )
                continue
            example_sql = prepare_example_sql(query)
            plan = QueryPlan(
                success=True, statement=example_sql, payload={"sql": example_sql}
            )
            validated = protocol.validate_plan(
                datasource, plan, [table.table_name for table in tables]
            )
            if not validated.success:
                issues.append(
                    {
                        "code": "QUERY_VALIDATION_FAILED",
                        "severity": "warning",
                        "locator": pattern_key,
                        "message": _query_issue_message(
                            validated.message or "Query validation failed"
                        ),
                    }
                )
                continue
            try:
                result = protocol.execute(datasource, validated, max_rows=1)
            except Exception as exc:  # noqa: BLE001 - recorded as warning
                issues.append(
                    {
                        "code": "QUERY_EXECUTION_FAILED",
                        "severity": "warning",
                        "locator": pattern_key,
                        "message": _query_issue_message(str(exc)),
                    }
                )
                continue
            mapping.setdefault("verified_query_patterns", {})[pattern_key] = {
                "executed": True,
                "passed": True,
                "verified_at": _now().isoformat(),
                "sample_rows": min(len(result.data), 1),
            }

    has_error = any(issue["severity"] == "error" for issue in issues)
    has_warning = any(issue["severity"] == "warning" for issue in issues)
    validation_status = "FAIL" if has_error else "WARNING" if has_warning else "PASS"
    now = _now()
    binding = session.exec(
        select(CompositionBinding).where(
            CompositionBinding.composition_id == composition_id,
            CompositionBinding.datasource_id == datasource_id,
        )
    ).first()
    if binding is None:
        binding = CompositionBinding(
            oid=oid,
            composition_id=composition_id,
            datasource_id=datasource_id,
            create_time=now,
            update_time=now,
        )
    binding.catalog_fingerprint = _mapped_fingerprint(tables, fields, mapping)
    binding.status = "BOUND"
    binding.mapping = mapping
    binding.validation_result = {"status": validation_status, "issues": issues}
    binding.update_time = now
    session.add(binding)
    others = session.exec(
        select(CompositionBinding).where(
            CompositionBinding.composition_id == composition_id,
            CompositionBinding.datasource_id != datasource_id,
        )
    ).all()
    for other in others:
        if other.status != "UNBOUND":
            other.status = "UNBOUND"
            other.update_time = now
            session.add(other)
    composition.validation_status = validation_status
    composition.update_time = now
    session.add(composition)
    session.commit()
    session.refresh(binding)
    return binding


def _field_key_for_ref(refs: dict[str, Any], ref: Any) -> str | None:
    for dataset_ref in refs.get("datasets") or []:
        if str(dataset_ref.get("unit_dataset_id") or "") != ref.dataset:
            continue
        for field_ref in dataset_ref.get("fields") or []:
            if str(field_ref.get("unit_field_id") or "") == ref.field:
                return str(field_ref.get("field_key") or "")
    return None


# ---------------------------------------------------------------------------
# Publish: pinning + snapshot + atomic node index
# ---------------------------------------------------------------------------


def _node_text_repr(kind: str, payload: dict[str, Any]) -> str:
    parts = [
        str(payload.get(field_name) or "") for field_name in text_fields_for_kind(kind)
    ]
    dictionary = payload.get("dictionary") or {}
    if isinstance(dictionary, dict):
        parts.extend(f"{key}={value}" for key, value in list(dictionary.items())[:40])
    aliases = payload.get("aliases") or []
    if isinstance(aliases, list):
        parts.extend(str(alias) for alias in aliases[:20])
    return " ".join(part for part in parts if part).strip()


def publish_composition(
    session: Session,
    *,
    oid: int,
    composition_id: int,
) -> CompositionDeployment:
    composition = session.get(UnitComposition, composition_id)
    if composition is None or composition.oid != oid:
        raise ValueError("knowledge composition not found")
    if composition.lifecycle_status not in {"APPROVED", "RETIRED"} or (
        composition.validation_status not in {"PASS", "WARNING"}
    ):
        raise ValueError(
            "only approved or unpublished compositions that passed validation can be published"
        )
    locked = session.exec(
        select(UnitComposition)
        .where(UnitComposition.id == composition_id)
        .with_for_update()
    ).first()
    if locked is None:
        raise ValueError("knowledge composition not found")
    binding = session.exec(
        select(CompositionBinding).where(
            CompositionBinding.composition_id == composition_id,
            CompositionBinding.status == "BOUND",
        )
    ).first()
    if binding is None:
        raise ValueError("knowledge composition has no valid datasource binding")
    now = _now()
    deployment = session.exec(
        select(CompositionDeployment).where(
            CompositionDeployment.composition_id == composition_id,
            CompositionDeployment.binding_id == int(binding.id or 0),
        )
    ).first()
    if deployment is None:
        deployment = CompositionDeployment(
            oid=oid,
            composition_id=composition_id,
            binding_id=int(binding.id or 0),
            create_time=now,
            update_time=now,
        )
    deployment.status = "BUILDING"
    deployment.error = None
    deployment.update_time = now
    session.add(deployment)
    session.flush()
    try:
        entry = assemble_composition(session, composition)
        KnowledgeUnitEntry.model_validate(entry)
        refs = dict(composition.refs or {})
        index_rows = _build_node_index_rows(session, oid, refs, int(deployment.id or 0))
        session.query(KnowledgeNodeIndex).filter(
            KnowledgeNodeIndex.deployment_id == int(deployment.id or 0)
        ).delete()
        for row in index_rows:
            session.add(row)
        previous = session.exec(
            select(CompositionDeployment).where(
                CompositionDeployment.oid == oid,
                CompositionDeployment.status == "ACTIVE",
                CompositionDeployment.composition_id == composition_id,
            )
        ).all()
        for active in previous:
            if int(active.id or 0) == int(deployment.id or 0):
                continue
            active.status = "RETIRED"
            active.update_time = now
            session.add(active)
        deployment.pinned_snapshot = {
            "entry": entry,
            "meta": {
                "composition_id": composition_id,
                "binding_id": int(binding.id or 0),
                "unit_key": composition.unit_key,
                "content_hash": composition.content_hash,
            },
        }
        deployment.status = "ACTIVE"
        deployment.activated_at = now
        deployment.update_time = now
        composition.lifecycle_status = "PUBLISHED"
        composition.active_deployment_id = int(deployment.id or 0)
        composition.update_time = now
        session.add(deployment)
        session.add(composition)
        session.commit()
    except Exception as exc:
        session.rollback()
        failed = session.exec(
            select(CompositionDeployment).where(
                CompositionDeployment.composition_id == composition_id,
                CompositionDeployment.binding_id == int(binding.id or 0),
            )
        ).first()
        if failed is None:
            failed = CompositionDeployment(
                oid=oid,
                composition_id=composition_id,
                binding_id=int(binding.id or 0),
                status="ERROR",
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


def _build_node_index_rows(
    session: Session,
    oid: int,
    refs: dict[str, Any],
    deployment_id: int,
) -> list[KnowledgeNodeIndex]:
    from apps.knowledge.graph.assembly import load_current_versions

    views = load_current_versions(session, composition_node_keys(refs))
    texts = [
        _node_text_repr(view.node.node_kind, view.version.payload)
        for view in views.values()
    ]
    vectors = build_embeddings_or_raise(texts)
    slot_meta = _slot_metadata(refs)
    rows: list[KnowledgeNodeIndex] = []
    now = _now()
    for index, view in enumerate(views.values()):
        physical_key = (
            view.node.natural_key if view.node.node_kind in {"dataset", "field"} else ""
        )
        rows.append(
            KnowledgeNodeIndex(
                oid=oid,
                deployment_id=deployment_id,
                node_version_id=int(view.version.id or 0),
                node_kind=view.node.node_kind,
                physical_key=physical_key,
                text_repr=texts[index][:4000],
                embedding=vectors[index] if vectors is not None else None,
                content=_index_content(
                    view.node.natural_key, view.version.payload, slot_meta
                ),
                create_time=now,
            )
        )
    return rows


def _slot_metadata(refs: dict[str, Any]) -> dict[str, dict[str, str]]:
    """Natural key -> unit-local id field + local id, per slot.

    The node index stores the slot projection (the runtime reads the pinned
    snapshot, never the editable current payload), so each index row carries
    its unit-local identity for bundle assembly.
    """
    meta: dict[str, dict[str, str]] = {}
    dataset_id_field = id_field_for_kind("dataset") or "dataset_id"
    field_id_field = id_field_for_kind("field") or "field_id"
    for dataset_ref in refs.get("datasets") or []:
        ds_key = str(dataset_ref.get("dataset_key") or "")
        meta[ds_key] = {
            "id_field": dataset_id_field,
            "local_id": str(dataset_ref.get("unit_dataset_id") or ""),
        }
        for field_ref in dataset_ref.get("fields") or []:
            f_key = str(field_ref.get("field_key") or "")
            meta[f_key] = {
                "id_field": field_id_field,
                "local_id": str(field_ref.get("unit_field_id") or ""),
                "dataset_id": str(dataset_ref.get("unit_dataset_id") or ""),
            }
    for bucket, id_field in BUCKET_ID_FIELDS.items():
        for node_ref in (refs.get("buckets") or {}).get(bucket) or []:
            meta[str(node_ref.get("node_key") or "")] = {
                "id_field": id_field,
                "local_id": str(node_ref.get("local_id") or ""),
            }
    return meta


def _index_content(
    natural_key: str,
    payload: dict[str, Any],
    slot_meta: dict[str, dict[str, str]],
) -> dict[str, Any]:
    content = dict(payload)
    meta = slot_meta.get(natural_key)
    if meta:
        content[meta["id_field"]] = meta["local_id"]
        if meta.get("dataset_id"):
            content["dataset_id"] = meta["dataset_id"]
    return content


def unpublish_composition(
    session: Session, *, oid: int, composition_id: int
) -> UnitComposition:
    row = session.get(UnitComposition, composition_id)
    if row is None or row.oid != oid:
        raise ValueError("knowledge composition not found")
    if row.lifecycle_status != "PUBLISHED":
        raise ValueError("only published compositions can be unpublished")
    now = _now()
    deployments = session.exec(
        select(CompositionDeployment).where(
            CompositionDeployment.composition_id == composition_id,
            CompositionDeployment.status == "ACTIVE",
        )
    ).all()
    for deployment in deployments:
        deployment.status = "RETIRED"
        deployment.update_time = now
        session.add(deployment)
        for index_row in session.exec(
            select(KnowledgeNodeIndex).where(
                KnowledgeNodeIndex.deployment_id == int(deployment.id or 0)
            )
        ).all():
            index_row.active = False
            session.add(index_row)
    row.lifecycle_status = "RETIRED"
    row.active_deployment_id = None
    row.update_time = now
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


# ---------------------------------------------------------------------------
# Node maintenance + impact
# ---------------------------------------------------------------------------


def _compositions_referencing(
    session: Session, *, oid: int, node_key: str
) -> list[UnitComposition]:
    rows = session.exec(select(UnitComposition).where(UnitComposition.oid == oid)).all()
    return [
        row for row in rows if node_key in composition_node_keys(dict(row.refs or {}))
    ]


def list_nodes(
    session: Session,
    *,
    oid: int,
    keyword: str = "",
    node_kind: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[dict[str, Any]], int]:
    statement = select(KnowledgeNode).where(KnowledgeNode.oid == oid)
    if node_kind:
        statement = statement.where(KnowledgeNode.node_kind == node_kind)
    needle = keyword.strip()
    if needle:
        statement = statement.where(
            col(KnowledgeNode.natural_key).icontains(needle)
            | col(KnowledgeNode.node_kind).icontains(needle)
        )
    rows = session.exec(statement).all()
    total = len(rows)
    page_rows = rows[(page - 1) * page_size : page * page_size]
    results: list[dict[str, Any]] = []
    for node in page_rows:
        current = session.exec(
            select(KnowledgeNodeVersion)
            .where(KnowledgeNodeVersion.node_id == int(node.id or 0))
            .order_by(col(KnowledgeNodeVersion.version).desc())
        ).first()
        results.append(
            {
                "id": int(node.id or 0),
                "node_kind": node.node_kind,
                "natural_key": node.natural_key,
                "namespace": node.namespace,
                "status": node.status,
                "stub": current.stub if current else False,
                "version": current.version if current else None,
                "update_time": node.update_time,
            }
        )
    return results, total


def edit_node(
    session: Session,
    *,
    oid: int,
    node_id: int,
    payload_patch: dict[str, Any],
) -> dict[str, Any]:
    node = session.get(KnowledgeNode, node_id)
    if node is None or node.oid != oid:
        raise ValueError("knowledge node not found")
    current = session.exec(
        select(KnowledgeNodeVersion)
        .where(KnowledgeNodeVersion.node_id == node_id)
        .order_by(col(KnowledgeNodeVersion.version).desc())
    ).first()
    if current is None:
        raise ValueError("knowledge node has no versions")
    merged = {**current.payload, **payload_patch}
    now = _now()
    version, changed = append_node_version(
        session,
        node=node,
        current=current,
        payload=merged,
        evidence_refs=current.evidence_refs,
        confidence=current.confidence,
        stub=current.stub,
        origin_package_id=current.origin_package_id,
        now=now,
    )
    if not changed:
        return {"changed": False, "version": current.version}
    affected: list[dict[str, Any]] = []
    for composition in _compositions_referencing(
        session, oid=oid, node_key=node.natural_key
    ):
        if composition.lifecycle_status in {"DRAFT", "REJECTED"}:
            continue
        composition.validation_status = NEEDS_REVALIDATE
        composition.update_time = now
        session.add(composition)
        affected.append(
            {
                "id": int(composition.id or 0),
                "unit_key": composition.unit_key,
                "title": composition.title,
                "lifecycle_status": composition.lifecycle_status,
            }
        )
    session.commit()
    return {
        "changed": True,
        "version": version.version,
        "affected_compositions": affected,
    }


def node_detail(session: Session, *, oid: int, node_id: int) -> dict[str, Any]:
    node = session.get(KnowledgeNode, node_id)
    if node is None or node.oid != oid:
        raise ValueError("knowledge node not found")
    versions = session.exec(
        select(KnowledgeNodeVersion)
        .where(KnowledgeNodeVersion.node_id == node_id)
        .order_by(col(KnowledgeNodeVersion.version).desc())
    ).all()
    edges_out = session.exec(
        select(KnowledgeEdge).where(KnowledgeEdge.src_node_id == node_id)
    ).all()
    edges_in = session.exec(
        select(KnowledgeEdge).where(KnowledgeEdge.dst_node_id == node_id)
    ).all()
    return {
        **node_summary(session, node, versions[0]),
        "versions": [
            {
                "version": v.version,
                "content_hash": v.content_hash,
                "stub": v.stub,
                "create_time": v.create_time,
            }
            for v in versions
        ],
        "edges_out": [
            {
                "edge_kind": e.edge_kind,
                "status": e.status,
                "dst_node_id": e.dst_node_id,
            }
            for e in edges_out
        ],
        "edges_in": [
            {
                "edge_kind": e.edge_kind,
                "status": e.status,
                "src_node_id": e.src_node_id,
            }
            for e in edges_in
        ],
    }


def node_impact(session: Session, *, oid: int, node_id: int) -> dict[str, Any]:
    node = session.get(KnowledgeNode, node_id)
    if node is None or node.oid != oid:
        raise ValueError("knowledge node not found")
    compositions = _compositions_referencing(
        session, oid=oid, node_key=node.natural_key
    )
    edge_counts: dict[str, int] = {}
    for edge in session.exec(
        select(KnowledgeEdge).where(
            (KnowledgeEdge.src_node_id == node_id)
            | (KnowledgeEdge.dst_node_id == node_id)
        )
    ).all():
        edge_counts[edge.edge_kind] = edge_counts.get(edge.edge_kind, 0) + 1
    return {
        "node_id": node_id,
        "natural_key": node.natural_key,
        "compositions": [
            {
                "id": int(c.id or 0),
                "unit_key": c.unit_key,
                "title": c.title,
                "lifecycle_status": c.lifecycle_status,
                "validation_status": c.validation_status,
            }
            for c in compositions
        ],
        "edge_counts": edge_counts,
    }


# ---------------------------------------------------------------------------
# Schema drift -> nodes -> compositions
# ---------------------------------------------------------------------------


def mark_compositions_stale_for_drift(
    session: Session,
    *,
    oid: int,
    ds_id: int,
    changed_field_names: list[tuple[str, str]],
    changed_table_names: list[str],
) -> int:
    """L-1 wiring for the node plane: drift marks referencing compositions."""
    from apps.knowledge.graph.identity import dataset_key, field_key, norm

    keys: set[str] = set()
    dataset_nodes = session.exec(
        select(KnowledgeNode).where(
            KnowledgeNode.oid == oid,
            KnowledgeNode.node_kind == "dataset",
        )
    ).all()
    for table, field_name in changed_field_names:
        for node in dataset_nodes:
            if node.natural_key.split(".")[-1] == norm(table):
                keys.add(field_key(node.natural_key, field_name))
    for table in changed_table_names:
        keys.add(dataset_key("", table))
        keys.add(norm(table))
    if not keys:
        return 0
    now = _now()
    marked = 0
    compositions = session.exec(
        select(UnitComposition).where(UnitComposition.oid == oid)
    ).all()
    for composition in compositions:
        refs_keys = set(composition_node_keys(dict(composition.refs or {})))
        if not refs_keys & keys:
            continue
        composition.validation_status = NEEDS_REVALIDATE
        composition.update_time = now
        session.add(composition)
        marked += 1
    if marked:
        session.flush()
        logger.info(
            "schema drift marked %d composition(s) NEEDS_REVALIDATE for ds %s",
            marked,
            ds_id,
        )
    return marked


# ---------------------------------------------------------------------------
# Merge-conflict queue
# ---------------------------------------------------------------------------


def list_merge_conflicts(
    session: Session, *, oid: int, status: str = "open"
) -> list[dict[str, Any]]:
    rows = session.exec(
        select(KnowledgeMergeConflict)
        .where(
            KnowledgeMergeConflict.oid == oid,
            KnowledgeMergeConflict.status == status,
        )
        .order_by(col(KnowledgeMergeConflict.create_time).desc())
    ).all()
    result: list[dict[str, Any]] = []
    for row in rows:
        node = session.get(KnowledgeNode, row.node_id)
        result.append(
            {
                "id": int(row.id or 0),
                "node_id": row.node_id,
                "node_kind": node.node_kind if node else None,
                "natural_key": node.natural_key if node else None,
                "claim": row.claim,
                "status": row.status,
                "resolution": row.resolution,
                "create_time": row.create_time,
            }
        )
    return result


def resolve_merge_conflict(
    session: Session,
    *,
    oid: int,
    conflict_id: int,
    action: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    conflict = session.get(KnowledgeMergeConflict, conflict_id)
    if conflict is None or conflict.oid != oid:
        raise ValueError("merge conflict not found")
    if conflict.status != "open":
        raise ValueError("merge conflict already resolved")
    if action not in {"keep_existing", "accept_claim", "custom"}:
        raise ValueError("action must be keep_existing | accept_claim | custom")
    now = _now()
    outcome: dict[str, Any] = {"action": action, "node_changed": False}
    if action in {"accept_claim", "custom"}:
        claim = dict(conflict.claim or {})
        new_payload = (
            payload
            if action == "custom" and payload is not None
            else dict(claim.get("new_payload") or {})
        )
        if new_payload:
            result = edit_node(
                session,
                oid=oid,
                node_id=conflict.node_id,
                payload_patch=new_payload,
            )
            outcome["node_changed"] = result["changed"]
            outcome["affected_compositions"] = result.get("affected_compositions", [])
    conflict.status = "resolved"
    conflict.resolution = {"action": action, "at": now.isoformat()}
    conflict.update_time = now
    session.add(conflict)
    session.commit()
    return outcome
