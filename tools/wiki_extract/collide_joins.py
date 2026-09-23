"""Cartesian field collide: TopK value bags → drop zero-hit pairs.

Stage-1 recall filter (do not miss):

1. Every joinable column vs every other table's joinable column (same type family).
2. Sample TopK per column via three paths: latest rows, ORDER BY col DESC,
   ORDER BY col ASC.
3. Keep a pair if bag_A values exist in B.col OR bag_B values exist in A.col
   (or bags already intersect in memory). Zero-hit pairs are dropped.
4. Ignore bare ``A.id ↔ B.id``, temporal types, and text/json/blob types.

Survivors feed later refine (validate_joins / patterns / code) — this module
does not write wiki fences.
"""

from __future__ import annotations

import datetime as dt
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from tools.wiki_extract.connect import connect, resolve_dsn
from tools.wiki_extract.join_policy import (
    TEMPORAL_TYPES,
    mysql_base,
    qualify,
    sql_ident,
    type_family,
    types_compatible,
)

DEFAULT_K = 50
# Load full distinct sets when cardinality fits; else fall back to TopK IN probes.
DISTINCT_CAP = 20000
BLOBISH_TYPES = frozenset(
    {
        "text",
        "tinytext",
        "mediumtext",
        "longtext",
        "blob",
        "tinyblob",
        "mediumblob",
        "longblob",
        "json",
        "binary",
        "varbinary",
        "bit",
    }
)
# Undirected pair progress / output key.
_PAIR_SEP = "||"
_PROGRESS_BATCH = 5000


@dataclass(frozen=True)
class Endpoint:
    table: str
    column: str
    mysql_type: str
    family: str

    @property
    def fq(self) -> str:
        return qualify(self.table, self.column)


