"""Assess whether an NLQ intent is sufficiently grounded to generate SQL."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any, Literal

import orjson
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from apps.chat.semantic_intent import (
    ClarificationQuestion,
    IntentBinding,
    IntentContext,
    IntentDecision,
    IntentKind,
    IntentIssue,
    IntentOption,
    IntentResolution,
    binding_identifiers,
    render_decision_value,
    time_contract_incomplete,
    validate_binding_requirements,
)
from apps.conversation.messages import message_content_text
from common.utils.json_utils import extract_nested_json


class IntentAssessment(BaseModel):
    intent_mode: Literal["new", "refine"] = "new"
    status: Literal["ready", "needs_clarification", "blocked"]
    summary: str = ""
    resolved_decisions: list[IntentDecision] = Field(default_factory=list)
    issues: list[IntentIssue] = Field(default_factory=list)
    questions: list[ClarificationQuestion] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)


@dataclass(frozen=True)
class SemanticAssessmentResult:
    """Validated semantic terminal plus bounded diagnostics for one graph span."""

    context: IntentContext
    usage: dict[str, Any]
    reasoning: str
    attempts: list[dict[str, Any]]


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
_FORBIDDEN_DISPLAY = "、".join(_FORBIDDEN_USER_FACING_TERMS)


_SYSTEM_PROMPT = """你是数据查询意图审核器。你的任务不是生成 SQL，而是在生成 SQL 前判断查询口径是否已经唯一、完整且有数据库证据支撑。

必须同时检查：
1. 指标定义与计算方式；
2. 维度及其数据库映射；
3. 时间范围、时间粒度及应使用的业务时间字段；
4. 组织、人员、系统、项目等范围过滤的业务归属口径；
5. 多表关联路径、基础数据集合/连接方向、统计主体与去重粒度；
6. 术语、示例、用户已确认决定之间是否冲突；
7. 实体候选是否存在多个可行解释。

多轮对话处理：
- previous_query 为空时 intent_mode 使用 new。
- 当前问题是独立的新查询时使用 new，不继承 previous_query。
- 当前问题是在上一条成功查询上增加、删除、更换或修正口径时使用 refine。未被当前问题影响的旧决定会由系统保留；你只需返回新增、替换或明确删除的决定，以及因此产生的新歧义。
- refine 时沿用稳定 key 覆盖旧决定；明确不再需要的旧输出用相同 key、effect=omit 表达。不得通过省略旧决定来暗中删除用户需求。

