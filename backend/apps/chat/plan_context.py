"""PlanContext — single plan-time brief injected into SQL generation.

Grounding and time-intent nodes write structured state only.
``render_plan_context`` is the one place that turns that state into prompt text.
Post-execution QC does not own SQL correctness; this block does.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from apps.chat.plan_policy import render_multi_fact_playbook
from apps.chat.query_contract import QueryContract
from apps.chat.semantic_intent import contract_display_rows

JOIN_PLAYBOOK_SUFFIX = """\
5. 时间维：按用户语义选择创建/完成/结束时间；无明确口径时结合字段注释，禁止机械套用固定时间列。
6. 人员：有 FK id 用 id 关联；仅有名称时按实体绑定 IN/eq，并避免非唯一名称 JOIN 放大计数。
7. 过滤：严格按【实体绑定】的 eq/IN；禁止只用口语短词过窄等值。
8. 直接给出最终方案，不讨论"为了符合规则"或泛化评价子查询效率；brief≤20 字。
9. 平台会独立限制查询返回行数；不得通过移除 SQL LIMIT 规避查询上限。明细结果应按业务指标
   稳定排序；用户同时要求总体汇总与明细时，分别返回小结果汇总和有序明细。
"""


def render_join_playbook() -> str:
    """Compose canonical multi-fact policy with plan-time binding guidance."""
    return render_multi_fact_playbook() + "\n" + JOIN_PLAYBOOK_SUFFIX.strip()


def _uniq_preserve(items: Sequence[str]) -> list[str]:
    out: list[str] = []
    seen = set()
    for x in items:
        s = (x or "").strip()
        if not s or s in seen:
            continue
        seen.add(s)
        out.append(s)
    return out


def entity_match_values(info: Mapping[str, Any]) -> list[str]:
    """Values that should appear in SQL filters for one resolved phrase."""
    canonical = str(info.get("canonical") or "").strip()
    alts = [str(a).strip() for a in (info.get("alternatives") or []) if str(a).strip()]
    match = (info.get("match") or "").strip().lower()
    if match == "eq" and canonical:
        return [canonical]
    return _uniq_preserve([canonical, *alts])[:12]


def render_entity_bindings(entity_bindings: Mapping[str, Any] | None) -> str:
    if not entity_bindings:
        return ""
    resolved = entity_bindings.get("resolved") or {}
    if not isinstance(resolved, dict) or not resolved:
        cands = entity_bindings.get("candidates") or []
        if cands:
            joined = "、".join(f"「{c}」" for c in cands[:12])
            return (
                "## 实体绑定\n"
                f"未解析到库内标准维值；候选短语：{joined}。"
                "名称过滤时优先 LIKE/IN 包含这些短语的标准全称，避免过窄等值。"
            )
        return ""

    lines = [
        "## 实体绑定（生成 WHERE 时必须遵守）",
        "自然语言已映射到库内名称；按 match 策略过滤名称类列（以 schema 字段注释为准）。",
    ]
    for phrase, info in resolved.items():
        if not isinstance(info, dict):
            continue
        canonical = str(info.get("canonical") or "").strip()
        alts_raw = info.get("alternatives") or []
        match = str(info.get("match") or ("eq" if canonical else "in")).lower()
        info_for_vals: dict[str, Any] = {
            **info,
            "phrase": phrase,
            "match": match,
        }
        vals = entity_match_values(info_for_vals)
        targets = info.get("targets") or []
        target_names = [
            f"{target.get('table_name')}.{target.get('field_name')}"
            for target in targets
            if isinstance(target, dict)
            and target.get("table_name")
            and target.get("field_name")
        ]
        col_hint = " / ".join(target_names) or "名称类字段"
        if match == "eq" and len(vals) == 1:
            lines.append(f"- 「{phrase}」→ `{col_hint}` = '{vals[0]}'（eq）")
        elif vals:
            in_list = ", ".join(f"'{v}'" for v in vals)
            note = ""
            if canonical and phrase != canonical:
                note = f"；禁止仅写 = '{phrase}'（标准名更完整时会漏数）"
            lines.append(f"- 「{phrase}」→ `{col_hint}` IN ({in_list})（in）{note}")
        alts = [a for a in alts_raw if a and a != canonical]
        if alts and match == "eq":
            lines.append(
                "  诊断候选（不得自动并入 IN，可能包含历史/废弃值）: "
                + "、".join(str(a) for a in alts[:6])
            )
    return "\n".join(lines)


def render_query_contract(contract: QueryContract | None) -> str:
    """Render the sole frozen execution contract for SQL planning."""
    if contract is None:
        return ""
    rows = contract_display_rows(contract)
    lines = [
        "## 已冻结查询契约（最高优先级）",
        (
            "结果形态：明细记录（不得擅自增加 GROUP BY 或聚合）"
            if contract.result_mode == "detail"
            else "结果形态：聚合统计（必须严格遵守输出粒度）"
        ),
        "每个 slot 是独立且必须落实的业务子句；不得新增业务过滤或改写口径：",
    ]
    for requirement, (label, rendered) in zip(
        contract.requirements,
        rows,
        strict=True,
    ):
        lines.append(
            f"- [{requirement.slot_id}] {requirement.clause} | {label}: {rendered}"
        )
    return "\n".join(lines)


def render_plan_context(
    *,
    entity_bindings: Mapping[str, Any] | None = None,
    contract: QueryContract | None = None,
    include_playbook: bool = True,
    repair: str = "",
    extra_sections: Sequence[str] | None = None,
) -> str:
    """Build the single plan-context body (no outer tags)."""
    parts: list[str] = []
    ent = render_entity_bindings(entity_bindings)
    if ent:
        parts.append(ent)
    contract_block = render_query_contract(contract)
    if contract_block:
        parts.append(contract_block)
    if include_playbook:
        parts.append(render_join_playbook())
    for sec in extra_sections or []:
        s = (sec or "").strip()
        if s:
            parts.append(s)
    rep = (repair or "").strip()
    if rep:
        if rep.startswith("##"):
            parts.append(rep)
        else:
            parts.append("## 计划校验/改写\n" + rep)
    return "\n\n".join(parts).strip()


def wrap_plan_context(body: str) -> str:
    body = (body or "").strip()
    if not body:
        return ""
    return "<plan-context>\n" + body + "\n</plan-context>\n"


def normalize_plan_context_block(plan_ctx: str | None) -> str:
    """Idempotent: accept raw body or pre-wrapped block; always trailing newline when non-empty."""
    plan_ctx = (plan_ctx or "").strip()
    if not plan_ctx:
        return ""
    if not plan_ctx.lstrip().startswith("<plan-context"):
        plan_ctx = wrap_plan_context(plan_ctx).rstrip("\n")
    if not plan_ctx.endswith("\n"):
        plan_ctx = plan_ctx + "\n"
    return plan_ctx
