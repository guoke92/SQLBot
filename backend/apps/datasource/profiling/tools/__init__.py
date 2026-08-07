"""Mining tool catalog for the metadata cognition agent."""

from __future__ import annotations

from typing import Any

from langchain_core.tools import BaseTool, StructuredTool
from pydantic import BaseModel, Field

from apps.conversation.session import session_scope
from apps.datasource.profiling.models import ScanRunMode

# Agent tools only — facts collection is owned by the worker/bootstrap path.
MINING_TOOL_NAMES = frozenset(
    {
        "list_tables_brief",
        "get_profile_brief",
        "get_samples",
        "extract_ddl_constraints",
        "refresh_dictionary_for_table",
        "compute_ai_priority",
        "name_similarity",
        "overlap_probe",
        "fanout_probe",
        "cooccurrence_probe",
        "formula_probe",
        "hierarchy_probe",
        "upsert_relation_candidate",
        "upsert_binding_candidate",
        "list_relation_candidates",
        "list_published_relations",
        "draft_field_description",
        "draft_table_description",
        "mine_query_log_joins",
        "confirm_relation",
        "reject_relation",
    }
)

# Per-mode tool allow-lists (confirm tools still gated by allow_confirm).
# Further intersected with MiningPolicy capabilities at build time.
_MODE_TOOLS: dict[str, frozenset[str]] = {
    ScanRunMode.VALIDATE.value: frozenset(
        {
            "list_tables_brief",
            "get_profile_brief",
            "list_relation_candidates",
            "list_published_relations",
            "name_similarity",
            "overlap_probe",
            "fanout_probe",
            "cooccurrence_probe",
            "formula_probe",
            "hierarchy_probe",
            "upsert_relation_candidate",
            "upsert_binding_candidate",
            "mine_query_log_joins",
        }
    ),
    ScanRunMode.SEMANTIC.value: frozenset(
        {
            "list_tables_brief",
            "get_profile_brief",
            "get_samples",
            "compute_ai_priority",
            "name_similarity",
            "overlap_probe",
            "fanout_probe",
            "cooccurrence_probe",
            "formula_probe",
            "hierarchy_probe",
            "upsert_relation_candidate",
            "upsert_binding_candidate",
            "list_relation_candidates",
            "list_published_relations",
            "extract_ddl_constraints",
            "draft_field_description",
            "draft_table_description",
            "mine_query_log_joins",
            "refresh_dictionary_for_table",
        }
    ),
    ScanRunMode.MANUAL.value: MINING_TOOL_NAMES
    - {"confirm_relation", "reject_relation"},
    ScanRunMode.FULL.value: MINING_TOOL_NAMES
    - {"confirm_relation", "reject_relation"},
}


class _Empty(BaseModel):
    pass


class _TableArgs(BaseModel):
    table_id: int | None = None


class _SampleArgs(BaseModel):
    table_id: int | None = None
    limit: int = 5


class _NameSimArgs(BaseModel):
    field_ids: list[int] = Field(default_factory=list)
    limit: int = 20


class _ProbeArgs(BaseModel):
    source_field_id: int
    target_field_id: int
    sample_size: int = 2000


class _FormulaArgs(BaseModel):
    result_field_id: int
    left_field_id: int
    right_field_id: int | None = None
    sample_size: int = 200


class _HierarchyArgs(BaseModel):
    parent_field_id: int
    child_field_id: int
    sample_size: int = 500


class _UpsertRelationArgs(BaseModel):
    source_field_id: int
    target_field_id: int
    kind: str = "EQUI_JOIN"
    confidence: float | None = None
    evidence: dict[str, Any] | None = None
    cardinality: str | None = None


class _BindingArgs(BaseModel):
    source_field_id: int
    target_field_id: int
    confidence: float | None = None
    evidence: dict[str, Any] | None = None


class _DraftFieldArgs(BaseModel):
    field_id: int
    description: str
    apply: bool = False
    force: bool = False


class _DraftTableArgs(BaseModel):
    description: str
    table_id: int | None = None
    apply: bool = False
    force: bool = False


class _RelationIdArgs(BaseModel):
    relation_id: int


class _QueryLogArgs(BaseModel):
    min_count: int = 2
    sql_limit: int = 200


