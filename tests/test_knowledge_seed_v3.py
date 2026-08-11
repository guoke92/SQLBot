from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import orjson
import pytest

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.query_specification import (  # noqa: E402
    BusinessRelationRequirement,
    FieldRef,
    OutputRequirement,
    PredicateRequirement,
    QuerySpecification,
    RelationPair,
    TimeWindowRequirement,
    parse_specification_fragment,
)
from apps.chat.steps.semantic_planner import plan_semantics_and_query  # noqa: E402
from apps.chat.steps.knowledge_seed import (  # noqa: E402
    apply_knowledge_seeds,
    prepare_knowledge_seed,
)
from apps.chat.planning import BatchParseResult  # noqa: E402
from apps.conversation.models import NlqEvidenceEvent  # noqa: E402
from apps.knowledge.capture.extractors import (  # noqa: E402
    _field_targets_from_specification,
    extract_v_t1_caliber,
)
from apps.knowledge.capture.snapshot import TurnSnapshot  # noqa: E402
from apps.knowledge.compile.bundle import BoundCaliber  # noqa: E402
from apps.knowledge.compile.compile import compile_knowledge_for_turn  # noqa: E402
from apps.knowledge.natural_key import (  # noqa: E402
    canonical_fragment_fingerprint,
    fragments_equivalent,
)
from apps.knowledge.retrieval.caliber_provider import (  # noqa: E402
    _applicability_score,
    _is_bindable,
)


def _output_fragment(aggregation: str = "sum") -> dict[str, object]:
    return {
        "version": 3,
        "requirements": [
            {
                "clause": "output",
                "requirement_id": "amount",
                "business_label": "签收金额",
                "field": {"resource": "asset", "field": "amount"},
                "aggregation": aggregation,
            }
        ],
    }


def _bound(fragment: dict[str, object]) -> BoundCaliber:
    return BoundCaliber(
        caliber_id=7,
        lineage_id="lineage-7",
        label="签收金额口径",
        fragment=fragment,
        trust_tier="certified",
    )


def test_fragment_fingerprint_covers_aggregation_time_and_population() -> None:
    assert canonical_fragment_fingerprint(_output_fragment("sum")) != (
        canonical_fragment_fingerprint(_output_fragment("avg"))
    )

    explicit = {
        "version": 3,
        "requirements": [
            {
                "clause": "time_window",
                "requirement_id": "window",
                "business_label": "今年",
                "fields": [{"resource": "asset", "field": "sign_date"}],
                "mode": "explicit",
                "start": "2026-01-01",
                "end_exclusive": "2027-01-01",
            }
        ],
    }
    shifted = {
        **explicit,
        "requirements": [
            {
                **explicit["requirements"][0],  # type: ignore[index]
                "start": "2025-01-01",
                "end_exclusive": "2026-01-01",
            }
        ],
    }
    assert canonical_fragment_fingerprint(explicit) != canonical_fragment_fingerprint(
        shifted
    )

    left = {
        "version": 3,
        "requirements": [
            {
                "clause": "business_relation",
                "requirement_id": "population",
                "business_label": "保留全部企业",
                "pairs": [
                    {
                        "left": {"resource": "company", "field": "id"},
                        "right": {"resource": "asset", "field": "company_id"},
                    }
                ],
                "population": "left",
            }
        ],
    }
    intersection = {
        **left,
        "requirements": [
            {
                **left["requirements"][0],  # type: ignore[index]
                "population": "intersection",
            }
        ],
    }
    assert canonical_fragment_fingerprint(left) != canonical_fragment_fingerprint(
        intersection
    )


def test_fragments_equivalent_treats_legacy_or_empty_as_mismatch() -> None:
    """Old flat slots / empty rows must not abort admit via fingerprint errors."""
    legacy = {
        "requirements": [
            {
                "clause": "predicate",
                "slot_id": "region",
                "label": "区域",
                "operation": "eq",
                "value": "华东",
            }
        ]
    }
    typed = _output_fragment("sum")
    assert fragments_equivalent(legacy, typed) is False
    assert fragments_equivalent({}, typed) is False
    assert fragments_equivalent(typed, typed) is True


def test_fragment_parser_rejects_dangling_output_and_order_references() -> None:
    with pytest.raises(ValueError, match="unknown operands"):
        parse_specification_fragment(
            {
                "version": 3,
                "requirements": [
                    {
                        "clause": "output",
                        "requirement_id": "ratio",
                        "business_label": "转化率",
                        "field": {"semantic_ref": "conversion_rate"},
                        "aggregation": "ratio",
                        "operand_requirement_ids": ["done", "all"],
                    }
                ],
            }
        )
    with pytest.raises(ValueError, match="unknown output"):
        parse_specification_fragment(
            {
                "version": 3,
                "requirements": [
                    {
                        "clause": "order",
                        "requirement_id": "order",
                        "business_label": "按金额倒序",
                        "output_requirement_id": "amount",
                        "direction": "desc",
                    }
                ],
            }
        )


