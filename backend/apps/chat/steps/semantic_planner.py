"""One-call semantic planner producing either clarification or executable plans."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from time import monotonic
from typing import TYPE_CHECKING, Any

import orjson
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from pydantic import ValidationError

from apps.chat.planning import BatchParseResult, parse_query_generation
from apps.chat.planning_prompt import protocol_prompt_bits, render_planner_input
from apps.chat.query_specification import (
    QuerySpecification,
    canonicalize_planner_requirement_ids,
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
from apps.chat.steps.knowledge_seed import KnowledgeSeed, apply_knowledge_seeds
from apps.chat.steps.stream import consume_llm
from apps.conversation.messages import message_content_text
from apps.conversation.models import NlqEvidenceEvent
from apps.conversation.usage import merge_usage
from apps.knowledge.compile.bundle import ApplyHit
from common.utils.json_utils import extract_nested_json

if TYPE_CHECKING:
    from apps.chat.steps.observability import AuditSpanHandle


@dataclass(frozen=True)
class SemanticPlanningResult:
    decision: PlanningDecision
    parsed_plans: BatchParseResult | None
    usage: dict[str, Any]
    reasoning: str
    attempts: list[dict[str, Any]]
    knowledge_apply: list[ApplyHit]
    model_messages: list[Any]


@dataclass(frozen=True)
class PhysicalPlanningResult:
    parsed_plans: BatchParseResult
    usage: dict[str, Any]
    reasoning: str
    raw_text: str
    model_messages: list[Any]


class SemanticPlanningError(ValueError):
    """The planner remained structurally invalid after bounded repair."""

    def __init__(
        self,
        message: str,
        *,
        usage: dict[str, Any],
        reasoning: str,
        attempts: list[dict[str, Any]],
        model_messages: list[Any],
    ) -> None:
        super().__init__(message)
        self.usage = usage
        self.reasoning = reasoning
        self.attempts = attempts
        self.model_messages = model_messages


_SYSTEM_PROMPT = """你是 AI 智能问数的业务语义规划器和物理查询计划生成器。

只返回一个 JSON 对象，不要 Markdown，不要解释。decision 只能是 needs_clarification 或 ready。

唯一真相：
- 当前问题、澄清回答、纠正和 conversation_history 中的先前用户问题都是不可变证据，不得改写或忽略。
- 同一会话默认延续：不得把「继续」或短续问当成全新独立问题；必须继承 previous_specification 与已确认口径，除非本轮明确开始全新分析。
- QuerySpecification 是唯一业务语义真相；查询候选只负责实现它。
- 有会显著改变金额、数量、数据归属、时间范围、结果人口或去重粒度的未决业务歧义时，只返回 needs_clarification，不得同时返回候选查询。
- 非关键展示选择写成 assumptions，不阻塞执行。
- 不询问 JOIN、表名、关联键、CTE、方言、排序实现等技术问题。
- schema 只能证明字段存在，不能创造业务过滤政策。
- 选项必须能映射到当前 schema/认证知识中的具体字段、值、聚合或粒度。
- 「主要」「默认」等没有明确字段或规则的选项不可执行。
- protected_knowledge_requirements 与 business_rules 必须遵守。
- query_examples 只是实现参考，不能代替用户回答。
- 每轮最多两个必要问题，每题 2~3 个互斥选项；同一指标组/主体/时间尽量本轮合并。
- 已在 resolved_business_axes 中的轴不得再问。澄清预算只约束本轮新问题。
- 面向用户的文字用业务语言，必要时写「业务名称(field_name)」。
- 候选项只要 label；不要 description、impact、reason、recommendation_reason、summary。
- 每个 resolution 必须是可执行的结构化含义，不能是空对象或 primary/auto/default。
- clarification_budget_exhausted=true 时不得继续提问。

规格：
- requirement_id 仅在本响应内一致；每个 requirement 一种 clause。
- source=user 时 evidence_refs 必须引用 user:question、user:prior_question、user:answer:<id> 或 user:prior_answer:<id>。
- 明细 aggregation=value；最新 N 条用 order_by+limit，不自动建时间窗口。
- 用户未要求的行上限不写入 specification.limit。
- candidates.payload 是协议原生查询 JSON。

输出形状：
{"decision":"needs_clarification","ambiguity_set":{"ambiguities":[{"business_axis":"amount_metric","business_question":"...","candidate_resolutions":[{"label":"...","resolution":{"field":"orig_asset_amt","date_field":"sign_date"}},{"label":"...","resolution":{}}]}]}}
或
{"decision":"ready","specification":{"version":3,"revision":1,"outputs":[],"predicates":[],"group_by":[],"time_windows":[],"order_by":[],"limit":null,"business_relations":[],"assumptions":[],"evidence_refs":[],"confidence":0.7},"candidates":[{"payload":{"sql":"SELECT ..."}}],"summary":""}
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


