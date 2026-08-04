# Author: Junjun
# Date: 2025/9/23
import json
import time
from typing import Any

from apps.ai_model.embedding import EmbeddingModelCache, has_compatible_dimension
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
        model = EmbeddingModelCache.get_model()
        query_embedding = model.embed_query(normalized_question)
        incompatible = 0
        for candidate in candidates:
            raw_embedding = candidate.get("embedding")
            if not raw_embedding:
                continue
            stored_embedding = json.loads(raw_embedding)
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

        candidates.sort(
            key=lambda item: float(item["cosine_similarity"]),
            reverse=True,
        )
        selected = candidates[: settings.TABLE_EMBEDDING_COUNT]
        SQLBotLogUtil.info(
            "Table embedding recall selected %s/%s table(s) in %.3fs",
            len(selected),
            len(candidates),
            time.monotonic() - started_at,
        )
        return selected
    except Exception:
        SQLBotLogUtil.exception("Table embedding recall failed")
        return candidates
