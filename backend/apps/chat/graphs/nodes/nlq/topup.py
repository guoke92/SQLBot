"""Evidence-driven working-set top-up family (resolver/fulfiller orchestration)."""

from __future__ import annotations

from typing import Any, NamedTuple

from apps.chat.graphs.nodes.nlq.state import (
    NlqState,
    _access_scope,
    _ds_databases,
    _ds_scope,
    _llm_service,  # noqa: F401
    _sql_dialect,
)
from apps.chat.planning_context import (
    capture_planning_context,
)
from apps.chat.steps.observability import log_span  # noqa: F401
from apps.chat.steps.recall_topup import (
    TopupManifest,
    TopupSignals,
    apply_knowledge_topup,
    fulfill_recall_topup,
    record_topup_event,
    resolve_recall_topup,
    signals_from_evidence,
    topup_enabled_for,
    value_evidence_block,
)
from apps.chat.task.llm import LLMService
from apps.conversation.models import QueryRun
from apps.conversation.run_service import (
    active_evidence,
)
from apps.conversation.session import session_scope
from apps.protocol.sql.identifier_validation import collect_sql_identifier_usage

# ── Constants ────────────────────────────────────────────────────────────────
from common.utils.utils import SQLBotLogUtil


class _TopupRun(NamedTuple):
    changed: bool
    manifest: TopupManifest
    notice: dict[str, Any]
    # topup 内部对 physical_gate_hits 等 wiki_context 的更新经此回传调用方
    wiki_context: dict[str, Any]


def _run_topup(
    state: NlqState,
    llm_service: LLMService,
    *,
    signals: TopupSignals,
    source: str,
    graph_node: str,
    audit: bool = True,
    persist: bool = True,
    extra_event: dict[str, Any] | None = None,
) -> _TopupRun:
    """Single top-up orchestration shared by every trigger source.

    resolve → knowledge recompile (+1 unit) → fulfill → telemetry → snapshot
    write-back. The write-back is not optional plumbing: plan_query restores
    ``QueryRun.planning_context`` on every entry, so a changed working set
    that is not persisted would be silently discarded by the next node.
    ``persist=False`` is only for the pre-capture question pass, whose caller
    captures the same snapshot immediately afterwards.
    """
    with session_scope() as session:
        oid, _ds_id = _ds_scope(llm_service)
        manifest = resolve_recall_topup(
            session,
            llm_service,
            signals,
            oid=int(oid or 1),
            access_scope=_access_scope(state),
        )
        wiki_result = _wiki_physical_recall_safely(
            signals.missing_concepts, ds_id=_ds_id, databases=_ds_databases(llm_service)
        )
        wiki_text = wiki_result.text if wiki_result is not None else ""
        wiki_context = state.setdefault("wiki_context", {})
        wiki_gate_history = list(wiki_context.get("physical_gate_hits") or [])
        if wiki_text:
            wiki_gate_history.append(
                {
                    "source": source,
                    "missing_concepts": list(signals.missing_concepts),
                    "physical_text_chars": len(wiki_text),
                    "manifest_has_additions": manifest.has_additions,
                }
            )
            wiki_context["physical_gate_hits"] = wiki_gate_history
            state = {**state, "wiki_context": wiki_context}
            # physical 段锚点闭包：门禁缺口页引用的表并入渲染清单
            # （base_tables=None → 渲染器只重渲闭包表会丢工作集表，
            # 故这里用当前 db_schema 已含的表不可知，交给调用方时机——
            # bounce 后 plan_query 恢复快照时 retrieve_schema 会再渲工作集；
            # 此处仅记遥测，避免渲染半份 schema。）
            wiki_context.setdefault("physical_gate_pages", []).extend(
                wiki_result.page_keys
            )
            _record_wiki_recall_telemetry(state, wiki_result, source=source)
        if not manifest.has_additions:
            if wiki_text:
                notice = {
                    "source": source,
                    "added_tables": [],
                    "value_hits": [],
                    "knowledge_units": [],
                    "wiki_passages": wiki_text,
                }
                record_topup_event(
                    session, str(state["run_id"]), {**notice, **(extra_event or {})}
                )
                return _TopupRun(
                    True, manifest, notice, dict(state.get("wiki_context") or {})
                )
            return _TopupRun(False, manifest, {}, dict(state.get("wiki_context") or {}))
        knowledge_changed = apply_knowledge_topup(
            session, llm_service, manifest, oid=int(oid or 1)
        )
        result = fulfill_recall_topup(
            session,
            llm_service,
            manifest,
            access_scope=_access_scope(state),
            graph_node=graph_node,
            audit=audit,
        )
        if result.changed and _wiki_backend_for(_ds_id):
            # topup 刷新 db_schema 后,wiki 后端必须用表页重渲,
            # planner 与执行期指纹才可比;扩窗表的关联表随 enrich 关系段
            # 一并由渲染器带出（闭包在 retrieve_context 的召回路径统一做）。
            _wiki_render_schema_text(state, llm_service, list(result.resources))
            evidence_block = value_evidence_block(list(manifest.value_hits))
            if evidence_block and evidence_block not in (
                llm_service.chat_question.db_schema or ""
            ):
                llm_service.chat_question.db_schema = (
                    str(llm_service.chat_question.db_schema or "") + evidence_block
                )
        if not (result.changed or knowledge_changed):
            return _TopupRun(False, manifest, {}, dict(state.get("wiki_context") or {}))
        notice: dict[str, Any] = {
            "source": source,
            "added_tables": list(result.added_tables),
            "value_hits": [dict(item) for item in manifest.value_hits],
            "knowledge_units": [dict(item) for item in manifest.knowledge_units],
        }
        record_topup_event(
            session, str(state["run_id"]), {**notice, **(extra_event or {})}
        )
        if persist:
            fresh = capture_planning_context(
                llm_service,
                entity_bindings=dict(state.get("entity_bindings") or {}),
                temporal_parse=dict(state.get("temporal_parse") or {}),
                wiki_context=dict(state.get("wiki_context") or {}),
            )
            nlq_run = session.get(QueryRun, str(state["run_id"]))
            if nlq_run is not None:
                nlq_run.planning_context = fresh.model_dump(mode="json")
                session.add(nlq_run)
                session.commit()
    return _TopupRun(True, manifest, notice, dict(state.get("wiki_context") or {}))


