"""Table-field vocabulary: DB cardinality + comments → topk / labels / dict.

Wiki table rows must declare whether a column is a dictionary and which enum
page it points at. ``dict`` is the recall pin (state machines, canonical
labels); field-level ``labels`` overlay column-specific display text (e.g.
已生成/未生成) and never replace the enum pointer. Drop ``dict`` only when
the bind is wrong (temporal/structured, identifier, or DB values diverge).
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

_GENERIC_FLAG_PAGES = frozenset({"enable", "boolean", "yn"})
_GENERIC_FLAG_VALUES = frozenset(
    {"Y", "N", "y", "n", "1", "0", "是", "否", "yes", "no", "true", "false"}
)
_YES_NO_LABELS = {
    "Y": "是",
    "N": "否",
    "y": "是",
    "n": "否",
    "1": "是",
    "0": "否",
    "是": "是",
    "否": "否",
    "yes": "是",
    "no": "否",
    "true": "是",
    "false": "否",
}
_ID_NAME = re.compile(
    r"(?:^id$|_id$|_ids$|^create_by$|^update_by$|^created_by$|^updated_by$"
    r"|^create_user$|^update_user$|_user_id$)",
    re.I,
)
_SNOWFLAKE = re.compile(r"^\d{15,}$")
_UUID = re.compile(r"^[0-9a-f]{32}$", re.I)
_CODE = re.compile(r"^[\w.@-]+$", re.I)
_CJK_NAME = re.compile(r"^[\u4e00-\u9fff]{2,20}$")
# 「Y 已生成 / N 未生成」「0 否 1 是」「PAID 已缴费 / UNPAID 未缴费」
_LABEL_PAIR = re.compile(
    r"(?:^|[：:\s/|,;；，])"
    r"([A-Za-z0-9_]+|[是否YN])"
    r"[：:\s]+"
    r"([\u4e00-\u9fffA-Za-z][\u4e00-\u9fffA-Za-z0-9_/／-]{0,15})"
)
# 「1,主数据」「1=主数据」「1-主数据」
_LABEL_PUNCT = re.compile(
    r"(?:^|[：:\s/|,;；，])"
    r"([A-Za-z0-9_]+|[是否YN])"
    r"\s*[,=＝\-–]\s*"
    r"([\u4e00-\u9fff][\u4e00-\u9fffA-Za-z0-9_/／-]{0,15})"
)
# 「0记录数据」：数字/YN 后直接跟中文，中间没有分隔符
_LABEL_GLUE = re.compile(
    r"(?:^|[：:\s/|,;；，])"
    r"([0-9]+|[YN])"
    r"([\u4e00-\u9fff][\u4e00-\u9fffA-Za-z0-9_/／-]{0,15})"
)
_VOCAB_NAME = re.compile(
    r"(?:^is_|_flag$|_status$|_state$|_type$|_mode$|_result$|^enable$|"
    r"^status$|^state$|^type$|^deleted$|^valid$|^locked$)",
    re.I,
)


def _acceptable_label_key(key: str) -> bool:
    if key in {"Y", "N", "y", "n", "是", "否"}:
        return True
    if re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,31}", key):
        return True
    return bool(re.fullmatch(r"[0-9]{1,8}", key))


def parse_comment_labels(desc: str) -> dict[str, str]:
    """从字段注释抽出 value→label。无显式配对则空，不脑补。"""
    text = str(desc or "").strip()
    if not text:
        return {}
    out: dict[str, str] = {}
    for pattern in (_LABEL_PAIR, _LABEL_PUNCT, _LABEL_GLUE):
        for key, label in pattern.findall(text):
            label = label.strip().strip("/／")
            if not label or label == key or not _acceptable_label_key(key):
                continue
            out.setdefault(key, label)
    return out


def format_labels(labels: Mapping[str, str], values: list[str] | None = None) -> str:
    keys = list(values) if values else list(labels)
    parts: list[str] = []
    for key in keys:
        label = str(labels.get(key) or "").strip()
        if not label or label == key:
            continue
        safe = label.replace("|", "／").replace(":", "：")
        parts.append(f"{key}:{safe}")
    return "|".join(parts)


def _is_snowflake_or_uuid(text: str) -> bool:
    return bool(_SNOWFLAKE.match(text) or _UUID.match(text))


def is_identifier_column(
    col: str,
    *,
    desc: str = "",
    phys: str = "",
    values: Mapping[str, Any] | None = None,
) -> bool:
    name = str(col or "")
    comment = str(desc or "")
    if _ID_NAME.search(name):
        return True
    if re.search(r"主键|创建人\s*id|更新人\s*id|操作人\s*id", comment, re.I):
        return True
    vals = [str(v) for v in (values or {}) if str(v).strip()]
    if vals and all(_is_snowflake_or_uuid(v) for v in vals):
        return True
    base = phys.split("(")[0].lower()
    if name.endswith("_id") and base in {"bigint", "int", "varchar"}:
        return True
    return False


def _value_is_code(text: str) -> bool:
    if not text or len(text) > 32:
        return False
    if _is_snowflake_or_uuid(text):
        return False
    if _CJK_NAME.match(text) and text not in {"是", "否"} and len(text) >= 4:
        return False
    return bool(_CODE.match(text) or text in {"是", "否"})


def _numeric_measure(values: list[str]) -> bool:
    nums: list[int] = []
    for item in values:
        if not re.fullmatch(r"-?\d+", item):
            return False
        nums.append(int(item))
    if not nums:
        return False
    if set(nums) <= {0, 1, 2}:
        return False
    return max(abs(n) for n in nums) > 2 or len(set(nums)) > 3


def looks_like_vocab(
    *,
    col: str,
    phys: str = "",
    family: str = "",
    distinct: int | None = None,
    values: Mapping[str, Any] | None = None,
) -> bool:
    """窄值域编码列：几个～十几个取值，且像字典而不是姓名/金额/ID。"""
    if family in {"temporal", "structured"}:
        return False
    if is_identifier_column(col, phys=phys, values=values):
        return False
    keys = [str(v) for v in (values or {}) if str(v).strip() != ""]
    n = distinct if distinct is not None else len(keys)
    if n <= 0 or n > 20:
        return False
    if not keys:
        return False
    if _numeric_measure(keys) and family == "number":
        return False
    if set(keys) <= _GENERIC_FLAG_VALUES:
        return True
    if _VOCAB_NAME.search(col) and n <= 20:
        coded = sum(1 for k in keys if _value_is_code(k))
        return coded >= max(1, int(0.7 * len(keys)))
    coded = sum(1 for k in keys if _value_is_code(k))
    return coded == len(keys) and n <= 20


def looks_like_enum_dict(
    *,
    col: str,
    phys: str = "",
    family: str = "",
    distinct: int | None = None,
    values: Mapping[str, Any] | None = None,
    desc: str = "",
) -> bool:
    """该列应建枚举页并写 dict：开关/状态/类型，或注释里已写出 value→label。

    窄值域编码列仍可写 topk（``looks_like_vocab``），但租户号、姓名、备注
    不是字典，不能因此造一页枚举。"""
    if not looks_like_vocab(
        col=col, phys=phys, family=family, distinct=distinct, values=values
    ):
        return False
    name = str(col or "")
    if re.search(
        r"tenant_code|_tenant$|^host$|^content$|_url$|^remark$|^name$|_name$"
        r"|custom_field|user_name|update_user|create_user|contact|^op_",
        name,
        re.I,
    ):
        return False
    keys = [str(v) for v in (values or {}) if str(v).strip() != ""]
    if len(set(keys)) >= 2 and set(keys) <= _GENERIC_FLAG_VALUES:
        return True
    if _VOCAB_NAME.search(name):
        return True
    if parse_comment_labels(desc):
        return True
    return bool(re.search(r"状态|类型|是否|开关|标志|枚举", desc or ""))


def default_flag_labels(values: list[str], desc: str) -> dict[str, str]:
    """是否/开关类列：注释没写清配对时，用是/否填 Y/N、0/1。"""
    keys = [k for k in values if k in _YES_NO_LABELS]
    if not keys or not set(keys) <= _GENERIC_FLAG_VALUES:
        return {}
    hint = desc or ""
    if re.search(r"是否|开关|启用|删除|锁定|生成|有效|软删", hint):
        return {k: _YES_NO_LABELS[k] for k in keys}
    if hint.lower() in {"enable", "yn", "flag", ""}:
        return {k: _YES_NO_LABELS[k] for k in keys}
    if set(keys) <= {"Y", "N", "0", "1"} and len(keys) <= 2:
        return {k: _YES_NO_LABELS[k] for k in keys}
    return {}


def shared_flag_page(keys: list[str], available: set[str]) -> str:
    """Y/N 开关列挂到已有的共享 enable/yn/boolean 页，不另起一页。"""
    if not keys or not set(keys) <= {"Y", "N", "y", "n"}:
        return ""
    for name in ("enable", "yn", "boolean"):
        if name in available and name in _GENERIC_FLAG_PAGES:
            return name
    return ""


def enum_values_compatible(
    *,
    db_values: list[str],
    enum_values: set[str],
    family: str,
) -> bool:
    """本列 DB 值必须大部分落在该枚举页里；类型也对得上。"""
    if family in {"temporal", "structured"}:
        return False
    if not db_values or not enum_values:
        return False
    overlap = {v for v in db_values if v in enum_values}
    return len(overlap) * 2 >= len(set(db_values))


def decide_field_vocab(
    *,
    col: str,
    phys: str,
    family: str,
    desc: str,
    stats: Mapping[str, Any] | None,
    dict_page: str,
    enum_values: set[str] | None,
    fallback_dict: str = "",
) -> dict[str, str]:
    """返回可写入 ground:table 的 topk / labels / dict（空键表示省略）。

    ``dict_page`` 在值集兼容时保留（含共享 enable）。不兼容或没有代码枚举时，
    字典列仍须指向 ``fallback_dict``（调用方按表.列生成的枚举页），不能只留
    topk/labels。"""
    stats = stats or {}
    raw_values = stats.get("values") or {}
    if not isinstance(raw_values, dict):
        raw_values = {}
    distinct = stats.get("distinct")
    try:
        n_distinct = int(distinct) if distinct is not None else len(raw_values)
    except (TypeError, ValueError):
        n_distinct = len(raw_values)
    keys = [str(k) for k in raw_values if str(k).strip() != ""]

    if is_identifier_column(col, desc=desc, phys=phys, values=raw_values):
        return {}

    vocab = looks_like_vocab(
        col=col,
        phys=phys,
        family=family,
        distinct=n_distinct,
        values=raw_values,
    )
    out: dict[str, str] = {}
    labels = parse_comment_labels(desc)
    if vocab:
        topk = "|".join(keys[:20])
        if topk:
            out["topk"] = topk
        if not labels and set(keys) <= _GENERIC_FLAG_VALUES:
            labels = default_flag_labels(keys, desc)
            if not labels and set(keys) <= {"Y", "N", "0", "1"}:
                labels = {k: _YES_NO_LABELS[k] for k in keys if k in _YES_NO_LABELS}
        if labels:
            formatted = format_labels(labels, keys or list(labels))
            if formatted:
                out["labels"] = formatted

    dict_key = str(dict_page or "").strip()
    chosen = ""
    if dict_key:
        keep_dict = True
        if family in {"temporal", "structured"}:
            keep_dict = False
        elif keys and enum_values:
            keep_dict = enum_values_compatible(
                db_values=keys, enum_values=enum_values, family=family
            )
        elif not vocab and keys:
            keep_dict = False
        if keep_dict:
            chosen = dict_key
    if not chosen and vocab:
        chosen = str(fallback_dict or "").strip()
    if chosen:
        out["dict"] = chosen
        if not out.get("labels") and labels:
            formatted = format_labels(labels, keys or list(labels))
            if formatted:
                out["labels"] = formatted
    return out
