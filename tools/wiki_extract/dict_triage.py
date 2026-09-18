"""Dictionary triage: closed low-card code sets → dicts/ pages.

Independent of instance_index. Verdicts are dict_keep | dict_hold | drop only.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

from tools.wiki_extract.heuristics import (
    attach_comment_labels,
    dict_page_key,
    parse_comment_labels,
)
from tools.wiki_extract.introspect import is_pii_column
from tools.wiki_extract.join_policy import AUDIT_USER_FIELDS, TENANT_FIELDS

ChatFn = Callable[[str, str], dict[str, Any]]

DEST_DICT_KEEP = "dict_keep"
DEST_DICT_HOLD = "dict_hold"
DEST_DROP = "drop"
MAX_DISTINCT = 32

_ENUM_NAME = re.compile(r"(^enable$|^status$|_status$|_type$|_flag$|_state$)")
_TIME_NAME = re.compile(
    r"(^create_time$|^update_time$|^req_time$|_time$|_date$|_at$|_dt$)",
    re.I,
)
_SECRET = re.compile(
    r"(password|passwd|(^|_)pwd($|_)|secret|token|api_key|private_key|密码)",
    re.I,
)
_CODEISH = re.compile(r"^[A-Za-z0-9_.+-]{1,32}$")
_LONG_ID = re.compile(r"^[0-9]{15,}$")
_SNOWFLAKE = re.compile(r"^[0-9]{16,20}$")
_UUID = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)
_CJK = re.compile(r"[\u4e00-\u9fff]")
_JSONISH = re.compile(r"^\s*[\[{]")
_TEMPORAL_TYPES = frozenset({"date", "datetime", "timestamp", "time", "year"})
_HARD_DROP = frozenset(
    {
        "audit_user",
        "temporal",
        "surrogate_id",
        "secret_or_pii",
        "snowflake_or_long_id",
        "tenant",
        "json_payload",
    }
)

PASS1_PROMPT = """你是 ChatBI 字典甄别员。只判断「这一列是不是封闭业务代码集」。
硬规则：
- 不得编造列名。verdict 只能是 dict_keep | dict_hold | drop。
- dict_keep = 明确是封闭业务代码字典（enable/status/type/flag 等，取值像代码；或列注释已列出码→中文）。
- dict_hold = 证据不足，保留字典页等待人工。
- drop = 明确不是字典（PII、审计人、时间、裸 id、密钥、自由文本、JSON 数组、租户码、联系人、地址）。
- 测库当前只有一个取值：必须结合列名与注释区分两种情况。
  不全码表（列名/注释像代码集，测库样本不全）→ dict_keep 或 dict_hold。
  测库污染（地址、乱码、单值垃圾、测试数据）→ drop。
  禁止因为「只有一个取值」就一律 hold，也禁止一律 drop。
