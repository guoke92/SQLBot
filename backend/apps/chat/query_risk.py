"""Versioned deterministic semantic-risk policy for executable query plans."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from apps.chat.plan_facts import PlanFacts

POLICY_VERSION = 1


class RiskReason(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    code: str
    detail: str
    severity: Literal["critical", "general"]


class QueryRisk(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    level: Literal["low", "high"]
    reasons: tuple[RiskReason, ...] = ()
    policy_version: int = POLICY_VERSION


@dataclass(frozen=True)
class QueryRiskInput:
    facts: tuple[PlanFacts, ...]
    schema_text: str = ""
    entity_bindings: dict[str, Any] | None = None
    temporal_evidence: dict[str, Any] | None = None
    evidence_kinds: tuple[str, ...] = ()
    certified_relation_count: int = 0
    certified_knowledge: bool = True


_TEMPORAL_TYPE = re.compile(
    r"(?im)\b([a-zA-Z_][\w$]*)\b[^\n,;]{0,80}\b(date|datetime|timestamp|time)\b"
)
_TEMPORAL_NAME = re.compile(r"(?i)(?:^|_)(date|time|year|month|day)(?:_|$)")
_IDENT = re.compile(r"[A-Za-z_][\w$]*")


def _temporal_fields(schema_text: str) -> set[str]:
    return {match.group(1).casefold() for match in _TEMPORAL_TYPE.finditer(schema_text)}


def _time_fields_in_predicate(text: str, known: set[str]) -> set[str]:
    names = {match.group(0).casefold() for match in _IDENT.finditer(text)}
    return {name for name in names if name in known or _TEMPORAL_NAME.search(name)}


def _ambiguous_entities(bindings: dict[str, Any] | None) -> bool:
    if not bindings:
        return False
    if bindings.get("ambiguous"):
        return True
    candidates = bindings.get("candidates") or []
    for item in candidates:
        if not isinstance(item, dict):
            continue
        values = (
            item.get("matches") or item.get("candidates") or item.get("values") or []
        )
        if isinstance(values, list) and len(values) > 1 and not item.get("resolved"):
            return True
    return False


def classify_query_risk(value: QueryRiskInput) -> QueryRisk:
    """Return the same result for identical evidence and PlanFacts."""
    critical: dict[str, str] = {}
    general: dict[str, str] = {}
    facts = value.facts
    time_fields = _temporal_fields(value.schema_text)
    if any(
        len(_time_fields_in_predicate(predicate, time_fields)) >= 2
        for fact in facts
        for predicate in fact.predicates
    ):
        critical["MULTIPLE_TIME_BASIS"] = "同一过滤条件混合了多个业务时间字段"
    if _ambiguous_entities(value.entity_bindings):
        critical["AMBIGUOUS_ENTITY"] = "业务实体存在多个有效候选且未唯一解析"
    resolved_entities = (value.entity_bindings or {}).get("resolved") or {}
    predicate_text = " ".join(
        predicate.casefold() for fact in facts for predicate in fact.predicates
    )
    predicate_fields = {
        field.casefold() for fact in facts for field in fact.predicate_fields
    }
    for binding in resolved_entities.values():
        if not isinstance(binding, dict):
            continue
        canonical = str(binding.get("canonical") or "").strip().casefold()
        target_fields = {
            str(item.get("field_name") or "").strip().casefold()
            for item in binding.get("targets") or []
            if isinstance(item, dict)
        }
        if (
            canonical
            and canonical not in predicate_text
            and not (target_fields & predicate_fields)
        ):
            critical["EXPLICIT_ENTITY_NOT_PROVEN"] = (
                "查询计划无法证明已解析业务实体被用于过滤"
            )
            break
    temporal = value.temporal_evidence or {}
    start = str(temporal.get("start") or "").strip().casefold()
    end = str(temporal.get("end_exclusive") or "").strip().casefold()
    implementation_text = " ".join(
        [
            *(predicate.casefold() for fact in facts for predicate in fact.predicates),
            *(
                expression.casefold()
                for fact in facts
                for expression in fact.output_expressions
            ),
        ]
    )
    if (
        start
        and end
        and (start not in implementation_text or end not in implementation_text)
    ):
        critical["EXPLICIT_TIME_NOT_PROVEN"] = "查询计划无法证明用户明确的时间范围"
    join_count = sum(len(item.joins) for item in facts)
    if join_count and value.certified_relation_count < join_count:
        critical["UNTRUSTED_RELATION"] = "查询使用未认证或低可信的表关系"
    if any(item.case_count or item.arithmetic_count for item in facts):
        critical["DERIVED_METRIC"] = "查询包含条件聚合或计算型派生指标"
    if len(facts) >= 2:
        critical["MULTIPLE_REQUIRED_DATASETS"] = "查询包含多个必需结果集"
    if any(item.parser_coverage != "full" for item in facts):
        critical["PARTIAL_PARSER_COVERAGE"] = "查询解析覆盖不完整"

    if sum(item.aggregation_count for item in facts) >= 2:
        general["MULTIPLE_METRICS"] = "查询包含多个指标"
    if len({resource for item in facts for resource in item.resources}) >= 2:
        general["MULTIPLE_TABLES"] = "查询使用多个数据资源"
    if any(
        item.subquery_count
        or item.cte_count
        or item.set_operation_count
        or item.window_count
        for item in facts
    ):
        general["COMPLEX_QUERY_SHAPE"] = "查询包含子查询、CTE、集合操作或窗口函数"
    if any(item.case_count for item in facts):
        general["CASE_AGGREGATION"] = "查询包含 CASE 条件表达式"
    if {"clarification_option", "clarification_custom", "user_correction"} & set(
        value.evidence_kinds
    ):
        general["USER_CLARIFICATION"] = "本轮使用了业务澄清或用户纠正"
    if not value.certified_knowledge:
        general["LOW_CONFIDENCE_KNOWLEDGE"] = "查询使用未认证知识或低置信度映射"
    if sum(len(item.predicates) for item in facts) >= 2:
        general["MULTIPLE_FILTERS"] = "查询组合了多个过滤条件"
    if sum(len(item.group_fields) for item in facts) >= 2:
        general["COMPOSITE_GRAIN"] = "结果粒度由多个维度共同决定"

    reasons = [
        RiskReason(code=code, detail=detail, severity="critical")
        for code, detail in sorted(critical.items())
    ] + [
        RiskReason(code=code, detail=detail, severity="general")
        for code, detail in sorted(general.items())
    ]
    level: Literal["low", "high"] = "high" if critical or len(general) >= 2 else "low"
    return QueryRisk(level=level, reasons=tuple(reasons))
