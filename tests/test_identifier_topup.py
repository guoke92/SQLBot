"""T4: rejected-SQL table references drive deterministic schema expansion."""

from __future__ import annotations

import contextlib
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.steps import recall_topup as rt  # noqa: E402
from apps.protocol.sql.identifier_validation import (  # noqa: E402
    collect_sql_identifier_usage,
)

_SQL = """
SELECT p.project_name, DATE_FORMAT(t.create_time, '%Y-%m') AS month, COUNT(t.id)
FROM d_task t
JOIN d_project p ON t.project_id = p.id
JOIN d_organization o ON p.organization_id = o.id
WHERE o.organization_name = '研发二部'
GROUP BY p.project_name, month
"""


def test_sql_tables_extraction_finds_outside_reference() -> None:
    usage = collect_sql_identifier_usage(_SQL, "mysql")
    assert {"d_task", "d_project", "d_organization"} <= usage.physical_tables

    working = {"d_task", "d_project"}
    outside = usage.physical_tables - working
    assert outside == {"d_organization"}


def test_unauthorized_table_signal_pulls_catalog_table(monkeypatch) -> None:
    """模型按地图写了正确 join 但表不在召回窗口 → 解析器补齐, 修复轮拿到完整 schema."""
    catalog = {
        name: rt._CatalogTable(table_id=tid, name=name, comment="")
        for name, tid in {
            "d_task": 1,
            "d_project": 2,
            "d_organization": 3,
        }.items()
    }
    monkeypatch.setattr(rt, "_catalog", lambda session, *, ds_id: catalog)
    monkeypatch.setattr(rt, "_match_knowledge_units", lambda *args, **kwargs: [])
    monkeypatch.setattr(rt, "_relation_neighbors", lambda *args, **kwargs: [])
    monkeypatch.setattr(rt, "match_values", lambda *args, **kwargs: [])

    service = SimpleNamespace(
        table_name_list=["d_task", "d_project"],
        ds=SimpleNamespace(id=8),
        current_user=None,
        record=SimpleNamespace(id=1),
        out_ds_instance=None,
        retrieval_question="研发二部每月task数",
        protocol=None,
        chat_question=SimpleNamespace(db_schema="old", sample_data=""),
    )
    usage = collect_sql_identifier_usage(_SQL, "mysql")
    outside = tuple(sorted(usage.physical_tables - set(service.table_name_list)))
    assert outside == ("d_organization",)

    manifest = rt.resolve_recall_topup(
        object(),
        service,
        rt.TopupSignals(unauthorized_tables=outside),
        oid=1,
    )
    assert manifest.tables == ("d_organization",)

    protocol_calls: list[list[str]] = []

    def fake_retrieve_schema(**kwargs):
        names = list(kwargs["resource_names"])
        protocol_calls.append(names)
        return SimpleNamespace(
            schema_text="S " + ",".join(names),
            resource_names=names,
            sample_data="",
        )

    service.protocol = SimpleNamespace(retrieve_schema=fake_retrieve_schema)
    result = rt.fulfill_recall_topup(object(), service, manifest, audit=False)

    assert result.changed is True
    assert protocol_calls == [["d_task", "d_project", "d_organization"]]
    assert service.table_name_list == ["d_task", "d_project", "d_organization"]


def test_unknown_table_reference_reports_miss(monkeypatch) -> None:
    """SQL 引用的表不在目录（幻觉）→ 不扩表, misses 留痕供遥测."""
    catalog = {"d_task": rt._CatalogTable(table_id=1, name="d_task", comment="")}
    monkeypatch.setattr(rt, "_catalog", lambda session, *, ds_id: catalog)
    monkeypatch.setattr(rt, "_match_knowledge_units", lambda *args, **kwargs: [])
    monkeypatch.setattr(rt, "_relation_neighbors", lambda *args, **kwargs: [])
    monkeypatch.setattr(rt, "match_values", lambda *args, **kwargs: [])

    service = SimpleNamespace(table_name_list=["d_task"], ds=SimpleNamespace(id=8))
    manifest = rt.resolve_recall_topup(
        object(),
        service,
        rt.TopupSignals(unauthorized_tables=("hallucinated_table",)),
        oid=1,
    )
    assert manifest.tables == ()
    assert manifest.has_additions is False