规则：
- 先把用户原问题中已经明确表达的指标、字段、聚合、时间、范围、关联、粒度和映射写入 resolved_decisions，再判断剩余歧义；原问题中的明确要求与后续用户锁定决定具有同等约束力，不得换一种说法再次确认。
- resolved_decisions 只保存用户明确表达或术语/规则/schema 能唯一确定的业务契约；纯 inference 不能关闭歧义，不得把仍有多个业务解释的内容伪装成已解决决定。
- SQL 实现细节不是业务歧义：过滤下推到 JOIN 前、FULL JOIN 的方言改写、COALESCE 合并两侧字段、预聚合、别名、排序等由系统自行实现，不得询问用户。
- 用户只确认业务结果，不负责设计数据库实现。多数据来源的技术差异必须翻译成业务影响，例如询问“只要任一类业务有数据是否都展示”“一个业务主体对应多个关联对象时合并一行还是分别展示”，不得询问使用哪张表或如何进行技术关联。
- 面向用户的字段映射采用“业务名称(field_name)”，例如“资产层级(apply_level)”“确权日期(confirm_date)”。字段名用于辅助核对，不能取代业务名称；不要默认展示原始物理表名。只有同名字段来源会改变业务含义时，才使用业务化来源说明。
- 若用户术语与字段业务说明不等价（例如用户所说的“对象层级”与“资产层级(apply_level)”），即使只有一个候选字段也必须确认映射，不能仅凭字段说明推断后直接锁定。
- “汇总金额/金额合计”在没有冲突证据时按 SUM 处理；“名称拼接”默认去重拼接。这类统一规则写入 resolved_decisions，不得阻断查询。
- 用户明确指定关联字段时直接锁定；若配置关系包含更多字段，先由后续 SQL 校验/数据验证处理，不得仅因存在更多可用字段就要求用户重复确认。只有证据表明用户指定方式无法表达唯一业务关系时才提出一个冲突澄清。
- 只对会实质改变结果集或统计值的歧义提问；不要询问格式、排序、图表类型等非关键偏好。
- 一次列出当前证据能发现的全部关键问题，避免逐轮挤牙膏。
- 先形成完整查询契约再提问：指标、时间、维度、过滤、基础数据集合、关联路径、分组粒度、去重方式都必须覆盖。
- 若业务范围、结果粒度和多值展示彼此依赖，应合并为一个业务问题；彼此正交的选择保持独立，避免形成复杂的组合选项矩阵。
- 一个问题可以通过 question.issue_keys 同时解决多个高度相关的 issue；不要生成含义重复或选项等价的问题。
- ready 必须至少包含一项 resolved_decisions 或已有 locked_decisions，不能只给 summary 而不形成可执行契约。
- 每个问题给出 2~3 个互斥、可执行的选项，说明影响；标记推荐项及推荐理由。
- title、reason、description、impact 保持简洁并以业务语言为主，避免重复描述字段结构和已确认决定。
- 推荐只用于标记建议项，不得视为用户已选择或已确认。
- 用户已确认决定是锁定事实，不得再次询问或改写。
- 用户自定义回答属于待解释证据。必须将其归一为具体 resolved_decision 后才能锁定；若仍不唯一，应保留原 issue 并用业务语言继续确认。
- 选项回答与自定义回答严格互斥。自定义回答若提到 A/B/C，应依据 submitted_clarifications.option_catalog 中相同 marker 的选项作为参考，再按用户补充内容形成新的完整口径；不得同时保留该选项与自定义文本后简单拼接。
- 已存在锁定决定时，这是契约一致性复核：所有剩余问题仍须本轮一次给出，优先合并由多个决定共同产生的冲突。
- 只有在现有证据不足以提供可执行选项时才返回 blocked；存在多个合理选项时返回 needs_clarification。
- 没有实质歧义时返回 ready。
- issue.key 和 resolved_decision.key 都是稳定的查询契约槽位，例如 scope.department_basis、metric.amount、relation.business_object.keys；同一语义不得换 key 或拆出同义子 key。
- 一个业务指标只能形成一个 metric decision；金额字段、业务日期和聚合方式必须共同放在该 decision 的 bindings 中。不得再拆分 metric.amount.aggregation 等修饰型 decision。calculation 仅用于比例、差值、代表值等真正的派生计算。
- question.issue_keys 必须引用 issues 中的 key。
- 每个 option.resolutions 必须逐一覆盖 question.issue_keys。每个 resolution 包含用户可理解的 label、具体 value、effect(include|omit) 和结构化 bindings。effect=omit 或确实不产生 SQL 字段约束时 bindings 才可为空。
- 业务时间字段与时间范围是两个独立契约槽位。问题标题若同时询问“按哪个时间、哪段期间”，选项必须同时解决 time.basis 与 time.range；不得在结构化选项描述中要求用户另行补充日期。previous_query 已有时间范围且 intent_mode=refine 时可直接继承，只询问受修改影响的业务时间字段。
- 每个 binding 结构为 {"identifier":"物理字段","role":"group|measure|attribute|filter|join","aggregation":"none|count|count_distinct|sum|avg|min|max|distinct_concat"}。一个字段只承担一个明确角色：统计主体/粒度使用 group，指标值使用 measure，随主体展示的属性使用 attribute，范围和时间条件使用 filter，关系键使用 join。
- measure 必须声明非 none 聚合；group/filter/join 使用 none；attribute 直接展示时使用 none，取代表值使用 min/max，多值去重拼接使用 distinct_concat。不得把指标的业务日期标成 measure，也不得把多个字段共用一个聚合声明。
- effect 必须明确使用 include 或 omit。用户明确选择“不输出”时使用 omit；其余情况使用 include。include 的指标、计算、维度和粒度必须提供 bindings，禁止用空数组掩盖尚未完成的字段映射。
- option.id 和 question.id 在本次响应内唯一，使用简短稳定英文标识。
- 输出严格 JSON，不要使用 Markdown。

