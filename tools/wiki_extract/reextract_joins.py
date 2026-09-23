"""Full-DB JOIN re-extraction pipeline (wiki draft + live validate).

Why the old L0 pass missed ``tenant_product_menu.menu_id ↔
tenant_product_menu_res.menu_id``:

- L0 name heuristics only nominate child ``*_id`` / ``*_code`` / ``ref_*``
  toward a *parent table* endpoint (usually ``id`` / ``code``).
- Same-column business keys across sibling tables were never a nomination
  class. The only menu edge proposed was the false friend
  ``tenant_product_menu.id → …menu_id`` (later removed by validate-joins).

Pipeline::

1. Inventory joinable fields from ``docs/wiki/v3/tables``
2. Pair by same-name / classic FK / ref_* / table-affinity (may over-match)
3. Drop removed_relations + already-confirmed remaining edges
4. Live ``validate_joins`` + join_patterns rules → keep/reject
5. Agent/code confirm before writing fences (this module emits candidates)

Usage::

    backend/venv/bin/python -m tools.wiki_extract reextract-joins \\
        --wiki docs/wiki/v3 \\
        --out docs/wiki/v3/_raw/join_reextract
"""

from __future__ import annotations

import datetime as dt
import re
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

from tools.wiki_extract.connect import connect, resolve_dsn
from tools.wiki_extract.join_policy import (
    AUDIT_USER_FIELDS,
    TENANT_FIELDS,
    child_endpoint_reason,
)
from tools.wiki_extract.validate_joins import (
    load_wiki_relations,
    render_markdown_report,
    validate_relations,
)

_TABLE_FENCE = re.compile(r"```ground:table\n([\s\S]*?)\n```")
_GENERIC_SKIP = frozenset(
    {
        "id",
        "enable",
        "remark",
        "name",
        "code",
        "create_by",
        "create_user",
        "create_time",
        "update_by",
        "update_user",
        "update_time",
        "act_procinst_id",
        "act_procinst_no",
        "act_procinst_status",
        "act_procinst_date",
        "organization_id",
        "app_tenant_code",
        "db_tenant_code",
    }
) | TENANT_FIELDS | AUDIT_USER_FIELDS

_SAME_NAME_PRIORITY = frozenset(
    {
        "menu_id",
        "resource_id",
        "product_code",
        "platform_product_code",
        "project_id",
        "project_code",
        "company_id",
        "company_code",
        "cust_id",
        "person_id",
        "tenant_id",
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
    }
)

_HUB_ID: dict[str, str | None] = {
    "cust_id": "cust_company_info.id",
    "company_id": "cust_company_info.id",
    "cust_company_id": "cust_company_info.id",
    "invite_cust_id": "cust_company_info.id",
    "person_id": "cust_person_info.id",
    "project_id": "tenant_project.id",
    "source_project_id": "tenant_project.id",
    "default_project_id": "tenant_project.id",
    "product_id": None,
    "platform_product_id": "platform_product.id",
    "tenant_id": "tenant_setting_config.id",
    "project_approval_id": "tenant_project_approval.id",
    "apply_id": "wechat_project_approval_apply.id",
}

_HUB_CODE: dict[str, str | None] = {
    "company_code": "cust_company_info.code",
    "product_code": None,
    "platform_product_code": None,
    "project_code": "tenant_project.code",
    "flow_code": "tenant_project_approval_flow_config.flow_code",
    "tenant_code": "tenant_setting_config.code",
}


@dataclass
class FieldInfo:
    table: str
    column: str
    typ: str = ""
    desc: str = ""
    joinable: bool = True
    drop_reason: str = ""
    tags: list[str] = field(default_factory=list)


@dataclass
class PairCandidate:
    left: str
    right: str
    strategy: str
    score: int
    reason: str
    status: str = "candidate"
    verdict: str = ""
    detail: str = ""


