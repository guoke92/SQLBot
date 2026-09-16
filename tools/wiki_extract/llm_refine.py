"""L0 LLM refine: enum keep/drop + semantic clusters + similar fields.

Mechanical heuristics still nominate. LLM never writes confirmed / labels / new columns.
Evidence stays database_schema (allowed prefix); rationale goes to REVIEW notes.
"""

from __future__ import annotations

import re
import sys
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from tools.wiki_extract.heuristics import (
    COMMON_COLUMNS,
    TENANT_FIELDS,
    seal_l0_reviews,
)
from tools.wiki_extract.introspect import is_pii_column

ChatFn = Callable[[str, str], dict[str, Any]]

_AUTO_INSTANCE_COLUMNS = frozenset(
    {
        "create_user",
        "update_user",
        "create_by",
        "update_by",
        *TENANT_FIELDS,
    }
)
_KEY_OK = re.compile(r"^[a-z][a-z0-9_]{0,47}$")

SYSTEM_PROMPT = """你是 ChatBI 库侧 wiki 的 L0 初审员。只有库表注释、列名、低基数样本，没有源码。
硬规则：
- 不得编造中文 label、不得把主张写成 confirmed、不得发明不存在的列名。
- 枚举页只留给「封闭业务代码集」（状态/类型/开关/渠道码）。实例名、人名、租户号、密码、主键/雪花、自由文本、配置碎片不是枚举。
- verdict 只能是 keep | instance | reject。
  keep = 明确是代码枚举（仍是 proposed）。
  instance = 低基数但像实例/名单，改入 value_index。
  reject = 不该出现在枚举也不该进 value_index（PII、噪声、空值）。
- 拿不准不要 keep。
- clusters：按业务语义分组，不要只按前缀。必须有且仅有一个 include=always 的 common（审计/id/enable/时间戳/有则 code）。
- similar_fields：同表近义/冗余列（名称拷贝对、重复编码），只点已有列。
只输出一个 JSON 对象，不要 markdown。"""


def refine_model(
    model: dict[str, Any],
    chat: ChatFn,
    *,
    workers: int = 4,
) -> dict[str, Any]:
    tables = list(model.get("table_order") or (model.get("tables") or {}).keys())
    judgments: dict[str, Any] = {}
    stats = {
        "tables": 0,
        "failed": 0,
        "enum_keep": 0,
        "enum_instance": 0,
        "enum_reject": 0,
        "enum_auto_reject": 0,
    }
    auto = _auto_triage_enums(model)
    stats["enum_auto_reject"] = auto["reject"]
    stats["enum_instance"] = auto["instance"]

    def one(tname: str) -> tuple[str, dict[str, Any] | None]:
        compiled = (model.get("tables") or {}).get(tname) or {}
        try:
            payload = _table_payload(tname, compiled, model)
            data = chat(SYSTEM_PROMPT, _user_prompt(payload))
            data["table"] = tname
            return tname, data
        except Exception as exc:  # noqa: BLE001 — keep mechanical result
            print(f"llm refine skip {tname}: {exc}", file=sys.stderr)
            return tname, None

    if tables:
        futs = []
        with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
            futs = [pool.submit(one, name) for name in tables]
            fetched = [fut.result() for fut in as_completed(futs)]
        for tname, data in fetched:
            stats["tables"] += 1
            if data is None:
                stats["failed"] += 1
                continue
            judgments[tname] = data
            apply_table_judgment(model, tname, data, stats)

    model["_llm_judge"] = {
        "tables": judgments,
        "stats": stats,
        "note": "L0 LLM refine; keep ≠ confirmed; no code_path",
    }
    model["llm_stats"] = stats
    return seal_l0_reviews(model)


def apply_table_judgment(
    model: dict[str, Any],
    tname: str,
    judgment: dict[str, Any],
    stats: dict[str, int],
) -> None:
    compiled = (model.get("tables") or {}).get(tname)
    if not compiled:
        return
    _apply_enums(model, tname, judgment, stats)
    _apply_clusters(compiled, judgment)
    _apply_similar(compiled, judgment)


