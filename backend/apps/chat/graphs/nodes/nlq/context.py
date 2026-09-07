"""Bootstrap/context nodes: record prep, datasource, access scope, recall, schema, wiki seam, turn-context assembly."""

from __future__ import annotations

import re
from typing import Any

from sqlalchemy import select
from sqlbot_xpack.custom_prompt.models.custom_prompt_model import CustomPromptTypeEnum

from apps.chat.binding_resolver import (
    binding_resource_names,
    resolve_entity_bindings,
    retain_binding_resources,
)
from apps.chat.context_bundle import choose_data_strategy, context_fingerprint
from apps.chat.graphs.nodes.nlq.analysis import (
    _dataset_capabilities,
)

# ── Constants ────────────────────────────────────────────────────────────────
from apps.chat.graphs.nodes.nlq.state import (
    _MAX_BATCH_SIZE,
    _MAX_STEPS,
    NlqState,
    _access_scope,
    _ds_databases,
    _ds_scope,
    _fail,
    _llm_service,
)

# monkeypatch-surface imports: tests setattr these names on submodules
from apps.chat.graphs.nodes.nlq.topup import (
    _apply_anchor_closure,  # noqa: F401
    _record_wiki_recall_telemetry,  # noqa: F401
    _run_topup,  # noqa: F401
    _topup_after_clarify,
    _topup_on_question,
    _wiki_backend_for,
    _wiki_business_recall_safely,
    _wiki_business_text_safely,  # noqa: F401
    _wiki_physical_text,  # noqa: F401
    _wiki_render_schema_text,
)
from apps.chat.models.chat_model import (
    ChatFinishStep,
    ChatRecord,
    OperationEnum,
)
from apps.chat.planning_context import (
    capture_planning_context,
    restore_planning_context,
)
from apps.chat.steps.chat_scope import (
    cached_access_scope,
    connection_fresh,
    invalidate_connection,
    is_missing,
    remember_access_scope,
    remember_connection,
)
from apps.chat.steps.custom_prompt import match_custom_prompts
from apps.chat.steps.datasource import select_datasource, validate_history_ds
from apps.chat.steps.knowledge import get_compiled_knowledge, match_knowledge
from apps.chat.steps.observability import log_span
from apps.chat.steps.recall_map import (
    render_knowledge_map,  # noqa: F401
    render_schema_map,  # noqa: F401
)
from apps.chat.steps.recall_topup import topup_enabled_for  # noqa: F401
from apps.chat.steps.schema import match_table_schema
from apps.chat.time_intent import infer_time_intent
from apps.chat.turn_contracts import TurnRoute
from apps.conversation.models import ConversationRun, QueryRun
from apps.conversation.outcome import (
    running_outcome,
)
from apps.conversation.run_service import (
    load_prior_user_evidence,
    require_active_run,
)
from apps.conversation.runtime_context import attach_runtime
from apps.conversation.session import session_scope
from apps.conversation.sink import StreamSink
from apps.datasource.access import (
    resolve_access_scope,
)
from common.error import SingleMessageError, SQLBotDBConnectionError
from common.utils.utils import SQLBotLogUtil


