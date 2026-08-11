"""One-call semantic planner producing either clarification or executable plans."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import orjson
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from pydantic import ValidationError

from apps.chat.planning import BatchParseResult, parse_query_generation
from apps.chat.query_specification import (
    QueryAssumption,
    QuerySpecification,
    normalize_specification,
)
from apps.chat.semantic_planning import (
    PLANNING_DECISION_ADAPTER,
    NeedClarification,
    PlanningDecision,
    enforce_clarification_policy,
)
from apps.chat.specification_validation import (
    blocking_issues,
    validate_specification,
    validate_specification_transition,
)
from apps.chat.steps.knowledge_seed import (
    KnowledgeApplication,
    KnowledgeSeed,
    apply_knowledge_seeds,
)
from apps.conversation.messages import message_content_text
from apps.conversation.models import NlqEvidenceEvent
from apps.conversation.usage import merge_usage, usage_from_response
from apps.knowledge.compile.bundle import ApplyHit
from common.utils.json_utils import extract_nested_json


@dataclass(frozen=True)
class SemanticPlanningResult:
    decision: PlanningDecision
    parsed_plans: BatchParseResult | None
    usage: dict[str, Any]
    reasoning: str
    attempts: list[dict[str, Any]]
    knowledge_apply: list[ApplyHit]


@dataclass(frozen=True)
class PhysicalPlanningResult:
    parsed_plans: BatchParseResult
    usage: dict[str, Any]
    reasoning: str
    raw_text: str


_SYSTEM_PROMPT = """你是 AI 智能问数的业务语义规划器和物理查询计划生成器。

你必须只返回 JSON，且严格符合给出的 PlanningDecision schema。

唯一真相规则：
- 用户问题、澄清回答和纠正是不可变证据；不得改写或忽略。
- QuerySpecification 是唯一业务语义真相；查询候选只负责实现它。
- 有任何会显著改变金额、数量、数据归属、时间范围、结果人口或去重粒度的未决业务歧义时，只返回 needs_clarification，不得同时返回候选查询。
- 非关键展示选择可转成 assumptions，不阻塞执行。
- 不询问 JOIN、表名、关联键、CTE、方言、排序实现等技术问题。
- schema 只能证明字段、类型和关系存在，不能自行创造业务过滤政策。
- protected_knowledge_requirements 是当前问题强相关的认证业务口径；除非用户当前证据明确覆盖，不得遗漏、改写或重复询问已解决的口径。
- business_rules 是工作空间管理员发布的业务规则约束；生成查询时必须遵守，不得忽略或违反。
- query_examples 只是字段映射、方言和物理查询实现参考；不得用它代替用户回答业务歧义，也不得覆盖用户证据或认证口径。
- 推荐项只作说明，不代表用户已选择。
- 每轮最多两个高度相关且必要的问题；每题 2~3 个互斥选项。
- 面向用户的文字使用业务语言；必要时写“业务名称(field_name)”，不展示表名或连接路径。
- 每个歧义必须给出稳定、简短、与问句措辞无关的 business_axis（例如 department_scope）；已经存在 user clarification evidence 的 business_axis 不得再次询问。
- 每个候选项的 resolution 必须包含该业务选择的结构化含义，不能是空对象。
- clarification_budget_exhausted=true 时不得继续提问；在仍可安全查询时采用最合理口径并明确写入 assumptions。

规格规则：
- requirement_id 是临时标识，服务端会重新分配；引用必须在本响应内一致。
- 每个 requirement 只表达一种 clause。
- source=user 时 evidence_refs 必须引用 user:question 或 user:answer:<evidence_id>。
- 明细和聚合都使用 outputs；明细字段 aggregation=value，聚合字段使用对应聚合方式。
- 最新 N 条是 order_by + limit，不自动创建时间窗口。
- 不输出字段不等于过滤数据。
- 用户未要求的返回行上限不写入 specification.limit。
- 多事实共享粒度时 business_relations 的 population 是业务范围；若其不同选择会明显改变结果，必须澄清。
- candidates.payload 必须是目标协议原生查询 JSON，不要放 Markdown。
- candidates 必须逐条完整实现 specification，不得增删业务条件。
"""


_REPAIR_PROMPT = """上一响应未通过结构、字段或计划一致性校验。只修复所列问题：
- 不得改变已引用用户证据的业务含义；
- 规格问题修正规格，物理计划问题只修候选 payload；
- 如果无法确认关键业务语义，改为 needs_clarification；
- 返回完整 PlanningDecision JSON。
"""

_PHYSICAL_REPAIR_PROMPT = """你是 AI 智能问数的物理查询计划修复器。

