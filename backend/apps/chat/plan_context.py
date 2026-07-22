"""PlanContext — single plan-time brief injected into SQL generation.

Probe nodes (entity grounding, boundary bindings) write structured state only.
``render_plan_context`` is the one place that turns that state into prompt text.
Post-execution QC does not own SQL correctness; this block does.
"""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Sequence

# Shared multi-fact / dimension playbook (must stay aligned with cost_validate).
# Complements template.yaml multi-fact-staging (always-on rules).
# Keep this block about *how* to apply bindings + grain — not a second full rule book.
JOIN_PLAYBOOK = """\
## 生成要点（与 Rules 中 multi-fact-staging 一致，此处强调落地）
1. 多事实对照：CTE/子查询内各自聚合到共享粒度后再 JOIN；或 ≤2 条维度一致的 SQL。未聚合互 JOIN 会被系统拦截。
2. 时间维：用业务完成/结束时间优先于 create_time（除非用户明确「创建」）；月维双侧对齐，缺侧用 FULL OUTER / 维键 UNION。
3. 人员：有 FK id 用 id 关联；仅有名则名称列按实体绑定 IN/eq。
4. 过滤：严格按【实体绑定】的 eq/IN；禁止只用口语短词过窄等值。
5. 能一条就一条；brief≤20 字；不反问；只用 schema 表列。
"""


def _uniq_preserve(items: Sequence[str]) -> List[str]:
    out: List[str] = []
    seen = set()
    for x in items:
        s = (x or "").strip()
        if not s or s in seen:
            continue
        seen.add(s)
        out.append(s)
    return out


def entity_match_values(info: Mapping[str, Any]) -> List[str]:
    """Values that should appear in SQL filters for one resolved phrase."""
    canonical = str(info.get("canonical") or "").strip()
    alts = [str(a).strip() for a in (info.get("alternatives") or []) if str(a).strip()]
    match = (info.get("match") or "").strip().lower()
    if match == "eq" and canonical:
        return [canonical]
    return _uniq_preserve([canonical, *alts])[:12]


def infer_entity_match(
    phrase: str,
    canonical: str,
    alternatives: Sequence[str],
) -> str:
    """eq when unique exact; otherwise in (canonical + close alternatives)."""
    alts = [a for a in alternatives if a and a != canonical]
    if not alts and canonical == phrase:
        return "eq"
    return "in"


def render_entity_bindings(entity_bindings: Optional[Mapping[str, Any]]) -> str:
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
        "自然语言已映射到库内名称；按 match 策略过滤机构/部门/人员/系统等名称列"
        "（如 organization_name、user_name、system_name，以 schema 为准）。",
    ]
    for phrase, info in resolved.items():
        if not isinstance(info, dict):
            continue
        canonical = str(info.get("canonical") or "").strip()
        alts_raw = info.get("alternatives") or []
        match = (
            info.get("match")
            or infer_entity_match(phrase, canonical, alts_raw)
        ).lower()
        info_for_vals: Dict[str, Any] = {
            **info,
            "phrase": phrase,
            "match": match,
        }
        vals = entity_match_values(info_for_vals)
        col_hint = str(info.get("column_hint") or "名称类字段").strip()
        if match == "eq" and len(vals) == 1:
            lines.append(f"- 「{phrase}」→ `{col_hint}` = '{vals[0]}'（eq）")
        elif vals:
            in_list = ", ".join(f"'{v}'" for v in vals)
            note = ""
            if canonical and phrase != canonical:
                note = f"；禁止仅写 = '{phrase}'（标准名更完整时会漏数）"
            lines.append(
                f"- 「{phrase}」→ `{col_hint}` IN ({in_list})（in）{note}"
            )
        alts = [a for a in alts_raw if a and a != canonical]
        if alts and match == "eq":
            lines.append(f"  备选（必要时改 IN）: {'、'.join(str(a) for a in alts[:6])}")
    return "\n".join(lines)


def render_query_bindings(query_bindings: Optional[Mapping[str, Any]]) -> str:
    if not query_bindings:
        return ""
    notes = query_bindings.get("_notes")
    if isinstance(notes, list) and notes:
        body = "\n".join(str(n) for n in notes if str(n).strip())
        if body:
            return "## 查询边界绑定\n" + body
    pairs = [
        (k, v)
        for k, v in query_bindings.items()
        if not str(k).startswith("_") and v is not None and str(v).strip() != ""
    ]
    if not pairs:
        return ""
    lines = [
        "## 查询边界绑定",
        "大表可同时施加主键下界与时间下界以控成本（正确性仍靠时间条件）：",
    ]
    for k, v in pairs:
        lines.append(f"- `{k}` → {v}")
    return "\n".join(lines)


def render_plan_context(
    *,
    entity_bindings: Optional[Mapping[str, Any]] = None,
    query_bindings: Optional[Mapping[str, Any]] = None,
    include_playbook: bool = True,
    repair: str = "",
    extra_sections: Optional[Sequence[str]] = None,
) -> str:
    """Build the single plan-context body (no outer tags)."""
    parts: List[str] = []
    ent = render_entity_bindings(entity_bindings)
    if ent:
        parts.append(ent)
    binds = render_query_bindings(query_bindings)
    if binds:
        parts.append(binds)
    if include_playbook:
        parts.append(JOIN_PLAYBOOK.strip())
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