def prepare_record_node(state: NlqState) -> NlqState:
    """Emit SSE header only — no domain match (match runs after ds is sure)."""
    llm_service = _llm_service(state)
    sink = StreamSink.from_state(state)
    record = llm_service.get_record()
    return_img = bool(state.get("return_img", True))
    json_result: dict[str, Any] = {"success": True}

    try:
        sink.event({"type": "id", "id": record.id})
        sink.event({"type": "question", "question": record.question})
        sink.record_header(
            record_id=record.id,
            question=record.question,
            prefix=llm_service.trans("i18n_chat.record_id_in_mcp"),
        )
        if sink.mode == "json":
            json_result["record_id"] = record.id

        return {
            **state,
            "graph_key": "chat",
            "mode": "primary",
            "chat_id": record.chat_id,
            "record_id": record.id,
            "return_img": return_img,
            "json_result": json_result,
            "step_index": 0,
            "active_candidate": {},
            "rejected_candidate": None,
            "accepted_candidate": None,
            "max_steps": state.get("max_steps") or _MAX_STEPS,
            "max_batch_size": state.get("max_batch_size") or _MAX_BATCH_SIZE,
            "analysis_text": "",
            "decision": "",
            "decision_reason": "",
            "repair_hint": "",
            "gen_attempts": 0,
            "entity_bindings": {},
            "knowledge_matches": [],
            "compiled_knowledge": {},
            "temporal_parse": {},
            "planning_decision": "pending",
            "ambiguity_payload": {},
            "unsupported_payload": {},
            "turn_route": {},
            "source_datasets": [],
            "data_strategy": "direct_query",
            "terminal_answer": {},
            "execution_mode": "verified",
            "risk_assessment": {},
            "semantic_review": {},
            "plan_facts": [],
            "planning_model_elapsed_sec": 0.0,
            "repair_source_plans": [],
            "outcome": running_outcome(),
            "finish_step": state.get("finish_step")
            or int(ChatFinishStep.GENERATE_CHART.value),
        }
    except Exception as e:
        return {
            **_fail(state, record.id, e),
            "graph_key": "chat",
            "mode": "primary",
            "chat_id": record.chat_id,
            "record_id": record.id,
            "return_img": return_img,
            "json_result": json_result,
        }


def ensure_datasource_node(state: NlqState) -> NlqState:
    """Select/validate datasource + connection (chat-scoped connection cache).

    The first turn of a conversation validates connectivity against the
    target DB and emits the audit span; later turns within the TTL reuse the
    cached verdict silently — the datasource bound to a chat does not change
    between turns, and connection failures invalidate the entry immediately.
    """
    llm_service = _llm_service(state)
    sink = StreamSink.from_state(state)

    try:
        connection_cached = bool(llm_service.ds) and connection_fresh(
            getattr(llm_service.ds, "id", None)
        )

        def _bind_datasource(span: Any) -> None:
            with session_scope() as session:
                selected_by_model = not bool(llm_service.ds)
                if selected_by_model:
                    for chunk in select_datasource(
                        llm_service, session, audit_span=span
                    ):
                        sink.token(
                            content=chunk.get("content"),
                            reasoning_content=chunk.get("reasoning_content"),
                            event_type="datasource-result",
                        )
                    sink.event(
                        {
                            "id": llm_service.ds.id,
                            "datasource_name": llm_service.ds.name,
                            "engine_type": getattr(llm_service.ds, "type", None),
                            "type": "datasource",
                        }
                    )
                else:
                    validate_history_ds(llm_service, session)

                if connection_cached:
                    return
                connected = llm_service.protocol.check_connection(ds=llm_service.ds)
                if not connected:
                    invalidate_connection(getattr(llm_service.ds, "id", None))
                    raise SQLBotDBConnectionError("Datasource connection failed")
                remember_connection(getattr(llm_service.ds, "id", None))
                if span is None:
                    return
                span.set_input(
                    {
                        "datasource_id": getattr(llm_service.ds, "id", None),
                        "selected_by_model": selected_by_model,
                    }
                )
                span.set_output(
                    {
                        "connected": True,
                        "datasource_id": getattr(llm_service.ds, "id", None),
                        "datasource_name": getattr(llm_service.ds, "name", ""),
                        "engine_type": getattr(llm_service.ds, "type", None),
                    }
                )
                span.set_summary("chat.audit.datasource_selected")

        if (connection_cached or state.get("planning_decision") == "replan") and (
            llm_service.ds
        ):
            _bind_datasource(None)
            return state
        with log_span(
            operate=OperationEnum.CHOOSE_DATASOURCE,
            record_id=llm_service.record.id,
            local_operation=bool(llm_service.ds),
            graph_node="ensure_datasource",
            title_key="chat.log.CHOOSE_DATASOURCE",
        ) as span:
            _bind_datasource(span)
            return state
    except Exception as e:
        return _fail(state, llm_service.record.id, e)