def run_collide(
    *,
    wiki_dir: Path,
    out_dir: Path,
    db_url: str = "",
    database: str = "",
    k: int = DEFAULT_K,
    workers: int = 8,
    limit: int = 0,
    resume: bool = True,
) -> dict[str, Any]:
    wiki_dir = Path(wiki_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    raw = wiki_dir / "_raw"
    catalog_path = raw / "catalog.yaml"
    if not catalog_path.exists():
        raise FileNotFoundError(f"missing catalog: {catalog_path}")
    catalog = yaml.safe_load(catalog_path.read_text()) or {}
    schema = (database or "").strip() or str(catalog.get("database") or "")
    if not schema:
        raise ValueError("database name required (--database or catalog.database)")

    endpoints = build_endpoints(catalog)
    target = resolve_dsn(db_url=db_url, database=schema)

    # Sample all endpoints first; drop empty bags before cartesian expand.
    bags = sample_all_bags(
        None,
        schema,
        catalog,
        endpoints,
        k=k,
        workers=workers,
        db_url=db_url,
        database=schema,
    )
    live_endpoints = [e for e in endpoints if bags.get(e.fq)]
    print(
        f"endpoints total={len(endpoints)} with_values={len(live_endpoints)}",
        flush=True,
    )
    pairs = list(iter_pairs(live_endpoints))
    if limit > 0:
        pairs = pairs[:limit]

    distincts = load_distinct_sets(
        None,
        schema,
        live_endpoints,
        bags,
        cap=DISTINCT_CAP,
        workers=workers,
        db_url=db_url,
        database=schema,
    )

    # Persist bag sizes only (full values are large / non-YAML-safe); keep in memory.
    _write_yaml(
        out_dir / "bags_meta.yaml",
        {
            "schema_version": "1.0",
            "generated_at": dt.date.today().isoformat(),
            "k": k,
            "endpoints": len(endpoints),
            "distinct_cached": sum(1 for v in distincts.values() if v is not None),
            "distinct_cap": DISTINCT_CAP,
            "bags": {
                fq: {"size": len(vals)}
                for fq, vals in sorted(bags.items())
            },
        },
    )

    progress_meta = out_dir / "progress_meta.json"
    hits_path = out_dir / "hits.jsonl"
    start_index = 0
    prior_hits: list[dict[str, Any]] = []
    if not resume:
        if progress_meta.exists():
            progress_meta.unlink()
        if hits_path.exists():
            hits_path.unlink()
    elif progress_meta.exists():
        meta = json.loads(progress_meta.read_text(encoding="utf-8"))
        start_index = int(meta.get("next_index") or 0)
        if hits_path.exists():
            prior_hits = _load_hits(hits_path)

    pending = pairs[start_index:]
    stats: dict[str, Any] = {
        "endpoints": len(endpoints),
        "pairs_total": len(pairs),
        "pairs_pending": len(pending),
        "pairs_resumed": start_index,
        "k": k,
        "workers": workers,
        "distinct_cached": sum(1 for v in distincts.values() if v is not None),
        "hit_sample_intersect": 0,
        "hit_distinct_cache": 0,
        "hit_sql": 0,
        "miss_zero": 0,
        "empty_bag": 0,
        "query_error": 0,
    }
    for row in prior_hits:
        _count_hit(stats, row)

    survivors: list[dict[str, Any]] = list(prior_hits)
    lock = threading.Lock()
    t0 = time.time()
    local = threading.local()

    def get_conn() -> Any:
        c = getattr(local, "conn", None)
        if c is None:
            c = connect(target)
            local.conn = c
        return c

    def probe_one(left: Endpoint, right: Endpoint) -> dict[str, Any]:
        return _probe_pair(
            left,
            right,
            bags=bags,
            distincts=distincts,
            schema=schema,
            get_conn=get_conn,
        )

    with hits_path.open("a", encoding="utf-8") as hits_fh, ThreadPoolExecutor(
        max_workers=max(1, workers)
    ) as pool:
        done_n = 0
        for batch_start in range(0, len(pending), _PROGRESS_BATCH):
            chunk = pending[batch_start : batch_start + _PROGRESS_BATCH]
            futures = [pool.submit(probe_one, a, b) for a, b in chunk]
            batch_rows = [fut.result() for fut in as_completed(futures)]
            with lock:
                for row in batch_rows:
                    done_n += 1
                    _count_hit(stats, row)
                    if row.get("hit"):
                        survivors.append(row)
                        hits_fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                next_index = start_index + batch_start + len(chunk)
                hits_fh.flush()
                progress_meta.write_text(
                    json.dumps({"next_index": next_index, "pairs_total": len(pairs)}),
                    encoding="utf-8",
                )
                elapsed = time.time() - t0
                rate = done_n / elapsed if elapsed > 0 else 0
                hits = (
                    stats["hit_sample_intersect"]
                    + stats["hit_distinct_cache"]
                    + stats["hit_sql"]
                )
                print(
                    f"collide {next_index}/{len(pairs)} "
                    f"hits={hits} zero={stats['miss_zero']} "
                    f"{rate:.0f}/s",
                    flush=True,
                )

    hit_rows = [r for r in survivors if r.get("hit")]
    by_key: dict[str, dict[str, Any]] = {}
    for r in hit_rows:
        by_key[str(r.get("key") or "")] = r
    hit_rows = sorted(
        by_key.values(), key=lambda r: (r.get("left") or "", r.get("right") or "")
    )

    removed = _load_removed_pairs(wiki_dir)
    existing = _load_existing_pairs(wiki_dir)
    filtered: list[dict[str, Any]] = []
    skipped_removed = 0
    skipped_existing = 0
    for r in hit_rows:
        pk = _undirected_fq(str(r.get("left") or ""), str(r.get("right") or ""))
        if pk in removed:
            skipped_removed += 1
            continue
        if pk in existing:
            skipped_existing += 1
            continue
        filtered.append(r)

    stats.update(
        {
            "survivors_raw": len(hit_rows),
            "survivors_new": len(filtered),
            "skipped_removed": skipped_removed,
            "skipped_existing": skipped_existing,
            "elapsed_sec": round(time.time() - t0, 1),
        }
    )

    payload = {
        "schema_version": "1.0",
        "generated_at": dt.date.today().isoformat(),
        "source": "tools.wiki_extract.collide_joins",
        "database": schema,
        "stats": stats,
        "survivors": filtered,
    }
    _write_yaml(out_dir / "survivors.yaml", payload)
    (out_dir / "summary.md").write_text(
        _summary_md(stats, filtered[:80]), encoding="utf-8"
    )
    _write_priority_candidates(out_dir / "hits.jsonl", out_dir / "priority_candidates.jsonl")
    return payload


def build_endpoints(catalog: dict[str, Any]) -> list[Endpoint]:
    out: list[Endpoint] = []
    for tname, tmeta in (catalog.get("tables") or {}).items():
        if not isinstance(tmeta, dict):
            continue
        for col, cmeta in (tmeta.get("columns") or {}).items():
            if not isinstance(cmeta, dict):
                continue
            mtype = str(cmeta.get("type") or "")
            base = mysql_base(mtype)
            if base in TEMPORAL_TYPES or base in BLOBISH_TYPES:
                continue
            fam = type_family(mtype)
            if fam not in {"number", "string"}:
                continue
            out.append(Endpoint(table=str(tname), column=str(col), mysql_type=mtype, family=fam))
    out.sort(key=lambda e: (e.table, e.column))
    return out


def iter_pairs(endpoints: list[Endpoint]) -> list[tuple[Endpoint, Endpoint]]:
    """Undirected cross-table pairs; skip bare id↔id; type-compatible only."""
    pairs: list[tuple[Endpoint, Endpoint]] = []
    n = len(endpoints)
    for i in range(n):
        a = endpoints[i]
        for j in range(i + 1, n):
            b = endpoints[j]
            if a.table == b.table:
                continue
            if a.column == "id" and b.column == "id":
                continue
            if not types_compatible(a.mysql_type, b.mysql_type):
                continue
            pairs.append((a, b))
    return pairs


def sample_all_bags(
    conn: Any,
    schema: str,
    catalog: dict[str, Any],
    endpoints: list[Endpoint],
    *,
    k: int,
    workers: int = 8,
    db_url: str = "",
    database: str = "",
) -> dict[str, list[Any]]:
    del conn  # use pooled workers
    target = resolve_dsn(db_url=db_url, database=database or schema)
    bags: dict[str, list[Any]] = {}
    lock = threading.Lock()
    done = 0

    def one(ep: Endpoint) -> tuple[str, list[Any]]:
        c = connect(target)
        try:
            return ep.fq, _sample_column_multipath(
                c, schema, catalog, ep.table, ep.column, k
            )
        finally:
            c.close()

    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        futs = [pool.submit(one, ep) for ep in endpoints]
        for fut in as_completed(futs):
            fq, vals = fut.result()
            with lock:
                bags[fq] = vals
                done += 1
                if done % 50 == 0 or done == len(endpoints):
                    print(f"sample bags {done}/{len(endpoints)}", flush=True)
    return bags


def load_distinct_sets(
    conn: Any,
    schema: str,
    endpoints: list[Endpoint],
    bags: dict[str, list[Any]],
    *,
    cap: int,
    workers: int,
    db_url: str = "",
    database: str = "",
) -> dict[str, set[str] | None]:
    del conn, bags
    target = resolve_dsn(db_url=db_url, database=database or schema)
    out: dict[str, set[str] | None] = {}
    lock = threading.Lock()
    done = 0

    def one(ep: Endpoint) -> tuple[str, set[str] | None]:
        c = connect(target)
        try:
            return ep.fq, _fetch_distinct_set(c, schema, ep.table, ep.column, cap=cap)
        finally:
            c.close()

    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        futs = [pool.submit(one, ep) for ep in endpoints]
        for fut in as_completed(futs):
            fq, dset = fut.result()
            with lock:
                out[fq] = dset
                done += 1
                if done % 50 == 0 or done == len(endpoints):
                    cached = sum(1 for v in out.values() if v is not None)
                    print(
                        f"distinct cache {done}/{len(endpoints)} cached={cached}",
                        flush=True,
                    )
    return out


def _fetch_distinct_set(
    conn: Any, schema: str, table: str, column: str, *, cap: int
) -> set[str] | None:
    sql = (
        f"SELECT DISTINCT {sql_ident(column)} AS v "
        f"FROM {sql_ident(schema)}.{sql_ident(table)} "
        f"WHERE {sql_ident(column)} IS NOT NULL "
        f"LIMIT %s"
    )
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (cap + 1,))
            rows = cur.fetchall() or []
    except Exception:
        return None
    if len(rows) > cap:
        return None
    return {str(r.get("v")) for r in rows if r.get("v") is not None}


