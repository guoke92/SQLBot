"""Target NLQ-path re-exports — agentic batch loop.

Canonical implementations live in ``apps.chat.graphs.nodes.nlq``.
``NlqState`` is the runtime TypedDict for current/chat and nlq_path nodes.
Target unified graph may use ``ChatState`` (superset) as the compiled state;
node functions accept the nlq batch fields present on both.
"""

from apps.chat.graphs.nodes.nlq import (  # noqa: F401
    NlqState,
    build_context_node,
    complete_node,
    decide_next_node,
    ensure_datasource_node,
    execute_queries_node,
    fail_node,
    generate_charts_node,
    generate_queries_node,
    ground_entities_node,
    match_custom_prompts_node,
    match_terminology_node,
    match_training_node,
    prepare_record_node,
    route_after_decision,
    route_after_execute,
    route_after_queries,
    summarize_node,
)

# Backward-compatible alias used by early target drafts.
ChatState = NlqState
