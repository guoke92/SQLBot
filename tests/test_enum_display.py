"""Unit tests for the single wiki enum display projector."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.steps.enum_display import apply_wiki_enum_labels, enum_refs_for_query


def test_enum_refs_for_query_maps_alias_to_physical_column(monkeypatch) -> None:
    monkeypatch.setattr(
        "apps.chat.steps.enum_display.wiki_table_columns",
        lambda _table, **_kwargs: {"cust_build_type", "identify_style"},
    )
    sql = (
        "SELECT cust_build_type AS build_type, identify_style AS auth_style "
        "FROM ca_certification_info"
    )
    refs, alias_to_ref = enum_refs_for_query(
        sql=sql,
        fields=["build_type", "auth_style"],
        tables=["ca_certification_info"],
        dialect="mysql",
    )
    assert "ca_certification_info.cust_build_type" in refs
    assert "ca_certification_info.identify_style" in refs
    assert alias_to_ref["build_type"] == "ca_certification_info.cust_build_type"
    assert alias_to_ref["auth_style"] == "ca_certification_info.identify_style"


def test_apply_wiki_enum_labels_translates_and_returns_map(monkeypatch) -> None:
    monkeypatch.setattr(
        "apps.chat.steps.enum_display.enum_refs_for_query",
        lambda **_k: (
            ["t.col"],
            {"status": "t.col"},
        ),
    )
    monkeypatch.setattr(
        "apps.chat.steps.wiki_recall.enum_maps_for",
        lambda _refs, ds_id=None: {"t.col": {"AGW": "平台录入"}},
    )

    rows, labels = apply_wiki_enum_labels(
        sql="SELECT col AS status FROM t",
        fields=["status"],
        rows=[{"status": "AGW"}],
        llm_service=SimpleNamespace(protocol=SimpleNamespace(type_key="mysql"), ds=None),
    )
    assert rows == [{"status": "平台录入"}]
    assert labels == {"status": {"AGW": "平台录入"}}
