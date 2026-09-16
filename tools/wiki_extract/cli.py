"""CLI: introspect / compile. Isolated from apps.knowledge.wiki."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

from tools.wiki_extract.connect import MysqlTarget, connect, resolve_dsn
from tools.wiki_extract.emit import emit
from tools.wiki_extract.heuristics import compile_model
from tools.wiki_extract.introspect import introspect
from tools.wiki_extract.llm_client import resolve_llm_config
from tools.wiki_extract.llm_refine import refine_model


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="wiki_extract",
        description="L0 DB → draft wiki (does not touch wiki-pages/ or old extract scripts)",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    intro = sub.add_parser("introspect", help="dump _raw catalog/profile only")
    _add_io_args(intro)

    compile_p = sub.add_parser("compile", help="introspect + emit draft wiki pages")
    _add_io_args(compile_p)
    compile_p.add_argument(
        "--from-raw",
        default="",
        help="compile from an existing _raw directory (skip live DB)",
    )
    llm = compile_p.add_mutually_exclusive_group()
    llm.add_argument(
        "--llm",
        action="store_true",
        help="require LLM refine (enum keep/drop + semantic clusters)",
    )
    llm.add_argument(
        "--skip-llm", action="store_true", help="mechanical heuristics only"
    )
    compile_p.add_argument("--llm-base-url", default="")
    compile_p.add_argument("--llm-model", default="")
    compile_p.add_argument(
        "--llm-workers",
        type=int,
        default=4,
        help="parallel table LLM calls",
    )

    args = parser.parse_args(argv)
    out = Path(args.out)
    tables = {t.strip() for t in (args.tables or "").split(",") if t.strip()} or None

    if args.cmd == "introspect":
        catalog, profile, target = _load_or_scan(args, tables)
        _write_raw(out, catalog, profile)
        print(
            f"raw catalog tables={len(catalog.get('tables') or {})} -> {out / '_raw'}",
            file=sys.stderr,
        )
        if target:
            print(f"connected {target.masked()}", file=sys.stderr)
        return 0

    if args.cmd == "compile":
        catalog, profile, target = _load_or_scan(args, tables)
        model = compile_model(
            catalog,
            profile,
            max_enum_distinct=int(args.max_distinct),
        )
        llm_note = " skip-llm"
        if not getattr(args, "skip_llm", False):
            cfg = resolve_llm_config(
                base_url=getattr(args, "llm_base_url", "") or "",
                model=getattr(args, "llm_model", "") or "",
            )
            if cfg is None:
                if getattr(args, "llm", False):
                    print(
                        "LLM required: set WIKI_EXTRACT_LLM_API_KEY / "
                        "WIKI_EXTRACT_LLM_BASE_URL / WIKI_EXTRACT_LLM_MODEL",
                        file=sys.stderr,
                    )
                    return 2
                print("LLM config missing; compiling without refine", file=sys.stderr)
            else:
                from tools.wiki_extract.llm_client import chat_json

                print(f"LLM refine via {cfg.masked()}", file=sys.stderr)

                def _chat(system: str, user: str) -> dict:
                    return chat_json(cfg, system=system, user=user)

                model = refine_model(
                    model, _chat, workers=int(getattr(args, "llm_workers", 4) or 4)
                )
                stats_llm = model.get("llm_stats") or {}
                llm_note = (
                    f" llm keep={stats_llm.get('enum_keep')} "
                    f"instance={stats_llm.get('enum_instance')} "
                    f"reject={stats_llm.get('enum_reject')}"
                )
        stats = emit(model, out, catalog=catalog, profile=profile)
        extra = f" via {target.masked()}" if target else " from --from-raw"
        print(
            f"L0 draft tables={stats['tables']} enums={stats['enums']} "
            f"reviews={stats['reviews']}{extra}{llm_note} -> {out}",
            file=sys.stderr,
        )
        return 0
    return 2


def _add_io_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--db-url", default="", help="mysql://user:pass@host:port/db")
    parser.add_argument("--database", default="", help="override database name")
    parser.add_argument(
        "--out",
        required=True,
        help="output tree (e.g. docs/wiki-knowledge/pplatform/l0)",
    )
    parser.add_argument("--tables", default="", help="comma-separated table whitelist")
    parser.add_argument("--skip-profile", action="store_true")
    parser.add_argument("--max-distinct", type=int, default=32)


def _load_or_scan(
    args: argparse.Namespace, tables: set[str] | None
) -> tuple[dict[str, Any], dict[str, Any], MysqlTarget | None]:
    raw = (getattr(args, "from_raw", "") or "").strip()
    if raw:
        from_raw = Path(raw)
        catalog_path = from_raw / "catalog.yaml"
        if not catalog_path.exists():
            raise FileNotFoundError(catalog_path)
        catalog = _read_yaml(catalog_path)
        profile_path = from_raw / "profile.yaml"
        profile = _read_yaml(profile_path) if profile_path.exists() else {"tables": {}}
        if tables:
            catalog["tables"] = {
                k: v for k, v in (catalog.get("tables") or {}).items() if k in tables
            }
        return catalog, profile, None
    target = resolve_dsn(db_url=args.db_url, database=args.database)
    conn = connect(target)
    try:
        catalog, profile = introspect(
            conn,
            target,
            tables=tables,
            skip_profile=bool(args.skip_profile),
            max_distinct=int(args.max_distinct),
        )
    finally:
        conn.close()
    return catalog, profile, target


def _write_raw(out: Path, catalog: dict[str, Any], profile: dict[str, Any]) -> None:
    raw = out / "_raw"
    raw.mkdir(parents=True, exist_ok=True)
    (raw / "catalog.yaml").write_text(
        yaml.safe_dump(catalog, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    (raw / "profile.yaml").write_text(
        yaml.safe_dump(profile, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )


def _read_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a mapping")
    return data