def _probe_pair(
    left: Endpoint,
    right: Endpoint,
    *,
    bags: dict[str, list[Any]],
    distincts: dict[str, set[str] | None],
    schema: str,
    get_conn: Any,
) -> dict[str, Any]:
    key = _pair_key(left, right)
    bag_l = bags.get(left.fq) or []
    bag_r = bags.get(right.fq) or []
    base = {
        "key": key,
        "left": left.fq,
        "right": right.fq,
        "left_bag": len(bag_l),
        "right_bag": len(bag_r),
    }
    if not bag_l or not bag_r:
        return {**base, "hit": False, "how": "empty_bag", "hit_count": 0}

    keys_l = _bag_keys(bag_l)
    keys_r = _bag_keys(bag_r)
    inter = keys_l & keys_r
    if inter:
        return {
            **base,
            "hit": True,
            "how": "sample_intersect",
            "hit_count": len(inter),
            "sample": sorted(inter)[:8],
        }

    set_l = distincts.get(left.fq)
    set_r = distincts.get(right.fq)

    # Full distinct available on both: true domain overlap (stronger than TopK).
    if set_l is not None and set_r is not None:
        both = set_l & set_r
        if both:
            return {
                **base,
                "hit": True,
                "how": "distinct_intersect",
                "hit_count": len(both),
                "sample": sorted(both)[:8],
            }
        return {**base, "hit": False, "how": "zero", "hit_count": 0}

    # TopK of one side against full distinct of the other.
    if set_r is not None:
        hit = keys_l & set_r
        if hit:
            return {
                **base,
                "hit": True,
                "how": "bag_in_distinct_right",
                "hit_count": len(hit),
                "sample": sorted(hit)[:8],
            }
        # still try reverse bag against left if left cached — already handled above
        if set_l is None:
            # left has no cache: bag_r may still hit left via SQL
            pass
        else:
            return {**base, "hit": False, "how": "zero", "hit_count": 0}

    if set_l is not None:
        hit = keys_r & set_l
        if hit:
            return {
                **base,
                "hit": True,
                "how": "bag_in_distinct_left",
                "hit_count": len(hit),
                "sample": sorted(hit)[:8],
            }
        if set_r is not None:
            return {**base, "hit": False, "how": "zero", "hit_count": 0}

    # Neither side cached (or one-sided miss still needs SQL for uncached side).
    c = get_conn()
    if set_r is None:
        lr = _exists_in(c, schema, right.table, right.column, bag_l)
        if lr.get("ok") and int(lr.get("hit") or 0) > 0:
            return {
                **base,
                "hit": True,
                "how": "sql_left_in_right",
                "hit_count": int(lr["hit"]),
            }
        if not lr.get("ok"):
            return {
                **base,
                "hit": False,
                "how": "query_error",
                "hit_count": 0,
                "error": lr.get("error"),
            }
    if set_l is None:
        rl = _exists_in(c, schema, left.table, left.column, bag_r)
        if rl.get("ok") and int(rl.get("hit") or 0) > 0:
            return {
                **base,
                "hit": True,
                "how": "sql_right_in_left",
                "hit_count": int(rl["hit"]),
            }
        if not rl.get("ok"):
            return {
                **base,
                "hit": False,
                "how": "query_error",
                "hit_count": 0,
                "error": rl.get("error"),
            }
    return {**base, "hit": False, "how": "zero", "hit_count": 0}


