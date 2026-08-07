from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.contract.issues import answer_evidence  # noqa: E402
from apps.knowledge.bind import apply_bound_calibers_to_intent  # noqa: E402
from apps.knowledge.compile.bundle import BoundCaliber, CompiledKnowledge  # noqa: E402
from apps.knowledge.db_models import BusinessCaliber  # noqa: E402
from apps.knowledge.natural_key import (  # noqa: E402
    caliber_natural_key,
    fragments_equivalent,
)
from apps.knowledge.policy import get_knowledge_policy  # noqa: E402
from apps.knowledge.retrieval.caliber_provider import (  # noqa: E402
    _is_bindable,
    _relevance_score,
)


def _caliber(**kwargs: object) -> BusinessCaliber:
    now = datetime.utcnow()
    defaults = dict(
        lineage_id="lin",
        version=1,
        oid=1,
        label="签收额",
        summary="订单签收金额合计",
        contract_fragment={},
        field_targets=[{"table_name": "orders", "field_name": "amount"}],
        synonyms=["签收"],
        trust_tier="certified",
        certified=True,
        enabled=True,
        natural_key="k",
        create_time=now,
        update_time=now,
    )
    defaults.update(kwargs)
    return BusinessCaliber(**defaults)  # type: ignore[arg-type]


def test_natural_key_differs_by_predicate_value() -> None:
    base = {
        "requirements": [
            {
                "clause": "predicate",
                "operator": "eq",
                "field": {"resource": "t", "field": "region"},
                "value": "华东",
            }
        ]
    }
    other = {
        "requirements": [
            {
                "clause": "predicate",
                "operator": "eq",
                "field": {"resource": "t", "field": "region"},
                "value": "华北",
            }
        ]
    }
    a = caliber_natural_key(oid=1, datasource_id=9, field_targets=[], fragment=base)
    b = caliber_natural_key(oid=1, datasource_id=9, field_targets=[], fragment=other)
    assert a != b
    assert fragments_equivalent(base, base)
    assert not fragments_equivalent(base, other)


def test_fragments_equivalent_ignores_evidence_noise() -> None:
    a = {
        "requirements": [
            {
                "clause": "output",
                "operation": "sum",
                "field": {"resource": "t", "field": "amt"},
                "slot_id": "s1",
                "evidence_refs": ["user:answer:q1"],
                "source": "user",
            }
        ]
    }
    b = {
        "requirements": [
            {
                "clause_type": "output",
                "operation": "sum",
                "field": {"resource": "t", "field": "amt"},
                "slot_id": "s9",
                "evidence_refs": ["knowledge:caliber:1"],
                "source": "knowledge",
            }
        ]
    }
    assert fragments_equivalent(a, b)


def test_relevance_blocks_unrelated_question() -> None:
    caliber = _caliber()
    assert _relevance_score(caliber, "今天天气怎么样") == 0
    assert _relevance_score(caliber, "看下签收额趋势") > 0


def test_bind_writes_draft_not_contract() -> None:
    bound = BoundCaliber(
        caliber_id=2,
        lineage_id="lin_y",
        label="签收额",
        fragment={
            "requirements": [
                {
                    "clause": "output",
                    "operation": "sum",
                    "field": {"resource": "t", "field": "amt"},
                    "slot_id": "s2",
                    "label": "签收额",
                }
            ]
        },
    )
    compiled = CompiledKnowledge(bound_calibers=[bound])
    updated, _logs = apply_bound_calibers_to_intent(
        {"status": "evaluating", "draft": {"requirements": []}, "contract": None},
        compiled,
    )
    assert updated.get("contract") is None
    assert len(updated["draft"]["requirements"]) == 1
    assert updated["draft"]["requirements"][0]["source"] == "knowledge"


def test_user_answer_overrides_bind() -> None:
    bound = BoundCaliber(
        caliber_id=1,
        lineage_id="lin_x",
        label="签收额",
        fragment={
            "requirements": [
                {
                    "clause": "output",
                    "operation": "sum",
                    "field": {"resource": "t", "field": "amt"},
                    "slot_id": "s1",
                    "label": "签收额",
                }
            ]
        },
    )
    compiled = CompiledKnowledge(bound_calibers=[bound])
    intent = {
        "status": "evaluating",
        "draft": {
            "requirements": [
                {
                    "clause": "output",
                    "operation": "avg",
                    "field": {"resource": "t", "field": "amt"},
                    "slot_id": "s1",
                    "label": "签收额",
                    "evidence_refs": [answer_evidence("q1")],
                    "source": "user",
                }
            ]
        },
    }
    updated, logs = apply_bound_calibers_to_intent(intent, compiled)
    reqs = updated["draft"]["requirements"]
    assert len(reqs) == 1
    assert reqs[0]["operation"] == "avg"
    assert any(hit.reason == "user_turn_override" for hit in logs)


