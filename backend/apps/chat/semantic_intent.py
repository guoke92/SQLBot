"""Structured semantic intent and clarification contracts for NLQ.

The intent contract describes *what* the user has confirmed.  It deliberately
does not contain SQL syntax or execute datasource work.  Graph nodes and HTTP
adapters share these models so one persisted payload drives streaming, history
rendering and the next clarification turn.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Literal, Self

from pydantic import BaseModel, Field, field_validator, model_validator

IntentStatus = Literal[
    "evaluating",
    "needs_clarification",
    "ready",
    "blocked",
]
IntentKind = Literal[
    "datasource",
    "entity",
    "scope",
    "metric",
    "dimension",
    "time",
    "filter",
    "relation",
    "grain",
    "calculation",
]
SelectionType = Literal["single", "multiple", "text"]
RecommendationStrength = Literal["strong", "moderate", "weak"]
Aggregation = Literal[
    "none",
    "count",
    "count_distinct",
    "sum",
    "avg",
    "min",
    "max",
    "distinct_concat",
]
IntentEffect = Literal["include", "omit"]
BindingRole = Literal["group", "measure", "attribute", "filter", "join"]
IntentMode = Literal["new", "refine"]


class IntentBinding(BaseModel):
    """One physical field's executable role in a confirmed business decision."""

    identifier: str
    role: BindingRole
    aggregation: Aggregation = "none"

    @field_validator("identifier")
    @classmethod
    def normalize_identifier(cls, value: str) -> str:
        identifier = value.strip()
        if not identifier:
            raise ValueError("Binding identifier cannot be empty")
        return identifier

    @model_validator(mode="after")
    def validate_role_aggregation(self) -> Self:
        if self.role == "measure" and self.aggregation == "none":
            raise ValueError(
                f"Measure binding {self.identifier} requires an aggregation"
            )
        if self.role in {"group", "filter", "join"} and self.aggregation != "none":
            raise ValueError(
                f"{self.role.title()} binding {self.identifier} cannot aggregate"
            )
        return self


class IntentResolution(BaseModel):
    """One option's concrete answer for one semantic contract slot."""

    label: str = ""
    value: Any
    bindings: list[IntentBinding] = Field(default_factory=list)
    effect: IntentEffect = "include"


class IntentOption(BaseModel):
    id: str
    label: str
    description: str = ""
    impact: str = ""
    evidence_refs: list[str] = Field(default_factory=list)
    resolutions: dict[str, IntentResolution] = Field(default_factory=dict)


class IntentIssue(BaseModel):
    key: str
    kind: IntentKind
    reason: str
    evidence_refs: list[str] = Field(default_factory=list)


class IntentDecision(BaseModel):
    key: str
    kind: IntentKind
    label: str
    value: Any
    source: Literal["user", "rule", "terminology", "schema", "inference"] = "user"
    evidence_refs: list[str] = Field(default_factory=list)
    bindings: list[IntentBinding] = Field(default_factory=list)
    effect: IntentEffect = "include"
    locked: bool = True
    # Set only by deterministic dictionary/entity-binding questions. Generic
    # semantic decisions (including field mappings) must never become filters.
    binding_phrase: str = ""


class ClarificationQuestion(BaseModel):
    id: str
    issue_keys: list[str] = Field(default_factory=list)
    kind: IntentKind
    title: str
    reason: str = ""
    selection_type: SelectionType = "single"
    required: bool = True
    recommended_option_ids: list[str] = Field(default_factory=list)
    recommendation_reason: str = ""
    recommendation_strength: RecommendationStrength = "weak"
    options: list[IntentOption] = Field(default_factory=list)
    allow_custom: bool = True
    custom_placeholder: str = ""
    # Internal provenance for deterministic entity-value clarification.
    # It is intentionally absent from the LLM response contract.
    binding_phrase: str = ""


class ClarificationAnswer(BaseModel):
    question_id: str
    option_ids: list[str] = Field(default_factory=list)
    custom_text: str = ""

    @model_validator(mode="after")
    def validate_answer_mode(self) -> Self:
        if self.option_ids and self.custom_text.strip():
            raise ValueError(
                "Clarification answer must use either option_ids or custom_text"
            )
        return self