def _sample_column_multipath(
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
    bags: list[Any] = []
    # latest rows
    order_row = (
        "id" if "id" in columns else ("create_time" if "create_time" in columns else "")
    )
    if order_row:
        bags.extend(
            _fetch_top(conn, schema, table, column, k, order_col=order_row, desc=True)
        )
    # field itself DESC / ASC
    bags.extend(_fetch_top(conn, schema, table, column, k, order_col=column, desc=True))
    bags.extend(_fetch_top(conn, schema, table, column, k, order_col=column, desc=False))
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
    desc: bool,
) -> list[Any]:
    direction = "DESC" if desc else "ASC"
    sql = (
        f"SELECT {sql_ident(column)} AS v FROM {sql_ident(schema)}.{sql_ident(table)} "
        f"WHERE {sql_ident(column)} IS NOT NULL "
        f"ORDER BY {sql_ident(order_col)} {direction} LIMIT %s"
    )
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (k,))
            return [row.get("v") for row in cur.fetchall() if row.get("v") is not None]
    except Exception:
        return []


def _exists_in(
    conn: Any, schema: str, table: str, column: str, values: list[Any]
) -> dict[str, Any]:
    if not values:
        return {"ok": True, "hit": 0}
    placeholders = ",".join(["%s"] * len(values))
    # COUNT(DISTINCT) capped by bag size — enough to know non-zero + rough hit size
    sql = (
        f"SELECT COUNT(DISTINCT {sql_ident(column)}) AS hit "
        f"FROM {sql_ident(schema)}.{sql_ident(table)} "
        f"WHERE {sql_ident(column)} IN ({placeholders})"
    )
    try:
        with conn.cursor() as cur:
            cur.execute(sql, tuple(values))
            row = cur.fetchone() or {}
            return {"ok": True, "hit": int(row.get("hit") or 0)}
    except Exception as exc:
        return {"ok": False, "hit": 0, "error": str(exc)[:200]}


