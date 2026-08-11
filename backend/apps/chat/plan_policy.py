"""Central PlanPolicy for the NLQ reviewed batch flow.

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

# ── result window ────────────────────────────────────────────────────────────
ROW_LIMIT = 1000

# ── catalog / cost gate ──────────────────────────────────────────────────────
# Tables with approx_rows >= this are "large" for fan-out decisions.
LARGE_TABLE_ROWS = 100_000
# Sum of EXPLAIN estimated rows (when available) above which plan is rejected.
EXPLAIN_MAX_ROWS = 5_000_000
# Max base large fact tables in one FROM/JOIN web without staging aggregation.
MAX_LARGE_FACTS_UNSTAGED = 1

# ── shared SQL-generation policy text ───────────────────────────────────────
# One semantic source rendered into the conditional PlanContext playbook.
MULTI_FACT_REQUIREMENTS = (
    "用户要求在同一结果中展示多个事实指标且存在共享粒度时，必须先在子查询/CTE "
    "内分别聚合后合并为一条查询；只有指标属于独立分析切片或不存在可靠共享键时才拆分",
    "禁止未聚合的事实明细表直接互相 JOIN，避免多对多行数膨胀",
    "多事实业务主体范围严格服从当前规格 revision 的 relation.population；intersection 使用 INNER，"
    "left/right 保留对应一侧，union 在不支持 FULL OUTER JOIN 的引擎上构造 UNION "
    "去重的共享维键集合，再分别 LEFT JOIN 各聚合结果",
    "多事实结果只能保留各事实都能按已确认业务口径映射的共享维度；"
    "不得用 NULL 伪造缺失维度，也不得用 MIN/MAX 随机挑选维度值",
    "只有当前数据库引擎明确支持且写法更简洁时才使用 FULL OUTER JOIN；"
    "不得用重复整段聚合查询的 LEFT/RIGHT JOIN + UNION ALL 模拟",
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
