"""Registered mining capabilities, presets, and dependency closure."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True)
class CapabilitySpec:
    id: str
    pipe: str  # sync | facts | agent | derive
    depends_on: tuple[str, ...] = ()
    recall_targets: tuple[str, ...] = ()
    tools: tuple[str, ...] = ()
    description: str = ""


CAPABILITIES: dict[str, CapabilitySpec] = {
    "structure": CapabilitySpec(
        id="structure",
        pipe="sync",
        recall_targets=("schema", "rank"),
        description="Catalog structure and fingerprint (RANK vectors)",
    ),
    "catalog_stats": CapabilitySpec(
        id="catalog_stats",
        pipe="facts",
        depends_on=("structure",),
        recall_targets=("schema", "brief"),
        description="approx_rows / index_summary",
    ),
    "field_profile": CapabilitySpec(
        id="field_profile",
        pipe="facts",
        depends_on=("structure",),
        recall_targets=("schema", "brief"),
        description="null/ndv/min/max/topk snapshots (PROMPT when READY)",
    ),
    "ddl_constraints": CapabilitySpec(
        id="ddl_constraints",
        pipe="facts",
        depends_on=("structure",),
        recall_targets=("chat_join", "brief"),
        tools=("extract_ddl_constraints",),
        description="Facts bootstrap publishes DDL FK as CONFIRMED; agent tool is read-only",
    ),
    "soft_signals": CapabilitySpec(
        id="soft_signals",
        pipe="derive",
        depends_on=("field_profile",),
        recall_targets=("brief", "agent"),
        description="key_likelihood / temporal_role / domain_role",
    ),
    "dictionary_refresh": CapabilitySpec(
        id="dictionary_refresh",
        pipe="agent",
        depends_on=("structure",),
        recall_targets=("bind",),
        tools=("refresh_dictionary_for_table",),
        description="Refresh enabled dictionary values",
    ),
    "name_similarity": CapabilitySpec(
        id="name_similarity",
        pipe="agent",
        depends_on=("structure",),
        recall_targets=("agent",),
        tools=("name_similarity",),
        description="Name-near field pairs",
    ),
    "inclusion_probe": CapabilitySpec(
        id="inclusion_probe",
        pipe="agent",
        depends_on=("field_profile", "soft_signals"),
        recall_targets=("admin", "agent"),
        tools=("overlap_probe", "fanout_probe"),
        description="Bounded inclusion / fanout probes",
    ),
    "equi_candidates": CapabilitySpec(
        id="equi_candidates",
        pipe="agent",
        depends_on=("inclusion_probe", "name_similarity"),
        recall_targets=("admin", "chat_join"),
        tools=("upsert_relation_candidate", "list_relation_candidates"),
        description="Write EQUI_JOIN candidates",
    ),
    "query_log_joins": CapabilitySpec(
        id="query_log_joins",
        pipe="agent",
        depends_on=("structure",),
        recall_targets=("admin", "chat_join"),
        tools=("mine_query_log_joins", "upsert_relation_candidate", "list_relation_candidates"),
        description="Historical SQL join co-occurrence",
    ),
    "binding_probe": CapabilitySpec(
        id="binding_probe",
        pipe="agent",
        depends_on=("field_profile",),
        recall_targets=("admin", "agent"),
        tools=("cooccurrence_probe", "upsert_binding_candidate"),
        description="Intra-table binding candidates",
    ),
    "hierarchy_probe": CapabilitySpec(
        id="hierarchy_probe",
        pipe="agent",
        depends_on=("field_profile",),
        recall_targets=("admin", "chat_join"),
        tools=("hierarchy_probe", "upsert_relation_candidate"),
        description="Hierarchy / path candidates",
    ),
    "formula_probe": CapabilitySpec(
        id="formula_probe",
        pipe="agent",
        depends_on=("field_profile",),
        recall_targets=("admin", "agent"),
        tools=("formula_probe", "upsert_relation_candidate"),
        description="Numeric formula candidates",
    ),
    "draft_descriptions": CapabilitySpec(
        id="draft_descriptions",
        pipe="agent",
        depends_on=("field_profile",),
        recall_targets=("admin",),
        tools=("draft_field_description", "draft_table_description"),
        description="LLM description drafts (no auto-apply)",
    ),
    "table_role": CapabilitySpec(
        id="table_role",
        pipe="derive",
        depends_on=("catalog_stats", "soft_signals"),
        recall_targets=("brief", "agent"),
        tools=("compute_ai_priority",),
        description="fact/dim/bridge role hint",
    ),
    "samples": CapabilitySpec(
        id="samples",
        pipe="agent",
        depends_on=("structure",),
        recall_targets=("agent",),
        tools=("get_samples",),
        description="Bounded sample rows for agent",
    ),
}

PRESET_LITE: frozenset[str] = frozenset(
    {
        "structure",
        "catalog_stats",
        "field_profile",
        "ddl_constraints",
    }
)
PRESET_STANDARD: frozenset[str] = PRESET_LITE | frozenset(
    {
        "soft_signals",
        "name_similarity",
        "inclusion_probe",
        "equi_candidates",
        "query_log_joins",
    }
)
PRESET_DEEP: frozenset[str] = PRESET_STANDARD | frozenset(
    {
        "binding_probe",
        "hierarchy_probe",
        "formula_probe",
        "draft_descriptions",
        "table_role",
        "samples",
        "dictionary_refresh",
    }
)

PRESETS: dict[str, frozenset[str]] = {
    "lite": PRESET_LITE,
    "standard": PRESET_STANDARD,
    "deep": PRESET_DEEP,
}

# Always available read helpers for agent sessions.
BASE_AGENT_TOOLS: frozenset[str] = frozenset(
    {
        "list_tables_brief",
        "get_profile_brief",
        "list_published_relations",
        "compute_ai_priority",
    }
)

# derive-* capabilities are read-time heuristics, not bootstrap steps.
FACTS_PIPES: frozenset[str] = frozenset({"facts", "sync"})
AGENT_PIPES: frozenset[str] = frozenset({"agent", "derive"})


def preset_capabilities(name: str) -> frozenset[str]:
    key = (name or "lite").strip().lower()
    if key == "custom":
        return frozenset()
    return PRESETS.get(key, PRESET_LITE)


def expand_capabilities(selected: Iterable[str]) -> frozenset[str]:
    """Return selected capabilities closed under depends_on."""
    pending = {str(x).strip() for x in selected if str(x).strip()}
    unknown = pending - set(CAPABILITIES)
    if unknown:
        raise ValueError(f"unknown capabilities: {sorted(unknown)}")
    closed: set[str] = set()
    stack = list(pending)
    while stack:
        cap = stack.pop()
        if cap in closed:
            continue
        closed.add(cap)
        for dep in CAPABILITIES[cap].depends_on:
            if dep not in closed:
                stack.append(dep)
    # Structure is always implied for any mining work.
    closed.add("structure")
    return frozenset(closed)


def facts_capabilities(caps: Iterable[str]) -> frozenset[str]:
    return frozenset(
        c
        for c in caps
        if CAPABILITIES.get(c) and CAPABILITIES[c].pipe in FACTS_PIPES
    )


def agent_capabilities(caps: Iterable[str]) -> frozenset[str]:
    return frozenset(
        c
        for c in caps
        if CAPABILITIES.get(c) and CAPABILITIES[c].pipe in AGENT_PIPES
    )


def tools_for_capabilities(caps: Iterable[str]) -> frozenset[str]:
    tools: set[str] = set(BASE_AGENT_TOOLS)
    for cap in caps:
        spec = CAPABILITIES.get(cap)
        if spec is None:
            continue
        tools.update(spec.tools)
    return frozenset(tools)


def bound_dependencies(selected: Iterable[str]) -> frozenset[str]:
    """Capabilities added solely by dependency closure (for UI hints)."""
    selected_set = frozenset(str(x).strip() for x in selected if str(x).strip())
    closed = expand_capabilities(selected_set)
    return closed - selected_set


@dataclass(frozen=True)
class EffectivePolicy:
    preset: str
    capabilities: frozenset[str]
    facts_caps: frozenset[str] = field(default_factory=frozenset)
    agent_caps: frozenset[str] = field(default_factory=frozenset)
    source: str = "default"  # table | ds | default

    def has(self, capability_id: str) -> bool:
        return capability_id in self.capabilities

    def has_agent_work(self) -> bool:
        return any(
            CAPABILITIES[c].pipe == "agent" for c in self.capabilities if c in CAPABILITIES
        )
