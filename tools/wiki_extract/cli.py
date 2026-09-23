"""CLI: introspect / compile / instance. Isolated from apps.knowledge.wiki."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

from tools.wiki_extract.connect import MysqlTarget, connect, resolve_dsn
from tools.wiki_extract.emit import emit
from tools.wiki_extract.heuristics import compile_model, seal_l0_reviews
from tools.wiki_extract.instance_index import packed_instance_index
from tools.wiki_extract.introspect import introspect
from tools.wiki_extract.llm_client import resolve_llm_config
from tools.wiki_extract.llm_refine import refine_model, replay_judgments
from tools.wiki_extract.overlap import apply_overlap, probe_overlap


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
        help="require LLM refine (dict keep/hold/drop + similar fields + join authenticity)",
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
    compile_p.add_argument(
        "--skip-overlap",
        action="store_true",
        help="skip live value-overlap probes",
    )

    overlap_p = sub.add_parser(
        "overlap", help="probe value inclusion into _raw/overlap.yaml"
    )
    _add_io_args(overlap_p)
    overlap_p.add_argument("--k", type=int, default=200, help="topK per sample path")

    instance_p = sub.add_parser(
        "instance", help="build instance_index.yaml without LLM"
    )
    _add_io_args(instance_p)
    instance_p.add_argument(
        "--from-raw",
        default="",
        help="build from an existing _raw directory (skip live DB)",
    )

    l1_p = sub.add_parser(
        "l1",
        help="aggregate l1_intermediate YAML onto L0 draft pages and emit 9 page types",
    )
    l1_p.add_argument(
        "--l0",
        required=True,
        help="L0 wiki tree (tables/, dicts/, _raw/catalog.yaml)",
    )
    l1_p.add_argument(
        "--intermediate",
        default="",
        help="l1_intermediate root (default: <l0>/_raw/l1_intermediate)",
    )
    l1_p.add_argument(
        "--out",
        required=True,
        help="output tree (e.g. docs/wiki/v3); refuses wiki-pages*",
    )
    l1_p.add_argument(
        "--code-root",
        default="",
        help="Java/XML repo used to verify code_path evidence",
    )
    l1_p.add_argument(
        "--skip-code-check",
        action="store_true",
        help="do not resolve code_path files (tests / no local repo)",
    )

    cov_p = sub.add_parser(
        "l1-coverage",
        help="list catalog tables / dicts / FK-like columns not yet in L1 IR",
    )
    cov_p.add_argument("--l0", required=True, help="L0 wiki tree")
    cov_p.add_argument(
        "--intermediate",
        default="",
        help="l1_intermediate root (default: <l0>/_raw/l1_intermediate)",
    )
    cov_p.add_argument("--prefix", default="cust", help="catalog table name prefix")
    cov_p.add_argument(
        "--req-index",
        default="",
        help="optional req-index root (lists concept markdown files)",
    )

    vj_p = sub.add_parser(
        "validate-joins",
        help=(
            "probe live DB for each EQUI_JOIN fence: join count + "
            "A.x IN/NOT IN B.y (+ reverse) to confirm/reject relation"
        ),
    )
    vj_p.add_argument(
        "--wiki",
        required=True,
        help="wiki tree with tables/*.md fences (e.g. docs/wiki/v3)",
    )
    vj_p.add_argument(
        "--db-url",
        default="",
        help="MySQL DSN (default: WIKI_EXTRACT_DSN)",
    )
    vj_p.add_argument(
        "--database",
        default="",
        help="override database name from DSN",
    )
    vj_p.add_argument(
        "--out",
        default="",
        help="report dir (default: <wiki>/_raw/join_validation)",
    )
    vj_p.add_argument(
        "--table-prefix",
        default="",
        help="only edges whose left or right table starts with this prefix",
    )
    vj_p.add_argument(
        "--trust",
        default="",
        help="comma-separated trust filter (e.g. high,medium)",
    )
    vj_p.add_argument(
        "--sample-limit",
        type=int,
        default=8,
        help="max sample values per intersection/diff (default 8)",
    )
    vj_p.add_argument(
        "--limit",
        type=int,
        default=0,
        help="max edges to probe (0 = all)",
    )

    cj_p = sub.add_parser(
        "collide-joins",
        help=(
            "cartesian field collide: TopK (latest + col ASC/DESC) bags vs all "
            "other-table fields; drop zero-hit; ignore id↔id / temporal / blob"
        ),
    )
    cj_p.add_argument("--wiki", required=True, help="wiki tree (e.g. docs/wiki/v3)")
    cj_p.add_argument(
        "--out",
        default="",
        help="report dir (default: <wiki>/_raw/join_collide)",
    )
    cj_p.add_argument("--db-url", default="", help="MySQL DSN (default: WIKI_EXTRACT_DSN)")
    cj_p.add_argument("--database", default="", help="override database name")
    cj_p.add_argument("--k", type=int, default=50, help="TopK per sample path (merged)")
    cj_p.add_argument("--workers", type=int, default=8, help="parallel IN probes")
    cj_p.add_argument(
        "--limit",
        type=int,
        default=0,
        help="max undirected pairs to probe (0 = all)",
    )
    cj_p.add_argument(
        "--no-resume",
        action="store_true",
        help="ignore progress.jsonl and re-probe all pairs",
    )

    rf_p = sub.add_parser(
        "refine-collide",
        help=(
            "refine collide survivors: pattern-orient + live validate; "
            "optionally --write confirmed EQUI_JOIN fences"
        ),
    )
    rf_p.add_argument("--wiki", required=True, help="wiki tree (e.g. docs/wiki/v3)")
    rf_p.add_argument(
        "--out",
        default="",
        help="collide report dir (default: <wiki>/_raw/join_collide)",
    )
    rf_p.add_argument("--db-url", default="", help="MySQL DSN (default: WIKI_EXTRACT_DSN)")
    rf_p.add_argument("--database", default="", help="override database name")
    rf_p.add_argument(
        "--limit",
        type=int,
        default=0,
        help="max candidates to live-validate (0 = all nominated)",
    )
    rf_p.add_argument(
        "--write",
        action="store_true",
        help="append accepted fences onto child table pages",
    )
    rf_p.add_argument(
        "--skip-validate",
        action="store_true",
        help="nominate only (no live DB)",
    )

    sync_p = sub.add_parser(
        "sync-wiki-related",
        help=(
            "rebuild table related + 页面链接/关联表 from EQUI_JOIN fences; "
            "mirror missing fences onto both endpoint pages"
        ),
    )
    sync_p.add_argument("--wiki", required=True, help="wiki tree (e.g. docs/wiki/v3)")
    sync_p.add_argument(
        "--no-mirror",
        action="store_true",
        help="do not copy relation fences onto the other endpoint page",
    )
    sync_p.add_argument(
        "--no-concepts",
        action="store_true",
        help="do not add ### 概念 links from field_semantics / concept field_targets",
    )

    scrub_p = sub.add_parser(
        "scrub-wiki",
        help=(
            "surgical scrub of wiki tables/dicts: drop polluted dict:, "
            "add comment_fk fences from schema comments; optional AI binary Y/N fill"
        ),
    )
    scrub_p.add_argument("--wiki", required=True, help="wiki tree (e.g. docs/wiki/v3)")
    scrub_p.add_argument(
        "--raw",
        default="",
        help="catalog/profile dir (default: <wiki>/_raw)",
    )
    scrub_p.add_argument(
        "--dry-run",
        action="store_true",
        help="report only; do not write pages",
    )
    scrub_p.add_argument(
        "--llm",
        action="store_true",
        help="require LLM for binary Y/N|0/1 fill on switch fields",
    )
    scrub_p.add_argument("--llm-base-url", default="")
    scrub_p.add_argument("--llm-model", default="")

    rx_p = sub.add_parser(
        "reextract-joins",
        help=(
            "re-nominate EQUI_JOIN candidates (incl. same-name keys like menu_id), "
            "skip removed/existing, live-validate, write report under --out"
        ),
    )
    rx_p.add_argument(
        "--wiki",
        required=True,
        help="wiki tree (e.g. docs/wiki/v3)",
    )
    rx_p.add_argument(
        "--out",
        default="",
        help="report dir (default: <wiki>/_raw/join_reextract)",
    )
    rx_p.add_argument("--db-url", default="", help="MySQL DSN (default: WIKI_EXTRACT_DSN)")
    rx_p.add_argument("--database", default="", help="override database name")
    rx_p.add_argument(
        "--skip-validate",
        action="store_true",
        help="only nominate candidates (no live DB)",
    )
    rx_p.add_argument("--min-score", type=int, default=5, help="min pair score")
    rx_p.add_argument(
        "--limit",
        type=int,
        default=0,
        help="max candidates to live-validate (0 = all)",
    )

    args = parser.parse_args(argv)
    if args.cmd == "collide-joins":
        from tools.wiki_extract.collide_joins import run_collide

        wiki = Path(args.wiki)
        out = Path(args.out) if args.out else wiki / "_raw" / "join_collide"
        try:
            payload = run_collide(
                wiki_dir=wiki,
                out_dir=out,
                db_url=(args.db_url or "").strip(),
                database=(args.database or "").strip(),
                k=int(args.k),
                workers=int(args.workers),
                limit=int(args.limit),
                resume=not bool(args.no_resume),
            )
        except (RuntimeError, ValueError, FileNotFoundError) as exc:
            print(str(exc), file=sys.stderr)
            return 2
        stats = payload.get("stats") or {}
        print(
            "collide-joins "
            f"endpoints={stats.get('endpoints')} pairs={stats.get('pairs_total')} "
            f"survivors_new={stats.get('survivors_new')} "
            f"zero={stats.get('miss_zero')} -> {out}",
            file=sys.stderr,
        )
        return 0

    if args.cmd == "refine-collide":
        from tools.wiki_extract.refine_collide import run_refine

        wiki = Path(args.wiki)
        out = Path(args.out) if args.out else wiki / "_raw" / "join_collide"
        try:
            payload = run_refine(
                wiki_dir=wiki,
                out_dir=out,
                db_url=(args.db_url or "").strip(),
                database=(args.database or "").strip(),
                limit=int(args.limit),
                write=bool(args.write),
                skip_validate=bool(args.skip_validate),
            )
        except (RuntimeError, ValueError, FileNotFoundError) as exc:
            print(str(exc), file=sys.stderr)
            return 2
        stats = payload.get("stats") or {}
        print(
            "refine-collide "
            f"nominated={stats.get('nominated')} validated={stats.get('to_validate')} "
            f"accepted={stats.get('accepted')} review={stats.get('review')} "
            f"written={stats.get('written')} -> {out}",
            file=sys.stderr,
        )
        return 0

    if args.cmd == "sync-wiki-related":
        from tools.wiki_extract.sync_wiki_related import run_sync

        wiki = Path(args.wiki)
        try:
            stats = run_sync(
                wiki_dir=wiki,
                mirror_fences=not bool(args.no_mirror),
                concept_links=not bool(args.no_concepts),
            )
        except (RuntimeError, ValueError, FileNotFoundError) as exc:
            print(str(exc), file=sys.stderr)
            return 2
        print(
            "sync-wiki-related "
            f"edges={stats.get('edges')} mirrored={stats.get('mirrored_fences')} "
            f"related={stats.get('updated_related')} links={stats.get('updated_page_links')} "
            f"-> {wiki}",
            file=sys.stderr,
        )
        return 0

    if args.cmd == "scrub-wiki":
        from tools.wiki_extract.scrub_wiki import run_scrub

        wiki = Path(args.wiki)
        raw = Path(args.raw) if args.raw else wiki / "_raw"
        chat = None
        if bool(getattr(args, "llm", False)):
            cfg = resolve_llm_config(
                base_url=getattr(args, "llm_base_url", "") or "",
                model=getattr(args, "llm_model", "") or "",
            )
            if cfg is None:
                print(
                    "LLM required: set WIKI_EXTRACT_LLM_API_KEY / "
                    "WIKI_EXTRACT_LLM_BASE_URL / WIKI_EXTRACT_LLM_MODEL",
                    file=sys.stderr,
                )
                return 2
            from tools.wiki_extract.llm_client import chat_json

            print(f"scrub-wiki LLM via {cfg.masked()}", file=sys.stderr)

            def _chat(system: str, user: str) -> dict:
                return chat_json(cfg, system=system, user=user)

            chat = _chat
        else:
            cfg = resolve_llm_config(
                base_url=getattr(args, "llm_base_url", "") or "",
                model=getattr(args, "llm_model", "") or "",
            )
            if cfg is not None:
                from tools.wiki_extract.llm_client import chat_json

                print(f"scrub-wiki LLM via {cfg.masked()}", file=sys.stderr)

                def _chat2(system: str, user: str) -> dict:
                    return chat_json(cfg, system=system, user=user)

                chat = _chat2
        try:
            report = run_scrub(
                wiki_dir=wiki,
                raw_dir=raw,
                chat=chat,
                write=not bool(args.dry_run),
            )
        except (RuntimeError, ValueError, FileNotFoundError) as exc:
            print(str(exc), file=sys.stderr)
            return 2
        print(
            "scrub-wiki "
            f"tables={len(report.get('tables_patched') or [])} "
            f"cleared={report.get('fields_dict_cleared')} "
            f"filled={report.get('fields_dict_filled')} "
            f"binary_fills={report.get('binary_fills')} "
            f"fences={len(report.get('fences_added') or [])} "
            f"dicts_deleted={len(report.get('dicts_deleted') or [])} "
            f"dicts_restored={len(report.get('dicts_restored') or [])} "
            f"{'(dry-run) ' if args.dry_run else ''}-> {wiki}",
            file=sys.stderr,
        )
        return 0

    if args.cmd == "reextract-joins":
        from tools.wiki_extract.reextract_joins import run_reextract

        wiki = Path(args.wiki)
        out = Path(args.out) if args.out else wiki / "_raw" / "join_reextract"
        try:
            payload = run_reextract(
                wiki_dir=wiki,
                out_dir=out,
                db_url=(args.db_url or "").strip(),
                database=(args.database or "").strip(),
                limit=int(args.limit),
                skip_validate=bool(args.skip_validate),
                min_score=int(args.min_score),
            )
        except (RuntimeError, ValueError, FileNotFoundError) as exc:
            print(str(exc), file=sys.stderr)
            return 2
        stats = payload.get("stats") or {}
        print(
            "reextract-joins "
            f"tables={stats.get('tables')} candidates={stats.get('candidates')} "
            f"accepted={stats.get('accepted')} review={stats.get('review')} "
            f"rejected={stats.get('rejected')} -> {out}",
            file=sys.stderr,
        )
        return 0

    if args.cmd == "validate-joins":
        from tools.wiki_extract.validate_joins import run_validate_joins

        wiki = Path(args.wiki)
        out = Path(args.out) if args.out else wiki / "_raw" / "join_validation"
        try:
            report = run_validate_joins(
                wiki_dir=wiki,
                db_url=(args.db_url or "").strip(),
                database=(args.database or "").strip(),
                out_dir=out,
                sample_limit=int(args.sample_limit),
                limit=int(args.limit),
                trust_filter=(args.trust or "").strip(),
                table_prefix=(args.table_prefix or "").strip(),
            )
        except (RuntimeError, ValueError, FileNotFoundError) as exc:
            print(str(exc), file=sys.stderr)
            return 2
        by = report.get("by_verdict") or {}
        print(
            "join validation "
            f"edges={report.get('relation_count')} "
            f"fk_like={by.get('fk_like', 0)} "
            f"shared={by.get('shared_domain', 0)} "
            f"weak={by.get('weak_overlap', 0)} "
            f"false_friend={by.get('false_friend', 0)} "
            f"impossible={by.get('impossible', 0)} "
            f"empty={by.get('empty_endpoint', 0)} "
            f"missing={by.get('missing_column', 0)} "
            f"error={by.get('query_error', 0)} "
            f"-> {report.get('out_report')}",
            file=sys.stderr,
        )
        return 0

    if args.cmd == "l1-coverage":
        from tools.wiki_extract.l1.coverage import coverage_report, format_coverage

        l0_dir = Path(args.l0)
        intermediate = (
            Path(args.intermediate) if args.intermediate else l0_dir / "_raw" / "l1_intermediate"
        )
        req_index = Path(args.req_index) if args.req_index else None
        report = coverage_report(
            l0_dir=l0_dir,
            intermediate_dir=intermediate,
            prefix=str(args.prefix or "cust"),
            req_index=req_index,
        )
        print(format_coverage(report), end="")
        counts = report.get("counts") or {}
        return 0 if int(counts.get("missing_tables") or 0) == 0 else 1

    out = Path(args.out)
    tables = {
        t.strip()
        for t in (getattr(args, "tables", "") or "").split(",")
        if t.strip()
    } or None

    if args.cmd == "introspect":
        catalog, profile, profile_instance, target = _load_or_scan(args, tables)
        _write_raw(out, catalog, profile, profile_instance)
        print(
            f"raw catalog tables={len(catalog.get('tables') or {})} -> {out / '_raw'}",
            file=sys.stderr,
        )
        if target:
            print(f"connected {target.masked()}", file=sys.stderr)
        return 0

    if args.cmd == "overlap":
        catalog, profile, profile_instance, target = _load_or_scan(args, tables)
        if target is None:
            print(
                "overlap requires a live DSN (--db-url / WIKI_EXTRACT_DSN)",
                file=sys.stderr,
            )
            return 2
        model = compile_model(
            catalog,
            profile,
            profile_instance=profile_instance,
            max_enum_distinct=int(args.max_distinct),
        )
        conn = connect(target)
        try:
            packed = probe_overlap(
                conn, catalog, model, k=int(getattr(args, "k", 200) or 200)
            )
        finally:
            conn.close()
        apply_overlap(model, packed)
        model = seal_l0_reviews(model)
        raw_dir = out / "_raw"
        raw_dir.mkdir(parents=True, exist_ok=True)
        _write_raw(out, catalog, profile, profile_instance)
        (raw_dir / "overlap.yaml").write_text(
            yaml.safe_dump(packed, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        stats = packed.get("stats") or model.get("overlap_stats") or {}
        print(
            f"overlap edges={len(packed.get('edges') or [])} "
            f"probed={stats.get('probed', 0)} likely={stats.get('likely', 0)} "
            f"-> {raw_dir / 'overlap.yaml'}",
            file=sys.stderr,
        )
        return 0

    if args.cmd == "instance":
        catalog, profile, profile_instance, target = _load_or_scan(args, tables)
        model = compile_model(
            catalog,
            profile,
            profile_instance=profile_instance,
            max_enum_distinct=int(args.max_distinct),
        )
        out.mkdir(parents=True, exist_ok=True)
        packed = packed_instance_index(model)
        (out / "instance_index.yaml").write_text(
            yaml.safe_dump(packed, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        _write_raw(out, catalog, profile, profile_instance)
        extra = f" via {target.masked()}" if target else " from --from-raw"
        print(
            f"instance_index entries={len(packed.get('entries') or [])}{extra} -> "
            f"{out / 'instance_index.yaml'}",
            file=sys.stderr,
        )
        return 0

    if args.cmd == "compile":
        catalog, profile, profile_instance, target = _load_or_scan(args, tables)
        raw = (getattr(args, "from_raw", "") or "").strip()
        overlap_pack = None
        if raw:
            overlap_path = Path(raw) / "overlap.yaml"
            if overlap_path.exists():
                overlap_pack = _read_yaml(overlap_path)
        model = compile_model(
            catalog,
            profile,
            profile_instance=profile_instance,
            max_enum_distinct=int(args.max_distinct),
            overlap=overlap_pack,
        )
        if target is not None and not bool(getattr(args, "skip_overlap", False)):
            conn = connect(target)
            try:
                overlap_pack = probe_overlap(conn, catalog, model)
            finally:
                conn.close()
            apply_overlap(model, overlap_pack)
            model = seal_l0_reviews(model)
        llm_note = " skip-llm"
        judge_path = Path(raw) / "llm_judge.yaml" if raw else None
        judge = (
            _read_yaml(judge_path)
            if judge_path is not None and judge_path.exists()
            else None
        )
        skip_llm = bool(getattr(args, "skip_llm", False))
        force_llm = bool(getattr(args, "llm", False))
        cfg = (
            None
            if skip_llm
            else resolve_llm_config(
                base_url=getattr(args, "llm_base_url", "") or "",
                model=getattr(args, "llm_model", "") or "",
            )
        )
        if force_llm or (not skip_llm and cfg is not None):
            if cfg is None:
                print(
                    "LLM required: set WIKI_EXTRACT_LLM_API_KEY / "
                    "WIKI_EXTRACT_LLM_BASE_URL / WIKI_EXTRACT_LLM_MODEL",
                    file=sys.stderr,
                )
                return 2
            from tools.wiki_extract.llm_client import chat_json

            print(f"LLM refine via {cfg.masked()}", file=sys.stderr)

            def _chat(system: str, user: str) -> dict:
                return chat_json(cfg, system=system, user=user)

            model = refine_model(
                model, _chat, workers=int(getattr(args, "llm_workers", 4) or 4)
            )
            stats_llm = model.get("llm_stats") or {}
            llm_note = (
                f" llm keep={stats_llm.get('dict_keep')} "
                f"hold={stats_llm.get('dict_hold')} "
                f"drop={stats_llm.get('dict_drop')}"
            )
        elif not skip_llm and judge:
            model = replay_judgments(model, judge)
            stats_llm = model.get("llm_stats") or {}
            llm_note = (
                f" replay-llm keep={stats_llm.get('dict_keep')} "
                f"hold={stats_llm.get('dict_hold')} "
                f"drop={stats_llm.get('dict_drop')}"
            )
            print("LLM refine replayed from _raw/llm_judge.yaml", file=sys.stderr)
        elif not skip_llm:
            print("LLM config missing; compiling without refine", file=sys.stderr)
        stats = emit(
            model,
            out,
            catalog=catalog,
            profile=profile,
            profile_instance=profile_instance,
            overlap=overlap_pack,
        )
        extra = f" via {target.masked()}" if target else " from --from-raw"
        print(
            f"L0 draft tables={stats['tables']} dicts={stats['dicts']} "
            f"reviews={stats['reviews']}{extra}{llm_note} -> {out}",
            file=sys.stderr,
        )
        return 0

    if args.cmd == "l1":
        from tools.wiki_extract.l1.reconcile import compile_l1

        l0_dir = Path(args.l0)
        intermediate = Path(args.intermediate) if args.intermediate else l0_dir / "_raw" / "l1_intermediate"
        code_root = Path(args.code_root) if args.code_root else None
        stats = compile_l1(
            l0_dir=l0_dir,
            intermediate_dir=intermediate,
            out_dir=out,
            code_root=code_root,
            skip_code_check=bool(args.skip_code_check),
        )
        print(
            "L1 draft "
            + " ".join(
                f"{k}={stats.get(k, 0)}"
                for k in (
                    "tables",
                    "dicts",
                    "concepts",
                    "processes",
                    "calibers",
                    "metrics",
                    "rules",
                    "scenarios",
                    "patterns",
                    "reviews",
                    "errors",
                )
            )
            + f" -> {out}",
            file=sys.stderr,
        )
        return 0 if int(stats.get("errors") or 0) == 0 else 1
    return 2


def _add_io_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--db-url", default="", help="mysql://user:pass@host:port/db")
    parser.add_argument("--database", default="", help="override database name")
    parser.add_argument(
        "--out",
        required=True,
        help="output tree (e.g. docs/wiki/v2)",
    )
    parser.add_argument("--tables", default="", help="comma-separated table whitelist")
    parser.add_argument("--skip-profile", action="store_true")
    parser.add_argument("--max-distinct", type=int, default=32)


def _load_or_scan(
    args: argparse.Namespace, tables: set[str] | None
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], MysqlTarget | None]:
    raw = (getattr(args, "from_raw", "") or "").strip()
    if raw:
        from_raw = Path(raw)
        catalog_path = from_raw / "catalog.yaml"
        if not catalog_path.exists():
            raise FileNotFoundError(catalog_path)
        catalog = _read_yaml(catalog_path)
        profile_path = from_raw / "profile.yaml"
        profile = _read_yaml(profile_path) if profile_path.exists() else {"tables": {}}
        inst_path = from_raw / "profile_instance.yaml"
        profile_instance = (
            _read_yaml(inst_path) if inst_path.exists() else {"tables": {}}
        )
        if tables:
            catalog["tables"] = {
                k: v for k, v in (catalog.get("tables") or {}).items() if k in tables
            }
        return catalog, profile, profile_instance, None
    target = resolve_dsn(db_url=args.db_url, database=args.database)
    conn = connect(target)
    try:
        catalog, profile, profile_instance = introspect(
            conn,
            target,
            tables=tables,
            skip_profile=bool(args.skip_profile),
            max_distinct=int(args.max_distinct),
        )
    finally:
        conn.close()
    return catalog, profile, profile_instance, target


def _write_raw(
    out: Path,
    catalog: dict[str, Any],
    profile: dict[str, Any],
    profile_instance: dict[str, Any] | None = None,
) -> None:
    raw = out / "_raw"
    raw.mkdir(parents=True, exist_ok=True)
    (raw / "catalog.yaml").write_text(
        yaml.safe_dump(catalog, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    (raw / "profile.yaml").write_text(
        yaml.safe_dump(profile, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )
    if profile_instance is not None:
        (raw / "profile_instance.yaml").write_text(
            yaml.safe_dump(profile_instance, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )


def _read_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} is not a mapping")
    return data
