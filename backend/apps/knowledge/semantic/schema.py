"""KnowledgePackage 2.0 and the sole planner-facing knowledge contract."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class PackageMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    package_id: str
    revision: int = Field(default=1, ge=1)
    title: str
    namespace: str
    description: str = ""
    repository: str = ""
    repository_revision: str = ""

    @field_validator("package_id", "title", "namespace")
    @classmethod
    def required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("value is required")
        return value


class SourceDescriptor(BaseModel):
    model_config = ConfigDict(extra="allow")

    source_id: str
    kind: str
    locator: str = ""
    repository_revision: str = ""
    content_hash: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvidenceDescriptor(BaseModel):
    model_config = ConfigDict(extra="allow")

    evidence_id: str
    source_id: str
    evidence_kind: str
    locator: str = ""
    content_hash: str = ""
    claim: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(default=0.5, ge=0, le=1)


class SemanticFieldRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset: str
    field: str
    database: str = ""


class ConceptDefinition(BaseModel):
    model_config = ConfigDict(extra="allow")

    concept_id: str
    name: str
    aliases: list[str] = Field(default_factory=list)
    definition: str
    dictionary: dict[str, str] = Field(default_factory=dict)
    field_targets: list[SemanticFieldRef] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)


class DataEffect(BaseModel):
    model_config = ConfigDict(extra="allow")

    operation: Literal["read", "insert", "update", "delete", "upsert"]
    dataset: str
    fields: list[str] = Field(default_factory=list)
    condition: str = ""
    description: str = ""
    evidence_refs: list[str] = Field(default_factory=list)


class ProcessStage(BaseModel):
    model_config = ConfigDict(extra="allow")

    stage_id: str
    name: str
    description: str = ""
    trigger: str = ""
    enter_conditions: list[str] = Field(default_factory=list)
    exit_conditions: list[str] = Field(default_factory=list)
    next_stages: list[str] = Field(default_factory=list)
    data_effects: list[DataEffect] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)


class SemanticField(BaseModel):
    model_config = ConfigDict(extra="allow")

    field_id: str
    name: str
    description: str = ""
    data_type: str = ""
    dictionary: dict[str, str] = Field(default_factory=dict)
    evidence_refs: list[str] = Field(default_factory=list)


class SemanticDataset(BaseModel):
    model_config = ConfigDict(extra="allow")

    dataset_id: str
    name: str
    description: str = ""
    database: str = ""
    inactive: bool = False
    fields: list[SemanticField] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)


class SemanticRelationship(BaseModel):
    model_config = ConfigDict(extra="allow")

    relationship_id: str
    left: SemanticFieldRef
    right: SemanticFieldRef
    relationship_type: str = "EQUI_JOIN"
    cardinality: str = ""
    business_meaning: str = ""
    status: Literal["proposed", "confirmed"] = "proposed"
    evidence_refs: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0, le=1)


class PackageRelationship(BaseModel):
    """Package-scoped physical table relation extracted from code evidence.

    Endpoints are physical table/field names, not unit-local dataset ids: a
    relation may cross two units and may reference fields no unit declares
    (minimal field declaration). Undeclared endpoints become stub field
    nodes at decomposition and are physically verified at bind time.
    """

    model_config = ConfigDict(extra="forbid")

    left_table: str
    left_field: str
    right_table: str
    right_field: str
    evidence: str = ""
    relationship_type: str = "EQUI_JOIN"
    cardinality: str = ""


class UnitLink(BaseModel):
    """Cross-scenario semantic link declared by one unit about another.

    Only semantic direction lives here (prerequisite / validates).
    Data coupling (shares_data) is derived by the decomposer from shared
    dataset nodes and must not be declared.
    """

    model_config = ConfigDict(extra="forbid")

    target_unit: str
    kind: Literal["prerequisite", "validates"]
    via: list[SemanticFieldRef] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    description: str = ""


class SemanticMetric(BaseModel):
    model_config = ConfigDict(extra="allow")

    metric_id: str
    name: str
    description: str = ""
    aggregation: str
    field: SemanticFieldRef | None = None
    filters: list[dict[str, Any]] = Field(default_factory=list)
    grain: list[SemanticFieldRef] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)


class CaliberDefinition(BaseModel):
    model_config = ConfigDict(extra="allow")

    caliber_id: str
    label: str
    description: str = ""
    contract_fragment: dict[str, Any]
    field_targets: list[SemanticFieldRef] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)


class DomainRuleDefinition(BaseModel):
    model_config = ConfigDict(extra="allow")

    rule_id: str
    label: str
    content: str
    applicability: str = ""
    query_impact: str
    field_targets: list[SemanticFieldRef] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_data_query_impact(self) -> DomainRuleDefinition:
        if not self.applicability.strip() or not self.query_impact.strip():
            raise ValueError(
                "domain rule requires a concrete business scope and query impact"
            )
        if not self.field_targets:
            raise ValueError(
                "domain rule must target physical business data; governance instructions are not knowledge"
            )
        return self


class VerifiedQueryPattern(BaseModel):
    """A query pattern. Execution proof lives on the binding, not the revision."""

    model_config = ConfigDict(extra="allow")

    pattern_id: str
    question: str
    query: str
    intended_specification: dict[str, Any] = Field(default_factory=dict)
    verification: dict[str, Any] = Field(default_factory=dict)
    evidence_refs: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_query_text(self) -> VerifiedQueryPattern:
        if not self.query.strip():
            raise ValueError("query pattern requires query")
        return self


class KnowledgeUnitContent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    concepts: list[ConceptDefinition] = Field(default_factory=list)
    processes: list[ProcessStage] = Field(default_factory=list)
    datasets: list[SemanticDataset] = Field(default_factory=list)
    relationships: list[SemanticRelationship] = Field(default_factory=list)
    metrics: list[SemanticMetric] = Field(default_factory=list)
    calibers: list[CaliberDefinition] = Field(default_factory=list)
    domain_rules: list[DomainRuleDefinition] = Field(default_factory=list)
    verified_query_patterns: list[VerifiedQueryPattern] = Field(default_factory=list)


class KnowledgeUnitEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    unit_id: str
    revision: int = Field(default=1, ge=1)
    title: str
    aliases: list[str] = Field(default_factory=list)
    domain: str
    applicability: str = ""
    description: str
    content: KnowledgeUnitContent
    evidence_refs: list[str] = Field(default_factory=list)
    unit_links: list[UnitLink] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    conflicts: list[dict[str, Any]] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0, le=1)

    @model_validator(mode="after")
    def require_business_data_semantics(self) -> KnowledgeUnitEntry:
        if (
            not self.title.strip()
            or not self.description.strip()
            or not self.domain.strip()
        ):
            raise ValueError("knowledge unit requires title, domain and description")
        if not self.content.datasets:
            raise ValueError(
                "knowledge unit must connect the business scenario to at least one dataset"
            )
        actionable = (
            self.content.processes
            or self.content.metrics
            or self.content.calibers
            or self.content.domain_rules
            or self.content.verified_query_patterns
        )
        all_inactive = bool(self.content.datasets) and all(
            dataset.inactive for dataset in self.content.datasets
        )
        if not actionable and not all_inactive:
            raise ValueError(
                "knowledge unit must describe a process, metric, caliber, rule or verified query "
                "unless every declared dataset is inactive (dormant-registration unit)"
            )
        if actionable and all_inactive:
            raise ValueError(
                "inactive-registration unit must not declare processes/metrics/calibers/rules/patterns; "
                "dormant tables carry no business semantics"
            )
        return self


class KnowledgePackageV2(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["2.0"] = "2.0"
    package: PackageMetadata
    sources: list[SourceDescriptor] = Field(default_factory=list)
    evidence: list[EvidenceDescriptor] = Field(default_factory=list)
    relationships: list[PackageRelationship] = Field(default_factory=list)
    knowledge_units: list[KnowledgeUnitEntry]

    @model_validator(mode="after")
    def validate_references(self) -> KnowledgePackageV2:
        source_ids = [source.source_id for source in self.sources]
        evidence_ids = [evidence.evidence_id for evidence in self.evidence]
        unit_ids = [unit.unit_id for unit in self.knowledge_units]
        for label, values in (
            ("source_id", source_ids),
            ("evidence_id", evidence_ids),
            ("unit_id", unit_ids),
        ):
            if len(values) != len(set(values)):
                raise ValueError(f"{label} must be unique")
        sources = set(source_ids)
        for evidence in self.evidence:
            if evidence.source_id not in sources:
                raise ValueError(
                    f"evidence {evidence.evidence_id} references unknown source {evidence.source_id}"
                )
        known_evidence = set(evidence_ids)
        unit_id_set = set(unit_ids)
        for unit in self.knowledge_units:
            for link in unit.unit_links:
                if link.target_unit == unit.unit_id:
                    raise ValueError(f"unit {unit.unit_id} links to itself")
                if link.target_unit not in unit_id_set:
                    raise ValueError(
                        f"unit {unit.unit_id} links to unknown unit "
                        f"{link.target_unit!r}"
                    )
            validate_knowledge_unit(unit, known_evidence)
        return self


def collect_evidence_refs(unit: KnowledgeUnitEntry) -> set[str]:
    """Collect every evidence reference reachable from one knowledge unit.

    Shared by reference-closure validation and extraction QA so the two never
    drift on which buckets/fields can cite evidence.
    """
    refs = set(unit.evidence_refs)
    for bucket in (
        unit.content.concepts,
        unit.content.processes,
        unit.content.datasets,
        unit.content.relationships,
        unit.content.metrics,
        unit.content.calibers,
        unit.content.domain_rules,
        unit.content.verified_query_patterns,
    ):
        for item in bucket:
            refs.update(item.evidence_refs)
    for dataset in unit.content.datasets:
        for field in dataset.fields:
            refs.update(field.evidence_refs)
    for process in unit.content.processes:
        for effect in process.data_effects:
            refs.update(effect.evidence_refs)
    for link in unit.unit_links:
        refs.update(link.evidence_refs)
    return refs


def validate_knowledge_unit(
    unit: KnowledgeUnitEntry,
    known_evidence: set[str],
) -> None:
    """Validate the reference closure shared by import and revision editing."""
    missing = sorted(collect_evidence_refs(unit) - known_evidence)
    if missing:
        raise ValueError(
            f"unit {unit.unit_id} references unknown evidence: {', '.join(missing)}"
        )

    dataset_ids = {dataset.dataset_id for dataset in unit.content.datasets}
    field_ids = {
        dataset.dataset_id: {field.field_id for field in dataset.fields}
        for dataset in unit.content.datasets
    }

    def validate_field_ref(ref: SemanticFieldRef, owner: str) -> None:
        if ref.dataset not in dataset_ids:
            raise ValueError(f"{owner} references unknown dataset {ref.dataset}")
        if ref.field not in field_ids.get(ref.dataset, set()):
            raise ValueError(
                f"{owner} references unknown field {ref.dataset}.{ref.field}"
            )

    for relation in unit.content.relationships:
        validate_field_ref(relation.left, f"relationship {relation.relationship_id}")
        validate_field_ref(relation.right, f"relationship {relation.relationship_id}")
    for metric in unit.content.metrics:
        if metric.field is not None:
            validate_field_ref(metric.field, f"metric {metric.metric_id}")
        for grain in metric.grain:
            validate_field_ref(grain, f"metric {metric.metric_id}")
    for caliber in unit.content.calibers:
        for target in caliber.field_targets:
            validate_field_ref(target, f"caliber {caliber.caliber_id}")
    for rule in unit.content.domain_rules:
        for target in rule.field_targets:
            validate_field_ref(target, f"rule {rule.rule_id}")
    for concept in unit.content.concepts:
        for target in concept.field_targets:
            validate_field_ref(target, f"concept {concept.concept_id}")
    for link in unit.unit_links:
        for ref in link.via:
            validate_field_ref(ref, f"unit link {link.target_unit}")
    for process in unit.content.processes:
        for effect in process.data_effects:
            if effect.dataset not in dataset_ids:
                raise ValueError(
                    f"process {process.stage_id} references unknown dataset {effect.dataset}"
                )
            unknown_fields = sorted(
                set(effect.fields) - field_ids.get(effect.dataset, set())
            )
            if unknown_fields:
                raise ValueError(
                    f"process {process.stage_id} references unknown fields in "
                    f"{effect.dataset}: {', '.join(unknown_fields)}"
                )
