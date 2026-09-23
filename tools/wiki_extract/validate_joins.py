"""Live DB validation for wiki EQUI_JOIN edges.

For each claimed edge ``A.x → B.y`` (left → right as stored on table pages),
probe both sides with full-table counts (not sampled TopK):

1. row / non-null / distinct counts on each endpoint
2. ``COUNT(*)`` of equi-join hits ``A.x = B.y``
3. inclusion: A rows whose ``x`` ∈ distinct(B.y) and the complement
4. inclusion: B rows whose ``y`` ∈ distinct(A.x) and the complement
5. small value-set samples: intersection + one-sided diffs

Verdicts (data-only; does not rewrite wiki pages)::

- ``impossible`` — both sides have values but intersection is empty
  (join hits = 0 and both inclusions = 0)
- ``false_friend`` — non-empty but negligible overlap on large domains
  (same-name / UUID-vs-code style collisions; not a usable equi-join)
- ``empty_endpoint`` — one side has no usable non-null values
- ``missing_column`` — catalog / information_schema lacks a column
- ``fk_like`` — almost all child (right) values appear on parent (left)
- ``shared_domain`` — substantial two-way overlap (same business code space)
- ``weak_overlap`` — non-empty but thin overlap (review samples)
- ``query_error`` — SQL failed (type cast / permissions / …)

Usage::

    export WIKI_EXTRACT_DSN='mysql://user:pass@host:port/lowcode_pplatform'
    backend/venv/bin/python -m tools.wiki_extract validate-joins \\
        --wiki docs/wiki/v3 \\
        --out docs/wiki/v3/_raw/join_validation
"""

from __future__ import annotations

import datetime as dt
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

from tools.wiki_extract.connect import connect, resolve_dsn
from tools.wiki_extract.join_policy import parse_fq, sql_ident

_RELATION_FENCE = re.compile(r"```ground:relation\n([\s\S]*?)\n```")


@dataclass
class EndpointStats:
    table: str
    column: str
    exists: bool = True
    row_count: int | None = None
    non_null: int | None = None
    distinct_non_null: int | None = None
    sample: list[str] = field(default_factory=list)
    error: str = ""


@dataclass
class JoinProbe:
    left: str
    right: str
    host: str = ""
    trust: str = ""
    authenticity: str = ""
    source: str = ""
    wiki_evidence: str = ""
    left_stats: EndpointStats | None = None
    right_stats: EndpointStats | None = None
    join_hits: int | None = None
    left_in_right: int | None = None
    left_not_in_right: int | None = None
    right_in_left: int | None = None
    right_not_in_left: int | None = None
    left_in_right_ratio: float | None = None
    right_in_left_ratio: float | None = None
    intersection_sample: list[str] = field(default_factory=list)
    left_only_sample: list[str] = field(default_factory=list)
    right_only_sample: list[str] = field(default_factory=list)
    verdict: str = ""
    reason: str = ""
    error: str = ""