JSON 结构：
{
  "intent_mode":"new|refine",
  "status": "ready|needs_clarification|blocked",
  "summary": "已确认口径的简要概述",
  "resolved_decisions": [{"key":"metric.amount","kind":"metric","label":"金额","value":"金额合计","source":"user|rule|terminology|schema","evidence_refs":["question"],"bindings":[{"identifier":"amount","role":"measure","aggregation":"sum"},{"identifier":"business_date","role":"filter","aggregation":"none"}],"effect":"include","locked":true}],
  "issues": [{"key":"...","kind":"scope|metric|dimension|time|filter|relation|grain|calculation|entity|datasource","reason":"...","evidence_refs":["schema"]}],
  "questions": [{
    "id":"...",
    "issue_keys":["..."],
    "kind":"...",
    "title":"...",
    "reason":"为什么需要确认",
    "selection_type":"single|multiple|text",
    "required":true,
    "recommended_option_ids":["..."],
    "recommendation_reason":"...",
    "recommendation_strength":"strong|moderate|weak",
    "options":[{"id":"...","label":"有任一类业务数据就展示","description":"指标 A 或指标 B 任一侧有记录的业务主体都会保留","impact":"可查看完整业务范围，缺少某项指标时对应值为空","evidence_refs":["schema"],"resolutions":{"result.population":{"label":"业务主体范围","value":"两个指标来源的业务主体合集","bindings":[{"identifier":"entity_name","role":"group","aggregation":"none"},{"identifier":"business_date","role":"filter","aggregation":"none"}],"effect":"include"}}}],
    "allow_custom":true,
    "custom_placeholder":"也可以描述你的口径"
  }],
  "blocking_reasons":[]
}"""
_SYSTEM_PROMPT += (
    f"\n- 面向用户的内容禁止出现以下数据库实现术语：{_FORBIDDEN_DISPLAY}。"
)

_REPAIR_PROMPT = """你是查询意图 JSON 契约修复器。请根据校验错误修复候选 JSON，不要重新解释业务需求。
- 只输出修正后的完整 JSON，不要使用 Markdown。
- 不得编造物理字段。缺少可靠字段映射的 resolved_decision 应移回 issues，并提供业务化澄清问题。
- 一个业务指标只保留一个 metric decision；金额字段使用 measure，业务日期使用 filter，聚合写在 measure binding 中。
- calculation 仅用于比例、差值或代表值等派生计算，并必须包含其实际输出字段的 measure binding。
- 保留候选中其他已经完整且不冲突的决定、问题和选项。"""


def _reasoning_content(response: Any) -> str:
    additional = getattr(response, "additional_kwargs", None) or {}
    if isinstance(additional, dict):
        return str(
            additional.get("reasoning_content") or additional.get("reasoning") or ""
        )
    return ""


def _assessment_shape(raw_text: str) -> dict[str, Any]:
    """Return bounded structural diagnostics without persisting full model text."""
    try:
        json_text = extract_nested_json(raw_text)
        payload = orjson.loads(json_text) if json_text else {}
    except (TypeError, ValueError):
        return {}
    if not isinstance(payload, dict):
        return {}

    decisions: list[dict[str, Any]] = []
    for raw in payload.get("resolved_decisions") or []:
        if not isinstance(raw, dict):
            continue
        bindings = [
            {
                "identifier": str(binding.get("identifier") or ""),
                "role": str(binding.get("role") or ""),
                "aggregation": str(binding.get("aggregation") or "none"),
            }
            for binding in raw.get("bindings") or []
            if isinstance(binding, dict)
        ]
        decisions.append(
            {
                "key": str(raw.get("key") or ""),
                "kind": str(raw.get("kind") or ""),
                "bindings": bindings,
            }
        )
    return {
        "status": str(payload.get("status") or ""),
        "decisions": decisions,
        "issue_keys": [
            str(issue.get("key") or "")
            for issue in payload.get("issues") or []
            if isinstance(issue, dict)
        ],
        "question_ids": [
            str(question.get("id") or "")
            for question in payload.get("questions") or []
            if isinstance(question, dict)
        ],
    }


def _attempt_diagnostic(
    *,
    attempt: int,
    raw_text: str,
    usage: dict[str, Any],
    error: Exception | None,
) -> dict[str, Any]:
    diagnostic = {
        "attempt": attempt,
        "valid": error is None,
        "token_usage": usage,
        **_assessment_shape(raw_text),
    }
    if error is not None:
        diagnostic["validation_error"] = str(error)[:1000]
    return diagnostic


def _entity_question_id(phrase: str) -> str:
    digest = hashlib.sha256(phrase.encode("utf-8")).hexdigest()[:12]
    return f"entity_{digest}"


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


def _entity_questions(
    bindings: dict[str, Any],
    trans: Callable[..., str] | None = None,
) -> tuple[list[IntentIssue], list[ClarificationQuestion]]:
    issues: list[IntentIssue] = []
    questions: list[ClarificationQuestion] = []
    for phrase, binding in (bindings.get("ambiguous") or {}).items():
        issue_key = f"entity.{phrase}"
        candidates_by_value: dict[str, dict[str, Any]] = {}
        for candidate in binding.get("options") or []:
            canonical = str(candidate.get("canonical") or "").strip()
            if not canonical:
                continue
            key = canonical.casefold()
            grouped = candidates_by_value.setdefault(
                key,
                {
                    "canonical": canonical,
                    "description": str(candidate.get("description") or "").strip(),
                    "targets": [],
                },
            )
            known_targets = {
                (target.get("table_name"), target.get("field_name"))
                for target in grouped["targets"]
            }
            for target in candidate.get("targets") or []:
                target_key = (target.get("table_name"), target.get("field_name"))
                if all(target_key) and target_key not in known_targets:
                    grouped["targets"].append(target)
                    known_targets.add(target_key)

        options: list[IntentOption] = []
        for index, candidate in enumerate(candidates_by_value.values()):
            canonical = candidate["canonical"]
            targets = [
                f"{target.get('table_name')}.{target.get('field_name')}"
                for target in candidate.get("targets") or []
                if target.get("table_name") and target.get("field_name")
            ]
            field_names = list(
                dict.fromkeys(target.rsplit(".", 1)[-1] for target in targets)
            )
            business_name = str(candidate.get("description") or "").strip()
            if business_name:
                field_names = [
                    (
                        f"{business_name}({field_name})"
                        if business_name.casefold() != field_name.casefold()
                        else field_name
                    )
                    for field_name in field_names
                ]
            options.append(
                IntentOption(
                    id=f"value_{index + 1}",
                    label=canonical,
                    description=(
                        _translated(
                            trans,
                            "i18n_chat.clarification.entity_targets",
                            "业务字段：{targets}",
                            targets="、".join(field_names),
                        )
                        if field_names
                        else ""
                    ),
                    impact=_translated(
                        trans,
                        "i18n_chat.clarification.entity_impact",
                        "查询中将“{phrase}”按“{canonical}”精确过滤",
                        phrase=phrase,
                        canonical=canonical,
                    ),
                    evidence_refs=[f"field:{target}" for target in targets],
                    resolutions={
                        issue_key: IntentResolution(
                            label=phrase,
                            value=canonical,
                            bindings=[
                                IntentBinding(
                                    identifier=target,
                                    role="filter",
                                    aggregation="none",
                                )
                                for target in targets
                            ],
                        )
                    },
                )
            )
        if not options:
            continue
        issues.append(
            IntentIssue(
                key=issue_key,
                kind="entity",
                reason=_translated(
                    trans,
                    "i18n_chat.clarification.entity_issue",
                    "“{phrase}”需要确认具体业务值",
                    phrase=phrase,
                ),
                evidence_refs=[
                    evidence for option in options for evidence in option.evidence_refs
                ],
            )
        )
        questions.append(
            ClarificationQuestion(
                id=_entity_question_id(phrase),
                issue_keys=[issue_key],
                kind="entity",
                title=_translated(
                    trans,
                    "i18n_chat.clarification.entity_title",
                    "“{phrase}”具体指哪个业务值？",
                    phrase=phrase,
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
                options=options,
                custom_placeholder=_translated(
                    trans,
                    "i18n_chat.clarification.entity_custom_placeholder",
                    "输入准确的业务值",
                ),
                binding_phrase=phrase,
            )
        )
    return issues, questions


def _normalize_question(
    question: ClarificationQuestion,
    *,
    issue_keys: list[str],
    issue_kinds: Mapping[str, IntentKind],
) -> ClarificationQuestion:
    deduplicated: list[IntentOption] = []
    option_ids: set[str] = set()
    option_labels: set[str] = set()
    if question.selection_type != "text":
        for option in question.options:
            label_key = option.label.strip().casefold()
            if not option.id or not label_key:
                continue
            if option.id in option_ids or label_key in option_labels:
                continue
            option_ids.add(option.id)
            option_labels.add(label_key)
            missing_resolutions = [
                key for key in issue_keys if key not in option.resolutions
            ]
            if missing_resolutions:
                raise ValueError(
                    f"Clarification option {option.id} does not resolve: "
                    + ", ".join(missing_resolutions)
                )
            for key in issue_keys:
                resolution = option.resolutions[key]
                kind = issue_kinds.get(key, question.kind)
                validate_binding_requirements(
                    kind=kind,
                    effect=resolution.effect,
                    bindings=resolution.bindings,
                    context=f"Clarification resolution {key}",
                )
            if question.kind in {"dimension", "grain"}:
                identifiers = list(
                    dict.fromkeys(
                        identifier.strip().strip("`\"'[]")
                        for resolution in option.resolutions.values()
                        for identifier in binding_identifiers(resolution.bindings)
                        if identifier.strip()
                    )
                )
                if len(identifiers) == 1 and "." not in identifiers[0]:
                    identifier = identifiers[0]
                    business_text = re.sub(
                        r"[\s()（）_\-]|使用|选择|字段",
                        "",
                        option.label.casefold().replace(identifier.casefold(), ""),
                    )
                    if not business_text:
                        raise ValueError(
                            "Dimension option must include a business name before "
                            f"its physical field hint: {identifier}"
                        )
                    if identifier.casefold() not in option.label.casefold():
                        option = option.model_copy(
                            update={"label": f"{option.label}({identifier})"}
                        )
            deduplicated.append(option)
        if not deduplicated:
            raise ValueError(
                f"Clarification question {question.id} requires an option or text input"
            )
        recommended_order = {
            option_id: index
            for index, option_id in enumerate(question.recommended_option_ids)
        }
        original_order = {option.id: index for index, option in enumerate(deduplicated)}
        deduplicated.sort(
            key=lambda option: (
                0 if option.id in recommended_order else 1,
                recommended_order.get(option.id, original_order[option.id]),
                original_order[option.id],
            )
        )
    options = deduplicated[:3]

    available_ids = {option.id for option in options}
    recommended = list(
        dict.fromkeys(
            option_id
            for option_id in question.recommended_option_ids
            if option_id in available_ids
        )
    )
    if question.selection_type == "single":
        recommended = recommended[:1]
    if options and not recommended:
        recommended = [options[0].id]
    visible_text = "\n".join(
        [
            question.title,
            question.reason,
            question.recommendation_reason,
            question.custom_placeholder,
            *(
                text
                for option in options
                for text in (
                    option.label,
                    option.description,
                    option.impact,
                    *(resolution.label for resolution in option.resolutions.values()),
                )
            ),
        ]
    ).casefold()
    forbidden = []
    for term in _FORBIDDEN_USER_FACING_TERMS:
        normalized = term.casefold()
        if (
            re.search(rf"\b{re.escape(normalized)}\b", visible_text)
            if normalized.isascii()
            else normalized in visible_text
        ):
            forbidden.append(term)
    if forbidden:
        raise ValueError(
            "Clarification question exposes database implementation term(s): "
            + ", ".join(forbidden)
        )
    return question.model_copy(
        update={
            "issue_keys": list(dict.fromkeys(issue_keys)),
            "options": options,
            "recommended_option_ids": recommended,
            "required": True,
            "allow_custom": True,
        }
    )


def _normalize_assessment(
    assessment: IntentAssessment,
    context: IntentContext,
    bindings: dict[str, Any],
    time_intent: Mapping[str, Any],
    trans: Callable[..., str] | None = None,
) -> IntentContext:
    current_decisions_by_key = {
        decision.key: decision for decision in context.decisions if decision.key.strip()
    }
    decisions_by_key = (
        {
            decision.key: decision
            for decision in context.base_decisions
            if decision.key.strip()
        }
        if assessment.intent_mode == "refine"
        else {}
    )
    decisions_by_key.update(current_decisions_by_key)
    newly_resolved_keys: set[str] = set()
    assessment_decision_keys: set[str] = set()
    for decision in assessment.resolved_decisions:
        key = decision.key.strip()
        if not key:
            raise ValueError("Resolved decision key cannot be empty")
        if key in assessment_decision_keys:
            raise ValueError(f"Duplicate resolved decision key: {key}")
        assessment_decision_keys.add(key)
        if decision.source == "inference":
            raise ValueError(
                f"Resolved decision {key} cannot rely on an unconfirmed inference"
            )
        if not render_decision_value(decision.value):
            raise ValueError(f"Resolved decision {key} requires a concrete value")
        existing = decisions_by_key.get(key)
        if existing is not None and existing.locked and key in current_decisions_by_key:
            continue
        validate_binding_requirements(
            kind=decision.kind,
            effect=decision.effect,
            bindings=decision.bindings,
            context=f"Resolved decision {key}",
        )
        decisions_by_key[key] = decision.model_copy(
            update={
                "key": key,
                "locked": True,
                "binding_phrase": "",
            }
        )
        newly_resolved_keys.add(key)

    for issue in assessment.issues:
        if issue.key not in current_decisions_by_key:
            decisions_by_key.pop(issue.key, None)
    locked_keys = {key for key, decision in decisions_by_key.items() if decision.locked}
    if any(not issue.key.strip() for issue in assessment.issues):
        raise ValueError("Clarification issue key cannot be empty")
    issue_keys = [issue.key for issue in assessment.issues]
    if len(issue_keys) != len(set(issue_keys)):
        raise ValueError("Duplicate clarification issue key")
    overlap = newly_resolved_keys & {issue.key for issue in assessment.issues}
    if overlap:
        raise ValueError(
            "A contract slot cannot be both resolved and ambiguous: "
            + ", ".join(sorted(overlap))
        )
    issues_by_key = {
        issue.key: issue for issue in assessment.issues if issue.key not in locked_keys
    }
    questions: list[ClarificationQuestion] = []
    known_question_ids: set[str] = set()
    covered_issue_keys: set[str] = set()
    entity_issues, entity_questions = _entity_questions(bindings, trans)
    for issue in entity_issues:
        if issue.key not in locked_keys:
            issues_by_key[issue.key] = issue

    deterministic_entity_ids = {question.id for question in entity_questions}
    for question in [*entity_questions, *assessment.questions]:
        if not question.id.strip():
            raise ValueError("Clarification question id cannot be empty")
        if question.id in known_question_ids:
            raise ValueError(f"Duplicate clarification question id: {question.id}")
        known_question_ids.add(question.id)
        issue_keys = [
            key
            for key in question.issue_keys
            if key in issues_by_key and key not in locked_keys
        ]
        if not issue_keys or all(key in covered_issue_keys for key in issue_keys):
            continue
        normalized = _normalize_question(
            (
                question
                if question.id in deterministic_entity_ids
                else question.model_copy(update={"binding_phrase": ""})
            ),
            issue_keys=issue_keys,
            issue_kinds={
                key: issues_by_key[key].kind
                for key in issue_keys
                if key in issues_by_key
            },
        )
        questions.append(normalized)
        covered_issue_keys.update(issue_keys)

    uncovered = [key for key in issues_by_key if key not in covered_issue_keys]
    if uncovered and assessment.status != "blocked":
        raise ValueError(
            "Clarification assessment omitted options for issue(s): "
            + ", ".join(uncovered)
        )

    blocking_reasons = list(dict.fromkeys(assessment.blocking_reasons))
    if questions:
        status: Literal["needs_clarification", "ready", "blocked"] = (
            "needs_clarification"
        )
    elif blocking_reasons or assessment.status == "blocked":
        status = "blocked"
    else:
        status = "ready"
    if status == "ready" and any(
        not decision.locked for decision in decisions_by_key.values()
    ):
        raise ValueError(
            "A ready semantic assessment cannot retain provisional user answers"
        )
    if status == "ready" and not locked_keys:
        raise ValueError(
            "A ready semantic assessment requires at least one resolved contract decision"
        )
    if status == "ready" and time_contract_incomplete(
        list(decisions_by_key.values()),
        time_intent,
    ):
        raise ValueError("A business-time filter requires a structured time range")
    if (
        assessment.intent_mode == "refine"
        and context.base_decisions
        and not assessment.resolved_decisions
        and not assessment.issues
    ):
        raise ValueError("A refinement must change or question the previous contract")
    if status == "blocked" and not blocking_reasons:
        blocking_reasons = list(
            dict.fromkeys(
                [
                    assessment.summary.strip(),
                    *(issue.reason.strip() for issue in issues_by_key.values()),
                ]
            )
        )
        blocking_reasons = [reason for reason in blocking_reasons if reason]
        if not blocking_reasons:
            blocking_reasons = ["现有证据不足以形成可执行的查询口径"]
    if status == "ready":
        from apps.chat.query_contract import compile_query_contract

        compile_query_contract(
            [decision.model_dump(mode="json") for decision in decisions_by_key.values()],
            time_intent=time_intent or None,
        )

    return IntentContext(
        version=context.version,
        status=status,
        original_question=context.original_question,
        summary=assessment.summary,
        decisions=list(decisions_by_key.values()),
        issues=list(issues_by_key.values()) if status != "ready" else [],
        questions=questions if status == "needs_clarification" else [],
        blocking_reasons=blocking_reasons if status == "blocked" else [],
        time_intent=dict(time_intent),
        submitted_answers=list(context.submitted_answers),
    )


def assess_semantic_intent(
    llm_service: Any,
    *,
    context: IntentContext,
    bindings: dict[str, Any],
    time_intent: dict[str, Any],
) -> SemanticAssessmentResult:
    """Return the validated semantic gate result, provider usage and reasoning."""
    submitted_answers = {
        answer.question_id: answer for answer in context.submitted_answers
    }
    evidence = {
        "question": (
            getattr(llm_service, "generation_question", "")
            or getattr(llm_service, "planning_question", "")
        ),
        "locked_decisions": [
            {
                "key": decision.key,
                "kind": decision.kind,
                "definition": decision.label,
                "selection": render_decision_value(decision.value),
                "source": decision.source,
                "bindings": [
                    binding.model_dump(mode="json") for binding in decision.bindings
                ],
            }
            for decision in context.decisions
            if decision.locked
        ],
        "provisional_decisions": [
            {
                "key": decision.key,
                "kind": decision.kind,
                "definition": decision.label,
                "user_answer": render_decision_value(decision.value),
                "bindings": [
                    binding.model_dump(mode="json") for binding in decision.bindings
                ],
                "effect": decision.effect,
            }
            for decision in context.decisions
            if not decision.locked
        ],
        "submitted_clarifications": [
            {
                "question_id": question.id,
                "title": question.title,
                "issue_keys": question.issue_keys,
                "answer": submitted_answers[question.id].model_dump(mode="json"),
                "option_catalog": [
                    {
                        "marker": chr(65 + index),
                        **option.model_dump(mode="json"),
                    }
                    for index, option in enumerate(question.options)
                ],
            }
            for question in context.questions
            if question.id in submitted_answers
        ],
        "previous_summary": context.summary,
        "previous_query": (
            {
                "record_id": context.base_record_id,
                "decisions": [
                    decision.model_dump(mode="json")
                    for decision in context.base_decisions
                    if decision.locked
                ],
                "time_intent": context.base_time_intent,
            }
            if context.base_record_id is not None
            else None
        ),
        "schema": llm_service.chat_question.db_schema,
        "sample_data": llm_service.chat_question.sample_data,
        "terminology": llm_service.chat_question.terminologies,
        "query_examples": llm_service.chat_question.data_training,
        "custom_rules": llm_service.chat_question.custom_prompt,
        "time_intent": time_intent,
        "entity_bindings": bindings,
    }
    target_language = str(getattr(llm_service.chat_question, "lang", "") or "简体中文")
    messages = [
        SystemMessage(
            content=(
                _SYSTEM_PROMPT
                + f"\n- 所有面向用户的 summary、reason、title、description、impact "
                f"必须使用当前会话语言：{target_language}。"
            )
        ),
        HumanMessage(
            content=("请审核以下查询意图及证据：\n" + orjson.dumps(evidence).decode())
        ),
    ]
    usage_items: list[dict[str, Any]] = []
    reasoning_items: list[str] = []
    attempts: list[dict[str, Any]] = []
    for attempt in range(2):
        response = llm_service.llm.invoke(messages)
        from apps.conversation.usage import merge_usage, usage_from_response

        usage_items.append(usage_from_response(response))
        reasoning = _reasoning_content(response).strip()
        if reasoning:
            reasoning_items.append(reasoning)
        raw_text = message_content_text(response.content)
        try:
            json_text = extract_nested_json(raw_text)
            if not json_text:
                raise ValueError("Cannot parse semantic clarification assessment")
            assessment = IntentAssessment.model_validate(orjson.loads(json_text))
            effective_time_intent = dict(
                time_intent
                or (
                    context.base_time_intent
                    if assessment.intent_mode == "refine"
                    else {}
                )
            )
            normalized = _normalize_assessment(
                assessment,
                context,
                bindings,
                effective_time_intent,
                getattr(llm_service, "trans", None),
            )
            if (
                assessment.status == "needs_clarification"
                and normalized.status == "ready"
            ):
                raise ValueError("Clarification assessment omitted required questions")
            attempts.append(
                _attempt_diagnostic(
                    attempt=attempt + 1,
                    raw_text=raw_text,
                    usage=usage_items[-1],
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
                    usage=usage_items[-1],
                    error=exc,
                )
            )
            if attempt == 1:
                break
            messages = [
                SystemMessage(content=_REPAIR_PROMPT),
                HumanMessage(
                    content=(
                        "候选 JSON：\n"
                        f"{raw_text}\n\n"
                        "校验错误：\n"
                        f"{exc}\n\n"
                        "请返回修正后的完整 JSON。"
                    )
                ),
            ]

    trans = getattr(llm_service, "trans", None)
    blocked_reason = _translated(
        trans,
        "i18n_chat.clarification.assessment_unavailable",
        "暂时未能可靠完成业务口径识别，请重试。",
    )
    blocked_context = context.model_copy(
        update={
            "status": "blocked",
            "summary": blocked_reason,
            "issues": [],
            "questions": [],
            "blocking_reasons": [blocked_reason],
        }
    )
    return SemanticAssessmentResult(
        context=blocked_context,
        usage=merge_usage(*usage_items),
        reasoning="\n".join(reasoning_items),
        attempts=attempts,
    )