def _bag_keys(values: list[Any]) -> set[str]:
    return {str(v) for v in values if v is not None}


def _pair_key(a: Endpoint, b: Endpoint) -> str:
    left, right = sorted([a.fq, b.fq])
    return f"{left}{_PAIR_SEP}{right}"


def _undirected_fq(left: str, right: str) -> tuple[str, str]:
    a, b = sorted([left, right])
    return (a, b)


def _count_hit(stats: dict[str, int], row: dict[str, Any]) -> None:
    how = str(row.get("how") or "")
    if row.get("hit"):
        if how == "sample_intersect":
            stats["hit_sample_intersect"] = stats.get("hit_sample_intersect", 0) + 1
        elif how in {
            "distinct_intersect",
            "bag_in_distinct_right",
            "bag_in_distinct_left",
        }:
            stats["hit_distinct_cache"] = stats.get("hit_distinct_cache", 0) + 1
        else:
            stats["hit_sql"] = stats.get("hit_sql", 0) + 1
    elif how == "empty_bag":
        stats["empty_bag"] = stats.get("empty_bag", 0) + 1
    elif how == "query_error":
        stats["query_error"] = stats.get("query_error", 0) + 1
    else:
        stats["miss_zero"] = stats.get("miss_zero", 0) + 1


def _write_priority_candidates(hits_path: Path, out_path: Path) -> int:
    """Name/FK/code signal cut for refine — full recall stays in hits.jsonl."""
    if not hits_path.exists():
        return 0
    skip_same = {
        "enable",
        "remark",
        "name",
        "code",
        "create_by",
        "create_user",
        "update_by",
        "update_user",
        "app_tenant_code",
        "db_tenant_code",
        "organization_id",
        "status",
        "version",
        "type",
        "sort",
        "order_num",
    }
    buckets: dict[str, list[dict[str, Any]]] = {
        "same_name": [],
        "fk_to_id": [],
        "code": [],
    }
    with hits_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not row.get("hit"):
                continue
            left = str(row.get("left") or "")
            right = str(row.get("right") or "")
            if "." not in left or "." not in right:
                continue
            _lt, lc = left.split(".", 1)
            _rt, rc = right.split(".", 1)
            if lc == rc and lc not in skip_same:
                buckets["same_name"].append(row)
            elif (lc.endswith("_id") and rc == "id") or (rc.endswith("_id") and lc == "id"):
                buckets["fk_to_id"].append(row)
            elif (
                (lc.endswith("_code") and rc in {lc, "code"})
                or (rc.endswith("_code") and lc in {rc, "code"})
            ):
                buckets["code"].append(row)

    seen: set[str] = set()
    out_rows: list[dict[str, Any]] = []
    for signal, rows in buckets.items():
        for row in rows:
            key = str(row.get("key") or "")
            if not key or key in seen:
                continue
            seen.add(key)
            packed = dict(row)
            packed["signal"] = signal
            out_rows.append(packed)
    out_rows.sort(
        key=lambda r: (
            -int(r.get("hit_count") or 0),
            str(r.get("left") or ""),
            str(r.get("right") or ""),
        )
    )
    with out_path.open("w", encoding="utf-8") as fh:
        for row in out_rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return len(out_rows)


