"""Canonical table-relation persistence shared by HTTP and tool adapters."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from fastapi import HTTPException
from sqlmodel import Session

from apps.datasource.models.datasource import CoreDatasource, CoreField, CoreTable

_NODE_SHAPE = "er-rect"
_EDGE_SHAPE = "edge"


def _get_datasource(session: Session, *, oid: int, ds_id: int) -> CoreDatasource:
    datasource = session.get(CoreDatasource, ds_id)
    if datasource is None or int(datasource.oid or 1) != int(oid):
        raise HTTPException(status_code=404, detail="Datasource not found")
    return datasource


def _graph_id(value: Any, *, label: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid {label}") from exc


def _validate_relation_graph(
    session: Session,
    *,
    ds_id: int,
    graph: Sequence[dict[str, Any]],
) -> None:
    """Enforce the same table/field invariants for UI and tool graph writes."""
    nodes = [item for item in graph if item.get("shape") != _EDGE_SHAPE]
    edges = [item for item in graph if item.get("shape") == _EDGE_SHAPE]
    node_ids = [_graph_id(item.get("id"), label="relation node id") for item in nodes]
    if len(node_ids) != len(set(node_ids)):
        raise HTTPException(status_code=400, detail="Duplicate relation node id")

    tables = {table_id: session.get(CoreTable, table_id) for table_id in set(node_ids)}
    if any(table is None or int(table.ds_id) != ds_id for table in tables.values()):
        raise HTTPException(
            status_code=400,
            detail="Every relation node must belong to the datasource",
        )

    field_cache: dict[int, CoreField] = {}

    def field_for(field_id: int) -> CoreField:
        field = field_cache.get(field_id)
        if field is None:
            field = session.get(CoreField, field_id)
            if field is not None:
                field_cache[field_id] = field
        if field is None or int(field.ds_id) != ds_id:
            raise HTTPException(
                status_code=400,
                detail="Every relation field must belong to the datasource",
            )
        return field

    for node, table_id in zip(nodes, node_ids, strict=True):
        ports = node.get("ports") or {}
        if not isinstance(ports, dict) or not isinstance(ports.get("items", []), list):
            raise HTTPException(status_code=400, detail="Invalid relation node ports")
        for port in ports.get("items", []):
            if not isinstance(port, dict):
                raise HTTPException(
                    status_code=400, detail="Invalid relation node port"
                )
            field = field_for(_graph_id(port.get("id"), label="relation port id"))
            if int(field.table_id) != table_id:
                raise HTTPException(
                    status_code=400,
                    detail="Relation port does not belong to its table",
                )

    edge_ids: set[str] = set()
    for edge in edges:
        edge_id = str(edge.get("id") or "").strip()
        if not edge_id or edge_id in edge_ids:
            raise HTTPException(status_code=400, detail="Invalid relation edge id")
        edge_ids.add(edge_id)
        source = edge.get("source")
        target = edge.get("target")
        if not isinstance(source, dict) or not isinstance(target, dict):
            raise HTTPException(status_code=400, detail="Invalid relation edge")
        source_table_id = _graph_id(source.get("cell"), label="source table id")
        target_table_id = _graph_id(target.get("cell"), label="target table id")
        if source_table_id not in tables or target_table_id not in tables:
            raise HTTPException(
                status_code=400,
                detail="Relation edge references a missing table node",
            )
        source_field = field_for(_graph_id(source.get("port"), label="source field id"))
        target_field = field_for(_graph_id(target.get("port"), label="target field id"))
        if (
            int(source_field.table_id) != source_table_id
            or int(target_field.table_id) != target_table_id
        ):
            raise HTTPException(
                status_code=400,
                detail="Relation edge field does not belong to its table",
            )


def get_relation_graph(
    session: Session,
    *,
    oid: int,
    ds_id: int,
) -> list[dict[str, Any]]:
    """Return ER graph with layout nodes preserved and edges from confirmed relations.

    ``field_relation`` is the semantic truth for edges; X6 JSON keeps layout only.
    """
    datasource = _get_datasource(session, oid=oid, ds_id=ds_id)
    return project_confirmed_relations_graph(
        session, oid=oid, ds_id=ds_id, layout=list(datasource.table_relation or [])
    )


def project_confirmed_relations_graph(
    session: Session,
    *,
    oid: int,
    ds_id: int,
    layout: Sequence[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Build an ER payload: layout nodes + CONFIRMED ``field_relation`` edges."""
    from apps.datasource.profiling.models import (
        FieldRelation,
        RelationKind,
        RelationStatus,
    )
    from sqlmodel import select

    existing = list(layout or [])
    tables = (
        session.query(CoreTable)
        .filter(CoreTable.ds_id == ds_id)
        .order_by(CoreTable.id)
        .all()
    )
    table_map = {int(t.id): t for t in tables if t.id is not None}
    existing_nodes: dict[int, dict[str, Any]] = {}
    for item in existing:
        if item.get("shape") == _EDGE_SHAPE or item.get("id") is None:
            continue
        try:
            table_id = _graph_id(item.get("id"), label="relation node id")
        except HTTPException:
            continue
        if table_id in table_map:
            existing_nodes[table_id] = item

    # Ensure tables referenced by confirmed relations appear as nodes.
    relations = list(
        session.exec(
            select(FieldRelation).where(
                FieldRelation.ds_id == ds_id,
                FieldRelation.status == RelationStatus.CONFIRMED.value,
                FieldRelation.kind.in_(  # type: ignore[attr-defined]
                    [RelationKind.EQUI_JOIN.value, RelationKind.HIERARCHY.value]
                ),
            )
        ).all()
    )
    for rel in relations:
        existing_nodes.setdefault(int(rel.source_table_id), {})
        existing_nodes.setdefault(int(rel.target_table_id), {})

    fields_by_table = _fields_by_table(
        session, ds_id=ds_id, table_ids=set(existing_nodes) & set(table_map)
    )
    nodes = [
        _table_node(
            table_map[table_id],
            fields_by_table.get(table_id, []),
            existing=existing_nodes.get(table_id) or None,
            index=index,
        )
        for index, table_id in enumerate(sorted(set(existing_nodes) & set(table_map)))
    ]
    edges: list[dict[str, Any]] = []
    for rel in relations:
        if (
            int(rel.source_table_id) not in table_map
            or int(rel.target_table_id) not in table_map
        ):
            continue
        edges.append(
            {
                "id": f"fr-{rel.id}",
                "shape": _EDGE_SHAPE,
                "source": {
                    "cell": int(rel.source_table_id),
                    "port": int(rel.source_field_id),
                },
                "target": {
                    "cell": int(rel.target_table_id),
                    "port": int(rel.target_field_id),
                },
                "attrs": {"line": {"stroke": "#5F95FF"}},
                "data": {
                    "field_relation_id": rel.id,
                    "kind": rel.kind,
                    "source": rel.source,
                },
            }
        )
    return [*nodes, *edges]


