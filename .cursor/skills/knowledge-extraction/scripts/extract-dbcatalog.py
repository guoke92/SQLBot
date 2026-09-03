#!/usr/bin/env python3
"""Step C: database substrate extractor (E2 — strongest evidence layer).

Reads a Spring properties profile, decrypts the druid RSA password, connects
read-only, and dumps the database substrate as YAML tmp artifacts (never part
of the wiki corpus):

  db-catalog.yaml    tables + columns + indexes + table comment + DDL stats
  db-profile.yaml    ANALYZE TABLE row estimates + per-column stats for
                     low-cardinality enum/status columns (value distributions)
  db-sample.yaml     newest N sample rows, text columns truncated/salted

The substrate answers "what is really there" (D7: 库 > 代码 > 文档); the code
scanner substrate (E3) corroborates and supplements with comments/semantics.

Usage::

    backend/venv/bin/python .cursor/skills/knowledge-extraction/scripts/extract-dbcatalog.py \
        [--db-profile <spring properties>] [--database lowcode_pplatform] \
        [--out-dir docs/wiki-knowledge/pplatform/db] \
        [--db-url mysql://host:port/db] [--db-user u] [--db-pass p] \
        [--sample-rows 5] [--max-distinct 20] [--tables t1,t2] [--skip-analyze]
"""

from __future__ import annotations

import argparse
import base64
import datetime as _dt
import re
import subprocess
import sys
from pathlib import Path

import yaml

_DEFAULT_PROFILE = (
    "/Users/fanjunwei/IdeaProjects/pplatform-web/lowcode-pplatform-application/"
    "src/main/resources/application-qa2-local.properties"
)
# Text-ish column types that get truncated in samples (never dumped whole).
_TEXT_TYPES = ("text", "mediumtext", "longtext", "blob", "json")
_SALT = "…[truncated]"
# Columns never sampled even if low-cardinality (secrets/PII-ish).
_DENY_COLUMNS = re.compile(r"password|secret|token|private_key|id_card|mobile|phone|salt", re.I)