def test_trusted_not_bindable_by_default() -> None:
    policy = get_knowledge_policy()
    caliber = _caliber(trust_tier="trusted", certified=False)
    assert _is_bindable(caliber, policy) is False
    caliber.certified = True
    caliber.trust_tier = "certified"
    assert _is_bindable(caliber, policy) is True


def test_extract_v_t1_requires_user_answer() -> None:
    from apps.knowledge.capture.extractors import extract_v_t1_caliber
    from apps.knowledge.capture.snapshot import TurnSnapshot

    snap = TurnSnapshot(
        record_id=1,
        ds_id=1,
        oid=1,
        outcome="success",
        original_question="签收额",
        intent_context={
            "status": "ready",
            "contract": {
                "requirements": [
                    {
                        "slot_id": "s1",
                        "label": "金额",
                        "clause": "output",
                        "operation": "sum",
                        "field": {"resource": "t", "field": "a"},
                        "evidence_refs": ["user:question"],
                    }
                ]
            },
        },
    )
    assert extract_v_t1_caliber(snap) is None

    snap.intent_context["contract"]["requirements"][0]["evidence_refs"] = [
        answer_evidence("q1")
    ]
    cand = extract_v_t1_caliber(snap)
    assert cand is not None
    assert cand["trigger_id"] == "V-T1"


def test_certify_rejects_conflict_status() -> None:
    from apps.knowledge.assets.caliber import certify_staging_caliber
    from apps.knowledge.db_models import KnowledgeStaging

    staging = KnowledgeStaging(
        id=1,
        oid=1,
        kind="caliber",
        status="conflict",
        natural_key="nk",
        scope={},
        payload={"contract_fragment": {"requirements": []}},
        trigger_id="V-T1",
        lineage_id="lin",
        create_time=datetime.utcnow(),
        update_time=datetime.utcnow(),
    )

    class Sess:
        def get(self, model: object, pk: object) -> object:
            return staging

    with pytest.raises(ValueError, match="conflict"):
        certify_staging_caliber(
            Sess(),  # type: ignore[arg-type]
            staging_id=1,
            actor_user_id=1,
            oid=1,
        )


def test_staging_payload_strips_envelope() -> None:
    from apps.knowledge.capture.extractors import staging_payload_from_candidate

    payload = staging_payload_from_candidate(
        {
            "kind": "caliber",
            "trigger_id": "V-T1",
            "label": "签收额",
            "summary": "s",
            "contract_fragment": {"requirements": []},
            "field_targets": [{"table_name": "t", "field_name": "a"}],
            "scope": {"ds_id": 1},
            "suggested_trust_tier": "admitted",
        }
    )
    assert set(payload.keys()) == {
        "label",
        "summary",
        "contract_fragment",
        "field_targets",
    }
    assert "kind" not in payload
    assert "trigger_id" not in payload


def test_extract_strips_clause_type_and_evidence() -> None:
    from apps.knowledge.capture.extractors import extract_v_t1_caliber
    from apps.knowledge.capture.snapshot import TurnSnapshot

    snap = TurnSnapshot(
        record_id=1,
        ds_id=1,
        oid=1,
        outcome="success",
        original_question="签收额",
        intent_context={
            "status": "ready",
            "contract": {
                "requirements": [
                    {
                        "slot_id": "s_amt",
                        "label": "签收额",
                        "clause_type": "output",
                        "operation": "sum",
                        "field": {"resource": "t", "field": "amt"},
                        "evidence_refs": [answer_evidence("q1")],
                        "source": "user",
                    }
                ]
            },
        },
    )
    cand = extract_v_t1_caliber(snap)
    assert cand is not None
    req = cand["contract_fragment"]["requirements"][0]
    assert req["clause"] == "output"
    assert "clause_type" not in req
    assert "evidence_refs" not in req
    assert "source" not in req


def test_demote_rejects_certified_tier() -> None:
    from apps.knowledge.assets.caliber import demote_caliber

    caliber = _caliber(id=7, certified=True, trust_tier="certified")

    class Sess:
        def get(self, model: object, pk: object) -> object:
            return caliber

        def add(self, obj: object) -> None:
            return None

        def flush(self) -> None:
            return None

    with pytest.raises(ValueError, match="demote to_tier"):
        demote_caliber(
            Sess(),  # type: ignore[arg-type]
            caliber_id=7,
            oid=1,
            actor_user_id=1,
            to_tier="certified",
        )


