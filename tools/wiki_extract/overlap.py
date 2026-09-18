"""Value-overlap measurement for L0 JOIN candidates.

Skip lists, type compatibility, join roles, and likely/unlikely thresholds
live in join_policy. This module samples, measures bag inclusion, and merges
results onto proposed EQUI_JOIN edges.
"""

from __future__ import annotations

import datetime as dt
from typing import Any

from tools.wiki_extract.heuristics import _exclude_join_rights_from_anchors
from tools.wiki_extract.join_policy import (
    Inclusion,
    child_endpoint_reason,
    decide_authenticity,
    is_fk_like,
    may_nominate_join,
    mysql_type_of,
    parent_join_columns,
    parse_fq,
    prefix_token_score,
    qualify,
    sql_ident,
    stamp_join_meta,
    types_compatible,
)

DEFAULT_K = 200
EXPAND_K = 800
WINDOW_LIMIT = 12

# Re-exports so tests and LLM keep a stable import path.
skip_overlap_child = child_endpoint_reason
validate_proposed_join = may_nominate_join


def apply_overlap(model: dict[str, Any], packed: dict[str, Any]) -> dict[str, Any]:
    """Merge overlap.yaml into compiled relations. Never deletes name-nominated edges."""
    by_pair: dict[tuple[str, str], dict[str, Any]] = {}
    for raw in packed.get("edges") or []:
        if not isinstance(raw, dict):
            continue
        left = str(raw.get("left") or "")
        right = str(raw.get("right") or "")
        if left and right:
            by_pair[(left, right)] = raw
    skipped = {str(x) for x in (packed.get("skipped_columns") or []) if x}
    stats = {
        "probed": 0,
        "likely": 0,
        "unlikely": 0,
        "unknown": 0,
        "llm_added": 0,
        "overlap_added": 0,
        "name_only_unprobed": 0,
        "deepened": 0,
        "skipped": 0,
    }

    for tname, compiled in (model.get("tables") or {}).items():
        for rel in compiled.get("relations") or []:
            left = str(rel.get("left") or "")
            right = str(rel.get("right") or "")
            _, child_col = parse_fq(right)
            fq = qualify(tname, child_col)
            reason = child_endpoint_reason(
                child_col, mysql_type_of(compiled, child_col)
            )
            if reason or fq in skipped or child_col in skipped:
                rel["overlap"] = {
                    "probed": False,
                    "skipped": reason or "skipped_generic_column",
                }
                stats["skipped"] += 1
                continue
            hit = by_pair.get((left, right))
            if not hit:
                rel.setdefault("overlap", {"probed": False})
                stats["name_only_unprobed"] += 1
                continue
            _write_overlap_on_rel(rel, hit)
            _count_overlap(stats, rel)

        existing = {
            (str(r.get("left") or ""), str(r.get("right") or ""))
            for r in compiled.get("relations") or []
        }
        added = False
        for (left, right), raw in by_pair.items():
            child, _child_col = parse_fq(right)
            if child != tname or (left, right) in existing:
                continue
            if str(raw.get("source") or "overlap") == "name":
                continue
            if str(raw.get("authenticity") or "") != "likely":
                continue
            if may_nominate_join(model, left, right, for_overlap_add=True):
                continue
            compiled.setdefault("relations", []).append(
                _new_overlap_relation(compiled, raw)
            )
            existing.add((left, right))
            stats["overlap_added"] += 1
            _count_overlap(stats, compiled["relations"][-1])
            added = True
        if added:
            _exclude_join_rights_from_anchors(compiled)
        stamp_join_meta(compiled)

    model["_overlap"] = packed
    model["overlap_stats"] = stats
    packed.setdefault("stats", stats)
    return model


def _count_overlap(stats: dict[str, int], rel: dict[str, Any]) -> None:
    ov = rel.get("overlap") or {}
    if ov.get("probed"):
        stats["probed"] = stats.get("probed", 0) + 1
    if ov.get("deepened"):
        stats["deepened"] = stats.get("deepened", 0) + 1
    auth = str(ov.get("authenticity") or rel.get("authenticity") or "unknown")
    if auth in stats:
        stats[auth] = stats.get(auth, 0) + 1


