"""Refine collide survivors → confirmed EQUI_JOIN fences.

Stage-2 after ``collide-joins``:

1. Read ``priority_candidates.jsonl`` (same_name / *_id→id / *_code)
2. Drop noise (tenant/audit/trace/act_procinst/UUID≠biz-code/sibling hub FKs)
3. Orient edges parent→child using join_patterns hub maps
4. Skip removed + existing wiki edges; shared-endpoint filter
5. Live ``validate_relations`` → accept ``fk_like`` / ``shared_domain``
6. Optionally write confirmed fences onto child table pages

Usage::

    backend/venv/bin/python -m tools.wiki_extract refine-collide \\
        --wiki docs/wiki/v3 \\
        --out docs/wiki/v3/_raw/join_collide \\
        --write
"""

from __future__ import annotations

import datetime as dt
import json
import re
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

from tools.wiki_extract.connect import connect, resolve_dsn
from tools.wiki_extract.join_policy import (
    AUDIT_USER_FIELDS,
    TENANT_FIELDS,
    classify_join_role,
)
from tools.wiki_extract.reextract_joins import (
    apply_shared_endpoint_filter_oriented,
    load_existing_pairs,
    load_removed_pairs,
)
from tools.wiki_extract.validate_joins import (
    load_wiki_relations,
    render_markdown_report,
    validate_relations,
)

_RELATION_FENCE = re.compile(r"```ground:relation\n([\s\S]*?)\n```")
_RELATION_HEADING = "## 关联关系"

# Sibling same-name of these is almost never a direct A↔B edge — both point at a hub.
_SIBLING_HUB_COLS = frozenset(
    {
        "cust_id",
        "company_id",
        "cust_company_id",
        "invite_cust_id",
        "person_id",
        "project_id",
        "source_project_id",
        "default_project_id",
        "product_id",
        "platform_product_id",
        "tenant_id",
        "project_approval_id",
        "apply_id",
        "rule_info_id",
    }
)

_SKIP_COLS = (
    frozenset(
        {
            "enable",
            "remark",
            "name",
            "status",
            "version",
            "type",
            "sort",
            "order_num",
            "registered_address",
            "req_sn",
            "user_id",
            "trace_id",
            "email",
            "company_name",
            "cust_manager_name",
            "cust_name",
            "file_name",
            "channel",
            "company_type",
            "alter_type_id",
            "operator_id",
            "operation_id",
            "source_id",
            "platform_cust_id",
            "root_cust_id",
            "parent_cust_id",
            "cust_manager_id",
        }
    )
    | TENANT_FIELDS
    | AUDIT_USER_FIELDS
)

_HUB_ID: dict[str, str] = {
    "cust_id": "cust_company_info.id",
    "company_id": "cust_company_info.id",
    "cust_company_id": "cust_company_info.id",
    "invite_cust_id": "cust_company_info.id",
    "person_id": "cust_person_info.id",
    "project_id": "tenant_project.id",
    "source_project_id": "tenant_project.id",
    "default_project_id": "tenant_project.id",
    "platform_product_id": "platform_product.id",
    "tenant_id": "tenant_setting_config.id",
    "project_approval_id": "tenant_project_approval.id",
    "apply_id": "wechat_project_approval_apply.id",
    "rule_info_id": "funding_rule_info.id",
}

_HUB_CODE: dict[str, str] = {
    "company_code": "cust_company_info.code",
    "project_code": "tenant_project.code",
    "flow_code": "tenant_project_approval_flow_config.flow_code",
    "tenant_code": "tenant_setting_config.code",
    "fund_rule_code_ref": "funding_rule_info.code",
}

# Same-name business keys worth validating (not hub siblings).
_SAME_NAME_KEEP = frozenset(
    {
        "menu_id",
        "resource_id",
        "product_code",
        "platform_product_code",
        "certification_no",
        "flow_code",
        "node_code",
        "approval_no",
        "sp_no",
        "batch_no",
        "funding_party_code",
        "channel_code",
        "org_code",
        "wechat_audit_no",
        "dbass_app_id",
        "app_id",
        "agreement_no",
        "order_no",
        "contract_no",
    }
)


@dataclass
class RefineCand:
    left: str
    right: str
    signal: str
    hit_count: int = 0
    how: str = ""
    status: str = "candidate"
    verdict: str = ""
    detail: str = ""
    note: str = ""


