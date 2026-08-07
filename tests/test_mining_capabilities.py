"""Tests for mining capability catalog, policy, soft signals, and query-log parse."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from apps.datasource.profiling.capability_catalog import (
    PRESET_DEEP,
    PRESET_LITE,
    PRESET_STANDARD,
    bound_dependencies,
    expand_capabilities,
    preset_capabilities,
    tools_for_capabilities,
)
from apps.datasource.profiling.policy import resolve_mining_policy
from apps.datasource.profiling.query_log_joins import extract_equi_join_pairs
from apps.datasource.profiling.soft_signals import (
    derive_field_soft_signals,
    inclusion_score,
    infer_table_role,
    key_likelihood,
)
from apps.datasource.profiling.tools import build_mining_tools
from apps.datasource.profiling.models import ScanRunMode


def test_preset_lite_has_no_agent_work() -> None:
    policy = resolve_mining_policy(ds_policy={"preset": "lite"})
    assert "field_profile" in policy.capabilities
    assert not policy.has_agent_work()
    assert policy.capabilities == expand_capabilities(PRESET_LITE)


def test_preset_standard_closes_inclusion_deps() -> None:
    closed = expand_capabilities(PRESET_STANDARD)
    assert "soft_signals" in closed
    assert "field_profile" in closed
    assert "structure" in closed
    policy = resolve_mining_policy(ds_policy={"preset": "standard"})
    assert policy.has_agent_work()
    assert "query_log_joins" in policy.agent_caps


def test_table_override_beats_ds() -> None:
    policy = resolve_mining_policy(
        ds_policy={"preset": "deep"},
        table_policy={"preset": "lite"},
    )
    assert policy.source == "table"
    assert policy.preset == "lite"
    assert not policy.has_agent_work()


def test_table_inherit_uses_ds() -> None:
    policy = resolve_mining_policy(
        ds_policy={"preset": "deep"},
        table_policy={"inherit": True},
    )
    assert policy.source == "ds"
    assert "samples" in policy.capabilities


def test_custom_requires_known_capabilities() -> None:
    policy = resolve_mining_policy(
        ds_policy={"preset": "custom", "capabilities": ["field_profile", "equi_candidates"]}
    )
    # equi pulls inclusion + name + soft_signals + structure
    assert "inclusion_probe" in policy.capabilities
    assert "name_similarity" in policy.capabilities
    bound = bound_dependencies(["equi_candidates"])
    assert "field_profile" in bound


def test_unknown_capability_raises() -> None:
    try:
        expand_capabilities(["not_a_real_cap"])
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        assert "unknown capabilities" in str(exc)


def test_tools_for_lite_excludes_probes() -> None:
    tools = tools_for_capabilities(PRESET_LITE)
    assert "overlap_probe" not in tools
    assert "get_profile_brief" in tools


def test_build_mining_tools_respects_capabilities() -> None:
    tools = build_mining_tools(
        oid=1,
        ds_id=1,
        table_id=1,
        run_mode=ScanRunMode.SEMANTIC.value,
        allow_confirm=False,
        capabilities=PRESET_LITE,
    )
    names = {t.name for t in tools}
    assert "get_profile_brief" in names
    assert "overlap_probe" not in names
    assert "mine_query_log_joins" not in names


def test_build_mining_tools_deep_includes_query_log() -> None:
    tools = build_mining_tools(
        oid=1,
        ds_id=1,
        table_id=1,
        run_mode=ScanRunMode.SEMANTIC.value,
        capabilities=PRESET_DEEP,
    )
    names = {t.name for t in tools}
    assert "mine_query_log_joins" in names
    assert "get_samples" in names


def test_key_likelihood_and_soft_signals() -> None:
    assert key_likelihood(distinct_ratio=0.99, null_rate=0.0) == "high"
    assert key_likelihood(distinct_ratio=0.5, null_rate=0.0) == "low"
    signals = derive_field_soft_signals(
        field_name="order_date",
        field_type="date",
        null_rate=0.0,
        distinct_ratio=0.3,
        approx_distinct=100,
        min_value="2024-01-01",
        max_value="2024-12-31",
    )
    assert signals["domain_role"] == "datetime"
    assert signals.get("temporal_role") in {"biz_date", "datetime", "event_time"}


def test_inclusion_score_suggests_when_target_is_key() -> None:
    scored = inclusion_score(
        containment_source_in_target=0.9,
        containment_target_in_source=0.2,
        source_key_likelihood="low",
        target_key_likelihood="high",
    )
    assert scored["suggest_candidate"] is True
    assert scored["suggested_direction"] == "source_fk_to_target_pk"
    weak = inclusion_score(
        containment_source_in_target=0.9,
        containment_target_in_source=0.9,
        source_key_likelihood="low",
        target_key_likelihood="low",
    )
    assert weak["suggest_candidate"] is False


def test_infer_table_role_fact_vs_dim() -> None:
    fact = infer_table_role(
        approx_rows=200_000,
        field_count=20,
        high_key_fields=1,
        outbound_candidate_edges=2,
    )
    assert fact["table_role"] == "fact"
    dim = infer_table_role(
        approx_rows=500,
        field_count=5,
        high_key_fields=1,
    )
    assert dim["table_role"] == "dim"


def test_extract_equi_join_pairs_from_sql() -> None:
    sql = """
    SELECT o.id, u.name
    FROM orders o
    JOIN users u ON o.user_id = u.id
    WHERE o.amount > 0
    """
    pairs = extract_equi_join_pairs(sql)
    tables = {(p[0], p[2]) for p in pairs}
    assert ("orders", "users") in tables or ("users", "orders") in tables
    assert all(len(p) == 6 for p in pairs)


def test_extract_equi_join_pairs_ignores_same_table() -> None:
    sql = "SELECT * FROM t a JOIN t b ON a.id = b.parent_id"
    # Same physical table name — skipped by design
    assert extract_equi_join_pairs(sql) == []


def test_extract_equi_join_pairs_keeps_database_qualifier() -> None:
    sql = """
    SELECT *
    FROM stg.orders o
    JOIN ods.users u ON o.user_id = u.id
    """
    pairs = extract_equi_join_pairs(sql)
    assert pairs
    dbs = {(p[4], p[5]) for p in pairs}
    assert ("stg", "ods") in dbs or ("ods", "stg") in dbs


def test_preset_capabilities_default() -> None:
    assert preset_capabilities("nope") == PRESET_LITE


def test_system_default_policy_is_lite() -> None:
    policy = resolve_mining_policy()
    assert policy.preset == "lite"
    assert policy.source == "default"
    assert not policy.has_agent_work()
    assert "soft_signals" not in policy.facts_caps
    assert "soft_signals" in resolve_mining_policy(
        ds_policy={"preset": "standard"}
    ).capabilities


def test_ddl_may_overwrite_respects_human_veto() -> None:
    from apps.datasource.profiling.service import ddl_may_overwrite_status

    assert ddl_may_overwrite_status(None) is True
    assert ddl_may_overwrite_status("CANDIDATE") is True
    assert ddl_may_overwrite_status("CONFIRMED") is True
    assert ddl_may_overwrite_status("REJECTED") is False
    assert ddl_may_overwrite_status("DISABLED") is False


def test_extract_ddl_tool_is_read_only() -> None:
    import inspect

    from apps.datasource.profiling.tools_impl import MiningOps

    src = inspect.getsource(MiningOps.extract_ddl_constraints)
    assert "upsert_ddl_foreign_keys" not in src
    assert "published" in src


def test_worker_drain_stops_when_idle() -> None:
    from apps.datasource.profiling import worker as profiling_worker

    calls = {"n": 0}

    def _once(*, max_jobs: int = 8) -> int:
        calls["n"] += 1
        return 0

    original = profiling_worker.run_profiling_worker_once
    profiling_worker.run_profiling_worker_once = _once  # type: ignore[assignment]
    try:
        assert profiling_worker.run_profiling_worker_drain(max_rounds=5) == 0
        assert calls["n"] == 1
    finally:
        profiling_worker.run_profiling_worker_once = original  # type: ignore[assignment]