def _write_overlap_on_rel(rel: dict[str, Any], hit: dict[str, Any]) -> None:
    auth = str(hit.get("authenticity") or "unknown").lower()
    if auth not in {"likely", "unlikely", "unknown"}:
        auth = "unknown"
    rel["overlap"] = {
        "probed": True,
        "ratio": hit.get("overlap_ratio"),
        "ratio_reverse": hit.get("overlap_ratio_reverse"),
        "sample_size": hit.get("sample_size"),
        "miss": hit.get("miss"),
        "deepened": bool(hit.get("deepened")),
        "query_ok": hit.get("query_ok", True),
        "authenticity": auth,
    }
    rel["authenticity"] = auth
    hit_source = str(hit.get("source") or "overlap")
    if str(rel.get("source") or "name") == "name" and hit_source in {
        "overlap",
        "both",
        "name",
    }:
        if hit_source != "name":
            rel["source"] = "both"
    evid = str(rel.get("evidence") or "")
    profile_ev = str(hit.get("evidence") or "")
    if profile_ev and profile_ev not in evid:
        rel["evidence"] = f"{evid};{profile_ev}" if evid else profile_ev


def _new_overlap_relation(
    compiled: dict[str, Any], raw: dict[str, Any]
) -> dict[str, Any]:
    left = str(raw.get("left") or "")
    right = str(raw.get("right") or "")
    child_col = parse_fq(right)[1]
    auth = str(raw.get("authenticity") or "likely")
    comment = _field_desc(compiled, child_col)
    return {
        "type": "EQUI_JOIN",
        "left": left,
        "right": right,
        "cardinality": "one_to_many",
        "trust": "proposed",
        "authenticity": auth,
        "source": "overlap",
        "name_evidence": {
            "match": "none",
            "stem": child_col,
            "comment": comment,
        },
        "overlap": {
            "probed": True,
            "ratio": raw.get("overlap_ratio"),
            "ratio_reverse": raw.get("overlap_ratio_reverse"),
            "sample_size": raw.get("sample_size"),
            "miss": raw.get("miss"),
            "deepened": bool(raw.get("deepened")),
            "query_ok": raw.get("query_ok", True),
            "authenticity": auth,
        },
        "evidence": str(
            raw.get("evidence")
            or f"database_profile:{compiled.get('database')}.{compiled.get('table')}.{child_col}"
        ),
    }


def build_join_window(
    tname: str, compiled: dict[str, Any], model: dict[str, Any]
) -> list[dict[str, Any]]:
    """Per-column bounded parents; only type-compatible identity columns."""
    resolved_rights = {
        parse_fq(str(r.get("right") or ""))[1] for r in compiled.get("relations") or []
    }
    tables = model.get("tables") or {}
    probes = _probe_index(model)
    out: list[dict[str, Any]] = []
    pk = set(compiled.get("primary_key") or [])
    child_type_cache = {
        col: mysql_type_of(compiled, col)
        for col in (compiled.get("column_names") or [])
    }
    for col in compiled.get("column_names") or []:
        if col in pk or col in resolved_rights or not is_fk_like(col):
            continue
        if child_endpoint_reason(col, child_type_cache.get(col, "")):
            continue
        parents: list[dict[str, Any]] = []
        for parent, pcomp in tables.items():
            if parent == tname:
                continue
            score = prefix_token_score(tname, parent)
            comment_hit = _comment_points_at(
                f"{_field_desc(compiled, col)} {compiled.get('description') or ''}",
                parent,
                str(pcomp.get("description") or ""),
            )
            if score <= 0 and not comment_hit:
                continue
            for ident in parent_join_columns(pcomp):
                left = qualify(parent, ident)
                if not types_compatible(
                    child_type_cache.get(col, ""), mysql_type_of(pcomp, ident)
                ):
                    continue
                if may_nominate_join(model, left, qualify(tname, col)):
                    continue
                probe = probes.get((qualify(tname, col), left), {})
                parents.append(
                    {
                        "left": left,
                        "table": parent,
                        "table_comment": str(pcomp.get("description") or "")[:80],
                        "prefix_score": score,
                        "comment_hit": comment_hit,
                        "overlap": probe or {"probed": False, "status": "not_probed"},
                    }
                )
        parents.sort(
            key=lambda item: (
                1 if (item.get("overlap") or {}).get("probed") else 0,
                int(item.get("prefix_score") or 0),
                1 if item.get("comment_hit") else 0,
            ),
            reverse=True,
        )
        parents = parents[:WINDOW_LIMIT]
        if not parents:
            continue
        out.append(
            {
                "column": col,
                "comment": _field_desc(compiled, col),
                "candidates": parents,
            }
        )
    return out


