from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.data_training.curd.recall_query import (  # noqa: E402
    build_embedding_training_sql,
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
