"""Structural + EXPLAIN cost checks for SQL plans.

Used exclusively from ``SqlProtocol.validate_plan`` so graph nodes stay free of
SQL dialect / catalog details.
"""

from __future__ import annotations

from typing import Any

from apps.chat.plan_policy import (
    EXPLAIN_MAX_ROWS,
    LARGE_TABLE_ROWS,
    MAX_LARGE_FACTS_UNSTAGED,
)
from common.utils.utils import SQLBotLogUtil


def _is_large_fact(approx_rows: int | None) -> bool:
    """Only *known-large* tables are hard large-facts.

    Name heuristics alone must not block valid plans when catalog statistics
    are unavailable.
    """
    if approx_rows is None:
        return False
    try:
        return int(approx_rows) >= LARGE_TABLE_ROWS
    except Exception:
        return False


def _count_staged_fact_aggs(tree: Any, fact_names: set[str], exp: Any) -> int:
    """How many derived tables / CTEs look like per-fact pre-aggregation."""
    staged = 0
    containers = []
    try:
        containers.extend(list(tree.find_all(exp.Subquery)))
    except Exception:
        pass
    try:
        containers.extend(list(tree.find_all(exp.CTE)))
    except Exception:
        pass
    # Unnamed derived: parenthesized Select in JOIN
    try:
        for join in tree.find_all(exp.Join):
            for sel in join.find_all(exp.Select):
                if sel is not tree:
                    containers.append(sel)
    except Exception:
        pass

    seen_ids: set[int] = set()
    for sub in containers:
        sid = id(sub)
        if sid in seen_ids:
            continue
        seen_ids.add(sid)
        try:
            has_group = bool(list(sub.find_all(exp.Group)))
            has_agg = bool(list(sub.find_all(exp.AggFunc)))
            if not (has_group or has_agg):
                continue
            sub_tables = {t.name for t in sub.find_all(exp.Table) if t.name}
            # Counts if this subquery aggregates at least one fact table
            if sub_tables & fact_names:
                staged += 1
        except Exception:
            continue
    return staged


def check_multi_fact_fanout(
    sql: str,
    dialect: str,
    stats_by_table: dict[str, dict[str, Any]],
) -> str | None:
    """Reject unstaged multi-fact join webs that tend to explode.

    Policy:
    - Hard reject only when **2+ known-large** facts (approx_rows)>= threshold
      appear together without per-fact staging aggregation.
    - Name-only hits (stats cold) never hard-reject alone; EXPLAIN + timeout
      still protect runtime.
    - Proper staging (subquery/CTE with GROUP BY/agg on each fact) is allowed.
    """
    try:
        import sqlglot as sg
        from sqlglot import exp
    except Exception:
        return None

    try:
        trees = sg.parse(sql, dialect=dialect or "mysql")
    except Exception:
        return None

    for tree in trees:
        if not tree:
            continue
        tables: set[str] = set()
        for t in tree.find_all(exp.Table):
            if t.name:
                tables.add(t.name)
        if len(tables) < 2:
            continue

        known_large: list = []
        for name in tables:
            st = stats_by_table.get(name) or {}
            rows = st.get("approx_rows")
            try:
                rows_i = int(rows) if rows is not None else None
            except Exception:
                rows_i = None
            if _is_large_fact(rows_i):
                known_large.append((name, rows_i))

        # Need multiple *known* large facts for hard gate
        if len(known_large) <= MAX_LARGE_FACTS_UNSTAGED:
            continue

        fact_name_set = {n for n, _ in known_large}
        staged = _count_staged_fact_aggs(tree, fact_name_set, exp)
        if staged >= 2:
            continue
        # Single staged subquery that already unifies grain — still allow if only
        # one known-large remains unstaged and others are dims.
        if staged >= max(1, len(known_large) - MAX_LARGE_FACTS_UNSTAGED):
            # e.g. 2 large facts both inside staging branches
            if staged >= len(known_large):
                continue

        fact_names = ", ".join(
            f"{n}(~{r if r is not None else '?'})" for n, r in known_large
        )
        return (
            "SQL joins multiple large fact tables without per-table staging "
            f"aggregation ({fact_names}). Prefer: aggregate each fact to the "
            "shared grain first (subquery/CTE), then join the small results — "
            "or split into ≤2 final queries. Direct multi-fact LEFT JOIN on a "
            "dimension causes join explosion."
        )
    return None