def window_lefts_for_column(window: list[dict[str, Any]], column: str) -> set[str]:
    for item in window:
        if item.get("column") == column:
            return {
                str(c.get("left") or "")
                for c in (item.get("candidates") or [])
                if c.get("left")
            }
    return set()


def overlap_from_window(
    window: list[dict[str, Any]], column: str, left: str
) -> dict[str, Any]:
    for item in window:
        if item.get("column") != column:
            continue
        for cand in item.get("candidates") or []:
            if cand.get("left") == left:
                ov = cand.get("overlap")
                return (
                    ov
                    if isinstance(ov, dict)
                    else {"probed": False, "status": "not_probed"}
                )
    return {"probed": False, "status": "not_probed"}


def _probe_index(
    model: dict[str, Any],
) -> dict[tuple[str, str], dict[str, Any]]:
    packed = model.get("_overlap") or {}
    out: dict[tuple[str, str], dict[str, Any]] = {}
    for group in ("edges", "unresolved_probes"):
        for raw in packed.get(group) or []:
            if not isinstance(raw, dict):
                continue
            right = str(raw.get("right") or "")
            left = str(raw.get("left") or "")
            if right and left:
                out[(right, left)] = {
                    "probed": True,
                    "ratio": raw.get("overlap_ratio"),
                    "ratio_reverse": raw.get("overlap_ratio_reverse"),
                    "sample_size": raw.get("sample_size"),
                    "authenticity": raw.get("authenticity") or "unknown",
                }
    return out


def _field_desc(compiled: dict[str, Any], column: str) -> str:
    for field in compiled.get("fields") or []:
        if field.get("name") == column:
            return str(field.get("description") or "")[:80]
    return ""


def _comment_points_at(blob: str, table: str, table_comment: str) -> bool:
    text = blob or ""
    if table and table in text:
        return True
    label = (table_comment or "").strip()
    if len(label) < 4:
        return False
    return label in text


def probe_overlap(
    conn: Any,
    catalog: dict[str, Any],
    model: dict[str, Any],
    *,
    k: int = DEFAULT_K,
) -> dict[str, Any]:
    session = _ProbeSession(conn, catalog, model, k=k)
    schema = str(catalog.get("database") or model.get("database") or "")
    stamp = dt.date.today().isoformat()
    edges: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    skipped: list[str] = []
    seen: set[tuple[str, str]] = set()

    for tname, compiled in (model.get("tables") or {}).items():
        for rel in compiled.get("relations") or []:
            left = str(rel.get("left") or "")
            right = str(rel.get("right") or "")
            child_col = parse_fq(right)[1]
            reason = child_endpoint_reason(
                child_col, mysql_type_of(compiled, child_col)
            )
            if reason:
                skipped.append(qualify(tname, child_col))
                continue
            reject = may_nominate_join(model, left, right)
            if reject == "type_mismatch":
                packed = _skipped_pair(left, right, "name", reject)
                edges.append(packed)
                seen.add((left, right))
                continue
            packed = session.probe(left, right, source="name")
            if packed:
                edges.append(packed)
                seen.add((left, right))

        window = build_join_window(tname, compiled, model)
        for item in window:
            col = str(item.get("column") or "")
            right = qualify(tname, col)
            for cand in item.get("candidates") or []:
                left = str(cand.get("left") or "")
                if not left or (left, right) in seen:
                    continue
                packed = session.probe(left, right, source="overlap")
                if not packed:
                    continue
                seen.add((left, right))
                if packed.get("authenticity") == "likely":
                    edges.append(packed)
                else:
                    unresolved.append(packed)

    return {
        "schema_version": "1.0",
        "generated_at": stamp,
        "source": "tools.wiki_extract.overlap",
        "database": schema,
        "k": k,
        "edges": edges,
        "unresolved_probes": unresolved,
        "skipped_columns": sorted(set(skipped)),
    }


