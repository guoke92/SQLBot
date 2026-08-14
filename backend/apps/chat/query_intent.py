"""Compact business intent for query planning.

``QueryIntent`` deliberately describes what the user wants, not how a
datasource should implement it.  Physical tables, joins, expressions,
permissions and execution caps belong to a plan candidate.  Model responses
never own durable IDs; the service derives stable item keys after validation.
"""

from __future__ import annotations

import hashlib
from typing import Any, Literal, Self

import orjson
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class IntentOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    business_name: str
    semantic_definition: str
    role: Literal["measure", "attribute"]
    aggregation: (
        Literal[
            "value",
            "count",
            "count_distinct",
            "sum",
            "avg",
            "min",
            "max",
            "ratio",
            "difference",
            "distinct_concat",
        ]
        | None
    ) = None

    @field_validator("business_name", "semantic_definition")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        value = " ".join(value.split()).strip()
        if not value:
            raise ValueError("Intent output text cannot be empty")
        return value

    @model_validator(mode="after")
    def validate_role(self) -> Self:
        if self.role == "attribute" and self.aggregation not in {None, "value"}:
            raise ValueError("Intent attributes cannot declare an aggregation")
        if self.role == "measure" and self.aggregation in {None, "value"}:
            raise ValueError("Intent measures require an aggregation")
        return self


