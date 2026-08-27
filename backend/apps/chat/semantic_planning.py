"""Planning decisions and the single clarification card contract.

The model names business questions and options. Service-owned IDs, resume
answers and the interrupt payload all use this same shape. LLM extras and
historical aliases are coerced once, then discarded.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping, Sequence
from typing import Any, Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter,
    ValidationError,
    model_validator,
)

MAX_CLARIFICATION_QUESTIONS = 4


def stable_id(prefix: str, *parts: str) -> str:
    body = "\x1f".join(part.strip().casefold() for part in parts if part)
    return f"{prefix}_{hashlib.sha256(body.encode()).hexdigest()[:16]}"


def _text(*values: Any) -> str:
    for value in values:
        text = " ".join(str(value or "").split())
        if text:
            return text
    return ""


def _option_meaning(option: dict[str, Any]) -> str:
    resolution = option.get("resolution")
    if isinstance(resolution, dict):
        return _text(
            option.get("meaning"),
            resolution.get("business_meaning"),
            option.get("label"),
            option.get("description"),
        )
    if isinstance(resolution, str):
        return _text(option.get("meaning"), resolution, option.get("label"))
    return _text(option.get("meaning"), option.get("label"), option.get("description"))


def _coerce_field_ref(item: Any) -> dict[str, Any] | None:
    if isinstance(item, str):
        name = _text(item)
        return {"name": name, "comment": "", "table": ""} if name else None
    payload = _as_dict(item)
    if payload is None:
        return None
    name = _text(payload.get("name"), payload.get("field"), payload.get("field_name"))
    if not name:
        return None
    return {
        "name": name,
        "comment": _text(payload.get("comment"), payload.get("field_comment")),
        "table": _text(payload.get("table"), payload.get("table_name")),
    }


def _coerce_option(option: dict[str, Any], *, recommended: bool) -> dict[str, Any]:
    meaning = _option_meaning(option)
    label = _text(option.get("label"))
    if not label or label.casefold() in {"a", "b", "c"}:
        label = meaning
    fields: list[dict[str, Any]] = []
    raw_fields = option.get("fields")
    if isinstance(raw_fields, list):
        for item in raw_fields:
            ref = _coerce_field_ref(item)
            if ref is not None:
                fields.append(ref)
    field = _text(option.get("field"), option.get("field_name"))
    field_comment = _text(
        option.get("field_comment"),
        option.get("comment"),
        option.get("field_label"),
    )
    table = _text(option.get("table"), option.get("table_name"))
    if not fields and field:
        fields = [{"name": field, "comment": field_comment, "table": table}]
    first = fields[0] if fields else {"name": "", "comment": "", "table": ""}
    return {
        "option_id": _text(option.get("option_id")),
        "label": label,
        "meaning": meaning,
        "field": first["name"],
        "field_comment": first["comment"],
        "table": first["table"] or table,
        "fields": fields,
        "recommended": bool(option.get("recommended")) or recommended,
    }


def _coerce_question(item: dict[str, Any]) -> dict[str, Any]:
    raw_options = item.get("options")
    if not isinstance(raw_options, list):
        raw_options = item.get("candidate_resolutions")
    recommended_id = _text(item.get("recommended_candidate_id"))
    options: list[dict[str, Any]] = []
    if isinstance(raw_options, list):
        for option in raw_options:
            if not isinstance(option, dict):
                continue
            supplied_id = _text(option.get("option_id"))
            options.append(
                _coerce_option(
                    option,
                    recommended=bool(recommended_id) and supplied_id == recommended_id,
                )
            )
    return {
        "question_id": _text(item.get("question_id") or item.get("ambiguity_id")),
        "question": _text(item.get("question"), item.get("business_question")),
        "why": _text(item.get("why"), item.get("reason")),
        "options": options,
    }


def _as_dict(item: Any) -> dict[str, Any] | None:
    if isinstance(item, dict):
        return item
    dump = getattr(item, "model_dump", None)
    if callable(dump):
        payload = dump(mode="python")
        if isinstance(payload, dict):
            return payload
    return None


def coerce_clarification_questions(value: Any) -> list[dict[str, Any]]:
    """Lift historical/LLM aliases onto canonical ``questions``."""
    if isinstance(value, list):
        items = value
    elif isinstance(value, dict):
        items = value.get("questions")
        if not isinstance(items, list):
            nested = value.get("ambiguity_set")
            nested_dict = nested if isinstance(nested, dict) else {}
            items = (
                nested_dict.get("questions")
                or nested_dict.get("ambiguities")
                or value.get("ambiguities")
            )
    else:
        items = None
    if not isinstance(items, list):
        return []
    questions: list[dict[str, Any]] = []
    for item in items:
        payload = _as_dict(item)
        if payload is not None:
            questions.append(_coerce_question(payload))
    return questions


def unsigned_clarification_questions(
    questions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Drop model-invented IDs so the service can mint stable ones."""
    unsigned: list[dict[str, Any]] = []
    for item in questions:
        options = []
        for option in item.get("options") or []:
            options.append({**option, "option_id": ""})
        unsigned.append({**item, "question_id": "", "options": options})
    return unsigned