def _skipped_pair(left: str, right: str, source: str, reason: str) -> dict[str, Any]:
    return {
        "left": left,
        "right": right,
        "source": source,
        "sample_size": 0,
        "overlap_ratio": None,
        "overlap_ratio_reverse": None,
        "deepened": False,
        "miss": None,
        "query_ok": False,
        "authenticity": "unknown",
        "skip": reason,
        "evidence": f"database_profile:{right}",
    }


class _ProbeSession:
    """Cache one value bag per (table, column, k)."""

    def __init__(
        self, conn: Any, catalog: dict[str, Any], model: dict[str, Any], *, k: int
    ) -> None:
        self.conn = conn
        self.catalog = catalog
        self.model = model
        self.k = k
        self.schema = str(catalog.get("database") or model.get("database") or "")
        self._bags: dict[tuple[str, str, int], list[Any]] = {}

    def probe(self, left: str, right: str, *, source: str) -> dict[str, Any] | None:
        parent, left_col = parse_fq(left)
        child, right_col = parse_fq(right)
        bag = self.bag(child, right_col, self.k)
        forward = self.inclusion(parent, left_col, bag)
        decision = decide_authenticity(
            sample_size=forward.sample_size,
            forward=forward.ratio,
            query_ok=forward.ok,
            deepened=False,
        )
        reverse_ratio: float | None = None
        deepened = False
        sample_size = forward.sample_size
        miss = forward.miss
        ratio = forward.ratio
        query_ok = forward.ok
        if decision.deepen:
            big = self.bag(child, right_col, min(EXPAND_K, max(self.k * 3, self.k)))
            forward = self.inclusion(parent, left_col, big)
            sample_size = forward.sample_size
            miss = forward.miss
            ratio = forward.ratio
            query_ok = query_ok and forward.ok
            parent_bag = self.bag(parent, left_col, self.k)
            rev = self.inclusion(child, right_col, parent_bag)
            reverse_ratio = rev.ratio if rev.ok else None
            query_ok = query_ok and rev.ok
            decision = decide_authenticity(
                sample_size=sample_size,
                forward=ratio,
                reverse=reverse_ratio,
                query_ok=query_ok,
                deepened=True,
            )
            deepened = True
        return {
            "left": left,
            "right": right,
            "source": source,
            "sample_size": sample_size,
            "overlap_ratio": None if ratio is None else round(ratio, 4),
            "overlap_ratio_reverse": (
                None if reverse_ratio is None else round(reverse_ratio, 4)
            ),
            "deepened": deepened,
            "miss": miss,
            "query_ok": query_ok,
            "authenticity": decision.value,
            "evidence": f"database_profile:{self.schema}.{child}.{right_col}",
        }

    def bag(self, table: str, column: str, k: int) -> list[Any]:
        key = (table, column, k)
        if key not in self._bags:
            self._bags[key] = _sample_column(
                self.conn, self.schema, self.catalog, table, column, k
            )
        return self._bags[key]

    def inclusion(self, table: str, column: str, values: list[Any]) -> Inclusion:
        return _bag_inclusion(self.conn, self.schema, table, column, values)


def _sample_column(
    conn: Any,
    schema: str,
    catalog: dict[str, Any],
    table: str,
    column: str,
    k: int,
) -> list[Any]:
    tmeta = (catalog.get("tables") or {}).get(table) or {}
    columns = tmeta.get("columns") or {}
    if column not in columns:
        return []
    order_row = (
        "id" if "id" in columns else ("create_time" if "create_time" in columns else "")
    )
    bags: list[Any] = []
    if order_row:
        bags.extend(_fetch_top(conn, schema, table, column, k, order_col=order_row))
    indexed = {
        str(c)
        for idx in (tmeta.get("indexes") or [])
        for c in (idx.get("columns") or [])
    }
    if column in indexed and column != order_row:
        bags.extend(_fetch_top(conn, schema, table, column, k, order_col=column))
    out: list[Any] = []
    seen: set[str] = set()
    for val in bags:
        if val is None:
            continue
        key = str(val)
        if key in seen:
            continue
        seen.add(key)
        out.append(val)
        if len(out) >= k:
            break
    return out


