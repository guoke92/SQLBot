"""Structured semantic intent and clarification contracts for NLQ.

The intent contract describes *what* the user has confirmed.  It deliberately
does not contain SQL syntax or execute datasource work.  Graph nodes and HTTP
adapters share these models so one persisted payload drives streaming, history
rendering and the next clarification turn.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Literal

from pydantic import BaseModel, Field

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


class IntentResolution(BaseModel):
    """One option's concrete answer for one semantic contract slot."""

    label: str = ""
    value: Any
    required_identifiers: list[str] = Field(default_factory=list)


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
    required_identifiers: list[str] = Field(default_factory=list)
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


class IntentContext(BaseModel):
    version: int = 1
    status: IntentStatus = "evaluating"
    original_question: str
    summary: str = ""
    decisions: list[IntentDecision] = Field(default_factory=list)
    issues: list[IntentIssue] = Field(default_factory=list)
    questions: list[ClarificationQuestion] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)

    @property
    def awaiting_input(self) -> bool:
        return self.status == "needs_clarification"


def new_intent_context(question: str) -> IntentContext:
    return IntentContext(original_question=(question or "").strip())


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
            identifiers = [
                str(item).strip()
                for item in decision.get("required_identifiers") or []
                if str(item).strip()
            ]
        else:
            if not getattr(decision, "locked", False):
                continue
            label = str(
                getattr(decision, "label", "") or getattr(decision, "key", "")
            ).strip()
            value = getattr(decision, "value", None)
            identifiers = [
                str(item).strip()
                for item in getattr(decision, "required_identifiers", []) or []
                if str(item).strip()
            ]
        rendered = render_decision_value(value)
        identifiers = list(dict.fromkeys(identifiers))
        signature = (label, rendered, tuple(identifiers))
        if not rendered or signature in seen:
            continue
        seen.add(signature)
        rows.append((label, rendered, identifiers))
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
        if question.selection_type == "single" and answer.option_ids and custom_text:
            raise ValueError(
                f"Question {question.id} accepts either one option or custom input"
            )
        if question.required and not answer.option_ids and not custom_text:
            raise ValueError(f"Question {question.id} requires an answer")

        selected = [options_by_id[option_id] for option_id in answer.option_ids]
        decision_keys = question.issue_keys or [f"answer.{question.id}"]
        for key in decision_keys:
            selected_values: list[dict[str, Any]] = []
            required_identifiers: list[str] = []
            evidence_refs: list[str] = []
            decision_label = question.title
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
                required_identifiers.extend(resolution.required_identifiers)
                evidence_refs.extend(option.evidence_refs)
            value: dict[str, Any] = {"selected_options": selected_values}
            if custom_text:
                value["custom_text"] = custom_text
            decisions_by_key[key] = IntentDecision(
                key=key,
                kind=question.kind,
                label=decision_label,
                value=value,
                source="user",
                evidence_refs=list(dict.fromkeys(evidence_refs)),
                required_identifiers=list(dict.fromkeys(required_identifiers)),
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
    status: IntentStatus = (
        "ready"
        if not has_custom_answer and not remaining_issues and decisions_by_key
        else "evaluating"
    )
    return IntentContext(
        version=context.version,
        status=status,
        original_question=context.original_question,
        summary=context.summary,
        decisions=list(decisions_by_key.values()),
        issues=remaining_issues,
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
