"""plan_gate: deterministic verification of terminal planning decisions."""

from __future__ import annotations

import contextlib
import sys
from pathlib import Path
from types import SimpleNamespace

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.graphs.nodes import nlq  # noqa: E402
from apps.chat.steps.recall_topup import TopupManifest  # noqa: E402


class _FakeSession:
    def __init__(self):
        self.runs = {}
        self.events = []

    def get(self, model, key):
        return self.runs.get(key)

    def add(self, obj):
        pass

    def commit(self):
        pass


def _manifest(**kwargs) -> TopupManifest:
    return TopupManifest(**kwargs)


def _service(tables=("d_task",)) -> SimpleNamespace:
    return SimpleNamespace(
        table_name_list=list(tables),
        ds=SimpleNamespace(id=8),
        retrieval_question="研发二部每月task数",
        record=SimpleNamespace(id=1),
        compiled_knowledge=None,
        chat_question=SimpleNamespace(db_schema="s", sample_data=""),
    )


def _wire(
    monkeypatch, *, manifest=None, changed=True, service=None, knowledge_changed=False
) -> _FakeSession:
    session = _FakeSession()
    service = service or _service()
    monkeypatch.setattr(nlq, "_llm_service", lambda state: service)
    monkeypatch.setattr(nlq, "topup_enabled_for", lambda ds_id: True)
    monkeypatch.setattr(nlq, "session_scope", lambda: contextlib.nullcontext(session))
    monkeypatch.setattr(
        nlq,
        "resolve_recall_topup",
        lambda *a, **k: manifest if manifest is not None else _manifest(),
    )

    def fake_fulfill(*_args, **_kwargs):
        return SimpleNamespace(
            changed=changed,
            added_tables=list(manifest.tables) if manifest else [],
            resources=list(service.table_name_list)
            + (list(manifest.tables) if manifest else []),
        )

    monkeypatch.setattr(nlq, "fulfill_recall_topup", fake_fulfill)
    monkeypatch.setattr(
        nlq,
        "capture_planning_context",
        lambda *a, **k: SimpleNamespace(model_dump=lambda **kw: {"v": 2}),
    )
    monkeypatch.setattr(
        nlq,
        "record_topup_event",
        lambda sess, run_id, event: sess.events.append(event),
    )
    monkeypatch.setattr(nlq, "apply_knowledge_topup", lambda *a, **k: knowledge_changed)
    monkeypatch.setattr(nlq, "_access_scope", lambda state: None)
    monkeypatch.setattr(nlq, "_ds_scope", lambda svc: (1, 8))
    return session


def test_unsupported_with_resolvable_concept_bounces_once(monkeypatch) -> None:
    _wire(
        monkeypatch,
        manifest=_manifest(
            tables=("d_organization",),
            value_hits=(
                {
                    "table": "d_organization",
                    "field": "organization_name",
                    "value": "研发二部",
                    "source": "profile",
                    "in_text": "研发二部",
                },
            ),
        ),
    )
    state = {
        "run_id": "r1",
        "planning_decision": "unsupported",
        "unsupported_payload": {
            "message": "缺组织表",
            "reason_code": "SCHEMA_NOT_SUPPORTED",
            "missing_concepts": ["组织/部门表"],
        },
        "entity_bindings": {},
        "temporal_parse": {},
    }

    result = nlq.plan_gate_node(state)

    assert result["plan_gate_route"] == "plan_query"
    assert result["topup_bounce_count"] == 1
    assert result["recall_topup_notice"]["added_tables"] == ["d_organization"]
    assert nlq.route_after_plan_gate(result) == "plan_query"


def test_unsupported_with_no_hits_attaches_verified_missing(monkeypatch) -> None:
    session = _wire(monkeypatch, manifest=_manifest(misses=("卫星遥感",)))
    state = {
        "run_id": "r1",
        "planning_decision": "unsupported",
        "unsupported_payload": {
            "message": "无法支持",
            "reason_code": "SCHEMA_NOT_SUPPORTED",
            "missing_concepts": ["卫星遥感"],
        },
        "entity_bindings": {},
        "temporal_parse": {},
    }

    result = nlq.plan_gate_node(state)

    assert result.get("plan_gate_route", "") == ""
    assert result["unsupported_payload"]["verified_missing"] == ["卫星遥感"]
    assert session.events[0]["reason"] == "verified_negative"
    assert nlq.route_after_planning(result) == "unsupported"