def _read_profile(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        values[key.strip()] = val.strip()
    return values


def _druid_decrypt(payload_b64: str, public_key_b64: str) -> str:
    """Decrypt a druid ConfigTools password with the profile's public key.

    ConfigTools.encrypt signs with the private key (PKCS1 v1.5 block type 1);
    decrypt is a public-key RSA operation. We emulate: m = c^e mod n, then
    unpad 0x00 0x01 FF..FF 0x00 <payload>.
    """
    from Crypto.PublicKey import RSA
    from Crypto.Util.number import bytes_to_long, long_to_bytes

    key = RSA.import_key(base64.b64decode(public_key_b64))
    c = bytes_to_long(base64.b64decode(payload_b64))
    m = pow(c, key.e, key.n)
    em = long_to_bytes(m, (key.n.bit_length() + 7) // 8)
    if em[:2] != b"\x00\x01":
        raise ValueError("druid payload is not block-type-1 RSA")
    idx = em.index(b"\x00", 2)
    return em[idx + 1 :].decode()


def resolve_conn(args: argparse.Namespace) -> tuple[str, int, str, str, str]:
    """Return (host, port, user, password, database)."""
    database = args.database
    if args.db_url:
        m = re.match(r"mysql://([^:/]+):(\d+)/(\w+)", args.db_url)
        if not m:
            raise SystemExit(f"unparseable --db-url: {args.db_url}")
        host, port = m.group(1), int(m.group(2))
        if args.database:
            database = args.database
        user, password = args.db_user or "", args.db_pass or ""
        if not (user and password):
            raise SystemExit("--db-url requires --db-user/--db-pass")
        return host, port, user, password, database

    profile = Path(args.db_profile).expanduser()
    props = _read_profile(profile)
    host = props.get("DB_SERVER", "")
    port = int(props.get("DB_PORT", "3306"))
    user = props.get("DB_USERNAME", "")
    enc = props.get("DB_PASSWORD", "")
    pubkey = props.get("DB_PUBLICKEY", "")
    if not (host and user and enc):
        raise SystemExit(f"profile {profile} lacks DB_SERVER/DB_USERNAME/DB_PASSWORD")
    password = _druid_decrypt(enc, pubkey) if pubkey else enc
    if not database:
        m = re.search(r"jdbc:mysql://[^/]+/(\w+)", props.get("spring.datasource.url", ""))
        database = m.group(1) if m else ""
    if not database:
        raise SystemExit("no --database and profile URL lacks a schema name")
    return host, port, user, password, database


def _mysql(host: str, port: int, user: str, password: str, database: str, sql: str) -> list[tuple]:
    """Run one SQL via the mysql CLI (password passed by env-free fd trick:
    MYSQL_PWD is env; using argv would leak via ps)."""
    import os

    env = dict(os.environ, MYSQL_PWD=password)
    proc = subprocess.run(
        ["mysql", "-h", host, "-P", str(port), "-u", user, "--connect-timeout=10",
         database, "--batch", "--raw", "-e", sql],
        capture_output=True, text=True, env=env, timeout=120,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"mysql failed: {proc.stderr.strip()[:300]}")
    rows: list[tuple] = []
    lines = proc.stdout.splitlines()
    if not lines:
        return rows
    for line in lines[1:]:  # skip header
        rows.append(tuple(None if v == "NULL" else v for v in line.split("\t")))
    return rows


def _split_truncate(value: str | None, limit: int = 120) -> str | None:
    if value is None:
        return None
    text = str(value)
    if len(text) > limit:
        return text[:limit] + _SALT
    return text


def extract(
    host: str, port: int, user: str, password: str, database: str,
    *, sample_rows: int, max_distinct: int, tables: set[str] | None,
    skip_analyze: bool,
) -> dict[str, dict]:
    where = ""
    if tables:
        names = ",".join(f"'{t}'" for t in sorted(tables))
        where = f" AND t.table_name IN ({names})"

    tables_meta = _mysql(
        host, port, user, password, database,
        "SELECT t.table_name, t.engine, t.table_rows, t.table_comment "
        f"FROM information_schema.tables t WHERE t.table_schema='{database}'{where} "
        "ORDER BY t.table_name",
    )
    columns_meta = _mysql(
        host, port, user, password, database,
        "SELECT c.table_name, c.column_name, c.column_type, c.column_comment, "
        "c.is_nullable, c.column_default, c.column_key, c.extra "
        f"FROM information_schema.columns c WHERE c.table_schema='{database}'{where.replace('t.table_name','c.table_name')} "
        "ORDER BY c.table_name, c.ordinal_position",
    )
    index_meta = _mysql(
        host, port, user, password, database,
        "SELECT s.table_name, s.index_name, s.non_unique, "
        "GROUP_CONCAT(s.column_name ORDER BY s.seq_in_index) "
        f"FROM information_schema.statistics s WHERE s.table_schema='{database}'{where.replace('t.table_name','s.table_name')} "
        "GROUP BY s.table_name, s.index_name, s.non_unique ORDER BY s.table_name",
    )

    if not skip_analyze and not tables:
        names = [r[0] for r in tables_meta]
        print(f"ANALYZE TABLE × {len(names)} …", file=sys.stderr)
        for i in range(0, len(names), 20):
            batch = names[i : i + 20]
            _mysql(host, port, user, password, database,
                   "ANALYZE TABLE " + ",".join(f"`{t}`" for t in batch))
    elif not skip_analyze and tables:
        _mysql(host, port, user, password, database,
               "ANALYZE TABLE " + ",".join(f"`{t}`" for t in sorted(tables)))

    by_table: dict[str, dict] = {
        r[0]: {"engine": r[1], "rows_estimate": int(r[2] or 0), "comment": r[3] or "",
               "columns": {}, "indexes": [], "column_stats": {}, "samples": []}
        for r in tables_meta
    }
    for tname, cname, ctype, comment, nullable, dflt, key, extra in columns_meta:
        if tname not in by_table:
            continue
        by_table[tname]["columns"][cname] = {
            "type": ctype, "comment": comment or "",
            "nullable": nullable == "YES", "default": dflt, "key": key, "extra": extra,
        }
    for tname, iname, non_unique, cols in index_meta:
        if tname in by_table:
            by_table[tname]["indexes"].append({
                "name": iname, "unique": non_unique == "0", "columns": (cols or "").split(","),
            })

    # Column stats for low-cardinality columns (enum/status semantics + aliases).
    print("Profiling low-cardinality columns …", file=sys.stderr)
    for tname, meta in by_table.items():
        if tables and tname not in tables:
            continue
        if meta["rows_estimate"] <= 0:
            continue
        candidates = [
            cname for cname, cinfo in meta["columns"].items()
            if not _DENY_COLUMNS.search(cname)
            and cinfo["type"].split("(")[0] in ("varchar", "char", "int", "tinyint", "smallint")
            and not cinfo["key"] == "PRI"
        ]
        for cname in candidates:
            try:
                distinct = _mysql(host, port, user, password, database,
                                  f"SELECT COUNT(DISTINCT `{cname}`) FROM `{tname}`")
                n_distinct = int(distinct[0][0] or 0)
                if n_distinct == 0 or n_distinct > max_distinct:
                    continue
                dist = _mysql(
                    host, port, user, password, database,
                    f"SELECT `{cname}`, COUNT(*) FROM `{tname}` "
                    f"WHERE `{cname}` IS NOT NULL GROUP BY 1 ORDER BY 2 DESC LIMIT {max_distinct}",
                )
                meta["column_stats"][cname] = {
                    "distinct": n_distinct,
                    "values": {v or "": int(cnt) for v, cnt in dist},
                }
            except RuntimeError:
                continue  # profiling is best-effort

    # Newest sample rows (text truncated, deny-columns dropped).
    print("Sampling newest rows …", file=sys.stderr)
    for tname, meta in by_table.items():
        if tables and tname not in tables:
            continue
        pk = next((i["columns"] for i in meta["indexes"] if i["unique"] and i["name"] == "PRIMARY"), None)
        order = f"ORDER BY `{pk[0]}` DESC" if pk else ""
        try:
            rows = _mysql(host, port, user, password, database,
                          f"SELECT * FROM `{tname}` {order} LIMIT {sample_rows}")
        except RuntimeError:
            continue
        cols = list(meta["columns"])
        for row in rows:
            sample = {}
            for cname, value in zip(cols, row):
                if _DENY_COLUMNS.search(cname):
                    continue
                ctype = meta["columns"][cname]["type"]
                if any(t in ctype for t in _TEXT_TYPES):
                    sample[cname] = _split_truncate(value, 60)
                else:
                    sample[cname] = _split_truncate(value)
            meta["samples"].append(sample)
    return by_table


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db-profile", default=_DEFAULT_PROFILE)
    parser.add_argument("--database", default="")
    parser.add_argument("--out-dir", default="docs/wiki-knowledge/pplatform/db")
    parser.add_argument("--db-url", default="")
    parser.add_argument("--db-user", default="")
    parser.add_argument("--db-pass", default="")
    parser.add_argument("--sample-rows", type=int, default=5)
    parser.add_argument("--max-distinct", type=int, default=20)
    parser.add_argument("--tables", default="")
    parser.add_argument("--skip-analyze", action="store_true")
    args = parser.parse_args()

    host, port, user, password, database = resolve_conn(args)
    tables = {t.strip() for t in args.tables.split(",") if t.strip()} or None
    print(f"Connecting {user}@{host}:{port}/{database} …", file=sys.stderr)
    data = extract(host, port, user, password, database,
                   sample_rows=args.sample_rows, max_distinct=args.max_distinct,
                   tables=tables, skip_analyze=args.skip_analyze)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = _dt.date.today().isoformat()
    header = {
        "schema_version": "1.0",
        "generated_at": stamp,
        "source": "extract-dbcatalog.py (E2 db substrate — tmp 中间产物, not wiki corpus)",
        "host": host,
        "port": port,
        "database": database,
        "tables": len(data),
    }
    # db-catalog: structure only
    catalog = {**header,
               "note": "columns/indexes/comments — machine truth for lint 对账",
               "tables": {t: {"engine": m["engine"], "comment": m["comment"],
                              "columns": m["columns"], "indexes": m["indexes"]}
                          for t, m in data.items()}}
    (out_dir / "db-catalog.yaml").write_text(
        yaml.safe_dump(catalog, allow_unicode=True, sort_keys=True), encoding="utf-8")
    # db-profile: row estimates + value distributions
    profile = {**header,
               "note": "ANALYZE row estimates + low-cardinality value distributions",
               "tables": {t: {"rows_estimate": m["rows_estimate"],
                              "column_stats": m["column_stats"]}
                          for t, m in data.items()}}
    (out_dir / "db-profile.yaml").write_text(
        yaml.safe_dump(profile, allow_unicode=True, sort_keys=True), encoding="utf-8")
    # db-sample: newest rows (truncated/salted, deny-columns dropped)
    sample = {**header,
              "note": f"newest {args.sample_rows} rows; text truncated; sensitive columns dropped",
              "tables": {t: {"samples": m["samples"]} for t, m in data.items()}}
    (out_dir / "db-sample.yaml").write_text(
        yaml.safe_dump(sample, allow_unicode=True, sort_keys=True), encoding="utf-8")

    stats = sum(len(m["column_stats"]) for m in data.values())
    print(f"tables={len(data)} profiled_columns={stats} -> {out_dir}/db-{{catalog,profile,sample}}.yaml")


if __name__ == "__main__":
    main()
