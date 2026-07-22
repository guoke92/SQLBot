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

# ── execute SLA (milliseconds for engines that support max_execution_time) ───
# 0 = do not inject statement timeout (rely on driver only).
EXECUTE_TIMEOUT_MS = 45_000
# Soft ceiling used when DatasourceConf.timeout is 0/None.
EXECUTE_TIMEOUT_SEC = 45

# ── boundary probe ───────────────────────────────────────────────────────────
BOUNDARY_PROBE_ENABLED = True
# Prefer probe when table rows >= this and SQL/question has time filter.
BOUNDARY_PROBE_MIN_ROWS = 50_000