QuerySpecification 是不可修改的唯一业务语义。你只能修复 SQL 或 REST 请求的物理实现：
- 不得新增、删除或改变任何业务 clause、过滤值、时间范围、聚合、粒度、排序或 limit；
- 只能使用给定 schema 中真实存在的表和字段；
- 遵守目标协议和方言规则；
- 返回协议原生查询 JSON 对象或数组，不要 Markdown，不要解释；
- 无法完整实现时仍返回最安全、最接近规格的候选，由验证器决定是否可降级执行。
"""


# A turn may clarify several related business decisions, but it must not be
# trapped indefinitely by renamed or progressively fragmented questions.
_MAX_RESOLVED_AMBIGUITIES = 4


def _reasoning(response: Any) -> str:
    extra = getattr(response, "additional_kwargs", None) or {}
    return (
        str(extra.get("reasoning_content") or extra.get("reasoning") or "")
        if isinstance(extra, dict)
        else ""
    )


def _evidence_payload(events: list[NlqEvidenceEvent]) -> list[dict[str, Any]]:
    def reference(event: NlqEvidenceEvent) -> str:
        if event.kind == "user_question":
            return "user:question"
        if event.source == "user":
            return f"user:answer:{event.evidence_id}"
        return f"{event.source}:{event.evidence_id}"

    return [
        {
            "evidence_id": event.evidence_id,
            "reference": reference(event),
            "kind": event.kind,
            "source": event.source,
            "content": event.content,
            "structured_value": event.structured_value,
            "confidence": event.confidence,
            "supersedes": event.supersedes,
        }
        for event in events
    ]


def _evidence_references(events: list[NlqEvidenceEvent]) -> set[str]:
    return {str(item["reference"]) for item in _evidence_payload(events)}


def _protocol_context(llm_service: Any) -> dict[str, Any]:
    bundle = llm_service.protocol.build_prompt_bundle(
        llm_service.chat_question,
        enable_query_limit=llm_service.enable_sql_row_limit,
    ).as_dict()
    return {
        "protocol_type": getattr(llm_service.protocol, "type_key", ""),
        "protocol_generation_rules": {
            key: bundle.get(key, "")
            for key in ("system", "rules", "custom_prompt")
            if bundle.get(key)
        },
    }


def plan_semantics_and_query(
    llm_service: Any,
    *,
    evidence: list[NlqEvidenceEvent],
    previous_specification: QuerySpecification | None,
    entity_bindings: dict[str, Any],
    temporal_parse: dict[str, Any],
    max_batch_size: int,
    knowledge_seeds: list[KnowledgeSeed] | None = None,
    business_rules: list[dict[str, Any]] | None = None,
) -> SemanticPlanningResult:
    """Return one validated decision; initial ready planning is one model call."""
    resolved_ambiguities = {
        str((event.structured_value or {}).get("ambiguity_id") or "")
        for event in evidence
        if event.kind
        in {"clarification_option", "clarification_custom", "user_correction"}
    }
    resolved_business_axes = {
        str((event.structured_value or {}).get("business_axis") or "")
        for event in evidence
        if event.kind
        in {"clarification_option", "clarification_custom", "user_correction"}
    }
    clarification_budget_exhausted = (
        len({item for item in resolved_ambiguities if item})
        >= _MAX_RESOLVED_AMBIGUITIES
    )
    protected_knowledge = list(knowledge_seeds or [])
    context = {
        "evidence": _evidence_payload(evidence),
        "resolved_ambiguity_ids": sorted(item for item in resolved_ambiguities if item),
        "resolved_business_axes": sorted(
            item for item in resolved_business_axes if item
        ),
        "clarification_budget_exhausted": clarification_budget_exhausted,
        "previous_specification": previous_specification.model_dump(mode="json")
        if previous_specification
        else None,
        "schema": llm_service.chat_question.db_schema,
        "sample_data": llm_service.chat_question.sample_data,
        "terminology": llm_service.chat_question.terminologies,
        "query_examples": llm_service.chat_question.data_training,
        "protected_knowledge_requirements": [
            seed.as_prompt_context() for seed in protected_knowledge
        ],
        "business_rules": [
            {"label": r.get("label", ""), "content": r.get("content", "")}
            for r in (business_rules or [])
        ],
        "custom_rules": llm_service.chat_question.custom_prompt,
        "entity_bindings": entity_bindings,
        "deterministic_time_parse": temporal_parse,
        **_protocol_context(llm_service),
    }
    schema = orjson.dumps(PLANNING_DECISION_ADAPTER.json_schema()).decode()
    messages: list[Any] = [
        SystemMessage(content=_SYSTEM_PROMPT + "\nJSON Schema:\n" + schema),
        HumanMessage(content=orjson.dumps(context).decode()),
    ]
    usage_items: list[dict[str, Any]] = []
    reasoning_items: list[str] = []
    attempts: list[dict[str, Any]] = []
    planner = llm_service.llm.bind(temperature=0)
    last_error = ""
    for attempt in range(2):
        response = planner.invoke(messages)
        usage_items.append(usage_from_response(response))
        if text := _reasoning(response).strip():
            reasoning_items.append(text)
        raw = message_content_text(response.content)
        try:
            nested = extract_nested_json(raw)
            if not nested:
                raise ValueError("Planner response is not JSON")
            decision = PLANNING_DECISION_ADAPTER.validate_python(orjson.loads(nested))
            if isinstance(decision, NeedClarification):
                if clarification_budget_exhausted:
                    raise ValueError(
                        "Clarification budget is exhausted. Produce a Ready decision "
                        "using explicit, disclosed assumptions when execution remains safe."
                    )
                enforce_clarification_policy(
                    decision.ambiguity_set,
                    resolved_business_axes=resolved_business_axes,
                )
                repeated = {
                    item.ambiguity_id for item in decision.ambiguity_set.ambiguities
                } & resolved_ambiguities
                if repeated:
                    raise ValueError(
                        "Planner repeated resolved ambiguities: "
                        + ", ".join(sorted(repeated))
                    )
                repeated_axes = {
                    item.business_axis for item in decision.ambiguity_set.ambiguities
                } & resolved_business_axes
                if repeated_axes:
                    raise ValueError(
                        "Planner repeated resolved business axes: "
                        + ", ".join(sorted(repeated_axes))
                    )
                attempts.append({"attempt": attempt + 1, "decision": decision.decision})
                return SemanticPlanningResult(
                    decision=decision,
                    parsed_plans=None,
                    usage=merge_usage(*usage_items),
                    reasoning="\n".join(reasoning_items),
                    attempts=attempts,
                    knowledge_apply=[],
                )
            normalized = decision.model_copy(
                update={
                    "specification": normalize_specification(decision.specification)
                }
            )
            knowledge_application = apply_knowledge_seeds(
                normalized.specification,
                protected_knowledge,
            )
            if knowledge_application.missing:
                if attempt == 0:
                    raise ValueError(
                        "Planner omitted protected certified knowledge requirements: "
                        + ", ".join(knowledge_application.missing)
                    )
                omitted_ids = {
                    int(item.split(":", 1)[0]) for item in knowledge_application.missing
                }
                omitted_seeds = [
                    seed
                    for seed in protected_knowledge
                    if seed.caliber_id in omitted_ids
                ]
                assumptions = list(knowledge_application.specification.assumptions)
                assumptions.extend(
                    QueryAssumption(
                        assumption_id=f"knowledge_seed_{seed.caliber_id}_omitted",
                        business_label=f"认证口径未完整应用：{seed.label}",
                        value="未应用",
                        reason="语义规划修复后仍无法完整吸收该认证口径",
                        risk="high",
                        evidence_refs=(seed.evidence_ref,),
                    )
                    for seed in omitted_seeds
                    if not any(
                        item.assumption_id
                        == f"knowledge_seed_{seed.caliber_id}_omitted"
                        for item in assumptions
                    )
                )
                knowledge_application = KnowledgeApplication(
                    specification=knowledge_application.specification.model_copy(
                        update={"assumptions": tuple(assumptions)}
                    ),
                    apply_log=(
                        *knowledge_application.apply_log,
                        *(
                            ApplyHit(
                                asset_kind="caliber",
                                asset_id=seed.caliber_id,
                                lineage_id=seed.lineage_id,
                                trust_tier=seed.trust_tier,
                                apply="drop",
                                reason="planner_omitted_after_repair",
                                meta={"label": seed.label},
                            )
                            for seed in omitted_seeds
                        ),
                    ),
                    missing=(),
                )
            normalized = normalized.model_copy(
                update={"specification": knowledge_application.specification}
            )
            issues = validate_specification(
                normalized.specification,
                schema_text=str(llm_service.chat_question.db_schema or ""),
                available_evidence_refs=_evidence_references(evidence),
            )
            issues.extend(
                validate_specification_transition(
                    previous_specification,
                    normalized.specification,
                    active_evidence_refs=_evidence_references(evidence),
                )
            )
            blockers = blocking_issues(issues)
            if blockers:
                raise ValueError(
                    "Specification validation failed: "
                    + "; ".join(
                        f"{item.code}:{','.join(item.fields)}" for item in blockers
                    )
                )
            raw_candidates = orjson.dumps(
                [candidate.payload for candidate in normalized.candidates]
            ).decode()
            parsed = parse_query_generation(
                raw_candidates,
                llm_service,
                max_batch_size=max_batch_size,
                specification=normalized.specification,
            )
            if parsed.plans and len(parsed.plans) == len(normalized.candidates):
                for candidate, plan in zip(
                    normalized.candidates, parsed.plans, strict=True
                ):
                    plan["plan_id"] = candidate.plan_id
            attempts.append(
                {
                    "attempt": attempt + 1,
                    "decision": normalized.decision,
                    "physical_plan_status": (
                        "valid"
                        if parsed.success and not parsed.requires_contract_repair
                        else "needs_repair"
                    ),
                    "physical_plan_error": parsed.error_message
                    or parsed.contract_message,
                }
            )
            return SemanticPlanningResult(
                decision=normalized,
                parsed_plans=parsed,
                usage=merge_usage(*usage_items),
                reasoning="\n".join(reasoning_items),
                attempts=attempts,
                knowledge_apply=list(knowledge_application.apply_log),
            )
        except (TypeError, ValueError, ValidationError) as exc:
            last_error = str(exc)
            attempts.append({"attempt": attempt + 1, "error": last_error})
            if attempt == 0:
                messages.extend(
                    [
                        AIMessage(content=raw),
                        HumanMessage(
                            content=_REPAIR_PROMPT + "\n校验问题：" + last_error
                        ),
                    ]
                )
    raise ValueError("Semantic planning failed: " + last_error)


def repair_physical_query_plan(
    llm_service: Any,
    *,
    specification: QuerySpecification,
    previous_plans: list[dict[str, Any]],
    validation_error: str,
    max_batch_size: int,
) -> PhysicalPlanningResult:
    """Repair only a physical plan while keeping one specification revision."""
    context = {
        "query_specification": specification.model_dump(mode="json"),
        "schema": llm_service.chat_question.db_schema,
        "previous_plans": previous_plans,
        "validation_error": validation_error,
        **_protocol_context(llm_service),
    }
    response = llm_service.llm.bind(temperature=0).invoke(
        [
            SystemMessage(content=_PHYSICAL_REPAIR_PROMPT),
            HumanMessage(content=orjson.dumps(context).decode()),
        ]
    )
    raw = message_content_text(response.content)
    parsed = parse_query_generation(
        raw,
        llm_service,
        max_batch_size=max_batch_size,
        specification=specification,
    )
    return PhysicalPlanningResult(
        parsed_plans=parsed,
        usage=usage_from_response(response),
        reasoning=_reasoning(response),
        raw_text=raw,
    )
