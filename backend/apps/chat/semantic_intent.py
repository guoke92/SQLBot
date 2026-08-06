"""Clarification state for the canonical clause-oriented query contract.

This module owns the user interaction lifecycle only. SQL planning never
consumes questions, answers or display summaries; it consumes the frozen
``QueryContract`` stored in the same context.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Literal, Self, TypeGuard

from pydantic import BaseModel, ConfigDict, Field, model_validator

from apps.chat.contract.issues import (
    ContractAssumption,
    ContractIssue,
    answer_evidence,
    blocking_issues,
)
from apps.chat.contract.validation import validate_contract
from apps.chat.query_contract import (
    QUERY_CONTRACT_VERSION,
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

    version: Literal[4] = 4
    status: IntentStatus = "evaluating"
    original_question: str
    summary: str = ""
    draft: ContractDraft = Field(default_factory=ContractDraft)
    contract: QueryContract | None = None
    questions: list[ClarificationQuestion] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    contract_issues: list[ContractIssue] = Field(default_factory=list)
    assumptions: list[ContractAssumption] = Field(default_factory=list)
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

    @property
    def blocking_messages(self) -> list[str]:
        """Return assessor-authored blockers only.

        Structured ``contract_issues`` carry a code and are rendered by the
        presentation layer through i18n; the backend never composes their text.
        """

        return list(dict.fromkeys(self.blocking_reasons))

    @model_validator(mode="after")
    def validate_terminal_state(self) -> Self:
        blockers = blocking_issues(self.contract_issues)
        if self.status == "ready":
            if self.contract is None:
                raise ValueError("Ready intent context requires a frozen contract")
            if self.draft.open_slots:
                raise ValueError("Ready intent context cannot retain open slots")
            # Recomputed independently of the caller: a terminal that claims to
            # be executable must still hold up on its own contract.
            blockers = blockers + blocking_issues(validate_contract(self.contract))
            if blockers:
                raise ValueError(
                    "Ready intent context retains blocking contract issues: "
                    + ", ".join(item.code for item in blockers)
                )
        elif self.status != "blocked" and self.contract is not None:
            raise ValueError(
                "Only ready or blocked intent may contain a frozen contract"
            )
        if self.status == "blocked" and self.contract is not None and not blockers:
            raise ValueError(
                "Blocked intent with a frozen contract requires a blocking issue"
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


def dropped_assumptions(
    draft: ContractDraft,
    contract: QueryContract,
    code: str,
) -> list[ContractAssumption]:
    """Describe every clause the degradation removed, in business language."""
    kept = {requirement.slot_id for requirement in contract.requirements}
    return [
        ContractAssumption(
            slot_id=requirement.slot_id,
            code=code,
            label=requirement.label,
            detail=requirement_value(requirement),
        )
        for requirement in draft.requirements
        if requirement.slot_id not in kept
    ]


def finalize_intent_context(
    context: IntentContext,
    *,
    draft: ContractDraft,
    summary: str,
    submitted_answers: Sequence[ClarificationAnswer] | None = None,
    schema_text: str | None = None,
    assumptions: Sequence[ContractAssumption] = (),
) -> IntentContext:
    """Freeze the business revision, degrading inferences before blocking.

    ``freeze()`` only establishes an immutable revision; preparation problems
    are expected outcomes.  An issue caused solely by system inferences is
    resolved by dropping those inferences and stating the assumption, so only
    a problem with what the user actually confirmed can block the turn.
    """

    contract = draft.freeze()
    issues = validate_contract(contract, schema_text=schema_text)
    notes = list(assumptions)

    # Only an inference may be dropped to clear an issue. A confirmed clause
    # stays no matter which advisory it triggered; that invariant is what makes
    # degradation safe regardless of the rule that produced the advisory.
    droppable = {
        requirement.slot_id
        for requirement in draft.requirements
        if not requirement.is_confirmed
    } & {
        slot_id
        for issue in issues
        if issue.severity == "advisory"
        for slot_id in issue.slot_ids
    }
    if droppable and not blocking_issues(issues):
        reduced = draft.without(droppable)
        if reduced is not None:
            recheck = validate_contract(reduced, schema_text=schema_text)
            if not blocking_issues(recheck):
                notes.extend(dropped_assumptions(draft, reduced, "dropped_inference"))
                contract, issues = reduced, recheck

    resolved_answers = list(
        submitted_answers
        if submitted_answers is not None
        else context.submitted_answers
    )
    if blocking_issues(issues):
        return IntentContext(
            status="blocked",
            original_question=context.original_question,
            summary=summary,
            draft=draft,
            contract=contract,
            contract_issues=issues,
            assumptions=notes,
            submitted_answers=resolved_answers,
            base_record_id=context.base_record_id,
        )
    return IntentContext(
        status="ready",
        original_question=context.original_question,
        summary=summary,
        draft=ContractDraft(requirements=list(contract.requirements)),
        contract=contract,
        contract_issues=issues,
        assumptions=notes,
        submitted_answers=resolved_answers,
        base_record_id=context.base_record_id,
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
        # The join kind is enforced when the generated SQL is checked, so it
        # has to read as an instruction here rather than as a raw enum.
        population = {
            "intersection": "仅保留两侧都匹配的记录（INNER JOIN）",
            "left": "保留左侧全部记录（LEFT JOIN）",
            "right": "保留右侧全部记录（RIGHT JOIN）",
            "union": "保留两侧全部记录（FULL OUTER JOIN，引擎不支持时用 UNION 维键再 LEFT JOIN）",
        }[requirement.population]
        return f"{population}：{pairs}"
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


def contract_summary(contract: QueryContract | ContractDraft) -> str:
    """Render a contract as the one-line summary shown above a record."""
    return "；".join(
        f"{label}: {value}" for label, value in contract_display_rows(contract)
    )


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
                # An answered question is the strongest possible evidence, and
                # the ref is what keeps the clause confirmed after reloading.
                requirement = parse_requirement(
                    {
                        **effect.requirement.model_dump(mode="json"),
                        "source": "user",
                        "evidence_refs": list(
                            dict.fromkeys(
                                [
                                    *effect.requirement.evidence_refs,
                                    answer_evidence(question.id),
                                ]
                            )
                        ),
                    }
                )
                requirements = replace_requirement(requirements, requirement)
            remaining.pop(slot_id, None)

    draft = ContractDraft(
        requirements=requirements,
        open_slots=list(remaining.values()),
    )
    if not has_custom and not draft.open_slots:
        return finalize_intent_context(
            context,
            draft=draft,
            summary=contract_summary(draft),
            submitted_answers=answers,
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
    if (
        not isinstance(payload, Mapping)
        or payload.get("version") != QUERY_CONTRACT_VERSION
    ):
        raise ValueError(
            "Only semantic intent contract version "
            f"{QUERY_CONTRACT_VERSION} can be reused for execution"
        )
    return IntentContext.model_validate(payload)


def is_current_intent_payload(
    payload: Any,
) -> TypeGuard[Mapping[str, Any]]:
    """Check the persisted envelope version without duplicating literals."""

    return (
        isinstance(payload, Mapping)
        and payload.get("version") == QUERY_CONTRACT_VERSION
    )


def public_intent_payload(context: IntentContext) -> dict[str, Any]:
    return context.model_dump(mode="json")