def recall_knowledge_node(state: NlqState) -> NlqState:
    llm_service = _llm_service(state)
    oid, ds_id = _ds_scope(llm_service)
    # Wiki 体系为唯一知识后端，返回干净的 wiki 上下文，不再编译旧 unit bundle
    return {
        **state,
        "knowledge_matches": [],
        "compiled_knowledge": {},
        "wiki_context": {
            **(state.get("wiki_context") or {}),
            "backend": "wiki",
            "unit_bundle": "disabled",
        },
    }


def parse_temporal_evidence_node(state: NlqState) -> NlqState:
    """Capture deterministic temporal evidence without creating contract state."""
    llm_service = _llm_service(state)
    question = llm_service.generation_question
    with session_scope() as session:
        run = require_active_run(session, str(state["run_id"]))
        business_now = run.business_now
    temporal_parse = infer_time_intent(str(question or ""), now=business_now)
    if not temporal_parse:
        return state
    return {**state, "temporal_parse": temporal_parse}


def resolve_access_scope_node(state: NlqState) -> NlqState:
    """Resolve datasource visibility once per (user, ds), reused across turns.

    The scope depends on the user and the datasource — never on the chat — so
    the first turn of any conversation resolves and emits the audit span, and
    later turns within the TTL reuse the cached scope silently. The snapshot
    write-back contract is unaffected: ``attach_runtime`` still binds the
    scope for every run.
    """
    llm_service = _llm_service(state)
    try:
        run_id = str(state["run_id"])
        oid, ds_id = _ds_scope(llm_service)
        user_id = getattr(llm_service.current_user, "id", None)
        if ds_id is not None:
            cached = cached_access_scope(int(oid or 1), int(ds_id), user_id)
            if not is_missing(cached):
                attach_runtime(run_id, access_scope=cached)
                return state

        def _bind_access_scope(span: Any) -> None:
            with session_scope() as session:
                access_scope = resolve_access_scope(
                    session,
                    current_user=llm_service.current_user,
                    ds=llm_service.ds,
                )
                if ds_id is not None:
                    remember_access_scope(
                        int(oid or 1), int(ds_id), user_id, access_scope
                    )
                attach_runtime(run_id, access_scope=access_scope)
                if span is None:
                    return
                span.set_detail(
                    {
                        "access_scope_applied": access_scope is not None,
                        "datasource_id": getattr(llm_service.ds, "id", None),
                    }
                )
                span.set_summary("chat.audit.access_scope_ready")

        if state.get("planning_decision") == "replan":
            _bind_access_scope(None)
            return state
        with log_span(
            operate=OperationEnum.CHOOSE_TABLE,
            record_id=llm_service.record.id,
            local_operation=True,
            graph_node="resolve_access_scope",
            title_key="chat.log.ACCESS_SCOPE",
            brief="确认数据访问范围",
        ) as span:
            _bind_access_scope(span)
            return state
    except Exception as exc:
        return _fail(state, llm_service.record.id, exc)


def match_custom_prompts_node(state: NlqState) -> NlqState:
    llm_service = _llm_service(state)
    oid, ds_id = _ds_scope(llm_service)
    with session_scope() as session:
        try:
            match_custom_prompts(
                llm_service, session, CustomPromptTypeEnum.GENERATE_SQL, oid, ds_id
            )
            return state
        except Exception as e:
            return _fail(state, llm_service.record.id, e)


