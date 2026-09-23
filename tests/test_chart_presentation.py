"""Tests for delivery chart_type gates and resolve path."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from apps.chat.chart_presentation import (  # noqa: E402
    resolve_delivery_chart,
    validate_chart_type,
)
from apps.chat.presentation import build_result_presentation  # noqa: E402


def _pres(fields: list[str], title: str = "t"):
    return build_result_presentation(fields, title=title)


def test_validate_rejects_line_without_measure() -> None:
    fields = ["id", "name", "create_time"]
    rows = [
        {"id": 1946025846161575938, "name": "甲", "create_time": "2025-01-01"},
        {"id": 2100000000000000000, "name": "乙", "create_time": "2025-02-01"},
    ]
    ok, reason = validate_chart_type("line", fields, rows)
    assert ok is False
    assert reason == "no_measure"


def test_validate_accepts_line_with_temporal_measure() -> None:
    fields = ["month_label", "qty"]
    rows = [
        {"month_label": "2024-01-01", "qty": 1},
        {"month_label": "2024-02-01", "qty": 2},
    ]
    ok, reason = validate_chart_type("line", fields, rows)
    assert ok is True
    assert reason == ""


def test_resolve_uses_suggested_table_for_entity_list() -> None:
    fields = ["id", "name", "create_time"]
    rows = [
        {"id": 1946025846161575938, "name": "甲", "create_time": "2025-01-01"},
        {"id": 2100000000000000000, "name": "乙", "create_time": "2025-02-01"},
        {"id": 1750000000000000000, "name": "丙", "create_time": "2025-03-01"},
    ]
    chart = resolve_delivery_chart(
        presentation=_pres(fields, "企业清单"),
        fields=fields,
        rows=rows,
        suggested_type="table",
    )
    assert chart["type"] == "table"


def test_resolve_wrong_line_falls_back_to_table_without_llm() -> None:
    fields = ["id", "name", "create_time"]
    rows = [
        {"id": 1946025846161575938, "name": "甲", "create_time": "2025-01-01"},
        {"id": 2100000000000000000, "name": "乙", "create_time": "2025-02-01"},
        {"id": 1750000000000000000, "name": "丙", "create_time": "2025-03-01"},
    ]
    chart = resolve_delivery_chart(
        presentation=_pres(fields, "企业清单"),
        fields=fields,
        rows=rows,
        suggested_type="line",
        llm_service=None,
    )
    assert chart["type"] == "table"


def test_resolve_adopts_valid_bar() -> None:
    fields = ["dept", "cnt"]
    rows = [{"dept": "A", "cnt": 3}, {"dept": "B", "cnt": 5}]
    chart = resolve_delivery_chart(
        presentation=_pres(fields),
        fields=fields,
        rows=rows,
        suggested_type="bar",
    )
    assert chart["type"] == "bar"
    assert chart["axis"]["x"]["value"] == "dept"
    assert chart["axis"]["y"]["value"] == "cnt"


def test_resolve_narrow_llm_success() -> None:
    fields = ["dept", "cnt"]
    rows = [{"dept": "A", "cnt": 3}, {"dept": "B", "cnt": 5}]

    class _Resp:
        content = '{"type":"bar","title":"t","axis":{"x":{"name":"部门","value":"dept"},"y":{"name":"数量","value":"cnt"}}}'

    class _LLM:
        def invoke(self, _messages):  # noqa: ANN001
            return _Resp()

    chart = resolve_delivery_chart(
        presentation=_pres(fields),
        fields=fields,
        rows=rows,
        # pie fails row/category gates? 2 rows with cat+measure actually passes pie.
        # Force failure with line (no temporal).
        suggested_type="line",
        llm_service=SimpleNamespace(llm=_LLM()),
    )
    assert chart["type"] == "bar"
    assert chart["axis"]["x"]["value"] == "dept"


def test_execute_sql_defaults_delivery_chart_type_table(monkeypatch) -> None:  # noqa: ANN001
    from apps.chat.tools import execute_sql as mod

    class _QR:
        data = [{"a": 1}]
        fields = ["a"]
        truncated = False

    class _Plan:
        success = True
        statement = "SELECT 1"
        message = ""

    class _Proto:
        def parse_candidate_payload(self, _payload):  # noqa: ANN001
            return _Plan()

        def validate_plan(self, *_a, **_k):  # noqa: ANN001
            return _Plan()

        def execute(self, *_a, **_k):  # noqa: ANN001
            return _QR()

    captured: dict = {}

    def _upsert(**kwargs):  # noqa: ANN001
        captured.update(kwargs)

    monkeypatch.setattr(mod, "upsert_result_dataset", _upsert)
    monkeypatch.setattr(mod, "current_worker_identity", lambda: ("run1", None))
    monkeypatch.setattr(mod, "_reject_enum_discovery", lambda *_a, **_k: None)
    monkeypatch.setattr(mod, "_consume_probe_budget", lambda *_a, **_k: None)
    monkeypatch.setattr(
        mod,
        "apply_wiki_enum_labels",
        lambda **_k: (_QR.data, {}),
    )
    monkeypatch.setattr(mod, "apply_result_window", lambda **_k: (False, None))
    monkeypatch.setattr(mod, "resolve_exec_row_limit", lambda *_a, **_k: 1000)

    llm = SimpleNamespace(protocol=_Proto(), ds=SimpleNamespace(id=1, type="mysql"))
    res = mod.execute_sql_sandbox(llm, "SELECT 1", required=True)
    assert res.get("ok") is True
    assert res["data"]["chart_type"] == "table"
    assert captured.get("chart_type") == "table"

    res2 = mod.execute_sql_sandbox(
        llm, "SELECT 1", required=False, chart_type="line"
    )
    assert res2.get("ok") is True
    assert "chart_type" not in (res2.get("data") or {})
