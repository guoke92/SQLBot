"""Build and resolve the canonical clause-oriented query contract."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any, Literal

import orjson
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from apps.chat.query_contract import (
    ContractDraft,
    ContractRequirement,
    ContractSlot,
    FieldRef,
    GroupRequirement,
    OutputRequirement,
    PredicateRequirement,
    RelationRequirement,
    SlotEffect,
    TimeWindowRequirement,
    parse_requirement,
    replace_requirement,
    requirement_fields,
    requirement_resources,
)
from apps.chat.semantic_intent import (
    ClarificationQuestion,
    IntentContext,
    IntentIssue,
    IntentOption,
    contract_display_rows,
)
from apps.conversation.messages import message_content_text
from common.utils.json_utils import extract_nested_json


class IntentAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intent_mode: Literal["new", "refine"] = "new"
    status: Literal["ready", "needs_clarification", "blocked"]
    summary: str = ""
    edits: list[SlotEffect] = Field(default_factory=list)
    issues: list[IntentIssue] = Field(default_factory=list)
    questions: list[ClarificationQuestion] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)


@dataclass(frozen=True)
class SemanticAssessmentResult:
    context: IntentContext
    usage: dict[str, Any]
    reasoning: str
    attempts: list[dict[str, Any]]


class SemanticAssessmentError(RuntimeError):
    """The assessor failed technically; this is not a business blockage."""

    def __init__(
        self,
        message: str,
        *,
        usage: dict[str, Any],
        reasoning: str,
        attempts: list[dict[str, Any]],
    ) -> None:
        super().__init__(message)
        self.usage = usage
        self.reasoning = reasoning
        self.attempts = attempts


_FORBIDDEN_USER_FACING_TERMS = (
    "join",
    "group by",
    "coalesce",
    "union",
    "cte",
    "主键",
    "外键",
    "关联字段",
    "关联路径",
)

_BUSINESS_TERM_REPLACEMENTS = {
    "主键": "唯一业务标识",
    "外键": "对应业务标识",
    "关联字段": "业务对应信息",
    "关联路径": "业务对应关系",
}

_SYSTEM_PROMPT = """你是数据查询契约审核器。不要生成 SQL。请把用户需求转换为一份按业务子句组织的查询契约，并只澄清会实质改变结果集或统计值的业务歧义。

唯一契约规则：
- clause 只能是 projection/output/predicate/group/relation/time_window/order/limit。
- 每个 requirement 只表达一个 clause，不能用一个通用 role 代替多个子句。
- slot_id 只是稳定引用。新槽位可使用有意义的临时名称，服务端会分配最终身份；已有槽位必须沿用原 slot_id。
- edits 和选项 effects 只使用 set/omit。set 提供完整 requirement；omit 不提供 requirement。
- new 查询不得改写已有已确认槽位；refine 才能 set/omit 已确认槽位。未变更槽位不重复返回。
- schema 只可验证字段存在、类型和用户概念的唯一映射，不能凭 schema 创造“排除隐藏”“仅有效数据”等结果集政策。
- 用户明确说“最新 N 条”表示 order + limit，不代表时间范围；只有明确期间才产生 time_window。
- 不输出某字段只影响 projection/output，不等于排除对应数据。
- 平台返回行数上限不是用户契约；只有用户明确数量才产生 limit。
- relation 同时给出字段对和业务主体范围 population(intersection/left/right/union)。
- 一个共享分组结果引用多个事实资源时，relation 是必需子句；字段对依据 schema，population 是业务范围，未明确时必须澄清，不能由 SQL 阶段默认选择。
- “查询/展示对应的字段”默认是 output(value)，不等于 group；只有用户要求“按该维度统计/拆分”时才生成 group。
- 多事实结果中的 group 必须是各事实都能对应的共享业务粒度；某字段只存在于一侧且会让另一侧指标重复时，必须澄清取值/展示政策，不能直接按它拆分。
- output.operation 只能是 value/count/count_distinct/sum/avg/min/max/distinct_concat/ratio/difference；不生成任意公式语言。
- predicate.null_policy 默认 exclude；只有业务明确要求保留空值时才用 preserve，is_null 使用 only。
- time_window.mode 只能是 all/explicit/rolling；explicit 使用 start + end_exclusive；一个业务范围涉及多个事实来源时 fields 列出每个对应时间字段。
- order 使用 field 或 output_slot_id 二选一；limit.value 必须大于 0。