def _fetch_top(
    conn: Any,
    schema: str,
    table: str,
    column: str,
    k: int,
    *,
    order_col: str,
) -> list[Any]:
    sql = (
        f"SELECT {sql_ident(column)} AS v FROM {sql_ident(schema)}.{sql_ident(table)} "
        f"WHERE {sql_ident(column)} IS NOT NULL "
        f"ORDER BY {sql_ident(order_col)} DESC LIMIT %s"
    )
    return _fetch_values(conn, sql, (k,))


def cap_inclusion(hit: int, size: int) -> tuple[int, float | None]:
    """Bag-inclusion hit may exceed the sampled bag; ratio is always ≤ 1."""
    if size <= 0:
        return 0, None
    capped = min(max(int(hit), 0), int(size))
    return capped, capped / size


def _bag_inclusion(
    conn: Any, schema: str, table: str, column: str, values: list[Any]
) -> Inclusion:
    """How many distinct bag values exist in table.column (not parent row count)."""
    if not values:
        return Inclusion(ok=True, hit=0, sample_size=0, ratio=None)
    placeholders = ",".join(["%s"] * len(values))
    sql = (
        f"SELECT COUNT(DISTINCT {sql_ident(column)}) AS hit "
        f"FROM {sql_ident(schema)}.{sql_ident(table)} "
        f"WHERE {sql_ident(column)} IN ({placeholders})"
    )
    try:
        with conn.cursor() as cur:
            cur.execute(sql, tuple(values))
            row = cur.fetchone() or {}
            hit = int(row.get("hit") or 0)
    except Exception:
        return Inclusion(ok=False, hit=0, sample_size=len(values), ratio=None)
    size = len(values)
    capped_hit, ratio = cap_inclusion(hit, size)
    return Inclusion(ok=True, hit=capped_hit, sample_size=size, ratio=ratio)


def _fetch_values(conn: Any, sql: str, params: tuple[Any, ...]) -> list[Any]:
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return [row.get("v") for row in cur.fetchall() if row.get("v") is not None]
    except Exception:
        return []


def sync_overlap_from_relations(
    model: dict[str, Any], packed: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Ensure LLM-proposed edges appear in _raw/overlap.yaml for traceability."""
    base = packed if packed is not None else (model.get("_overlap") or {})
    out = dict(base)
    edges = [dict(e) for e in (base.get("edges") or []) if isinstance(e, dict)]
    seen = {
        (str(e.get("left") or ""), str(e.get("right") or ""))
        for e in edges
        if e.get("left") and e.get("right")
    }
    for compiled in (model.get("tables") or {}).values():
        for rel in compiled.get("relations") or []:
            left = str(rel.get("left") or "")
            right = str(rel.get("right") or "")
            if not left or not right or (left, right) in seen:
                continue
            ov = rel.get("overlap") if isinstance(rel.get("overlap"), dict) else {}
            edges.append(
                {
                    "left": left,
                    "right": right,
                    "source": str(rel.get("source") or "name"),
                    "sample_size": ov.get("sample_size"),
                    "overlap_ratio": ov.get("ratio"),
                    "overlap_ratio_reverse": ov.get("ratio_reverse"),
                    "deepened": bool(ov.get("deepened")),
                    "miss": ov.get("miss"),
                    "query_ok": ov.get("query_ok", ov.get("probed")),
                    "authenticity": str(
                        ov.get("authenticity") or rel.get("authenticity") or "unknown"
                    ),
                    "evidence": rel.get("evidence"),
                    "probed": bool(ov.get("probed")),
                    "name_evidence": rel.get("name_evidence"),
                    "join_role": rel.get("join_role"),
                    "priority": rel.get("priority"),
                }
            )
            seen.add((left, right))
    out["edges"] = edges
    model["_overlap"] = out
    return out
