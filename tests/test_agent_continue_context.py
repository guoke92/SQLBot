"""Unit tests for multi-turn continue context hydration."""

from __future__ import annotations

from apps.chat.memory_slots import (
    MemorySlots,
    answer_has_executable_sql,
    hydrate_memory_slots_from_referenced_turns,
)
from apps.chat.turn_contracts import TurnRoute


def test_answer_has_executable_sql_requires_succeeded_dataset() -> None:
    assert not answer_has_executable_sql({"status": "succeeded", "datasets": []})
    assert not answer_has_executable_sql(
        {"status": "failed", "datasets": [{"sql": "SELECT 1"}]}
    )
    assert answer_has_executable_sql(
        {"status": "succeeded", "datasets": [{"sql": "SELECT 1"}]}
    )


def test_continue_turn_route_shape() -> None:
    route = TurnRoute(
        task_kind="query",
        relation="continue",
        reference_record_ids=(551,),
        source="deterministic",
        confidence=0.9,
    )
    assert route.model_dump(mode="json")["reference_record_ids"] == [551]


def test_hydrate_memory_slots_from_prior_turn() -> None:
    slots = MemorySlots()
    hydrate_memory_slots_from_referenced_turns(
        slots,
        [
            {
                "record_id": 551,
                "datasets": [
                    {
                        "sql": "SELECT code FROM cust_company_info LIMIT 1000",
                        "fields": ["code"],
                        "row_count": 1000,
                    }
                ],
                "assumptions": [
                    {
                        "source": "clarification",
                        "question": "认证方式口径",
                        "label": "邀请认证-内管录入",
                    },
                    {
                        "source": "declared",
                        "question": "默认过滤",
                        "label": "排除已注销",
                    },
                ],
            }
        ],
    )
    assert "LIMIT 1000" in slots.active_baseline_sql
    assert slots.active_dataset_outline["row_count"] == 1000
    caliber = slots.confirmed_calibers["认证方式口径"]
    assert isinstance(caliber, dict)
    assert caliber["label"] == "邀请认证-内管录入"
    assert len(slots.assumptions) == 1
    assert slots.assumptions[0]["label"] == "排除已注销"


def test_hydrate_confirmed_calibers_from_answer_list() -> None:
    slots = MemorySlots()
    hydrate_memory_slots_from_referenced_turns(
        slots,
        [
            {
                "record_id": 552,
                "datasets": [{"sql": "SELECT 1", "fields": ["x"], "row_count": 1}],
                "confirmed_calibers": [
                    {
                        "question": "时间口径",
                        "label": "按创建时间",
                        "meaning": "按创建时间",
                        "source": "clarification",
                    }
                ],
                "assumptions": [
                    {
                        "source": "declared",
                        "question": "默认过滤",
                        "label": "排除已注销",
                    },
                    {
                        "source": "clarification",
                        "question": "残留澄清",
                        "label": "不应留在假设",
                    },
                ],
            }
        ],
    )
    assert slots.confirmed_calibers["时间口径"]["label"] == "按创建时间"
    assert len(slots.assumptions) == 1
    assert slots.assumptions[0]["label"] == "排除已注销"
