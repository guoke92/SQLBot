from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.planning_context import (  # noqa: E402
    _split_knowledge_payload,
    capture_planning_context,
    execution_schema_resources,
    restore_planning_context,
)


def _service(schema: str = "# Table: orders\n(id:int)") -> SimpleNamespace:
    return SimpleNamespace(
        table_name_list=["orders"],
        compiled_knowledge=None,
        chat_question=SimpleNamespace(
            db_schema=schema,
            sample_data="sample",
            terminologies="terms",
            data_training="examples",
            custom_prompt="rules",
        ),
    )


def test_planning_context_round_trips_request_local_retrieval() -> None:
    source = _service()
    snapshot = capture_planning_context(
        source,
        entity_bindings={"研发二部": {"canonical": "研发二部"}},
        temporal_parse={"start": "2026-01-01"},
    )
    restored = _service("")
    restored.table_name_list = []

    result = restore_planning_context(restored, snapshot.model_dump(mode="json"))

    assert result.usable is True
    assert restored.chat_question.db_schema == source.chat_question.db_schema
    assert restored.table_name_list == ["orders"]
    assert result.entity_bindings["研发二部"]["canonical"] == "研发二部"


def test_empty_planning_context_cannot_reach_planner() -> None:
    with pytest.raises(ValueError, match="usable schema"):
        restore_planning_context(
            _service(""),
            {
                "version": 2,
                "schema_text": "",
                "resources": [],
                "fingerprint": "empty",
            },
        )


def test_planning_context_omits_matches_and_log_items() -> None:
    pytest.skip("Retired legacy unit compilation test")

