"""Single L0 JOIN caliber: endpoints, types, join roles, inclusion authenticity.

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
BUSINESS_CODE_COLUMNS = frozenset({"product_code", "platform_product_code"})
IDENTITY_COLUMNS = frozenset({"id", "code"})
JOIN_ROLE_IDENTITY = "identity"
JOIN_ROLE_BUSINESS_CODE = "business_code"
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
    """True when the pair is a business-code join (still a valid EQUI_JOIN)."""
    return classify_join_role(left_col, right_col) == JOIN_ROLE_BUSINESS_CODE


def classify_join_role(left_col: str, right_col: str) -> str:
    """identity = PK/id; business_code = code-to-code (product_code included)."""
    left_col = (left_col or "").strip()
    right_col = (right_col or "").strip()
    if left_col == "id":
        return JOIN_ROLE_IDENTITY
    if _is_business_code_pair(left_col, right_col):
        return JOIN_ROLE_BUSINESS_CODE
    if left_col == "code":
        return JOIN_ROLE_BUSINESS_CODE
    if left_col in IDENTITY_COLUMNS:
        return JOIN_ROLE_IDENTITY
    return JOIN_ROLE_BUSINESS_CODE


def _is_business_code_pair(left_col: str, right_col: str) -> bool:
    if right_col in BUSINESS_CODE_COLUMNS or left_col in BUSINESS_CODE_COLUMNS:
        return True
    if right_col.endswith("_code") and left_col in {"code", right_col}:
        return True
    if (
        right_col == left_col
        and right_col not in IDENTITY_COLUMNS
        and not right_col.endswith("_id")
    ):
        return True
    return False


def parent_join_columns(compiled: dict[str, Any]) -> list[str]:
    """Parent endpoints eligible for EQUI_JOIN: identity keys plus business codes."""
    names = set(compiled.get("column_names") or [])
    out = list(identity_columns(compiled))
    for col in BUSINESS_CODE_COLUMNS:
        if col in names and col not in out:
            out.append(col)
    return out


def allowed_parent_lefts(parent_c: dict[str, Any], right_col: str) -> set[str]:
    names = set(parent_c.get("column_names") or [])
    allowed = set(parent_join_columns(parent_c))
    if (
        right_col in names
        and right_col not in IDENTITY_COLUMNS
        and not right_col.endswith("_id")
    ):
        allowed.add(right_col)
    return allowed


def stamp_join_meta(compiled: dict[str, Any]) -> None:
    """Annotate join_role and priority (identity beats code-to-code on the same parent)."""
    identity_parents: set[str] = set()
    for rel in compiled.get("relations") or []:
        left = str(rel.get("left") or "")
        right = str(rel.get("right") or "")
        _, left_col = parse_fq(left)
        _, right_col = parse_fq(right)
        role = classify_join_role(left_col, right_col)
        rel["join_role"] = role
        parent, _ = parse_fq(left)
        if role == JOIN_ROLE_IDENTITY and parent:
            identity_parents.add(parent)
    for rel in compiled.get("relations") or []:
        parent, _ = parse_fq(str(rel.get("left") or ""))
        if (
            str(rel.get("join_role") or "") == JOIN_ROLE_BUSINESS_CODE
            and parent in identity_parents
        ):
            rel["priority"] = "secondary"
        else:
            rel["priority"] = "primary"
        seal_join_preview(rel)


def has_join_semantic(rel: dict[str, Any]) -> bool:
    """Name match or comment pointing at the peer table / FK wording."""
    name_ev = rel.get("name_evidence") or {}
    match = str(name_ev.get("match") or "none").strip().lower()
    if match not in {"", "none"}:
        return True
    if str(rel.get("source") or "") == "comment_fk":
        return True
    comment = str(name_ev.get("comment") or "")
    left = str(rel.get("left") or "")
    parent, _ = parse_fq(left)
    if parent and parent in comment:
        return True
    if any(token in comment for token in ("关联", "外键", "引用")):
        return True
    return False


def seal_join_preview(rel: dict[str, Any]) -> str:
    """Edge authenticity is 初审, not bag-inclusion.

    overlap.authenticity stays the value-fit probe. likely on the edge
    requires value-fit AND name/comment semantic.
    """
    overlap = rel.get("overlap") if isinstance(rel.get("overlap"), dict) else {}
    probed = bool(overlap.get("probed"))
    inclusion = str(
        (overlap.get("authenticity") if probed else None)
        or rel.get("authenticity")
        or "unknown"
    ).lower()
    if inclusion not in {"likely", "unlikely", "unknown"}:
        inclusion = "unknown"
    semantic = has_join_semantic(rel)
    rel.pop("preview_block", None)
    if inclusion == "likely" and not semantic:
        rel["authenticity"] = "unknown"
        rel["preview_block"] = "overlap_unsemantic"
        return "unknown"
    rel["authenticity"] = inclusion
    return inclusion


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
    """EQUI_JOIN type gate for probes.

    bigint/int stored as varchar on the FK side is normal in Java DO layers
    (Long → String). Treat number↔string as compatible so overlap can still run.
    """
    left = type_family(child_mysql)
    right = type_family(parent_mysql)
    if not left or not right:
        return True
    if left == right:
        return True
    return {left, right} <= {"number", "string"}


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
    semantic: bool = True,
) -> tuple[str, str]:
    """Return (authenticity, extra_note). Missing LLM vote keeps current.

    LLM cannot mint likely without name/comment semantic. Overlap-likely
    only outweighs LLM-unlikely when the edge already has semantic.
    """
    if llm_auth is None:
        return current, ""
    if llm_auth not in {"likely", "unlikely", "unknown"}:
        llm_auth = "unknown"
    if not semantic and llm_auth == "likely":
        return (
            "unknown",
            "LLM likely ignored: overlap fit without name/comment semantic",
        )
    if overlap_probed and overlap_auth == "likely" and llm_auth == "unlikely":
        if semantic:
            return "likely", "LLM unlikely vs overlap likely — edge kept"
        return (
            "unknown",
            "overlap fit without name/comment semantic — kept, not likely",
        )
    if overlap_probed and overlap_auth == "unlikely" and llm_auth == "likely":
        return (
            "unknown",
            "LLM likely vs overlap unlikely — edge kept, authenticity=unknown",
        )
    return llm_auth, ""


def may_nominate_join(
    model: dict[str, Any],
    left: str,
    right: str,
    *,
    window_lefts: set[str] | None = None,
    for_overlap_add: bool = False,
) -> str:
    """Empty string = pair may be an EQUI_JOIN candidate.

    Name heuristics, overlap add, and LLM propose all use this gate.
    """
    return link_reject_reason(
        model,
        left,
        right,
        window_lefts=window_lefts,
        for_overlap_add=for_overlap_add,
    )


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
    if left_col not in allowed_parent_lefts(parent_c, right_col):
        return "left_not_identity"
    if not types_compatible(
        mysql_type_of(child_c, right_col), mysql_type_of(parent_c, left_col)
    ):
        return "type_mismatch"
    role = classify_join_role(left_col, right_col)
    if for_overlap_add and role == JOIN_ROLE_IDENTITY:
        if not parent_is_unique(parent_c, left_col):
            return "parent_not_unique"
        if left_col == "id" and not family_ok_for_overlap_add(child, parent):
            return "weak_family"
    return ""
