"""PlanContext — single plan-time brief injected into SQL generation.

Probe nodes (entity grounding, boundary bindings) write structured state only.
``render_plan_context`` is the one place that turns that state into prompt text.
Post-execution QC does not own SQL correctness; this block does.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Mapping, Optional, Sequence

from apps.chat.plan_policy import render_multi_fact_playbook


JOIN_PLAYBOOK_SUFFIX = """\
5. 时间维：按用户语义选择创建/完成/结束时间；无明确口径时结合字段注释，禁止机械套用固定时间列。
6. 人员：有 FK id 用 id 关联；仅有名称时按实体绑定 IN/eq，并避免非唯一名称 JOIN 放大计数。
7. 过滤：严格按【实体绑定】的 eq/IN；禁止只用口语短词过窄等值。
8. 直接给出最终方案，不讨论"为了符合规则"或泛化评价子查询效率；brief≤20 字。
9. **交叉验证原则**：当用户质疑某个结果项时，必须沿原查询的关联路径验证，辅以相关表交叉验证，**绝不能仅查一张表就下结论**。
10. **默认时间范围**：当用户未指定时间范围且查询涉及时间维度时，默认使用最近 12 个月（以数据中最新月份为基准往前推）。若结果为空再放宽。仅当用户明确表示"所有时间"或"全部"时才不限时间。
"""


def render_join_playbook() -> str:
    """Compose canonical multi-fact policy with plan-time binding guidance."""
    return render_multi_fact_playbook() + "\n" + JOIN_PLAYBOOK_SUFFIX.strip()


def _extract_tables_from_sql(sql: str) -> List[str]:
    """Extract table names from FROM/JOIN clauses (best-effort, not a full parser)."""
    tables: List[str] = []
    # Match `schema`.`table` or `table` after FROM/JOIN
    for m in re.finditer(
        r'(?:FROM|JOIN)\s+(?:`?\w+`?\.)?`?(\w+)`?',
        sql or "",
        re.IGNORECASE,
    ):
        t = m.group(1).strip()
        if t and t not in tables:
            tables.append(t)
    return tables


def _extract_where_conditions(sql: str) -> List[str]:
    """Extract WHERE conditions mentioning specific values (best-effort)."""
    conditions: List[str] = []
    where_match = re.search(r'\bWHERE\b(.+?)(?:\bGROUP\b|\bORDER\b|\bLIMIT\b|\bUNION\b|$)',
                            sql or "", re.IGNORECASE | re.DOTALL)
    if not where_match:
        return conditions
    where_text = where_match.group(1).strip()
    # Extract IN (subquery) — note the subquery target
    for m in re.finditer(r'`?(\w+)`?\s+IN\s*\(\s*(SELECT\s+.+?)\)', where_text, re.IGNORECASE | re.DOTALL):
        col = m.group(1)
        sub = m.group(2).strip()[:120]
        conditions.append(f"`{col}` IN (subquery: {sub}...)")
    # Extract IN (...) with literal values
    for m in re.finditer(r'`?(\w+)`?\s+IN\s*\(([^)]+)\)', where_text, re.IGNORECASE):
        col = m.group(1)
        vals = m.group(2).strip()
        if len(vals) < 200:
            conditions.append(f"`{col}` IN ({vals})")
    # Extract = 'value' conditions
    for m in re.finditer(r'`?(\w+)`?\s*=\s*[\'"]([^\'\"]+)[\'"]', where_text):
        col = m.group(1)
        val = m.group(2)
        if col not in ("deleted",):
            conditions.append(f"`{col}` = '{val}'")
    # Extract LIKE conditions
    for m in re.finditer(r'`?(\w+)`?\s+LIKE\s+[\'"]([^\'\"]+)[\'"]', where_text, re.IGNORECASE):
        col = m.group(1)
        val = m.group(2)
        conditions.append(f"`{col}` LIKE '{val}'")
    return conditions[:12]


def build_cross_validation_section(
    previous_sqls: List[str],
    question: str,
) -> str:
    """Build a cross-validation context section from previous SQL join paths.

    When the user questions a result item, the LLM must trace the original
    join path and cross-validate — not just query a single table.
    """
    if not previous_sqls:
        return ""
    # Deduplicate
    unique_sqls = list(dict.fromkeys(s.strip() for s in previous_sqls if s and s.strip()))
    if not unique_sqls:
        return ""

    lines = [
        "## 上一轮查询关联路径（验证时必须沿此路径交叉验证，禁止仅查单表下结论）",
    ]
    for i, sql in enumerate(unique_sqls[:3], 1):
        tables = _extract_tables_from_sql(sql)
        conditions = _extract_where_conditions(sql)
        lines.append(f"### 查询{i}")
        if tables:
            lines.append(f"- 涉及表: {', '.join(tables)}")
        if conditions:
            lines.append(f"- 过滤条件: {'; '.join(conditions)}")
        # Show the actual SQL snippet for LLM to understand join logic
        sql_snip = sql[:600] if len(sql) <= 600 else sql[:600] + " …"
        lines.append(f"- SQL:\n```sql\n{sql_snip}\n```")

    lines.append("")
    lines.append(
        "**验证要求**：用户质疑某个结果项时，必须：\n"
        "1. 沿原查询的 JOIN 路径确认数据来源\n"
        "2. 辅以相关表交叉验证（从不同关联角度确认同一结论）\n"
        "3. 列出具体数据值作为证据\n"
        "4. **绝不能仅查一张表就给出确定性结论**"
    )
    return "\n".join(lines)


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
    """eq when canonical resolved; alternatives are advisory fallback only.

    The canonical name was selected by the disambiguation step, so ``= canonical``
    is the correct filter.  Alternatives are surfaced to the LLM as advisory
    notes; they are NOT automatically injected into an IN list (which would
    pull in deprecated/废弃 orgs or unrelated values the user didn't ask for).
    """
    if canonical:
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
        "自然语言已映射到库内名称；按 match 策略过滤名称类列（以 schema 字段注释为准）。",
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
