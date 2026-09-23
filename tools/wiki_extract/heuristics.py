"""L0 heuristics: type family, name anchors, identity joins."""

from __future__ import annotations

import re
from typing import Any

from tools.wiki_extract.join_policy import (
    AUDIT_USER_FIELDS,
    TENANT_FIELDS,
    child_endpoint_reason,
    is_fk_like,
    may_nominate_join,
    mysql_type_of,
    stamp_join_meta,
    prefix_token_score,
    type_family,
)

_FK_ID = re.compile(r"^(.+)_(id|code)$", re.I)
_REF_TABLE = re.compile(r"^ref_(.+)$", re.I)
_FAMILY_HUB = {
    ("cust", "cust"): "cust_company_info",
    ("company", "cust"): "cust_company_info",
    ("person", "cust"): "cust_person_info",
    ("project", "tenant"): "tenant_project",
}
_SNOWFLAKE = re.compile(r"^\d{15,}$")
_CODEISH = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,63}$")
_NOISE_SIMILAR = TENANT_FIELDS | AUDIT_USER_FIELDS
_CODE_TOKEN = r"(?:[A-Za-z][A-Za-z0-9_]{0,47}|[YN01])"
_PAIR_CODE_FIRST = re.compile(
    rf"(?P<code>{_CODE_TOKEN})\s*[-:=：=]\s*(?P<label>[^\s,，;；/|]{{1,24}})"
)
_PAIR_LABEL_FIRST = re.compile(
    rf"(?P<label>[\u4e00-\u9fff]{{1,24}})\s*[-:=]\s*(?P<code>{_CODE_TOKEN})"
)
_PAIR_SPACE = re.compile(
    rf"(?P<code>{_CODE_TOKEN})\s+(?P<label>[\u4e00-\u9fff]{{1,24}})"
)
_PAIR_DIGIT = re.compile(
    r"(?P<code>\d{1,4})\s*[,，:：]\s*(?P<label>[\u4e00-\u9fff]{1,24})"
)
_BARE_YN = re.compile(r"(?<![A-Za-z0-9_])Y\s*[/|、,，]\s*N(?![A-Za-z0-9_])", re.I)
# Column comments like「…（tenant_project_approval_flow_config#flow_code）」
_COMMENT_FK = re.compile(
    r"(?P<table>[A-Za-z_][A-Za-z0-9_]*)\s*#\s*(?P<column>[A-Za-z_][A-Za-z0-9_]*)"
)


def parse_comment_fk(comment: str) -> list[tuple[str, str]]:
    """Extract explicit ``table#column`` FK hints from a column comment."""
    text = str(comment or "")
    if "#" not in text:
        return []
    out: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for match in _COMMENT_FK.finditer(text):
        pair = (match.group("table"), match.group("column"))
        if pair in seen:
            continue
        seen.add(pair)
        out.append(pair)
    return out


def dict_page_key(table: str, column: str) -> str:
    """L0 dict page identity is 表__字段 (git-safe).

    Not 表.字段 (collides with physical anchors), not 表_字段 (ambiguous),
    not 表::字段 (:: breaks some git/path tooling).
    """
    return f"{table}__{column}"


