"""Instance list: utterance → (table, column) TopK. Not a wiki page, not a dict.

Independent of dict_triage. No distinct<=32 cap. Verdicts are index|skip only.
"""

from __future__ import annotations

import datetime as dt
import re
from typing import Any

from tools.wiki_extract.join_policy import AUDIT_USER_FIELDS, TENANT_FIELDS

DEST_INDEX = "index"
DEST_SKIP = "skip"
INSTANCE_TOP_K = 200

_CREDIT_NAME = re.compile(
    r"(credit_code|uscc|uniscid|org_code|certification_no|social_credit|"
    r"unified_code|usc_code)",
    re.I,
)
_CREDIT_COMMENT = re.compile(r"统一社会信用|组织机构代码|信用代码|统一信用")
_NAME_HINT = re.compile(
    r"(^name$|_name$|^company_name$|_company_name$|^customer|"
    r"cust_name|^dept|_dept$|^org_name$|_org_name$|channel_name|channel_code)",
    re.I,
)
_STATUS_UTTERANCE = re.compile(r"(^status$|_status$|^state$|_state$)")
_SECRET = re.compile(
    r"(password|passwd|(^|_)pwd($|_)|secret|token|api_key|private_key|密码)",
    re.I,
)
_TIME_NAME = re.compile(
    r"(^create_time$|^update_time$|^req_time$|_time$|_date$|_at$|_dt$)",
    re.I,
)
_SKIP_TYPES = frozenset(
    {
        "date",
        "datetime",
        "timestamp",
        "time",
        "year",
        "blob",
        "tinyblob",
        "mediumblob",
        "longblob",
        "binary",
        "varbinary",
        "json",
        "longtext",
        "mediumtext",
    }
)
_SNOWFLAKE = re.compile(r"^[0-9]{15,}$")
_UUID = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
_HEX64 = re.compile(r"^[0-9a-fA-F]{32,}$")
_JSONISH = re.compile(r"^\s*[\[{]")


def skip_instance_column(
    column: str,
    *,
    mysql_type: str = "",
    comment: str = "",
    pk: list[str] | None = None,
) -> str:
    """Mechanical hard-exclude. Empty string means the column may be indexed."""
    name = str(column or "").strip()
    lower = name.lower()
    if not name:
        return "empty"
    if lower in AUDIT_USER_FIELDS or lower in {"create_user", "update_user"}:
        return "audit_user"
    if _TIME_NAME.search(lower):
        return "temporal_name"
    base = str(mysql_type or "").split("(", 1)[0].lower()
    if base in _SKIP_TYPES:
        return "temporal_or_blob_type"
    if lower == "id" or (
        pk and lower in {p.lower() for p in pk} and lower.endswith("id")
    ):
        if lower == "id":
            return "surrogate_pk"
    if _SECRET.search(lower) or _SECRET.search(str(comment or "")):
        return "secret"
    from tools.wiki_extract.introspect import is_pii_column

    if is_pii_column(name):
        return "pii"
    if lower.endswith("_id") and lower != "id":
        return "surrogate_fk"
    return ""


def nominate_instance_column(
    column: str,
    *,
    comment: str = "",
    mysql_type: str = "",
    name_anchors: list[str] | None = None,
    pk: list[str] | None = None,
) -> bool:
    """Business-meaning nomination. Independent of cardinality and dict_triage."""
    if skip_instance_column(column, mysql_type=mysql_type, comment=comment, pk=pk):
        return False
    name = str(column or "").strip()
    lower = name.lower()
    anchors = {str(a).lower() for a in (name_anchors or [])}
    if lower in anchors:
        return True
    if _CREDIT_NAME.search(lower) or _CREDIT_COMMENT.search(str(comment or "")):
        return True
    if _NAME_HINT.search(lower):
        return True
    if lower in TENANT_FIELDS or lower.endswith("_tenant_code"):
        return True
    if _STATUS_UTTERANCE.search(lower):
        return True
    if lower.endswith("_code") and lower not in {p.lower() for p in (pk or [])}:
        return True
    return False


def should_profile_column(
    column: str,
    *,
    comment: str = "",
    mysql_type: str = "",
    name_anchors: list[str] | None = None,
    pk: list[str] | None = None,
) -> bool:
    return nominate_instance_column(
        column,
        comment=comment,
        mysql_type=mysql_type,
        name_anchors=name_anchors,
        pk=pk,
    )