def retrieve_schema_node(state: NlqState) -> NlqState:
    """Project schema from bound knowledge tables; rank only when no unit hit.

    ``required_override`` / ``table_limit`` 由 retrieve_context_node 注入
    （wiki 主导表选择）：闭包表必选 + embedding 召回按预算补充。独立调用
    （单测/其它路径）时两者为 None，行为与历史一致。
    """
    llm_service = _llm_service(state)
    compiled = get_compiled_knowledge(llm_service)
    bound = list(compiled.bound_resources) if compiled is not None else []
    entity_tables = binding_resource_names(state.get("entity_bindings") or {})
    exact = list(dict.fromkeys([*bound, *entity_tables])) if bound else None
    required_override = state.get("_wiki_required_tables")
    table_limit = state.get("_wiki_table_limit")
    required = (
        list(dict.fromkeys([*entity_tables, *required_override]))
        if required_override
        else entity_tables
    )
    if required_override:
        state.pop("_wiki_required_tables", None)
        state.pop("_wiki_table_limit", None)
    with session_scope() as session:
        try:
            # audit=False：外层 retrieve_context 已有单一检索 span，
            # 这里再发一个 CHOOSE_TABLE span 会造成双卡片（chat 167 问题 1）
            resource_names = match_table_schema(
                llm_service,
                session,
                resource_names=exact,
                required_resource_names=required,
                access_scope=_access_scope(state),
                table_limit=table_limit,
                audit=False,
            )
            if resource_names and _wiki_backend_for(_ds_scope(llm_service)[1]):
                _wiki_render_schema_text(state, llm_service, list(resource_names))
            return {
                **state,
                "entity_bindings": retain_binding_resources(
                    state.get("entity_bindings") or {},
                    resource_names,
                ),
            }
        except Exception as e:
            return _fail(state, llm_service.record.id, e)


_SCHEMA_SECTION_RE = re.compile(r"^## .+? \((\w+)\)", re.M)


def _split_schema_sections(
    schema_text: str, table_origins: dict[str, str]
) -> list[dict[str, Any]]:
    """渲染后的 schema 全文按表分节（详情卡片：每表一卡）。

    行格式 ``## 中文注释 (表名)``（db 兜底带 ``[db]`` 后缀）——以括号内
    表名定界。origins 缺失的表按 "embedding" 兜底标注。"""
    matches = list(_SCHEMA_SECTION_RE.finditer(schema_text))
    if not matches:
        return []
    sections: list[dict[str, Any]] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(schema_text)
        table = match.group(1)
        sections.append(
            {
                "table": table,
                "origin": table_origins.get(table, "embedding"),
                "chars": end - start,
                "text": schema_text[start:end].strip("\n"),
            }
        )
    return sections


