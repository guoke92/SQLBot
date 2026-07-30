from __future__ import annotations

from typing import Literal

TrainingScope = Literal["datasource", "advanced_application"]

_TRAINING_SCOPES: tuple[TrainingScope, ...] = (
    "datasource",
    "advanced_application",
)


def build_embedding_training_sql(
    scope: TrainingScope,
    *,
    filter_by_training_type: bool,
    similarity_threshold: float,
    top_count: int,
) -> str:
    """Build the vector-recall query shared by all data-training scopes."""
    if scope not in _TRAINING_SCOPES:
        raise ValueError(f"Unsupported data-training scope: {scope}")
    if not 0 <= similarity_threshold <= 1:
        raise ValueError("Similarity threshold must be between 0 and 1")
    if top_count <= 0:
        raise ValueError("Top count must be positive")

    training_type_filter = (
        "AND child.training_type = :training_type"
        if filter_by_training_type
        else ""
    )
    return f"""
SELECT candidate.id, candidate.question, candidate.similarity
FROM (
    SELECT
        child.id,
        child.question,
        (1 - (child.embedding <=> :embedding_array)) AS similarity
    FROM data_training AS child
    WHERE child.oid = :oid
      AND child.{scope} = :scope_value
      AND child.enabled IS TRUE
      AND child.embedding IS NOT NULL
      {training_type_filter}
) AS candidate
WHERE candidate.similarity > {similarity_threshold}
ORDER BY candidate.similarity DESC
LIMIT {top_count}
"""