def load_table_fields(wiki_dir: Path) -> dict[str, list[FieldInfo]]:
    tables_dir = wiki_dir / "tables"
    out: dict[str, list[FieldInfo]] = {}
    for path in sorted(tables_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        block = _TABLE_FENCE.search(text)
        if not block:
            continue
        data = yaml.safe_load(block.group(1)) or {}
        tname = str(data.get("table") or path.stem)
        fields: list[FieldInfo] = []
        for raw in data.get("fields") or []:
            if not isinstance(raw, dict):
                continue
            col = str(raw.get("name") or "").strip()
            if not col:
                continue
            info = FieldInfo(
                table=tname,
                column=col,
                typ=str(raw.get("type") or ""),
                desc=str(raw.get("desc") or ""),
            )
            _tag_and_filter_field(info)
            fields.append(info)
        out[tname] = fields
    return out


def _tag_and_filter_field(info: FieldInfo) -> None:
    col = info.column
    lowered = col.lower()
    tags: list[str] = []
    if lowered in _SAME_NAME_PRIORITY:
        tags.append("same_name_priority")
    if lowered.endswith("_id") or lowered.endswith("_code") or lowered.endswith("_no"):
        tags.append("suffix_key")
    if lowered.startswith("ref_"):
        tags.append("ref")
    if lowered in {"id", "code"}:
        tags.append("identity")
    if any(k in (info.desc or "") for k in ("关联", "外键", "编号", "编码", "主键")):
        tags.append("desc_hint")
    info.tags = tags

    reason = child_endpoint_reason(col, info.typ)
    if reason:
        info.joinable = False
        info.drop_reason = reason
        return
    if lowered in _GENERIC_SKIP:
        info.joinable = False
        info.drop_reason = "skipped_generic_or_tenant"
        return
    if lowered.startswith("act_procinst"):
        info.joinable = False
        info.drop_reason = "skipped_workflow"
        return


def load_removed_pairs(removed_path: Path) -> set[tuple[str, str]]:
    if not removed_path.exists():
        return set()
    data = yaml.safe_load(removed_path.read_text(encoding="utf-8")) or {}
    out: set[tuple[str, str]] = set()
    for edge in data.get("edges") or []:
        left = str(edge.get("left") or "").strip()
        right = str(edge.get("right") or "").strip()
        if left and right:
            out.add(_norm_pair(left, right))
    return out


def load_existing_pairs(wiki_dir: Path) -> set[tuple[str, str]]:
    out: set[tuple[str, str]] = set()
    for rel in load_wiki_relations(wiki_dir):
        out.add(_norm_pair(rel["left"], rel["right"]))
    return out


def _norm_pair(a: str, b: str) -> tuple[str, str]:
    return tuple(sorted([a, b]))  # type: ignore[return-value]


def _table_prefix(name: str) -> str:
    return name.split("_", 1)[0]


def _affinity(a: str, b: str) -> int:
    if a == b:
        return 0
    score = 0
    if _table_prefix(a) == _table_prefix(b):
        score += 2
    pa, pb = set(a.split("_")), set(b.split("_"))
    shared = pa & pb - {"info", "record", "config", "data", "rel"}
    score += min(3, len(shared))
    if a in b or b in a:
        score += 3
    for tok in shared:
        if len(tok) >= 5:
            score += 1
    return score


def propose_pairs(
    fields_by_table: dict[str, list[FieldInfo]],
    *,
    removed: set[tuple[str, str]],
    existing: set[tuple[str, str]],
) -> list[PairCandidate]:
    tables = sorted(fields_by_table)
    col_index: dict[str, list[tuple[str, FieldInfo]]] = defaultdict(list)
    joinable: dict[str, dict[str, FieldInfo]] = {}

    for t, flist in fields_by_table.items():
        joinable[t] = {}
        for f in flist:
            keep = f.joinable or f.column in _SAME_NAME_PRIORITY or "ref" in f.tags
            if not keep:
                continue
            joinable[t][f.column] = f
            col_index[f.column].append((t, f))

    raw: list[PairCandidate] = []

    # A: same-name business keys (HIGH) — the class L0 missed
    for col, owners in col_index.items():
        is_priority = col in _SAME_NAME_PRIORITY
        is_suffix = col.endswith(("_id", "_code", "_no")) and col not in _GENERIC_SKIP
        if not is_priority and not is_suffix:
            continue
        if col in {"id", "code", "name", "enable"}:
            continue
        for i, (ta, _) in enumerate(owners):
            for tb, _ in owners[i + 1 :]:
                aff = _affinity(ta, tb)
                if not is_priority and aff < 2:
                    continue
                if aff < 1:
                    continue
                left, right = f"{ta}.{col}", f"{tb}.{col}"
                if len(tb) < len(ta) or (tb in ta and ta != tb):
                    left, right = f"{tb}.{col}", f"{ta}.{col}"
                score = 8 if is_priority else 5
                score += aff
                raw.append(
                    PairCandidate(
                        left=left,
                        right=right,
                        strategy="same_name",
                        score=score,
                        reason=f"same column `{col}` affinity={aff}",
                    )
                )

    # B: hub *_id
    for t, cols in joinable.items():
        for col in cols:
            hub = _HUB_ID.get(col)
            if col in _HUB_ID and hub is None:
                for parent in (
                    "tenant_product",
                    "tenant_interworking_product",
                    "cust_customized_product",
                ):
                    if parent == t:
                        continue
                    if _affinity(t, parent) >= 2 and any(
                        f.column == "id" for f in fields_by_table.get(parent, [])
                    ):
                        hub = f"{parent}.id"
                        break
            if not hub:
                continue
            pt = hub.split(".", 1)[0]
            if pt == t:
                continue
            raw.append(
                PairCandidate(
                    left=hub,
                    right=f"{t}.{col}",
                    strategy="hub_id",
                    score=7 + _affinity(t, pt),
                    reason=f"hub map {col}→{hub}",
                )
            )

    # C: hub *_code (never platform_product.code ← platform_product_code)
    for t, cols in joinable.items():
        for col in cols:
            hub = _HUB_CODE.get(col)
            if col in _HUB_CODE and hub is None:
                if col == "product_code":
                    for parent in ("tenant_product",):
                        if parent != t and _affinity(t, parent) >= 2:
                            hub = f"{parent}.code"
                            break
                elif col == "platform_product_code":
                    continue
            if not hub:
                continue
            pt = hub.split(".", 1)[0]
            if pt == t:
                continue
            raw.append(
                PairCandidate(
                    left=hub,
                    right=f"{t}.{col}",
                    strategy="hub_code",
                    score=6 + _affinity(t, pt),
                    reason=f"hub code map {col}→{hub}",
                )
            )

    # D: ref_* → parent.code (company) / parent.id
    ref_re = re.compile(r"^ref_(.+)$", re.I)
    for t, cols in joinable.items():
        for col in cols:
            m = ref_re.match(col)
            if not m:
                continue
            stem = m.group(1)
            parent = None
            if stem in fields_by_table:
                parent = stem
            else:
                for cand in sorted(tables, key=len, reverse=True):
                    if stem.endswith(cand) or cand in stem:
                        parent = cand
                        break
            if not parent or parent == t:
                continue
            parent_cols = {f.column for f in fields_by_table.get(parent, [])}
            if parent == "cust_company_info" and "code" in parent_cols:
                left = "cust_company_info.code"
            elif "code" in parent_cols and col.endswith(parent):
                left = f"{parent}.code"
            elif "id" in parent_cols:
                left = f"{parent}.id"
            else:
                continue
            raw.append(
                PairCandidate(
                    left=left,
                    right=f"{t}.{col}",
                    strategy="ref_column",
                    score=6 + _affinity(t, parent),
                    reason=f"ref stem→{left}",
                )
            )

    best: dict[tuple[str, str], PairCandidate] = {}
    for cand in raw:
        key = _norm_pair(cand.left, cand.right)
        if key in removed or key in existing:
            continue
        lt, lc = cand.left.split(".", 1)
        rt, rc = cand.right.split(".", 1)
        if lt not in fields_by_table or rt not in fields_by_table:
            continue
        lcols = {f.column for f in fields_by_table[lt]}
        rcols = {f.column for f in fields_by_table[rt]}
        if lc not in lcols or rc not in rcols:
            continue
        prev = best.get(key)
        if prev is None or cand.score > prev.score:
            best[key] = cand
    return sorted(best.values(), key=lambda c: (-c.score, c.left, c.right))


def apply_pattern_rules(cands: list[PairCandidate]) -> list[PairCandidate]:
    out: list[PairCandidate] = []
    for c in cands:
        left, right = c.left, c.right
        if left == "platform_product.code" and right.endswith("platform_product_code"):
            c.status = "rejected"
            c.detail = "pattern: platform_product.code(UUID) ≠ *.platform_product_code"
            out.append(c)
            continue
        if right == "platform_product.code" and left.endswith("platform_product_code"):
            c.status = "rejected"
            c.detail = "pattern: platform_product.code(UUID) ≠ *.platform_product_code"
            out.append(c)
            continue
        if left == "cust_company_info.id" and "ref_" in right and "cust_company_info" in right:
            c.status = "rejected"
            c.detail = "pattern: ref_*cust_company_info → code not id"
            out.append(c)
            continue
        out.append(c)
    return out


def apply_shared_endpoint_filter_oriented(
    cands: list[PairCandidate],
    oriented_existing: list[tuple[str, str]],
) -> list[PairCandidate]:
    left_to_right_tables: dict[str, set[str]] = defaultdict(set)
    right_to_left_tables: dict[str, set[str]] = defaultdict(set)
    for left, right in oriented_existing:
        lt = left.split(".", 1)[0]
        rt = right.split(".", 1)[0]
        left_to_right_tables[left].add(rt)
        right_to_left_tables[right].add(lt)

    out: list[PairCandidate] = []
    for c in cands:
        if c.status in {"skipped", "rejected"}:
            out.append(c)
            continue
        lt = c.left.split(".", 1)[0]
        rt = c.right.split(".", 1)[0]
        if rt in left_to_right_tables.get(c.left, set()):
            c.status = "rejected"
            c.detail = (
                f"shared-endpoint: `{c.left}` already has confirmed join into `{rt}`"
            )
            out.append(c)
            continue
        if lt in right_to_left_tables.get(c.right, set()):
            c.status = "rejected"
            c.detail = (
                f"shared-endpoint: `{c.right}` already has confirmed join from `{lt}`"
            )
            out.append(c)
            continue
        out.append(c)
    return out


def run_reextract(
    *,
    wiki_dir: Path,
    out_dir: Path,
    db_url: str = "",
    database: str = "",
    limit: int = 0,
    skip_validate: bool = False,
    min_score: int = 5,
) -> dict[str, Any]:
    wiki_dir = Path(wiki_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    fields = load_table_fields(wiki_dir)
    removed = load_removed_pairs(
        wiki_dir / "_raw" / "join_validation" / "removed_relations.yaml"
    )
    existing_set = load_existing_pairs(wiki_dir)
    oriented_existing = [
        (r["left"], r["right"]) for r in load_wiki_relations(wiki_dir)
    ]

    field_rows = [asdict(f) for flist in fields.values() for f in flist]
    (out_dir / "field_inventory.yaml").write_text(
        yaml.safe_dump(
            {"generated_at": _now(), "fields": field_rows},
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    cands = propose_pairs(fields, removed=removed, existing=existing_set)
    cands = [c for c in cands if c.score >= min_score]
    cands = apply_pattern_rules(cands)
    cands = apply_shared_endpoint_filter_oriented(cands, oriented_existing)

    to_validate = [c for c in cands if c.status == "candidate"]
    if limit and limit > 0:
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
                    "source": c.strategy,
                    "evidence": c.reason,
                }
                for c in to_validate
            ]
            report = validate_relations(conn, rels, database=target.database)
        finally:
            conn.close()
        by_pair = {
            _norm_pair(e["left"], e["right"]): e for e in (report.get("edges") or [])
        }
        accept_verdicts = {"fk_like", "shared_domain"}
        review_verdicts = {"weak_overlap"}
        for c in to_validate:
            edge = by_pair.get(_norm_pair(c.left, c.right)) or {}
            v = str(edge.get("verdict") or "")
            c.verdict = v
            if v in accept_verdicts:
                c.status = "accepted"
                c.detail = str(edge.get("reason") or "")
            elif v in review_verdicts:
                c.status = "review"
                c.detail = str(edge.get("reason") or "")
            else:
                c.status = "rejected"
                c.detail = str(edge.get("reason") or v)

    payload = {
        "generated_at": _now(),
        "wiki": str(wiki_dir),
        "stats": {
            "tables": len(fields),
            "candidates": len(cands),
            "to_validate": len(to_validate),
            "accepted": sum(1 for c in cands if c.status == "accepted"),
            "review": sum(1 for c in cands if c.status == "review"),
            "rejected": sum(1 for c in cands if c.status == "rejected"),
        },
        "note": (
            "Old L0 missed same-name keys (e.g. menu_id↔menu_id) because it only "
            "nominated *_id→parent.id. Removed false friend menu.id→menu_id stays excluded."
        ),
        "candidates": [asdict(c) for c in cands],
    }
    (out_dir / "candidates.yaml").write_text(
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    if report is not None:
        (out_dir / "validate.yaml").write_text(
            yaml.safe_dump(report, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        (out_dir / "validate.md").write_text(
            render_markdown_report(report), encoding="utf-8"
        )

    lines = [
        f"# JOIN re-extract ({payload['generated_at']})",
        "",
        f"- tables: {payload['stats']['tables']}",
        f"- stats: `{payload['stats']}`",
        f"- note: {payload['note']}",
        "",
        "## Accepted (live fk_like / shared_domain)",
        "",
    ]
    for c in cands:
        if c.status != "accepted":
            continue
        lines.append(
            f"- `{c.left}` → `{c.right}`  _{c.strategy}_ score={c.score}  "
            f"verdict=`{c.verdict}` — {c.detail}"
        )
    lines += ["", "## Review (weak_overlap)", ""]
    for c in cands:
        if c.status != "review":
            continue
        lines.append(
            f"- `{c.left}` → `{c.right}`  _{c.strategy}_ score={c.score}  "
            f"verdict=`{c.verdict}` — {c.detail}"
        )
    lines += ["", "## Rejected sample", ""]
    n = 0
    for c in cands:
        if c.status != "rejected":
            continue
        lines.append(
            f"- `{c.left}` → `{c.right}`  _{c.strategy}_ — {c.detail or c.reason}"
        )
        n += 1
        if n >= 50:
            break
    lines.append("")
    (out_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    return payload


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()
