"""Unit tests for metadata cognition helpers."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from apps.datasource.profiling.fingerprint import table_schema_fingerprint
from apps.datasource.profiling.models import ScanRunMode
from apps.datasource.profiling.tools import build_mining_tools
from apps.datasource.profiling.tools_impl import _normalize_name


def test_table_schema_fingerprint_stable_and_order_insensitive_by_index() -> None:
    table = SimpleNamespace(database_name="db1", table_name="orders")
    fields_a = [
        SimpleNamespace(field_index=1, field_name="id", field_type="bigint"),
        SimpleNamespace(field_index=2, field_name="amount", field_type="decimal"),
    ]
    fields_b = list(reversed(fields_a))
    assert table_schema_fingerprint(table, fields_a) == table_schema_fingerprint(
        table, fields_b
    )


def test_table_schema_fingerprint_changes_on_type() -> None:
    table = SimpleNamespace(database_name="", table_name="orders")
    a = [SimpleNamespace(field_index=0, field_name="id", field_type="int")]
    b = [SimpleNamespace(field_index=0, field_name="id", field_type="bigint")]
    assert table_schema_fingerprint(table, a) != table_schema_fingerprint(table, b)


def test_normalize_name_strips_id_suffix() -> None:
    assert _normalize_name("user_id") == "user"
    assert _normalize_name("CustomerID") == "customer"
    assert _normalize_name("order_code") == "order"


def test_validate_mode_excludes_heavy_collect_tools() -> None:
    tools = build_mining_tools(
        oid=1,
        ds_id=1,
        table_id=1,
        run_mode=ScanRunMode.VALIDATE.value,
        allow_confirm=False,
    )
    names = {t.name for t in tools}
    assert "overlap_probe" in names
    assert "run_table_profile" not in names
    assert "refresh_catalog_stats" not in names
    assert "confirm_relation" not in names


def test_agent_modes_do_not_enqueue_facts_tools() -> None:
    for mode in (
        ScanRunMode.SEMANTIC.value,
        ScanRunMode.FULL.value,
        ScanRunMode.MANUAL.value,
    ):
        names = {
            t.name
            for t in build_mining_tools(
                oid=1, ds_id=1, table_id=1, run_mode=mode, allow_confirm=False
            )
        }
        assert "run_table_profile" not in names


def test_semantic_mode_includes_samples_and_probes() -> None:
    tools = build_mining_tools(
        oid=1,
        ds_id=1,
        table_id=1,
        run_mode=ScanRunMode.SEMANTIC.value,
        allow_confirm=False,
    )
    names = {t.name for t in tools}
    assert {
        "get_samples",
        "name_similarity",
        "cooccurrence_probe",
        "formula_probe",
        "hierarchy_probe",
        "draft_field_description",
    } <= names


def test_format_profile_field_bits() -> None:
    from apps.datasource.profiling.fingerprint import format_profile_field_bits

    bits = format_profile_field_bits(
        null_rate=0.1, distinct_ratio=0.85, min_value="1", max_value="9"
    )
    assert bits[0] == "null=0.10"
    assert bits[1] == "ndv=0.85"
    assert "range=" in bits[2]


def test_format_profile_field_bits_topk_only_for_low_ndv() -> None:
    from apps.datasource.profiling.fingerprint import format_profile_field_bits

    low = format_profile_field_bits(
        distinct_ratio=0.02,
        top_values=[{"value": "A"}, {"value": "B"}, {"value": "C"}],
        include_topk=True,
        topk_limit=2,
    )
    assert any(b.startswith("topk=A|B") for b in low)

    high = format_profile_field_bits(
        distinct_ratio=0.5,
        top_values=[{"value": "A"}],
        include_topk=True,
    )
    assert not any(b.startswith("topk=") for b in high)


def test_profile_generation_ready_ratio() -> None:
    from apps.datasource.profiling.service import profile_generation_ready

    assert profile_generation_ready(success_count=None) is True
    assert profile_generation_ready(success_count=0) is False
    assert profile_generation_ready(success_count=5, attempted_count=10) is True
    assert profile_generation_ready(success_count=4, attempted_count=10) is False
    assert profile_generation_ready(success_count=3, attempted_count=None) is True


def test_publish_failure_marks_prior_generation_stale() -> None:
    from types import SimpleNamespace

    from apps.datasource.profiling.models import ProfileStatus
    from apps.datasource.profiling.service import publish_table_profile_generation

    table = SimpleNamespace(
        id=1,
        active_profile_generation=2,
        profile_status=ProfileStatus.PROFILING.value,
        profile_error=None,
        profile_updated_at=None,
    )

    class _Session:
        def add(self, _obj: object) -> None:
            return None

        def commit(self) -> None:
            return None

    published = publish_table_profile_generation(
        _Session(),  # type: ignore[arg-type]
        table=table,  # type: ignore[arg-type]
        generation=3,
        success_count=1,
        attempted_count=10,
        commit=False,
    )
    assert published is False
    assert table.active_profile_generation == 2
    assert table.profile_status == ProfileStatus.STALE.value


def test_claim_next_run_reclaim_does_not_burn_attempt(monkeypatch: pytest.MonkeyPatch) -> None:
    from datetime import datetime, timedelta

    from apps.datasource.profiling.models import ScanRunStatus
    from apps.datasource.profiling.service import claim_next_run

    now = datetime.now()
    run = SimpleNamespace(
        id=9,
        status=ScanRunStatus.RUNNING.value,
        attempt=1,
        max_attempts=3,
        lease_until=now - timedelta(seconds=10),
        lease_owner="old",
        started_at=now - timedelta(minutes=5),
        update_time=now,
        error="stale",
        finished_at=None,
        table_id=1,
    )

    class _Exec:
        def first(self):
            return run

    class _Session:
        def exec(self, _stmt):
            return _Exec()

        def add(self, _obj):
            return None

        def commit(self):
            return None

        def refresh(self, _obj):
            return None

    claimed = claim_next_run(_Session(), worker_id="new")  # type: ignore[arg-type]
    assert claimed is run
    assert run.attempt == 1
    assert run.lease_owner == "new"
    assert run.status == ScanRunStatus.RUNNING.value


def test_worker_finalize_partial_when_not_published(monkeypatch: pytest.MonkeyPatch) -> None:
    from apps.datasource.profiling.models import ProfileStatus, ScanRunMode
    from apps.datasource.profiling import worker as worker_mod

    calls: list[str] = []

    class _Session:
        pass

    run = object()

    monkeypatch.setattr(
        worker_mod,
        "mark_run_partial",
        lambda _s, _r, *, detail=None: calls.append(f"partial:{detail}"),
    )
    monkeypatch.setattr(
        worker_mod,
        "mark_run_succeeded",
        lambda _s, _r: calls.append("succeeded"),
    )

    worker_mod._finalize_run(
        _Session(),  # type: ignore[arg-type]
        run=run,
        mode=ScanRunMode.FACTS_ONLY.value,
        result={
            "status": ProfileStatus.STALE.value,
            "published": False,
            "errors": ["too sparse"],
        },
        needs_facts=True,
    )
    assert calls == ["partial:too sparse"]

    calls.clear()
    worker_mod._finalize_run(
        _Session(),  # type: ignore[arg-type]
        run=run,
        mode=ScanRunMode.FACTS_ONLY.value,
        result={"status": ProfileStatus.READY.value, "published": True},
        needs_facts=True,
    )
    assert calls == ["succeeded"]


def test_content_fingerprint_stable() -> None:
    from apps.datasource.profiling.fingerprint import content_fingerprint

    assert content_fingerprint("abc") == content_fingerprint("abc")
    assert content_fingerprint("abc") != content_fingerprint("abd")


def test_upsert_equi_requires_suggest_candidate_true() -> None:
    from apps.datasource.profiling.tools_impl import MiningContext, MiningOps

    ops = MiningOps(MiningContext(oid=1, ds_id=1, table_id=1, run_mode="semantic"))
    src = SimpleNamespace(id=1, ds_id=1, table_id=10)
    dst = SimpleNamespace(id=2, ds_id=1, table_id=11)

    class _Session:
        def get(self, model, pk):  # noqa: ANN001
            return {1: src, 2: dst}.get(pk)

    rejected = ops.upsert_relation_candidate(
        _Session(),  # type: ignore[arg-type]
        source_field_id=1,
        target_field_id=2,
        kind="EQUI_JOIN",
        evidence={"inclusion_score": 0.1, "suggest_candidate": False},
    )
    assert rejected.get("ok") is False
    assert "suggest_candidate" in str(rejected.get("error") or rejected)

    rejected_missing = ops.upsert_relation_candidate(
        _Session(),  # type: ignore[arg-type]
        source_field_id=1,
        target_field_id=2,
        kind="EQUI_JOIN",
        evidence={"inclusion_score": 0.9},
    )
    assert rejected_missing.get("ok") is False


def test_metadata_graph_nodes_renew_lease_on_agent_path() -> None:
    root = Path(__file__).resolve().parents[1]
    nodes_text = (
        root / "backend/apps/datasource/profiling/graphs/nodes.py"
    ).read_text(encoding="utf-8")
    yaml_text = (root / "backend/graphs/current/metadata.yaml").read_text(
        encoding="utf-8"
    )
    assert "def _renew_scan_lease" in nodes_text
    assert "renew_run_lease" in nodes_text
    assert "shared_agent_node" in nodes_text
    assert "shared_execute_tools" in nodes_text
    assert "apps.datasource.profiling.graphs.nodes.agent_node" in yaml_text
    assert "apps.datasource.profiling.graphs.nodes.execute_tools_node" in yaml_text


def test_draft_tools_never_auto_apply_in_mining_agent() -> None:
    """Mining wrappers hard-disable allow_apply so weak text cannot publish."""
    import inspect

    from apps.datasource.profiling import tools as mining_tools

    src = inspect.getsource(mining_tools.build_mining_tools)
    assert "allow_apply=False" in src


def test_worker_rejects_failed_graph_outcome() -> None:
    from apps.conversation.outcome import failed_outcome, outcome_is_success

    assert not outcome_is_success(failed_outcome("boom"))
    assert not outcome_is_success({"status": "failed"})


def test_field_relations_from_graph_extracts_equi_pairs() -> None:
    from apps.datasource.relation_service import field_relations_from_graph

    pairs = field_relations_from_graph(
        [
            {"id": 1, "shape": "er-rect"},
            {
                "id": "e1",
                "shape": "edge",
                "source": {"cell": 11, "port": 21},
                "target": {"cell": 12, "port": 23},
            },
        ]
    )
    assert pairs == [
        {
            "source_table_id": 11,
            "source_field_id": 21,
            "target_table_id": 12,
            "target_field_id": 23,
        }
    ]