def apply_instance_index(
    model: dict[str, Any],
    catalog: dict[str, Any] | None = None,
    profile: dict[str, Any] | None = None,
    profile_instance: dict[str, Any] | None = None,
    *,
    top_k: int = INSTANCE_TOP_K,
) -> dict[str, Any]:
    """Fill model['instance_index'] from nominated columns + TopK samples."""
    tables = model.get("tables") or {}
    catalog_tables = (catalog or {}).get("tables") or {}
    entries: list[dict[str, Any]] = []
    for tname, compiled in tables.items():
        tmeta = catalog_tables.get(tname) or {}
        columns = tmeta.get("columns") or {}
        pk = list(compiled.get("primary_key") or tmeta.get("primary_key") or [])
        anchors = list(compiled.get("name_anchors") or [])
        names = list(compiled.get("column_names") or columns.keys())
        for col in names:
            cinfo = columns.get(col) or {}
            comment = str(
                cinfo.get("comment")
                or next(
                    (
                        f.get("description") or ""
                        for f in (compiled.get("fields") or [])
                        if f.get("name") == col
                    ),
                    "",
                )
            )
            mysql_type = str(
                cinfo.get("type")
                or next(
                    (
                        f.get("data_type") or ""
                        for f in (compiled.get("fields") or [])
                        if f.get("name") == col
                    ),
                    "",
                )
            )
            if not nominate_instance_column(
                col,
                comment=comment,
                mysql_type=mysql_type,
                name_anchors=anchors,
                pk=pk,
            ):
                continue
            values = _topk_values(
                tname,
                col,
                profile=profile,
                profile_instance=profile_instance,
                top_k=top_k,
            )
            if not values:
                continue
            if looks_like_opaque_instance_values(values):
                continue
            entries.append(
                {
                    "table": tname,
                    "column": col,
                    "comment": comment,
                    "values": values,
                }
            )
    entries.sort(key=lambda e: (str(e.get("table") or ""), str(e.get("column") or "")))
    model["instance_index"] = entries
    return model


def looks_like_opaque_instance_values(values: list[dict[str, Any]]) -> bool:
    """Skip UUID / snowflake / hex blob / JSON payload columns after sampling."""
    keys = [
        str(row.get("value") or "").strip() for row in values if isinstance(row, dict)
    ]
    keys = [k for k in keys if k]
    if not keys:
        return False
    opaque = 0
    for key in keys:
        if (
            _UUID.match(key)
            or _SNOWFLAKE.match(key)
            or _HEX64.match(key)
            or _JSONISH.match(key)
        ):
            opaque += 1
    return opaque >= max(1, int(0.8 * len(keys)))


def packed_instance_index(model: dict[str, Any]) -> dict[str, Any]:
    today = str(model.get("generated_at") or dt.date.today().isoformat())
    return {
        "generated_at": today,
        "database": model.get("database"),
        "entries": model.get("instance_index") or [],
    }


def _topk_values(
    table: str,
    column: str,
    *,
    profile: dict[str, Any] | None,
    profile_instance: dict[str, Any] | None,
    top_k: int,
) -> list[dict[str, Any]]:
    inst = ((profile_instance or {}).get("tables") or {}).get(table) or {}
    col = (inst.get("column_stats") or {}).get(column) or {}
    raw = col.get("top_values") or col.get("values")
    rows = _normalize_values(raw, top_k)
    if rows:
        return rows
    low = ((profile or {}).get("tables") or {}).get(table) or {}
    stats = (low.get("column_stats") or {}).get(column) or {}
    return _normalize_values(stats.get("values"), top_k)


def _normalize_values(raw: object, top_k: int) -> list[dict[str, Any]]:
    items: list[tuple[str, int]] = []
    if isinstance(raw, list):
        for row in raw:
            if isinstance(row, dict):
                value = str(row.get("value") or row.get("v") or "").strip()
                count = int(row.get("count") or row.get("c") or 0)
            else:
                value = str(row or "").strip()
                count = 0
            if value and value.lower() not in {"none", "null"}:
                items.append((value, count))
    elif isinstance(raw, dict):
        for value, count in raw.items():
            text = str(value or "").strip()
            if text and text.lower() not in {"none", "null"}:
                items.append((text, int(count or 0)))
    items.sort(key=lambda pair: (-pair[1], pair[0]))
    return [{"value": value, "count": count} for value, count in items[:top_k]]