澄清规则：
- 一次列出当前证据能发现的全部关键业务问题；高度相关的问题可以合并，正交问题保持独立。
- 用户只确认业务需求，不负责选择表、连接方式或 SQL 实现。
- 字段提示用“业务名称(field_name)”；不要默认展示物理表名。
- 推荐仅标记，不代替用户选择。每题提供 2~3 个互斥选项和业务影响，并允许自定义回答。
- question 不声明 clause kind；一条业务问题可以同时确认 output/time_window/group 等多个相关子句。
- question.slot_ids 必须覆盖对应 issues.slot_id；每个 option.effects 必须恰好逐一处理这些 slot，不能缺少或额外处理其他 slot。
- 结构化选项的 set effect 必须给出完整 requirement，requirement.slot_id 与 effect.slot_id 相同；omit 仅可用于 issue.allow_omit=true 的可选业务维度。
- 自定义回答只作为这些 slot 的新证据，不能与选项简单拼接。
- deterministic_time_parse 中明确且高置信度的 start/end_exclusive 是用户已表达的期间。每个相关 time_window 选项必须直接使用该范围，并绑定实际业务时间字段；不得创建没有 fields 的独立“年份范围”槽位。
- 已有契约槽位是锁定事实；除 refine 的显式 replace/remove 外不得改写，也不得重复提问。
- 只有现有证据无法提供可执行选项才 blocked；存在合理选项则 needs_clarification；所有槽位明确后 ready。
- ready 必须能形成非空契约，且 edits/issues/questions 互不冲突。
- 所有面向用户的 title/reason/label/description/impact 使用业务语言，不出现数据库实现术语。
- 输出必须严格符合随后提供的 JSON Schema，不要 Markdown，也不要输出 schema 之外的字段。
"""


def _assessment_schema_text() -> str:
    return orjson.dumps(IntentAssessment.model_json_schema()).decode()


_REPAIR_PROMPT = """上一候选未通过结构或契约校验。请基于原始系统规则、原始业务证据和校验问题，返回修正后的完整 JSON。
- 只修复已指出的问题，不重新解释或遗失已经完整的业务口径。
- 不得编造字段；不确定的 requirement 应保留为 issue/question。
- 输出严格符合 JSON Schema，不要 Markdown。
"""


def _reasoning_content(response: Any) -> str:
    additional = getattr(response, "additional_kwargs", None) or {}
    if isinstance(additional, dict):
        return str(
            additional.get("reasoning_content") or additional.get("reasoning") or ""
        )
    return ""


def _assessment_shape(raw_text: str) -> dict[str, Any]:
    try:
        json_text = extract_nested_json(raw_text)
        payload = orjson.loads(json_text) if json_text else {}
    except (TypeError, ValueError):
        return {}
    if not isinstance(payload, dict):
        return {}
    return {
        "status": str(payload.get("status") or ""),
        "edit_count": len(payload.get("edits") or []),
        "issue_slots": [
            str(item.get("slot_id") or "")
            for item in payload.get("issues") or []
            if isinstance(item, dict)
        ],
        "question_ids": [
            str(item.get("id") or "")
            for item in payload.get("questions") or []
            if isinstance(item, dict)
        ],
    }


def _attempt_diagnostic(
    *,
    attempt: int,
    raw_text: str,
    usage: dict[str, Any],
    error: Exception | None,
) -> dict[str, Any]:
    result = {
        "attempt": attempt,
        "valid": error is None,
        "token_usage": usage,
        **_assessment_shape(raw_text),
    }
    if error is not None:
        result["validation_error"] = str(error)[:1000]
    return result


def _validation_diagnostic(error: Exception) -> str:
    if isinstance(error, ValidationError):
        issues = [
            {
                "path": ".".join(str(part) for part in item.get("loc") or ()),
                "code": item.get("type"),
                "message": item.get("msg"),
            }
            for item in error.errors(include_url=False, include_input=False)
        ]
        return orjson.dumps(issues).decode()
    return str(error)[:2000]


def _translated(
    trans: Callable[..., str] | None,
    key: str,
    fallback: str,
    **kwargs: str,
) -> str:
    if callable(trans):
        value = trans(key, **kwargs)
        if value and value != key:
            return value
    return fallback.format(**kwargs)


def _entity_slot_id(phrase: str) -> str:
    digest = hashlib.sha256(phrase.encode("utf-8")).hexdigest()[:12]
    return f"entity_{digest}"


def _target_field(target: Mapping[str, Any]) -> FieldRef | None:
    table = str(target.get("table_name") or "").strip()
    field = str(target.get("field_name") or "").strip()
    if not field:
        return None
    return FieldRef(resource=table, field=field)


def _entity_questions(
    bindings: Mapping[str, Any],
    trans: Callable[..., str] | None,
) -> tuple[list[IntentIssue], list[ClarificationQuestion]]:
    issues: list[IntentIssue] = []
    questions: list[ClarificationQuestion] = []
    for phrase, binding in (bindings.get("ambiguous") or {}).items():
        slot_id = _entity_slot_id(str(phrase))
        options: list[IntentOption] = []
        seen: set[tuple[str, str]] = set()
        for index, candidate in enumerate(binding.get("options") or []):
            canonical = str(candidate.get("canonical") or "").strip()
            fields = [
                field
                for target in candidate.get("targets") or []
                if (field := _target_field(target)) is not None
            ]
            if not canonical or not fields:
                continue
            field = fields[0]
            signature = (canonical.casefold(), field.normalized)
            if signature in seen:
                continue
            seen.add(signature)
            description = str(candidate.get("description") or "").strip()
            business_field = (
                f"{description}({field.field})" if description else field.field
            )
            requirement = PredicateRequirement(
                slot_id=slot_id,
                label=str(phrase),
                source="terminology",
                evidence_refs=[f"field:{field.identifier}"],
                field=field,
                operator="eq",
                values=[canonical],
            )
            options.append(
                IntentOption(
                    id=f"value_{index + 1}",
                    label=canonical,
                    description=_translated(
                        trans,
                        "i18n_chat.clarification.entity_targets",
                        "业务字段：{targets}",
                        targets=business_field,
                    ),
                    impact=_translated(
                        trans,
                        "i18n_chat.clarification.entity_impact",
                        "查询中将“{phrase}”按“{canonical}”精确过滤",
                        phrase=str(phrase),
                        canonical=canonical,
                    ),
                    evidence_refs=requirement.evidence_refs,
                    effects=[
                        SlotEffect(
                            slot_id=slot_id,
                            action="set",
                            requirement=requirement,
                        )
                    ],
                )
            )
        if not options:
            continue
        issue = IntentIssue(
            slot_id=slot_id,
            clause="predicate",
            label=str(phrase),
            reason=_translated(
                trans,
                "i18n_chat.clarification.entity_issue",
                "“{phrase}”需要确认具体业务值",
                phrase=str(phrase),
            ),
            evidence_refs=list(
                dict.fromkeys(ref for option in options for ref in option.evidence_refs)
            ),
        )
        issues.append(issue)
        questions.append(
            ClarificationQuestion(
                id=slot_id,
                slot_ids=[slot_id],
                title=_translated(
                    trans,
                    "i18n_chat.clarification.entity_title",
                    "“{phrase}”具体指哪个业务值？",
                    phrase=str(phrase),
                ),
                reason=_translated(
                    trans,
                    "i18n_chat.clarification.entity_reason",
                    "不同取值会直接改变过滤范围。",
                ),
                recommended_option_ids=[options[0].id],
                recommendation_reason=_translated(
                    trans,
                    "i18n_chat.clarification.entity_recommendation",
                    "按术语召回相关度推荐最匹配的值。",
                ),
                recommendation_strength="moderate",
                options=options[:3],
                custom_placeholder=_translated(
                    trans,
                    "i18n_chat.clarification.entity_custom_placeholder",
                    "输入准确的业务值",
                ),
            )
        )
    return issues, questions


def _next_slot_id(existing: set[str], counter: int) -> tuple[str, int]:
    current = counter
    while True:
        candidate = f"slot_{current:04d}"
        current += 1
        if candidate not in existing:
            existing.add(candidate)
            return candidate, current


def _source_from_evidence(evidence_refs: list[str]) -> str:
    joined = " ".join(evidence_refs).casefold()
    if "terminology" in joined or "entity" in joined:
        return "terminology"
    if "example" in joined or "training" in joined:
        return "example"
    if "rule" in joined or "custom_prompt" in joined:
        return "rule"
    if "schema" in joined or "field:" in joined:
        return "schema"
    return "user"


_TABLE_HEADER_RE = re.compile(r"^#\s*Table:\s*([^,;\s]+)", re.MULTILINE)
_FIELD_LINE_RE = re.compile(r"^\s*\(([^:(),\s]+)\s*:", re.MULTILINE)


def _schema_fields(schema_text: str) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    matches = list(_TABLE_HEADER_RE.finditer(schema_text or ""))
    for index, match in enumerate(matches):
        table = match.group(1).strip().strip('`"[]').casefold()
        end = (
            matches[index + 1].start() if index + 1 < len(matches) else len(schema_text)
        )
        block = schema_text[match.end() : end]
        fields = {
            field.group(1).strip().strip('`"[]').casefold()
            for field in _FIELD_LINE_RE.finditer(block)
        }
        result[table] = fields
        result.setdefault(table.rsplit(".", 1)[-1], fields)
    return result


def _validate_contract_fields(
    requirements: list[ContractRequirement],
    schema_text: str,
) -> None:
    catalog = _schema_fields(schema_text)
    if not catalog:
        return
    all_fields = set().union(*catalog.values()) if catalog else set()
    unknown: list[str] = []
    for requirement in requirements:
        if isinstance(requirement, OutputRequirement) and requirement.operation in {
            "ratio",
            "difference",
        }:
            continue
        for field in requirement_fields(requirement):
            if field.resource:
                valid = field.field.casefold() in catalog.get(
                    field.resource.casefold(),
                    catalog.get(field.resource_name.casefold(), set()),
                )
            else:
                valid = field.field.casefold() in all_fields
            if not valid:
                unknown.append(field.identifier)
    if unknown:
        raise ValueError(
            "Contract references field(s) absent from the retrieved schema: "
            + ", ".join(dict.fromkeys(unknown))
        )


def _remap_new_slots(
    assessment: IntentAssessment,
    *,
    existing_ids: set[str],
) -> IntentAssessment:
    """Turn response-local names into opaque server slot ids exactly once."""
    mapping: dict[str, str] = {}
    counter = 1
    for effect in assessment.edits:
        raw = effect.slot_id.strip()
        if raw in existing_ids:
            mapping[raw] = raw
        elif effect.action == "omit":
            raise ValueError(f"Omit edit references unknown slot: {raw}")
        elif raw not in mapping:
            mapping[raw], counter = _next_slot_id(existing_ids, counter)
    for issue in assessment.issues:
        raw = issue.slot_id.strip()
        if raw not in existing_ids and raw not in mapping:
            mapping[raw], counter = _next_slot_id(existing_ids, counter)
        else:
            mapping.setdefault(raw, raw)

    edits: list[SlotEffect] = []
    for effect in assessment.edits:
        slot_id = mapping.get(effect.slot_id, effect.slot_id)
        requirement = effect.requirement
        if requirement is not None:
            requirement = parse_requirement(
                {
                    **requirement.model_dump(mode="json"),
                    "slot_id": slot_id,
                    "source": _source_from_evidence(requirement.evidence_refs),
                }
            )
        edits.append(
            SlotEffect(
                action=effect.action,
                slot_id=slot_id,
                requirement=requirement,
            )
        )
    issues = [
        issue.model_copy(update={"slot_id": mapping.get(issue.slot_id, issue.slot_id)})
        for issue in assessment.issues
    ]
    questions: list[ClarificationQuestion] = []
    for question in assessment.questions:
        slot_ids = [mapping.get(slot_id, slot_id) for slot_id in question.slot_ids]
        options: list[IntentOption] = []
        for option in question.options:
            effects: list[SlotEffect] = []
            for effect in option.effects:
                slot_id = mapping.get(effect.slot_id, effect.slot_id)
                requirement = effect.requirement
                if requirement is not None:
                    requirement = parse_requirement(
                        {
                            **requirement.model_dump(mode="json"),
                            "slot_id": slot_id,
                            "source": _source_from_evidence(requirement.evidence_refs),
                        }
                    )
                effects.append(
                    SlotEffect(
                        slot_id=slot_id,
                        action=effect.action,
                        requirement=requirement,
                    )
                )
            options.append(option.model_copy(update={"effects": effects}))
        questions.append(
            question.model_copy(update={"slot_ids": slot_ids, "options": options})
        )
    return assessment.model_copy(
        update={"edits": edits, "issues": issues, "questions": questions}
    )


def _validate_question(
    question: ClarificationQuestion,
    open_slots: Mapping[str, ContractSlot],
    schema_text: str,
) -> None:
    if not question.id.strip():
        raise ValueError("Clarification question id cannot be empty")
    if not question.slot_ids or any(
        slot_id not in open_slots for slot_id in question.slot_ids
    ):
        raise ValueError(
            f"Clarification question {question.id} references non-open slots"
        )
    option_ids: set[str] = set()
    option_labels: set[str] = set()
    normalized_options: list[IntentOption] = []
    for option in question.options:
        option = option.model_copy(
            update={
                "label": _business_language(option.label),
                "description": _business_language(option.description),
                "impact": _business_language(option.impact),
            }
        )
        label = option.label.strip().casefold()
        if (
            not option.id
            or not label
            or option.id in option_ids
            or label in option_labels
        ):
            raise ValueError(
                f"Clarification question {question.id} has duplicate options"
            )
        option_ids.add(option.id)
        option_labels.add(label)
        effect_ids = {effect.slot_id for effect in option.effects}
        expected_ids = set(question.slot_ids)
        if effect_ids != expected_ids:
            raise ValueError(
                f"Clarification option {option.id} must resolve exactly: "
                + ", ".join(sorted(expected_ids))
            )
        for effect in option.effects:
            slot = open_slots[effect.slot_id]
            if effect.action == "omit":
                if not slot.allow_omit:
                    raise ValueError(
                        f"Contract slot {effect.slot_id} cannot be omitted"
                    )
                continue
            assert effect.requirement is not None
            if effect.requirement.clause != slot.clause:
                raise ValueError(
                    f"Effect for {effect.slot_id} has clause "
                    f"{effect.requirement.clause}, expected {slot.clause}"
                )
            _validate_contract_fields([effect.requirement], schema_text)
        fields = list(
            dict.fromkeys(
                field.field
                for effect in option.effects
                if effect.requirement is not None
                and effect.requirement.clause
                in {"output", "group", "time_window", "order"}
                for field in requirement_fields(effect.requirement)
            )
        )
        if len(fields) == 1 and fields[0].casefold() not in option.label.casefold():
            option = option.model_copy(update={"label": f"{option.label}({fields[0]})"})
        normalized_options.append(option)
    if question.selection_type != "text" and len(question.options) < 2:
        raise ValueError(f"Clarification question {question.id} requires 2-3 options")
    if len(question.options) > 3:
        del question.options[3:]
    question.options = normalized_options[:3]
    question.title = _business_language(question.title)
    question.reason = _business_language(question.reason)
    question.recommendation_reason = _business_language(
        question.recommendation_reason
    )
    question.custom_placeholder = _business_language(question.custom_placeholder)
    available = {option.id for option in question.options}
    question.recommended_option_ids = [
        item
        for item in dict.fromkeys(question.recommended_option_ids)
        if item in available
    ][:1]
    visible = "\n".join(
        [
            question.title,
            question.reason,
            question.recommendation_reason,
            *(
                text
                for option in question.options
                for text in (option.label, option.description, option.impact)
            ),
        ]
    ).casefold()
    forbidden = [
        term
        for term in _FORBIDDEN_USER_FACING_TERMS
        if (
            re.search(rf"\b{re.escape(term)}\b", visible)
            if term.isascii()
            else term in visible
        )
    ]
    if forbidden:
        raise ValueError(
            "Clarification exposes database implementation terms: "
            + ", ".join(forbidden)
        )


def _business_language(value: str) -> str:
    """Normalize known implementation vocabulary at the presentation boundary."""
    result = value
    for term, replacement in _BUSINESS_TERM_REPLACEMENTS.items():
        if term.isascii():
            result = re.sub(
                rf"\b{re.escape(term)}\b",
                replacement,
                result,
                flags=re.IGNORECASE,
            )
        else:
            result = result.replace(term, replacement)
    return result


def _validate_draft_relation_closure(
    requirements: list[ContractRequirement],
    open_slots: Mapping[str, ContractSlot],
    questions: list[ClarificationQuestion],
) -> None:
    """Ensure a multi-resource shared grain cannot omit the relation decision.

    For unresolved slots we only use resources common to every selectable
    option.  Alternative source choices therefore do not create false
    multi-resource requirements, while mandatory signed/financing facts do.
    """
    clauses: list[tuple[str, frozenset[str]]] = [
        (requirement.clause, requirement_resources(requirement))
        for requirement in requirements
    ]
    question_by_slot = {
        slot_id: question
        for question in questions
        for slot_id in question.slot_ids
    }
    for slot_id, slot in open_slots.items():
        question = question_by_slot.get(slot_id)
        if question is None:
            continue
        option_resources: list[frozenset[str]] = []
        for option in question.options:
            effect = next(
                (effect for effect in option.effects if effect.slot_id == slot_id),
                None,
            )
            if effect is None or effect.requirement is None:
                option_resources = []
                break
            option_resources.append(requirement_resources(effect.requirement))
        if option_resources:
            common = set(option_resources[0])
            for resources in option_resources[1:]:
                common.intersection_update(resources)
            clauses.append((slot.clause, frozenset(common)))

    group_resources = {
        resource
        for clause, resources in clauses
        if clause == "group"
        for resource in resources
    }
    output_resources = {
        resource
        for clause, resources in clauses
        if clause == "output"
        for resource in resources
    }
    result_resources = group_resources | output_resources
    if not group_resources or len(result_resources) <= 1:
        return
    has_relation = any(
        isinstance(requirement, RelationRequirement) for requirement in requirements
    ) or any(slot.clause == "relation" for slot in open_slots.values())
    if not has_relation:
        raise ValueError(
            "Grouped multi-resource assessment must expose a relation/population "
            "contract slot for: " + ", ".join(sorted(result_resources))
        )


def _validate_deterministic_time(
    requirements: list[ContractRequirement],
    temporal_parse: Mapping[str, Any],
) -> None:
    if (
        temporal_parse.get("scope") != "explicit"
        or float(temporal_parse.get("confidence") or 0) < 0.9
    ):
        return
    expected_start = str(temporal_parse.get("start") or "")
    expected_end = str(temporal_parse.get("end_exclusive") or "")
    for requirement in requirements:
        if not isinstance(requirement, TimeWindowRequirement):
            continue
        if requirement.mode != "explicit":
            raise ValueError(
                f"Time slot {requirement.slot_id} contradicts the explicit user period"
            )
        if (
            requirement.start != expected_start
            or requirement.end_exclusive != expected_end
        ):
            raise ValueError(
                f"Time slot {requirement.slot_id} must use deterministic bounds "
                f"{expected_start} to {expected_end}"
            )


def _normalize_assessment(
    assessment: IntentAssessment,
    context: IntentContext,
    bindings: Mapping[str, Any],
    schema_text: str,
    trans: Callable[..., str] | None,
    temporal_parse: Mapping[str, Any],
) -> IntentContext:
    existing = {item.slot_id: item for item in context.draft.requirements}
    existing_open = {slot.slot_id: slot for slot in context.draft.open_slots}
    if (
        assessment.intent_mode == "new"
        and context.base_record_id is not None
        and not context.submitted_answers
        and not context.draft.open_slots
    ):
        existing = {}
    known_ids = set(existing) | {slot.slot_id for slot in context.draft.open_slots}
    normalized = _remap_new_slots(assessment, existing_ids=known_ids)
    requirements = list(existing.values())
    changed_slots: set[str] = set()
    for effect in normalized.edits:
        if effect.slot_id in changed_slots:
            raise ValueError(f"Duplicate contract edit for slot {effect.slot_id}")
        changed_slots.add(effect.slot_id)
        if effect.slot_id in existing and normalized.intent_mode != "refine":
            raise ValueError(
                f"New query cannot mutate locked contract slot {effect.slot_id}"
            )
        open_slot = existing_open.get(effect.slot_id)
        if open_slot is not None:
            if effect.action == "omit" and not open_slot.allow_omit:
                raise ValueError(f"Contract slot {effect.slot_id} cannot be omitted")
            if (
                effect.requirement is not None
                and effect.requirement.clause != open_slot.clause
            ):
                raise ValueError(
                    f"Edit for {effect.slot_id} has clause "
                    f"{effect.requirement.clause}, expected {open_slot.clause}"
                )
        if effect.action == "omit":
            requirements = [
                item for item in requirements if item.slot_id != effect.slot_id
            ]
        else:
            assert effect.requirement is not None
            requirements = replace_requirement(requirements, effect.requirement)

    resolved_ids = {item.slot_id for item in requirements}
    issues_by_id: dict[str, ContractSlot] = {
        slot_id: slot
        for slot_id, slot in existing_open.items()
        if slot_id not in resolved_ids and slot_id not in changed_slots
    }
    for issue in normalized.issues:
        if issue.slot_id not in resolved_ids:
            issues_by_id.setdefault(issue.slot_id, issue)
    entity_issues, entity_questions = _entity_questions(bindings, trans)
    for issue in entity_issues:
        if issue.slot_id not in resolved_ids:
            issues_by_id.setdefault(issue.slot_id, issue)
    overlap = set(issues_by_id) & resolved_ids
    if overlap:
        raise ValueError(
            "Contract slots cannot be both resolved and ambiguous: "
            + ", ".join(sorted(overlap))
        )
    draft = ContractDraft(
        requirements=requirements,
        open_slots=list(issues_by_id.values()),
    )
    _validate_contract_fields(requirements, schema_text)
    _validate_deterministic_time(requirements, temporal_parse)
    questions: list[ClarificationQuestion] = []
    question_ids: set[str] = set()
    covered: set[str] = set()
    for question in [*entity_questions, *normalized.questions]:
        if question.id in question_ids:
            raise ValueError(f"Duplicate clarification question id: {question.id}")
        relevant = [slot_id for slot_id in question.slot_ids if slot_id in issues_by_id]
        if not relevant:
            raise ValueError(
                f"Clarification question {question.id} has no matching open slot"
            )
        overlap_slots = covered & set(relevant)
        if overlap_slots:
            raise ValueError(
                "Contract slot(s) covered by multiple questions: "
                + ", ".join(sorted(overlap_slots))
            )
        question = question.model_copy(update={"slot_ids": relevant})
        _validate_question(question, issues_by_id, schema_text)
        _validate_deterministic_time(
            [
                effect.requirement
                for option in question.options
                for effect in option.effects
                if effect.requirement is not None
            ],
            temporal_parse,
        )
        questions.append(question)
        question_ids.add(question.id)
        covered.update(relevant)
    uncovered = set(issues_by_id) - covered
    if uncovered and normalized.status != "blocked":
        raise ValueError(
            "Clarification omitted options for slot(s): " + ", ".join(sorted(uncovered))
        )

    if normalized.status != "blocked":
        _validate_draft_relation_closure(
            requirements,
            issues_by_id,
            questions,
        )

    blocking = list(dict.fromkeys(normalized.blocking_reasons))
    if questions:
        status: Literal["needs_clarification", "ready", "blocked"] = (
            "needs_clarification"
        )
    elif normalized.status == "blocked" or blocking:
        status = "blocked"
    else:
        status = "ready"
    if status == "ready":
        contract = ContractDraft(requirements=requirements).freeze()
        return IntentContext(
            status="ready",
            original_question=context.original_question,
            summary=normalized.summary,
            draft=ContractDraft(requirements=requirements),
            contract=contract,
            submitted_answers=list(context.submitted_answers),
            base_record_id=context.base_record_id,
        )
    if status == "blocked" and not blocking:
        blocking = [normalized.summary or "现有证据不足以形成可执行查询口径"]
    return IntentContext(
        status=status,
        original_question=context.original_question,
        summary=normalized.summary,
        draft=draft,
        questions=questions if status == "needs_clarification" else [],
        blocking_reasons=blocking if status == "blocked" else [],
        submitted_answers=list(context.submitted_answers),
        base_record_id=context.base_record_id,
    )


def _context_evidence(context: IntentContext) -> dict[str, Any]:
    submitted = {answer.question_id: answer for answer in context.submitted_answers}
    return {
        "existing_contract": [
            requirement.model_dump(mode="json")
            for requirement in context.draft.requirements
        ],
        "open_slots": [
            slot.model_dump(mode="json") for slot in context.draft.open_slots
        ],
        "submitted_clarifications": [
            {
                "question_id": question.id,
                "title": question.title,
                "slot_ids": question.slot_ids,
                "answer": submitted[question.id].model_dump(mode="json"),
                "option_catalog": [
                    {"marker": chr(65 + index), **option.model_dump(mode="json")}
                    for index, option in enumerate(question.options)
                ],
            }
            for question in context.questions
            if question.id in submitted
        ],
        "base_record_id": context.base_record_id,
    }


def assess_semantic_intent(
    llm_service: Any,
    *,
    context: IntentContext,
    bindings: dict[str, Any],
    temporal_parse: dict[str, Any],
) -> SemanticAssessmentResult:
    """Return one validated contract draft or frozen contract."""
    evidence = {
        "question": (
            getattr(llm_service, "generation_question", "")
            or getattr(llm_service, "planning_question", "")
        ),
        **_context_evidence(context),
        "deterministic_time_parse": temporal_parse,
        "schema": llm_service.chat_question.db_schema,
        "sample_data": llm_service.chat_question.sample_data,
        "terminology": llm_service.chat_question.terminologies,
        "query_examples": llm_service.chat_question.data_training,
        "custom_rules": llm_service.chat_question.custom_prompt,
        "entity_bindings": bindings,
    }
    target_language = str(getattr(llm_service.chat_question, "lang", "") or "简体中文")
    messages = [
        SystemMessage(
            content=(
                _SYSTEM_PROMPT
                + "\n所有面向用户的文本必须使用当前会话语言："
                + target_language
                + "\n必须符合以下 JSON Schema：\n"
                + _assessment_schema_text()
            )
        ),
        HumanMessage(
            content="请审核以下需求及证据：\n" + orjson.dumps(evidence).decode()
        ),
    ]
    usage_items: list[dict[str, Any]] = []
    reasoning_items: list[str] = []
    attempts: list[dict[str, Any]] = []
    assessment_llm = llm_service.llm.bind(temperature=0)
    for attempt in range(2):
        response = assessment_llm.invoke(messages)
        from apps.conversation.usage import merge_usage, usage_from_response

        usage = usage_from_response(response)
        usage_items.append(usage)
        reasoning = _reasoning_content(response).strip()
        if reasoning:
            reasoning_items.append(reasoning)
        raw_text = message_content_text(response.content)
        try:
            json_text = extract_nested_json(raw_text)
            if not json_text:
                raise ValueError("Cannot parse semantic contract assessment")
            assessment = IntentAssessment.model_validate(orjson.loads(json_text))
            normalized = _normalize_assessment(
                assessment,
                context,
                bindings,
                llm_service.chat_question.db_schema,
                getattr(llm_service, "trans", None),
                temporal_parse,
            )
            attempts.append(
                _attempt_diagnostic(
                    attempt=attempt + 1,
                    raw_text=raw_text,
                    usage=usage,
                    error=None,
                )
            )
            return SemanticAssessmentResult(
                context=normalized,
                usage=merge_usage(*usage_items),
                reasoning="\n".join(reasoning_items),
                attempts=attempts,
            )
        except (TypeError, ValueError) as exc:
            attempts.append(
                _attempt_diagnostic(
                    attempt=attempt + 1,
                    raw_text=raw_text,
                    usage=usage,
                    error=exc,
                )
            )
            if attempt == 1:
                break
            messages = [
                *messages,
                AIMessage(content=raw_text),
                HumanMessage(
                    content=(
                        _REPAIR_PROMPT + "\n校验问题：\n" + _validation_diagnostic(exc)
                    )
                ),
            ]

    from apps.conversation.usage import merge_usage

    raise SemanticAssessmentError(
        "Semantic contract assessment failed validation after repair",
        usage=merge_usage(*usage_items),
        reasoning="\n".join(reasoning_items),
        attempts=attempts,
    )


def assessment_contract_rows(context: IntentContext) -> list[dict[str, str]]:
    """Small observability adapter; not another execution representation."""
    return [
        {"slot_id": requirement.slot_id, "label": label, "value": value}
        for requirement, (label, value) in zip(
            context.draft.requirements,
            contract_display_rows(context.draft),
            strict=True,
        )
    ]
