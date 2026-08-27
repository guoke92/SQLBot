"""Turn-router fallback ladder: payload repair + conservative anaphora rescue.

chat-61/record-170 regression: the model router's output failed validation
and the plain independent fallback detached an anaphoric message
("我需要在第一列展示项目名称") from its referenced turn — the planner then
re-planned around a clarify answer and the query subject collapsed to a
single lookup table.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.turn_contracts import TurnRoute  # noqa: E402
from apps.chat.turn_router import (  # noqa: E402
    repair_route_payload,
    route_turn,
)


def test_170_scenario_conservative_rescue_keeps_reference() -> None:
    """模型路由彻底失败 + 指代表述 + 有历史 → 保守挂回最近一轮（170 场景锁定）."""

    def broken_router(_: str) -> dict[str, object]:
        raise ValueError("model output unparseable")

    route = route_turn(
        "我需要在第一列展示项目名称",
        candidate_record_ids=(169,),
        has_history=True,
        model_router=broken_router,
    )
    assert route.relation == "revise"
    assert route.reference_record_ids == (169,)
    assert route.source == "deterministic"


def test_repair_rescues_structurally_defective_model_output() -> None:
    """L1：task_kind 拼错 + 引用幻觉 id → 修补为合法路由（不丢引用语义）."""
    repaired = repair_route_payload(
        {
            "task_kind": "queryy",
            "relation": "revise",
            "reference_record_ids": [999, 169, 169],
        },
        candidate_record_ids=(168, 169),
    )
    assert repaired is not None
    route = TurnRoute.model_validate(repaired)
    assert route.task_kind == "query"
    assert route.relation == "revise"
    assert route.reference_record_ids == (169,)


def test_repair_attaches_latest_when_relation_needs_references() -> None:
    repaired = repair_route_payload(
        {"task_kind": "query", "relation": "continue"},
        candidate_record_ids=(160, 161),
    )
    route = TurnRoute.model_validate(repaired)
    assert route.relation == "continue"
    assert route.reference_record_ids == (161,)


def test_repair_analysis_without_reference_degrades_or_attaches() -> None:
    # 有候选 → 挂最近一轮继续
    repaired = repair_route_payload(
        {"task_kind": "analysis", "relation": "independent"},
        candidate_record_ids=(169,),
    )
    assert TurnRoute.model_validate(repaired).relation == "continue"
    # 无候选 → 降级为 query（TurnRoute 禁止 analysis 独立成轮）
    repaired = repair_route_payload(
        {"task_kind": "analysis", "relation": "independent"}
    )
    route = TurnRoute.model_validate(repaired)
    assert route.task_kind == "query"
    assert route.relation == "independent"


def test_repair_rejects_signal_free_payload() -> None:
    assert repair_route_payload({"foo": 1}) is None
    assert repair_route_payload({"confidence": 0.9}) is None


def test_route_turn_uses_repair_before_rescue() -> None:
    """模型输出可修补时优先用修补结果（source=model），不进保守救回."""
    calls: list[str] = []

    def defective_router(message: str) -> dict[str, object]:
        calls.append(message)
        return {
            "task_kind": "query",
            "relation": "revise",
            "reference_record_ids": "bad",
        }

    route = route_turn(
        "我需要在第一列展示项目名称",
        candidate_record_ids=(169,),
        has_history=True,
        model_router=defective_router,
    )
    assert route.source == "model"
    assert route.relation == "revise"
    assert route.reference_record_ids == (169,)
    assert len(calls) == 1  # 只调用一次模型，修补不重试


def test_non_anaphoric_failure_still_falls_back_independent() -> None:
    """无指代信号 + 模型失败 → 维持独立 fallback（不误挂历史）."""

    def broken_router(_: str) -> dict[str, object]:
        raise ValueError("boom")

    route = route_turn(
        "统计所有部门的月度销售额",
        candidate_record_ids=(169,),
        has_history=True,
        model_router=broken_router,
    )
    assert route.source == "fallback"
    assert route.relation == "independent"
    assert route.reference_record_ids == ()


def test_continuation_wording_rescues_as_continue() -> None:
    def broken_router(_: str) -> dict[str, object]:
        return {"nonsense": True}  # 无信号载荷 → 修补拒绝 → 救回

    route = route_turn(
        "其中研发二部的情况再看一下",
        candidate_record_ids=(160, 161),
        has_history=True,
        model_router=broken_router,
    )
    assert route.relation == "continue"
    assert route.reference_record_ids == (161,)


def test_rescue_requires_history_candidates() -> None:
    def broken_router(_: str) -> dict[str, object]:
        raise ValueError("boom")

    route = route_turn(
        "我需要在第一列展示项目名称",
        candidate_record_ids=(),
        has_history=True,  # 有历史但无带结果的候选记录
        model_router=broken_router,
    )
    assert route.source == "fallback"
    assert route.relation == "independent"