def _collect_explain_rows(plan_rows: Any) -> int:
    """Best-effort max/sum row estimate from EXPLAIN output shapes."""
    total = 0
    max_r = 0

    def walk(obj: Any) -> None:
        nonlocal total, max_r
        if isinstance(obj, dict):
            for k, v in obj.items():
                lk = str(k).lower()
                if (
                    lk in ("rows", "est_rows", "row count", "plan_rows")
                    and v is not None
                ):
                    try:
                        iv = int(float(v))
                        total += iv
                        max_r = max(max_r, iv)
                    except Exception:
                        pass
                else:
                    walk(v)
        elif isinstance(obj, list):
            for it in obj:
                walk(it)

    walk(plan_rows)
    return max(total, max_r)


def explain_cost_too_high(ds: Any, sql: str) -> str | None:
    """Run EXPLAIN when supported; reject invalid or prohibitively costly SQL.

    JSON EXPLAIN is an optional optimization and may fall back to the regular
    form. Once the datasource rejects regular EXPLAIN, however, the statement
    is not safe to execute and the error must participate in the repair loop.
    """
    dtype = (getattr(ds, "type", None) or "").lower()
    if dtype not in (
        "mysql",
        "mariadb",
        "doris",
        "starrocks",
        "pg",
        "postgresql",
        "kingbase",
    ):
        return None
    try:
        import orjson
        from sqlalchemy import text

        from apps.db.db import get_session
    except Exception:
        return None

    explain_sql = f"EXPLAIN {sql}"
    use_json = dtype in ("mysql", "mariadb")
    try:
        with get_session(ds) as session:
            if use_json:
                try:
                    raw = session.execute(text(f"EXPLAIN FORMAT=JSON {sql}")).fetchall()
                    payload = raw[0][0] if raw else "{}"
                    if isinstance(payload, (bytes, bytearray)):
                        payload = payload.decode()
                    data = (
                        orjson.loads(payload) if isinstance(payload, str) else payload
                    )
                    est = _collect_explain_rows(data)
                    if est >= EXPLAIN_MAX_ROWS:
                        return (
                            f"EXPLAIN estimates ~{est} rows (≥ {EXPLAIN_MAX_ROWS}). "
                            "Narrow filters, pre-aggregate facts, or split the query."
                        )
                    return None
                except Exception:
                    pass
            rows = session.execute(text(explain_sql)).fetchall()
            est = 0
            for r in rows:
                if hasattr(r, "_mapping"):
                    m = dict(r._mapping)
                    for k in ("rows", "ROWS", "Rows"):
                        if k in m and m[k] is not None:
                            try:
                                est = max(est, int(m[k]))
                            except Exception:
                                pass
                else:
                    if len(r) >= 10:
                        try:
                            est = max(est, int(r[9]))
                        except Exception:
                            pass
            if est >= EXPLAIN_MAX_ROWS:
                return (
                    f"EXPLAIN estimates ~{est} rows (≥ {EXPLAIN_MAX_ROWS}). "
                    "Narrow filters, pre-aggregate facts, or split the query."
                )
    except Exception as exc:
        detail = str(getattr(exc, "orig", exc) or exc).strip()
        detail = " ".join(detail.split())[:1200]
        message = f"SQL EXPLAIN validation failed: {detail}"
        SQLBotLogUtil.warning(message)
        return message
    return None