def test_seed_is_applied_with_real_provenance_and_log() -> None:
    seed = prepare_knowledge_seed(
        _bound(_output_fragment()),
        evidence_ref="knowledge:event-7",
    )
    candidate = QuerySpecification(
        revision=1,
        outputs=(
            OutputRequirement(
                requirement_id="candidate",
                business_label="签收金额",
                field=FieldRef(resource="asset", field="amount"),
                aggregation="sum",
            ),
        ),
    )
    applied = apply_knowledge_seeds(candidate, [seed])
    assert not applied.missing
    assert applied.specification.outputs[0].source == "knowledge"
    assert applied.specification.outputs[0].evidence_refs == ("knowledge:event-7",)
    assert [(item.apply, item.reason) for item in applied.apply_log] == [
        ("bind", "certified_seed_applied")
    ]


def test_user_time_basis_overrides_certified_default() -> None:
    fragment = {
        "version": 3,
        "requirements": [
            {
                "clause": "time_window",
                "requirement_id": "time",
                "business_label": "按签收日统计今年",
                "fields": [{"resource": "asset", "field": "sign_date"}],
                "mode": "explicit",
                "start": "2026-01-01",
                "end_exclusive": "2027-01-01",
            }
        ],
    }
    seed = prepare_knowledge_seed(
        _bound(fragment),
        evidence_ref="knowledge:event-7",
    )
    user_specification = QuerySpecification(
        revision=1,
        time_windows=(
            TimeWindowRequirement(
                requirement_id="user-time",
                business_label="按确权日统计今年",
                fields=(FieldRef(resource="asset", field="confirm_date"),),
                mode="explicit",
                start="2026-01-01",
                end_exclusive="2027-01-01",
                source="user",
                evidence_refs=("user:question",),
                confidence=1,
            ),
        ),
    )
    applied = apply_knowledge_seeds(user_specification, [seed])
    assert not applied.missing
    assert applied.specification.time_windows[0].source == "user"
    assert [(item.apply, item.reason) for item in applied.apply_log] == [
        ("drop", "user_override")
    ]


def test_missing_seed_without_user_override_requires_planner_repair() -> None:
    seed = prepare_knowledge_seed(
        _bound(_output_fragment()),
        evidence_ref="knowledge:event-7",
    )
    unrelated = QuerySpecification(
        revision=1,
        predicates=(
            PredicateRequirement(
                requirement_id="status",
                business_label="仅已完成",
                field=FieldRef(resource="asset", field="status"),
                operator="eq",
                values=("done",),
            ),
        ),
    )
    applied = apply_knowledge_seeds(unrelated, [seed])
    assert len(applied.missing) == 1
    assert applied.missing[0].startswith("7:req_")
    assert not applied.apply_log


def test_field_targets_cover_time_windows_and_relation_pairs() -> None:
    specification = QuerySpecification(
        revision=1,
        time_windows=(
            TimeWindowRequirement(
                requirement_id="time",
                business_label="今年",
                fields=(
                    FieldRef(resource="task", field="created_at"),
                    FieldRef(resource="story", field="created_at"),
                ),
                mode="explicit",
                start="2026-01-01",
                end_exclusive="2027-01-01",
            ),
        ),
        business_relations=(
            BusinessRelationRequirement(
                requirement_id="relation",
                business_label="任务与项目对应",
                pairs=(
                    RelationPair(
                        left=FieldRef(resource="task", field="project_id"),
                        right=FieldRef(resource="project", field="id"),
                    ),
                ),
                population="intersection",
            ),
        ),
    )
    targets = _field_targets_from_specification(specification, 8)
    assert {(item["table_name"], item["field_name"]) for item in targets} == {
        ("task", "created_at"),
        ("story", "created_at"),
        ("task", "project_id"),
        ("project", "id"),
    }


def test_capture_emits_a_typed_reusable_fragment() -> None:
    output = dict(_output_fragment()["requirements"][0])  # type: ignore[index]
    output.update(
        {
            "source": "user",
            "evidence_refs": ["user:answer:answer-1"],
        }
    )
    snapshot = TurnSnapshot(
        record_id=9,
        ds_id=8,
        original_question="查询累计签收金额",
        specification={
            "version": 3,
            "revision": 1,
            "outputs": [output],
        },
        outcome="success",
        contract_status="ready",
    )
    candidate = extract_v_t1_caliber(snapshot)
    assert candidate is not None
    parsed = parse_specification_fragment(candidate["contract_fragment"])
    assert parsed.outputs[0].aggregation == "sum"
    assert candidate["field_targets"] == [
        {
            "ds_id": 8,
            "table_name": "asset",
            "field_name": "amount",
            "field_id": None,
            "table_id": None,
        }
    ]