# A turn may clarify related decisions, but it must not progressively invent
# more policy after each answer. The UI already supports two related questions
# in one card; a second card is allowed only when the first card contained one
# decision. Any remaining uncertainty becomes a disclosed assumption.
_MAX_RESOLVED_BUSINESS_AXES = 2


def _history_evidence(history: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for index, turn in enumerate(history):
        question = str(turn.get("question") or "").strip()
        if question:
            items.append(
                {
                    "evidence_id": f"history-q-{index}",
                    "reference": f"user:prior_question:{index}",
                    "kind": "prior_user_question",
                    "source": "user",
                    "content": question,
                    "structured_value": {
                        "status": turn.get("status"),
                        "has_specification": bool(turn.get("has_specification")),
                    },
                    "confidence": 1.0,
                    "supersedes": None,
                }
            )
        for option_index, clarification in enumerate(turn.get("clarifications") or []):
            if not isinstance(clarification, dict):
                continue
            content = str(clarification.get("content") or "").strip()
            if not content:
                continue
            items.append(
                {
                    "evidence_id": f"history-a-{index}-{option_index}",
                    "reference": f"user:prior_answer:{index}-{option_index}",
                    "kind": "prior_clarification",
                    "source": "user",
                    "content": content,
                    "structured_value": {
                        "business_axis": clarification.get("business_axis") or "",
                        "resolution": clarification.get("resolution"),
                    },
                    "confidence": 1.0,
                    "supersedes": None,
                }
            )
    return items


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


def _evidence_references(
    events: list[NlqEvidenceEvent],
    extra: list[dict[str, Any]] | None = None,
) -> set[str]:
    refs = {str(item["reference"]) for item in _evidence_payload(events)}
    for item in extra or []:
        ref = item.get("reference")
        if ref:
            refs.add(str(ref))
    return refs


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
    conversation_history: list[dict[str, Any]] | None = None,
    inherited_business_axes: set[str] | None = None,
    audit_span: AuditSpanHandle | None = None,
    on_stream: Callable[[dict[str, str]], None] | None = None,
) -> SemanticPlanningResult:
    """Return one validated decision; initial ready planning is one model call."""
    this_run_axes = {
        str((event.structured_value or {}).get("business_axis") or "")
        for event in evidence
        if event.kind
        in {"clarification_option", "clarification_custom", "user_correction"}
    }
    this_run_axes.discard("")
    inherited_axes = {
        item.strip() for item in (inherited_business_axes or set()) if item.strip()
    }
    resolved_ambiguities = {
        str((event.structured_value or {}).get("ambiguity_id") or "")
        for event in evidence
        if event.kind
        in {"clarification_option", "clarification_custom", "user_correction"}
    }
    resolved_business_axes = this_run_axes | inherited_axes
    remaining_question_budget = max(
        0, _MAX_RESOLVED_BUSINESS_AXES - len(this_run_axes)
    )
    clarification_budget_exhausted = remaining_question_budget == 0
    protected_knowledge = list(knowledge_seeds or [])
    history_evidence = _history_evidence(list(conversation_history or []))
    unresolved_business_axes = (
        "metric definitions, business subject/population, grouping level, "
        "time field/range, status scope, and zero-data retention"
    )
    question = llm_service.chat_question
    human_content = render_planner_input(
        schema=str(question.db_schema or ""),
        sample_data=str(question.sample_data or ""),
        terminology=str(question.terminologies or ""),
        query_examples=str(question.data_training or ""),
        custom_rules=str(question.custom_prompt or ""),
        protocol=protocol_prompt_bits(llm_service),
        structured={
            "evidence": [*history_evidence, *_evidence_payload(evidence)],
            "conversation_history": list(conversation_history or []),
            "resolved_ambiguity_ids": sorted(
                item for item in resolved_ambiguities if item
            ),
            "resolved_business_axes": sorted(resolved_business_axes),
            "clarification_budget_exhausted": clarification_budget_exhausted,
            "clarification_policy": {
                "inspect_axes_before_asking": unresolved_business_axes,
                "max_questions_this_round": remaining_question_budget,
                "merge_related_axes": True,
            },
            "previous_specification": (
                previous_specification.model_dump(mode="json")
                if previous_specification
                else None
            ),
            "protected_knowledge_requirements": [
                seed.as_prompt_context() for seed in protected_knowledge
            ],
            "business_rules": [
                {"label": r.get("label", ""), "content": r.get("content", "")}
                for r in (business_rules or [])
            ],
            "entity_bindings": entity_bindings,
            "deterministic_time_parse": temporal_parse,
        },
    )
    messages: list[Any] = [
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=human_content),
    ]
    if audit_span is not None:
        audit_span.set_input_messages(messages)
        audit_span.persist_progress()
    usage_items: list[dict[str, Any]] = []
    reasoning_items: list[str] = []
    attempts: list[dict[str, Any]] = []
    planner = llm_service.llm.bind(temperature=0)
    last_error = ""
    available_refs = _evidence_references(evidence, history_evidence)
    for attempt in range(2):
        streamed_content: list[str] = []
        streamed_reasoning: list[str] = []
        last_persist = 0.0

        def _on_chunk(
            chunk: dict[str, str],
            *,
            content_parts: list[str] = streamed_content,
            reasoning_parts: list[str] = streamed_reasoning,
        ) -> None:
            nonlocal last_persist
            content = chunk.get("content") or ""
            reasoning = chunk.get("reasoning_content") or ""
            if content:
                content_parts.append(content)
            if reasoning:
                reasoning_parts.append(reasoning)
                if on_stream is not None:
                    on_stream({"content": "", "reasoning_content": reasoning})
            if audit_span is None:
                return
            now = monotonic()
            if now - last_persist < 2.0:
                return
            last_persist = now
            assembled = "".join(content_parts)
            thought = "".join(reasoning_parts)
            if assembled:
                audit_span.set_output_message(AIMessage(content=assembled))
            if thought:
                audit_span["reasoning_content"] = thought
            audit_span.persist_progress()

        call = consume_llm(planner, messages, on_chunk=_on_chunk)
        usage_items.append(call.usage)
        if call.reasoning.strip():
            reasoning_items.append(call.reasoning.strip())
        raw = call.content or message_content_text(getattr(call.message, "content", ""))
        if audit_span is not None:
            audit_span.set_output_message(call.message)
            audit_span.set_usage(merge_usage(*usage_items))
            audit_span["reasoning_content"] = "\n".join(reasoning_items)
            audit_span.set_detail(
                {"attempts": attempts, "active_attempt": attempt + 1}
            )
            audit_span.persist_progress()
        try:
            nested = extract_nested_json(raw)
            if not nested:
                raise ValueError("Planner response is not JSON")
            decision_payload = orjson.loads(nested)
            if (
                isinstance(decision_payload, dict)
                and decision_payload.get("decision") == "ready"
                and isinstance(decision_payload.get("specification"), dict)
            ):
                decision_payload["specification"] = (
                    canonicalize_planner_requirement_ids(
                        decision_payload["specification"]
                    )
                )
            decision = PLANNING_DECISION_ADAPTER.validate_python(decision_payload)
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
                    model_messages=[*messages, call.message],
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
            normalized = normalized.model_copy(
                update={"specification": knowledge_application.specification}
            )
            issues = validate_specification(
                normalized.specification,
                schema_text=str(llm_service.chat_question.db_schema or ""),
                available_evidence_refs=available_refs,
            )
            issues.extend(
                validate_specification_transition(
                    previous_specification,
                    normalized.specification,
                    active_evidence_refs=available_refs,
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
                model_messages=[*messages, call.message],
            )
        except (TypeError, ValueError, ValidationError) as exc:
            last_error = str(exc)
            attempts.append({"attempt": attempt + 1, "error": last_error})
            if audit_span is not None:
                audit_span.set_detail(
                    {"attempts": attempts, "active_attempt": attempt + 1}
                )
                audit_span.persist_progress()
            if attempt == 0:
                messages.extend(
                    [
                        AIMessage(content=raw),
                        HumanMessage(
                            content=_REPAIR_PROMPT + "\n校验问题：" + last_error
                        ),
                    ]
                )
                if audit_span is not None:
                    audit_span.set_input_messages(messages)
                    audit_span.persist_progress()
    raise SemanticPlanningError(
        "Semantic planning failed: " + last_error,
        usage=merge_usage(*usage_items),
        reasoning="\n".join(reasoning_items),
        attempts=attempts,
        model_messages=messages,
    )

def repair_physical_query_plan(
    llm_service: Any,
    *,
    specification: QuerySpecification,
    previous_plans: list[dict[str, Any]],
    validation_error: str,
    max_batch_size: int,
) -> PhysicalPlanningResult:
    """Repair only a physical plan while keeping one specification revision."""
    question = llm_service.chat_question
    human_content = render_planner_input(
        schema=str(question.db_schema or ""),
        protocol=protocol_prompt_bits(llm_service),
        structured={
            "query_specification": specification.model_dump(mode="json"),
            "previous_plans": previous_plans,
            "validation_error": validation_error,
        },
    )
    messages = [
        SystemMessage(content=_PHYSICAL_REPAIR_PROMPT),
        HumanMessage(content=human_content),
    ]
    call = consume_llm(llm_service.llm.bind(temperature=0), messages)
    parsed = parse_query_generation(
        call.content,
        llm_service,
        max_batch_size=max_batch_size,
        specification=specification,
    )
    return PhysicalPlanningResult(
        parsed_plans=parsed,
        usage=call.usage,
        reasoning=call.reasoning,
        raw_text=call.content,
        model_messages=[*messages, call.message],
    )
