"""Code-side defaults for agent runtime configuration.

Single source of truth for what a fresh install runs. The database only ever
*overrides* these values; when no row exists (or the DB is unreachable) the
agent must behave exactly as it did before this feature landed.
"""

from __future__ import annotations

from typing import Any, NamedTuple

from apps.chat.agent_knowledge import (
    EXECUTION_ROUND_LIMIT,
    KNOWLEDGE_TOOLS,
    PROBE_SQL_LIMIT,
    SEARCH_WIKI_ROUND_LIMIT,
    WIKI_SCHEMA_GAP_SEARCH_LIMIT,
)

# Tool names as registered by ``apps.chat.tools.registry.build_agent_tools``.
# Guarded by ``tests/test_agent_config_loader.py`` so a new tool cannot be added
# without showing up on the management page.
QUERY_TOOL_NAMES: tuple[str, ...] = (
    "get_table_schema",
    "get_table_relations",
    "search_knowledge",
    "lookup_values",
    "get_dict_values",
    "patch_and_compile_sql",
    "execute_sql_sandbox",
    "compare_results",
    "request_clarification",
)
ANALYZE_TOOL_NAMES: tuple[str, ...] = (
    "profile_sql_result",
    "aggregate_sql_result",
)
DEFAULT_TOOL_NAMES: tuple[str, ...] = QUERY_TOOL_NAMES + ANALYZE_TOOL_NAMES

# Disabling any of these would leave the agent unable to fetch or pause a turn.
REQUIRED_TOOL_NAMES: frozenset[str] = frozenset(
    {
        "execute_sql_sandbox",
        "request_clarification",
    }
)

# Tools with no cross-tool ordering dependency. Parallel dispatch is enabled
# for this set in ``apps.chat.agent.tools.runtime``; exclusive tools serialize
# the whole batch.
DEFAULT_PARALLEL_SAFE: frozenset[str] = KNOWLEDGE_TOOLS


class LoopParamSpec(NamedTuple):
    key: str
    default: int
    minimum: int
    maximum: int
    #: i18n key suffix, resolved by the frontend as ``agent_config.params.<label_key>``
    label_key: str


LOOP_PARAM_SPECS: tuple[LoopParamSpec, ...] = (
    LoopParamSpec(
        "execution_round_limit", EXECUTION_ROUND_LIMIT, 1, 20, "execution_round_limit"
    ),
    LoopParamSpec("probe_sql_limit", PROBE_SQL_LIMIT, 0, 10, "probe_sql_limit"),
    LoopParamSpec(
        "search_wiki_round_limit",
        SEARCH_WIKI_ROUND_LIMIT,
        0,
        10,
        "search_wiki_round_limit",
    ),
    LoopParamSpec(
        "wiki_schema_gap_search_limit",
        WIKI_SCHEMA_GAP_SEARCH_LIMIT,
        0,
        10,
        "wiki_schema_gap_search_limit",
    ),
    LoopParamSpec("tool_call_limit", 24, 1, 64, "tool_call_limit"),
    LoopParamSpec("clarify_limit", 2, 0, 6, "clarify_limit"),
    LoopParamSpec("context_token_limit", 48000, 4000, 200000, "context_token_limit"),
)

LOOP_PARAM_DEFAULTS: dict[str, int] = {
    spec.key: spec.default for spec in LOOP_PARAM_SPECS
}


class SqlRuleSpec(NamedTuple):
    kind: str
    enabled: bool
    #: i18n key suffix, resolved as ``agent_config.sql_rules.<label_key>``
    label_key: str


# Mechanisms checked before execute_sql_sandbox. Order is evaluation order.
SQL_RULE_SPECS: tuple[SqlRuleSpec, ...] = (
    SqlRuleSpec("catalog_probe", True, "catalog_probe"),
    SqlRuleSpec("enum_discovery", True, "enum_discovery"),
    SqlRuleSpec("closed_literal", True, "closed_literal"),
)

SQL_RULE_DEFAULTS: dict[str, dict[str, bool]] = {
    spec.kind: {"enabled": spec.enabled} for spec in SQL_RULE_SPECS
}


def default_tools() -> dict[str, dict[str, Any]]:
    """Neutral tool snapshot: everything enabled, nothing overridden.

    ``description=None`` matters: the management page then shows the code-side
    description and an empty override keeps the tool text byte-identical.
    """
    return {
        name: {
            "enabled": True,
            "description": None,
            "parallel_safe": name in DEFAULT_PARALLEL_SAFE,
            "round_budget": None,
        }
        for name in DEFAULT_TOOL_NAMES
    }
