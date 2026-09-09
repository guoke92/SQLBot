from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.steps import recall_map as rmap  # noqa: E402


class _FakeExec:
    def __init__(self, rows):
        self._rows = rows

    def all(self):
        return self._rows


class _FakeSession:
    def __init__(self, responses):
        self._responses = list(responses)

    def exec(self, stmt):
        return _FakeExec(self._responses.pop(0))


def _table(name: str, comment: str = "", rows: int | None = None, db: str = ""):
    return SimpleNamespace(
        table_name=name,
        custom_comment=comment,
        approx_rows=rows,
        database_name=db,
    )


def test_schema_map_full_tier_one_line_per_table() -> None:
    session = _FakeSession(
        [
            [
                _table("d_organization", "组织机构：部门/团队层级", 120),
                _table("d_task", "任务", 9000),
            ]
        ]
    )
    text = rmap.render_schema_map(session, ds=SimpleNamespace(id=8))
    assert text.startswith("【Schema map】(2 tables")
    assert "d_organization | 组织机构：部门/团队层级 | ~120行" in text
    assert "d_task | 任务 | ~9000行" in text


def test_schema_map_access_scope_fence() -> None:
    from apps.datasource.access import AccessScope

    session = _FakeSession([[_table("d_task"), _table("d_secret")]])
    scope = AccessScope(resource_names=("d_task",))
    text = rmap.render_schema_map(session, ds=SimpleNamespace(id=8), access_scope=scope)
    assert "d_task" in text
    assert "d_secret" not in text
    assert "(1 tables" in text


def test_schema_map_dropped_beyond_catalog_max() -> None:
    """超过 _CATALOG_MAP_MAX 张表 → 不下发地图（知识包兑底）。"""
    tables = [_table(f"t{i:03d}") for i in range(rmap._CATALOG_MAP_MAX + 1)]
    text = rmap.render_schema_map(_FakeSession([tables]), ds=SimpleNamespace(id=8))
    assert text == ""


def test_schema_map_excludes_schema_window_tables() -> None:
    """窗口内表从地图剔除 — 地图是窗口的补集。"""
    tables = [_table("d_task", "任务"), _table("d_organization", "机构表")]
    text = rmap.render_schema_map(
        _FakeSession([tables]),
        ds=SimpleNamespace(id=8),
        exclude={"d_task"},
    )
    assert "d_task" not in text
    assert "d_organization" in text
    assert "(1 tables" in text


def test_schema_map_empty_catalog() -> None:
    assert rmap.render_schema_map(_FakeSession([[]]), ds=SimpleNamespace(id=8)) == ""
    assert rmap.render_schema_map(_FakeSession([[]]), ds=SimpleNamespace(id=0)) == ""


def test_knowledge_map_unbound_corpus_is_empty(monkeypatch) -> None:
    from common.core.config import settings

    monkeypatch.setattr(settings, "KNOWLEDGE_BACKEND", "wiki")
    monkeypatch.setattr("apps.chat.steps.wiki_recall._store", lambda ds_id=None: None)
    assert rmap.render_knowledge_map(_FakeSession([[]]), oid=1, ds_id=8) == ""


def test_knowledge_map_empty(monkeypatch) -> None:
    from common.core.config import settings

    monkeypatch.setattr(settings, "KNOWLEDGE_BACKEND", "unit")
    assert rmap.render_knowledge_map(_FakeSession([[]]), oid=1, ds_id=8) == ""


def test_knowledge_map_wiki_backend_renders_pages(monkeypatch) -> None:
    """wiki 后端：页面清单渲染（published 页一行一条，封顶+more）。"""
    from apps.knowledge.wiki.contract import parse_page
    from apps.knowledge.wiki.recall import InMemoryWikiStore
    from common.core.config import settings

    monkeypatch.setattr(settings, "KNOWLEDGE_BACKEND", "wiki")
    monkeypatch.setattr(settings, "KNOWLEDGE_WIKI_DS_ALLOWLIST", "*")
    pages = [
        parse_page(
            f"---\ntype: rule\ntitle: 规则{i}\npage_key: rule_{i}\nstatus: published\n"
            f"oid: 1\nscope:\n  databases: [db_x]\n---\n- [[x]]\n规则{i}正文",
            page_key=f"rule_{i}",
        )
        for i in range(3)
    ]
    store = InMemoryWikiStore(pages)
    monkeypatch.setattr("apps.chat.steps.wiki_recall._store", lambda ds_id=None: store)
    text = rmap.render_knowledge_map(
        _FakeSession([[]]), oid=1, ds_id=8, databases=["db_x"]
    )
    assert "wiki 页面" in text
    assert "rule_0" in text and "规则0" in text
    # scope.databases 围栏是严格交集：库名不相交/未传库名 → 声明围栏的页不可见
    fenced = rmap.render_knowledge_map(
        _FakeSession([[]]), oid=1, ds_id=8, databases=["other_db"]
    )
    assert fenced == ""
    no_db = rmap.render_knowledge_map(_FakeSession([[]]), oid=1, ds_id=8)
    assert no_db == ""
