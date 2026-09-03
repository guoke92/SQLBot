"""NLQ node package — split from the former single-module nlq.py.

Pure code motion: chat.yaml dotted paths (apps.chat.graphs.nodes.nlq.*)
and ``from apps.chat.graphs.nodes import nlq`` keep working via this
aggregate re-export.
"""

from apps.chat.graphs.nodes.nlq.analysis import (  # noqa: F401
    _dataset_capabilities,
    _run_downstream_agent,
    _turn_source_datasets,
    analysis_agent_node,
    prediction_agent_node,
)
from apps.chat.graphs.nodes.nlq.audit import (  # noqa: F401
    _apply_row_permissions,
    _enqueue_knowledge_capture,
    _enum_refs_for_step,
    _merge_compiled_apply_log,
    _query_plan,
    _record_intent_default_application,
    _record_snapshot_values,
    _serialized_plan,
    _wiki_table_columns,
)
from apps.chat.graphs.nodes.nlq.context import (  # noqa: F401
    _REFERENCED_CELL_WIDTH,
    _REFERENCED_FIELD_LIMIT,
    _REFERENCED_ROW_LIMIT,
    _record_answer_datasets,
    _referenced_dataset_outline,
    assemble_turn_context_node,
    ensure_datasource_node,
    ground_entities_node,
    match_custom_prompts_node,
    parse_temporal_evidence_node,
    prepare_record_node,
    recall_knowledge_node,
    resolve_access_scope_node,
    retrieve_context_node,
    retrieve_schema_node,
    unavailable_context_node,
)
from apps.chat.graphs.nodes.nlq.execution import (  # noqa: F401
    _decide_next_impl,
    decide_next_node,
    execute_queries_node,
    generate_queries_node,
)
from apps.chat.graphs.nodes.nlq.planning import (  # noqa: F401
    _accepted_review_card,
    _clarification_card_from_review,
    _classify_plan_risk,
    _invoke_semantic_review,
    _persist_query_terminal_failure,
    _plan_fact_models,
    _plan_repair_message,
    _planning_call_timeout_sec,
    _planning_elapsed_for_state,
    _ready_entity_coverage_lint,
    _resolved_question_ids,
    await_clarification_node,
    plan_gate_node,
    plan_query_node,
    review_query_node,
    unsupported_query_node,
)
from apps.chat.graphs.nodes.nlq.presentation import (  # noqa: F401
    _SUMMARY_PROMPT,
    _brief_result_facts,
    _extract_summary_text,
    _extract_title_from_sql_answer,
    _maybe_update_chat_brief,
    _summary_messages,
    _table_chart,
    complete_node,
    fail_node,
    generate_charts_node,
    summarize_answer_node,
)
from apps.chat.graphs.nodes.nlq.quality import (  # noqa: F401
    _assess_all_steps,
    _assess_step_quality,
    _attach_aggregation_totals,
    _build_candidate_quality,
    _candidate_batch,
    _column_stats,
    _data_sample,
    _fallback_analysis,
    _merge_batch_into_steps,
    _metric_stats,
    _normalize_result_data,
    _null_rate,
    _repair_instruction,
    _result_fields,
    _result_rows,
    _scan_field,
)
from apps.chat.graphs.nodes.nlq.routing import (  # noqa: F401
    route_after_context,
    route_after_decision,
    route_after_execute,
    route_after_plan_gate,
    route_after_planning,
    route_after_presentation,
    route_after_queries,
    route_after_review,
    route_after_turn_router,
    turn_router_node,
    unsupported_turn_node,
)
from apps.chat.graphs.nodes.nlq.state import (  # noqa: F401
    _MAX_BATCH_SIZE,
    _MAX_STEPS,
    _ROW_LIMIT,
    _TEMPORAL_RE,
    CandidateBatch,
    NlqState,
    _access_scope,
    _ds_scope,
    _fail,
    _finish_step_value,
    _generation_question,
    _llm_service,
    _sql_dialect,
)
from apps.chat.graphs.nodes.nlq.topup import (  # noqa: F401
    _apply_anchor_closure,
    _GateExpansion,
    _run_topup,
    _topup_after_clarify,
    _topup_on_failed_gates,
    _topup_on_question,
    _TopupRun,
    _wiki_backend_for,
    _wiki_business_recall_safely,
    _wiki_business_text_safely,
    _wiki_physical_recall_safely,
    _wiki_physical_text,
    _wiki_render_schema_text,
)

# Third-party symbols re-exported: tests monkeypatch them on this namespace.
from apps.chat.planning_context import (  # noqa: F401
    capture_planning_context,
    restore_planning_context,
)
from apps.chat.steps.datasource import validate_history_ds  # noqa: F401
from apps.chat.steps.observability import log_span  # noqa: F401
from apps.chat.steps.query_agent import (  # noqa: F401
    revalidate_query_plans,
    run_query_agent,
)
from apps.chat.steps.recall_map import (  # noqa: F401
    render_knowledge_map,
    render_schema_map,
)
from apps.chat.steps.recall_topup import (  # noqa: F401
    TopupSignals,
    apply_knowledge_topup,
    fulfill_recall_topup,
    record_topup_event,
    resolve_recall_topup,
    topup_enabled_for,
)
from apps.chat.steps.stream import consume_llm  # noqa: F401
from apps.conversation.run_service import (  # noqa: F401
    active_evidence,
    finalize_run,
    persist_query_decision,
    require_active_run,
)
from apps.conversation.runtime_context import attach_runtime  # noqa: F401
from apps.conversation.session import session_scope  # noqa: F401
from apps.conversation.sink import StreamSink  # noqa: F401
from apps.datasource.access import resolve_access_scope  # noqa: F401