def compile_model(
    catalog: dict[str, Any],
    profile: dict[str, Any] | None = None,
    *,
    profile_instance: dict[str, Any] | None = None,
    max_enum_distinct: int = 32,
    overlap: dict[str, Any] | None = None,
) -> dict[str, Any]:
    database = str(catalog.get("database") or "")
    tables_in = catalog.get("tables") or {}
    profile_tables = (profile or {}).get("tables") or {}
    table_names = list(tables_in.keys())

    tables: dict[str, Any] = {}
    reviews: list[dict[str, Any]] = []
    dict_candidates: list[dict[str, Any]] = []

    for tname, tmeta in tables_in.items():
        pk = list(tmeta.get("primary_key") or [])
        if not pk:
            pk = _pk_from_indexes(tmeta.get("indexes") or [])
        compiled = _compile_table(tname, tmeta, pk, database)
        tables[tname] = compiled
        if not compiled["primary_key"]:
            reviews.append(
                _review(
                    f"tables/{tname}#primary_key",
                    "missing",
                    "error",
                    f"{tname} has no PRIMARY KEY in INFORMATION_SCHEMA",
                )
            )

    for tname, compiled in tables.items():
        # comment_fk first so explicit table#column wins over name heuristics.
        compiled["relations"] = _merge_relations(
            _comment_fk_relations(tname, compiled, tables),
            _identity_relations(tname, compiled, tables),
        )
        stamp_join_meta(compiled)
        _exclude_join_rights_from_anchors(compiled)

    from tools.wiki_extract.dict_triage import (
        apply_mechanical_only,
        collect_candidates,
    )
    from tools.wiki_extract.instance_index import apply_instance_index

    for tname, compiled in tables.items():
        stats = (profile_tables.get(tname) or {}).get("column_stats") or {}
        dict_candidates.extend(
            collect_candidates(compiled, stats, max_enum_distinct=max_enum_distinct)
        )

    packed: dict[str, Any] = {
        "database": database,
        "generated_at": catalog.get("generated_at"),
        "table_order": table_names,
        "tables": tables,
        "dicts": {},
        "instance_index": [],
        "dict_candidates": dict_candidates,
        "reviews": reviews,
    }
    apply_mechanical_only(packed)
    apply_instance_index(packed, catalog, profile, profile_instance)
    if overlap:
        from tools.wiki_extract.overlap import apply_overlap

        apply_overlap(packed, overlap)
    return seal_l0_reviews(packed)


def seal_l0_reviews(model: dict[str, Any]) -> dict[str, Any]:
    """Keep PK-missing, JOIN authenticity, similar (non-audit), enum comment conflicts."""
    kept = [
        item for item in (model.get("reviews") or []) if item.get("kind") == "missing"
    ]
    extra: list[dict[str, Any]] = []
    for tname, compiled in (model.get("tables") or {}).items():
        for rel in compiled.get("relations") or []:
            extra.append(_join_review(tname, compiled, rel))
        for group in compiled.get("similar_fields") or []:
            fields = [str(x) for x in (group.get("fields") or []) if x]
            if len(fields) < 2 or _noise_similar(fields):
                continue
            extra.append(
                _review(
                    f"tables/{tname}#similar_fields.{'_'.join(fields[:4])}",
                    "unanchored",
                    "info",
                    str(group.get("note") or f"similar fields: {', '.join(fields)}"),
                )
            )
    for item in (model.get("dicts") or {}).values():
        if not item.get("label_conflict"):
            continue
        extra.append(
            _review(
                f"dicts/{item['dict']}#values",
                "conflict",
                "warning",
                "column comment codes do not overlap profile values",
            )
        )
    model["reviews"] = kept + extra
    return model


def attach_comment_labels(
    values: dict[str, Any],
    comment: str,
    extra_labels: dict[str, str] | None = None,
    *,
    evidence: str = "",
) -> None:
    """Write proposed labels only when the comment can ground them."""
    observed = list(values)
    parsed = parse_comment_labels(comment, observed)
    incoming = {str(k): str(v).strip() for k, v in (extra_labels or {}).items() if v}
    incoming_ci = {k.upper(): v for k, v in incoming.items()}
    for code, row in values.items():
        if not isinstance(row, dict):
            continue
        proposed = (
            incoming.get(code) or incoming_ci.get(str(code).upper()) or parsed.get(code)
        )
        if not proposed:
            row.pop("label", None)
            row.pop("evidence", None)
            continue
        if not label_grounded(comment, str(code), proposed):
            row.pop("label", None)
            row.pop("evidence", None)
            continue
        row["label"] = proposed
        row["trust"] = row.get("trust") or "proposed"
        if evidence:
            row["evidence"] = evidence