def retrieve_context_node(state: NlqState) -> NlqState:
    """Build planner context as one checkpointed stage.

    Domain steps keep their own audit spans, but the graph does not checkpoint
    a chain of micro-nodes whose only purpose is passing the same dictionary.
    Re-running this stage after clarification is safe because retrieved facts
    are deduplicated when they enter the evidence ledger.
    """
    # Clarification only appends immutable user evidence; it does not change
    # datasource metadata. Reuse the durable snapshot instead of repeating all
    # external retrieval calls (and their failure modes) after every answer.
    if state.get("planning_decision") == "replan":
        llm_service = _llm_service(state)
        with session_scope() as session:
            nlq_run = session.get(QueryRun, str(state["run_id"]))
            persisted = dict(nlq_run.planning_context or {}) if nlq_run else {}
        if persisted:
            try:
                snapshot = restore_planning_context(llm_service, persisted)
                restored_state = {
                    **state,
                    "entity_bindings": snapshot.entity_bindings,
                    "temporal_parse": snapshot.temporal_parse,
                    "compiled_knowledge": snapshot.compiled_knowledge,
                    "wiki_context": snapshot.wiki_context,
                }
                # 先 topup 后拉 wiki 业务段：topup 可能扩工作集，扩窗后重拉
                # 才能让业务语义段覆盖最终窗口（对齐 gate bounce 时序）。
                topped = _topup_after_clarify(restored_state, llm_service)
                _oid_w, _ds_w = _ds_scope(llm_service)
                wiki_result = _wiki_business_recall_safely(
                    str(getattr(llm_service, "retrieval_question", "") or ""),
                    ds_id=_ds_w,
                    databases=_ds_databases(llm_service),
                )
                if wiki_result is not None:
                    _record_wiki_recall_telemetry(
                        topped, wiki_result, source="refresh_on_replan"
                    )
                    topped = {
                        **topped,
                        "wiki_knowledge_text": wiki_result.text,
                        "wiki_context": {
                            **(topped.get("wiki_context") or {}),
                            "business_recall_source": "refresh_on_replan",
                            "business_text_chars": len(wiki_result.text),
                        },
                    }
                    # 锚点闭包（召回后补渲）：引用即可见
                    _apply_anchor_closure(
                        topped,
                        llm_service,
                        wiki_result.page_keys,
                        base_tables=list(llm_service.table_name_list or []),
                    )
                return topped
            except ValueError:
                # A malformed/incomplete snapshot is rebuilt through the sole
                # retrieval path below; planning is never allowed to consume it.
                pass

    current = state
    # ── 检索段（单 span 承载：wiki 召回 → 表选择 → schema 渲染 → 闭包）──
    # chat 167 复盘：schema 检索与 wiki 召回曾是两个同名 CHOOSE_TABLE span，
    # 中间还有表向量召回的 4.4s 盲区；这里合成一个 span 连续覆盖。
    llm_service_lead = _llm_service(state)
    _oid_l, _ds_l = _ds_scope(llm_service_lead)
    # wiki 主导表选择：business 召回先行——命中页的锚点闭包表成为
    # required（必选），embedding 召回按预算补充（chat 167：14 表→10 表内）。
    # 无 wiki 命中时注入 None，完全走现状（不裁剪）。
    wiki_lead = (
        _wiki_business_recall_safely(
            str(getattr(llm_service_lead, "retrieval_question", "") or ""),
            ds_id=_ds_l,
            databases=_ds_databases(llm_service_lead),
        )
        if not llm_service_lead.out_ds_instance
        else None
    )
    if wiki_lead is not None and wiki_lead.page_keys:
        try:
            from apps.chat.steps.wiki_recall import _store
            from apps.knowledge.wiki.anchors import closure_tables

            store = _store()
            if store is not None:
                closure, _truncated = closure_tables(store, wiki_lead.page_keys)
                if closure:
                    from common.core.config import settings

                    current = {
                        **current,
                        "_wiki_required_tables": closure,
                        "_wiki_table_limit": len(closure)
                        + max(0, int(settings.WIKI_TABLE_SUPPLEMENT_COUNT)),
                    }
        except Exception as exc:  # noqa: BLE001 — wiki 层零影响约定
            SQLBotLogUtil.warning("wiki-led table selection degraded: %s", exc)
    # 单一检索 span：链前 wiki 召回 + 领域步骤链 + 遥测投影全部在其内，
    # 4.4s 表向量召回盲区随之消失（with 形式保证异常也关闭 span）。
    with log_span(
        operate=OperationEnum.CHOOSE_TABLE,
        record_id=getattr(llm_service_lead.record, "id", None),
        local_operation=True,
        graph_node="retrieve_context",
        title_key="chat.log.CHOOSE_TABLE",
    ) as retrieval_span:
        for step in (
            recall_knowledge_node,
            ground_entities_node,
            match_custom_prompts_node,
            retrieve_schema_node,
            parse_temporal_evidence_node,
        ):
            current = step(current)
            if current.get("error"):
                break
        if not current.get("error"):
            llm_service = _llm_service(current)
            notice, question_wiki_context = _topup_on_question(current, llm_service)
            if notice:
                current = {**current, "recall_topup_notice": notice}
            current = {**current, "wiki_context": question_wiki_context}
            # wiki 召回已在链前主导表选择（wiki_lead）；此处复用其结果落遥测与
            # business_knowledge 文本，避免二次召回（嵌入查询/RRF 重复计算）。
            wiki_result = wiki_lead
            if wiki_result is None:
                _oid_w, _ds_w = _ds_scope(llm_service)
                wiki_result = _wiki_business_recall_safely(
                    str(getattr(llm_service, "retrieval_question", "") or ""),
                    ds_id=_ds_w,
                    databases=_ds_databases(llm_service),
                )
            if wiki_result is not None:
                _record_wiki_recall_telemetry(
                    current, wiki_result, source="retrieve_context"
                )
                current = {
                    **current,
                    "wiki_knowledge_text": wiki_result.text,
                    "wiki_context": {
                        **(current.get("wiki_context") or {}),
                        "backend": "wiki",
                        "business_recall_source": "retrieve_context",
                        "business_text_chars": len(wiki_result.text),
                    },
                }
                # 锚点闭包（召回后补渲）：被召回语义页引用的表并入 schema 渲染
                # 清单——引用即可见，闭包表随 wiki_context 落快照可审计。
                _apply_anchor_closure(
                    current,
                    llm_service,
                    wiki_result.page_keys,
                    base_tables=list(llm_service.table_name_list or []),
                )
            wc = dict(current.get("wiki_context") or {})
            hits = wc.get("wiki_hits") or []
            # 完整原始响应回填（chat 168 问题 1：原始值 tab 要完整数据，
            # 不是摘要）。schema 全文与命中页渲染文本均可从上游对象直接取，
            # 大小有界（schema ~40KB / 每页正文 400 字封顶）。
            schema_full = str(
                getattr(llm_service_lead.chat_question, "db_schema", "") or ""
            )
            closure_tables_list = wc.get("anchor_closure_tables") or []
            # 每表来源标注 + 闭包归因（chat 169：表选择可解释——每张表
            # 是闭包拉入还是 embedding 补充、被哪个命中页的哪个字段引用）
            table_origins = {
                name: "closure" if name in closure_tables_list else "embedding"
                for name in (llm_service_lead.table_name_list or [])
            }
            anchor_attribution: dict[str, Any] = {}
            try:
                from apps.chat.steps.wiki_recall import _store as _wiki_store
                from apps.knowledge.wiki.anchors import anchor_table_attribution

                _store_obj = _wiki_store()
                if _store_obj is not None and wiki_result is not None:
                    anchor_attribution = anchor_table_attribution(
                        _store_obj, wiki_result.page_keys
                    )
            except Exception as exc:  # noqa: BLE001 — 归因失败不影响检索
                SQLBotLogUtil.warning("anchor attribution degraded: %s", exc)
            # schema 按表分节（详情卡片：每表一卡）
            schema_sections = _split_schema_sections(schema_full, table_origins)
            retrieval_span["payload"] = {
                "resource_count": len(llm_service_lead.table_name_list or []),
                "resources": list(llm_service_lead.table_name_list or []),
                "table_origins": table_origins,
                "access_scope_applied": _access_scope(state) is not None,
                "schema_chars": len(schema_full),
                "schema_text": schema_full,
                "schema_sections": schema_sections,
                "wiki": {
                    "hit_count": len(hits),
                    "elapsed_ms": wc.get("wiki_recall_elapsed_ms"),
                    "embedding_built": wc.get("wiki_embedding_built"),
                    "hits": hits,
                    "passages": (wiki_result.passages if wiki_result else {}),
                    "trace": (wiki_result.trace if wiki_result else {}),
                    "anchor_closure_tables": closure_tables_list,
                    "anchor_closure_truncated": wc.get("anchor_closure_truncated", 0),
                    "anchor_attribution": anchor_attribution,
                },
            }
            retrieval_span.set_summary(
                "chat.audit.retrieval_ready",
                count=len(llm_service_lead.table_name_list or []),
                wiki_hits=len(hits),
            )
        snapshot = capture_planning_context(
            llm_service,
            entity_bindings=current.get("entity_bindings") or {},
            temporal_parse=current.get("temporal_parse") or {},
            wiki_context=dict(current.get("wiki_context") or {}),
        )
        if not snapshot.usable:
            return _fail(
                current,
                llm_service.record.id,
                "No usable datasource schema was retrieved for query planning",
            )
        with session_scope() as session:
            require_active_run(session, str(current["run_id"]))
            nlq_run = session.get(QueryRun, str(current["run_id"]))
            if nlq_run is None:
                return _fail(
                    current,
                    llm_service.record.id,
                    f"NLQ run {current['run_id']} not found",
                )
            nlq_run.planning_context = snapshot.model_dump(mode="json")
            session.add(nlq_run)
            session.commit()
        if snapshot.truncation:
            SQLBotLogUtil.info(
                "planner context truncated: "
                + ", ".join(str(item.get("section")) for item in snapshot.truncation)
            )
    return current