class IntentContext(BaseModel):
    version: int = 1
    status: IntentStatus = "evaluating"
    original_question: str
    summary: str = ""
    decisions: list[IntentDecision] = Field(default_factory=list)
    issues: list[IntentIssue] = Field(default_factory=list)
    questions: list[ClarificationQuestion] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    time_intent: dict[str, Any] = Field(default_factory=dict)
    submitted_answers: list[ClarificationAnswer] = Field(default_factory=list)
    base_record_id: int | None = None
    base_decisions: list[IntentDecision] = Field(default_factory=list)
    base_time_intent: dict[str, Any] = Field(default_factory=dict)

    @property
    def awaiting_input(self) -> bool:
        return self.status == "needs_clarification"


def new_intent_context(
    question: str,
    *,
    base_record_id: int | None = None,
    base_decisions: Sequence[IntentDecision] = (),
    base_time_intent: Mapping[str, Any] | None = None,
) -> IntentContext:
    return IntentContext(
        original_question=(question or "").strip(),
        base_record_id=base_record_id,
        base_decisions=list(base_decisions),
        base_time_intent=dict(base_time_intent or {}),
    )


def decision_selected_values(value: Any) -> list[str]:
    """Return selected labels/custom text from the canonical decision value."""
    if not isinstance(value, Mapping):
        rendered = str(value or "").strip()
        return [rendered] if rendered else []

    values = [
        str(option.get("label") or "").strip()
        for option in value.get("selected_options") or []
        if isinstance(option, Mapping) and str(option.get("label") or "").strip()
    ]
    custom = str(value.get("custom_text") or "").strip()
    if custom:
        values.append(custom)
    return list(dict.fromkeys(values))


def binding_identifiers(bindings: Sequence[Any]) -> list[str]:
    """Return stable physical identifiers from structured intent bindings."""
    values: list[str] = []
    for binding in bindings:
        raw = (
            binding.get("identifier")
            if isinstance(binding, Mapping)
            else getattr(binding, "identifier", "")
        )
        identifier = str(raw or "").strip()
        if identifier:
            values.append(identifier)
    return list(dict.fromkeys(values))


def validate_binding_requirements(
    *,
    kind: str,
    effect: str,
    bindings: Sequence[Any],
    binding_phrase: str = "",
    context: str = "Decision",
) -> None:
    """Validate decision completeness once, independently of its source adapter."""
    if effect == "omit":
        return
    signatures: dict[str, tuple[str, str]] = {}
    for binding in bindings:
        identifier = str(
            binding.get("identifier")
            if isinstance(binding, Mapping)
            else getattr(binding, "identifier", "")
        ).strip()
        role = str(
            binding.get("role")
            if isinstance(binding, Mapping)
            else getattr(binding, "role", "")
        ).strip()
        aggregation = str(
            binding.get("aggregation", "none")
            if isinstance(binding, Mapping)
            else getattr(binding, "aggregation", "none")
        ).strip()
        signature = (role, aggregation)
        existing = signatures.get(identifier)
        if identifier and existing is not None and existing != signature:
            raise ValueError(f"{context} has conflicting bindings for {identifier}")
        if identifier:
            signatures[identifier] = signature
    roles = {
        str(
            binding.get("role")
            if isinstance(binding, Mapping)
            else getattr(binding, "role", "")
        ).strip()
        for binding in bindings
    }
    if kind in {"metric", "calculation"} and "measure" not in roles:
        raise ValueError(f"{context} requires a measure binding")
    if kind in {"dimension", "grain"} and not roles.intersection(
        {"group", "attribute"}
    ):
        raise ValueError(f"{context} requires a group or attribute binding")
    if kind == "entity" and binding_phrase and "filter" not in roles:
        raise ValueError(f"{context} requires a filter binding")


def binding_contract_labels(bindings: Sequence[Any]) -> list[str]:
    """Render physical bindings with the SQL role the planner must implement."""
    values: list[str] = []
    for binding in bindings:
        if isinstance(binding, Mapping):
            identifier = str(binding.get("identifier") or "").strip()
            role = str(binding.get("role") or "").strip()
            aggregation = str(binding.get("aggregation") or "none").strip()
        else:
            identifier = str(getattr(binding, "identifier", "") or "").strip()
            role = str(getattr(binding, "role", "") or "").strip()
            aggregation = str(
                getattr(binding, "aggregation", "none") or "none"
            ).strip()
        if not identifier or not role:
            continue
        operation = f"，聚合={aggregation}" if aggregation != "none" else ""
        values.append(f"`{identifier}`（角色={role}{operation}）")
    return list(dict.fromkeys(values))