def _topup_after_clarify(state: NlqState, llm_service: LLMService) -> NlqState:
    """Evidence-driven working-set top-up on clarify resume (deterministic).

    Clarification answers are the strongest recall signal: option targets name
    tables structurally and custom text carries business values. The restored
    snapshot keeps the expensive deterministic fetches; this pass only unions
    evidence-driven additions in and persists a fresh snapshot via
    ``_run_topup``. State carries the restored ``entity_bindings`` /
    ``temporal_parse``, so the unified write-back captures the same values.
    """
    if not topup_enabled_for(getattr(llm_service.ds, "id", None)):
        return state
    with session_scope() as session:
        evidence = active_evidence(session, str(state["run_id"]))
    signals = signals_from_evidence(list(evidence))
    if not signals.evidence_tables and not signals.evidence_texts:
        return state
    run = _run_topup(
        state,
        llm_service,
        signals=signals,
        source="clarify_resume",
        graph_node="retrieve_context",
    )
    # 未变更路径也要回传：_run_topup 可能已追加 physical_gate_hits
    # （manifest 无表可扩但 wiki physical 命中 → changed=False 的分支）
    if not run.changed:
        return {**state, "wiki_context": run.wiki_context}
    return {
        **state,
        "wiki_context": run.wiki_context,
        "recall_topup_notice": run.notice,
    }


