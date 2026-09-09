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


def test_execute_sql_probe_keeps_raw_enum_codes(monkeypatch) -> None:
    """Probes must not translate enums in tool samples or result_dataset rows."""
    from apps.chat.tools import execute_sql as mod

    class _QR:
        data = [
            {"pay_status": None, "cnt": 7},
            {"pay_status": "PAID", "cnt": 14},
            {"pay_status": "UNPAID", "cnt": 284},
        ]
        fields = ["pay_status", "cnt"]
        truncated = False

    class _Plan:
        success = True
        statement = "SELECT pay_status, COUNT(*) AS cnt FROM ca_fee_company GROUP BY pay_status"
        message = ""
        payload = {"sql": statement}

    class _Proto:
        def parse_candidate_payload(self, _payload):  # noqa: ANN001
            return _Plan()

        def execute(self, *_a, **_k):  # noqa: ANN001
            return _QR()

        def format_statement_for_display(self, plan):  # noqa: ANN001
            return plan.statement

    captured: dict = {}
    label_calls = {"n": 0}

    def _upsert(**kwargs):  # noqa: ANN001
        captured.update(kwargs)

    def _label(**kwargs):  # noqa: ANN001
        label_calls["n"] += 1
        return (
            [
                {"pay_status": None, "cnt": 7},
                {"pay_status": "已缴费", "cnt": 14},
                {"pay_status": "未缴费", "cnt": 284},
            ],
            {"pay_status": {"PAID": "已缴费", "UNPAID": "未缴费"}},
        )

    monkeypatch.setattr(mod, "upsert_result_dataset", _upsert)
    monkeypatch.setattr(mod, "current_worker_identity", lambda: ("run-probe-enum", None))
    monkeypatch.setattr(mod, "_schema_ready", lambda: None)
    monkeypatch.setattr(mod, "_reject_enum_discovery", lambda *_a, **_k: None)
    monkeypatch.setattr(mod, "_consume_probe_budget", lambda *_a, **_k: None)
    monkeypatch.setattr(mod, "apply_wiki_enum_labels", _label)
    monkeypatch.setattr(mod, "apply_result_window", lambda **_k: (False, None))
    monkeypatch.setattr(mod, "resolve_exec_row_limit", lambda *_a, **_k: 1000)

    llm = SimpleNamespace(protocol=_Proto(), ds=SimpleNamespace(id=15, type="mysql"))
    res = mod.execute_sql_sandbox(
        llm,
        "SELECT pay_status, COUNT(*) AS cnt FROM ca_fee_company GROUP BY pay_status",
        required=False,
    )
    assert res.get("ok") is True
    assert label_calls["n"] == 0
    samples = res["data"]["sample_rows"]
    assert samples[1]["pay_status"] == "PAID"
    assert samples[2]["pay_status"] == "UNPAID"
    assert "value_labels" not in res["data"]
    assert captured["rows"][1]["pay_status"] == "PAID"
    assert not captured.get("value_labels")

    # Delivery still projects labels into the row store for UI, but tool samples stay raw.
    captured.clear()
    label_calls["n"] = 0
    res2 = mod.execute_sql_sandbox(
        llm,
        "SELECT pay_status, COUNT(*) AS cnt FROM ca_fee_company GROUP BY pay_status",
        required=True,
        result_title="缴费分布",
        chart_type="table",
    )
    assert res2.get("ok") is True
    assert label_calls["n"] == 1
    assert res2["data"]["sample_rows"][1]["pay_status"] == "PAID"
    assert res2["data"]["value_labels"]["pay_status"]["PAID"] == "已缴费"
    assert captured["rows"][1]["pay_status"] == "已缴费"