def _auto_triage_enums(model: dict[str, Any]) -> dict[str, int]:
    counts = {"reject": 0, "instance": 0}
    enums = model.get("enums") or {}
    value_index: list[dict[str, Any]] = list(model.get("value_index") or [])
    drop: list[str] = []
    for key, enum in enums.items():
        col = str(enum.get("column") or "")
        if _should_auto_reject(col):
            drop.append(key)
            _clear_dictionary(model, str(enum.get("table") or ""), col)
            counts["reject"] += 1
            continue
        if _should_auto_instance(col):
            drop.append(key)
            _clear_dictionary(model, str(enum.get("table") or ""), col)
            counts["instance"] += 1
            value_index.append(_enum_to_index(enum))
    for key in drop:
        enums.pop(key, None)
    model["value_index"] = value_index
    return counts


def _enum_to_index(enum: dict[str, Any]) -> dict[str, Any]:
    counts = enum.get("counts") or {}
    values = enum.get("values") or {}
    return {
        "table": enum.get("table"),
        "column": enum.get("column"),
        "values": [{"value": str(k), "count": int(counts.get(k) or 0)} for k in values],
    }


def _should_auto_reject(column: str) -> bool:
    if is_pii_column(column):
        return True
    lowered = column.lower()
    return any(
        token in lowered
        for token in ("password", "passwd", "pwd", "secret", "token", "private_key")
    )


def _should_auto_instance(column: str) -> bool:
    if column in _AUTO_INSTANCE_COLUMNS:
        return True
    return column.endswith(("_tenant_code", "_tenant_id"))


def _apply_enums(
    model: dict[str, Any],
    tname: str,
    judgment: dict[str, Any],
    stats: dict[str, int],
) -> None:
    by_col = {
        str(item.get("column") or ""): item
        for item in (judgment.get("enums") or [])
        if isinstance(item, dict)
    }
    enums = model.setdefault("enums", {})
    value_index: list[dict[str, Any]] = list(model.get("value_index") or [])
    drop_keys: list[str] = []
    for key, enum in list(enums.items()):
        if str(enum.get("table") or "") != tname:
            continue
        col = str(enum.get("column") or "")
        verdict = str((by_col.get(col) or {}).get("verdict") or "instance").lower()
        if verdict == "keep":
            stats["enum_keep"] = stats.get("enum_keep", 0) + 1
            continue
        drop_keys.append(key)
        _clear_dictionary(model, tname, col)
        if verdict == "reject":
            stats["enum_reject"] = stats.get("enum_reject", 0) + 1
            continue
        stats["enum_instance"] = stats.get("enum_instance", 0) + 1
        value_index.append(_enum_to_index(enum))
    for key in drop_keys:
        enums.pop(key, None)
    model["value_index"] = value_index