def parse_comment_labels(
    comment: str, codes: list[str] | None = None
) -> dict[str, str]:
    """Pull code→label pairs out of a column comment. Empty if there is no mapping."""
    text = str(comment or "").strip()
    if not text:
        return {}
    allow = {str(c): str(c) for c in (codes or []) if c}
    allow_ci = {k.upper(): k for k in allow}
    found: dict[str, str] = {}

    def _take(code: str, label: str) -> None:
        code = str(code or "").strip()
        label = str(label or "").strip().strip("。；;,.）)")
        if not code or not label or label.upper() == code.upper():
            return
        if allow:
            key = allow.get(code) or allow_ci.get(code.upper())
            if not key:
                return
            code = key
        elif codes is not None:
            return
        found.setdefault(code, label)

    for match in _PAIR_LABEL_FIRST.finditer(text):
        _take(match.group("code"), match.group("label"))
    for match in _PAIR_CODE_FIRST.finditer(text):
        _take(match.group("code"), match.group("label"))
    for match in _PAIR_SPACE.finditer(text):
        _take(match.group("code"), match.group("label"))
    for match in _PAIR_DIGIT.finditer(text):
        _take(match.group("code"), match.group("label"))
    return found


def label_grounded(comment: str, code: str, label: str) -> bool:
    """Accept a label only when the comment contains both the code and the gloss."""
    text = str(comment or "")
    code = str(code or "").strip()
    label = str(label or "").strip()
    if not text or not code or not label:
        return False
    if label.upper() == code.upper():
        return False
    if label not in text and _compact(label) not in _compact(text):
        return False
    if not _has_code_token(text, code):
        return False
    if code.upper() in {"Y", "N"} and _BARE_YN.search(text):
        # 「是否启用：Y/N」is a field gloss, not per-code labels.
        if not re.search(rf"{re.escape(code)}\s*[-:=]", text, re.I) and not re.search(
            rf"[\u4e00-\u9fff]\s*[-:=]\s*{re.escape(code)}", text, re.I
        ):
            return False
    idx = _code_index(text, code)
    if idx < 0:
        return False
    window = text[max(0, idx - 32) : idx + len(code) + 32]
    return label in window or _compact(label) in _compact(window)


def _compact(text: str) -> str:
    return re.sub(r"\s+", "", text)


def _has_code_token(comment: str, code: str) -> bool:
    return (
        re.search(rf"(?<![A-Za-z0-9_]){re.escape(code)}(?![A-Za-z0-9_])", comment)
        is not None
    )


def _code_index(comment: str, code: str) -> int:
    match = re.search(rf"(?<![A-Za-z0-9_]){re.escape(code)}(?![A-Za-z0-9_])", comment)
    return match.start() if match else -1


def _comment_code_conflict(comment: str, observed: list[str]) -> bool:
    mapped = {c.upper() for c in parse_comment_labels(comment, None)}
    obs = {str(c).upper() for c in observed if c}
    if not mapped or not obs:
        return False
    return mapped.isdisjoint(obs)


def _pk_from_indexes(indexes: list[dict[str, Any]]) -> list[str]:
    for item in indexes:
        if str(item.get("name") or "").upper() == "PRIMARY":
            return list(item.get("columns") or [])
    return []


def _compile_table(
    tname: str, tmeta: dict[str, Any], pk: list[str], database: str
) -> dict[str, Any]:
    columns = tmeta.get("columns") or {}
    ordered = sorted(
        columns.items(),
        key=lambda kv: int((kv[1] or {}).get("pos") or 10_000),
    )
    names = [name for name, _ in ordered]
    fields: list[dict[str, Any]] = []
    for name, info in ordered:
        info = info or {}
        fields.append(
            {
                "name": name,
                "data_type": type_family(str(info.get("type") or "")),
                "mysql_type": str(info.get("type") or ""),
                "description": str(info.get("comment") or ""),
                "nullable": bool(info.get("nullable", True)),
            }
        )

    anchors = [
        c
        for c in names
        if c in {"name", "code", "title"}
        or c.endswith("_name")
        or (c.endswith("_code") and c not in TENANT_FIELDS)
    ]
    pk_label = ",".join(pk) if pk else "?"
    return {
        "table": tname,
        "database": database,
        "description": str(tmeta.get("comment") or tname),
        "inactive": False,
        "primary_key": pk,
        "grain": f"一行一记录（{pk_label}）",
        "name_anchors": anchors,
        "fields": fields,
        "column_names": names,
        "rows_estimate": int(tmeta.get("rows_estimate") or 0),
        "indexed_columns": _indexed_columns(tmeta),
        "relations": [],
    }


