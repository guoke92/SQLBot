"""Dictionary triage: closed low-card code sets → dicts/ pages.

Independent of instance_index. Verdicts are dict_keep | dict_hold | drop only.

Table-field ``dict:`` is emitted only for ``dict_keep``. ``dict_hold`` stays in
the model for review but does not attach to table fields (avoids sample pollution).
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from typing import Any

from tools.wiki_extract.heuristics import (
    attach_comment_labels,
    dict_page_key,
    parse_comment_fk,
    parse_comment_labels,
)
from tools.wiki_extract.introspect import is_pii_column
from tools.wiki_extract.join_policy import AUDIT_USER_FIELDS, TENANT_FIELDS

ChatFn = Callable[[str, str], dict[str, Any]]

DEST_DICT_KEEP = "dict_keep"
DEST_DICT_HOLD = "dict_hold"
DEST_DROP = "drop"
MAX_DISTINCT = 32

_ENUM_NAME = re.compile(
    r"(^enable$|^enabled$|^disabled$|^status$|_status$|_type$|_flag$|_flg$|_state$)",
    re.I,
)
_UPPER_SNAKE = re.compile(r"^[A-Z][A-Z0-9_]{0,47}$")
_BINARY_NAME = re.compile(
    r"(^enable$|^enabled$|^disabled$|(^|_)is_[a-z0-9_]+$|_flg$|_flag$|_switch$)",
    re.I,
)
_BINARY_COMMENT = re.compile(r"(是否|开关|启用|禁用|布尔|YN\b|Y/N)", re.I)
_ORDINAL_NAME = re.compile(
    r"(^|_)(order|seq|sort|rank|index|node_order|sort_no|seq_no)($|_)",
    re.I,
)
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
_HEX32 = re.compile(r"^[0-9a-fA-F]{32}$")
_BIZ_SAMPLE = re.compile(
    r"^(CT-|DT_|MN-|SP-|wx[0-9a-fA-F]{6,}|app_[A-Za-z]|400\s|\d{3,4}-)",
    re.I,
)
_CJK = re.compile(r"[\u4e00-\u9fff]")
_JSONISH = re.compile(r"^\s*[\[{]")
_DIGIT_ONLY = re.compile(r"^\d{1,4}$")
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
        "fk_ref_column",
        "comment_fk",
        "ordinal",
        "business_id_sample",
        "product_code_concept_not_dict",
    }
)

PASS1_PROMPT = """你是 ChatBI 字典甄别员。只判断「这一列是不是封闭业务代码集」。
硬规则：
- 不得编造列名。verdict 只能是 dict_keep | dict_hold | drop。
- dict_keep = 明确是封闭业务代码字典（enable/status/type/flag 等，取值像代码；或列注释已列出码→中文）。
- dict_hold = 证据不足，保留字典页等待人工（不会写进表字段 dict:）。
- drop = 明确不是字典（PII、审计人、时间、裸 id、密钥、自由文本、JSON、租户码、业务单号/协议号样本、UUID/ref 外键、顺序号、注释里 table#column 指向的关联列）。
- 测库当前只有一个取值：必须结合列名与注释区分两种情况。
  不全码表（列名/注释像代码集，测库样本不全）→ dict_keep 或 dict_hold。
  测库污染（地址、乱码、单值垃圾、测试数据、业务主键样本）→ drop。
  禁止因为「只有一个取值」就一律 hold，也禁止一律 drop。