- 不要判断实例清单；公司名、信用代码、渠道实例不是本任务。
- 同业务定位的列判决应更严谨、大概率同向，但允许因注释不同而不同判。
只输出 JSON：{"dicts":[{"column":"...","verdict":"dict_keep|dict_hold|drop","reason":"..."}]}"""

PASS2_PROMPT = """你是 ChatBI 字典复核员。机械检查与初判不一致，或测库仅单值，请在 dict_keep|dict_hold|drop 内终裁。
只看字典语义。单值可能是不全码表，也可能是测库污染，必须结合列名与注释区分，不要一律 hold 或一律 drop。
只输出 JSON：{"column":"...","verdict":"dict_keep|dict_hold|drop","reason":"..."}"""


def collect_candidates(
    compiled: dict[str, Any],
    column_stats: dict[str, Any],
    *,
    max_enum_distinct: int = MAX_DISTINCT,
) -> list[dict[str, Any]]:
    tname = str(compiled.get("table") or "")
    pk = {str(c) for c in (compiled.get("primary_key") or [])}
    out: list[dict[str, Any]] = []
    for field in compiled.get("fields") or []:
        col = str(field.get("name") or "")
        if not col or col in pk:
            continue
        stats = column_stats.get(col) or {}
        values = {
            str(k): int(v)
            for k, v in (stats.get("values") or {}).items()
            if str(k).strip() and str(k).strip().lower() not in {"none", "null"}
        }
        distinct = int(stats.get("distinct") or len(values) or 0)
        if not values or distinct <= 0 or distinct > max_enum_distinct:
            continue
        comment = str(field.get("description") or "")
        mysql_type = str(field.get("data_type") or "")
        cand = {
            "table": tname,
            "column": col,
            "comment": comment,
            "mysql_type": mysql_type,
            "distinct": distinct,
            "values": values,
            "looks_like_enum": looks_like_enum(values),
            "looks_like_ids": looks_like_ids(values),
            "comment_labels": parse_comment_labels(comment, None),
        }
        out.append(cand)
    return out


def looks_like_enum(values: dict[str, Any]) -> bool:
    keys = [str(k) for k in values]
    if not keys:
        return False
    if any(_CJK.search(k) and len(k) > 16 for k in keys):
        return False
    codeish = sum(1 for k in keys if _CODEISH.match(k) and not _LONG_ID.match(k))
    return codeish >= max(1, int(0.8 * len(keys)))


def looks_like_json_values(values: dict[str, Any]) -> bool:
    keys = [str(k).strip() for k in values]
    if not keys:
        return False
    hits = sum(1 for k in keys if _JSONISH.match(k))
    return hits >= max(1, int(0.5 * len(keys)))


def looks_like_ids(values: dict[str, Any]) -> bool:
    keys = [str(k) for k in values]
    if not keys:
        return False
    return all(_SNOWFLAKE.match(k) or _UUID.match(k) or _LONG_ID.match(k) for k in keys)


def mechanical_suggestion(cand: dict[str, Any]) -> tuple[str, str]:
    col = str(cand.get("column") or "")
    comment = str(cand.get("comment") or "")
    mysql_type = str(cand.get("mysql_type") or "")
    values = cand.get("values") or {}
    if col.lower() in AUDIT_USER_FIELDS:
        return DEST_DROP, "audit_user"
    if _TIME_NAME.search(col) or mysql_type.split("(", 1)[0].lower() in _TEMPORAL_TYPES:
        return DEST_DROP, "temporal"
    if col.lower() == "id":
        return DEST_DROP, "surrogate_id"
    if _SECRET.search(col) or _SECRET.search(comment) or is_pii_column(col):
        return DEST_DROP, "secret_or_pii"
    if col.lower() in TENANT_FIELDS or col.lower().endswith("_tenant_code"):
        return DEST_DROP, "tenant"
    if looks_like_json_values(values):
        return DEST_DROP, "json_payload"
    if cand.get("looks_like_ids"):
        return DEST_DROP, "snowflake_or_long_id"
    if _ENUM_NAME.search(col) and cand.get("looks_like_enum"):
        return DEST_DICT_KEEP, "named_code_set"
    if cand.get("looks_like_enum"):
        return DEST_DICT_HOLD, "codeish_values"
    if values:
        return DEST_DROP, "not_a_code_set"
    return DEST_DROP, "empty"


def apply_mechanical_only(model: dict[str, Any]) -> dict[str, Any]:
    """--skip-llm path: mechanical dest if any, else dict_hold."""
    for cand in model.get("dict_candidates") or []:
        dest, reason = mechanical_suggestion(cand)
        cand["mechanical_dest"] = dest
        cand["mechanical_reason"] = reason
        cand["dest"] = dest
        cand["dest_source"] = "mechanical"
        cand["llm_dest"] = None
    _materialize(model)
    return model


def apply_llm_triage(
    model: dict[str, Any],
    judgments: dict[str, Any],
    chat: ChatFn | None,
    stats: dict[str, int],
) -> dict[str, Any]:
    by_col = {
        (c["table"], c["column"]): c for c in (model.get("dict_candidates") or [])
    }
    for tname, judgment in (judgments or {}).items():
        if not isinstance(judgment, dict):
            continue
        items = judgment.get("dicts") or []
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            col = str(item.get("column") or "")
            cand = by_col.get((tname, col))
            if cand is None:
                continue
            dest = _normalize_dest(item.get("verdict") or item.get("dest"))
            if dest is None:
                continue
            cand["llm_dest"] = dest
            cand["llm_reason"] = str(item.get("reason") or "")
            extra = item.get("labels") if isinstance(item.get("labels"), dict) else {}
            cand["llm_labels"] = {str(k): str(v).strip() for k, v in extra.items() if v}

    for cand in model.get("dict_candidates") or []:
        mech, reason = mechanical_suggestion(cand)
        cand["mechanical_dest"] = mech
        cand["mechanical_reason"] = reason
        llm_dest = cand.get("llm_dest")
        distinct = int(cand.get("distinct") or len(cand.get("values") or {}) or 0)
        hard = reason in _HARD_DROP and mech == DEST_DROP
        if hard:
            cand["dest"] = DEST_DROP
            cand["dest_source"] = "mechanical"
            continue
        if llm_dest is None:
            cand["dest"] = mech
            cand["dest_source"] = "mechanical"
            continue
        need_pass2 = llm_dest != mech or distinct <= 1
        if not need_pass2:
            cand["dest"] = llm_dest
            cand["dest_source"] = "agree"
            continue
        if chat is None:
            if distinct <= 1:
                cand["dest"] = llm_dest
                cand["dest_source"] = "llm_single"
            else:
                cand["dest"] = mech
                cand["dest_source"] = "mechanical_override"
            continue
        final = _pass2(chat, cand, llm_dest, mech)
        cand["dest"] = final
        cand["dest_source"] = "pass2"
        cand["pass2_dest"] = final
    _materialize(model)
    _count_dest(model, stats)
    return model


def _normalize_dest(raw: object) -> str | None:
    text = str(raw or "").strip().lower()
    if text in {"dict_keep", "keep"}:
        return DEST_DICT_KEEP
    if text in {"dict_hold", "hold"}:
        return DEST_DICT_HOLD
    if text in {"drop", "reject"}:
        return DEST_DROP
    return None


def _pass2(chat: ChatFn, cand: dict[str, Any], llm_dest: str, mech: str) -> str:
    payload = {
        "table": cand.get("table"),
        "column": cand.get("column"),
        "comment": cand.get("comment"),
        "values": list((cand.get("values") or {}).keys())[:16],
        "distinct": cand.get("distinct"),
        "llm_dest": llm_dest,
        "mechanical_dest": mech,
        "mechanical_reason": cand.get("mechanical_reason"),
    }
    import json

    try:
        data = chat(
            PASS2_PROMPT,
            json.dumps(payload, ensure_ascii=False),
        )
    except Exception:
        return mech
    dest = _normalize_dest((data or {}).get("verdict") or (data or {}).get("dest"))
    return dest or mech


def _materialize(model: dict[str, Any]) -> None:
    dicts: dict[str, Any] = {}
    by_table: dict[str, dict[str, Any]] = {}
    for cand in model.get("dict_candidates") or []:
        dest = str(cand.get("dest") or DEST_DROP)
        tname = str(cand.get("table") or "")
        col = str(cand.get("column") or "")
        compiled = (model.get("tables") or {}).get(tname) or {}
        kept = dest in {DEST_DICT_KEEP, DEST_DICT_HOLD}
        if kept:
            key = dict_page_key(tname, col)
            item = _candidate_to_dict(cand, key, dest)
            dicts[key] = item
            by_table.setdefault(tname, {})[col] = key
        for field in compiled.get("fields") or []:
            if field.get("name") != col:
                continue
            if kept:
                field["dictionary"] = dict_page_key(tname, col)
            else:
                field.pop("dictionary", None)
    model["dicts"] = dicts
    model["_dict_by_table"] = by_table


def _candidate_to_dict(cand: dict[str, Any], key: str, dest: str) -> dict[str, Any]:
    tname = str(cand.get("table") or "")
    col = str(cand.get("column") or "")
    values = {str(k): {"trust": "proposed"} for k in (cand.get("values") or {})}
    attach_comment_labels(
        values,
        str(cand.get("comment") or ""),
        cand.get("llm_labels") if dest == DEST_DICT_KEEP else None,
        evidence=f"database_schema:{tname}.{col}",
    )
    return {
        "dict": key,
        "table": tname,
        "column": col,
        "fields": [f"{tname}.{col}"],
        "values": values,
        "triage": "keep" if dest == DEST_DICT_KEEP else "hold",
        "needs_review": dest == DEST_DICT_HOLD,
        "label_conflict": bool(
            (cand.get("comment_labels") or {})
            and not set((cand.get("comment_labels") or {})).intersection(
                set(cand.get("values") or {})
            )
        ),
        "source": f"database_profile:{tname}.{col}",
        "dest_source": cand.get("dest_source"),
    }


def _count_dest(model: dict[str, Any], stats: dict[str, int]) -> None:
    for cand in model.get("dict_candidates") or []:
        dest = str(cand.get("dest") or "")
        source = str(cand.get("dest_source") or "")
        if dest == DEST_DICT_KEEP:
            stats["dict_keep"] = stats.get("dict_keep", 0) + 1
        elif dest == DEST_DICT_HOLD:
            stats["dict_hold"] = stats.get("dict_hold", 0) + 1
        elif dest == DEST_DROP:
            if source == "mechanical" and cand.get("llm_dest") is None:
                stats["dict_auto_drop"] = stats.get("dict_auto_drop", 0) + 1
            else:
                stats["dict_drop"] = stats.get("dict_drop", 0) + 1