def ground_entities_node(state: NlqState) -> NlqState:
    """Resolve bindings from local knowledge snapshots; never query the datasource."""
    llm_service = _llm_service(state)
    record_id = getattr(llm_service.record, "id", None) or state.get("record_id")
    with log_span(
        operate=OperationEnum.GROUND_ENTITIES,
        record_id=record_id,
        ai_modal_id=getattr(llm_service.chat_question, "ai_modal_id", None),
        ai_modal_name=getattr(llm_service.chat_question, "ai_modal_name", None),
        local_operation=True,
        graph_node="ground_entities",
        title_key="chat.log.GROUND_ENTITIES",
    ) as span:
        bindings = resolve_entity_bindings(
            state.get("knowledge_matches") or [],
        )
        span["payload"] = {
            "candidates": bindings.get("candidates") or [],
            "resolved": bindings.get("resolved") or {},
            "ambiguous": bindings.get("ambiguous") or {},
            "match_count": bindings.get("match_count") or 0,
        }
        match_count = int(bindings.get("match_count") or 0)
        if match_count:
            span.set_summary("chat.audit.entities_grounded", count=match_count)
        else:
            span.set_summary("chat.audit.entities_none")
        return {
            **state,
            "entity_bindings": bindings,
        }


_REFERENCED_FIELD_LIMIT = 20