- 不要判断实例清单；公司名、信用代码、渠道实例、审批单号、协议号不是本任务。
- 同业务定位的列判决应更严谨、大概率同向，但允许因注释不同而不同判。
只输出 JSON：{"dicts":[{"column":"...","verdict":"dict_keep|dict_hold|drop","reason":"..."}]}"""

PASS2_PROMPT = """你是 ChatBI 字典复核员。机械检查与初判不一致，或测库仅单值，请在 dict_keep|dict_hold|drop 内终裁。
只看字典语义。单值可能是不全码表，也可能是测库污染，必须结合列名与注释区分，不要一律 hold 或一律 drop。
只输出 JSON：{"column":"...","verdict":"dict_keep|dict_hold|drop","reason":"..."}"""

BINARY_FILL_PROMPT = """你是 ChatBI 二值字典补全员。
场景：列名/注释像开关、是否、enable 等二值语义，测库 profile 只出现对立码的一侧（仅 Y 或仅 N，或仅 0 或仅 1）。
任务：判断是否应补全封闭对的另一侧。
硬规则：
- 仅当列明确是二值开关语义时 supplement=true。
- 只允许补全对立码：已有 Y→补 N；已有 N→补 Y；已有 0→补 1；已有 1→补 0。禁止发明其它码。
- 不是开关语义、或取值不是 Y/N/0/1 单侧 → supplement=false，add 为 null。
- 不得编造列名。
只输出 JSON：{"column":"...","supplement":true|false,"add":"Y"|"N"|"0"|"1"|null,"reason":"..."}"""


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
            "looks_like_ordinals": looks_like_ordinals(col, values),
            "looks_like_biz_sample": looks_like_biz_sample(values),
            "looks_like_binary_switch": looks_like_binary_switch(col, comment),
            "comment_labels": parse_comment_labels(comment, None),
            "comment_fk": parse_comment_fk(comment),
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
    return all(
        _SNOWFLAKE.match(k) or _UUID.match(k) or _HEX32.match(k) or _LONG_ID.match(k)
        for k in keys
    )


def looks_like_ordinals(col: str, values: dict[str, Any]) -> bool:
    keys = [str(k) for k in values]
    if not keys:
        return False
    if _ORDINAL_NAME.search(col) and all(_DIGIT_ONLY.match(k) for k in keys):
        return True
    if len(keys) >= 2 and all(_DIGIT_ONLY.match(k) for k in keys):
        nums = sorted(int(k) for k in keys)
        return nums == list(range(nums[0], nums[0] + len(nums)))
    return False


def looks_like_biz_sample(values: dict[str, Any]) -> bool:
    keys = [str(k) for k in values]
    if not keys:
        return False
    hits = sum(1 for k in keys if _BIZ_SAMPLE.match(k) or _HEX32.match(k))
    return hits >= max(1, int(0.6 * len(keys)))


def looks_like_closed_code_enum(values: dict[str, Any]) -> bool:
    """UPPER_SNAKE symbolic codes (node_code / flow_code / status enums).

    Rejects short alphabet tokens like ``A``/``B`` so unnamed codeish stays hold.
    """
    keys = [str(k) for k in values]
    if not keys:
        return False
    upper = [k for k in keys if _UPPER_SNAKE.match(k)]
    if len(upper) < max(1, int(0.8 * len(keys))):
        return False
    substantial = sum(1 for k in upper if "_" in k or len(k) >= 3)
    return substantial >= max(1, int(0.8 * len(upper)))


def looks_like_binary_switch(col: str, comment: str) -> bool:
    if _BINARY_NAME.search(str(col or "")):
        return True
    return bool(_BINARY_COMMENT.search(str(comment or "")))


def incomplete_binary_pair(values: dict[str, Any]) -> tuple[str, str] | None:
    """If profile has only one side of Y/N or 0/1, return (present, missing)."""
    keys = {str(k).strip() for k in values if str(k).strip()}
    pairs = (("Y", "N"), ("N", "Y"), ("0", "1"), ("1", "0"))
    for present, missing in pairs:
        if keys == {present}:
            return present, missing
    # case-fold Y/N only
    folded = {k.upper() for k in keys}
    if folded == {"Y"} and keys != {"Y"}:
        return next(iter(keys)), "N"
    if folded == {"N"} and keys != {"N"}:
        return next(iter(keys)), "Y"
    return None


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
    if col.lower().startswith("ref_"):
        return DEST_DROP, "fk_ref_column"
    if cand.get("comment_fk") or parse_comment_fk(comment):
        return DEST_DROP, "comment_fk"
    if _SECRET.search(col) or _SECRET.search(comment) or is_pii_column(col):
        return DEST_DROP, "secret_or_pii"
    if col.lower() in TENANT_FIELDS or col.lower().endswith("_tenant_code"):
        return DEST_DROP, "tenant"
    if looks_like_json_values(values):
        return DEST_DROP, "json_payload"
    if cand.get("looks_like_ids") or looks_like_ids(values):
        return DEST_DROP, "snowflake_or_long_id"
    if cand.get("looks_like_ordinals") or looks_like_ordinals(col, values):
        return DEST_DROP, "ordinal"
    if cand.get("looks_like_biz_sample") or looks_like_biz_sample(values):
        return DEST_DROP, "business_id_sample"
    # Product business codes: only the master catalog table is a dict page.
    # Satellite copies belong to same_semantic concepts / EQUI_JOIN, not per-table dicts.
    tname = str(cand.get("table") or "")
    if col in {"product_code", "platform_product_code"} and not (
        tname == "platform_product" and col == "product_code"
    ):
        return DEST_DROP, "product_code_concept_not_dict"
    binary = cand.get("looks_like_binary_switch")
    if binary is None:
        binary = looks_like_binary_switch(col, comment)
    if binary and incomplete_binary_pair(values):
        return DEST_DICT_KEEP, "binary_switch_incomplete"
    if binary and set(str(k).strip().upper() for k in values) <= {"Y", "N", "0", "1"}:
        return DEST_DICT_KEEP, "binary_switch"
    if _ENUM_NAME.search(col) and cand.get("looks_like_enum"):
        return DEST_DICT_KEEP, "named_code_set"
    if cand.get("looks_like_enum") and looks_like_closed_code_enum(values):
        return DEST_DICT_KEEP, "closed_code_enum"
    if "字典" in comment and cand.get("looks_like_enum"):
        return DEST_DICT_KEEP, "comment_dict_hint"
    if cand.get("looks_like_enum"):
        return DEST_DICT_HOLD, "codeish_values"
    if values:
        return DEST_DROP, "not_a_code_set"
    return DEST_DROP, "empty"


def apply_mechanical_only(model: dict[str, Any]) -> dict[str, Any]:
    """--skip-llm path: mechanical dest only (no AI binary fill)."""
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

    if chat is not None:
        _fill_binary_pairs_via_ai(model, chat, stats)

    _materialize(model)
    _count_dest(model, stats)
    return model


def _fill_binary_pairs_via_ai(
    model: dict[str, Any],
    chat: ChatFn,
    stats: dict[str, int],
) -> None:
    """AI decides whether to add the missing Y/N or 0/1 for switch-like columns."""
    for cand in model.get("dict_candidates") or []:
        if str(cand.get("dest") or "") != DEST_DICT_KEEP:
            continue
        col = str(cand.get("column") or "")
        comment = str(cand.get("comment") or "")
        values = cand.get("values") or {}
        pair = incomplete_binary_pair(values)
        if not pair:
            continue
        if not (
            cand.get("looks_like_binary_switch")
            or looks_like_binary_switch(col, comment)
        ):
            continue
        present, missing = pair
        payload = {
            "table": cand.get("table"),
            "column": col,
            "comment": comment,
            "observed": list(values.keys()),
            "suggested_add": missing,
            "pair": [present, missing],
        }
        try:
            data = chat(
                BINARY_FILL_PROMPT,
                json.dumps(payload, ensure_ascii=False),
            )
        except Exception:
            continue
        if not isinstance(data, dict):
            continue
        if not bool(data.get("supplement")):
            cand["binary_fill"] = {
                "supplement": False,
                "reason": str(data.get("reason") or ""),
            }
            continue
        add = str(data.get("add") or "").strip()
        if add not in {missing, missing.upper(), missing.lower()}:
            # Only accept the expected opposite code.
            if add.upper() == missing.upper() and missing.upper() in {"Y", "N"}:
                add = missing if missing in {"Y", "N"} else add.upper()
            else:
                continue
        if add not in {"Y", "N", "0", "1"}:
            continue
        if add in values:
            continue
        values[add] = 0
        cand["values"] = values
        cand["distinct"] = len(values)
        cand["binary_fill"] = {
            "supplement": True,
            "add": add,
            "reason": str(data.get("reason") or ""),
        }
        stats["dict_binary_fill"] = stats.get("dict_binary_fill", 0) + 1


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
        # hold: keep review artifact pages; keep: attach to table fields for emit.
        page_worthy = dest in {DEST_DICT_KEEP, DEST_DICT_HOLD}
        field_attach = dest == DEST_DICT_KEEP
        if page_worthy:
            key = dict_page_key(tname, col)
            item = _candidate_to_dict(cand, key, dest)
            dicts[key] = item
            if field_attach:
                by_table.setdefault(tname, {})[col] = key
        for field in compiled.get("fields") or []:
            if field.get("name") != col:
                continue
            if field_attach:
                field["dictionary"] = dict_page_key(tname, col)
            else:
                field.pop("dictionary", None)
    model["dicts"] = dicts
    model["_dict_by_table"] = by_table


def _candidate_to_dict(cand: dict[str, Any], key: str, dest: str) -> dict[str, Any]:
    tname = str(cand.get("table") or "")
    col = str(cand.get("column") or "")
    values = {str(k): {"trust": "proposed"} for k in (cand.get("values") or {})}
    if cand.get("binary_fill", {}).get("supplement"):
        add = str(cand["binary_fill"].get("add") or "")
        if add and add in values:
            values[add] = {
                "trust": "proposed",
                "source": "ai_binary_fill",
                "evidence": str(cand["binary_fill"].get("reason") or "binary_pair"),
            }
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
        "binary_fill": cand.get("binary_fill"),
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
