# Author: Junjun
# Date: 2025/9/23
import json
import time
from typing import Any

from apps.ai_model.embedding import EmbeddingModelCache, has_compatible_dimension
from apps.datasource.embedding.recall import select_by_similarity
from apps.datasource.embedding.utils import cosine_similarity
from common.core.config import settings
from common.utils.utils import SQLBotLogUtil


def calc_table_embedding(
    tables: list[dict[str, Any]],
    question: str,
) -> list[dict[str, Any]]:
    candidates = [
        {
            "id": table.get("id"),
            "schema_table": table.get("schema_table"),
            "embedding": table.get("embedding"),
            "cosine_similarity": 0.0,
            "table_name": table.get("table_name"),
        }
        for table in tables
    ]
    normalized_question = (question or "").strip()
    if not candidates or not normalized_question:
        return candidates

    try:
        started_at = time.monotonic()
        query_embedding = EmbeddingModelCache.embed_query(normalized_question)
        incompatible = 0
        for candidate in candidates:
            raw_embedding = candidate.get("embedding")
            if not raw_embedding:
                continue
            try:
                stored_embedding = json.loads(raw_embedding)
            except (TypeError, ValueError):
                incompatible += 1
                continue
            if not has_compatible_dimension(query_embedding, stored_embedding):
                incompatible += 1
                continue
            candidate["cosine_similarity"] = cosine_similarity(
                query_embedding,
                stored_embedding,
            )
        if incompatible:
            SQLBotLogUtil.warning(
                "Skipped %s table embedding(s) incompatible with active dimension %s",
                incompatible,
                len(query_embedding),
            )

        selected = select_by_similarity(
            candidates,
            score_of=lambda item: float(item["cosine_similarity"]),
            threshold=float(settings.EMBEDDING_TABLE_SIMILARITY),
            top_count=int(settings.TABLE_EMBEDDING_COUNT),
            has_vector=lambda item: _usable_stored_vector(
                item.get("embedding"), query_embedding
            ),
        )
        SQLBotLogUtil.info(
            "Table embedding recall selected %s/%s table(s) in %.3fs",
            len(selected),
            len(candidates),
            time.monotonic() - started_at,
        )
        return selected
    except Exception:
        SQLBotLogUtil.exception("Table embedding recall failed")
        # Never dump the whole catalog into the prompt on failure.
        return candidates[: max(1, int(settings.TABLE_EMBEDDING_COUNT))]


def _usable_stored_vector(raw_embedding: Any, query_embedding: list[float]) -> bool:
    if not raw_embedding:
        return False
    try:
        stored = json.loads(raw_embedding)
    except (TypeError, ValueError):
        return False
    return has_compatible_dimension(query_embedding, stored)
