from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.ai_model.embedding import (  # noqa: E402
    embedding_query_params,
    has_compatible_dimension,
)
from apps.data_training.curd.recall_query import (  # noqa: E402
    build_embedding_training_sql,
)
from apps.datasource.crud.table import _needs_embedding_refresh  # noqa: E402
from apps.datasource.embedding.table_embedding import (  # noqa: E402
    calc_table_embedding,
)


@pytest.mark.parametrize("scope", ["datasource", "advanced_application"])
def test_embedding_training_query_uses_one_scoped_filter(scope: str) -> None:
    sql = build_embedding_training_sql(
        scope,  # type: ignore[arg-type]
        filter_by_training_type=False,
        similarity_threshold=0.7,
        top_count=5,
    )

    assert f"child.{scope} = :scope_value" in sql
    assert "vector_dims(child.embedding) = :embedding_dimension" in sql
    assert "child.training_type" not in sql
    assert ".replace(" not in sql


@pytest.mark.parametrize("scope", ["datasource", "advanced_application"])
def test_embedding_training_query_filters_type_inside_candidate_scope(
    scope: str,
) -> None:
    sql = build_embedding_training_sql(
        scope,  # type: ignore[arg-type]
        filter_by_training_type=True,
        similarity_threshold=0.7,
        top_count=5,
    )

    inner_query, outer_query = sql.split(") AS candidate", maxsplit=1)
    assert "child.training_type = :training_type" in inner_query
    assert "training_type" not in outer_query


def test_embedding_training_query_rejects_unknown_scope() -> None:
    with pytest.raises(ValueError, match="Unsupported data-training scope"):
        build_embedding_training_sql(
            "custom_scope",  # type: ignore[arg-type]
            filter_by_training_type=False,
            similarity_threshold=0.7,
            top_count=5,
        )


def test_embedding_dimension_contract_is_shared_by_query_and_memory_recall() -> None:
    params = embedding_query_params([0.1, 0.2, 0.3])

    assert params["embedding_dimension"] == 3
    assert has_compatible_dimension([0.1, 0.2], [0.3, 0.4])
    assert not has_compatible_dimension([0.1, 0.2], [0.3])


@pytest.mark.parametrize(
    ("stored", "dimension", "expected"),
    [
        (None, 3, True),
        ("", 3, True),
        ("not-json", 3, True),
        ('{"unexpected": true}', 3, True),
        ("[0.1, 0.2]", 3, True),
        ("[0.1, 0.2, 0.3]", 3, False),
    ],
)
def test_schema_embeddings_are_refreshed_when_dimension_is_stale(
    stored: str | None,
    dimension: int,
    expected: bool,
) -> None:
    assert _needs_embedding_refresh(stored, dimension) is expected


def test_empty_retrieval_question_skips_table_embedding_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_if_called(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("embedding model must not be called for an empty question")

    monkeypatch.setattr(
        "apps.datasource.embedding.table_embedding.EmbeddingModelCache.get_model",
        fail_if_called,
    )
    tables = [
        {
            "id": 1,
            "table_name": "orders",
            "schema_table": "orders(id bigint)",
            "embedding": "[0.1, 0.2]",
        }
    ]

    result = calc_table_embedding(tables, "  ")

    assert [table["id"] for table in result] == [1]
    assert result[0]["cosine_similarity"] == 0.0