def _apply_clusters(compiled: dict[str, Any], judgment: dict[str, Any]) -> None:
    names = set(compiled.get("column_names") or [])
    database = str(compiled.get("database") or "")
    tname = str(compiled.get("table") or "")
    incoming = judgment.get("clusters")
    if not isinstance(incoming, list) or not incoming:
        return
    assigned: dict[str, str] = {}
    clusters: list[dict[str, Any]] = []
    seen_keys: set[str] = set()
    common_members = [c for c in COMMON_COLUMNS if c in names]
    if "code" in names and "code" not in common_members:
        common_members.append("code")

    for raw in incoming:
        if not isinstance(raw, dict):
            continue
        key = _cluster_key(str(raw.get("key") or raw.get("title") or ""))
        if not key or key in seen_keys:
            continue
        members = [
            str(c)
            for c in (raw.get("fields") or raw.get("members") or [])
            if str(c) in names
        ]
        include = raw.get("include")
        if key == "common" or include == "always":
            key = "common"
            for col in common_members:
                if col not in members:
                    members.append(col)
            clusters.append(
                {
                    "key": "common",
                    "title": str(raw.get("title") or "通用"),
                    "include": "always",
                }
            )
            seen_keys.add("common")
            for col in members:
                assigned.setdefault(col, "common")
            continue
        if len(members) < 2:
            continue
        seen_keys.add(key)
        clusters.append(
            {
                "key": key,
                "title": str(raw.get("title") or key),
                "trust": "proposed",
                "source": "llm",
                "evidence": f"database_schema:{database}.{tname}",
            }
        )
        for col in members:
            assigned.setdefault(col, key)

    if "common" not in seen_keys:
        clusters.insert(0, {"key": "common", "title": "通用", "include": "always"})
        for col in common_members:
            assigned.setdefault(col, "common")
    else:
        # keep common first
        clusters.sort(key=lambda item: 0 if item.get("key") == "common" else 1)

    compiled["clusters"] = clusters
    for field in compiled.get("fields") or []:
        name = str(field.get("name") or "")
        if name in assigned:
            field["cluster"] = assigned[name]
        else:
            field.pop("cluster", None)


def _apply_similar(compiled: dict[str, Any], judgment: dict[str, Any]) -> None:
    names = set(compiled.get("column_names") or [])
    groups: list[dict[str, Any]] = []
    for raw in judgment.get("similar_fields") or []:
        if not isinstance(raw, dict):
            continue
        fields = [str(c) for c in (raw.get("fields") or []) if str(c) in names]
        if len(fields) < 2:
            continue
        groups.append(
            {
                "fields": fields,
                "note": str(raw.get("note") or "L0 LLM: similar/redundant columns"),
            }
        )
    compiled["similar_fields"] = groups


def _clear_dictionary(model: dict[str, Any], tname: str, column: str) -> None:
    compiled = (model.get("tables") or {}).get(tname) or {}
    for field in compiled.get("fields") or []:
        if field.get("name") == column:
            field.pop("dictionary", None)


def _cluster_key(raw: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "_", raw.strip().lower()).strip("_")
    if text == "always":
        return "common"
    if _KEY_OK.match(text):
        return text
    return ""


def _table_payload(
    tname: str, compiled: dict[str, Any], model: dict[str, Any]
) -> dict[str, Any]:
    enums = [
        {
            "column": enum.get("column"),
            "values": list((enum.get("values") or {}).keys())[:16],
            "distinct": len(enum.get("values") or {}),
        }
        for enum in (model.get("enums") or {}).values()
        if enum.get("table") == tname
    ]
    prefix = [
        item.get("key")
        for item in (compiled.get("clusters") or [])
        if item.get("key") != "common"
    ]
    fields = [
        {
            "name": item.get("name"),
            "data_type": item.get("data_type"),
            "comment": (item.get("description") or "")[:80],
            "cluster": item.get("cluster"),
        }
        for item in (compiled.get("fields") or [])
    ]
    return {
        "table": tname,
        "comment": compiled.get("description") or tname,
        "primary_key": compiled.get("primary_key") or [],
        "fields": fields,
        "prefix_clusters": prefix,
        "enum_candidates": enums,
    }


def _user_prompt(payload: dict[str, Any]) -> str:
    import json

    return (
        "对下面这张表做 L0 初审。prefix_clusters 只是机械前缀，可推翻。"
        "enum_candidates 已去掉租户/审计人/PII。\n"
        + json.dumps(payload, ensure_ascii=False, indent=2)
        + "\n\n输出：\n"
        '{"table":"...","enums":[{"column":"...","verdict":"keep|instance|reject","reason":"..."}],'
        '"clusters":[{"key":"common","title":"通用","include":"always","fields":["id","enable"]},'
        '{"key":"identity","title":"主档身份","fields":["name","code"]}],'
        '"similar_fields":[{"fields":["a","b"],"note":"..."}]}'
    )