_REFERENCED_ROW_LIMIT = 3


_REFERENCED_CELL_WIDTH = 24


def _referenced_dataset_outline(dataset: dict[str, Any]) -> dict[str, Any]:
    """Planner-facing shape of one referenced dataset.

    A continuation/revision turn plans against the previous result — the
    final SQL (the authoritative semantics the user saw), the field list, and
    a couple of sample rows let the planner reason about shape and grain
    without guessing from the prose summary. Rows are clipped hard: this is
    an outline, not data transport.
    """

    def _clip_cell(value: Any) -> Any:
        text = str(value)
        return (
            text[:_REFERENCED_CELL_WIDTH]
            if len(text) > _REFERENCED_CELL_WIDTH
            else value
        )

    fields = [str(item) for item in dataset.get("fields") or []][
        :_REFERENCED_FIELD_LIMIT
    ]
    sample_rows = [
        {key: _clip_cell(value) for key, value in row.items() if key in fields}
        for row in (dataset.get("preview_rows") or dataset.get("rows") or [])[
            :_REFERENCED_ROW_LIMIT
        ]
        if isinstance(row, dict)
    ]
    return {
        "dataset_id": dataset.get("dataset_id"),
        "title": dataset.get("title") or "",
        "fields": fields,
        "row_count": dataset.get("row_count"),
        "sql": str(dataset.get("sql") or "")[:1200],
        "sample_rows": sample_rows,
    }


def _record_answer_datasets(record: ChatRecord) -> list[dict[str, Any]]:
    answer = record.answer if isinstance(record.answer, dict) else {}
    raw = answer.get("datasets") or answer.get("source_datasets") or []
    return [
        _dataset_capabilities(
            {
                **dict(item),
                "source_record_id": int(record.id or 0),
                "rows": list(item.get("preview_rows") or item.get("rows") or []),
                "preview_rows": list(item.get("preview_rows") or item.get("rows") or []),
            }
        )
        for item in raw
        if isinstance(item, dict) and item.get("status") in {"succeeded", "degraded"}
    ]


