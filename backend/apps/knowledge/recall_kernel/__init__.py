"""Unified knowledge recall kernel (Wiki + schema_vector)."""

from apps.knowledge.recall_kernel.conflicts import (
    conflict_page_keys,
    conflicts_to_evidence,
    detect_caliber_conflicts,
    unresolved_conflicts,
)
from apps.knowledge.recall_kernel.tables import (
    expand_schema_working_set,
    resolve_schema_vector_tables,
    resolve_wiki_tables,
    trim_schema_chars,
)
from apps.knowledge.recall_kernel.types import (
    PassageHit,
    RecallBudget,
    RecallBundle,
    TableCandidate,
)

__all__ = [
    "PassageHit",
    "RecallBudget",
    "RecallBundle",
    "TableCandidate",
    "conflict_page_keys",
    "conflicts_to_evidence",
    "detect_caliber_conflicts",
    "expand_schema_working_set",
    "resolve_schema_vector_tables",
    "resolve_wiki_tables",
    "trim_schema_chars",
    "unresolved_conflicts",
]