class ClarificationFieldRef(BaseModel):
    """One schema field cited by a clarification option.

    Composite caliber (e.g. signed amount by sign_date and financed amount by
    apply_date) uses several refs on the same option.
    """

    model_config = ConfigDict(extra="ignore")
    name: str = ""
    comment: str = ""
    table: str = ""

    @model_validator(mode="after")
    def normalize(self) -> Self:
        self.name = _text(self.name)
        self.comment = _text(self.comment)
        self.table = _text(self.table)
        if not self.name:
            raise ValueError("Clarification field requires a name")
        return self


class ClarificationOption(BaseModel):
    model_config = ConfigDict(extra="ignore")
    option_id: str = ""
    label: str = ""
    meaning: str = ""
    field: str = ""
    field_comment: str = ""
    table: str = ""
    fields: list[ClarificationFieldRef] = Field(default_factory=list)
    recommended: bool = False

    @model_validator(mode="after")
    def validate_option(self) -> Self:
        self.meaning = _text(self.meaning, self.label)
        self.label = _text(self.label) or self.meaning
        self.field = _text(self.field)
        self.field_comment = _text(self.field_comment)
        self.table = _text(self.table)
        if not self.fields and self.field:
            self.fields = [
                ClarificationFieldRef(
                    name=self.field, comment=self.field_comment, table=self.table
                )
            ]
        if self.fields:
            first = self.fields[0]
            self.field = first.name
            self.field_comment = first.comment
            self.table = first.table
        if self.label.casefold() in {"a", "b", "c"} and self.meaning:
            self.label = self.meaning
        if not self.meaning:
            raise ValueError("Clarification option requires a business meaning")
        return self


class ClarificationQuestion(BaseModel):
    model_config = ConfigDict(extra="ignore")
    question_id: str = ""
    question: str
    why: str = ""
    options: list[ClarificationOption] = Field(min_length=2, max_length=3)

    @model_validator(mode="after")
    def assign_ids(self) -> Self:
        self.question = _text(self.question)
        self.why = _text(self.why)
        if not self.question:
            raise ValueError("Clarification question is required")
        meanings = sorted(option.meaning for option in self.options)
        if not self.question_id:
            self.question_id = stable_id("q", *meanings)
        for option in self.options:
            if not option.option_id:
                option.option_id = stable_id("opt", self.question_id, option.meaning)
        ids = [option.option_id for option in self.options]
        if len(ids) != len(set(ids)):
            raise ValueError("Clarification option meanings must be unique")
        if sum(1 for option in self.options if option.recommended) > 1:
            raise ValueError("At most one option may be recommended")
        return self


