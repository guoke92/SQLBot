"""Single L0 JOIN caliber: endpoints, types, copy keys, inclusion authenticity.

Name heuristics, value-overlap probes, and LLM propose/review all call this
module. Do not re-implement skip lists, type families, or likely/unlikely
thresholds elsewhere.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from tools.wiki_extract.introspect import is_pii_column

TENANT_FIELDS = frozenset(
    {
        "tenant_id",
        "tenant_code",
        "db_tenant_code",
        "app_tenant_code",
        "organization_id",
    }
)
AUDIT_USER_FIELDS = frozenset({"create_by", "create_user", "update_by", "update_user"})
GENERIC_CHILD_NAMES = frozenset(
    {
        "id",
        "create_time",
        "update_time",
        "req_time",
        "created_at",
        "updated_at",
        "create_date",
        "update_date",
    }
)
AUDIT_TIME_SUFFIX = ("_time", "_date", "_at", "_dt")
GEO_CODE_SUFFIX = ("_province_code", "_city_code")
# Workflow/audit stems only — not generic words like user/parent/file/task.
FK_STEM_BLOCKLIST = frozenset(
    {
        "act_procinst",
        "create",
        "update",
        "trace",
        "trans",
        "token",
        "session",
        "request",
        "source",
        "default",
        "original",
        "operator",
        "manager",
        "root",
        "main_data",
    }
)
COPY_CHILD_COLUMNS = frozenset({"product_code"})
IDENTITY_COLUMNS = frozenset({"id", "code"})
TEMPORAL_TYPES = frozenset({"date", "datetime", "timestamp", "time", "year"})
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
_FKISH = re.compile(r"^(?:ref_.+|.+_(?:id|code)|.+ref(?:_[a-z0-9]+)?)$", re.I)
_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

LIKELY = 0.95
UNLIKELY = 0.05
CONTROVERSIAL_LOW = 0.30
MIN_DISTINCT = 3
FAMILY_TOKEN_MIN = 2


def type_family(mysql_type: str) -> str:
    base = (mysql_type or "").split("(")[0].strip().lower()
    return _TYPE_FAMILY.get(base, "string")


def mysql_base(mysql_type: str) -> str:
    return (mysql_type or "").split("(")[0].strip().lower()


def parse_fq(name: str) -> tuple[str, str]:
    if "." not in (name or ""):
        return "", str(name or "")
    table, col = str(name).split(".", 1)
    return table, col


def qualify(table: str, column: str) -> str:
    return f"{table}.{column}"


def sql_ident(name: str) -> str:
    if not _IDENT.match(name or ""):
        raise ValueError(f"refusing to quote identifier {name!r}")
    return f"`{name}`"


def is_geo_code(column: str) -> bool:
    return (column or "").endswith(GEO_CODE_SUFFIX)


def is_fk_like(column: str) -> bool:
    return bool(_FKISH.match(column or ""))


def fk_stem(column: str) -> str:
    name = column or ""
    if name.lower().startswith("ref_"):
        return name[4:]
    if "_" not in name:
        return name
    return name.rsplit("_", 1)[0]


def is_blocked_fk_stem(column: str) -> bool:
    return fk_stem(column).lower() in FK_STEM_BLOCKLIST or (
        column or ""
    ).lower().startswith("act_procinst")


def child_endpoint_reason(column: str, mysql_type: str = "") -> str:
    """Why this column must not be an overlap/FK child endpoint. Empty = allowed."""
    name = (column or "").strip()
    lowered = name.lower()
    if lowered in GENERIC_CHILD_NAMES:
        return "skipped_generic_column"
    if lowered.endswith(AUDIT_TIME_SUFFIX) and lowered in GENERIC_CHILD_NAMES:
        return "skipped_generic_column"
    if lowered.endswith(AUDIT_TIME_SUFFIX) and lowered.split("_", 1)[0] in {
        "create",
        "update",
        "req",
        "gmt",
    }:
        return "skipped_generic_column"
    if mysql_base(mysql_type) in TEMPORAL_TYPES:
        return "skipped_temporal_type"
    if is_pii_column(name) or name in TENANT_FIELDS:
        return "skipped_restricted"
    if is_geo_code(name) or is_blocked_fk_stem(name):
        return "skipped_restricted"
    return ""


def is_copy_key(right_col: str, left_col: str) -> bool:
    """Shared business codes, not identity keys. Not an EQUI_JOIN."""
    if right_col in COPY_CHILD_COLUMNS:
        return True
    if right_col == left_col and right_col not in IDENTITY_COLUMNS:
        return True
    return False


def identity_columns(compiled: dict[str, Any]) -> list[str]:
    names = set(compiled.get("column_names") or [])
    out: list[str] = []
    for col in ("id", "code"):
        if col in names:
            out.append(col)
    for col in compiled.get("primary_key") or []:
        if col not in out:
            out.append(str(col))
    return out


def is_identity_column(compiled: dict[str, Any], column: str) -> bool:
    return column in identity_columns(compiled)


def parent_is_unique(compiled: dict[str, Any], column: str) -> bool:
    """L0 identity keys (id/code) and single-column PKs count as unique parents."""
    if column in IDENTITY_COLUMNS:
        return True
    pk = [str(x) for x in (compiled.get("primary_key") or [])]
    return pk == [column]


def types_compatible(child_mysql: str, parent_mysql: str) -> bool:
    left = type_family(child_mysql)
    right = type_family(parent_mysql)
    if not left or not right:
        return True
    return left == right


def mysql_type_of(compiled: dict[str, Any], column: str) -> str:
    for field in compiled.get("fields") or []:
        if field.get("name") == column:
            return str(field.get("mysql_type") or "")
    return ""


def prefix_token_count(left: str, right: str) -> int:
    a = left.split("_")
    b = right.split("_")
    n = 0
    for x, y in zip(a, b, strict=False):
        if x != y:
            break
        n += 1
    return n


def prefix_token_score(left: str, right: str) -> int:
    n = prefix_token_count(left, right)
    if n == 0:
        return 0
    joined = "_".join(left.split("_")[:n])
    return len(joined) if len(joined) >= 3 else 0


def family_ok_for_overlap_add(child_table: str, parent_table: str) -> bool:
    """Overlap-nominated id joins need a 2-token family, not a shared 'cust'."""
    return prefix_token_count(child_table, parent_table) >= FAMILY_TOKEN_MIN


@dataclass(frozen=True)
class Inclusion:
    ok: bool
    hit: int
    sample_size: int
    ratio: float | None

    @property
    def miss(self) -> int | None:
        if not self.ok:
            return None
        return max(0, self.sample_size - self.hit)


@dataclass(frozen=True)
class Authenticity:
    value: str
    deepen: bool


def decide_authenticity(
    *,
    sample_size: int,
    forward: float | None,
    reverse: float | None = None,
    query_ok: bool = True,
    deepened: bool = False,
) -> Authenticity:
    """One threshold table for name-edge review and overlap nomination."""
    if not query_ok or forward is None:
        return Authenticity("unknown", False)
    if sample_size < MIN_DISTINCT:
        return Authenticity("unknown", False)
    if forward >= LIKELY:
        return Authenticity("likely", False)
    if forward <= UNLIKELY:
        if deepened and reverse is not None and reverse >= 0.80:
            return Authenticity("unknown", False)
        return Authenticity("unlikely", False)
    if UNLIKELY < forward < LIKELY:
        return Authenticity("unknown", not deepened)
    return Authenticity("unknown", False)


def merge_llm_authenticity(
    *,
    current: str,
    overlap_probed: bool,
    overlap_auth: str,
    llm_auth: str | None,
) -> tuple[str, str]:
    """Return (authenticity, extra_note). Missing LLM vote keeps current."""
    if llm_auth is None:
        return current, ""
    if llm_auth not in {"likely", "unlikely", "unknown"}:
        llm_auth = "unknown"
    if overlap_probed and overlap_auth == "likely" and llm_auth == "unlikely":
        return "likely", "LLM unlikely vs overlap likely — edge kept"
    if overlap_probed and overlap_auth == "unlikely" and llm_auth == "likely":
        return (
            "unknown",
            "LLM likely vs overlap unlikely — edge kept, authenticity=unknown",
        )
    return llm_auth, ""


def link_reject_reason(
    model: dict[str, Any],
    left: str,
    right: str,
    *,
    window_lefts: set[str] | None = None,
    for_overlap_add: bool = False,
) -> str:
    """Empty string = pair may be an EQUI_JOIN candidate."""
    parent, left_col = parse_fq(left)
    child, right_col = parse_fq(right)
    if not parent or not child or not left_col or not right_col:
        return "unbound"
    if is_copy_key(right_col, left_col):
        return "product_code_copy" if right_col in COPY_CHILD_COLUMNS else "copy_key"
    tables = model.get("tables") or {}
    if parent not in tables or child not in tables:
        return "unknown_table"
    if window_lefts is not None and left not in window_lefts:
        return "outside_window"
    parent_c = tables[parent]
    child_c = tables[child]
    parent_cols = set(parent_c.get("column_names") or [])
    child_cols = set(child_c.get("column_names") or [])
    if left_col not in parent_cols or right_col not in child_cols:
        return "unknown_column"
    reason = child_endpoint_reason(right_col, mysql_type_of(child_c, right_col))
    if reason:
        return reason
    if not is_identity_column(parent_c, left_col):
        return "left_not_identity"
    if not types_compatible(
        mysql_type_of(child_c, right_col), mysql_type_of(parent_c, left_col)
    ):
        return "type_mismatch"
    if for_overlap_add:
        if not parent_is_unique(parent_c, left_col):
            return "parent_not_unique"
        if left_col == "id" and not family_ok_for_overlap_add(child, parent):
            return "weak_family"
    return ""
