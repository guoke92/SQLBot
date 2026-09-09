"""Unified knowledge recall kernel (Wiki + schema_vector)."""

from apps.knowledge.recall_kernel.tables import (
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
    "resolve_schema_vector_tables",
    "resolve_wiki_tables",
    "trim_schema_chars",
]