class ClarificationCard(BaseModel):
    """Canonical interrupt payload and planner clarify body."""

    model_config = ConfigDict(extra="ignore")
    questions: list[ClarificationQuestion] = Field(
        min_length=1, max_length=MAX_CLARIFICATION_QUESTIONS
    )

    @model_validator(mode="before")
    @classmethod
    def coerce_payload(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value
        return {"questions": coerce_clarification_questions(value)}


def public_interrupt_payload(payload: dict[str, Any] | None) -> dict[str, Any]:
    """Serialize a stored interrupt body into the canonical card."""
    try:
        return ClarificationCard.model_validate(payload or {}).model_dump(mode="json")
    except ValidationError:
        return {"questions": []}


def public_resume_answers(answers: list[Any] | None) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for item in answers or []:
        if not isinstance(item, dict):
            continue
        row = dict(item)
        question_id = _text(row.get("question_id"), row.get("ambiguity_id"))
        if question_id:
            row["question_id"] = question_id
        row.pop("ambiguity_id", None)
        result.append(row)
    return result


def question_id_of(value: dict[str, Any] | None) -> str:
    payload = value or {}
    return _text(payload.get("question_id"), payload.get("ambiguity_id"))


def enforce_clarification_policy(
    card: ClarificationCard,
    *,
    resolved_question_ids: set[str] | None = None,
) -> ClarificationCard:
    """Accept only unresolved questions that change the business result.

    Emitting a question is itself the blocking signal. Skip/assume flags are
    not part of the contract; low-impact uncertainty belongs in the query
    description, not on this card.
    """
    resolved = {item.strip() for item in resolved_question_ids or set() if item.strip()}
    identities = [item.question_id for item in card.questions]
    if len(identities) != len(set(identities)):
        raise ValueError("Clarification questions must be semantically unique")
    repeated = set(identities) & resolved
    if repeated:
        raise ValueError(
            "Planner repeated resolved questions: " + ", ".join(sorted(repeated))
        )
    return card


def _rule_constrained_fields(rule: Mapping[str, Any]) -> set[str]:
    names: set[str] = set()
    for target in rule.get("field_targets") or []:
        if not isinstance(target, dict):
            continue
        field = str(target.get("field") or "").strip()
        if field:
            names.add(field.casefold())
    for text in (rule.get("content"), rule.get("query_impact")):
        hay = str(text or "")
        names.update(
            match.group(0).casefold()
            for match in re.finditer(r"[A-Za-z_][A-Za-z0-9_]*", hay)
            if "_" in match.group(0)
        )
    return names


def constrain_clarification_by_rules(
    card: ClarificationCard,
    rules: Sequence[Mapping[str, Any]] | None,
) -> ClarificationCard:
    """Drop recommended when an option field is named by a published rule."""
    forbidden: set[str] = set()
    for rule in rules or []:
        if isinstance(rule, Mapping):
            forbidden.update(_rule_constrained_fields(rule))
    if not forbidden:
        return card
    questions: list[ClarificationQuestion] = []
    changed = False
    for question in card.questions:
        options: list[ClarificationOption] = []
        for option in question.options:
            field_names = {
                ref.name.casefold() for ref in option.fields if ref.name
            }
            if option.field:
                field_names.add(option.field.casefold())
            if option.recommended and field_names & forbidden:
                options.append(option.model_copy(update={"recommended": False}))
                changed = True
            else:
                options.append(option)
        questions.append(question.model_copy(update={"options": options}))
    return card.model_copy(update={"questions": questions}) if changed else card


class QueryDescription(BaseModel):
    model_config = ConfigDict(extra="ignore")
    description: str = ""
    sql: str | None = None
    request: dict[str, Any] | None = None

    @model_validator(mode="after")
    def validate_payload(self) -> Self:
        self.description = " ".join(self.description.split()).strip()
        if bool(self.sql and self.sql.strip()) == bool(self.request):
            raise ValueError("Each query requires exactly one SQL or REST request")
        if self.sql is not None:
            self.sql = self.sql.strip()
        return self


class NeedClarification(BaseModel):
    model_config = ConfigDict(extra="ignore")
    decision: Literal["clarify"] = "clarify"
    questions: list[ClarificationQuestion] = Field(
        min_length=1, max_length=MAX_CLARIFICATION_QUESTIONS
    )
    missing_concepts: list[str] = Field(default_factory=list, max_length=8)

    @model_validator(mode="before")
    @classmethod
    def coerce_payload(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value
        return {
            "decision": value.get("decision") or "clarify",
            "questions": unsigned_clarification_questions(
                coerce_clarification_questions(value)
            ),
            "missing_concepts": value.get("missing_concepts") or [],
        }

    def as_card(self) -> ClarificationCard:
        return ClarificationCard(questions=self.questions)


class Ready(BaseModel):
    model_config = ConfigDict(extra="ignore")
    decision: Literal["ready"] = "ready"
    queries: list[QueryDescription] = Field(min_length=1)


class QueryUnsupported(BaseModel):
    """A query-shaped turn that cannot be answered by the selected context."""

    model_config = ConfigDict(extra="ignore")
    decision: Literal["unsupported"] = "unsupported"
    message: str
    reason_code: str = "QUERY_NOT_SUPPORTED"
    # Concepts the planner claims are missing (e.g. "组织/部门表"). The plan
    # gate verifies each against the catalog map / value index before the
    # terminal negative is allowed to stand; empty on a first attempt is a
    # protocol gap and bounces once.
    missing_concepts: list[str] = Field(default_factory=list, max_length=8)

    @model_validator(mode="after")
    def validate_message(self) -> Self:
        self.message = " ".join(self.message.split()).strip()
        self.reason_code = self.reason_code.strip().upper() or "QUERY_NOT_SUPPORTED"
        if not self.message:
            raise ValueError(
                "Unsupported query decision requires a user-facing message"
            )
        return self


PlanningDecision = NeedClarification | Ready | QueryUnsupported
PLANNING_DECISION_ADAPTER = TypeAdapter(PlanningDecision)