# ── T4 致命判定契约：策略在节点, 事实由 _topup_on_failed_gates 裁决 ──────────────


class _ExpansionSession:
    def __init__(self):
        self.runs = {}
        self.events = []

    def get(self, model, key):
        return self.runs.get(key)

    def add(self, obj):
        pass

    def commit(self):
        pass


def _wire_failed_gates(
    monkeypatch, *, enabled=True, expandable=frozenset({"d_organization"})
):
    """Monkeypatch nlq internals; fake _run_topup admits only `expandable`."""
    from apps.chat.graphs.nodes import nlq

    session = _ExpansionSession()
    service = SimpleNamespace(
        table_name_list=["d_task", "d_project"],
        ds=SimpleNamespace(id=8),
        record=SimpleNamespace(id=408),
        current_user=None,
        out_ds_instance=None,
        retrieval_question="研发二部每月task数",
        protocol=None,
        chat_question=SimpleNamespace(db_schema="s", sample_data=""),
    )
    for _patch_target in (nlq, nlq.topup, nlq.context, nlq.planning, nlq.routing):
        monkeypatch.setattr(_patch_target, "topup_enabled_for",
lambda ds_id: enabled)
    for _patch_target in (nlq, nlq.quality, nlq.topup, nlq.planning, nlq.execution):
        monkeypatch.setattr(_patch_target, "_sql_dialect",
lambda svc: "mysql")
    for _patch_target in (nlq, nlq.context, nlq.topup, nlq.routing, nlq.planning, nlq.execution, nlq.presentation, nlq.analysis, nlq.audit):
        monkeypatch.setattr(_patch_target, "session_scope",
lambda: contextlib.nullcontext(session))

    calls: list[tuple[str, ...]] = []

    def fake_run_topup(_state, llm_service, *, signals, **_kwargs):
        calls.append(tuple(signals.unauthorized_tables))
        for name in signals.unauthorized_tables:
            if name in expandable:
                llm_service.table_name_list.append(name)
        return SimpleNamespace(
            changed=bool(expandable & set(signals.unauthorized_tables)),
            manifest=None,
            notice={},
            wiki_context={},
        )

    for _patch_target in (nlq, nlq.topup, nlq.context, nlq.planning):
        monkeypatch.setattr(_patch_target, "_run_topup",
fake_run_topup)
    return nlq, service, calls


def test_failed_gates_catalog_table_expansion_clears_uncovered(monkeypatch) -> None:
    """chatId=141 场景：地图可见表被拒 → 扩表后 uncovered 清空 → 走修复而非致命."""
    nlq, service, calls = _wire_failed_gates(monkeypatch)
    plan = {
        "sql": _SQL,
        "hard_gate_status": "failed",
        "hard_gate_code": "ACCESS_POLICY_VIOLATION",
    }

    result = nlq._topup_on_failed_gates({"run_id": "r1"}, service, [plan])

    assert result.uncovered == frozenset()
    assert result.undetermined is False
    assert result.expanded is True
    assert calls == [("d_organization",)]
    assert "d_organization" in service.table_name_list


def test_failed_gates_hallucinated_table_stays_fatal(monkeypatch) -> None:
    nlq, service, calls = _wire_failed_gates(monkeypatch)
    sql = "SELECT * FROM hallucinated_table WHERE x = 1"
    plan = {
        "sql": sql,
        "hard_gate_status": "failed",
        "hard_gate_code": "ACCESS_POLICY_VIOLATION",
    }

    result = nlq._topup_on_failed_gates({"run_id": "r1"}, service, [plan])

    assert result.uncovered == frozenset({"hallucinated_table"})
    assert result.undetermined is False
    assert result.expanded is False


