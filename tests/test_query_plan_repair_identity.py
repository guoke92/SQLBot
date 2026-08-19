from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.steps.query_agent import bind_repaired_plan, plan_body_fingerprint
from apps.conversation.run_service import lease_renew_interval_sec


def test_repaired_plan_keeps_failed_candidate_id() -> None:
    prior = {
        "plan_id": "plan_original",
        "dataset_id": "dataset_1",
        "dataset_index": 0,
        "sql": "SELECT a FROM t JOIN u",
        "hard_gate_status": "failed",
    }
    bound = bind_repaired_plan(
        {"sql": "SELECT company, SUM(amt) FROM t GROUP BY company", "brief": "ok"},
        {"sql": "SELECT company, SUM(amt) FROM t GROUP BY company"},
        prior,
        0,
        description="按企业汇总",
    )
    assert bound["plan_id"] == "plan_original"
    assert bound["hard_gate_status"] == "passed"
    assert bound["description"] == "按企业汇总"
    assert "SUM(amt)" in bound["sql"]


def test_repaired_plan_mints_id_without_prior() -> None:
    bound = bind_repaired_plan(
        {"sql": "SELECT 1"},
        {"sql": "SELECT 1"},
        {},
        0,
        description="查询结果",
    )
    assert bound["plan_id"].startswith("plan_")
    assert bound["dataset_id"] == "dataset_1"


def test_lease_renew_interval_is_a_fraction_of_lease() -> None:
    interval = lease_renew_interval_sec()
    assert interval >= 30
    assert interval <= 420


def test_plan_body_fingerprint_ignores_slot_id() -> None:
    left = {"plan_id": "plan_a", "payload": {"sql": "SELECT 1"}}
    right = {"plan_id": "plan_b", "payload": {"sql": "SELECT 1"}}
    changed = {"plan_id": "plan_a", "payload": {"sql": "SELECT 2"}}
    assert plan_body_fingerprint(left) == plan_body_fingerprint(right)
    assert plan_body_fingerprint(left) != plan_body_fingerprint(changed)
