"""Schema vector space — isolated from Wiki recall."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.datasource.embedding.schema_index import (  # noqa: E402
    _pick_tables,
    field_rank_text,
    relation_rank_text,
)


def test_pick_tables_promotes_field_and_relation_hits() -> None:
    scored = [
        {"kind": "table", "table_name": "d_qa_case", "score": 0.31},
        {
            "kind": "field",
            "table_name": "d_organization",
            "score": 0.62,
        },
        {
            "kind": "relation",
            "table_name": "d_task",
            "peer_table": "d_project",
            "score": 0.55,
        },
    ]
    names = _pick_tables(scored, table_limit=4)
    assert names[0] == "d_organization"
    assert "d_task" in names
    assert "d_project" in names
    assert "d_qa_case" in names


def test_rank_text_covers_field_and_relation() -> None:
    field = type(
        "F",
        (),
        {
            "field_name": "org_id",
            "field_type": "bigint",
            "custom_comment": "所属部门",
            "field_comment": "",
        },
    )()
    assert "d_task.org_id" in field_rank_text(table_name="d_task", field=field)
    assert "所属部门" in field_rank_text(table_name="d_task", field=field)
    rel = relation_rank_text(
        source_table="d_task",
        source_field="project_id",
        target_table="d_project",
        target_field="id",
        kind="EQUI_JOIN",
    )
    assert "d_task.project_id → d_project.id" in rel


def test_recall_schema_context_uses_only_schema_vector(monkeypatch) -> None:
    """Empty schema_vector must not be patched from CoreTable.embedding."""
    from apps.datasource.embedding import schema_index as si

    assert not hasattr(si, "_table_docs_from_catalog")

    captured: dict[str, object] = {}

    class _Sess:
        pass

    def _docs(session, *, ds_id, allowed):
        captured["ds_id"] = ds_id
        return []

    def _embed_query(text: str):
        raise AssertionError("must not embed when schema_vector is empty")

    monkeypatch.setattr(si, "_docs_from_schema_vector", _docs)
    monkeypatch.setattr(si.EmbeddingModelCache, "embed_query", _embed_query)
    monkeypatch.setattr(si.settings, "TABLE_EMBEDDING_ENABLED", True)

    llm = type("L", (), {"ds": type("D", (), {"id": 8})(), "chat_question": None})()
    out = si.recall_schema_context(llm, "研发二部 task", session=_Sess())
    assert out["tables"] == []
    assert out["schema_text"] == ""
    assert out["backend"] == "schema_vector"
    assert captured["ds_id"] == 8


def test_schema_fallback_writes_chat_question_not_property(monkeypatch) -> None:
    """LLMService.retrieval_question is read-only; fallback must not assign it."""
    import apps.chat.steps.wiki_recall as wr
    import apps.datasource.embedding.schema_index as si

    calls: list[str] = []

    class _CQ:
        retrieval_question = "prior"

    class _LLM:
        ds = type("D", (), {"id": 8})()
        chat_question = _CQ()

        @property
        def retrieval_question(self) -> str:
            return self.chat_question.retrieval_question or "orig"

    def _schedule(ds_id: int | None) -> None:
        calls.append(f"schedule:{ds_id}")

    def _recall(llm: object, query: str, **_kwargs: object) -> dict:
        calls.append(f"recall:{query}:{getattr(llm, 'retrieval_question')}")
        return {
            "knowledge_text": "",
            "tables": ["d_task"],
            "schema_text": "table d_task",
            "backend": "schema_vector",
            "page_keys": [],
            "hit_count": 1,
        }

    monkeypatch.setattr(si, "schedule_schema_vector_sync", _schedule)
    monkeypatch.setattr(si, "recall_schema_context", _recall)

    llm = _LLM()
    out = wr._schema_fallback_context(llm, "研发二部 task")
    assert out["tables"] == ["d_task"]
    assert "schedule:8" in calls
    assert any(c.startswith("recall:研发二部 task:研发二部 task") for c in calls)
    assert llm.chat_question.retrieval_question == "prior"