def time_contract_incomplete(
    decisions: Sequence[IntentDecision],
    time_intent: Mapping[str, Any],
) -> bool:
    """Return whether a confirmed business-time filter lacks a time scope."""
    has_time_filter = any(
        decision.effect == "include"
        and decision.kind == "time"
        and any(binding.role == "filter" for binding in decision.bindings)
        for decision in decisions
    )
    if not has_time_filter:
        return False
    scope = str(time_intent.get("scope") or "").strip()
    if scope == "all":
        return False
    if scope == "explicit":
        return not (
            str(time_intent.get("start") or "").strip()
            and str(time_intent.get("end_exclusive") or "").strip()
        )
    if scope in {"rolling", "default"}:
        lookback_months = time_intent.get("lookback_months")
        return not (
            str(time_intent.get("anchor") or "").strip()
            and isinstance(lookback_months, int)
            and not isinstance(lookback_months, bool)
            and lookback_months > 0
        )
    return True


def render_decision_value(value: Any) -> str:
    """Render one confirmed decision consistently for recall and SQL planning."""
    if not isinstance(value, Mapping):
        return str(value or "").strip()

    parts: list[str] = []
    for option in value.get("selected_options") or []:
        if not isinstance(option, Mapping):
            continue
        label = str(option.get("label") or "").strip()
        if not label:
            continue
        resolution = str(option.get("resolution") or "").strip()
        description = str(option.get("description") or "").strip()
        impact = str(option.get("impact") or "").strip()
        detail = "；".join(
            item
            for item in (
                f"具体口径：{resolution}" if resolution else "",
                description,
                impact,
            )
            if item
        )
        parts.append(f"{label}（{detail}）" if detail else label)
    custom = str(value.get("custom_text") or "").strip()
    if custom:
        parts.append(custom)
    return "、".join(parts)


def decision_contract_rows(
    decisions: Sequence[Any],
) -> list[tuple[str, str, list[str]]]:
    """Render the resolved contract once while retaining SQL requirements."""
    rows: list[tuple[str, str, list[str]]] = []
    seen: set[tuple[str, str, tuple[str, ...]]] = set()
    for decision in decisions:
        if isinstance(decision, Mapping):
            if not decision.get("locked"):
                continue
            label = str(decision.get("label") or decision.get("key") or "").strip()
            value = decision.get("value")
            requirements = binding_contract_labels(decision.get("bindings") or [])
        else:
            if not getattr(decision, "locked", False):
                continue
            label = str(
                getattr(decision, "label", "") or getattr(decision, "key", "")
            ).strip()
            value = getattr(decision, "value", None)
            requirements = binding_contract_labels(
                getattr(decision, "bindings", []) or []
            )
        rendered = render_decision_value(value)
        signature = (label, rendered, tuple(requirements))
        if not rendered or signature in seen:
            continue
        seen.add(signature)
        rows.append((label, rendered, requirements))
    return rows


def decision_display_rows(
    decisions: Sequence[Any],
) -> list[tuple[str, str]]:
    """Render semantically identical decisions for user-facing summaries."""
    return [
        (label, rendered)
        for label, rendered, _identifiers in decision_contract_rows(decisions)
    ]


