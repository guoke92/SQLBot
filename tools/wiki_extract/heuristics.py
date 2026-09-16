"""L0 heuristics: type family, common/prefix clusters, name anchors, identity joins."""

from __future__ import annotations

import re
from typing import Any

from tools.wiki_extract.introspect import is_pii_column

COMMON_COLUMNS = (
    "id",
    "enable",
    "create_time",
    "update_time",
    "create_by",
    "create_user",
    "update_by",
    "update_user",
)
TENANT_FIELDS = frozenset(
    {
        "tenant_id",
        "tenant_code",
        "db_tenant_code",
        "app_tenant_code",
        "organization_id",
    }
)
_TYPE_FAMILY = {
    "varchar": "string",
    "char": "string",
    "text": "string",
    "tinytext": "string",
    "mediumtext": "string",
    "longtext": "string",
    "enum": "string",
    "set": "string",
    "int": "number",
    "integer": "number",
    "bigint": "number",
    "smallint": "number",
    "tinyint": "number",
    "mediumint": "number",
    "decimal": "number",
    "numeric": "number",
    "double": "number",
    "float": "number",
    "real": "number",
    "bit": "boolean",
    "bool": "boolean",
    "boolean": "boolean",
    "date": "temporal",
    "datetime": "temporal",
    "timestamp": "temporal",
    "time": "temporal",
    "year": "temporal",
    "json": "structured",
    "blob": "structured",
    "tinyblob": "structured",
    "mediumblob": "structured",
    "longblob": "structured",
    "binary": "structured",
    "varbinary": "structured",
}
_FK_ID = re.compile(r"^(.+)_(id|code)$", re.I)
_REF_TABLE = re.compile(r"^ref_(.+)$", re.I)
_SNOWFLAKE = re.compile(r"^\d{15,}$")
_CODEISH = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,63}$")


def type_family(mysql_type: str) -> str:
    base = (mysql_type or "").split("(")[0].strip().lower()
    return _TYPE_FAMILY.get(base, "string")


def enum_page_key(table: str, column: str) -> str:
    """L0 enum identity is 表.字段 — not table_column."""
    return f"{table}.{column}"


def _enum_code_key(raw: object) -> str:
    text = str(raw or "").strip()
    if not text or text.lower() in {"none", "null"}:
        return ""
    return text


def compile_model(
    catalog: dict[str, Any],
    profile: dict[str, Any] | None = None,
    *,
    max_enum_distinct: int = 32,
) -> dict[str, Any]:
    database = str(catalog.get("database") or "")
    tables_in = catalog.get("tables") or {}
    profile_tables = (profile or {}).get("tables") or {}
    table_names = list(tables_in.keys())

    tables: dict[str, Any] = {}
    reviews: list[dict[str, Any]] = []
    enums: dict[str, Any] = {}
    value_index: list[dict[str, Any]] = []

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
        relations, rel_reviews = _identity_relations(tname, compiled, tables)
        compiled["relations"] = relations
        reviews.extend(rel_reviews)

    for tname, compiled in tables.items():
        stats = (profile_tables.get(tname) or {}).get("column_stats") or {}
        for cname, stat in stats.items():
            if is_pii_column(cname):
                continue
            values = stat.get("values") or {}
            n_distinct = int(stat.get("distinct") or len(values))
            if n_distinct <= 0 or n_distinct > max_enum_distinct:
                continue
            keys = [str(v) for v in values.keys()]
            if _looks_like_ids(keys):
                continue
            if _looks_like_enum_codes(keys):
                codes = {k: v for k, v in values.items() if _enum_code_key(k)}
                if not codes:
                    continue
                enum_key = enum_page_key(tname, cname)
                enums[enum_key] = {
                    "enum": enum_key,
                    "table": tname,
                    "column": cname,
                    "fields": [f"{tname}.{cname}"],
                    "values": {str(_enum_code_key(k)): {"trust": "proposed"} for k in codes},
                    "counts": {
                        str(_enum_code_key(k)): int(c) for k, c in codes.items()
                    },
                }
                field = _field(compiled, cname)
                if field is not None:
                    field["dictionary"] = enum_key
            else:
                value_index.append(
                    {
                        "table": tname,
                        "column": cname,
                        "values": [
                            {"value": str(k), "count": int(c)}
                            for k, c in values.items()
                        ],
                    }
                )

    return seal_l0_reviews(
        {
            "database": database,
            "generated_at": catalog.get("generated_at"),
            "table_order": table_names,
            "tables": tables,
            "enums": enums,
            "value_index": value_index,
            "reviews": reviews,
        }
    )