def test_failed_gates_disabled_keeps_legacy_fatal_facts(monkeypatch) -> None:
    nlq, service, calls = _wire_failed_gates(monkeypatch, enabled=False)
    plan = {
        "sql": _SQL,
        "hard_gate_status": "failed",
        "hard_gate_code": "ACCESS_POLICY_VIOLATION",
    }

    result = nlq._topup_on_failed_gates({"run_id": "r1"}, service, [plan])

    assert result.uncovered == frozenset({"d_organization"})  # 未扩表 → 致命保留
    assert result.expanded is False
    assert calls == []  # 禁用时不做任何扩表
    assert "d_organization" not in service.table_name_list


def test_failed_gates_non_sql_violation_is_undetermined(monkeypatch) -> None:
    nlq, service, _calls = _wire_failed_gates(monkeypatch)
    plan = {
        "sql": None,
        "request": {"path": "/x"},
        "hard_gate_status": "failed",
        "hard_gate_code": "ACCESS_POLICY_VIOLATION",
    }

    result = nlq._topup_on_failed_gates({"run_id": "r1"}, service, [plan])
    assert result.undetermined is True  # 无法裁决 → 默认致命（保持 REST 语义）
    assert result.expanded is False


def test_persist_query_decision_preserves_topup_telemetry() -> None:
    from apps.conversation.run_service import _merged_agent_decision

    previous = {"decision": "ready", "queries": [], "topup": [{"source": "question"}]}
    merged = _merged_agent_decision(
        previous, {"decision": "unsupported", "message": "m"}
    )
    assert merged["decision"] == "unsupported"  # 模型决策整体替换
    assert "queries" not in merged
    assert merged["topup"] == [{"source": "question"}]  # 服务端键存活

    assert _merged_agent_decision(None, {"decision": "ready"}) == {"decision": "ready"}
    assert _merged_agent_decision({"other": 1}, {"decision": "ready"}) == {
        "decision": "ready"
    }


# ── 节点级：扩表后门禁错误必须刷新（chatId=142 场景锁定） ────────────────────────


class _SpanStub:
    def set_usage(self, *a, **k):
        pass

    def set_detail(self, *a, **k):
        pass

    def set_model_calls(self, *a, **k):
        pass

    def __setitem__(self, key, value):
        pass


class _ChainedExec:
    def all(self):
        return []

    def scalars(self):
        return self

    def one_or_none(self):
        return None