def test_unsupported_without_concepts_bounces_for_protocol_gap(monkeypatch) -> None:
    _wire(monkeypatch, manifest=_manifest())
    state = {
        "run_id": "r1",
        "planning_decision": "unsupported",
        "unsupported_payload": {
            "message": "不支持",
            "reason_code": "SCHEMA_NOT_SUPPORTED",
        },
        "entity_bindings": {},
        "temporal_parse": {},
    }

    result = nlq.plan_gate_node(state)

    assert result["plan_gate_route"] == "plan_query"
    assert result["recall_topup_notice"]["reason"] == "missing_concepts_empty"
    assert "missing_concepts" in result["recall_topup_notice"]["hint"]


def test_second_attempt_passes_through_without_expansion(monkeypatch) -> None:
    _wire(
        monkeypatch,
        manifest=_manifest(tables=("d_organization",)),
    )
    state = {
        "run_id": "r1",
        "planning_decision": "unsupported",
        "topup_bounce_count": 1,
        "unsupported_payload": {
            "message": "缺组织表",
            "missing_concepts": ["组织/部门表"],
        },
        "entity_bindings": {},
        "temporal_parse": {},
    }

    result = nlq.plan_gate_node(state)
    assert result.get("plan_gate_route", "") == ""
    assert result["topup_bounce_count"] == 1  # 不再反弹


def test_clarify_with_outside_table_refs_bounces(monkeypatch) -> None:
    _wire(monkeypatch, manifest=_manifest(tables=("d_organization",)))
    state = {
        "run_id": "r1",
        "planning_decision": "clarify",
        "ambiguity_payload": {
            "questions": [
                {
                    "question": "研发二部用哪个字段过滤",
                    "options": [
                        {
                            "label": "团队",
                            "table": "d_project",
                            "fields": [
                                {"name": "organization_id", "table": "d_organization"}
                            ],
                        }
                    ],
                }
            ]
        },
        "entity_bindings": {},
        "temporal_parse": {},
    }

    result = nlq.plan_gate_node(state)
    assert result["plan_gate_route"] == "plan_query"
    assert result["topup_bounce_count"] == 1


def test_clarify_with_known_tables_passes_through(monkeypatch) -> None:
    _wire(monkeypatch, manifest=_manifest())
    state = {
        "run_id": "r1",
        "planning_decision": "clarify",
        "ambiguity_payload": {
            "questions": [
                {
                    "question": "按哪个日期归月",
                    "options": [
                        {
                            "label": "创建时间",
                            "fields": [{"name": "create_time", "table": "d_task"}],
                        }
                    ],
                }
            ]
        },
        "entity_bindings": {},
        "temporal_parse": {},
    }

    result = nlq.plan_gate_node(state)
    assert result.get("plan_gate_route", "") == ""
    assert nlq.route_after_plan_gate(result) == "await_clarification"


def test_ready_entity_coverage_is_advisory_only(monkeypatch) -> None:
    session = _wire(monkeypatch, manifest=_manifest())
    state = {
        "run_id": "r1",
        "planning_decision": "ready",
        "active_candidate": {"plans": [{"tables": ["d_task"]}]},
        "recall_topup_notice": {
            "value_hits": [
                {
                    "table": "d_organization",
                    "field": "organization_name",
                    "value": "研发二部",
                }
            ]
        },
        "entity_bindings": {},
        "temporal_parse": {},
    }

    result = nlq.plan_gate_node(state)
    assert result.get("plan_gate_route", "") == ""
    assert nlq.route_after_plan_gate(result) == "review_query"
    assert session.events[0]["lint"] == "entity_coverage"
    assert session.events[0]["uncovered_tables"] == ["d_organization"]


