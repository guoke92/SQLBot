"""Unit tests for multi-turn continue context hydration."""

from __future__ import annotations

from types import SimpleNamespace

from apps.chat.agent.context_spec import recap_from_turn_answer, render_recap
from apps.chat.agent.init import sql_datasets_along_continue
from apps.chat.memory_slots import (
    MemorySlots,
    answer_has_executable_sql,
    hydrate_memory_slots_from_referenced_turns,
)
from apps.chat.turn_contracts import TurnRoute


def _turn(**kwargs: object) -> SimpleNamespace:
    return SimpleNamespace(
        id=kwargs.get("id"),
        chat_id=kwargs.get("chat_id", 1),
        create_by=kwargs.get("create_by", 1),
        datasource=kwargs.get("datasource", 1),
        reference_record_ids=list(kwargs.get("reference_record_ids") or []),
        answer=kwargs.get("answer") or {},
    )


def test_recap_from_turn_answer_reads_handles_and_calibers() -> None:
    recap = recap_from_turn_answer(
        {
            "status": "succeeded",
            "content": "本月签约 12 单",
            "datasets": [
                {"sql": "SELECT 1", "dataset_id": "ds-old", "rev": "r1"},
                {"sql": "SELECT id FROM t", "dataset_id": "ds-new", "rev": "r2"},
            ],
            "confirmed_calibers": [{"question": "口径", "label": "签约"}],
            "assumptions": [{"label": "排除已注销"}],
            "knowledge_refs": {"page_keys": ["p1"], "tables": ["t"]},
        }
    )
    dumped = recap.model_dump(mode="json")
    assert "sql" not in dumped["datasets"][-1]
    assert recap.datasets[-1].rev == "r2"
    assert recap.datasets[-1].dataset_id == "ds-new"
    assert recap.dataset_id == "ds-old"
    assert recap.confirmed_calibers[0]["label"] == "签约"
    assert recap.knowledge_refs["page_keys"] == ["p1"]


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
                        "rev": "r1",
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
    assert slots.current_rev == "r1"
    assert slots.active_dataset_outline["row_count"] == 1000
    assert slots.active_dataset_outline["rev"] == "r1"
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


def test_sql_datasets_walk_continue_chain_to_last_delivery() -> None:
    delivered = _turn(
        id=860,
        answer={
            "status": "succeeded",
            "datasets": [
                {
                    "status": "succeeded",
                    "sql": "SELECT code FROM cust_company_info LIMIT 1000",
                    "dataset_id": "ds1",
                    "rev": "r1",
                    "fields": ["code"],
                    "row_count": 1000,
                    "truncated": True,
                    "limit": 1000,
                }
            ],
        },
    )
    text_close = _turn(
        id=861,
        reference_record_ids=[860],
        answer={"status": "succeeded", "datasets": []},
    )
    store = {860: delivered, 861: text_close}
    found = sql_datasets_along_continue(
        text_close,
        load=store.get,
        chat_id=1,
        user_id=1,
        datasource=1,
    )
    assert len(found) == 1
    assert found[0]["sql"].startswith("SELECT code")
    assert found[0]["row_count"] == 1000
    assert found[0]["source_record_id"] == 860


def test_sql_datasets_keep_immediate_delivery() -> None:
    parent = _turn(
        id=1,
        answer={
            "status": "succeeded",
            "datasets": [
                {
                    "status": "succeeded",
                    "sql": "SELECT 1",
                    "dataset_id": "old",
                }
            ],
        },
    )
    child = _turn(
        id=2,
        reference_record_ids=[1],
        answer={
            "status": "succeeded",
            "datasets": [
                {
                    "status": "succeeded",
                    "sql": "SELECT 2",
                    "dataset_id": "new",
                }
            ],
        },
    )
    found = sql_datasets_along_continue(
        child,
        load={1: parent, 2: child}.get,
        chat_id=1,
        user_id=1,
        datasource=1,
    )
    assert [item["dataset_id"] for item in found] == ["new"]


def test_render_recap_clips_long_question() -> None:
    text = render_recap(
        [{"question": "问" * 500, "answer_summary": "短答", "datasets": []}]
    )
    question_line = text.splitlines()[0]
    assert len(question_line) <= 403
    assert question_line.startswith("问：")