def build_mining_tools(
    *,
    oid: int,
    ds_id: int,
    table_id: int | None,
    run_mode: str,
    allow_confirm: bool = False,
    capabilities: frozenset[str] | set[str] | None = None,
) -> list[BaseTool]:
    from apps.datasource.profiling.capability_catalog import tools_for_capabilities
    from apps.datasource.profiling.tools_impl import MiningContext, MiningOps

    ctx = MiningContext(oid=oid, ds_id=ds_id, table_id=table_id, run_mode=run_mode)
    ops = MiningOps(ctx)
    mode = (run_mode or ScanRunMode.SEMANTIC.value).strip()
    allowed = set(_MODE_TOOLS.get(mode, _MODE_TOOLS[ScanRunMode.SEMANTIC.value]))
    if capabilities is not None:
        allowed &= set(tools_for_capabilities(capabilities))
    if allow_confirm:
        allowed |= {"confirm_relation", "reject_relation"}

    def list_tables_brief() -> dict[str, Any]:
        with session_scope() as session:
            return ops.list_tables_brief(session)

    def get_profile_brief(table_id: int | None = None) -> dict[str, Any]:
        with session_scope() as session:
            return ops.get_profile_brief(session, table_id=table_id)

    def get_samples(table_id: int | None = None, limit: int = 5) -> dict[str, Any]:
        with session_scope() as session:
            return ops.get_samples(session, table_id=table_id, limit=limit)

    def extract_ddl_constraints(table_id: int | None = None) -> dict[str, Any]:
        with session_scope() as session:
            return ops.extract_ddl_constraints(session, table_id=table_id)

    def refresh_dictionary_for_table(table_id: int | None = None) -> dict[str, Any]:
        with session_scope() as session:
            return ops.refresh_dictionary_for_table(session, table_id=table_id)

    def compute_ai_priority(table_id: int | None = None) -> dict[str, Any]:
        with session_scope() as session:
            return ops.compute_ai_priority(session, table_id=table_id)

    def mine_query_log_joins(
        min_count: int = 2, sql_limit: int = 200
    ) -> dict[str, Any]:
        with session_scope() as session:
            return ops.mine_query_log_joins(
                session, min_count=min_count, sql_limit=sql_limit
            )

    def name_similarity(field_ids: list[int] | None = None, limit: int = 20) -> dict[str, Any]:
        with session_scope() as session:
            return ops.name_similarity(session, field_ids=field_ids or [], limit=limit)

    def overlap_probe(
        source_field_id: int, target_field_id: int, sample_size: int = 2000
    ) -> dict[str, Any]:
        with session_scope() as session:
            return ops.overlap_probe(
                session,
                source_field_id=source_field_id,
                target_field_id=target_field_id,
                sample_size=sample_size,
            )

    def fanout_probe(
        source_field_id: int, target_field_id: int, sample_size: int = 2000
    ) -> dict[str, Any]:
        with session_scope() as session:
            return ops.fanout_probe(
                session,
                source_field_id=source_field_id,
                target_field_id=target_field_id,
                sample_size=sample_size,
            )

    def cooccurrence_probe(
        source_field_id: int, target_field_id: int, sample_size: int = 2000
    ) -> dict[str, Any]:
        with session_scope() as session:
            return ops.cooccurrence_probe(
                session,
                source_field_id=source_field_id,
                target_field_id=target_field_id,
                sample_size=sample_size,
            )

    def formula_probe(
        result_field_id: int,
        left_field_id: int,
        right_field_id: int | None = None,
        sample_size: int = 200,
    ) -> dict[str, Any]:
        with session_scope() as session:
            return ops.formula_probe(
                session,
                result_field_id=result_field_id,
                left_field_id=left_field_id,
                right_field_id=right_field_id,
                sample_size=sample_size,
            )

    def hierarchy_probe(
        parent_field_id: int,
        child_field_id: int,
        sample_size: int = 500,
    ) -> dict[str, Any]:
        with session_scope() as session:
            return ops.hierarchy_probe(
                session,
                parent_field_id=parent_field_id,
                child_field_id=child_field_id,
                sample_size=sample_size,
            )

    def upsert_relation_candidate(
        source_field_id: int,
        target_field_id: int,
        kind: str = "EQUI_JOIN",
        confidence: float | None = None,
        evidence: dict[str, Any] | None = None,
        cardinality: str | None = None,
    ) -> dict[str, Any]:
        with session_scope() as session:
            return ops.upsert_relation_candidate(
                session,
                source_field_id=source_field_id,
                target_field_id=target_field_id,
                kind=kind,
                confidence=confidence,
                evidence=evidence,
                cardinality=cardinality,
            )

    def upsert_binding_candidate(
        source_field_id: int,
        target_field_id: int,
        confidence: float | None = None,
        evidence: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        with session_scope() as session:
            return ops.upsert_binding_candidate(
                session,
                source_field_id=source_field_id,
                target_field_id=target_field_id,
                confidence=confidence,
                evidence=evidence,
            )

    def list_relation_candidates() -> dict[str, Any]:
        with session_scope() as session:
            return ops.list_relations(session, status="CANDIDATE")

    def list_published_relations() -> dict[str, Any]:
        with session_scope() as session:
            return ops.list_relations(session, status="CONFIRMED")

    def draft_field_description(
        field_id: int,
        description: str,
        apply: bool = False,
        force: bool = False,
    ) -> dict[str, Any]:
        with session_scope() as session:
            return ops.draft_field_description(
                session,
                field_id=field_id,
                description=description,
                apply=apply,
                force=force,
                allow_apply=False,
            )

    def draft_table_description(
        description: str,
        table_id: int | None = None,
        apply: bool = False,
        force: bool = False,
    ) -> dict[str, Any]:
        with session_scope() as session:
            return ops.draft_table_description(
                session,
                description=description,
                table_id=table_id,
                apply=apply,
                force=force,
                allow_apply=False,
            )

    catalog: list[tuple[str, Any, type[BaseModel], str]] = [
        ("list_tables_brief", list_tables_brief, _Empty, "List compact table briefs."),
        ("get_profile_brief", get_profile_brief, _TableArgs, "Get profile brief."),
        ("get_samples", get_samples, _SampleArgs, "Fetch bounded sample rows (redacted)."),
        (
            "extract_ddl_constraints",
            extract_ddl_constraints,
            _TableArgs,
            "Read PK/FK constraints (read-only; facts bootstrap publishes CONFIRMED DDL).",
        ),
        (
            "refresh_dictionary_for_table",
            refresh_dictionary_for_table,
            _TableArgs,
            "Refresh enabled dictionary values for a table.",
        ),
        (
            "compute_ai_priority",
            compute_ai_priority,
            _TableArgs,
            "Score whether a table is high-value / recommend deep preset; include table_role hint.",
        ),
        (
            "mine_query_log_joins",
            mine_query_log_joins,
            _QueryLogArgs,
            "Mine EQUI_JOIN candidates from historical successful SQL (never auto-confirms).",
        ),
        ("name_similarity", name_similarity, _NameSimArgs, "Rank name-similar field pairs."),
        ("overlap_probe", overlap_probe, _ProbeArgs, "Probe value overlap."),
        ("fanout_probe", fanout_probe, _ProbeArgs, "Probe join fan-out."),
        (
            "cooccurrence_probe",
            cooccurrence_probe,
            _ProbeArgs,
            "Probe intra-table co-non-null rate.",
        ),
        (
            "formula_probe",
            formula_probe,
            _FormulaArgs,
            "Probe numeric formula relations (sum/product/diff/ratio).",
        ),
        (
            "hierarchy_probe",
            hierarchy_probe,
            _HierarchyArgs,
            "Probe path/prefix hierarchy between string fields.",
        ),
        (
            "upsert_relation_candidate",
            upsert_relation_candidate,
            _UpsertRelationArgs,
            "Upsert a CANDIDATE relation.",
        ),
        (
            "upsert_binding_candidate",
            upsert_binding_candidate,
            _BindingArgs,
            "Upsert a BINDING candidate (1:1 co-occurrence).",
        ),
        (
            "list_relation_candidates",
            list_relation_candidates,
            _Empty,
            "List candidate relations.",
        ),
        (
            "list_published_relations",
            list_published_relations,
            _Empty,
            "List confirmed relations.",
        ),
        (
            "draft_field_description",
            draft_field_description,
            _DraftFieldArgs,
            "Draft a field description (never auto-applies; confirm separately).",
        ),
        (
            "draft_table_description",
            draft_table_description,
            _DraftTableArgs,
            "Draft a table description (never auto-applies; confirm separately).",
        ),
    ]

    tools: list[BaseTool] = []
    for name, func, schema, desc in catalog:
        if name not in allowed:
            continue
        tools.append(
            StructuredTool.from_function(
                func=func, name=name, description=desc, args_schema=schema
            )
        )

    if allow_confirm and "confirm_relation" in allowed:

        def confirm_relation(relation_id: int) -> dict[str, Any]:
            with session_scope() as session:
                return ops.set_relation_status(session, relation_id, "CONFIRMED")

        def reject_relation(relation_id: int) -> dict[str, Any]:
            with session_scope() as session:
                return ops.set_relation_status(session, relation_id, "REJECTED")

        tools.extend(
            [
                StructuredTool.from_function(
                    func=confirm_relation,
                    name="confirm_relation",
                    description="Confirm a candidate relation.",
                    args_schema=_RelationIdArgs,
                ),
                StructuredTool.from_function(
                    func=reject_relation,
                    name="reject_relation",
                    description="Reject a candidate relation.",
                    args_schema=_RelationIdArgs,
                ),
            ]
        )

    return tools