def _merge_relations(
    *batches: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Dedupe by (left, right); earlier batches win (comment_fk before name)."""
    seen: set[tuple[str, str]] = set()
    out: list[dict[str, Any]] = []
    for batch in batches:
        for rel in batch:
            pair = (str(rel.get("left") or ""), str(rel.get("right") or ""))
            if not pair[0] or not pair[1] or pair in seen:
                continue
            seen.add(pair)
            out.append(rel)
    return out


def _comment_fk_relations(
    tname: str,
    compiled: dict[str, Any],
    tables: dict[str, Any],
) -> list[dict[str, Any]]:
    """Nominate EQUI_JOIN from explicit ``table#column`` in column comments."""
    relations: list[dict[str, Any]] = []
    pk_here = set(compiled.get("primary_key") or [])
    for field in compiled.get("fields") or []:
        col = str(field.get("name") or "")
        if not col or col in pk_here or col in TENANT_FIELDS:
            continue
        comment = str(field.get("description") or "")
        for target, target_col in parse_comment_fk(comment):
            if target not in tables or target == tname:
                continue
            peer = tables[target]
            peer_cols = set(peer.get("column_names") or [])
            if target_col not in peer_cols or target_col in TENANT_FIELDS:
                continue
            if child_endpoint_reason(col, mysql_type_of(compiled, col)):
                continue
            left = f"{target}.{target_col}"
            right = f"{tname}.{col}"
            if may_nominate_join({"tables": tables}, left, right):
                continue
            relations.append(
                {
                    "type": "EQUI_JOIN",
                    "left": left,
                    "right": right,
                    "cardinality": "one_to_many",
                    "trust": "proposed",
                    "authenticity": "unknown",
                    "source": "comment_fk",
                    "name_evidence": {
                        "match": "comment_fk",
                        "stem": target,
                        "comment": comment[:80],
                    },
                    "overlap": {"probed": False},
                    "evidence": (
                        f"database_schema:{compiled.get('database')}.{tname}.{col}"
                        f"#comment_fk:{target}#{target_col}"
                    ),
                }
            )
    return relations


def _identity_relations(
    tname: str,
    compiled: dict[str, Any],
    tables: dict[str, Any],
) -> list[dict[str, Any]]:
    relations: list[dict[str, Any]] = []
    pk_here = set(compiled.get("primary_key") or [])
    seen: set[tuple[str, str]] = set()
    comment_owned = {
        str(field.get("name") or "")
        for field in compiled.get("fields") or []
        if parse_comment_fk(str(field.get("description") or ""))
    }
    for col in compiled.get("column_names") or []:
        if col in pk_here or col in TENANT_FIELDS:
            continue
        if col in comment_owned:
            continue
        if not is_fk_like(col):
            continue
        if child_endpoint_reason(col, mysql_type_of(compiled, col)):
            continue
        hit = _resolve_target_hit(col, tables, tname)
        if not hit:
            continue
        target, match_kind, stem = hit
        if target == tname:
            continue
        identity_col = _target_key(tables[target], col)
        if not identity_col or identity_col in TENANT_FIELDS:
            continue
        # pages.md: left = identity table.id|code, right = FK col; written on FK page.
        left = f"{target}.{identity_col}"
        right = f"{tname}.{col}"
        pair = (left, right)
        if pair in seen:
            continue
        if may_nominate_join({"tables": tables}, left, right):
            continue
        seen.add(pair)
        field = _field(compiled, col)
        comment = str((field or {}).get("description") or "")
        relations.append(
            {
                "type": "EQUI_JOIN",
                "left": left,
                "right": right,
                "cardinality": "one_to_many",
                "trust": "proposed",
                "authenticity": "unknown",
                "source": "name",
                "name_evidence": {
                    "match": match_kind,
                    "stem": stem,
                    "comment": comment[:80],
                },
                "overlap": {"probed": False},
                "evidence": f"database_schema:{compiled.get('database')}.{tname}.{col}",
            }
        )
    return relations


def _exclude_join_rights_from_anchors(compiled: dict[str, Any]) -> None:
    rights = {
        str(rel.get("right") or "").split(".", 1)[-1]
        for rel in compiled.get("relations") or []
    }
    compiled["name_anchors"] = [
        col for col in (compiled.get("name_anchors") or []) if col not in rights
    ]


def _join_review(
    tname: str, compiled: dict[str, Any], rel: dict[str, Any]
) -> dict[str, Any]:
    left = str(rel.get("left") or "")
    right = str(rel.get("right") or "")
    col = right.split(".", 1)[-1] if "." in right else right
    field = _field(compiled, col)
    comment = str((field or {}).get("description") or "")
    auth = str(rel.get("authenticity") or "unknown")
    name_ev = rel.get("name_evidence") or {}
    match = str(name_ev.get("match") or "none")
    overlap = rel.get("overlap") or {}
    note = (
        f"identity-bundle JOIN {left} → {right} is L0-proposed; "
        f"authenticity={auth}; name_match={match}"
    )
    if overlap.get("probed"):
        ratio = overlap.get("ratio")
        rev = overlap.get("ratio_reverse")
        note += f"; overlap_ratio={ratio}"
        if rev is not None:
            note += f"; overlap_ratio_reverse={rev}"
        if overlap.get("deepened"):
            note += "; deepened=true"
    elif overlap.get("skipped"):
        note += f"; overlap={overlap.get('skipped')}"
    else:
        note += "; overlap=not_probed"
    if comment:
        note += f"; comment={comment[:80]}"
    extra = str(rel.get("authenticity_note") or "").strip()
    if extra:
        note += f"; {extra}"
    kind = "unverified_join"
    if str(rel.get("preview_block") or "") == "overlap_unsemantic":
        kind = "join_overlap_unsemantic"
        note = "值域契合但列名/注释无关联语义，保留待源码或人工复核。 " + note
    return _review(
        f"tables/{tname}#relations.{left}__{right}",
        kind,
        "warning",
        note,
    )


def _noise_similar(fields: list[str]) -> bool:
    return bool(fields) and all(name in _NOISE_SIMILAR for name in fields)


def _resolve_target(col: str, tables: dict[str, Any], tname: str = "") -> str | None:
    hit = _resolve_target_hit(col, tables, tname)
    return hit[0] if hit else None


def _resolve_target_hit(
    col: str, tables: dict[str, Any], tname: str = ""
) -> tuple[str, str, str] | None:
    """Map a local column to (table, match_kind, stem). Never invent a missing table."""
    ref = _REF_TABLE.match(col)
    if ref:
        rest = ref.group(1)
        if rest in tables and rest != tname:
            return rest, "exact_table", rest
        if tname and rest.startswith(f"{tname}_"):
            tail = rest[len(tname) + 1 :]
            if tail in tables and tail != tname:
                return tail, "long_ref", tail
        hit = _longest_table_suffix(rest, tables, exclude=tname)
        if hit:
            return hit, "long_ref", hit
    match = _FK_ID.match(col)
    if not match:
        return None
    stem = match.group(1)
    if stem in tables and stem != tname:
        return stem, "exact_table", stem
    info = f"{stem}_info"
    if info in tables and info != tname:
        return info, "stem_info", stem
    scored = _score_suffix_tables(stem, tname, tables)
    if scored:
        return scored, "family_suffix", stem
    hub = _family_hub(stem, tname, tables)
    if hub:
        return hub, "family_hub", stem
    return None


def _longest_table_suffix(
    text: str, tables: dict[str, Any], *, exclude: str
) -> str | None:
    best: str | None = None
    for tbl in tables:
        if tbl == exclude:
            continue
        if text == tbl or text.endswith(f"_{tbl}"):
            if best is None or len(tbl) > len(best):
                best = tbl
    return best


def _score_suffix_tables(stem: str, tname: str, tables: dict[str, Any]) -> str | None:
    """Prefer the table sharing the longest underscore prefix with the local table."""
    ranked: list[tuple[int, int, int, str]] = []
    for tbl in tables:
        if tbl == tname:
            continue
        if not (
            tbl.endswith(f"_{stem}")
            or tbl.endswith(f"_{stem}_info")
            or tbl == f"{stem}_info"
        ):
            continue
        score = prefix_token_score(tname, tbl)
        if score <= 0:
            continue
        tightness = 0
        if tbl == f"{stem}_info":
            tightness = 3
        elif tbl.endswith(f"_{stem}_info"):
            tightness = 2
        elif tbl.endswith(f"_{stem}"):
            tightness = 1
        # Tie-break: tighter suffix, then shorter name (cust_company_info over
        # cust_head_company_info when both only share the family token).
        ranked.append((score, tightness, -len(tbl), tbl))
    if not ranked:
        return None
    ranked.sort(reverse=True)
    return ranked[0][3]


def _family_hub(stem: str, tname: str, tables: dict[str, Any]) -> str | None:
    head = tname.split("_", 1)[0] if tname else ""
    hub = _FAMILY_HUB.get((stem, head))
    if hub and hub in tables and hub != tname:
        return hub
    return None


def _indexed_columns(tmeta: dict[str, Any]) -> list[str]:
    names: set[str] = set()
    for idx in tmeta.get("indexes") or []:
        for col in idx.get("columns") or []:
            if col:
                names.add(str(col))
    return sorted(names)


def _target_key(target: dict[str, Any], local_col: str) -> str | None:
    """Map B.xxx_id → A.id; B.xxx_code → A.xxx_code when present, else A.code.

    Prefer same-name business code columns (``flow_code``→``flow_code``) over
    blindly wiring every ``*_code`` onto peer ``code`` (UUID/row key).
    """
    names = set(target.get("column_names") or [])
    pk = list(target.get("primary_key") or [])
    match = _FK_ID.match(local_col)
    kind = match.group(2).lower() if match else ""
    if kind == "code":
        if local_col in names:
            return local_col
        return "code" if "code" in names else None
    if "id" in names:
        return "id"
    if len(pk) == 1:
        return pk[0]
    return None


def looks_like_ids(values: list[str]) -> bool:
    if not values:
        return True
    return all(
        _SNOWFLAKE.match(v or "") or (v.isdigit() and len(v) > 12) for v in values
    )


def looks_like_enum_codes(values: list[str]) -> bool:
    if not values:
        return False
    scored = 0
    for raw in values:
        text = (raw or "").strip()
        if not text:
            continue
        if _CODEISH.match(text) or re.fullmatch(r"[YN01]", text) or text.isupper():
            scored += 1
            continue
        if any("\u4e00" <= ch <= "\u9fff" for ch in text):
            return False
    return scored >= max(1, int(len(values) * 0.6))


def _field(compiled: dict[str, Any], name: str) -> dict[str, Any] | None:
    for item in compiled.get("fields") or []:
        if item.get("name") == name:
            return item
    return None


def _review(claim_path: str, kind: str, severity: str, note: str) -> dict[str, Any]:
    return {
        "claim_path": claim_path,
        "kind": kind,
        "severity": severity,
        "status": "open",
        "note": note,
    }
