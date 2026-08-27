from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.datasource.recall import value_index as vi  # noqa: E402
from common.core.config import settings  # noqa: E402


def _entry(table: str, field: str, value: str, source: str = "profile") -> vi._IndexEntry:
    from apps.dictionary.matching import normalize_dictionary_value

    return vi._IndexEntry(
        table_name=table,
        field_name=field,
        value=value,
        normalized_value=normalize_dictionary_value(value),
        source=source,
    )


def test_top_values_accepts_scalars_and_dicts() -> None:
    assert vi._iter_top_values(None, top_k=5) == []
    assert vi._iter_top_values(["a", {"value": "b"}, None, ""], top_k=5) == ["a", "b"]
    assert vi._iter_top_values(list(range(10)), top_k=3) == ["0", "1", "2"]


def test_match_values_containment_and_dedup(monkeypatch) -> None:
    monkeypatch.setattr(settings, "RECALL_VALUE_INDEX_ENABLED", True)
    entries = (
        _entry("d_organization", "organization_name", "研发二部"),
        _entry("d_organization", "org_name", "研发二部"),
        _entry("d_organization", "organization_name", "研发"),
        _entry("d_task", "task_name", "某任务"),
    )
    monkeypatch.setattr(vi, "_get_index", lambda session, *, oid, ds_id: entries)
    vi.clear_value_index_cache()

    hits = vi.match_values(object(), "帮我统计研发二部每月的task数", oid=1, ds_id=8)

    tables = {(hit.table_name, hit.field_name) for hit in hits}
    assert ("d_organization", "organization_name") in tables
    assert ("d_organization", "org_name") in tables
    assert ("d_task", "task_name") not in tables  # 值未出现在问题文本
    # 同 (table, field) 保留最长匹配值（"研发" 与 "研发二部" 都命中, 留后者）
    org_hits = [
        hit for hit in hits if hit.field_name == "organization_name"
    ]
    assert org_hits and org_hits[0].value == "研发二部"


def test_match_values_respects_access_fence_and_flag(monkeypatch) -> None:
    monkeypatch.setattr(settings, "RECALL_VALUE_INDEX_ENABLED", True)
    entries = (
        _entry("d_organization", "organization_name", "研发二部"),
        _entry("d_user", "dept", "研发二部"),
    )
    monkeypatch.setattr(vi, "_get_index", lambda session, *, oid, ds_id: entries)

    fenced = vi.match_values(
        object(),
        "研发二部",
        oid=1,
        ds_id=8,
        allowed_tables=frozenset({"d_user"}),
    )
    assert [hit.table_name for hit in fenced] == ["d_user"]

    monkeypatch.setattr(settings, "RECALL_VALUE_INDEX_ENABLED", False)
    assert vi.match_values(object(), "研发二部", oid=1, ds_id=8) == []


def test_index_rebuild_only_on_stamp_drift(monkeypatch) -> None:
    monkeypatch.setattr(settings, "RECALL_VALUE_INDEX_ENABLED", True)
    vi.clear_value_index_cache()
    stamps = [(1, 10, 1, 3)]
    builds = []
    entries = (_entry("d_organization", "organization_name", "研发二部"),)
    monkeypatch.setattr(
        vi, "_generation_stamp", lambda session, *, oid, ds_id: stamps[-1]
    )
    monkeypatch.setattr(
        vi,
        "_build_entries",
        lambda session, *, oid, ds_id: builds.append(1) or entries,
    )

    assert vi.match_values(object(), "研发二部在哪", oid=1, ds_id=8)
    assert vi.match_values(object(), "研发二部在哪", oid=1, ds_id=8)
    assert len(builds) == 1  # 同 stamp 复用进程内副本

    stamps.append((1, 11, 1, 3))  # 字典重新发布
    assert vi.match_values(object(), "研发二部在哪", oid=1, ds_id=8)
    assert len(builds) == 2
    vi.clear_value_index_cache()