def _wire_plan_query(monkeypatch, *, revalidated_plans):
    import datetime
    from unittest.mock import Mock

    from apps.chat.graphs.nodes import nlq
    from apps.chat.semantic_planning import QueryDescription, Ready

    service = SimpleNamespace(
        table_name_list=["d_task", "d_project"],
        ds=SimpleNamespace(id=8),
        record=SimpleNamespace(id=410),
        current_user=None,
        out_ds_instance=None,
        retrieval_question="研发二部每月task数",
        compiled_knowledge=None,
        chat_question=SimpleNamespace(
            db_schema="s",
            sample_data="",
            ai_modal_id=None,
            ai_modal_name="m",
            question="q",
        ),
    )
    snapshot = SimpleNamespace(
        entity_bindings={},
        temporal_parse={},
        compiled_knowledge={},
        resources=["d_task"],
        fingerprint="f",
        schema_fingerprint="sf",
        truncation=[],
    )
    session = _ExpansionSession()
    session.exec = lambda stmt: _ChainedExec()
    session.runs["r1"] = SimpleNamespace(planning_context={"v": 2})
    persisted: list[dict] = []

    for _patch_target in (nlq, nlq.context, nlq.topup, nlq.routing, nlq.planning, nlq.execution, nlq.presentation, nlq.analysis):
        monkeypatch.setattr(_patch_target, "_llm_service",
lambda state: service)
    monkeypatch.setattr(
        nlq.StreamSink, "from_state", classmethod(lambda _c, _s: Mock())
    )
    for _patch_target in (nlq, nlq.context, nlq.topup, nlq.routing, nlq.planning, nlq.execution, nlq.presentation, nlq.analysis, nlq.audit):
        monkeypatch.setattr(_patch_target, "session_scope",
lambda: contextlib.nullcontext(session))
    for _patch_target in (nlq, nlq.context, nlq.routing, nlq.planning, nlq.execution, nlq.presentation):
        monkeypatch.setattr(_patch_target, "require_active_run",
lambda s, rid: SimpleNamespace(
            business_now=datetime.datetime(2026, 8, 25, 12), timezone="Asia/Shanghai"
        ),
    )
    for _patch_target in (nlq, nlq.planning):
        monkeypatch.setattr(_patch_target, "active_evidence",
lambda s, rid: [])
    for _patch_target in (nlq, nlq.context, nlq.planning):
        monkeypatch.setattr(_patch_target, "restore_planning_context",
lambda svc, payload: snapshot)
    span_titles: list[str] = []

    def fake_log_span(**kw):
        span_titles.append(str(kw.get("title_key") or ""))
        return contextlib.nullcontext(_SpanStub())

    for _patch_target in (nlq, nlq.context, nlq.topup, nlq.routing, nlq.planning, nlq.execution, nlq.presentation, nlq.analysis):
        monkeypatch.setattr(_patch_target, "log_span",
fake_log_span)
    for _patch_target in (nlq, nlq.topup, nlq.context, nlq.planning, nlq.routing):
        monkeypatch.setattr(_patch_target, "topup_enabled_for",
lambda ds_id: True)
    for _patch_target in (nlq, nlq.context, nlq.planning):
        monkeypatch.setattr(_patch_target, "render_schema_map",
lambda *a, **k: "")
    for _patch_target in (nlq, nlq.context):
        monkeypatch.setattr(_patch_target, "render_knowledge_map",
lambda *a, **k: "")
    for _patch_target in (nlq, nlq.context, nlq.topup, nlq.planning, nlq.presentation, nlq.audit):
        monkeypatch.setattr(_patch_target, "_ds_scope",
lambda svc: (1, 8))
    for _patch_target in (nlq, nlq.context, nlq.topup, nlq.planning, nlq.execution):
        monkeypatch.setattr(_patch_target, "_access_scope",
lambda state: None)
    for _patch_target in (nlq, nlq.quality, nlq.topup, nlq.planning, nlq.execution):
        monkeypatch.setattr(_patch_target, "_sql_dialect",
lambda svc: "mysql")
    for _patch_target in (nlq, nlq.execution, nlq.planning):
        monkeypatch.setattr(_patch_target, "persist_query_decision",
lambda sess, **kw: persisted.append(kw)
        )

    decision = Ready(queries=[QueryDescription(description="d", sql=_SQL)])
    stale_plan = {
        "plan_id": "p1",
        "sql": _SQL,
        "hard_gate_status": "failed",
        "hard_gate_code": "ACCESS_POLICY_VIOLATION",
        "hard_gate_errors": ["SQL contains unauthorized tables: d_organization."],
    }

    def fake_agent(_llm_service, **_kwargs):
        return SimpleNamespace(
            decision=decision,
            plans=[stale_plan],
            usage={},
            reasoning="",
            model_calls=[{"elapsed_ms": 100}],
        )

    for _patch_target in (nlq, nlq.planning, nlq.execution):
        monkeypatch.setattr(_patch_target, "run_query_agent",
fake_agent)

    def fake_topup(_state, llm_service, _plans):
        # 忠实模拟：表已在窗口内时第二轮扩表无事可做（expanded=False → 收敛）
        if "d_organization" in llm_service.table_name_list:
            return nlq._GateExpansion(frozenset(), False, False)
        llm_service.table_name_list.append("d_organization")
        return nlq._GateExpansion(frozenset(), False, True)

    for _patch_target in (nlq, nlq.topup, nlq.planning):
        monkeypatch.setattr(_patch_target, "_topup_on_failed_gates",
fake_topup)

    fingerprints: list[str] = []

    def fake_revalidate(_llm_service, **kwargs):
        fingerprints.append(kwargs["schema_fingerprint"])
        return [dict(item) for item in revalidated_plans]

    for _patch_target in (nlq, nlq.execution, nlq.planning):
        monkeypatch.setattr(_patch_target, "revalidate_query_plans",
fake_revalidate)
    return nlq, persisted, fingerprints, span_titles


