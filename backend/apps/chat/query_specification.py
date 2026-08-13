"""Canonical, revisioned business specification for NLQ execution.

This module deliberately contains no clarification UI state and no physical
SQL/REST plan.  It is the sole semantic input accepted by plan generation and
plan validation.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from copy import deepcopy
from typing import Annotated, Any, Literal, Self

import orjson
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter,
    field_validator,
    model_validator,
)

RequirementSource = Literal[
    "user",
    "model",
    "terminology",
    "example",
    "schema",
    "knowledge",
    "system_default",
]
RequirementStatus = Literal["active", "superseded", "dropped"]


def is_user_evidence_ref(ref: str) -> bool:
    """True when a citation points at immutable user wording in this chat."""
    value = (ref or "").strip()
    return (
        value == "user:question"
        or value.startswith("user:answer:")
        or value.startswith("user:prior_question")
        or value.startswith("user:prior_answer:")
    )
Aggregation = Literal[
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


class FieldRef(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    resource: str = ""
    field: str = ""
    semantic_ref: str = ""

    @field_validator("resource", "field", "semantic_ref")
    @classmethod
    def normalize(cls, value: str) -> str:
        return value.strip().strip('`"[]')

    @model_validator(mode="after")
    def validate_identity(self) -> Self:
        if not self.field and not self.semantic_ref:
            raise ValueError("FieldRef requires field or semantic_ref")
        return self

    @property
    def identifier(self) -> str:
        if self.field:
            return f"{self.resource}.{self.field}" if self.resource else self.field
        return self.semantic_ref

    @property
    def resource_name(self) -> str:
        return self.resource.rsplit(".", 1)[-1] if self.resource else ""

    @property
    def normalized(self) -> str:
        return self.identifier.casefold()


class RequirementBase(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    requirement_id: str
    business_label: str
    evidence_refs: tuple[str, ...] = ()
    confidence: float = Field(default=0.5, ge=0, le=1)
    source: RequirementSource = "model"
    status: RequirementStatus = "active"

    @field_validator("requirement_id", "business_label")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        return value.strip()

    @model_validator(mode="after")
    def validate_required_text(self) -> Self:
        if not self.requirement_id or not self.business_label:
            raise ValueError("Requirement requires requirement_id and business_label")
        if self.source == "user" and not any(
            is_user_evidence_ref(ref) for ref in self.evidence_refs
        ):
            raise ValueError("User requirement must cite immutable user evidence")
        return self

    @property
    def label(self) -> str:
        return self.business_label


class OutputRequirement(RequirementBase):
    clause: Literal["output"] = "output"
    field: FieldRef
    aggregation: Aggregation = "value"
    operand_requirement_ids: tuple[str, ...] = ()

    @property
    def operation(self) -> Aggregation:
        return self.aggregation

    @property
    def operands(self) -> tuple[str, ...]:
        return self.operand_requirement_ids

    @model_validator(mode="after")
    def validate_derived_output(self) -> Self:
        derived = self.aggregation in {"ratio", "difference"}
        if derived != (len(self.operand_requirement_ids) == 2):
            raise ValueError("Derived outputs require exactly two operands")
        return self


class PredicateRequirement(RequirementBase):
    clause: Literal["predicate"] = "predicate"
    field: FieldRef
    operator: PredicateOperator
    values: tuple[Any, ...] = ()
    null_policy: Literal["preserve", "exclude", "only"] = "exclude"

    @model_validator(mode="after")
    def validate_values(self) -> Self:
        count = len(self.values)
        if self.operator in {"is_null", "is_not_null"} and count:
            raise ValueError(f"{self.operator} cannot declare values")
        if (
            self.operator in {"eq", "ne", "gt", "gte", "lt", "lte", "like"}
            and count != 1
        ):
            raise ValueError(f"{self.operator} requires one value")
        if self.operator in {"in", "not_in"} and not count:
            raise ValueError(f"{self.operator} requires values")
        return self


class GroupRequirement(RequirementBase):
    clause: Literal["group"] = "group"
    field: FieldRef
    bucket: Literal["day", "week", "month", "quarter", "year"] | None = None


class TimeWindowRequirement(RequirementBase):
    clause: Literal["time_window"] = "time_window"
    fields: tuple[FieldRef, ...]
    mode: Literal["all", "explicit", "rolling"]
    start: str | None = None
    end_exclusive: str | None = None
    rolling_months: int | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def validate_window(self) -> Self:
        if not self.fields:
            raise ValueError("Time window requires at least one field")
        if self.mode == "explicit" and (not self.start or not self.end_exclusive):
            raise ValueError("Explicit time window requires start and end_exclusive")
        if self.mode == "rolling" and self.rolling_months is None:
            raise ValueError("Rolling time window requires rolling_months")
        if self.mode == "all" and (
            self.start or self.end_exclusive or self.rolling_months is not None
        ):
            raise ValueError("All-time window cannot declare boundaries")
        if self.mode == "explicit" and self.rolling_months is not None:
            raise ValueError("Explicit time window cannot declare rolling_months")
        if self.mode == "rolling" and (self.start or self.end_exclusive):
            raise ValueError("Rolling time window cannot declare explicit boundaries")
        return self


class OrderRequirement(RequirementBase):
    clause: Literal["order"] = "order"
    field: FieldRef | None = None
    output_requirement_id: str | None = None
    direction: Literal["asc", "desc"] = "asc"

    @model_validator(mode="after")
    def validate_target(self) -> Self:
        if (self.field is None) == (not self.output_requirement_id):
            raise ValueError("Order requires exactly one field or output requirement")
        return self


class RelationPair(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    left: FieldRef
    right: FieldRef


class BusinessRelationRequirement(RequirementBase):
    clause: Literal["business_relation"] = "business_relation"
    pairs: tuple[RelationPair, ...]
    population: Literal["intersection", "left", "right", "union"]

    @model_validator(mode="after")
    def validate_pairs(self) -> Self:
        if not self.pairs:
            raise ValueError("Business relation requires field pairs")
        return self


SpecificationRequirement = Annotated[
    OutputRequirement
    | PredicateRequirement
    | GroupRequirement
    | TimeWindowRequirement
    | OrderRequirement
    | BusinessRelationRequirement,
    Field(discriminator="clause"),
]
_REQUIREMENT_ADAPTER = TypeAdapter(SpecificationRequirement)


class QueryAssumption(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    assumption_id: str
    business_label: str
    value: str
    reason: str
    risk: Literal["low", "medium", "high"] = "low"
    evidence_refs: tuple[str, ...] = ()


class QuerySpecification(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    version: Literal[3] = 3
    revision: int = Field(ge=1)
    outputs: tuple[OutputRequirement, ...] = ()
    predicates: tuple[PredicateRequirement, ...] = ()
    group_by: tuple[GroupRequirement, ...] = ()
    time_windows: tuple[TimeWindowRequirement, ...] = ()
    order_by: tuple[OrderRequirement, ...] = ()
    limit: int | None = Field(default=None, gt=0)
    business_relations: tuple[BusinessRelationRequirement, ...] = ()
    assumptions: tuple[QueryAssumption, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    confidence: float = Field(default=0.5, ge=0, le=1)

    @property
    def requirements(self) -> tuple[SpecificationRequirement, ...]:
        return (
            *self.outputs,
            *self.predicates,
            *self.group_by,
            *self.time_windows,
            *self.order_by,
            *self.business_relations,
        )

    @property
    def result_mode(self) -> Literal["detail", "aggregate"]:
        return (
            "aggregate"
            if self.group_by or any(o.aggregation != "value" for o in self.outputs)
            else "detail"
        )

    def by_requirement_id(self) -> dict[str, SpecificationRequirement]:
        """Return the canonical requirement lookup used by planning and validation."""
        return {item.requirement_id: item for item in self.requirements}

    @model_validator(mode="after")
    def validate_identity_and_refs(self) -> Self:
        requirements = self.requirements
        ids = [item.requirement_id for item in requirements]
        if not requirements:
            raise ValueError("QuerySpecification must contain requirements")
        if len(ids) != len(set(ids)):
            raise ValueError("QuerySpecification requirement IDs must be unique")
        output_ids = {item.requirement_id for item in self.outputs}
        output_dependencies: dict[str, tuple[str, ...]] = {}
        for output in self.outputs:
            missing = set(output.operand_requirement_ids) - output_ids
            if missing:
                raise ValueError(
                    f"Output {output.requirement_id} has unknown operands: {sorted(missing)}"
                )
            if output.requirement_id in output.operand_requirement_ids:
                raise ValueError(
                    f"Output {output.requirement_id} cannot reference itself"
                )
            output_dependencies[output.requirement_id] = output.operand_requirement_ids
        for order in self.order_by:
            if (
                order.output_requirement_id
                and order.output_requirement_id not in output_ids
            ):
                raise ValueError(
                    f"Order {order.requirement_id} references unknown output"
                )

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(output_id: str) -> None:
            if output_id in visited:
                return
            if output_id in visiting:
                raise ValueError("Derived output dependencies must not contain cycles")
            visiting.add(output_id)
            for dependency in output_dependencies.get(output_id, ()):
                visit(dependency)
            visiting.remove(output_id)
            visited.add(output_id)

        for output_id in output_dependencies:
            visit(output_id)
        return self


def parse_requirement(value: Any) -> SpecificationRequirement:
    return _REQUIREMENT_ADAPTER.validate_python(value)


def canonicalize_planner_requirement_ids(
    raw_specification: Mapping[str, Any],
) -> dict[str, Any]:
    """Replace model-owned temporary IDs before specification validation.

    Planner IDs are only local references inside one response.  The service is
    the identity authority and ``normalize_specification`` assigns durable
    semantic IDs after validation.  This boundary repair accepts harmless
    duplicate, unreferenced model IDs while still rejecting references that
    became genuinely ambiguous because an ID was reused.
    """
    specification = deepcopy(dict(raw_specification))
    buckets = (
        "outputs",
        "predicates",
        "group_by",
        "time_windows",
        "order_by",
        "business_relations",
    )
    replacements: dict[str, list[str]] = {}
    rows: list[dict[str, Any]] = []
    for bucket in buckets:
        raw_rows = specification.get(bucket) or []
        if not isinstance(raw_rows, list | tuple):
            continue
        rewritten: list[Any] = []
        for index, raw in enumerate(raw_rows):
            if not isinstance(raw, Mapping):
                rewritten.append(raw)
                continue
            item = dict(raw)
            old_id = str(item.get("requirement_id") or "")
            temporary_id = f"tmp_{bucket}_{index + 1}"
            item["requirement_id"] = temporary_id
            if old_id:
                replacements.setdefault(old_id, []).append(temporary_id)
            rows.append(item)
            rewritten.append(item)
        specification[bucket] = rewritten

    def resolve(reference: Any) -> str:
        text = str(reference or "")
        candidates = replacements.get(text, [])
        if len(candidates) == 1:
            return candidates[0]
        if len(candidates) > 1:
            raise ValueError(
                f"Planner requirement reference {text!r} is ambiguous because "
                "the temporary ID was reused"
            )
        return text

    for item in rows:
        operands = item.get("operand_requirement_ids")
        if isinstance(operands, list | tuple):
            item["operand_requirement_ids"] = [resolve(value) for value in operands]
        if item.get("output_requirement_id"):
            item["output_requirement_id"] = resolve(item["output_requirement_id"])
    return specification


_FRAGMENT_BUCKETS = {
    "output": "outputs",
    "predicate": "predicates",
    "group": "group_by",
    "time_window": "time_windows",
    "order": "order_by",
    "business_relation": "business_relations",
}
_SEMANTIC_METADATA = {
    "requirement_id",
    "business_label",
    "evidence_refs",
    "confidence",
    "source",
    "status",
    "operand_requirement_ids",
    "output_requirement_id",
}


def parse_specification_fragment(fragment: dict[str, Any]) -> QuerySpecification:
    """Parse a reusable knowledge fragment with full reference validation.

    Capture, certification, fingerprinting and application all use this entry
    point so a fragment cannot be valid in one knowledge stage and malformed in
    another. Reusable fragments intentionally contain requirements only; run
    revision, evidence and physical plans belong to the current conversation.
    """
    if not isinstance(fragment, dict):
        raise ValueError("Specification fragment must be an object")
    version = fragment.get("version", 3)
    if version not in (None, 3):
        raise ValueError("Only QuerySpecification v3 fragments are supported")
    raw_requirements = fragment.get("requirements")
    if not isinstance(raw_requirements, list) or not raw_requirements:
        raise ValueError("Specification fragment requires non-empty requirements")

    buckets: dict[str, list[SpecificationRequirement]] = {
        value: [] for value in _FRAGMENT_BUCKETS.values()
    }
    for index, raw in enumerate(raw_requirements):
        try:
            requirement = parse_requirement(raw)
        except Exception as exc:
            raise ValueError(
                f"Specification fragment requirement[{index}] is invalid: {exc}"
            ) from exc
        buckets[_FRAGMENT_BUCKETS[requirement.clause]].append(requirement)
    return QuerySpecification.model_validate({"revision": 1, **buckets})


def _requirement_semantic_data(
    requirement: SpecificationRequirement,
    *,
    by_id: dict[str, SpecificationRequirement],
    visiting: set[str] | None = None,
) -> dict[str, Any]:
    stack = set(visiting or ())
    if requirement.requirement_id in stack:
        raise ValueError("Requirement references contain a cycle")
    stack.add(requirement.requirement_id)
    data = requirement.model_dump(mode="json", exclude=_SEMANTIC_METADATA)
    if (
        isinstance(requirement, OutputRequirement)
        and requirement.operand_requirement_ids
    ):
        data["operands"] = [
            _requirement_semantic_data(by_id[item], by_id=by_id, visiting=stack)
            for item in requirement.operand_requirement_ids
        ]
    if isinstance(requirement, OrderRequirement) and requirement.output_requirement_id:
        data["output_target"] = _requirement_semantic_data(
            by_id[requirement.output_requirement_id],
            by_id=by_id,
            visiting=stack,
        )
    return data


def specification_semantic_material(
    specification: QuerySpecification,
) -> tuple[dict[str, Any], ...]:
    """Return presentation- and evidence-independent clause semantics."""
    by_id = specification.by_requirement_id()
    material = [
        _requirement_semantic_data(requirement, by_id=by_id)
        for requirement in specification.requirements
    ]
    material.sort(key=lambda item: orjson.dumps(item, option=orjson.OPT_SORT_KEYS))
    return tuple(material)


def requirement_semantic_material(
    requirement: SpecificationRequirement,
    specification: QuerySpecification,
) -> dict[str, Any]:
    """Return canonical semantics for one requirement in its reference graph."""
    return _requirement_semantic_data(
        requirement,
        by_id=specification.by_requirement_id(),
    )


def requirement_target_material(
    requirement: SpecificationRequirement,
    specification: QuerySpecification,
) -> dict[str, Any]:
    """Return the business target used only to detect user overrides."""
    if isinstance(requirement, OutputRequirement):
        return {"clause": requirement.clause, "field": requirement.field.model_dump()}
    if isinstance(requirement, PredicateRequirement):
        return {"clause": requirement.clause, "field": requirement.field.model_dump()}
    if isinstance(requirement, GroupRequirement):
        return {"clause": requirement.clause, "field": requirement.field.model_dump()}
    if isinstance(requirement, TimeWindowRequirement):
        # One query-wide time basis may map to different physical fields. A
        # user-confirmed time window therefore overrides a certified default
        # even when the chosen date field changes.
        return {"clause": requirement.clause}
    if isinstance(requirement, OrderRequirement):
        if requirement.field is not None:
            return {
                "clause": requirement.clause,
                "field": requirement.field.model_dump(),
            }
        assert requirement.output_requirement_id is not None
        target = specification.by_requirement_id()[requirement.output_requirement_id]
        return {
            "clause": requirement.clause,
            "output_target": _requirement_semantic_data(
                target,
                by_id=specification.by_requirement_id(),
            ),
        }
    return {
        "clause": requirement.clause,
        "pairs": sorted(
            (
                pair.left.normalized,
                pair.right.normalized,
            )
            for pair in requirement.pairs
        ),
    }


def normalize_specification(
    specification: QuerySpecification,
) -> QuerySpecification:
    """Assign stable requirement IDs from canonical clause semantics."""
    by_id = specification.by_requirement_id()
    mapping: dict[str, str] = {}
    identities: list[tuple[SpecificationRequirement, str]] = []
    for requirement in specification.requirements:
        material = _requirement_semantic_data(requirement, by_id=by_id)
        encoded = orjson.dumps(material, option=orjson.OPT_SORT_KEYS)
        base_id = "req_" + hashlib.sha256(encoded).hexdigest()[:16]
        identities.append((requirement, base_id))

    semantic_counts: dict[str, int] = {}
    for _requirement, base_id in identities:
        semantic_counts[base_id] = semantic_counts.get(base_id, 0) + 1
    discriminators: dict[str, int] = {}
    for requirement, base_id in identities:
        if semantic_counts[base_id] == 1:
            mapping[requirement.requirement_id] = base_id
            continue
        # Two requested business metrics may intentionally share the same
        # physical expression. Distinguish them by their stable business role,
        # without changing IDs for the normal one-clause case.
        role = orjson.dumps(
            {
                "clause": requirement.clause,
                "business_label": requirement.business_label,
            },
            option=orjson.OPT_SORT_KEYS,
        )
        discriminator = hashlib.sha256(role).hexdigest()[:8]
        candidate = f"{base_id}_{discriminator}"
        occurrence = discriminators.get(candidate, 0) + 1
        discriminators[candidate] = occurrence
        mapping[requirement.requirement_id] = (
            candidate if occurrence == 1 else f"{candidate}_{occurrence}"
        )

    updates: dict[str, Any] = {"revision": specification.revision}
    for bucket in _FRAGMENT_BUCKETS.values():
        rewritten: list[dict[str, Any]] = []
        for requirement in getattr(specification, bucket):
            data = requirement.model_dump(mode="python")
            data["requirement_id"] = mapping[requirement.requirement_id]
            if any(is_user_evidence_ref(ref) for ref in requirement.evidence_refs):
                data["source"] = "user"
            if "operand_requirement_ids" in data:
                data["operand_requirement_ids"] = tuple(
                    mapping.get(item, item) for item in data["operand_requirement_ids"]
                )
            if data.get("output_requirement_id"):
                data["output_requirement_id"] = mapping.get(
                    data["output_requirement_id"], data["output_requirement_id"]
                )
            rewritten.append(data)
        updates[bucket] = tuple(rewritten)
    return QuerySpecification.model_validate(
        {**specification.model_dump(mode="python"), **updates}
    )


def requirement_fields(requirement: SpecificationRequirement) -> tuple[FieldRef, ...]:
    if isinstance(requirement, TimeWindowRequirement):
        return requirement.fields
    if isinstance(requirement, BusinessRelationRequirement):
        return tuple(
            field for pair in requirement.pairs for field in (pair.left, pair.right)
        )
    field = getattr(requirement, "field", None)
    return (field,) if isinstance(field, FieldRef) else ()