def field_relations_from_graph(
    graph: Sequence[dict[str, Any]],
) -> list[dict[str, int]]:
    """Project X6 graph edges into the semantic relation contract."""
    relations: list[dict[str, int]] = []
    for item in graph:
        if item.get("shape") != _EDGE_SHAPE:
            continue
        source = item.get("source")
        target = item.get("target")
        if not isinstance(source, dict) or not isinstance(target, dict):
            continue
        relations.append(
            {
                "source_table_id": _graph_id(
                    source.get("cell"), label="source table id"
                ),
                "source_field_id": _graph_id(
                    source.get("port"), label="source field id"
                ),
                "target_table_id": _graph_id(
                    target.get("cell"), label="target table id"
                ),
                "target_field_id": _graph_id(
                    target.get("port"), label="target field id"
                ),
            }
        )
    return relations


def save_relation_graph(
    session: Session,
    *,
    oid: int,
    ds_id: int,
    graph: Sequence[dict[str, Any]],
) -> None:
    """Validate canvas graph, sync EQUI_JOIN semantics via profiling service, store layout.

    ``field_relation`` remains the semantic truth; X6 keeps layout nodes and is
    re-projected from CONFIRMED edges after sync.
    """
    from apps.datasource.profiling.service import (
        project_datasource_relation_layout,
        sync_manual_equi_joins,
    )

    datasource = _get_datasource(session, oid=oid, ds_id=ds_id)
    _validate_relation_graph(session, ds_id=ds_id, graph=graph)
    pairs = field_relations_from_graph(graph)
    sync_manual_equi_joins(
        session,
        oid=oid,
        ds_id=ds_id,
        pairs=pairs,
        commit=False,
    )
    # Keep node positions from the canvas; edges always come from CONFIRMED rows.
    layout_nodes = [item for item in graph if item.get("shape") != _EDGE_SHAPE]
    project_datasource_relation_layout(
        session,
        ds=datasource,
        layout=layout_nodes,
        commit=True,
    )


