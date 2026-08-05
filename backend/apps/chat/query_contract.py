"""Canonical clause-oriented contract for NLQ planning and validation.

The contract is the only executable semantic truth. Clarification edits a
``ContractDraft``; SQL generation receives only a frozen ``QueryContract``.
Every requirement owns one SQL/business clause and is referenced through an
opaque server slot id, so labels and model-generated names never become
contract identity.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Annotated, Any, Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter,
    field_validator,
    model_validator,
)

ClauseType = Literal[
    "projection",
    "output",
    "predicate",
    "group",
    "relation",
    "time_window",
    "order",
    "limit",
]
RequirementSource = Literal[
    "user",
    "rule",
    "terminology",
    "example",
    "schema",
]
OutputOperation = Literal[
    "value",
    "count",
    "count_distinct",
    "sum",
    "avg",
    "min",
    "max",
    "distinct_concat",
    "ratio",
    "difference",
]
PredicateOperator = Literal[
    "eq",
    "ne",
    "in",
    "not_in",
    "gt",
    "gte",
    "lt",
    "lte",
    "like",
    "is_null",
    "is_not_null",
]
TimeWindowMode = Literal["all", "explicit", "rolling"]
TimeBucket = Literal["day", "month", "year"]
PopulationPolicy = Literal["intersection", "left", "right", "union"]


class FieldRef(BaseModel):
    """A physical field identity qualified when a resource is known."""

    model_config = ConfigDict(extra="forbid")

    resource: str = ""
    field: str

    @field_validator("resource", "field")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return value.strip().strip('`"[]')

    @model_validator(mode="after")
    def validate_field(self) -> Self:
        if not self.field:
            raise ValueError("Field reference requires a field name")
        return self

    @property
    def identifier(self) -> str:
        return f"{self.resource}.{self.field}" if self.resource else self.field

    @property
    def resource_name(self) -> str:
        """Physical table name used by SQL ASTs, without a schema prefix."""
        return self.resource.rsplit(".", 1)[-1] if self.resource else ""

    @property
    def normalized(self) -> str:
        resource = self.resource_name.casefold()
        field = self.field.casefold()
        return f"{resource}.{field}" if resource else field


class RequirementBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slot_id: str
    label: str
    source: RequirementSource = "user"
    evidence_refs: list[str] = Field(default_factory=list)

    @field_validator("slot_id", "label")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        return value.strip()

    @model_validator(mode="after")
    def validate_identity(self) -> Self:
        if not self.slot_id:
            raise ValueError("Contract requirement requires a slot_id")
        if not self.label:
            raise ValueError(f"Contract requirement {self.slot_id} requires a label")
        return self


class ProjectionRequirement(RequirementBase):
    clause: Literal["projection"] = "projection"
    mode: Literal["all", "listed"] = "listed"
    fields: list[FieldRef] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_projection(self) -> Self:
        if self.mode == "listed" and not self.fields:
            raise ValueError("Listed projection requires at least one field")
        if self.mode == "all" and self.fields:
            raise ValueError("Projection mode 'all' cannot also list fields")
        return self


class OutputRequirement(RequirementBase):
    clause: Literal["output"] = "output"
    field: FieldRef
    operation: OutputOperation = "value"
    operands: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_output(self) -> Self:
        if self.operation in {"ratio", "difference"} and len(self.operands) != 2:
            raise ValueError(
                f"Derived output {self.slot_id} requires exactly two operand slot ids"
            )
        if self.operation not in {"ratio", "difference"} and self.operands:
            raise ValueError(
                f"Non-derived output {self.slot_id} cannot declare operands"
            )
        return self


class PredicateRequirement(RequirementBase):
    clause: Literal["predicate"] = "predicate"
    field: FieldRef
    operator: PredicateOperator
    values: list[Any] = Field(default_factory=list)
    null_policy: Literal["preserve", "exclude", "only"] = "exclude"

    @model_validator(mode="after")
    def validate_predicate(self) -> Self:
        value_count = len(self.values)
        if self.operator in {"is_null", "is_not_null"} and value_count:
            raise ValueError(f"{self.operator} predicate cannot declare values")
        if self.operator in {"eq", "ne", "gt", "gte", "lt", "lte", "like"}:
            if value_count != 1:
                raise ValueError(f"{self.operator} predicate requires one value")
        if self.operator in {"in", "not_in"} and not value_count:
            raise ValueError(f"{self.operator} predicate requires values")
        if self.operator == "is_null" and self.null_policy != "only":
            raise ValueError("is_null predicate requires null_policy='only'")
        if self.operator == "is_not_null" and self.null_policy != "exclude":
            raise ValueError("is_not_null predicate requires null_policy='exclude'")
        if self.null_policy == "only" and self.operator != "is_null":
            raise ValueError("null_policy='only' requires an is_null predicate")
        return self


class GroupRequirement(RequirementBase):
    clause: Literal["group"] = "group"
    field: FieldRef
    bucket: TimeBucket | None = None


class RelationPair(BaseModel):
    model_config = ConfigDict(extra="forbid")

    left: FieldRef
    right: FieldRef


class RelationRequirement(RequirementBase):
    clause: Literal["relation"] = "relation"
    pairs: list[RelationPair]
    # The join population changes which business entities are returned.  It is
    # therefore part of the executable contract and must never be supplied by
    # an implicit model/default choice.
    population: PopulationPolicy

    @field_validator("pairs")
    @classmethod
    def validate_pairs(cls, value: list[RelationPair]) -> list[RelationPair]:
        if not value:
            raise ValueError("Relation requirement requires at least one field pair")
        return value


class TimeWindowRequirement(RequirementBase):
    clause: Literal["time_window"] = "time_window"
    fields: list[FieldRef]
    mode: TimeWindowMode
    start: str | None = None
    end_exclusive: str | None = None
    rolling_months: int | None = None

    @model_validator(mode="after")
    def validate_window(self) -> Self:
        if not self.fields:
            raise ValueError("Time window requires at least one business-time field")
        if self.mode == "explicit":
            if not self.start or not self.end_exclusive:
                raise ValueError(
                    "Explicit time window requires start and end_exclusive"
                )
        elif self.start or self.end_exclusive:
            raise ValueError(f"{self.mode} time window cannot declare explicit bounds")
        if self.mode == "rolling":
            if not self.rolling_months or self.rolling_months <= 0:
                raise ValueError("Rolling time window requires positive rolling_months")
        elif self.rolling_months is not None:
            raise ValueError(f"{self.mode} time window cannot declare rolling_months")
        return self


class OrderRequirement(RequirementBase):
    clause: Literal["order"] = "order"
    field: FieldRef | None = None
    output_slot_id: str | None = None
    direction: Literal["asc", "desc"] = "asc"

    @model_validator(mode="after")
    def validate_target(self) -> Self:
        if (self.field is None) == (not self.output_slot_id):
            raise ValueError(
                "Order requirement needs exactly one field or output_slot_id target"
            )
        return self


class LimitRequirement(RequirementBase):
    clause: Literal["limit"] = "limit"
    value: int

    @field_validator("value")
    @classmethod
    def validate_limit(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("User result limit must be positive")
        return value


ContractRequirement = Annotated[
    ProjectionRequirement
    | OutputRequirement
    | PredicateRequirement
    | GroupRequirement
    | RelationRequirement
    | TimeWindowRequirement
    | OrderRequirement
    | LimitRequirement,
    Field(discriminator="clause"),
]
_REQUIREMENT_ADAPTER = TypeAdapter(ContractRequirement)


class SlotEffect(BaseModel):
    """One explicit edit against a stable contract slot."""

    model_config = ConfigDict(extra="forbid")

    slot_id: str
    action: Literal["set", "omit"]
    requirement: ContractRequirement | None = None

    @field_validator("slot_id")
    @classmethod
    def normalize_slot_id(cls, value: str) -> str:
        return value.strip()

    @model_validator(mode="after")
    def validate_effect(self) -> Self:
        if not self.slot_id.strip():
            raise ValueError("Slot effect requires a slot_id")
        if self.action == "set" and self.requirement is None:
            raise ValueError("Set effect requires a contract requirement")
        if self.action == "omit" and self.requirement is not None:
            raise ValueError("Omit effect cannot contain a contract requirement")
        if self.requirement is not None and self.requirement.slot_id != self.slot_id:
            raise ValueError(
                f"Effect slot {self.slot_id} does not match requirement slot "
                f"{self.requirement.slot_id}"
            )
        return self


class ContractSlot(BaseModel):
    """One material unresolved clause; it has no executable default."""

    model_config = ConfigDict(extra="forbid")

    slot_id: str
    clause: ClauseType
    label: str
    reason: str
    allow_omit: bool = False
    evidence_refs: list[str] = Field(default_factory=list)

    @field_validator("slot_id", "label", "reason")
    @classmethod
    def normalize_slot_text(cls, value: str) -> str:
        return value.strip()

    @model_validator(mode="after")
    def validate_slot(self) -> Self:
        if not self.slot_id or not self.label or not self.reason:
            raise ValueError("Contract slot requires slot_id, label and reason")
        return self


def _validate_requirement_set(
    requirements: Sequence[ContractRequirement],
    *,
    allow_missing_operands: bool,
) -> None:
    slot_ids = [requirement.slot_id for requirement in requirements]
    if len(slot_ids) != len(set(slot_ids)):
        raise ValueError("Query contract contains duplicate slot ids")
    signatures: set[tuple[Any, ...]] = set()
    for requirement in requirements:
        signature: tuple[Any, ...] | None = None
        if isinstance(requirement, OutputRequirement):
            signature = (
                requirement.clause,
                requirement.field.normalized,
                requirement.operation,
                *requirement.operands,
            )
        elif isinstance(requirement, PredicateRequirement):
            signature = (
                requirement.clause,
                requirement.field.normalized,
                requirement.operator,
                *(str(value) for value in requirement.values),
            )
        elif isinstance(requirement, GroupRequirement):
            signature = (
                requirement.clause,
                requirement.field.normalized,
                requirement.bucket,
            )
        elif isinstance(requirement, TimeWindowRequirement):
            signature = (
                requirement.clause,
                *(field.normalized for field in requirement.fields),
                requirement.mode,
                requirement.start,
                requirement.end_exclusive,
                requirement.rolling_months,
            )
        elif isinstance(requirement, RelationRequirement):
            signature = (
                requirement.clause,
                requirement.population,
                *sorted(
                    f"{pair.left.normalized}={pair.right.normalized}"
                    for pair in requirement.pairs
                ),
            )
        elif isinstance(requirement, OrderRequirement):
            signature = (
                requirement.clause,
                (
                    requirement.field.normalized
                    if requirement.field is not None
                    else requirement.output_slot_id
                ),
                requirement.direction,
            )
        elif isinstance(requirement, LimitRequirement):
            signature = (requirement.clause,)
        elif isinstance(requirement, ProjectionRequirement):
            signature = (requirement.clause,)
        if signature is not None and signature in signatures:
            raise ValueError(
                f"Query contract contains duplicate semantic requirement: {signature}"
            )
        if signature is not None:
            signatures.add(signature)
    known = set(slot_ids)
    for requirement in requirements:
        if isinstance(requirement, OutputRequirement):
            missing = set(requirement.operands) - known
            if missing and not allow_missing_operands:
                raise ValueError(
                    f"Derived output {requirement.slot_id} references unknown slots: "
                    + ", ".join(sorted(missing))
                )
        if isinstance(requirement, OrderRequirement) and requirement.output_slot_id:
            if requirement.output_slot_id not in known and not allow_missing_operands:
                raise ValueError(
                    f"Order {requirement.slot_id} references unknown output slot "
                    f"{requirement.output_slot_id}"
                )


def requirement_resources(requirement: ContractRequirement) -> frozenset[str]:
    """Return physical resources referenced by one canonical requirement."""
    return frozenset(
        field.resource_name.casefold()
        for field in requirement_fields(requirement)
        if field.resource_name
    )


def _connected_resources(
    resources: set[str], requirements: Sequence[ContractRequirement]
) -> set[str]:
    adjacency: dict[str, set[str]] = {resource: set() for resource in resources}
    for requirement in requirements:
        if not isinstance(requirement, RelationRequirement):
            continue
        for pair in requirement.pairs:
            left = pair.left.resource_name.casefold()
            right = pair.right.resource_name.casefold()
            if not left or not right or left == right:
                continue
            adjacency.setdefault(left, set()).add(right)
            adjacency.setdefault(right, set()).add(left)
    if not resources:
        return set()
    pending = [next(iter(resources))]
    visited: set[str] = set()
    while pending:
        current = pending.pop()
        if current in visited:
            continue
        visited.add(current)
        pending.extend(adjacency.get(current, set()) - visited)
    return visited


def validate_relation_closure(
    requirements: Sequence[ContractRequirement],
) -> None:
    """Require an explicit relation for one grouped result spanning resources.

    Independent scalar outputs may still be emitted as separate plans.  Once a
    shared result grain exists, however, an output from another resource cannot
    be interpreted without both a physical relation and a business population
    policy.  This is the semantic boundary that prevents SQL generation from
    silently inventing LEFT/INNER/UNION behaviour.
    """
    group_resources = {
        resource
        for requirement in requirements
        if isinstance(requirement, GroupRequirement)
        for resource in requirement_resources(requirement)
    }
    output_resources = {
        resource
        for requirement in requirements
        if isinstance(requirement, OutputRequirement)
        for resource in requirement_resources(requirement)
    }
    result_resources = group_resources | output_resources
    if not group_resources or len(result_resources) <= 1:
        return
    connected = _connected_resources(result_resources, requirements)
    missing = sorted(result_resources - connected)
    if missing:
        raise ValueError(
            "Grouped multi-resource contract requires explicit relation coverage "
            "and population policy for: " + ", ".join(sorted(result_resources))
        )


class ContractDraft(BaseModel):
    version: Literal[2] = 2
    requirements: list[ContractRequirement] = Field(default_factory=list)
    open_slots: list[ContractSlot] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_draft(self) -> Self:
        _validate_requirement_set(self.requirements, allow_missing_operands=True)
        open_ids = [slot.slot_id for slot in self.open_slots]
        if len(open_ids) != len(set(open_ids)):
            raise ValueError("Contract draft contains duplicate open slot ids")
        overlap = set(open_ids) & {item.slot_id for item in self.requirements}
        if overlap:
            raise ValueError(
                "Contract slots cannot be both resolved and open: "
                + ", ".join(sorted(overlap))
            )
        return self

    def freeze(self) -> QueryContract:
        if self.open_slots:
            raise ValueError("Cannot freeze a contract with unresolved slots")
        return QueryContract(requirements=list(self.requirements))


class QueryContract(BaseModel):
    version: Literal[2] = 2
    requirements: list[ContractRequirement]

    @model_validator(mode="after")
    def validate_contract(self) -> Self:
        if not self.requirements:
            raise ValueError("Executable query contract cannot be empty")
        _validate_requirement_set(self.requirements, allow_missing_operands=False)
        validate_relation_closure(self.requirements)
        return self

    def by_slot(self) -> dict[str, ContractRequirement]:
        return {item.slot_id: item for item in self.requirements}

    def clauses(self, clause: ClauseType) -> list[ContractRequirement]:
        return [item for item in self.requirements if item.clause == clause]


def requirement_fields(requirement: ContractRequirement) -> tuple[FieldRef, ...]:
    """Return all physical fields owned by one clause without role inference."""
    if isinstance(requirement, ProjectionRequirement):
        return tuple(requirement.fields)
    if isinstance(
        requirement,
        (OutputRequirement, PredicateRequirement, GroupRequirement),
    ):
        return (requirement.field,)
    if isinstance(requirement, RelationRequirement):
        return tuple(
            field for pair in requirement.pairs for field in (pair.left, pair.right)
        )
    if isinstance(requirement, TimeWindowRequirement):
        return tuple(requirement.fields)
    if isinstance(requirement, OrderRequirement) and requirement.field is not None:
        return (requirement.field,)
    return ()


def parse_requirement(
    value: Mapping[str, Any] | ContractRequirement,
) -> ContractRequirement:
    if isinstance(value, RequirementBase):
        return value
    return _REQUIREMENT_ADAPTER.validate_python(value)


def replace_requirement(
    requirements: Iterable[ContractRequirement],
    replacement: ContractRequirement,
) -> list[ContractRequirement]:
    """Replace one stable slot, preserving deterministic list order."""
    result: list[ContractRequirement] = []
    replaced = False
    for current in requirements:
        if current.slot_id == replacement.slot_id:
            result.append(replacement)
            replaced = True
        else:
            result.append(current)
    if not replaced:
        result.append(replacement)
    return result