def test_plan_query_refreshes_gate_errors_after_expansion(monkeypatch) -> None:
    """扩表后旧 unauthorized 错误必须被重校验的新错误替换, 绝不进修复提示."""
    fresh_plan = {
        "plan_id": "p2",
        "sql": _SQL,
        "hard_gate_status": "failed",
        "hard_gate_code": "UNKNOWN_IDENTIFIER",
        "hard_gate_errors": ["unknown column o.name — catalog: organization_name"],
    }
    nlq, persisted, fingerprints, span_titles = _wire_plan_query(
        monkeypatch, revalidated_plans=[fresh_plan]
    )

    result = nlq.plan_query_node(
        {"run_id": "r1", "entity_bindings": {}, "temporal_parse": {}}
    )

    assert fingerprints == ["sf"]  # 用扩展后快照的指纹重校验
    assert "unauthorized" not in result["repair_hint"]
    assert "organization_name" in result["repair_hint"]  # 修复器看到新鲜列名错误
    assert result["repair_source_plans"][0]["plan_id"] == "p2"
    assert persisted[-1]["planning_status"] == "repairing"
    assert persisted[-1]["hard_gate_report"]["plans"][0]["code"] == "UNKNOWN_IDENTIFIER"


def test_plan_query_skips_repair_when_revalidation_passes(monkeypatch) -> None:
    """重校验全通过 → 直接进成功路径（省一次修复轮 LLM 调用）."""
    passing_plan = {"plan_id": "p2", "sql": _SQL, "hard_gate_status": "passed"}
    nlq, persisted, fingerprints, _span_titles = _wire_plan_query(
        monkeypatch, revalidated_plans=[passing_plan]
    )

    result = nlq.plan_query_node(
        {"run_id": "r1", "entity_bindings": {}, "temporal_parse": {}}
    )

    assert fingerprints == ["sf"]
    assert result["planning_decision"] == "ready"
    assert result["repair_hint"] == ""
    assert result["active_candidate"]["plans"][0]["plan_id"] == "p2"
    assert persisted[-1]["planning_status"] == "reviewing"
    assert persisted[-1]["hard_gate_report"]["status"] == "passed"


def test_hard_fatal_codes_skip_expansion_entirely(monkeypatch) -> None:
    """NON_READ_ONLY/PROTOCOL_UNSUPPORTED 无条件致命 — 不做扩表与快照写库."""
    nlq, persisted, fingerprints, _span_titles = _wire_plan_query(
        monkeypatch, revalidated_plans=[]
    )
    topup_calls: list[Any] = []
    original_topup = nlq._topup_on_failed_gates

    def counting_topup(state, llm_service, plans):
        topup_calls.append(plans)
        return original_topup(state, llm_service, plans)

    for _patch_target in (nlq, nlq.topup, nlq.planning):
        monkeypatch.setattr(_patch_target, "_topup_on_failed_gates",
counting_topup)
    # 覆写 agent 产物为非只读违规
    from apps.chat.semantic_planning import QueryDescription, Ready

    def _patched_value_481(*a, **k):
            return SimpleNamespace(
            decision=Ready(
                queries=[QueryDescription(description="d", sql="DELETE FROM d_task")]
            ),
            plans=[
                {
                    "plan_id": "p1",
                    "sql": "DELETE FROM d_task",
                    "hard_gate_status": "failed",
                    "hard_gate_code": "NON_READ_ONLY_PLAN",
                    "hard_gate_errors": ["non read-only statement"],
                }
            ],
            usage={},
            reasoning="",
            model_calls=[{"elapsed_ms": 1}],
        )
    for _patch_target in (nlq, nlq.planning, nlq.execution):
        monkeypatch.setattr(_patch_target, "run_query_agent", _patched_value_481)

    result = nlq.plan_query_node(
        {"run_id": "r1", "entity_bindings": {}, "temporal_parse": {}}
    )

    assert topup_calls == []  # 未做任何扩表
    assert result.get("error")  # 走 _fail 终局
    assert "安全、权限或协议门禁" in str(
        result.get("public_error") or result.get("error")
    )