def assemble_turn_context_node(state: NlqState) -> NlqState:
    """Select durable history/results before any datasource or model work."""
    try:
        route = TurnRoute.model_validate(state.get("turn_route") or {})
        source_datasets: list[dict[str, Any]] = []
        referenced_turns: list[dict[str, Any]] = []
        prior_user_evidence: list[dict[str, Any]] = []
        with session_scope() as session:
            run = require_active_run(session, str(state["run_id"]))
            current = session.get(ChatRecord, run.chat_record_id)
            if current is None:
                raise LookupError("Conversation turn not found")
            prior_user_evidence = load_prior_user_evidence(
                session,
                chat_id=int(current.chat_id),
                user_id=int(run.user_id),
                reference_record_ids=route.reference_record_ids,
            )
            for record_id in route.reference_record_ids:
                referenced = session.get(ChatRecord, int(record_id))
                if (
                    referenced is None
                    or int(referenced.create_by or 0) != int(run.user_id)
                    or int(referenced.chat_id) != int(current.chat_id)
                ):
                    raise SingleMessageError(
                        "Referenced conversation result is unavailable"
                    )
                if (
                    current.datasource is not None
                    and referenced.datasource is not None
                    and int(current.datasource) != int(referenced.datasource)
                ):
                    raise SingleMessageError(
                        "Cannot continue a query across different datasources"
                    )
                datasets = _record_answer_datasets(referenced)
                source_datasets.extend(datasets)
                latest_run = (
                    session.exec(
                        select(ConversationRun)
                        .where(
                            ConversationRun.chat_record_id == int(referenced.id),
                        )
                        .order_by(ConversationRun.attempt_index.desc())
                        .limit(1)
                    )
                    .scalars()
                    .one_or_none()
                )
                latest_query = (
                    session.get(QueryRun, latest_run.run_id)
                    if latest_run is not None
                    else None
                )
                answer = (
                    referenced.answer if isinstance(referenced.answer, dict) else {}
                )
                planning = (
                    dict(latest_query.planning_context or {})
                    if latest_query is not None
                    else {}
                )
                referenced_turns.append(
                    {
                        "record_id": referenced.id,
                        "question": referenced.question,
                        "turn_kind": referenced.turn_kind,
                        "answer_status": answer.get("status"),
                        "answer_summary": str(answer.get("content") or "")[:1000],
                        "run_status": latest_run.status
                        if latest_run is not None
                        else None,
                        "planning_status": (
                            latest_query.planning_status
                            if latest_query is not None
                            else None
                        ),
                        "datasets": [
                            _referenced_dataset_outline(item) for item in datasets
                        ],
                        "revision_ids": list(
                            (planning.get("compiled_knowledge") or {}).get("revision_ids") or []
                            if isinstance(planning.get("compiled_knowledge"), dict)
                            else []
                        ),
                    }
                )
            strategy = choose_data_strategy(
                route,
                referenced_datasets=tuple(source_datasets),
                message_has_query_need=route.task_kind in {"query", "prediction"},
            )
            business_now_text = run.business_now.isoformat()
            business_timezone = run.timezone
            fingerprint = context_fingerprint(
                {
                    "message": current.question,
                    "route": route.model_dump(mode="json"),
                    "references": referenced_turns,
                    "prior_user_evidence": prior_user_evidence,
                    "dataset_ids": [item.get("dataset_id") for item in source_datasets],
                    "business_now": business_now_text,
                    "timezone": business_timezone,
                }
            )
            run.context_fingerprint = fingerprint
            session.add(run)
            session.commit()
        return {
            **state,
            "referenced_turns": referenced_turns,
            "prior_user_evidence": prior_user_evidence,
            "source_datasets": source_datasets,
            "data_strategy": strategy,
            "context_fingerprint": fingerprint,
            "business_now": business_now_text,
            "timezone": business_timezone,
            "reference_record_ids": list(route.reference_record_ids),
        }
    except Exception as exc:
        return _fail(state, state.get("record_id"), exc)


def unavailable_context_node(state: NlqState) -> NlqState:
    route = state.get("turn_route") or {}
    task = str(route.get("task_kind") or "analysis")
    message = (
        "当前没有可用于分析的查询结果，请先提出需要查询的数据。"
        if task == "analysis"
        else "当前没有满足预测条件的时间序列数据，请明确要预测的指标和时间粒度。"
    )
    return _fail(state, state.get("record_id"), SingleMessageError(message))