def load_wiki_relations(wiki_dir: Path) -> list[dict[str, Any]]:
    """Parse every ``ground:relation`` fence under ``wiki_dir/tables``.

    Dedupes by oriented pair ``(left, right)`` — the same edge is often
    mirrored onto both endpoint table pages.
    """
    tables = wiki_dir / "tables"
    if not tables.is_dir():
        raise FileNotFoundError(f"tables dir not found: {tables}")
    seen: dict[tuple[str, str], dict[str, Any]] = {}
    for path in sorted(tables.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for block in _RELATION_FENCE.findall(text):
            try:
                data = yaml.safe_load(block) or {}
            except yaml.YAMLError:
                continue
            if not isinstance(data, dict):
                continue
            left = str(data.get("left") or "").strip()
            right = str(data.get("right") or "").strip()
            if not left or not right or "." not in left or "." not in right:
                continue
            key = (left, right)
            if key in seen:
                # Prefer the page whose stem matches the left table.
                if seen[key].get("host") == left.split(".", 1)[0]:
                    continue
                if path.stem != left.split(".", 1)[0]:
                    continue
            seen[key] = {
                "left": left,
                "right": right,
                "host": path.stem,
                "trust": str(data.get("trust") or ""),
                "authenticity": str(data.get("authenticity") or ""),
                "source": str(data.get("source") or ""),
                "evidence": str(data.get("evidence") or ""),
                "join_role": str(data.get("join_role") or ""),
                "type": str(data.get("type") or "EQUI_JOIN"),
            }
    return list(seen.values())


def validate_relations(
    conn: Any,
    relations: list[dict[str, Any]],
    *,
    database: str = "",
    sample_limit: int = 8,
    only: set[tuple[str, str]] | None = None,
    limit: int = 0,
    progress: bool = True,
) -> dict[str, Any]:
    """Run live probes for each relation; return a serialisable report."""
    import sys

    schema = (database or "").strip() or _current_database(conn)
    probes: list[JoinProbe] = []
    pairs = relations
    if only:
        pairs = [r for r in pairs if (r["left"], r["right"]) in only]
    if limit and limit > 0:
        pairs = pairs[:limit]

    cache: dict[tuple[str, str], EndpointStats] = {}
    total = len(pairs)
    for idx, rel in enumerate(pairs, start=1):
        left, right = rel["left"], rel["right"]
        if progress:
            print(
                f"[{idx}/{total}] {left} → {right}",
                file=sys.stderr,
                flush=True,
            )
        probe = JoinProbe(
            left=left,
            right=right,
            host=str(rel.get("host") or ""),
            trust=str(rel.get("trust") or ""),
            authenticity=str(rel.get("authenticity") or ""),
            source=str(rel.get("source") or ""),
            wiki_evidence=str(rel.get("evidence") or ""),
        )
        try:
            lt, lc = parse_fq(left)
            rt, rc = parse_fq(right)
            probe.left_stats = cache.get((lt, lc)) or _endpoint_stats(
                conn, schema, lt, lc, sample_limit=sample_limit
            )
            cache[(lt, lc)] = probe.left_stats
            probe.right_stats = cache.get((rt, rc)) or _endpoint_stats(
                conn, schema, rt, rc, sample_limit=sample_limit
            )
            cache[(rt, rc)] = probe.right_stats
            if not probe.left_stats.exists or not probe.right_stats.exists:
                probe.verdict = "missing_column"
                probe.reason = "endpoint column missing in live schema"
                probes.append(probe)
                continue
            if (probe.left_stats.non_null or 0) == 0 or (
                probe.right_stats.non_null or 0
            ) == 0:
                probe.verdict = "empty_endpoint"
                probe.reason = "one side has zero usable non-null values"
                probes.append(probe)
                continue
            _fill_pair_metrics(
                conn,
                schema,
                probe,
                sample_limit=sample_limit,
            )
            probe.verdict, probe.reason = _decide_verdict(probe)
            if progress:
                print(
                    f"    → {probe.verdict} "
                    f"(join_hits={probe.join_hits}, "
                    f"L→R={probe.left_in_right_ratio}, "
                    f"R→L={probe.right_in_left_ratio})",
                    file=sys.stderr,
                    flush=True,
                )
        except Exception as exc:  # noqa: BLE001 — isolate per-edge failures
            probe.verdict = "query_error"
            probe.error = str(exc)
            probe.reason = "SQL probe failed"
            if progress:
                print(f"    → query_error: {exc}", file=sys.stderr, flush=True)
        probes.append(probe)

    by_verdict: dict[str, int] = {}
    for item in probes:
        by_verdict[item.verdict] = by_verdict.get(item.verdict, 0) + 1

    return {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "database": schema,
        "relation_count": len(probes),
        "by_verdict": by_verdict,
        "edges": [_probe_to_dict(item) for item in probes],
    }


def render_markdown_report(report: dict[str, Any]) -> str:
    """Human-readable summary ordered by severity."""
    order = [
        "impossible",
        "false_friend",
        "empty_endpoint",
        "missing_column",
        "query_error",
        "weak_overlap",
        "shared_domain",
        "fk_like",
    ]
    lines = [
        f"# JOIN live validation ({report.get('database')})",
        "",
        f"- generated_at: `{report.get('generated_at')}`",
        f"- edges: {report.get('relation_count')}",
        f"- by_verdict: `{report.get('by_verdict')}`",
        "",
    ]
    edges = report.get("edges") or []
    by: dict[str, list[dict[str, Any]]] = {}
    for edge in edges:
        by.setdefault(str(edge.get("verdict") or "other"), []).append(edge)
    for verdict in order:
        items = by.pop(verdict, [])
        if not items:
            continue
        lines.append(f"## {verdict} ({len(items)})")
        lines.append("")
        for edge in items:
            lines.append(
                f"- `{edge.get('left')}` → `{edge.get('right')}` "
                f"(host=`{edge.get('host')}`, wiki trust=`{edge.get('trust')}`/"
                f"`{edge.get('authenticity')}`)"
            )
            lines.append(f"  - reason: {edge.get('reason')}")
            lines.append(
                "  - join_hits={jh} | left_in_right={lir}/{lnn} ({lr}) | "
                "right_in_left={ril}/{rnn} ({rr})".format(
                    jh=edge.get("join_hits"),
                    lir=edge.get("left_in_right"),
                    lnn=(edge.get("left_stats") or {}).get("non_null"),
                    lr=edge.get("left_in_right_ratio"),
                    ril=edge.get("right_in_left"),
                    rnn=(edge.get("right_stats") or {}).get("non_null"),
                    rr=edge.get("right_in_left_ratio"),
                )
            )
            if edge.get("intersection_sample"):
                lines.append(f"  - intersection sample: {edge.get('intersection_sample')}")
            if edge.get("left_only_sample"):
                lines.append(f"  - left-only sample: {edge.get('left_only_sample')}")
            if edge.get("right_only_sample"):
                lines.append(f"  - right-only sample: {edge.get('right_only_sample')}")
            if edge.get("error"):
                lines.append(f"  - error: {edge.get('error')}")
        lines.append("")
    for verdict, items in sorted(by.items()):
        lines.append(f"## {verdict} ({len(items)})")
        lines.append("")
        for edge in items:
            lines.append(f"- `{edge.get('left')}` → `{edge.get('right')}`")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def run_validate_joins(
    *,
    wiki_dir: Path,
    db_url: str = "",
    database: str = "",
    out_dir: Path | None = None,
    out_report: Path | None = None,
    out_markdown: Path | None = None,
    sample_limit: int = 8,
    limit: int = 0,
    trust_filter: str = "",
    table_prefix: str = "",
) -> dict[str, Any]:
    relations = load_wiki_relations(wiki_dir)
    if trust_filter.strip():
        wanted = {part.strip() for part in trust_filter.split(",") if part.strip()}
        relations = [r for r in relations if r.get("trust") in wanted]
    prefix = (table_prefix or "").strip()
    if prefix:
        relations = [
            r
            for r in relations
            if r["left"].startswith(prefix) or r["right"].startswith(prefix)
        ]
    target = resolve_dsn(db_url=db_url, database=database)
    conn = connect(target)
    try:
        report = validate_relations(
            conn,
            relations,
            database=target.database,
            sample_limit=sample_limit,
            limit=limit,
        )
    finally:
        conn.close()
    if out_dir is not None:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        if out_report is None:
            out_report = out_dir / "join_validate.yaml"
        if out_markdown is None:
            out_markdown = out_dir / "join_validate.md"
    if out_report is not None:
        out_report.parent.mkdir(parents=True, exist_ok=True)
        out_report.write_text(
            yaml.safe_dump(report, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        report["out_report"] = str(out_report)
    if out_markdown is not None:
        out_markdown.parent.mkdir(parents=True, exist_ok=True)
        out_markdown.write_text(render_markdown_report(report), encoding="utf-8")
        report["out_markdown"] = str(out_markdown)
    return report


def _current_database(conn: Any) -> str:
    with conn.cursor() as cur:
        cur.execute("SELECT DATABASE() AS db")
        row = cur.fetchone() or {}
    return str(row.get("db") or "")


def _endpoint_stats(
    conn: Any,
    schema: str,
    table: str,
    column: str,
    *,
    sample_limit: int,
) -> EndpointStats:
    stats = EndpointStats(table=table, column=column)
    if not _column_exists(conn, schema, table, column):
        stats.exists = False
        stats.error = "column not found"
        return stats
    t = sql_ident(table)
    c = sql_ident(column)
    s = sql_ident(schema)
    usable = _usable_predicate("t", column)
    try:
        with conn.cursor() as cur:
            # One pass for row / usable counts; distinct separately (needed for verdicts).
            cur.execute(
                f"""
                SELECT
                  COUNT(*) AS row_count,
                  SUM(CASE WHEN {usable} THEN 1 ELSE 0 END) AS non_null
                FROM {s}.{t} AS t
                """
            )
            row = cur.fetchone() or {}
            stats.row_count = int(row.get("row_count") or 0)
            stats.non_null = int(row.get("non_null") or 0)
            if stats.non_null == 0:
                stats.distinct_non_null = 0
                stats.sample = []
                return stats
            cur.execute(
                f"SELECT COUNT(DISTINCT t.{c}) AS n FROM {s}.{t} AS t WHERE {usable}"
            )
            stats.distinct_non_null = int((cur.fetchone() or {}).get("n") or 0)
            # Cheap sample without GROUP BY full scan when high-cardinality PK-like.
            cur.execute(
                f"""
                SELECT CAST(t.{c} AS CHAR) AS v
                FROM {s}.{t} AS t
                WHERE {usable}
                LIMIT %s
                """,
                (sample_limit,),
            )
            stats.sample = [
                str(r.get("v"))
                for r in (cur.fetchall() or [])
                if r.get("v") is not None
            ]
    except Exception as exc:  # noqa: BLE001
        stats.error = str(exc)
    return stats


def _fill_pair_metrics(
    conn: Any,
    schema: str,
    probe: JoinProbe,
    *,
    sample_limit: int,
) -> None:
    """Probe overlap via distinct-set joins (avoids slow correlated NOT IN)."""
    lt, lc = parse_fq(probe.left)
    rt, rc = parse_fq(probe.right)
    s = sql_ident(schema)
    a, ax = sql_ident(lt), sql_ident(lc)
    b, by = sql_ident(rt), sql_ident(rc)
    a_ok = _usable_predicate("a", lc)
    b_ok = _usable_predicate("b", rc)
    a_v = f"CAST(a.{ax} AS CHAR)"
    b_v = f"CAST(b.{by} AS CHAR)"
    la = f"(SELECT DISTINCT {a_v} AS v FROM {s}.{a} AS a WHERE {a_ok}) AS la"
    lb = f"(SELECT DISTINCT {b_v} AS v FROM {s}.{b} AS b WHERE {b_ok}) AS lb"

    with conn.cursor() as cur:
        # Distinct intersection size — cheap empty check.
        cur.execute(
            f"SELECT COUNT(*) AS n FROM {la} INNER JOIN {lb} ON la.v = lb.v"
        )
        distinct_inter = int((cur.fetchone() or {}).get("n") or 0)

        if distinct_inter == 0:
            left_nn = int((probe.left_stats.non_null if probe.left_stats else 0) or 0)
            right_nn = int(
                (probe.right_stats.non_null if probe.right_stats else 0) or 0
            )
            probe.join_hits = 0
            probe.left_in_right = 0
            probe.left_not_in_right = left_nn
            probe.right_in_left = 0
            probe.right_not_in_left = right_nn
            probe.left_in_right_ratio = 0.0
            probe.right_in_left_ratio = 0.0
            probe.intersection_sample = []
            # One-sided samples only (prove emptiness).
            cur.execute(
                f"SELECT la.v FROM {la} LIMIT %s",
                (sample_limit,),
            )
            probe.left_only_sample = [
                str(row.get("v"))
                for row in (cur.fetchall() or [])
                if row.get("v") is not None
            ]
            cur.execute(
                f"SELECT lb.v FROM {lb} LIMIT %s",
                (sample_limit,),
            )
            probe.right_only_sample = [
                str(row.get("v"))
                for row in (cur.fetchall() or [])
                if row.get("v") is not None
            ]
            return

        # Row-level inclusion via LEFT JOIN to the other side's distinct set.
        cur.execute(
            f"""
            SELECT
              SUM(CASE WHEN lb.v IS NOT NULL THEN 1 ELSE 0 END) AS in_cnt,
              SUM(CASE WHEN lb.v IS NULL THEN 1 ELSE 0 END) AS not_in_cnt
            FROM {s}.{a} AS a
            LEFT JOIN {lb} ON {a_v} = lb.v
            WHERE {a_ok}
            """
        )
        row = cur.fetchone() or {}
        probe.left_in_right = int(row.get("in_cnt") or 0)
        probe.left_not_in_right = int(row.get("not_in_cnt") or 0)

        cur.execute(
            f"""
            SELECT
              SUM(CASE WHEN la.v IS NOT NULL THEN 1 ELSE 0 END) AS in_cnt,
              SUM(CASE WHEN la.v IS NULL THEN 1 ELSE 0 END) AS not_in_cnt
            FROM {s}.{b} AS b
            LEFT JOIN {la} ON {b_v} = la.v
            WHERE {b_ok}
            """
        )
        row = cur.fetchone() or {}
        probe.right_in_left = int(row.get("in_cnt") or 0)
        probe.right_not_in_left = int(row.get("not_in_cnt") or 0)

        # Avoid COUNT(*) of A⋈B (cartesian blow-up on many-to-many).
        # Use matching left-row count as the join-hit proxy.
        probe.join_hits = probe.left_in_right

        cur.execute(
            f"SELECT la.v FROM {la} INNER JOIN {lb} ON la.v = lb.v LIMIT %s",
            (sample_limit,),
        )
        probe.intersection_sample = [
            str(row.get("v"))
            for row in (cur.fetchall() or [])
            if row.get("v") is not None
        ]
        cur.execute(
            f"""
            SELECT la.v FROM {la}
            LEFT JOIN {lb} ON la.v = lb.v
            WHERE lb.v IS NULL
            LIMIT %s
            """,
            (sample_limit,),
        )
        probe.left_only_sample = [
            str(row.get("v"))
            for row in (cur.fetchall() or [])
            if row.get("v") is not None
        ]
        cur.execute(
            f"""
            SELECT lb.v FROM {lb}
            LEFT JOIN {la} ON lb.v = la.v
            WHERE la.v IS NULL
            LIMIT %s
            """,
            (sample_limit,),
        )
        probe.right_only_sample = [
            str(row.get("v"))
            for row in (cur.fetchall() or [])
            if row.get("v") is not None
        ]

    left_nn = float((probe.left_stats.non_null if probe.left_stats else 0) or 0)
    right_nn = float((probe.right_stats.non_null if probe.right_stats else 0) or 0)
    if left_nn > 0 and probe.left_in_right is not None:
        probe.left_in_right_ratio = round(probe.left_in_right / left_nn, 4)
    if right_nn > 0 and probe.right_in_left is not None:
        probe.right_in_left_ratio = round(probe.right_in_left / right_nn, 4)


def _usable_predicate(alias: str, column: str) -> str:
    """Lightweight non-null / non-blank filter (avoid TRIM/LOWER on every row)."""
    col = sql_ident(column)
    return (
        f"{alias}.{col} IS NOT NULL "
        f"AND CAST({alias}.{col} AS CHAR) <> '' "
        f"AND CAST({alias}.{col} AS CHAR) <> 'null' "
        f"AND CAST({alias}.{col} AS CHAR) <> 'none' "
        f"AND CAST({alias}.{col} AS CHAR) <> 'NULL' "
        f"AND CAST({alias}.{col} AS CHAR) <> 'NONE'"
    )


def _column_exists(conn: Any, schema: str, table: str, column: str) -> bool:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT 1 AS ok
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s AND COLUMN_NAME=%s
            LIMIT 1
            """,
            (schema, table, column),
        )
        return cur.fetchone() is not None


def _decide_verdict(probe: JoinProbe) -> tuple[str, str]:
    jh = probe.join_hits or 0
    lir = probe.left_in_right or 0
    ril = probe.right_in_left or 0
    lr = probe.left_in_right_ratio or 0.0
    rr = probe.right_in_left_ratio or 0.0
    left_d = int(
        (probe.left_stats.distinct_non_null if probe.left_stats else 0) or 0
    )
    right_d = int(
        (probe.right_stats.distinct_non_null if probe.right_stats else 0) or 0
    )
    if jh == 0 and lir == 0 and ril == 0:
        return (
            "impossible",
            "no shared values: join_hits=0 and both inclusion counts are 0 "
            "(cannot be an equi-join / same business key in this DB)",
        )
    # Negligible accidental collisions on large domains (UUID vs business code).
    if (
        (jh > 0 or lir > 0 or ril > 0)
        and max(lr, rr) < 0.02
        and min(left_d, right_d) >= 20
    ):
        return (
            "false_friend",
            f"negligible overlap on large domains "
            f"(left->right={lr}, right->left={rr}, join_hits={jh}, "
            f"distinct L/R={left_d}/{right_d}); not a usable equi-join",
        )
    if rr >= 0.95 and (probe.right_stats and (probe.right_stats.non_null or 0) >= 5):
        return (
            "fk_like",
            f">=95% of right-side rows resolve on left (ratio={rr}); "
            "consistent with FK / identity reference",
        )
    if lr >= 0.5 and rr >= 0.5:
        return (
            "shared_domain",
            f"two-way overlap (left->right={lr}, right->left={rr}); "
            "same value domain / business code space likely",
        )
    if jh > 0 or lir > 0 or ril > 0:
        return (
            "weak_overlap",
            f"non-empty but thin overlap (left->right={lr}, right->left={rr}, "
            f"join_hits={jh})",
        )
    return ("weak_overlap", "unexpected empty metrics")


def _probe_to_dict(probe: JoinProbe) -> dict[str, Any]:
    packed = asdict(probe)
    if not packed.get("error"):
        packed.pop("error", None)
    return packed