class IntentGrouping(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    business_name: str
    grain: Literal["day", "week", "month", "quarter", "year"] | None = None

    @field_validator("business_name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = " ".join(value.split()).strip()
        if not value:
            raise ValueError("Intent grouping name cannot be empty")
        return value


class IntentFilter(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    business_name: str
    operator: Literal[
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
    values: tuple[Any, ...] = ()

    @field_validator("business_name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = " ".join(value.split()).strip()
        if not value:
            raise ValueError("Intent filter name cannot be empty")
        return value

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


class IntentTime(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    original_expression: str = ""
    start: str | None = None
    end_exclusive: str | None = None
    grain: Literal["day", "week", "month", "quarter", "year"] | None = None
    basis_concept: str

    @field_validator("original_expression", "basis_concept")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        return " ".join(value.split()).strip()

    @model_validator(mode="after")
    def validate_range(self) -> Self:
        if not self.basis_concept:
            raise ValueError("Intent time requires a business basis")
        if bool(self.start) != bool(self.end_exclusive):
            raise ValueError("Intent time requires both range boundaries")
        return self


class IntentOrder(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    business_name: str
    direction: Literal["asc", "desc"] = "asc"

    @field_validator("business_name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = " ".join(value.split()).strip()
        if not value:
            raise ValueError("Intent order name cannot be empty")
        return value


class IntentAssumption(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    business_name: str
    value: str
    reason: str
    risk: Literal["low", "medium", "high"] = "low"

    @field_validator("business_name", "value", "reason")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        value = " ".join(value.split()).strip()
        if not value:
            raise ValueError("Intent assumption text cannot be empty")
        return value


class IntentDataset(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    purpose: str
    required: bool = True
    mode: Literal["detail", "aggregate"]
    subject: str
    outputs: tuple[IntentOutput, ...] = Field(min_length=1)
    groupings: tuple[IntentGrouping, ...] = ()
    filters: tuple[IntentFilter, ...] = ()
    time: IntentTime | None = None
    population: str = ""
    ordering: tuple[IntentOrder, ...] = ()
    user_limit: int | None = Field(default=None, gt=0)

    @field_validator("purpose", "subject", "population")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        return " ".join(value.split()).strip()

    @model_validator(mode="after")
    def validate_mode(self) -> Self:
        if not self.purpose or not self.subject:
            raise ValueError("Intent dataset requires purpose and subject")
        has_measure = any(item.role == "measure" for item in self.outputs)
        if self.mode == "aggregate" and not has_measure:
            raise ValueError("Aggregate intent requires at least one measure")
        if self.mode == "detail" and (has_measure or self.groupings):
            raise ValueError("Detail intent cannot contain measures or groupings")
        return self


class QueryIntent(BaseModel):
    """The only structured business semantic truth for a verified query."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    version: Literal[1] = 1
    purpose: str
    datasets: tuple[IntentDataset, ...] = Field(min_length=1, max_length=4)
    assumptions: tuple[IntentAssumption, ...] = ()
    confidence: float = Field(default=0.5, ge=0, le=1)

    @field_validator("purpose")
    @classmethod
    def normalize_purpose(cls, value: str) -> str:
        value = " ".join(value.split()).strip()
        if not value:
            raise ValueError("Query intent purpose cannot be empty")
        return value

    @model_validator(mode="after")
    def validate_datasets(self) -> Self:
        identities = [
            semantic_digest(item.model_dump(mode="json")) for item in self.datasets
        ]
        if len(identities) != len(set(identities)):
            raise ValueError("Query intent datasets must be semantically unique")
        return self


class IntentRevision(BaseModel):
    """Service-owned immutable revision envelope around model business intent."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    revision: int = Field(gt=0)
    status: Literal["draft", "proposed", "accepted", "superseded"]
    intent: QueryIntent
    item_catalog: dict[str, dict[str, Any]]
    evidence_map: dict[str, tuple[str, ...]] = Field(default_factory=dict)
    unresolved_ambiguities: tuple[str, ...] = ()
    content_hash: str
    execution_mode: Literal["verified", "unverified"] = "verified"


def build_intent_revision(
    intent: QueryIntent,
    *,
    revision: int,
    status: Literal["draft", "proposed", "accepted", "superseded"],
    evidence_map: dict[str, tuple[str, ...]] | None = None,
    unresolved_ambiguities: tuple[str, ...] = (),
) -> IntentRevision:
    """Assign stable item references without letting the model own IDs."""
    if not isinstance(intent, QueryIntent):
        raise TypeError("Intent revisions can only be built from QueryIntent")
    return IntentRevision(
        revision=revision,
        status=status,
        intent=intent,
        item_catalog=intent_item_catalog(intent),
        evidence_map=evidence_map or {},
        unresolved_ambiguities=unresolved_ambiguities,
        content_hash=query_intent_hash(intent),
    )


def semantic_digest(value: Any) -> str:
    payload = orjson.dumps(value, option=orjson.OPT_SORT_KEYS, default=str)
    return hashlib.sha256(payload).hexdigest()


def intent_item_key(dataset_index: int, kind: str, index: int, value: Any) -> str:
    """Create a service-owned stable key; models never emit durable IDs."""
    digest = semantic_digest(value)[:16]
    return f"d{dataset_index}:{kind}:{index}:{digest}"


def intent_item_catalog(intent: QueryIntent) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for dataset_index, dataset in enumerate(intent.datasets):
        result[intent_item_key(dataset_index, "subject", 0, dataset.subject)] = {
            "business_name": dataset.subject
        }
        if dataset.population:
            result[
                intent_item_key(dataset_index, "population", 0, dataset.population)
            ] = {"business_name": dataset.population}
        for kind, items in (
            ("output", dataset.outputs),
            ("group", dataset.groupings),
            ("filter", dataset.filters),
            ("order", dataset.ordering),
        ):
            for index, item in enumerate(items):
                item_value = item.model_dump(mode="json")
                result[intent_item_key(dataset_index, kind, index, item_value)] = (
                    item_value
                )
        if dataset.time is not None:
            time_value = dataset.time.model_dump(mode="json")
            result[intent_item_key(dataset_index, "time", 0, time_value)] = time_value
    return result


def query_intent_hash(intent: QueryIntent) -> str:
    return semantic_digest(intent.model_dump(mode="json"))


def calculate_intent_confidence(
    intent: QueryIntent,
    evidence_map: dict[str, tuple[str, ...]],
) -> float:
    """Derive intent confidence from provenance, never from model self-rating."""
    catalog = intent_item_catalog(intent)
    if not catalog:
        return 0.0
    scores: list[float] = []
    for item_key in catalog:
        refs = tuple(evidence_map.get(item_key) or ())
        if any(ref.startswith("user:answer:") for ref in refs):
            scores.append(1.0)
        elif any(ref.startswith("user:question:") for ref in refs):
            scores.append(0.9)
        elif any(ref.startswith("history:confirmed:") for ref in refs):
            scores.append(0.8)
        elif any(ref.startswith("knowledge:certified:") for ref in refs):
            scores.append(0.75)
        elif refs:
            scores.append(0.6)
        else:
            scores.append(0.45)
    risk_penalty = sum(
        {"low": 0.02, "medium": 0.06, "high": 0.14}[item.risk]
        for item in intent.assumptions
    )
    return round(max(0.0, min(1.0, sum(scores) / len(scores) - risk_penalty)), 4)


def resolve_intent_item_key(
    intent: QueryIntent, *, dataset_index: int, kind: str, item_index: int
) -> str:
    """Resolve a model-local semantic path to a service-owned stable key."""
    prefix = f"d{dataset_index}:{kind}:{item_index}:"
    matches = [key for key in intent_item_catalog(intent) if key.startswith(prefix)]
    if len(matches) != 1:
        raise ValueError(
            f"Unknown intent item path dataset={dataset_index} kind={kind} index={item_index}"
        )
    return matches[0]