def _load_hits(path: Path) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("hit"):
                hits.append(row)
    return hits


def _load_progress(path: Path) -> tuple[set[str], list[dict[str, Any]]]:
    """Legacy helper kept for tests; prefer progress_meta + hits.jsonl."""
    done: set[str] = set()
    hits: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            key = str(row.get("key") or "")
            if key:
                done.add(key)
            if row.get("hit"):
                hits.append(row)
    return done, hits


def _load_removed_pairs(wiki_dir: Path) -> set[tuple[str, str]]:
    path = wiki_dir / "_raw" / "join_validation" / "removed_relations.yaml"
    return _pairs_from_yaml_edges(path)


def _load_existing_pairs(wiki_dir: Path) -> set[tuple[str, str]]:
    """Existing EQUI_JOIN fences in tables/*.md (undirected)."""
    import re

    fence = re.compile(r"```ground:relation\n([\s\S]*?)\n```")
    out: set[tuple[str, str]] = set()
    for p in (wiki_dir / "tables").glob("*.md"):
        text = p.read_text(encoding="utf-8")
        for m in fence.finditer(text):
            data = yaml.safe_load(m.group(1)) or {}
            if str(data.get("type") or "") != "EQUI_JOIN":
                continue
            left = str(data.get("left") or "")
            right = str(data.get("right") or "")
            if left and right:
                out.add(_undirected_fq(left, right))
    return out


def _pairs_from_yaml_edges(path: Path) -> set[tuple[str, str]]:
    if not path.exists():
        return set()
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    out: set[tuple[str, str]] = set()
    rows = data if isinstance(data, list) else (data.get("removed") or data.get("edges") or [])
    for raw in rows or []:
        if not isinstance(raw, dict):
            continue
        left = str(raw.get("left") or "")
        right = str(raw.get("right") or "")
        if left and right:
            out.add(_undirected_fq(left, right))
    return out


def _summary_md(stats: dict[str, Any], sample: list[dict[str, Any]]) -> str:
    lines = [
        "# Join collide (cartesian TopK)",
        "",
        "Stage-1 recall: keep any pair with non-zero TopK value presence; "
        "drop zero-hit. Refine later.",
        "",
        "## Stats",
        "",
        "```yaml",
        yaml.safe_dump(stats, allow_unicode=True, sort_keys=False).rstrip(),
        "```",
        "",
        "## Sample survivors (first 80 new)",
        "",
        "| left | right | how | hit_count |",
        "|---|---|---|---|",
    ]
    for r in sample:
        lines.append(
            f"| `{r.get('left')}` | `{r.get('right')}` | {r.get('how')} | {r.get('hit_count')} |"
        )
    lines.append("")
    return "\n".join(lines)


def _write_yaml(path: Path, data: Any) -> None:
    path.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


def _jsonable(v: Any) -> Any:
    if isinstance(v, (dt.datetime, dt.date)):
        return v.isoformat()
    if isinstance(v, bytes):
        return v.decode("utf-8", errors="replace")
    # Decimal / UUID / etc. from MySQL drivers
    try:
        from decimal import Decimal

        if isinstance(v, Decimal):
            return str(v)
    except Exception:
        pass
    if type(v).__name__ == "UUID":
        return str(v)
    return v