def merge_clarification_answers(
    context: IntentContext,
    answers: list[ClarificationAnswer],
) -> IntentContext:
    """Validate one submitted form and merge its semantic decisions.

    Structured options are executable resolutions and can be locked
    deterministically. Free-form answers are provisional evidence until the
    semantic assessor maps them to a concrete contract decision.
    """
    question_by_id = {question.id: question for question in context.questions}
    issue_kind_by_key = {issue.key: issue.kind for issue in context.issues}
    answer_by_id: dict[str, ClarificationAnswer] = {}
    for answer in answers:
        if answer.question_id in answer_by_id:
            raise ValueError(f"Duplicate clarification answer: {answer.question_id}")
        if answer.question_id not in question_by_id:
            raise ValueError(f"Unknown clarification question: {answer.question_id}")
        answer_by_id[answer.question_id] = answer

    missing = [
        question.id
        for question in context.questions
        if question.required and question.id not in answer_by_id
    ]
    if missing:
        raise ValueError("Missing clarification answer(s): " + ", ".join(missing))

    decisions_by_key = {decision.key: decision for decision in context.decisions}
    answered_issue_keys: set[str] = set()
    has_custom_answer = False
    for question in context.questions:
        answer = answer_by_id.get(question.id)
        if answer is None:
            continue
        options_by_id = {option.id: option for option in question.options}
        unknown = [
            option_id
            for option_id in answer.option_ids
            if option_id not in options_by_id
        ]
        if unknown:
            raise ValueError(
                f"Unknown option(s) for {question.id}: " + ", ".join(unknown)
            )
        if question.selection_type == "single" and len(answer.option_ids) > 1:
            raise ValueError(f"Question {question.id} accepts only one option")
        custom_text = answer.custom_text.strip()
        has_custom_answer = has_custom_answer or bool(custom_text)
        if custom_text and not question.allow_custom:
            raise ValueError(f"Question {question.id} does not accept custom input")
        if question.required and not answer.option_ids and not custom_text:
            raise ValueError(f"Question {question.id} requires an answer")

        selected = [options_by_id[option_id] for option_id in answer.option_ids]
        decision_keys = question.issue_keys or [f"answer.{question.id}"]
        for key in decision_keys:
            selected_values: list[dict[str, Any]] = []
            bindings_by_identifier: dict[str, IntentBinding] = {}
            evidence_refs: list[str] = []
            decision_label = question.title
            effects: set[IntentEffect] = set()
            for option in selected:
                resolution = option.resolutions.get(key)
                if resolution is None:
                    resolution = IntentResolution(
                        label=question.title, value=option.label
                    )
                if resolution.label:
                    decision_label = resolution.label
                option_value = option.model_dump(
                    mode="json",
                    exclude={"resolutions"},
                )
                option_value["resolution"] = resolution.value
                selected_values.append(option_value)
                for binding in resolution.bindings:
                    identifier = binding.identifier.strip()
                    if not identifier:
                        continue
                    existing_binding = bindings_by_identifier.get(identifier)
                    if existing_binding is not None and existing_binding != binding:
                        raise ValueError(
                            f"Selected options for {key} assign conflicting roles "
                            f"to {identifier}"
                        )
                    bindings_by_identifier[identifier] = binding.model_copy(
                        update={"identifier": identifier}
                    )
                effects.add(resolution.effect)
                evidence_refs.extend(option.evidence_refs)
            if len(effects) > 1:
                raise ValueError(f"Selected options for {key} have conflicting effects")
            value: dict[str, Any] = {"selected_options": selected_values}
            if custom_text:
                value["custom_text"] = custom_text
            decisions_by_key[key] = IntentDecision(
                key=key,
                kind=issue_kind_by_key.get(key, question.kind),
                label=decision_label,
                value=value,
                source="user",
                evidence_refs=list(dict.fromkeys(evidence_refs)),
                bindings=list(bindings_by_identifier.values()),
                effect=next(iter(effects), "include"),
                locked=not bool(custom_text),
                binding_phrase=question.binding_phrase,
            )
            if not custom_text:
                answered_issue_keys.add(key)

    remaining_issues = [
        issue for issue in context.issues if issue.key not in answered_issue_keys
    ]
    # Structured options already carry complete, validated resolutions for
    # every issue key. Re-running the LLM after such a submission only repeats
    # the same clarification. Custom text still needs semantic interpretation.
    merged_decisions = list(decisions_by_key.values())
    status: IntentStatus = (
        "ready"
        if (
            not has_custom_answer
            and not remaining_issues
            and decisions_by_key
            and not time_contract_incomplete(merged_decisions, context.time_intent)
        )
        else "evaluating"
    )
    summary = context.summary
    if status == "ready":
        resolved_summary = "; ".join(
            f"{label}: {rendered}"
            for label, rendered in decision_display_rows(
                list(decisions_by_key.values())
            )
        )
        summary = resolved_summary or context.original_question
    return IntentContext(
        version=context.version,
        status=status,
        original_question=context.original_question,
        summary=summary,
        decisions=merged_decisions,
        issues=remaining_issues,
        questions=list(context.questions) if status == "evaluating" else [],
        time_intent=dict(context.time_intent),
        submitted_answers=list(answers),
    )


def render_planning_question(
    context: IntentContext,
    *,
    latest_user_text: str = "",
) -> str:
    """Render one authoritative NLQ text from the persisted semantic contract."""
    parts = [f"原始问题：{context.original_question.strip()}"]
    if context.decisions:
        parts.append("已确定的查询口径（不得改写或忽略）：")
        for label, rendered in decision_display_rows(context.decisions):
            parts.append(f"- {label}: {rendered}")
    latest = (latest_user_text or "").strip()
    if latest and latest != context.original_question.strip():
        parts.append(f"本轮用户补充：{latest}")
    return "\n".join(parts)


def intent_context_from_payload(payload: Any) -> IntentContext:
    if isinstance(payload, IntentContext):
        return payload
    return IntentContext.model_validate(payload)


def public_intent_payload(context: IntentContext) -> dict[str, Any]:
    """Return the single SSE/REST/history representation."""
    return context.model_dump(mode="json")