def run_refine(
    *,
    wiki_dir: Path,
    out_dir: Path,
    db_url: str = "",
    database: str = "",
    limit: int = 0,
    write: bool = False,
    skip_validate: bool = False,
) -> dict[str, Any]:
    wiki_dir = Path(wiki_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    priority_path = out_dir / "priority_candidates.jsonl"
    hits_path = out_dir / "hits.jsonl"
    if not priority_path.exists() and not hits_path.exists():
        raise FileNotFoundError(
            f"missing collide outputs under {out_dir} (run collide-joins first)"
        )

    removed = load_removed_pairs(
        wiki_dir / "_raw" / "join_validation" / "removed_relations.yaml"
    )
    existing = load_existing_pairs(wiki_dir)
    oriented_existing = [
        (r["left"], r["right"]) for r in load_wiki_relations(wiki_dir)
    ]

    raw_rows = _load_priority(priority_path, hits_path)
    cands = nominate(raw_rows, removed=removed, existing=existing)
    cands = apply_pattern_rejects(cands)
    # Convert to PairCandidate-compatible for shared-endpoint helper
    from tools.wiki_extract.reextract_joins import PairCandidate

    pcs = [
        PairCandidate(
            left=c.left,
            right=c.right,
            strategy=c.signal,
            score=c.hit_count,
            reason=c.note or c.signal,
            status=c.status,
            verdict=c.verdict,
            detail=c.detail,
        )
        for c in cands
    ]
    pcs = apply_shared_endpoint_filter_oriented(pcs, oriented_existing)
    by_key = {_norm(c.left, c.right): c for c in cands}
    for pc in pcs:
        key = _norm(pc.left, pc.right)
        if key in by_key:
            by_key[key].status = pc.status
            if pc.detail:
                by_key[key].detail = pc.detail
    cands = list(by_key.values())

    to_validate = [c for c in cands if c.status == "candidate"]
    to_validate.sort(key=lambda c: (-c.hit_count, c.left, c.right))
    if limit > 0:
        to_validate = to_validate[:limit]

    report: dict[str, Any] | None = None
    if not skip_validate and to_validate:
        target = resolve_dsn(db_url=db_url, database=database)
        conn = connect(target)
        try:
            rels = [
                {
                    "left": c.left,
                    "right": c.right,
                    "host": c.right.split(".", 1)[0],
                    "trust": "proposed",
                    "authenticity": "unknown",
                    "source": f"collide:{c.signal}",
                    "evidence": c.note or c.signal,
                }
                for c in to_validate
            ]
            print(f"validate {len(rels)} candidates…", flush=True)
            report = validate_relations(conn, rels, database=target.database)
        finally:
            conn.close()
        by_pair = {
            _norm(e["left"], e["right"]): e for e in (report.get("edges") or [])
        }
        accept = {"fk_like", "shared_domain"}
        review = {"weak_overlap"}
        for c in to_validate:
            edge = by_pair.get(_norm(c.left, c.right)) or {}
            v = str(edge.get("verdict") or "")
            c.verdict = v
            if v in accept:
                c.status = "accepted"
                c.detail = str(edge.get("reason") or "")
            elif v in review:
                c.status = "review"
                c.detail = str(edge.get("reason") or "")
            else:
                c.status = "rejected"
                c.detail = str(edge.get("reason") or v)

    accepted = [c for c in cands if c.status == "accepted"]
    review_rows = [c for c in cands if c.status == "review"]
    written: list[dict[str, Any]] = []
    if write and accepted:
        written = write_confirmed_edges(wiki_dir, accepted)

    stats = {
        "raw_priority": len(raw_rows),
        "nominated": len(cands),
        "to_validate": len(to_validate),
        "accepted": len(accepted),
        "review": len(review_rows),
        "rejected": sum(1 for c in cands if c.status == "rejected"),
        "written": len(written),
    }
    payload = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "source": "tools.wiki_extract.refine_collide",
        "stats": stats,
        "candidates": [asdict(c) for c in sorted(cands, key=lambda x: (-x.hit_count, x.left))],
        "written": written,
    }
    (out_dir / "refine.yaml").write_text(
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    if report is not None:
        (out_dir / "refine_validate.yaml").write_text(
            yaml.safe_dump(report, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        (out_dir / "refine_validate.md").write_text(
            render_markdown_report(report), encoding="utf-8"
        )
    (out_dir / "refine_summary.md").write_text(
        _summary_md(stats, accepted, review_rows, written), encoding="utf-8"
    )
    if written:
        (out_dir / "confirmed_written.yaml").write_text(
            yaml.safe_dump(
                {
                    "generated_at": payload["generated_at"],
                    "policy": "collide TopK survivors → pattern orient → live fk_like/shared_domain",
                    "count": len(written),
                    "edges": written,
                },
                allow_unicode=True,
                sort_keys=False,
            ),
            encoding="utf-8",
        )
        (out_dir / "confirmed_written.md").write_text(
            _written_md(written, payload["generated_at"]), encoding="utf-8"
        )
    return payload


def nominate(
    rows: list[dict[str, Any]],
    *,
    removed: set[tuple[str, str]],
    existing: set[tuple[str, str]],
) -> list[RefineCand]:
    best: dict[tuple[str, str], RefineCand] = {}
    for row in rows:
        oriented = orient_pair(row)
        if oriented is None:
            continue
        left, right, signal, note = oriented
        key = _norm(left, right)
        if key in removed or key in existing:
            continue
        hit = int(row.get("hit_count") or 0)
        cand = RefineCand(
            left=left,
            right=right,
            signal=signal,
            hit_count=hit,
            how=str(row.get("how") or ""),
            note=note,
        )
        prev = best.get(key)
        if prev is None or hit > prev.hit_count:
            best[key] = cand
    return list(best.values())


def orient_pair(
    row: dict[str, Any],
) -> tuple[str, str, str, str] | None:
    """Return (left, right, signal, note) or None to drop."""
    a = str(row.get("left") or "")
    b = str(row.get("right") or "")
    if "." not in a or "." not in b:
        return None
    ta, ca = a.split(".", 1)
    tb, cb = b.split(".", 1)
    if ta == tb:
        return None
    if ca in _SKIP_COLS or cb in _SKIP_COLS:
        return None
    if ca.startswith("act_procinst") or cb.startswith("act_procinst"):
        return None
    if ca.endswith(("_province_code", "_city_code")) or cb.endswith(
        ("_province_code", "_city_code")
    ):
        return None

    # platform_product.code (UUID) ≠ *.platform_product_code
    if {a, b} & {"platform_product.code"} and (
        ca.endswith("platform_product_code") or cb.endswith("platform_product_code")
    ):
        return None

    # id paired with non-*_id
    if ca == "id" and not (cb.endswith("_id") or cb.startswith("ref_")):
        return None
    if cb == "id" and not (ca.endswith("_id") or ca.startswith("ref_")):
        return None

    # id → ref_* is wrong (should be code → ref_*)
    if ca == "id" and cb.startswith("ref_"):
        return None
    if cb == "id" and ca.startswith("ref_"):
        return None

    # Hub id orientation: *.cust_id ↔ cust_company_info.id
    for child_col, hub in _HUB_ID.items():
        hub_t, hub_c = hub.split(".", 1)
        if ca == child_col and tb == hub_t and cb == hub_c:
            return hub, a, "hub_id", f"pattern: {child_col} → {hub}"
        if cb == child_col and ta == hub_t and ca == hub_c:
            return hub, b, "hub_id", f"pattern: {child_col} → {hub}"

    # Known hub FK columns must not point at a wrong parent.id
    if ca in _HUB_ID or cb in _HUB_ID:
        return None

    # Hub code orientation
    for child_col, hub in _HUB_CODE.items():
        hub_t, hub_c = hub.split(".", 1)
        if ca == child_col and tb == hub_t and cb == hub_c:
            return hub, a, "hub_code", f"pattern: {child_col} → {hub}"
        if cb == child_col and ta == hub_t and ca == hub_c:
            return hub, b, "hub_code", f"pattern: {child_col} → {hub}"
    if ca in _HUB_CODE or cb in _HUB_CODE:
        return None

    # product_id ambiguous hubs — only accept when other side is known product table id
    if {ca, cb} == {"product_id", "id"}:
        id_side = a if ca == "id" else b
        fk_side = b if ca == "id" else a
        id_table = id_side.split(".", 1)[0]
        if id_table in {
            "tenant_product",
            "tenant_interworking_product",
            "platform_product",
        }:
            return (
                id_side,
                fk_side,
                "hub_id",
                f"pattern: product_id → {id_table}.id",
            )
        return None

    # ref_* → parent.code — require stem affinity (avoid random code parents)
    if ca.startswith("ref_") and cb == "code":
        if not _stem_affinity(ca, tb):
            return None
        return b, a, "ref_code", f"pattern: {ca} → {tb}.code"
    if cb.startswith("ref_") and ca == "code":
        if not _stem_affinity(cb, ta):
            return None
        return a, b, "ref_code", f"pattern: {cb} → {ta}.code"

    # Same-name business keys — only same-family parent/child (menu↔menu_res),
    # not cross-scenario cliques (platform_product_code across auth/migratory/log).
    if ca == cb:
        if ca in _SIBLING_HUB_COLS:
            return None
        if ca.startswith("ref_"):
            return None
        if ca.endswith("_id") and ca not in _SAME_NAME_KEEP:
            return None
        if ca.endswith("_user_id") or ca.endswith("_by"):
            return None
        # Same-name: allow within family; cross-family same-semantic joins are
        # nominated only after live high-overlap (refine validate), not blocked
        # solely because B↔C. Homonym column names never nominate.
        if ca in {
            "channel_code",  # homonym bundle — senses must not join
            "sp_no",  # wechat vs online approval
            "wechat_audit_no",
        }:
            return None
        if ca not in _SAME_NAME_KEEP and not ca.endswith(("_code", "_no", "_id")):
            return None
        left, right = _prefer_parent_left(a, b)
        # platform_product_code / product_code: allow nominate; validate decides
        if ca in {"platform_product_code", "product_code", "certification_no", "node_code"}:
            return left, right, "same_name", f"same-name `{ca}` (overlap-gated)"
        if not _same_family(left.split(".", 1)[0], right.split(".", 1)[0]):
            return None
        return left, right, "same_name", f"same-name `{ca}` (family)"

    # Classic *_id → *.id (non-hub): require stem affinity with parent table
    if ca.endswith("_id") and cb == "id":
        if not _stem_affinity(ca, tb):
            return None
        return b, a, "fk_to_id", f"{ca} → {tb}.id"
    if cb.endswith("_id") and ca == "id":
        if not _stem_affinity(cb, ta):
            return None
        return a, b, "fk_to_id", f"{cb} → {ta}.id"

    # *_code → *.code with stem affinity
    if ca.endswith("_code") and cb == "code":
        if not _stem_affinity(ca, tb):
            return None
        return b, a, "fk_to_code", f"{ca} → {tb}.code"
    if cb.endswith("_code") and ca == "code":
        if not _stem_affinity(cb, ta):
            return None
        return a, b, "fk_to_code", f"{cb} → {ta}.code"

    return None


def _same_family(ta: str, tb: str) -> bool:
    """True when tables share a scenario family (menu/res, funding_*, log/bak)."""
    if ta == tb:
        return True
    for suf in ("_res", "_bak", "_detail", "_front_cfg", "_share", "_history"):
        if ta + suf == tb or tb + suf == ta:
            return True
        if ta.removesuffix(suf) == tb.removesuffix(suf) and (
            ta.endswith(suf) or tb.endswith(suf)
        ):
            return True
    # funding_rule_* family
    fa = ta.split("_")[:2]
    fb = tb.split("_")[:2]
    if fa == fb == ["funding", "rule"]:
        return True
    if fa == fb and fa[0] in {"tenant", "cust", "ca", "wechat"}:
        # require longer shared prefix (3 tokens) to avoid tenant_product vs tenant_project
        pa, pb = ta.split("_"), tb.split("_")
        shared = 0
        for x, y in zip(pa, pb):
            if x != y:
                break
            shared += 1
        return shared >= 3
    return False


def _stem_affinity(fk_col: str, parent_table: str) -> bool:
    stem = fk_col
    if stem.startswith("ref_"):
        stem = stem[4:]
    for suf in ("_id", "_code", "_no"):
        if stem.endswith(suf):
            stem = stem[: -len(suf)]
            break
    if not stem or len(stem) < 3:
        return False
    pt = parent_table.lower().replace("_", "")
    st = stem.lower()
    # Exact / containment on compact forms
    if st.replace("_", "") in pt or pt in st.replace("_", ""):
        return True
    parts = [p for p in st.split("_") if len(p) >= 4]
    if not parts:
        return False
    # Primary (last) token must appear in parent table name.
    primary = parts[-1]
    if primary not in parent_table.lower():
        return False
    return True


def apply_pattern_rejects(cands: list[RefineCand]) -> list[RefineCand]:
    out: list[RefineCand] = []
    for c in cands:
        if c.left == "platform_product.code" and c.right.endswith(
            "platform_product_code"
        ):
            c.status = "rejected"
            c.detail = "pattern: UUID code ≠ platform_product_code"
        elif c.right.startswith("ref_") and c.left.endswith(".id"):
            c.status = "rejected"
            c.detail = "pattern: ref_* ← code not id"
        out.append(c)
    return out


def write_confirmed_edges(
    wiki_dir: Path, accepted: list[RefineCand]
) -> list[dict[str, Any]]:
    written: list[dict[str, Any]] = []
    for c in accepted:
        host = c.right.split(".", 1)[0]
        path = wiki_dir / "tables" / f"{host}.md"
        if not path.exists():
            continue
        note = c.note or c.signal
        block = {
            "type": "EQUI_JOIN",
            "left": c.left,
            "right": c.right,
            "cardinality": "one_to_many",
            "trust": "confirmed",
            "authenticity": "likely",
            "evidence": f"live_validate:{c.verdict};collide_refine:{note}",
            "source": "collide_refine",
            "join_role": classify_join_role(
                c.left.split(".", 1)[1], c.right.split(".", 1)[1]
            ),
            "priority": "primary",
            "authenticity_note": note[:120],
        }
        if _append_relation_fence(path, block):
            written.append(
                {
                    "left": c.left,
                    "right": c.right,
                    "host": host,
                    "verdict": c.verdict,
                    "signal": c.signal,
                    "note": note,
                    "hit_count": c.hit_count,
                    "wrote": True,
                }
            )
    return written


def _append_relation_fence(path: Path, block: dict[str, Any]) -> bool:
    text = path.read_text(encoding="utf-8")
    left = str(block.get("left") or "")
    right = str(block.get("right") or "")
    for m in _RELATION_FENCE.finditer(text):
        try:
            data = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            continue
        if str(data.get("left")) == left and str(data.get("right")) == right:
            return False  # already present
    fence = (
        "```ground:relation\n"
        + yaml.safe_dump(block, allow_unicode=True, sort_keys=False).rstrip()
        + "\n```\n"
    )
    if _RELATION_HEADING in text:
        # Insert before next ## after heading, or at end of relation section
        idx = text.find(_RELATION_HEADING)
        rest = text[idx + len(_RELATION_HEADING) :]
        next_h = rest.find("\n## ")
        if next_h < 0:
            updated = text.rstrip() + "\n" + fence
        else:
            insert_at = idx + len(_RELATION_HEADING) + next_h
            updated = text[:insert_at].rstrip() + "\n" + fence + text[insert_at:]
    else:
        # Append section before 页面链接 if present
        marker = "\n## 页面链接"
        if marker in text:
            pos = text.find(marker)
            updated = (
                text[:pos].rstrip()
                + f"\n\n{_RELATION_HEADING}\n\n"
                + fence
                + text[pos:]
            )
        else:
            updated = text.rstrip() + f"\n\n{_RELATION_HEADING}\n\n" + fence
    path.write_text(updated, encoding="utf-8")
    return True


def _prefer_parent_left(a: str, b: str) -> tuple[str, str]:
    def score(fq: str) -> tuple[int, str]:
        t = fq.split(".", 1)[0]
        penalty = 0
        for suf in ("_res", "_detail", "_log", "_bak", "_history", "_record", "_rel"):
            if t.endswith(suf):
                penalty += 1
        return (penalty, t)

    return (a, b) if score(a) <= score(b) else (b, a)


def _load_priority(
    priority_path: Path, hits_path: Path
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    src = priority_path if priority_path.exists() else hits_path
    with src.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("hit") is False:
                continue
            rows.append(row)
    return rows


def _norm(left: str, right: str) -> tuple[str, str]:
    return tuple(sorted([left, right]))  # type: ignore[return-value]


def _summary_md(
    stats: dict[str, Any],
    accepted: list[RefineCand],
    review: list[RefineCand],
    written: list[dict[str, Any]],
) -> str:
    lines = [
        "# Collide refine",
        "",
        f"stats: `{stats}`",
        "",
        f"## Accepted ({len(accepted)})",
        "",
    ]
    for c in accepted:
        mark = "✓ wrote" if any(
            w["left"] == c.left and w["right"] == c.right for w in written
        ) else ""
        lines.append(
            f"- `{c.left}` → `{c.right}` [{c.verdict}] hit={c.hit_count} {c.note} {mark}"
        )
    lines += ["", f"## Review ({len(review)})", ""]
    for c in review[:80]:
        lines.append(
            f"- `{c.left}` → `{c.right}` hit={c.hit_count} — {c.detail[:120]}"
        )
    lines.append("")
    return "\n".join(lines)


def _written_md(written: list[dict[str, Any]], stamp: str) -> str:
    lines = [
        f"# Collide refine confirmed written ({len(written)})",
        "",
        f"- generated_at: `{stamp}`",
        "",
    ]
    for w in written:
        lines.append(
            f"- [NEW] `{w['left']}` → `{w['right']}` host=`{w['host']}` "
            f"verdict=`{w['verdict']}` — {w.get('note')}"
        )
    lines.append("")
    return "\n".join(lines)
