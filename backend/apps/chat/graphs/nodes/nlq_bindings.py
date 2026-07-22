"""Query binding probes for NLQ (boundary ids, time-column preference).

Single-purpose node: write structured ``query_bindings`` only.
Prompt text is owned solely by ``apps.chat.plan_context`` at generate time.
Observability: only open a ChatLog span when a real probe runs and succeeds.
"""

from __future__ import annotations

import datetime
import traceback
from typing import Any, Dict, List, Optional, Tuple

import orjson
from sqlalchemy import and_
from sqlmodel import Session, select

from apps.chat.models.chat_model import OperationEnum
from apps.chat.plan_policy import BOUNDARY_PROBE_ENABLED, BOUNDARY_PROBE_MIN_ROWS
from apps.chat.steps.observability import log_span
from apps.conversation.sink import StreamSink
from apps.datasource.crud.catalog_stats import load_table_stats_for_ds
from apps.datasource.models.datasource import CoreField, CoreTable
from apps.protocol import QueryPlan
from common.core.db import engine as sqlbot_engine
from common.utils.utils import SQLBotLogUtil


def prepare_query_bindings_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """Optional MIN(pk) probe for large tables with year/time intent.

    Writes structured ``query_bindings`` only — prompt text is assembled later
    via ``plan_context.render_plan_context``. No ChatLog when probe is skipped.
    """
    if not BOUNDARY_PROBE_ENABLED:
        return state
    llm_service = state.get("llm_service")
    if not llm_service or not getattr(llm_service, "ds", None):
        return state

    question = llm_service.chat_question.question or ""
    tables: List[str] = list(getattr(llm_service, "table_name_list", None) or [])
    if not tables:
        return state

    time_cues = (
        "今年",
        "本年",
        "本月",
        "近一年",
        "2024",
        "2025",
        "2026",
        "actual_end",
        "月份",
        "每月",
    )
    if not any(k in question for k in time_cues):
        return state

    ds_id = getattr(llm_service.ds, "id", None)
    if not ds_id:
        return state

    completion_cue = any(
        k in question for k in ("完成", "实际", "交付", "上线", "结束", "关闭")
    )
    create_cue = any(k in question for k in ("创建", "提出", "提交", "新建"))

    try:
        result = _run_boundary_probe(
            llm_service,
            tables=tables,
            ds_id=int(ds_id),
            question=question,
            completion_cue=completion_cue,
            create_cue=create_cue,
        )
    except Exception:
        traceback.print_exc()
        return state

    if not result:
        return state

    binds, public_binds = result
    record_id = getattr(getattr(llm_service, "record", None), "id", None) or state.get(
        "record_id"
    )
    with log_span(
        operate=OperationEnum.PREPARE_BINDINGS,
        record_id=record_id,
        local_operation=True,
        graph_node="prepare_query_bindings",
        initial_payload=dict(public_binds),
    ) as span:
        span["payload"] = dict(public_binds)
        if binds.get("_notes"):
            span["payload"]["_notes"] = binds.get("_notes")
        sink = StreamSink.from_state(state)
        try:
            sink.event(
                {
                    "type": "query-bindings",
                    "content": orjson.dumps(public_binds).decode(),
                }
            )
        except Exception:
            pass
        return {
            **state,
            "query_bindings": binds,
            "record": llm_service.record,
        }


def _run_boundary_probe(
    llm_service: Any,
    *,
    tables: List[str],
    ds_id: int,
    question: str,
    completion_cue: bool,
    create_cue: bool,
) -> Optional[Tuple[Dict[str, Any], Dict[str, Any]]]:
    """Return (full_binds, public_binds) or None when probe not applicable."""
    with Session(sqlbot_engine) as session:
        stats = load_table_stats_for_ds(session, int(ds_id), tables)
        large = [
            n
            for n in tables
            if int((stats.get(n) or {}).get("approx_rows") or 0) >= BOUNDARY_PROBE_MIN_ROWS
        ]
        if not large:
            return None
        target = large[0]
        trow = session.exec(
            select(CoreTable).where(
                and_(CoreTable.ds_id == ds_id, CoreTable.table_name == target)
            )
        ).first()
        if not trow:
            return None
        fields = session.exec(select(CoreField).where(CoreField.table_id == trow.id)).all()
        names = [f.field_name for f in fields if f.field_name]
        lower_map = {n.lower(): n for n in names}

        pk = lower_map.get("id")
        if not pk:
            for key in ("task_id", "story_id", "case_id"):
                if key in lower_map:
                    pk = lower_map[key]
                    break

        completion_first = (
            "actually_end_time",
            "actual_end_time",
            "end_time",
            "finish_time",
            "close_time",
            "create_time",
            "update_time",
        )
        create_first = (
            "create_time",
            "created_at",
            "actually_end_time",
            "actual_end_time",
            "update_time",
        )
        default_order = (
            "actually_end_time",
            "actual_end_time",
            "create_time",
            "update_time",
        )
        if create_cue and not completion_cue:
            cand_order = create_first
            time_pref_note = "问题偏「创建/提出」：优先 create_time 类列。"
        elif completion_cue:
            cand_order = completion_first
            time_pref_note = "问题偏「完成/实际/交付」：优先 actual/end 类时间列。"
        else:
            cand_order = default_order
            time_pref_note = "未写清创建/完成时：完成/实际结束时间优先于 create_time。"

        time_col = None
        for cand in cand_order:
            if cand in lower_map:
                time_col = lower_map[cand]
                break
        if not pk or not time_col:
            return None

        year = datetime.datetime.now().year
        for y in range(year, year - 6, -1):
            if str(y) in question:
                year = y
                break
        start = f"{year}-01-01"
        del_clause = ""
        if "deleted" in lower_map:
            del_clause = " AND `deleted` = '0'"
        probe_sql = (
            f"SELECT MIN(`{pk}`) AS v FROM `{target}` "
            f"WHERE `{time_col}` >= '{start}'{del_clause} LIMIT 1"
        )
        plan = QueryPlan(
            success=True,
            statement=probe_sql,
            payload={"sql": probe_sql},
            resources=[target],
        )
        try:
            qr = llm_service.protocol.execute(llm_service.ds, plan)
        except Exception as exc:
            SQLBotLogUtil.warning("boundary probe failed: %s" % exc)
            return None
        val = None
        for r in qr.data or []:
            if isinstance(r, dict):
                val = r.get("v")
                if val is None and r:
                    val = next(iter(r.values()), None)
                break
        if val is None:
            return None

        rows_hint = (stats.get(target) or {}).get("approx_rows")
        notes = [
            f"- 表 `{target}` 约 {rows_hint} 行；`{time_col}` >= {start} 时主键 `{pk}` 下界 ≈ {val}。",
            f"- 主查询建议同时：`{pk}` >= {val} AND `{time_col}` >= '{start}' "
            "（主键缩范围 + 时间条件保正确）。",
            f"- {time_pref_note}",
        ]
        binds: Dict[str, Any] = {}
        binds[f"{target}.{pk}_ge"] = val
        binds[f"{target}.{time_col}_ge"] = start
        binds["_notes"] = notes
        binds["_preferred_time_col"] = f"{target}.{time_col}"
        public_binds = {k: v for k, v in binds.items() if not str(k).startswith("_")}
        return binds, public_binds