def _fields_by_table(
    session: Session,
    *,
    ds_id: int,
    table_ids: set[int],
) -> dict[int, list[CoreField]]:
    fields = (
        session.query(CoreField)
        .filter(
            CoreField.ds_id == ds_id,
            CoreField.table_id.in_(list(table_ids)),
        )
        .order_by(CoreField.field_index)
        .all()
        if table_ids
        else []
    )
    result: dict[int, list[CoreField]] = {}
    for field in fields:
        result.setdefault(int(field.table_id), []).append(field)
    return result


def _table_node(
    table: CoreTable,
    fields: Sequence[CoreField],
    *,
    existing: dict[str, Any] | None,
    index: int,
) -> dict[str, Any]:
    if table.id is None:
        raise ValueError("Relation table id is required")
    table_id = int(table.id)
    previous = existing or {}
    return {
        **previous,
        "id": table_id,
        "shape": _NODE_SHAPE,
        "label": table.table_name,
        "position": previous.get("position")
        or {"x": 80 + (index % 3) * 240, "y": 80 + (index // 3) * 220},
        "ports": {
            "items": [
                {
                    "id": int(field.id),
                    "group": "list",
                    "attrs": {
                        "portNameLabel": {"text": field.field_name},
                        "portTypeLabel": {"text": field.field_type or ""},
                    },
                }
                for field in fields
                if field.id is not None
            ]
        },
    }


def reconcile_relation_graph(
    session: Session,
    *,
    oid: int,
    ds_id: int,
    commit: bool = True,
) -> list[dict[str, Any]]:
    """Reconcile saved ER layout with the current table/field projection.

    Catalog synchronization owns table and field lifecycle. This hook keeps the
    same persisted graph valid by pruning removed nodes/ports/edges and refreshing
    the metadata of surviving nodes. It never invents new relationships.
    """
    datasource = _get_datasource(session, oid=oid, ds_id=ds_id)
    current_tables = (
        session.query(CoreTable)
        .filter(CoreTable.ds_id == ds_id)
        .order_by(CoreTable.id)
        .all()
    )
    tables = {int(table.id): table for table in current_tables if table.id is not None}
    existing_graph = list(datasource.table_relation or [])
    existing_nodes: dict[int, dict[str, Any]] = {}
    for item in existing_graph:
        if item.get("shape") == _EDGE_SHAPE or item.get("id") is None:
            continue
        try:
            table_id = _graph_id(item.get("id"), label="relation node id")
        except HTTPException:
            continue
        existing_nodes.setdefault(table_id, item)
    kept_table_ids = set(existing_nodes) & set(tables)
    fields_by_table = _fields_by_table(
        session,
        ds_id=ds_id,
        table_ids=kept_table_ids,
    )

    nodes = [
        _table_node(
            tables[table_id],
            fields_by_table.get(table_id, []),
            existing=existing_nodes[table_id],
            index=index,
        )
        for index, table_id in enumerate(sorted(kept_table_ids))
    ]
    fields = {
        int(field.id): field
        for table_fields in fields_by_table.values()
        for field in table_fields
        if field.id is not None
    }
    edges: list[dict[str, Any]] = []
    edge_ids: set[str] = set()
    for item in existing_graph:
        if item.get("shape") != _EDGE_SHAPE:
            continue
        source = item.get("source")
        target = item.get("target")
        if not isinstance(source, dict) or not isinstance(target, dict):
            continue
        try:
            source_table_id = _graph_id(source.get("cell"), label="source table id")
            target_table_id = _graph_id(target.get("cell"), label="target table id")
            source_field_id = _graph_id(source.get("port"), label="source field id")
            target_field_id = _graph_id(target.get("port"), label="target field id")
        except HTTPException:
            continue
        source_field = fields.get(source_field_id)
        target_field = fields.get(target_field_id)
        edge_id = str(item.get("id") or "").strip()
        if (
            not edge_id
            or edge_id in edge_ids
            or source_table_id not in kept_table_ids
            or target_table_id not in kept_table_ids
            or source_field is None
            or target_field is None
            or int(source_field.table_id) != source_table_id
            or int(target_field.table_id) != target_table_id
        ):
            continue
        edge_ids.add(edge_id)
        edges.append(item)

    graph = [*nodes, *edges]
    if graph != existing_graph:
        datasource.table_relation = graph
        session.add(datasource)
    if commit:
        session.commit()
    return graph


def replace_field_relations(
    session: Session,
    *,
    oid: int,
    ds_id: int,
    relations: Sequence[dict[str, int]],
) -> list[dict[str, Any]]:
    """Validate semantic field pairs and publish the canonical graph payload."""
    datasource = _get_datasource(session, oid=oid, ds_id=ds_id)

    field_ids = {
        int(relation[key])
        for relation in relations
        for key in ("source_field_id", "target_field_id")
    }
    fields = {
        int(field.id): field
        for field_id in field_ids
        if (field := session.get(CoreField, field_id)) is not None
        and field.id is not None
        and int(field.ds_id) == ds_id
    }
    if set(fields) != field_ids:
        raise HTTPException(
            status_code=400,
            detail="Every relation field must belong to the datasource",
        )

    existing_nodes = {
        int(item["id"]): item
        for item in (datasource.table_relation or [])
        if item.get("shape") != _EDGE_SHAPE and item.get("id") is not None
    }
    table_ids = set(existing_nodes) | {int(field.table_id) for field in fields.values()}
    tables = {
        int(table.id): table
        for table_id in table_ids
        if (table := session.get(CoreTable, table_id)) is not None
        and table.id is not None
        and int(table.ds_id) == ds_id
    }
    missing_relation_tables = {int(field.table_id) for field in fields.values()} - set(
        tables
    )
    if missing_relation_tables:
        raise HTTPException(status_code=400, detail="Relation table not found")

    fields_by_table = _fields_by_table(
        session,
        ds_id=ds_id,
        table_ids=set(tables),
    )

    graph: list[dict[str, Any]] = []
    for index, table in enumerate(
        sorted(tables.values(), key=lambda item: int(item.id))
    ):
        graph.append(
            _table_node(
                table,
                fields_by_table.get(int(table.id), []),
                existing=existing_nodes.get(int(table.id)),
                index=index,
            )
        )

    for relation in relations:
        source_id = int(relation["source_field_id"])
        target_id = int(relation["target_field_id"])
        source = fields[source_id]
        target = fields[target_id]
        graph.append(
            {
                "id": f"relation_{source_id}_{target_id}",
                "shape": _EDGE_SHAPE,
                "source": {"cell": int(source.table_id), "port": source_id},
                "target": {"cell": int(target.table_id), "port": target_id},
            }
        )

    save_relation_graph(session, oid=oid, ds_id=ds_id, graph=graph)
    return graph
