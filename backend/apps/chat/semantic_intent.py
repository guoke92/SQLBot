"""Clarification state for the canonical clause-oriented query contract.

This module owns the user interaction lifecycle only. SQL planning never
consumes questions, answers or display summaries; it consumes the frozen
``QueryContract`` stored in the same context.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from apps.chat.query_contract import (
    ContractDraft,
    ContractRequirement,
    ContractSlot,
    FieldRef,
    GroupRequirement,
    LimitRequirement,
    OrderRequirement,
    OutputRequirement,
    PredicateRequirement,
    ProjectionRequirement,
    QueryContract,
    RelationRequirement,
    SlotEffect,
    TimeWindowRequirement,
    parse_requirement,
    replace_requirement,
)

IntentStatus = Literal[
    "evaluating",
    "needs_clarification",
    "ready",
    "blocked",
]
SelectionType = Literal["single", "multiple", "text"]
RecommendationStrength = Literal["strong", "moderate", "weak"]


class IntentOption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    label: str
    description: str = ""
    impact: str = ""
    evidence_refs: list[str] = Field(default_factory=list)
    effects: list[SlotEffect] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_effect_slots(self) -> Self:
        slot_ids = [effect.slot_id for effect in self.effects]
        if len(slot_ids) != len(set(slot_ids)):
            raise ValueError(f"Option {self.id} contains duplicate slot effects")
        return self


class IntentIssue(ContractSlot):
    """Public name retained for the clarification payload."""


class ClarificationQuestion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    slot_ids: list[str] = Field(default_factory=list)
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

    @model_validator(mode="after")
    def validate_slot_ids(self) -> Self:
        self.id = self.id.strip()
        self.slot_ids = [slot_id.strip() for slot_id in self.slot_ids]
        if not self.id or not self.slot_ids or any(not item for item in self.slot_ids):
            raise ValueError("Clarification question requires id and slot_ids")
        if len(self.slot_ids) != len(set(self.slot_ids)):
            raise ValueError(f"Question {self.id} contains duplicate slot ids")
        return self


class ClarificationAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid")

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
    model_config = ConfigDict(extra="forbid")

    version: Literal[2] = 2
    status: IntentStatus = "evaluating"
    original_question: str
    summary: str = ""
    draft: ContractDraft = Field(default_factory=ContractDraft)
    contract: QueryContract | None = None
    questions: list[ClarificationQuestion] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    submitted_answers: list[ClarificationAnswer] = Field(default_factory=list)
    base_record_id: int | None = None

    @property
    def awaiting_input(self) -> bool:
        return self.status == "needs_clarification"

    @property
    def issues(self) -> list[IntentIssue]:
        return [
            IntentIssue.model_validate(slot.model_dump())
            for slot in self.draft.open_slots
        ]

    @model_validator(mode="after")
    def validate_terminal_state(self) -> Self:
        if self.status == "ready":
            if self.contract is None:
                raise ValueError("Ready intent context requires a frozen contract")
            if self.draft.open_slots:
                raise ValueError("Ready intent context cannot retain open slots")
        elif self.contract is not None:
            raise ValueError(
                "Only a ready intent context may contain a frozen contract"
            )
        return self


def new_intent_context(
    question: str,
    *,
    base_record_id: int | None = None,
    base_contract: QueryContract | None = None,
) -> IntentContext:
    requirements = list(base_contract.requirements) if base_contract else []
    return IntentContext(
        original_question=(question or "").strip(),
        base_record_id=base_record_id,
        draft=ContractDraft(requirements=requirements),
    )


def _field_text(field: FieldRef) -> str:
    return field.identifier


def requirement_value(requirement: ContractRequirement) -> str:
    """Render one clause in stable business-first text for prompts and history."""
    if isinstance(requirement, ProjectionRequirement):
        if requirement.mode == "all":
            return "展示全部字段"
        return "展示 " + "、".join(_field_text(field) for field in requirement.fields)
    if isinstance(requirement, OutputRequirement):
        operation = {
            "value": "直接展示",
            "count": "计数",
            "count_distinct": "去重计数",
            "sum": "合计",
            "avg": "平均",
            "min": "最小值",
            "max": "最大值",
            "distinct_concat": "去重拼接",
            "ratio": "比率",
            "difference": "差值",
        }[requirement.operation]
        return f"{operation} {_field_text(requirement.field)}"
    if isinstance(requirement, PredicateRequirement):
        values = "、".join(str(value) for value in requirement.values)
        return (
            f"{_field_text(requirement.field)} {requirement.operator} {values}".strip()
        )
    if isinstance(requirement, GroupRequirement):
        suffix = f"，按{requirement.bucket}分组" if requirement.bucket else ""
        return f"按 {_field_text(requirement.field)} 分组{suffix}"
    if isinstance(requirement, RelationRequirement):
        pairs = "、".join(
            f"{_field_text(pair.left)} ↔ {_field_text(pair.right)}"
            for pair in requirement.pairs
        )
        return f"{requirement.population}：{pairs}"
    if isinstance(requirement, TimeWindowRequirement):
        fields = "、".join(_field_text(field) for field in requirement.fields)
        if requirement.mode == "all":
            scope = "全部时间"
        elif requirement.mode == "rolling":
            scope = f"最近 {requirement.rolling_months} 个月"
        else:
            scope = f"{requirement.start} 至 {requirement.end_exclusive}（结束不含）"
        return f"{fields}：{scope}"
    if isinstance(requirement, OrderRequirement):
        target = (
            _field_text(requirement.field)
            if requirement.field is not None
            else requirement.output_slot_id or ""
        )
        return f"按 {target} {requirement.direction.upper()} 排序"
    if isinstance(requirement, LimitRequirement):
        return f"仅返回 {requirement.value} 条"
    return requirement.label


def contract_display_rows(
    contract: QueryContract | ContractDraft,
) -> list[tuple[str, str]]:
    return [
        (requirement.label, requirement_value(requirement))
        for requirement in contract.requirements
    ]


def _merge_selected_effects(
    slot_id: str,
    selected: Sequence[SlotEffect],
) -> SlotEffect:
    if not selected:
        raise ValueError(f"No selected effect for slot {slot_id}")
    if all(effect.action == "omit" for effect in selected):
        return SlotEffect(slot_id=slot_id, action="omit")
    if any(effect.action == "omit" for effect in selected):
        raise ValueError(
            f"Multiple selections for slot {slot_id} mix set and omit effects"
        )
    requirements = [
        effect.requirement for effect in selected if effect.requirement is not None
    ]
    if not requirements:
        raise ValueError(f"No selected requirement for slot {slot_id}")
    first = requirements[0]
    if len(requirements) == 1:
        return SlotEffect(slot_id=slot_id, action="set", requirement=first)
    if all(
        isinstance(item, PredicateRequirement)
        and item.field == first.field
        and item.operator in {"eq", "in"}
        for item in requirements
    ):
        values = list(
            dict.fromkeys(
                value
                for item in requirements
                if isinstance(item, PredicateRequirement)
                for value in item.values
            )
        )
        return SlotEffect(
            slot_id=slot_id,
            action="set",
            requirement=PredicateRequirement(
                slot_id=slot_id,
                label=first.label,
                source="user",
                evidence_refs=list(
                    dict.fromkeys(
                        ref for item in requirements for ref in item.evidence_refs
                    )
                ),
                field=first.field,
                operator="in",
                values=values,
            ),
        )
    raise ValueError(
        f"Multiple selections for slot {slot_id} cannot form one deterministic clause"
    )


def merge_clarification_answers(
    context: IntentContext,
    answers: list[ClarificationAnswer],
) -> IntentContext:
    """Apply structured choices directly; custom text remains targeted evidence."""
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

    requirements = list(context.draft.requirements)
    remaining = {slot.slot_id: slot for slot in context.draft.open_slots}
    has_custom = False
    for question in context.questions:
        answer = answer_by_id.get(question.id)
        if answer is None:
            continue
        options = {option.id: option for option in question.options}
        unknown = [
            option_id for option_id in answer.option_ids if option_id not in options
        ]
        if unknown:
            raise ValueError(
                f"Unknown option(s) for {question.id}: " + ", ".join(unknown)
            )
        if question.selection_type == "single" and len(answer.option_ids) > 1:
            raise ValueError(f"Question {question.id} accepts only one option")
        custom_text = answer.custom_text.strip()
        if custom_text and not question.allow_custom:
            raise ValueError(f"Question {question.id} does not accept custom input")
        if question.required and not answer.option_ids and not custom_text:
            raise ValueError(f"Question {question.id} requires an answer")
        if custom_text:
            has_custom = True
            continue

        selected_options = [options[option_id] for option_id in answer.option_ids]
        for slot_id in question.slot_ids:
            effects = [
                effect
                for option in selected_options
                for effect in option.effects
                if effect.slot_id == slot_id
            ]
            if not effects:
                raise ValueError(
                    f"Selected option does not resolve contract slot {slot_id}"
                )
            effect = _merge_selected_effects(slot_id, effects)
            if effect.action == "omit":
                requirements = [
                    item for item in requirements if item.slot_id != slot_id
                ]
            else:
                assert effect.requirement is not None
                requirement = parse_requirement(
                    {
                        **effect.requirement.model_dump(mode="json"),
                        "source": "user",
                    }
                )
                requirements = replace_requirement(requirements, requirement)
            remaining.pop(slot_id, None)

    draft = ContractDraft(
        requirements=requirements, open_slots=list(remaining.values())
    )
    if not has_custom and not draft.open_slots:
        contract = draft.freeze()
        return IntentContext(
            status="ready",
            original_question=context.original_question,
            summary="；".join(
                f"{label}: {value}" for label, value in contract_display_rows(contract)
            ),
            draft=draft,
            contract=contract,
            submitted_answers=list(answers),
            base_record_id=context.base_record_id,
        )
    return context.model_copy(
        update={
            "status": "evaluating",
            "draft": draft,
            "contract": None,
            "submitted_answers": list(answers),
        }
    )


def render_planning_question(
    context: IntentContext,
    *,
    latest_user_text: str = "",
) -> str:
    parts = [f"原始问题：{context.original_question.strip()}"]
    if context.draft.requirements:
        parts.append("已确定的查询口径（不得改写或忽略）：")
        for label, rendered in contract_display_rows(context.draft):
            parts.append(f"- {label}: {rendered}")
    latest = latest_user_text.strip()
    if latest and latest != context.original_question.strip():
        parts.append(f"本轮用户补充：{latest}")
    return "\n".join(parts)


def intent_context_from_payload(payload: Any) -> IntentContext:
    if isinstance(payload, IntentContext):
        return payload
    if not isinstance(payload, Mapping) or payload.get("version") != 2:
        raise ValueError(
            "Only semantic intent contract version 2 can be reused for execution"
        )
    return IntentContext.model_validate(payload)


def public_intent_payload(context: IntentContext) -> dict[str, Any]:
    return context.model_dump(mode="json")
