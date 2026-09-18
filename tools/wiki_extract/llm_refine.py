"""L0 LLM refine: value triage + similar fields + join authenticity.

Mechanical heuristics still nominate. LLM never writes confirmed or new columns.
Enum labels must be grounded in the column comment. JOIN authenticity never deletes edges.
"""

from __future__ import annotations

import sys
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from tools.wiki_extract.heuristics import (
    seal_l0_reviews,
)
from tools.wiki_extract.join_policy import (
    has_join_semantic,
    may_nominate_join,
    merge_llm_authenticity,
    parse_fq,
    stamp_join_meta,
)
from tools.wiki_extract.overlap import (
    build_join_window,
    overlap_from_window,
    sync_overlap_from_relations,
    window_lefts_for_column,
)
from tools.wiki_extract.dict_triage import apply_llm_triage

ChatFn = Callable[[str, str], dict[str, Any]]

SYSTEM_PROMPT = """你是 ChatBI 库侧 wiki 的 L0 初审员。只有库表注释、列名、低基数样本、列名启发式与值域包含率，没有源码。
硬规则：
- 不得编造中文 label、不得把主张写成 confirmed、不得发明不存在的列名或表名。
- labels 只能从该列注释里已有的「码→中文」抄出；注释没有映射就不要写 labels。
- 字典分流 verdict：dict_keep | dict_hold | drop（兼容 keep/hold/reject）。
  dict_keep = 明确是封闭业务代码字典（仍 proposed）。
  dict_hold = 证据不足，保留字典页等待人工审核。
  drop = 明确不是字典（PII、审计人、时间、裸 id、密钥、自由文本、JSON、租户码、测库污染）。
- 实例清单不是本任务，不要输出 value_index / instance。
- 测库当前只有一个取值：必须区分不全码表（列名/注释像代码集 → keep/hold）与测库污染（地址、乱码、单值垃圾 → drop）。禁止一律 hold，也禁止一律 drop。
- 同业务定位的列（如各表 enable、status）判决应更严谨、大概率同向，但允许因注释/语义不同而不同判。
- similar_fields：同表近义/冗余列，只点已有列。不要报审计字段对、租户字段对。
- joins：对每条候选边同时看 name_evidence 与 overlap（未探测=not_probed）。likely 必须值域契合且列名/注释有关联语义；仅值域契合给 unknown。不得删边、不得标主引用。
- propose_joins：只对 unresolved_join_window 里的列/对端做 accept|skip。码对码（product_code / platform_product_code / *.code）可以是合法 EQUI_JOIN；若同表已有指向同一父表的 id 主键边，码边标 secondary，不要因为「拷贝码」而 skip。禁止自造表列。
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
        "dict_keep": 0,
        "dict_hold": 0,
        "dict_drop": 0,
        "dict_auto_drop": 0,
        "join_likely": 0,
        "join_unlikely": 0,
        "join_unknown": 0,
        "join_llm_added": 0,
    }

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

    apply_llm_triage(model, judgments, chat, stats)
    for compiled in (model.get("tables") or {}).values():
        stamp_join_meta(compiled)
    sync_overlap_from_relations(model, model.get("_overlap"))
    model["_llm_judge"] = {
        "tables": judgments,
        "stats": stats,
        "dict_candidates": [
            {
                "table": c.get("table"),
                "column": c.get("column"),
                "dest": c.get("dest"),
                "dest_source": c.get("dest_source"),
                "llm_dest": c.get("llm_dest"),
                "mechanical_dest": c.get("mechanical_dest"),
                "mechanical_reason": c.get("mechanical_reason"),
            }
            for c in (model.get("dict_candidates") or [])
        ],
        "note": "L0 LLM refine; dict_triage pass1+mechanical+pass2; joins kept proposed",
    }
    model["llm_stats"] = stats
    return seal_l0_reviews(model)


def replay_judgments(model: dict[str, Any], packed: dict[str, Any]) -> dict[str, Any]:
    """Re-apply a saved `_raw/llm_judge.yaml` without calling the LLM."""
    tables_j = packed.get("tables") or {}
    stats = {
        "tables": 0,
        "failed": 0,
        "dict_keep": 0,
        "dict_hold": 0,
        "dict_drop": 0,
        "dict_auto_drop": 0,
        "join_likely": 0,
        "join_unlikely": 0,
        "join_unknown": 0,
        "join_llm_added": 0,
    }
    order = list(model.get("table_order") or (model.get("tables") or {}).keys())
    for tname in order:
        stats["tables"] += 1
        data = tables_j.get(tname)
        if not isinstance(data, dict):
            stats["failed"] += 1
            continue
        apply_table_judgment(model, tname, data, stats)
    apply_llm_triage(model, tables_j, None, stats)
    for compiled in (model.get("tables") or {}).values():
        stamp_join_meta(compiled)
    sync_overlap_from_relations(model, model.get("_overlap"))
    model["_llm_judge"] = {
        "tables": tables_j,
        "stats": packed.get("stats") or stats,
        "note": packed.get("note") or "replayed llm_judge.yaml; keep ≠ confirmed",
    }
    model["llm_stats"] = packed.get("stats") or stats
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
    _apply_similar(compiled, judgment)
    _apply_joins(compiled, judgment, stats)
    _apply_propose_joins(model, tname, compiled, judgment, stats)


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


def _apply_joins(
    compiled: dict[str, Any],
    judgment: dict[str, Any],
    stats: dict[str, int],
) -> None:
    by_right: dict[str, dict[str, Any]] = {}
    for raw in judgment.get("joins") or []:
        if not isinstance(raw, dict):
            continue
        right = str(raw.get("right") or raw.get("column") or "").strip()
        if not right:
            continue
        by_right[right] = raw
        if "." not in right:
            by_right[f"{compiled.get('table')}.{right}"] = raw
    for rel in compiled.get("relations") or []:
        right = str(rel.get("right") or "")
        col = right.split(".", 1)[-1]
        item = by_right.get(right) or by_right.get(col)
        llm_auth = None
        note = ""
        if isinstance(item, dict) and item:
            raw_auth = item.get("authenticity")
            if raw_auth is not None:
                llm_auth = str(raw_auth).lower()
            note = str(item.get("note") or "").strip()
        overlap = rel.get("overlap") or {}
        current = str(rel.get("authenticity") or "unknown")
        auth, extra = merge_llm_authenticity(
            current=current,
            overlap_probed=bool(overlap.get("probed")),
            overlap_auth=str(overlap.get("authenticity") or ""),
            llm_auth=llm_auth,
            semantic=has_join_semantic(rel),
        )
        rel["authenticity"] = auth
        if llm_auth is not None:
            rel["llm_authenticity"] = llm_auth
        merged_note = "; ".join(p for p in (note, extra) if p)
        if merged_note:
            rel["authenticity_note"] = merged_note
        stats[f"join_{auth}"] = stats.get(f"join_{auth}", 0) + 1


def _apply_propose_joins(
    model: dict[str, Any],
    tname: str,
    compiled: dict[str, Any],
    judgment: dict[str, Any],
    stats: dict[str, int],
) -> None:
    window = build_join_window(tname, compiled, model)
    existing = {
        (str(r.get("left") or ""), str(r.get("right") or ""))
        for r in compiled.get("relations") or []
    }
    added = 0
    for raw in judgment.get("propose_joins") or []:
        if not isinstance(raw, dict):
            continue
        verdict = str(raw.get("verdict") or raw.get("decision") or "").lower()
        if verdict not in {"accept", "add"}:
            continue
        left = str(raw.get("left") or "").strip()
        right = str(raw.get("right") or "").strip()
        if right and "." not in right:
            right = f"{tname}.{right}"
        child_col = parse_fq(right)[1]
        allowed = window_lefts_for_column(window, child_col)
        reason = may_nominate_join(model, left, right, window_lefts=allowed)
        if reason:
            continue
        pair = (left, right)
        if pair in existing:
            continue
        ov = overlap_from_window(window, child_col, left)
        compiled.setdefault("relations", []).append(
            {
                "type": "EQUI_JOIN",
                "left": left,
                "right": right,
                "cardinality": "one_to_many",
                "trust": "proposed",
                "authenticity": str(ov.get("authenticity") or "unknown"),
                "source": "llm",
                "name_evidence": {
                    "match": "llm_propose",
                    "stem": child_col,
                    "comment": str(raw.get("note") or "")[:80],
                },
                "overlap": ov,
                "authenticity_note": str(raw.get("note") or "L0 LLM propose_joins"),
                "evidence": f"database_schema:{compiled.get('database')}.{tname}.{child_col}",
            }
        )
        existing.add(pair)
        added += 1
    if added:
        from tools.wiki_extract.heuristics import _exclude_join_rights_from_anchors

        _exclude_join_rights_from_anchors(compiled)
        stamp_join_meta(compiled)
        stats["join_llm_added"] = stats.get("join_llm_added", 0) + added
        ov_stats = model.setdefault("overlap_stats", {})
        ov_stats["llm_added"] = int(ov_stats.get("llm_added") or 0) + added


def _table_payload(
    tname: str, compiled: dict[str, Any], model: dict[str, Any]
) -> dict[str, Any]:
    dicts = [
        {
            "column": cand.get("column"),
            "comment": (cand.get("comment") or "")[:160],
            "values": list((cand.get("values") or {}).keys())[:16],
            "distinct": len(cand.get("values") or {}),
            "looks_like_enum": bool(cand.get("looks_like_enum")),
        }
        for cand in (model.get("dict_candidates") or [])
        if cand.get("table") == tname
    ]
    fields = [
        {
            "name": item.get("name"),
            "data_type": item.get("data_type"),
            "comment": (item.get("description") or "")[:80],
        }
        for item in (compiled.get("fields") or [])
    ]
    joins = [
        {
            "left": rel.get("left"),
            "right": rel.get("right"),
            "name_evidence": rel.get("name_evidence")
            or {"match": "none", "stem": "", "comment": ""},
            "overlap": _overlap_payload(rel.get("overlap")),
            "current_authenticity": rel.get("authenticity") or "unknown",
            "local_comment": (
                next(
                    (
                        str(f.get("description") or "")
                        for f in (compiled.get("fields") or [])
                        if f.get("name")
                        == str(rel.get("right") or "").split(".", 1)[-1]
                    ),
                    "",
                )
            )[:80],
        }
        for rel in compiled.get("relations") or []
    ]
    return {
        "table": tname,
        "comment": compiled.get("description") or tname,
        "primary_key": compiled.get("primary_key") or [],
        "fields": fields,
        "dict_candidates": dicts,
        "join_candidates": joins,
        "unresolved_join_window": build_join_window(tname, compiled, model),
    }


def _overlap_payload(raw: object) -> dict[str, Any]:
    if not isinstance(raw, dict) or not raw:
        return {"probed": False, "status": "not_probed"}
    if raw.get("skipped"):
        return {
            "probed": False,
            "status": str(raw.get("skipped") or "skipped"),
        }
    if not raw.get("probed"):
        return {"probed": False, "status": "not_probed"}
    return {
        "probed": True,
        "ratio": raw.get("ratio"),
        "ratio_reverse": raw.get("ratio_reverse"),
        "deepened": bool(raw.get("deepened")),
        "sample_size": raw.get("sample_size"),
        "miss": raw.get("miss"),
        "authenticity": raw.get("authenticity") or "unknown",
    }


def _user_prompt(payload: dict[str, Any]) -> str:
    import json

    return (
        "对下面这张表做 L0 初审。"
        "dict_candidates 是低基数字典候选池，请给出 dict_keep|dict_hold|drop。"
        "join_candidates 必须全部保留；每条含 name_evidence 与 overlap。"
        "unresolved_join_window 的 overlap 供 propose_joins 参考；码边可 accept。\n"
        + json.dumps(payload, ensure_ascii=False, indent=2)
        + "\n\n输出：\n"
        '{"table":"...","dicts":[{"column":"...","verdict":"dict_keep|dict_hold|drop",'
        '"labels":{"CODE":"注释里的中文"},"reason":"..."}],'
        '"similar_fields":[{"fields":["a","b"],"note":"..."}],'
        '"joins":[{"right":"table.fk","authenticity":"likely|unlikely|unknown","note":"..."}],'
        '"propose_joins":[{"left":"parent.id","right":"table.col","verdict":"accept|skip","note":"..."}]}'
    )