def seal_l0_reviews(model: dict[str, Any]) -> dict[str, Any]:
    """Rebuild grain/cluster/enum/similar REVIEWs. Keep PK-missing and JOIN items."""
    kept = [
        item
        for item in (model.get("reviews") or [])
        if item.get("kind") in {"missing", "unverified_join"}
    ]
    extra: list[dict[str, Any]] = []
    for tname, compiled in (model.get("tables") or {}).items():
        extra.append(
            _review(
                f"tables/{tname}#grain",
                "unanchored",
                "warning",
                "grain is L0 draft from PK; confirm from how code treats a row",
            )
        )
        for cluster in compiled.get("clusters") or []:
            if cluster.get("key") == "common":
                continue
            if cluster.get("trust") == "proposed" or cluster.get("confidence") == "proposed":
                source = cluster.get("source") or "prefix"
                extra.append(
                    _review(
                        f"tables/{tname}#clusters.{cluster['key']}",
                        "unanchored",
                        "warning",
                        f"{source} cluster {cluster['key']!r} is L0-proposed (no code evidence)",
                    )
                )
        for group in compiled.get("similar_fields") or []:
            fields = [str(x) for x in (group.get("fields") or []) if x]
            extra.append(
                _review(
                    f"tables/{tname}#similar_fields.{'_'.join(fields[:4])}",
                    "unanchored",
                    "warning",
                    str(group.get("note") or f"similar fields: {', '.join(fields)}"),
                )
            )
    for enum in (model.get("enums") or {}).values():
        extra.append(
            _review(
                f"enums/{enum['enum']}#values",
                "unanchored",
                "warning",
                "L0 enum candidate; labels require code; LLM keep ≠ confirmed",
            )
        )
    model["reviews"] = kept + extra
    return model


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
    common_present = [c for c in COMMON_COLUMNS if c in columns]
    if "code" in columns and "code" not in common_present:
        common_present.append("code")

    assigned: dict[str, str] = {c: "common" for c in common_present}
    prefix_groups = _prefix_groups(names, set(assigned))
    clusters: list[dict[str, Any]] = [
        {"key": "common", "title": "通用", "include": "always"}
    ]
    for key, members in prefix_groups.items():
        clusters.append(
            {
                "key": key,
                "title": key,
                "include": None,
                "trust": "proposed",
                "source": "prefix",
                "evidence": f"database_schema:{database}.{tname} prefix:{key}_",
            }
        )
        for col in members:
            assigned[col] = key

    fields: list[dict[str, Any]] = []
    for name, info in ordered:
        info = info or {}
        item: dict[str, Any] = {
            "name": name,
            "data_type": type_family(str(info.get("type") or "")),
            "description": str(info.get("comment") or ""),
            "nullable": bool(info.get("nullable", True)),
        }
        if name in assigned:
            item["cluster"] = assigned[name]
        fields.append(item)

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
        "clusters": clusters,
        "fields": fields,
        "column_names": names,
        "rows_estimate": int(tmeta.get("rows_estimate") or 0),
        "relations": [],
    }


def _prefix_groups(names: list[str], skip: set[str]) -> dict[str, list[str]]:
    buckets: dict[str, list[str]] = {}
    for name in names:
        if name in skip:
            continue
        key = _prefix_key(name)
        if not key:
            continue
        buckets.setdefault(key, []).append(name)
    return {k: v for k, v in buckets.items() if len(v) >= 2}


def _prefix_key(name: str) -> str | None:
    parts = [p for p in name.split("_") if p]
    if len(parts) < 2:
        return None
    if len(parts[0]) >= 4:
        return parts[0]
    if len(parts) >= 3:
        return f"{parts[0]}_{parts[1]}"
    return None


def _identity_relations(
    tname: str,
    compiled: dict[str, Any],
    tables: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    relations: list[dict[str, Any]] = []
    reviews: list[dict[str, Any]] = []
    pk_here = set(compiled.get("primary_key") or [])
    seen: set[tuple[str, str]] = set()
    for col in compiled.get("column_names") or []:
        if col in pk_here or col in TENANT_FIELDS:
            continue
        target = _resolve_target(col, tables)
        if not target or target == tname:
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
        seen.add(pair)
        relations.append(
            {
                "type": "EQUI_JOIN",
                "left": left,
                "right": right,
                "cardinality": "one_to_many",
                "trust": "proposed",
                "evidence": f"database_schema:{compiled.get('database')}.{tname}.{col}",
            }
        )
        reviews.append(
            _review(
                f"tables/{tname}#relations.{left}__{right}",
                "unverified_join",
                "warning",
                f"identity-bundle JOIN {left} → {right} is L0-proposed; needs code_path",
            )
        )
    return relations, reviews


def _resolve_target(col: str, tables: dict[str, Any]) -> str | None:
    ref = _REF_TABLE.match(col)
    if ref:
        candidate = ref.group(1)
        if candidate in tables:
            return candidate
    match = _FK_ID.match(col)
    if not match:
        return None
    stem = match.group(1)
    if stem in tables:
        return stem
    if f"{stem}_info" in tables:
        return f"{stem}_info"
    return None


def _target_key(target: dict[str, Any], local_col: str) -> str | None:
    """Map B.xxx_id → A.id (or single PK); B.xxx_code → A.code. Never cross-wire."""
    names = set(target.get("column_names") or [])
    pk = list(target.get("primary_key") or [])
    match = _FK_ID.match(local_col)
    kind = match.group(2).lower() if match else ""
    if kind == "code":
        return "code" if "code" in names else None
    if "id" in names:
        return "id"
    if len(pk) == 1:
        return pk[0]
    return None


def _looks_like_ids(values: list[str]) -> bool:
    if not values:
        return True
    return all(
        _SNOWFLAKE.match(v or "") or (v.isdigit() and len(v) > 12) for v in values
    )


def _looks_like_enum_codes(values: list[str]) -> bool:
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
