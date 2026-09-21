"""Business-column nomination and opaque-value filters for the value index.

Ported from ``tools/wiki_extract/instance_index.py``. Keep the mechanical
skip/nominate/opaque rules identical so extract and wiki tooling agree.
"""

from __future__ import annotations

import re
from typing import Any

INSTANCE_TOP_K = 200

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
_PII_COLUMNS = re.compile(
    r"password|passwd|(^|_)pwd($|_)|secret|token|private_key|id_card|"
    r"legal_certification_no|mobile|phone|email|login_name|salt|密码",
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


def is_pii_column(name: str) -> bool:
    return bool(_PII_COLUMNS.search(name or ""))


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


def looks_like_opaque_instance_values(values: list[dict[str, Any]] | list[str]) -> bool:
    """Skip UUID / snowflake / hex blob / JSON payload columns after sampling."""
    keys: list[str] = []
    for row in values:
        if isinstance(row, dict):
            text = str(row.get("value") or "").strip()
        else:
            text = str(row or "").strip()
        if text:
            keys.append(text)
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