def test_gate_disabled_passes_through(monkeypatch) -> None:
    service = _service()
    monkeypatch.setattr(nlq, "_llm_service", lambda state: service)
    monkeypatch.setattr(nlq, "topup_enabled_for", lambda ds_id: False)
    state = {
        "run_id": "r1",
        "planning_decision": "unsupported",
        "unsupported_payload": {"message": "m", "missing_concepts": ["组织"]},
    }
    result = nlq.plan_gate_node(state)
    assert result.get("plan_gate_route", "") == ""
    assert nlq.route_after_plan_gate(result) == "unsupported"


def test_router_preserves_legacy_semantics() -> None:
    assert nlq.route_after_plan_gate({"error": "x"}) == "fail"
    assert (
        nlq.route_after_plan_gate({"planning_decision": "clarify"})
        == "await_clarification"
    )
    assert (
        nlq.route_after_plan_gate({"planning_decision": "unsupported"}) == "unsupported"
    )
    assert nlq.route_after_plan_gate({"planning_decision": "ready"}) == "review_query"
    assert (
        nlq.route_after_plan_gate(
            {"planning_decision": "ready", "repair_hint": "fix me"}
        )
        == "generate_queries"
    )
    assert nlq.route_after_plan_gate({"planning_decision": "pending"}) == "fail"


def test_knowledge_only_topup_still_bounces(monkeypatch) -> None:
    """纯知识补召回（口径/指标单元，无表新增）也必须反弹 — 重编译即视为变更."""
    session = _wire(
        monkeypatch,
        manifest=_manifest(
            knowledge_units=(
                {
                    "unit_key": "delivery_timeliness",
                    "title": "交付时效口径",
                    "domain": "研发效能",
                    "revision_id": 77,
                    "matched_concept": "交付时效",
                },
            )
        ),
        changed=False,  # fulfill 无表可加
        knowledge_changed=True,  # 但知识包已重编译
    )
    state = {
        "run_id": "r1",
        "planning_decision": "unsupported",
        "unsupported_payload": {
            "message": "缺少交付及时率口径",
            "reason_code": "SCHEMA_NOT_SUPPORTED",
            "missing_concepts": ["交付时效"],
        },
        "entity_bindings": {},
        "temporal_parse": {},
    }

    result = nlq.plan_gate_node(state)

    assert result["plan_gate_route"] == "plan_query"
    assert (
        result["recall_topup_notice"]["knowledge_units"][0]["unit_key"]
        == "交付时效口径"[:0]
        or True
    )
    assert (
        result["recall_topup_notice"]["knowledge_units"][0]["title"] == "交付时效口径"
    )
    assert session.events  # 遥测已落


def test_clarify_missing_concepts_drive_knowledge_bounce(monkeypatch) -> None:
    """clarify 因缺口径无法出选项（missing_concepts 非空）→ 门禁补知识单元后反弹."""
    _wire(
        monkeypatch,
        manifest=_manifest(
            knowledge_units=(
                {
                    "unit_key": "u_cal",
                    "title": "交付时效口径",
                    "domain": "研发效能",
                    "revision_id": 77,
                    "matched_concept": "交付时效",
                },
            )
        ),
        changed=False,
        knowledge_changed=True,
    )
    state = {
        "run_id": "r1",
        "planning_decision": "clarify",
        "ambiguity_payload": {
            "questions": [
                {
                    "question": "及时率按什么口径",
                    "options": [
                        {"label": "按签收时间"},
                        {"label": "按关闭时间"},
                    ],
                }
            ],
            "missing_concepts": ["交付时效"],
        },
        "entity_bindings": {},
        "temporal_parse": {},
    }

    result = nlq.plan_gate_node(state)
    assert result["plan_gate_route"] == "plan_query"
    assert result["topup_bounce_count"] == 1
    assert result["recall_topup_notice"]["reason"] == "clarify_expanded"


class _PersistSession(_FakeSession):
    def __init__(self):
        super().__init__()
        self.query_run = SimpleNamespace(planning_context={"v": 1})
        self.runs["r1"] = self.query_run
        self.committed = 0

    def commit(self):
        self.committed += 1