def test_certify_rejects_invalid_fragment_shape() -> None:
    from apps.knowledge.assets.caliber import certify_staging_caliber
    from apps.knowledge.db_models import KnowledgeStaging

    staging = KnowledgeStaging(
        id=2,
        oid=1,
        kind="caliber",
        status="pending",
        natural_key="nk",
        scope={"ds_id": 1},
        payload={"contract_fragment": {"requirements": [{"clause": "output"}]}},
        trigger_id="V-T3",
        lineage_id="lin",
        create_time=datetime.utcnow(),
        update_time=datetime.utcnow(),
    )

    class Sess:
        def get(self, model: object, pk: object) -> object:
            return staging

        def exec(self, *_a: object, **_k: object) -> object:
            class R:
                def first(self) -> None:
                    return None

            return R()

        def add(self, obj: object) -> None:
            return None

        def flush(self) -> None:
            return None

    with pytest.raises(ValueError, match="not a valid contract slot"):
        certify_staging_caliber(
            Sess(),  # type: ignore[arg-type]
            staging_id=2,
            actor_user_id=1,
            oid=1,
        )


def test_bind_conflict_on_values_does_not_stamp_knowledge() -> None:
    bound = BoundCaliber(
        caliber_id=9,
        lineage_id="lin_z",
        label="华东筛选",
        fragment={
            "requirements": [
                {
                    "clause": "predicate",
                    "operator": "eq",
                    "field": {"resource": "t", "field": "region"},
                    "values": ["华东"],
                    "slot_id": "p1",
                    "label": "区域",
                }
            ]
        },
    )
    compiled = CompiledKnowledge(bound_calibers=[bound])
    intent = {
        "status": "evaluating",
        "draft": {
            "requirements": [
                {
                    "clause": "predicate",
                    "operator": "eq",
                    "field": {"resource": "t", "field": "region"},
                    "values": ["华北"],
                    "slot_id": "p1",
                    "label": "区域",
                    "source": "model",
                }
            ]
        },
    }
    updated, logs = apply_bound_calibers_to_intent(intent, compiled)
    req = updated["draft"]["requirements"][0]
    assert req["values"] == ["华北"]
    assert req.get("source") != "knowledge"
    assert not any(
        str(r).startswith("knowledge:caliber:") for r in (req.get("evidence_refs") or [])
    )
    assert any(hit.reason == "caliber_slot_conflict" for hit in logs)


def test_ephemeral_filters_values_tuple() -> None:
    from apps.knowledge.capture.extractors import extract_v_t1_caliber
    from apps.knowledge.capture.snapshot import TurnSnapshot

    snap = TurnSnapshot(
        record_id=1,
        ds_id=1,
        oid=1,
        outcome="degraded",
        original_question="查订单",
        intent_context={
            "status": "ready",
            "contract": {
                "requirements": [
                    {
                        "slot_id": "p_oid",
                        "label": "订单号",
                        "clause": "predicate",
                        "operator": "eq",
                        "field": {"resource": "t", "field": "order_id"},
                        "values": ["1234567890123456"],
                        "evidence_refs": [answer_evidence("q1")],
                        "source": "user",
                    }
                ]
            },
        },
    )
    assert extract_v_t1_caliber(snap) is None


def test_v_t1_accepts_degraded_outcome() -> None:
    from apps.knowledge.capture.extractors import extract_v_t1_caliber
    from apps.knowledge.capture.snapshot import TurnSnapshot

    snap = TurnSnapshot(
        record_id=1,
        ds_id=1,
        oid=1,
        outcome="degraded",
        original_question="签收额",
        intent_context={
            "status": "ready",
            "contract": {
                "requirements": [
                    {
                        "slot_id": "s1",
                        "label": "签收额",
                        "clause": "output",
                        "operation": "sum",
                        "field": {"resource": "t", "field": "amt"},
                        "evidence_refs": [answer_evidence("q1")],
                        "source": "user",
                    }
                ]
            },
        },
    )
    assert extract_v_t1_caliber(snap) is not None


def test_l1_disable_matches_field_names() -> None:
    from apps.knowledge.assets.caliber import disable_for_schema_change

    caliber = _caliber(
        id=3,
        datasource_id=9,
        field_targets=[{"table_name": "orders", "field_name": "amount"}],
        enabled=True,
    )
    added: list[object] = []

    class Sess:
        def exec(self, *_a: object, **_k: object) -> object:
            class R:
                def all(self) -> list[object]:
                    return [caliber]

            return R()

        def add(self, obj: object) -> None:
            added.append(obj)

        def flush(self) -> None:
            return None

    n = disable_for_schema_change(
        Sess(),  # type: ignore[arg-type]
        ds_id=9,
        changed_field_names=[("orders", "amount")],
    )
    assert n == 1
    assert caliber.enabled is False

