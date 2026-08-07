"""Canonical clause-oriented contract for NLQ planning and validation.

The contract is the only executable semantic truth. Clarification edits a
``ContractDraft``; SQL generation receives only a frozen ``QueryContract``.
Every requirement owns one SQL/business clause and is referenced through an
opaque server slot id, so labels and model-generated names never become
contract identity.

Freezing does not make every clause equally permanent.  A clause is
*confirmed* only when its evidence traces back to something the user said;
everything else is a system inference that stays revocable, so a failure in
the system's own reasoning can never invalidate what the user did confirm.
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

from apps.chat.contract.issues import has_user_evidence

QUERY_CONTRACT_VERSION = 4

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
    "model",
    "rule",
    "terminology",
    "example",
    "schema",
    "knowledge",
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
ResultMode = Literal["detail", "aggregate"]


class FieldRef(BaseModel):
    """A physical field identity qualified when a resource is known."""

    model_config = ConfigDict(extra="forbid", frozen=True)

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
    model_config = ConfigDict(extra="forbid", frozen=True)

    slot_id: str
    label: str
    source: RequirementSource = "model"
    evidence_refs: tuple[str, ...] = ()

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
        # A clause counts as user-confirmed only when its evidence points at
        # the user's own words.  Without that anchor the assessor could label
        # its own inference as intent and make it unrevocable.
        if self.source == "user" and not has_user_evidence(self.evidence_refs):
            object.__setattr__(self, "source", "model")
        return self

    @property
    def is_confirmed(self) -> bool:
        """Whether this clause is locked for the turn.

        User evidence is strongest. Certified knowledge binds (source=knowledge
        with knowledge:caliber:* evidence) also count as filled so assess does
        not re-ask; the user can still override on a later turn / answer.
        """
        if self.source == "user":
            return True
        if self.source == "knowledge" and any(
            str(ref).startswith("knowledge:caliber:") for ref in self.evidence_refs
        ):
            return True
        return False


class ProjectionRequirement(RequirementBase):
    clause: Literal["projection"] = "projection"
    mode: Literal["all", "listed"] = "listed"
    fields: tuple[FieldRef, ...] = ()

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
    operands: tuple[str, ...] = ()

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
    values: tuple[Any, ...] = ()
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
    model_config = ConfigDict(extra="forbid", frozen=True)

    left: FieldRef
    right: FieldRef


class RelationRequirement(RequirementBase):
    clause: Literal["relation"] = "relation"
    pairs: tuple[RelationPair, ...]
    # The join population changes which business entities are returned.  It is
    # therefore part of the executable contract and must never be supplied by
    # an implicit model/default choice.
    population: PopulationPolicy

    @field_validator("pairs")
    @classmethod
    def validate_pairs(
        cls, value: tuple[RelationPair, ...]
    ) -> tuple[RelationPair, ...]:
        if not value:
            raise ValueError("Relation requirement requires at least one field pair")
        return value


class TimeWindowRequirement(RequirementBase):
    clause: Literal["time_window"] = "time_window"
    fields: tuple[FieldRef, ...]
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


def infer_result_mode(
    requirements: Sequence[ContractRequirement],
) -> ResultMode:
    """Derive detail-vs-aggregate shape from canonical clauses.

    A record/detail request does not need a synthetic grouping or record-id
    clarification.  Grouping and aggregate outputs are the only constructs
    that turn the result into an aggregate shape.
    """

    if any(isinstance(item, GroupRequirement) for item in requirements):
        return "aggregate"
    if any(
        isinstance(item, OutputRequirement) and item.operation != "value"
        for item in requirements
    ):
        return "aggregate"
    return "detail"


def _validate_result_shape(
    requirements: Sequence[ContractRequirement],
    result_mode: ResultMode,
) -> None:
    """Reject clause combinations that cannot describe one result shape."""

    projections = [
        item for item in requirements if isinstance(item, ProjectionRequirement)
    ]
    if result_mode == "aggregate" and projections:
        raise ValueError(
            "Aggregate contracts must express dimensions and metrics with "
            "group/output clauses instead of projection"
        )

    outputs = {
        item.slot_id: item
        for item in requirements
        if isinstance(item, OutputRequirement)
    }
    for output in outputs.values():
        if output.operation not in {"ratio", "difference"}:
            continue
        operands = [outputs.get(slot_id) for slot_id in output.operands]
        if any(item is None for item in operands):
            raise ValueError(
                f"Derived output {output.slot_id} operands must reference outputs"
            )
        if any(item.operation == "value" for item in operands if item is not None):
            raise ValueError(
                f"Derived aggregate output {output.slot_id} cannot use row-level "
                "value operands"
            )


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
            # A query has exactly one row limit, so the clause alone identifies it.
            signature = (requirement.clause,)
        elif isinstance(requirement, ProjectionRequirement):
            # Displaying two different things is two decisions the user can
            # confirm separately, so only the same fields are a duplicate.
            signature = (
                requirement.clause,
                requirement.mode,
                *sorted(field.normalized for field in requirement.fields),
            )
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


def _prune_dangling_requirements(
    requirements: Sequence[ContractRequirement],
) -> list[ContractRequirement]:
    """Drop clauses whose referenced slots no longer exist, until stable."""
    current = list(requirements)
    while True:
        known = {item.slot_id for item in current}
        kept: list[ContractRequirement] = []
        for item in current:
            if isinstance(item, OutputRequirement) and item.operands:
                if not set(item.operands) <= known:
                    continue
            if isinstance(item, OrderRequirement) and item.output_slot_id:
                if item.output_slot_id not in known:
                    continue
            kept.append(item)
        if len(kept) == len(current):
            return kept
        current = kept


class ContractDraft(BaseModel):
    version: Literal[4] = 4
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
        return QueryContract.model_validate(
            {
                "requirements": [
                    item.model_dump(mode="json") for item in self.requirements
                ]
            }
        )

    def without(self, slot_ids: Iterable[str]) -> QueryContract | None:
        """Freeze this draft with the given clauses and their dependents gone.

        Returns ``None`` when nothing executable remains.
        """
        excluded = set(slot_ids)
        kept = _prune_dangling_requirements(
            [item for item in self.requirements if item.slot_id not in excluded]
        )
        if not kept:
            return None
        try:
            return QueryContract.model_validate(
                {"requirements": [item.model_dump(mode="json") for item in kept]}
            )
        except ValueError:
            return None

    def minimal_executable(self) -> QueryContract | None:
        """Return only what the user confirmed.

        This is the escape hatch of the semantic gate: confirmed choices stay
        executable even when the system's own inferences, its validators or the
        assessor cannot complete, so an internal failure never becomes a dead
        end for the user.
        """
        return self.without(
            item.slot_id for item in self.requirements if not item.is_confirmed
        )


class QueryContract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    version: Literal[4] = 4
    requirements: tuple[ContractRequirement, ...]
    result_mode: ResultMode | None = None

    @model_validator(mode="after")
    def validate_contract(self) -> Self:
        if not self.requirements:
            raise ValueError("Executable query contract cannot be empty")
        _validate_requirement_set(self.requirements, allow_missing_operands=False)
        inferred = infer_result_mode(self.requirements)
        if self.result_mode is None:
            object.__setattr__(self, "result_mode", inferred)
        elif self.result_mode != inferred:
            raise ValueError(
                f"Contract result_mode={self.result_mode} conflicts with "
                f"its {inferred} requirements"
            )
        _validate_result_shape(self.requirements, inferred)
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
