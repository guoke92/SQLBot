"""Canonical schema for extracted and manually assembled knowledge packages.

The package is a transport contract, not another runtime asset model.  Import
adapters project its typed items into the existing K1-K5 domain stores.
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

KnowledgeItemStatus = Literal["draft", "candidate", "reviewed", "verified", "rejected"]
KnowledgeItemKind = Literal[
    "terminology", "caliber", "relation", "example", "rule", "evidence"
]


class KnowledgeSource(BaseModel):
    model_config = ConfigDict(extra="allow")

    source_id: str
    kind: str
    uri: str = ""
    fingerprint: str = ""
    revision: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgePackageDefaults(BaseModel):
    datasource_id: int | None = None
    datasource_name: str | None = None
    assistant_id: int | None = None


class PackageFieldRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    table_name: str
    field_name: str
    database_name: str = ""
    table_id: int | None = None
    field_id: int | None = None

    @field_validator("table_name", "field_name", "database_name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return value.strip().strip('`"[]')


class VerificationInfo(BaseModel):
    executed: bool = False
    passed: bool = False
    datasource_id: int | None = None
    checked_at: str | None = None
    query_hash: str | None = None
    row_count: int | None = None
    notes: str = ""


class KnowledgeItemBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    item_id: str
    status: KnowledgeItemStatus = "candidate"
    confidence: float = Field(default=0.5, ge=0, le=1)
    evidence_refs: list[str] = Field(default_factory=list)
    provenance: dict[str, Any] = Field(default_factory=dict)
    datasource_id: int | None = None
    datasource_name: str | None = None
    assistant_id: int | None = None

    @field_validator("item_id")
    @classmethod
    def require_item_id(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("item_id is required")
        return value


class TerminologyPackageItem(KnowledgeItemBase):
    kind: Literal["terminology"] = "terminology"
    word: str
    aliases: list[str] = Field(default_factory=list)
    description: str
    enabled: bool = True
    knowledge_meta: dict[str, Any] = Field(default_factory=dict)


class CaliberPackageItem(KnowledgeItemBase):
    kind: Literal["caliber"] = "caliber"
    label: str
    summary: str = ""
    contract_fragment: dict[str, Any] = Field(default_factory=dict)
    draft_definition: dict[str, Any] = Field(default_factory=dict)
    field_targets: list[PackageFieldRef] = Field(default_factory=list)


class RelationPackageItem(KnowledgeItemBase):
    kind: Literal["relation"] = "relation"
    left: PackageFieldRef
    right: PackageFieldRef
    relation_kind: str = "EQUI_JOIN"
    cardinality: str | None = None
    evidence: dict[str, Any] = Field(default_factory=dict)


class ExamplePackageItem(KnowledgeItemBase):
    kind: Literal["example"] = "example"
    question: str
    query: str = ""
    intended_specification: dict[str, Any] = Field(default_factory=dict)
    training_type: Literal["sql", "rest"] = "sql"
    enabled: bool = True
    verification: VerificationInfo = Field(default_factory=VerificationInfo)
    knowledge_meta: dict[str, Any] = Field(default_factory=dict)


class RulePackageItem(KnowledgeItemBase):
    kind: Literal["rule"] = "rule"
    label: str
    content: str


class EvidencePackageItem(KnowledgeItemBase):
    kind: Literal["evidence"] = "evidence"
    subject: str
    predicate: str
    value: Any
    evidence: list[dict[str, Any]] = Field(default_factory=list)


KnowledgePackageItem = Annotated[
    TerminologyPackageItem
    | CaliberPackageItem
    | RelationPackageItem
    | ExamplePackageItem
    | RulePackageItem
    | EvidencePackageItem,
    Field(discriminator="kind"),
]


class KnowledgePackage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["1.0"] = "1.0"
    package_id: str
    title: str = ""
    description: str = ""
    generated_at: str | None = None
    generator: dict[str, Any] = Field(default_factory=dict)
    defaults: KnowledgePackageDefaults = Field(default_factory=KnowledgePackageDefaults)
    sources: list[KnowledgeSource] = Field(default_factory=list)
    items: list[KnowledgePackageItem]

    @model_validator(mode="after")
    def validate_identity(self) -> KnowledgePackage:
        if not self.package_id.strip():
            raise ValueError("package_id is required")
        ids = [item.item_id for item in self.items]
        if len(ids) != len(set(ids)):
            raise ValueError("item_id must be unique within a package")
        return self


class KnowledgeIssue(BaseModel):
    """Stable API issue contract; UI must not branch on display text."""

    code: str
    severity: Literal["info", "warning", "error"] = "info"
    detail: str = ""
    params: dict[str, Any] = Field(default_factory=dict)


_KNOWN_ISSUES: dict[str, tuple[str, Literal["info", "warning", "error"]]] = {
    "item status is rejected": ("ITEM_REJECTED", "error"),
    "evidence is provenance input and is not a runtime asset": (
        "EVIDENCE_RETAINED",
        "info",
    ),
    "terminology must be reviewed before direct publication": (
        "TERMINOLOGY_REVIEW_REQUIRED",
        "warning",
    ),
    "terminology will be global to the workspace": (
        "TERMINOLOGY_GLOBAL_SCOPE",
        "info",
    ),
    "caliber draft must be converted to a QueryIntent default fragment": (
        "CALIBER_DEFINITION_REQUIRED",
        "warning",
    ),
    "relation will enter CANDIDATE and requires confirmation": (
        "RELATION_CONFIRMATION_REQUIRED",
        "warning",
    ),
    "query example has an intended specification but no executable plan": (
        "EXAMPLE_QUERY_REQUIRED",
        "error",
    ),
    "query example requires executed and passed verification": (
        "EXAMPLE_VERIFICATION_REQUIRED",
        "warning",
    ),
    "rule will enter staging and requires explicit certification": (
        "RULE_CERTIFICATION_REQUIRED",
        "info",
    ),
}


def knowledge_issue_from_message(message: str) -> KnowledgeIssue:
    code, severity = _KNOWN_ISSUES.get(message, ("VALIDATION_FAILED", "error"))
    return KnowledgeIssue(code=code, severity=severity, detail=message)


class KnowledgeImportItemResult(BaseModel):
    item_id: str
    kind: str
    readiness: Literal["ready", "review_required", "invalid", "retained_only"]
    action: str = "previewed"
    target_id: int | None = None
    messages: list[str] = Field(default_factory=list)
    issues: list[KnowledgeIssue] = Field(default_factory=list)
    normalized: dict[str, Any] | None = None

    @model_validator(mode="after")
    def normalize_issues(self) -> KnowledgeImportItemResult:
        if not self.issues and self.messages:
            self.issues = [
                knowledge_issue_from_message(message) for message in self.messages
            ]
        return self


class KnowledgeImportReport(BaseModel):
    package_id: str
    package_fingerprint: str
    dry_run: bool
    total: int
    kind_counts: dict[str, int] = Field(default_factory=dict)
    readiness_counts: dict[str, int] = Field(default_factory=dict)
    action_counts: dict[str, int] = Field(default_factory=dict)
    registry_id: int | None = None
    registry_revision: int | None = None
    registry_action: str | None = None
    warnings: list[str] = Field(default_factory=list)
    items: list[KnowledgeImportItemResult] = Field(default_factory=list)


class KnowledgePackageDocument(BaseModel):
    name: str
    content: str

    @field_validator("name")
    @classmethod
    def require_safe_relative_name(cls, value: str) -> str:
        normalized = value.replace("\\", "/").lstrip("/")
        if not normalized or ".." in normalized.split("/"):
            raise ValueError("document name must be a safe relative path")
        return normalized


class KnowledgeImportRequest(BaseModel):
    package: dict[str, Any] | list[Any] | str | None = None
    documents: list[KnowledgePackageDocument] = Field(default_factory=list)
    package_id: str | None = None
    default_datasource_id: int | None = None
    default_datasource_name: str | None = None
    include_kinds: list[KnowledgeItemKind] = Field(default_factory=list)
    expected_preview_fingerprint: str | None = None

    @model_validator(mode="after")
    def require_input(self) -> KnowledgeImportRequest:
        if self.package is None and not self.documents:
            raise ValueError("package or documents is required")
        if self.package is not None and self.documents:
            raise ValueError("package and documents are mutually exclusive")
        return self
