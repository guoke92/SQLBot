"""RANK vs PROMPT schema text and shared similarity recall helpers."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from apps.datasource.embedding.recall import select_by_similarity
from apps.datasource.embedding.table_embedding import calc_table_embedding
from apps.datasource.schema_text import SchemaTextPurpose, render_table_schema_text


class _FakeSession:
    pass


def _table(**kwargs: Any) -> SimpleNamespace:
    defaults = {
        "id": 1,
        "table_name": "orders",
        "custom_comment": "销售订单",
        "approx_rows": 1_200_000,
        "index_summary": "PRIMARY(id)",
        "active_profile_generation": 3,
        "profile_status": "READY",
        "ds_id": 9,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def _field(**kwargs: Any) -> SimpleNamespace:
    defaults = {
        "id": 11,
        "field_name": "status",
        "field_type": "varchar",
        "custom_comment": "订单状态",
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_rank_text_is_structural_only(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(*_a: object, **_k: object) -> list[Any]:
        raise AssertionError("RANK must not load field profiles")

    monkeypatch.setattr(
        "apps.datasource.profiling.service.get_active_field_profiles",
        boom,
    )
    text = render_table_schema_text(
        _FakeSession(),
        table=_table(),
        fields=[_field()],
        purpose=SchemaTextPurpose.RANK,
    )
    assert "# Table: orders" in text
    assert "销售订单" in text
    assert "status:varchar" in text
    assert "订单状态" in text
    assert "null=" not in text
    assert "topk=" not in text
    assert "profile_g=" not in text
    assert "~1200000 rows" not in text
    assert "idx:" not in text
    assert "Confirmed" not in text


def test_prompt_text_includes_profile_bits(monkeypatch: pytest.MonkeyPatch) -> None:
    snap = SimpleNamespace(
        field_id=11,
        null_rate=0.01,
        distinct_ratio=0.02,
        min_value="a",
        max_value="z",
        top_values=[{"value": "paid"}, {"value": "cancel"}],
    )
    monkeypatch.setattr(
        "apps.datasource.profiling.service.get_active_field_profiles",
        lambda *_a, **_k: [snap],
    )
    text = render_table_schema_text(
        _FakeSession(),
        table=_table(),
        fields=[_field()],
        purpose=SchemaTextPurpose.PROMPT,
    )
    assert "~1200000 rows" in text
    assert "idx: PRIMARY(id)" in text
    assert "null=0.01" in text
    assert "topk=paid|cancel" in text


def test_prompt_skips_profile_bits_when_stale(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(*_a: object, **_k: object) -> list[Any]:
        raise AssertionError("STALE must not load field profiles")

    monkeypatch.setattr(
        "apps.datasource.profiling.service.get_active_field_profiles",
        boom,
    )
    text = render_table_schema_text(
        _FakeSession(),
        table=_table(profile_status="STALE"),
        fields=[_field()],
        purpose=SchemaTextPurpose.PROMPT,
    )
    assert "null=" not in text
    assert "topk=" not in text
    assert "status:varchar" in text


def test_select_by_similarity_threshold_and_fallbacks() -> None:
    items = [
        {"id": "a", "score": 0.9, "vec": True},
        {"id": "b", "score": 0.5, "vec": True},
        {"id": "c", "score": 0.2, "vec": True},
        {"id": "d", "score": 0.0, "vec": False},
    ]
    picked = select_by_similarity(
        items,
        score_of=lambda x: float(x["score"]),
        threshold=0.4,
        top_count=2,
        has_vector=lambda x: bool(x["vec"]),
    )
    assert [x["id"] for x in picked] == ["a", "b"]

    weak = select_by_similarity(
        [{"id": "x", "score": 0.1, "vec": True}],
        score_of=lambda x: float(x["score"]),
        threshold=0.4,
        top_count=3,
        has_vector=lambda x: bool(x["vec"]),
    )
    assert [x["id"] for x in weak] == ["x"]

    no_vec = select_by_similarity(
        [{"id": "1"}, {"id": "2"}, {"id": "3"}],
        score_of=lambda _x: 0.0,
        threshold=0.4,
        top_count=2,
        has_vector=lambda _x: False,
    )
    assert [x["id"] for x in no_vec] == ["1", "2"]


def test_table_recall_failure_does_not_dump_catalog(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def boom(*_a: object, **_k: object) -> None:
        raise RuntimeError("model down")

    monkeypatch.setattr(
        "apps.datasource.embedding.table_embedding.EmbeddingModelCache.get_model",
        boom,
    )
    from common.core.config import settings as app_settings

    monkeypatch.setattr(app_settings, "TABLE_EMBEDDING_COUNT", 2)
    tables = [
        {"id": i, "table_name": f"t{i}", "schema_table": f"t{i}", "embedding": "[0.1]"}
        for i in range(5)
    ]
    result = calc_table_embedding(tables, "订单")
    assert len(result) == 2
    assert [t["id"] for t in result] == [0, 1]