def _topup_on_question(
    state: NlqState, llm_service: LLMService
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    """First-pass value-index top-up on the question text (deterministic).

    Runs after the standard recall steps and before the planning-context
    snapshot is captured, so additions land in the same snapshot
    (``persist=False``) with no separate write-back. ``audit=False``: this
    graph node already emitted its CHOOSE_TABLE span for this execution.

    返回 ``(notice, wiki_context)``：notice 供遥测展示，wiki_context 含
    topup 期间追加的 physical_gate_hits——调用方显式合入 state，不依赖
    ``_run_topup`` 对传入 dict 的原地突变。"""
    if not topup_enabled_for(getattr(llm_service.ds, "id", None)):
        return None, dict(state.get("wiki_context") or {})
    question = str(llm_service.retrieval_question or "").strip()
    if not question:
        return None, dict(state.get("wiki_context") or {})
    run = _run_topup(
        state,
        llm_service,
        signals=TopupSignals(question_text=question),
        source="question",
        graph_node="retrieve_context",
        audit=False,
        persist=False,
    )
    return (run.notice if run.changed else None), run.wiki_context


class _GateExpansion(NamedTuple):
    """Hard-gate adjudication facts for the fatal policy in plan_query_node.

    ``uncovered`` are SQL-referenced tables still outside the working set after
    evidence-driven expansion — an ACCESS_POLICY_VIOLATION over them is a real
    permission breach. ``undetermined`` marks a violation whose references
    cannot be parsed (non-SQL plan / unparsable SQL); those stay fatal.
    ``expanded`` says the working set grew, which invalidates the recorded
    gate errors and obliges the caller to re-validate the decision.
    """

    uncovered: frozenset[str]
    undetermined: bool
    expanded: bool


def _topup_on_failed_gates(
    state: NlqState, llm_service: LLMService, plans: list[dict[str, Any]]
) -> _GateExpansion:
    """Expand rejected-SQL table references into the working set and adjudicate.

    A hard-gate rejection for an out-of-working-set table is usually a recall
    gap, not a model defect: the table exists in the catalog and inside the
    user's AccessScope (it is map-visible), so the deterministic resolver
    pulls it in and the repair loop gets a complete schema window. Tables the
    resolver cannot admit — hallucinated or genuinely out of scope — are
    returned as ``uncovered`` so the caller keeps the fatal policy for real
    violations.
    """
    dialect = _sql_dialect(llm_service)
    working = {str(name) for name in (llm_service.table_name_list or [])}
    outside: set[str] = set()
    undetermined = False
    for plan in plans:
        if plan.get("hard_gate_status") != "failed":
            continue
        sql = str(plan.get("sql") or "")
        if not sql:
            if plan.get("hard_gate_code") == "ACCESS_POLICY_VIOLATION":
                undetermined = True
            continue
        try:
            usage = collect_sql_identifier_usage(sql, dialect)
        except Exception:  # noqa: BLE001
            undetermined = True
            continue
        outside.update(name for name in usage.physical_tables if name not in working)
    if not topup_enabled_for(getattr(llm_service.ds, "id", None)):
        # Legacy policy: no evidence expansion, every outside table stays fatal.
        return _GateExpansion(frozenset(outside), undetermined, expanded=False)
    if outside:
        gate_topup = _run_topup(
            state,
            llm_service,
            signals=TopupSignals(unauthorized_tables=tuple(sorted(outside))),
            source="failed_gates",
            graph_node="plan_query",
            extra_event={"referenced": sorted(outside)},
        )
        if gate_topup.changed:
            state = {**state, "wiki_context": gate_topup.wiki_context}
    remaining = {
        name for name in outside if name not in set(llm_service.table_name_list or [])
    }
    return _GateExpansion(
        frozenset(remaining),
        undetermined,
        expanded=bool(outside - remaining),
    )


def _wiki_backend_for(ds_id: Any) -> bool:
    """wiki 后端判定（复用 wiki_recall 单一实现；判定失败保守 False）。"""
    try:
        from apps.chat.steps.wiki_recall import wiki_backend_active

        return wiki_backend_active(int(ds_id) if ds_id is not None else None)
    except Exception:  # noqa: BLE001
        return False


def _wiki_business_text_safely(
    question: str, *, ds_id: Any, databases: list[str] | None = None
) -> str:
    try:
        from apps.chat.steps.wiki_recall import wiki_business_text

        return (
            wiki_business_text(question, ds_id=ds_id, databases=databases) or ""
        )
    except Exception:  # noqa: BLE001 — wiki 层零影响
        return ""


def _wiki_business_recall_safely(
    question: str, *, ds_id: Any, databases: list[str] | None = None
) -> Any:
    """business 召回（WikiRecallResult：text/hits/page_keys/观测）。

    失败返回 None——与"召回成功但零命中"（空 hits）区分，调用方遥测
    不混淆。"""
    try:
        from apps.chat.steps.wiki_recall import wiki_business_recall

        return wiki_business_recall(question, ds_id=ds_id, databases=databases)
    except Exception:  # noqa: BLE001 — wiki 层零影响
        return None


def _wiki_physical_text(
    missing_concepts: tuple[str, ...],
    *,
    ds_id: Any,
    databases: list[str] | None = None,
) -> str:
    """plan_gate missing_concepts 的 physical 模式检索（小窗口、无图扩展）。"""
    result = _wiki_physical_recall_safely(
        missing_concepts, ds_id=ds_id, databases=databases
    )
    if result is None:
        return ""
    return result.text


def _wiki_physical_recall_safely(
    missing_concepts: tuple[str, ...],
    *,
    ds_id: Any,
    databases: list[str] | None = None,
) -> Any:
    """physical 召回（WikiRecallResult）；失败/未命中返回 None。"""
    if not missing_concepts:
        return None
    try:
        from apps.chat.steps.wiki_recall import wiki_physical_recall

        return wiki_physical_recall(
            " ".join(missing_concepts), ds_id=ds_id, databases=databases
        )
    except Exception:  # noqa: BLE001
        return None


def _record_wiki_recall_telemetry(
    state: dict[str, Any], result: Any, *, source: str
) -> None:
    """WikiRecallResult → wiki_context 遥测（wiki_hits/耗时/嵌入构建）。

    执行详情读 planning_context.wiki_context（单一持久化通道）；
    retrieval span 的输入也来自这里——一次采集、多处消费。"""
    if result is None:
        return
    try:
        hits = list(result.hits or [])
        wiki_context = state.setdefault("wiki_context", {})
        wiki_context["wiki_hits"] = hits
        wiki_context["wiki_recall_source"] = source
        wiki_context["wiki_recall_elapsed_ms"] = int(result.elapsed_ms or 0)
        wiki_context["store_source"] = getattr(result, "store_source", "") or ""
        wiki_context["corpus_id"] = int(getattr(result, "corpus_id", 0) or 0)
        wiki_context["corpus_generation"] = int(getattr(result, "generation", 0) or 0)
        wiki_context["vector_chunks"] = int(getattr(result, "vector_chunks", 0) or 0)
        wiki_context["vector_channel"] = bool(getattr(result, "vector_channel", False))
        wiki_context["wiki_trace"] = dict(result.trace or {})
        if result.embedding_built:
            wiki_context["wiki_embedding_built"] = True
    except Exception:  # noqa: BLE001 — 遥测失败零影响
        pass


def _live_tables_projection(llm_service: Any) -> dict[str, Any]:
    """core_table/core_field 同步产物 → 渲染器活元数据兜底源（chat 172）。

    wiki 接缝对所有 ds 开启，但语料只覆盖部分数据源；其它 ds 的表在
    db-catalog（语料根旁文件）里不命中，只渲表头零字段。这里把当前
    数据源已同步的表/列转成渲染器的第二兜底源——零额外连库，一次投影。"""
    try:
        from apps.datasource.crud.datasource import get_table_obj_by_ds
        from common.core.db import Session, engine
        from common.core.security import create_access_token  # noqa: F401

        ds = getattr(llm_service, "ds", None)
        user = getattr(llm_service, "current_user", None)
        if ds is None or user is None or getattr(ds, "id", None) is None:
            return {}
        with Session(engine) as session:
            table_objs = get_table_obj_by_ds(session=session, current_user=user, ds=ds)
        projection: dict[str, Any] = {}
        for obj in table_objs or []:
            table = getattr(obj, "table", None)
            name = getattr(table, "table_name", None)
            if not name:
                continue
            fields = [
                (
                    str(getattr(f, "field_name", "") or ""),
                    str(getattr(f, "field_type", "") or "string"),
                    str(
                        getattr(f, "custom_comment", None)
                        or getattr(f, "field_comment", "")
                        or ""
                    ),
                )
                for f in (getattr(obj, "fields", None) or [])
            ]
            projection[str(name)] = {
                "comment": getattr(table, "table_comment", None) or "",
                "fields": fields,
            }
        return projection
    except Exception as exc:  # noqa: BLE001 — 活元数据兜底失败零影响
        SQLBotLogUtil.warning("live tables projection degraded: %s", exc)
        return {}


def _wiki_render_schema_text(
    state: dict[str, Any], llm_service: Any, tables: list[str]
) -> None:
    """用 wiki table 页重写 chat_question.db_schema 并记录缺页遥测。"""
    try:
        from apps.chat.steps.wiki_recall import _store
        from apps.knowledge.recall_kernel.render import render_schema

        ds_id = getattr(getattr(llm_service, "ds", None), "id", None)
        store = _store(ds_id)
        if store is None:
            return
        rendered = render_schema(
            tables, store=store, live_tables=_live_tables_projection(llm_service)
        )
        wiki_context = state.setdefault("wiki_context", {})
        wiki_context["schema_source"] = "wiki" if rendered else wiki_context.get("schema_source")
        wiki_context["schema_page_missing"] = False
        if rendered:
            llm_service.chat_question.db_schema = rendered
    except Exception as exc:  # noqa: BLE001 — 渲染失败保持原 schema
        SQLBotLogUtil.warning("wiki schema render degraded: %s", exc)


def _apply_anchor_closure(
    state: dict[str, Any],
    llm_service: Any,
    page_keys: list[str],
    *,
    base_tables: list[str] | None = None,
) -> None:
    """锚点闭包（召回后补渲）：召回页引用的表并入 schema 渲染清单。

    图扩展负责"发现"，闭包负责"落地"——被召回语义页 anchors/field_targets/
    maps_to 引用的表必须已在 planner 的 schema_text 中。纯确定性补渲
    （进程内、零 LLM），失败只表现为无闭包，绝不影响主链路。
    遥测：wiki_context 记 anchor_closure_tables / anchor_closure_truncated /
    anchor_closure_missing（缺表页，增量提取信号）。"""
    if not page_keys:
        return
    try:
        from apps.chat.steps.wiki_recall import _store
        from apps.knowledge.recall_kernel.tables import resolve_wiki_tables
        from apps.knowledge.recall_kernel.types import RecallBudget
        from apps.knowledge.wiki.anchors import anchor_tables_missing

        store = _store(getattr(getattr(llm_service, "ds", None), "id", None))
        if store is None:
            return
        budget = RecallBudget.from_settings()
        candidates, truncated = resolve_wiki_tables(
            store, page_keys=page_keys, budget=budget
        )
        closure = [item.name for item in candidates]
        missing = anchor_tables_missing(store, page_keys)
        wiki_context = state.setdefault("wiki_context", {})
        wiki_context["anchor_closure_tables"] = closure
        if truncated:
            wiki_context["anchor_closure_truncated"] = truncated
        if missing:
            wiki_context["anchor_closure_missing"] = missing
        if not closure:
            return
        merged = list(dict.fromkeys([*(base_tables or []), *closure]))
        if len(merged) > len(base_tables or []):
            _wiki_render_schema_text(state, llm_service, merged)
            # 闭包表必须同步进 working set：硬门禁的 allowed 集合来自
            # table_name_list（_accept_plan → protocol.validate_plan），
            # 只落 schema 文本会造成"prompt 可见、门禁不可用"的割裂。
            existing = {str(n) for n in (llm_service.table_name_list or [])}
            added = [t for t in closure if t not in existing]
            if added:
                llm_service.table_name_list = [
                    *(llm_service.table_name_list or []),
                    *added,
                ]
    except Exception as exc:  # noqa: BLE001 — wiki 层零影响约定
        SQLBotLogUtil.warning("wiki anchor closure degraded: %s", exc)
