"""Deterministic soft signals derived from field profiles and table stats."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any


_TEMPORAL_NAME = re.compile(
    r"(^|_)(dt|date|time|ts|timestamp|ymd|biz_date|event_time|created|updated|deleted)(_|$)",
    re.I,
)
_ID_NAME = re.compile(r"(^|_)(id|pk|key|code|no|num)(_|$)", re.I)
_MEASURE_NAME = re.compile(
    r"(^|_)(amt|amount|qty|quantity|cnt|count|sum|total|price|fee|score|rate|ratio)(_|$)",
    re.I,
)
_TEMPORAL_TYPE = re.compile(r"date|time|timestamp|datetime", re.I)
_NUMERIC_TYPE = re.compile(
    r"int|decimal|numeric|float|double|real|number|money|bigint|smallint",
    re.I,
)


def key_likelihood(
    *,
    distinct_ratio: float | None,
    null_rate: float | None,
) -> str:
    try:
        ndv = float(distinct_ratio) if distinct_ratio is not None else None
    except (TypeError, ValueError):
        ndv = None
    try:
        nulls = float(null_rate) if null_rate is not None else None
    except (TypeError, ValueError):
        nulls = None
    if ndv is None:
        return "unknown"
    nulls = 0.0 if nulls is None else nulls
    if ndv >= 0.95 and nulls <= 0.01:
        return "high"
    if ndv >= 0.80 and nulls <= 0.05:
        return "medium"
    return "low"


def _parse_datetimeish(value: str | None) -> bool:
    if not value:
        return False
    text = str(value).strip()
    if not text:
        return False
    for fmt in (
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d",
        "%Y%m%d",
        "%Y-%m-%dT%H:%M:%S",
    ):
        try:
            datetime.strptime(text[:19], fmt)
            return True
        except ValueError:
            continue
    return False


def temporal_role(
    *,
    field_name: str,
    field_type: str | None,
    min_value: str | None,
    max_value: str | None,
) -> str | None:
    name = field_name or ""
    ftype = field_type or ""
    type_hit = bool(_TEMPORAL_TYPE.search(ftype))
    name_hit = bool(_TEMPORAL_NAME.search(name))
    range_hit = _parse_datetimeish(min_value) or _parse_datetimeish(max_value)
    if not (type_hit or name_hit or range_hit):
        return None
    lower = name.lower()
    if "biz" in lower or "partition" in lower or lower.endswith("_date"):
        return "biz_date"
    if "event" in lower or "occur" in lower:
        return "event_time"
    if "create" in lower:
        return "created_at"
    if "update" in lower:
        return "updated_at"
    if type_hit or range_hit:
        return "datetime"
    return "datetime"


def domain_role(
    *,
    field_name: str,
    field_type: str | None,
    distinct_ratio: float | None,
    approx_distinct: int | None,
    key_like: str,
) -> str:
    name = field_name or ""
    ftype = field_type or ""
    if temporal_role(
        field_name=name,
        field_type=ftype,
        min_value=None,
        max_value=None,
    ) or _TEMPORAL_TYPE.search(ftype):
        return "datetime"
    if key_like == "high" or _ID_NAME.search(name):
        return "id"
    try:
        ndv = float(distinct_ratio) if distinct_ratio is not None else None
    except (TypeError, ValueError):
        ndv = None
    try:
        ad = int(approx_distinct) if approx_distinct is not None else None
    except (TypeError, ValueError):
        ad = None
    if ndv is not None and ndv <= 0.05 and ad is not None and ad <= 50:
        return "enum"
    if _MEASURE_NAME.search(name) and _NUMERIC_TYPE.search(ftype):
        return "measure"
    if _NUMERIC_TYPE.search(ftype):
        return "measure" if _MEASURE_NAME.search(name) else "text"
    return "text"


def derive_field_soft_signals(
    *,
    field_name: str,
    field_type: str | None,
    null_rate: float | None = None,
    distinct_ratio: float | None = None,
    approx_distinct: int | None = None,
    min_value: str | None = None,
    max_value: str | None = None,
) -> dict[str, Any]:
    kl = key_likelihood(distinct_ratio=distinct_ratio, null_rate=null_rate)
    tr = temporal_role(
        field_name=field_name,
        field_type=field_type,
        min_value=min_value,
        max_value=max_value,
    )
    dr = domain_role(
        field_name=field_name,
        field_type=field_type,
        distinct_ratio=distinct_ratio,
        approx_distinct=approx_distinct,
        key_like=kl,
    )
    out: dict[str, Any] = {
        "key_likelihood": kl,
        "domain_role": dr,
    }
    if tr:
        out["temporal_role"] = tr
    return out


def infer_table_role(
    *,
    approx_rows: int | None,
    field_count: int,
    high_key_fields: int,
    outbound_candidate_edges: int = 0,
    inbound_candidate_edges: int = 0,
) -> dict[str, Any]:
    try:
        rows = int(approx_rows) if approx_rows is not None else 0
    except (TypeError, ValueError):
        rows = 0
    reasons: list[str] = []
    role = "unknown"
    if field_count >= 2 and high_key_fields >= 2 and rows > 0 and rows < 100_000:
        if outbound_candidate_edges >= 2 and inbound_candidate_edges == 0:
            role = "bridge"
            reasons.append("multiple key-like columns and outbound edges")
    if role == "unknown" and rows >= 50_000 and outbound_candidate_edges >= 1:
        role = "fact"
        reasons.append("large table with outbound join candidates")
    if role == "unknown" and high_key_fields >= 1 and rows < 50_000:
        role = "dim"
        reasons.append("smaller table with key-like column")
    if role == "unknown" and rows >= 50_000:
        role = "fact"
        reasons.append("large row count")
    return {"table_role": role, "reasons": reasons}


def inclusion_score(
    *,
    containment_source_in_target: float,
    containment_target_in_source: float,
    source_key_likelihood: str,
    target_key_likelihood: str,
) -> dict[str, Any]:
    """Score unary IND-like evidence and suggest FK→PK direction."""

    def _w(level: str) -> float:
        return {"high": 1.0, "medium": 0.7, "low": 0.35, "unknown": 0.5}.get(
            level, 0.5
        )

    st = float(containment_source_in_target or 0.0)
    ts = float(containment_target_in_source or 0.0)
    # Prefer direction where values are contained in the key-like side.
    score_fk_to_pk = st * _w(target_key_likelihood)
    score_pk_to_fk = ts * _w(source_key_likelihood)
    if score_fk_to_pk >= score_pk_to_fk:
        direction = "source_fk_to_target_pk"
        score = score_fk_to_pk
        target_key = target_key_likelihood
    else:
        direction = "target_fk_to_source_pk"
        score = score_pk_to_fk
        target_key = source_key_likelihood
    suggest = (
        score >= 0.55
        and target_key in {"high", "medium"}
        and max(st, ts) >= 0.6
    )
    return {
        "inclusion_score": round(score, 4),
        "suggested_direction": direction,
        "target_key_likelihood": target_key,
        "suggest_candidate": suggest,
    }