def test_strong_applicability_requires_label_or_synonym_phrase() -> None:
    caliber = SimpleNamespace(
        label="签收金额口径",
        payload={"synonyms": ["累计签收额"]},
    )
    assert _applicability_score(caliber, "查询今年累计签收额") > 0
    assert _applicability_score(caliber, "查询今年企业融资金额") == 0
    assert _is_bindable(
        SimpleNamespace(
            enabled=True,
            superseded_by=None,
            certified=True,
            trust_tier="certified",
        )
    )
    assert not _is_bindable(
        SimpleNamespace(
            enabled=True,
            superseded_by=None,
            certified=False,
            trust_tier="trusted",
        )
    )


def test_compile_does_not_report_bind_before_specification_absorbs_seed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bound = _bound(_output_fragment())
    monkeypatch.setattr(
        "apps.knowledge.compile.compile.recall_knowledge",
        lambda *_args, **_kwargs: SimpleNamespace(
            prompt_template="",
            log_items=[],
            matches=[],
        ),
    )
    monkeypatch.setattr(
        "apps.knowledge.retrieval.caliber_provider.recall_bindable_calibers",
        lambda *_args, **_kwargs: [
            SimpleNamespace(
                apply="bind",
                bound=bound,
                asset_id=bound.caliber_id,
                lineage_id=bound.lineage_id,
                trust_tier=bound.trust_tier,
                drop_reason=None,
            )
        ],
    )
    session = SimpleNamespace(
        exec=lambda _stmt: SimpleNamespace(all=lambda: []),
    )
    compiled = compile_knowledge_for_turn(
        session,  # type: ignore[arg-type]
        stage="assess",
        question="签收金额口径",
        oid=1,
        ds_id=8,
    )
    assert compiled.bound_calibers == [bound]
    assert not [
        item
        for item in compiled.apply_log
        if item.asset_kind == "caliber" and item.apply == "bind"
    ]


def test_planner_repairs_missing_seed_then_degrades_without_blocking(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seed = prepare_knowledge_seed(
        _bound(_output_fragment()),
        evidence_ref="knowledge:event-7",
    )
    response_payload = {
        "decision": "ready",
        "specification": {
            "version": 3,
            "revision": 1,
            "predicates": [
                {
                    "clause": "predicate",
                    "requirement_id": "status",
                    "business_label": "仅已完成",
                    "field": {"semantic_ref": "status"},
                    "operator": "eq",
                    "values": ["done"],
                    "source": "user",
                    "evidence_refs": ["user:question"],
                }
            ],
        },
        "candidates": [{"payload": {"sql": "SELECT 1"}}],
    }

    class _FakeModel:
        def __init__(self) -> None:
            self.calls = 0

        def bind(self, **_kwargs: object) -> _FakeModel:
            return self

        def invoke(self, _messages: object) -> SimpleNamespace:
            self.calls += 1
            return SimpleNamespace(
                content=orjson.dumps(response_payload).decode(),
                additional_kwargs={},
                usage_metadata={},
                response_metadata={},
            )

    model = _FakeModel()
    service = SimpleNamespace(
        llm=model,
        protocol=SimpleNamespace(
            type_key="sql",
            build_prompt_bundle=lambda *_args, **_kwargs: SimpleNamespace(
                as_dict=lambda: {}
            ),
        ),
        chat_question=SimpleNamespace(
            db_schema="",
            sample_data="",
            terminologies="",
            data_training="",
            custom_prompt="",
        ),
        enable_sql_row_limit=True,
    )
    monkeypatch.setattr(
        "apps.chat.steps.semantic_planner.parse_query_generation",
        lambda *_args, **_kwargs: BatchParseResult(
            plans=[{"sql": "SELECT 1", "payload": {"sql": "SELECT 1"}}],
            plan_validated=True,
            contract_status="partial",
        ),
    )
    evidence = [
        NlqEvidenceEvent(
            evidence_id="question-1",
            run_id="run-1",
            sequence=1,
            kind="user_question",
            source="user",
            content="查询已完成数据",
        ),
        NlqEvidenceEvent(
            evidence_id="event-7",
            run_id="run-1",
            sequence=2,
            kind="knowledge_caliber",
            source="knowledge",
            content="caliber:7:lineage-7",
        ),
    ]
    result = plan_semantics_and_query(
        service,
        evidence=evidence,
        previous_specification=None,
        entity_bindings={},
        temporal_parse={},
        max_batch_size=1,
        knowledge_seeds=[seed],
    )
    assert model.calls == 2
    assert result.decision.decision == "ready"
    assert result.decision.specification.assumptions[0].risk == "high"
    assert [(item.apply, item.reason) for item in result.knowledge_apply] == [
        ("drop", "planner_omitted_after_repair")
    ]