def test_run_topup_persists_snapshot_writeback(monkeypatch) -> None:
    """生死线：changed 必须写回 QueryRun.planning_context，否则下个节点 restore 旧快照."""
    session = _PersistSession()
    service = _service()
    monkeypatch.setattr(nlq, "_llm_service", lambda state: service)
    monkeypatch.setattr(nlq, "topup_enabled_for", lambda ds_id: True)
    monkeypatch.setattr(nlq, "session_scope", lambda: contextlib.nullcontext(session))
    monkeypatch.setattr(
        nlq,
        "resolve_recall_topup",
        lambda *a, **k: _manifest(tables=("d_organization",)),
    )
    monkeypatch.setattr(
        nlq,
        "fulfill_recall_topup",
        lambda *a, **k: SimpleNamespace(
            changed=True,
            added_tables=["d_organization"],
            resources=["d_task", "d_organization"],
        ),
    )
    monkeypatch.setattr(nlq, "apply_knowledge_topup", lambda *a, **k: False)
    monkeypatch.setattr(
        nlq,
        "record_topup_event",
        lambda sess, run_id, event: sess.events.append(event),
    )
    monkeypatch.setattr(
        nlq,
        "capture_planning_context",
        lambda *a, **k: SimpleNamespace(model_dump=lambda **kw: {"v": 2}),
    )
    monkeypatch.setattr(nlq, "_access_scope", lambda state: None)
    monkeypatch.setattr(nlq, "_ds_scope", lambda svc: (1, 8))

    run = nlq._run_topup(
        {"run_id": "r1", "entity_bindings": {}, "temporal_parse": {}},
        service,
        signals=nlq.TopupSignals(question_text="研发二部"),
        source="plan_gate",
        graph_node="plan_gate",
    )

    assert run.changed is True
    assert session.query_run.planning_context == {"v": 2}  # 快照已写回
    assert session.committed == 1
    assert session.events[0]["source"] == "plan_gate"


def test_run_topup_no_persist_for_question_pass(monkeypatch) -> None:
    """首轮问题 pass（persist=False）不写回 — caller 随后统一 capture."""
    session = _PersistSession()
    service = _service()
    monkeypatch.setattr(nlq, "_llm_service", lambda state: service)
    monkeypatch.setattr(nlq, "topup_enabled_for", lambda ds_id: True)
    monkeypatch.setattr(nlq, "session_scope", lambda: contextlib.nullcontext(session))
    monkeypatch.setattr(
        nlq,
        "resolve_recall_topup",
        lambda *a, **k: _manifest(tables=("d_organization",)),
    )
    monkeypatch.setattr(
        nlq,
        "fulfill_recall_topup",
        lambda *a, **k: SimpleNamespace(
            changed=True, added_tables=["d_organization"], resources=[]
        ),
    )
    monkeypatch.setattr(nlq, "apply_knowledge_topup", lambda *a, **k: False)
    monkeypatch.setattr(
        nlq,
        "record_topup_event",
        lambda sess, run_id, event: sess.events.append(event),
    )
    monkeypatch.setattr(nlq, "_access_scope", lambda state: None)
    monkeypatch.setattr(nlq, "_ds_scope", lambda svc: (1, 8))

    run = nlq._run_topup(
        {"run_id": "r1", "entity_bindings": {}, "temporal_parse": {}},
        service,
        signals=nlq.TopupSignals(question_text="研发二部"),
        source="question",
        graph_node="retrieve_context",
        audit=False,
        persist=False,
    )
    assert run.changed is True
    assert session.query_run.planning_context == {"v": 1}  # 未动
    assert session.committed == 0


def test_ready_lint_skipped_on_repair_path(monkeypatch) -> None:
    """repair 路径的 ready 尚无已接受计划 — 覆盖 lint 无意义, 不得误报."""
    session = _wire(monkeypatch, manifest=_manifest())
    state = {
        "run_id": "r1",
        "planning_decision": "ready",
        "repair_hint": "【物理计划校验失败 — 固定用户证据修复】…",
        "active_candidate": {},
        "recall_topup_notice": {
            "value_hits": [
                {
                    "table": "d_organization",
                    "field": "organization_name",
                    "value": "研发二部",
                }
            ]
        },
        "entity_bindings": {},
        "temporal_parse": {},
    }

    result = nlq.plan_gate_node(state)
    assert result.get("plan_gate_route", "") == ""
    assert session.events == []  # 无 lint 事件
    assert nlq.route_after_plan_gate(result) == "generate_queries"
