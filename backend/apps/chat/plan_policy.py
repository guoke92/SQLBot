"""Central PlanPolicy for NLQ agentic loop.

Single place for knobs that used to be scattered across guidance text,
quality gates, and ad-hoc constants. Protocol validate + graph nodes both
import from here — do not re-declare magic numbers in nodes.
"""

from __future__ import annotations

# ── loop bounds ──────────────────────────────────────────────────────────────
MAX_BATCH_ROUNDS = 2
MAX_QUERIES_PER_BATCH = 3
# Extra generate→validate attempts after a plan-time failure (same batch slot).
# Total plan attempts per slot = 1 + MAX_PLAN_REGEN.
MAX_PLAN_REGEN = 1
DEFAULT_CHART = "table"

# ── result quality (severe-only continue) ────────────────────────────────────
NULL_DIM_SEVERE = 0.60
ROW_LIMIT = 1000
ROW_LIMIT_NEAR = int(ROW_LIMIT * 0.9)

# ── catalog / cost gate ──────────────────────────────────────────────────────
# Tables with approx_rows >= this are "large" for fan-out / probe decisions.
LARGE_TABLE_ROWS = 100_000
# Sum of EXPLAIN estimated rows (when available) above which plan is rejected.
EXPLAIN_MAX_ROWS = 5_000_000
# Max base large fact tables in one FROM/JOIN web without staging aggregation.
MAX_LARGE_FACTS_UNSTAGED = 1

# Tokens that often mark "fact" tables in naming conventions (supplement rows).
FACT_NAME_HINTS = (
    "story",
    "task",
    "bug",
    "case",
    "result",
    "order",
    "detail",
    "log",
    "event",
    "record",
    "transaction",
)


# ── shared SQL-generation policy text ───────────────────────────────────────
# One semantic source rendered into both the base Rules block and PlanContext.
MULTI_FACT_REQUIREMENTS = (
    "同一维度下对比多个事实表时，先在子查询/CTE 内分别聚合到共享粒度再关联；"
    "确需拆分时最多生成 2 条维度一致的 SQL",
    "禁止未聚合的事实明细表直接互相 JOIN，避免多对多行数膨胀",
    "月/周等双侧时间维缺数据时，优先构造 UNION 去重的共享维键集合，"
    "再分别 LEFT JOIN 各聚合结果",
    "只有当前数据库引擎明确支持且写法更简洁时才使用 FULL OUTER JOIN；"
    "不得用重复整段聚合查询的 LEFT/RIGHT JOIN + UNION ALL 模拟",
)


def render_multi_fact_rule_xml() -> str:
    """Render the canonical multi-fact policy for template Rules."""
    requirements = "\n".join(
        f"            <requirement>{requirement}</requirement>"
        for requirement in MULTI_FACT_REQUIREMENTS
    )
    return (
        '<rule priority="critical" id="multi-fact-staging">\n'
        "          <title>多事实表合成</title>\n"
        "          <requirements>\n"
        f"{requirements}\n"
        "          </requirements>\n"
        "        </rule>"
    )


def render_multi_fact_playbook() -> str:
    """Render the same policy as compact PlanContext guidance."""
    lines = ["## 多事实表合成（multi-fact-staging）"]
    lines.extend(
        f"{index}. {requirement}"
        for index, requirement in enumerate(MULTI_FACT_REQUIREMENTS, start=1)
    )
    return "\n".join(lines)


# ── execute SLA (milliseconds for engines that support max_execution_time) ───
# 0 = do not inject statement timeout (rely on driver only).
EXECUTE_TIMEOUT_MS = 45_000
# Soft ceiling used when DatasourceConf.timeout is 0/None.
EXECUTE_TIMEOUT_SEC = 45

# ── boundary probe ───────────────────────────────────────────────────────────
BOUNDARY_PROBE_ENABLED = True
# Prefer probe when table rows >= this and SQL/question has time filter.
BOUNDARY_PROBE_MIN_ROWS = 50_000
