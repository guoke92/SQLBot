"""Worker session nesting, audit isolation, and AccessScope DTO regressions."""

from __future__ import annotations

import sys
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from sqlalchemy import Column, Integer, String, create_engine, inspect
from sqlalchemy.orm import Session, declarative_base, scoped_session, sessionmaker

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.models.chat_model import OperationEnum  # noqa: E402
from apps.chat.steps.observability import log_span  # noqa: E402
from apps.conversation import session as session_mod  # noqa: E402
from apps.datasource.access import AccessScope, access_scope_fingerprint  # noqa: E402


def _sqlite_factory() -> Any:
    engine = create_engine("sqlite://")
    return scoped_session(sessionmaker(bind=engine, class_=Session)), engine


def test_nested_session_scope_keeps_outer_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    factory, _engine = _sqlite_factory()
    monkeypatch.setattr(session_mod, "session_factory", factory)
    session_mod._scope_state.depth = 0

    with session_mod.session_scope() as outer:
        with session_mod.session_scope() as inner:
            assert inner is outer
        assert factory() is outer
        assert outer.is_active

    replacement = factory()
    try:
        assert replacement is not outer
    finally:
        factory.remove()


def test_log_span_does_not_detach_worker_orm(monkeypatch: pytest.MonkeyPatch) -> None:
    Base = declarative_base()

    class Widget(Base):  # type: ignore[misc, valid-type]
        __tablename__ = "widgets"
        id = Column(Integer, primary_key=True)
        table_name = Column(String)

    worker_engine = create_engine("sqlite://")
    Base.metadata.create_all(worker_engine)
    worker_factory = scoped_session(sessionmaker(bind=worker_engine, class_=Session))
    audit_engine = create_engine("sqlite://")
    audit_maker = sessionmaker(bind=audit_engine, class_=Session)
    started: list[Any] = []

    monkeypatch.setattr(session_mod, "session_factory", worker_factory)
    session_mod._scope_state.depth = 0

    @contextmanager
    def independent_audit_session():
        session = audit_maker()
        try:
            yield session
        finally:
            session.close()

    def fake_start_log(session: Session, **_kwargs: Any) -> Any:
        started.append(session)
        session.commit()
        return SimpleNamespace(id=1)

    def fake_end_log(session: Session, **_kwargs: Any) -> Any:
        session.commit()
        return SimpleNamespace(id=1)

    monkeypatch.setattr(
        "apps.chat.steps.observability.audit_session", independent_audit_session
    )
    monkeypatch.setattr("apps.chat.steps.observability._start_log", fake_start_log)
    monkeypatch.setattr("apps.chat.steps.observability._end_log", fake_end_log)

    seed = worker_factory()
    seed.add(Widget(id=1, table_name="orders"))
    seed.commit()
    worker_factory.remove()

    with session_mod.session_scope() as session:
        widget = session.get(Widget, 1)
        assert widget is not None
        with log_span(
            operate=OperationEnum.CHOOSE_TABLE,
            record_id=1,
            run_id="run-test",
            graph_node="execute_queries",
            brief="refresh schema",
        ):
            assert started and started[0] is not session
            assert inspect(widget).detached is False
            assert widget.table_name == "orders"
            assert worker_factory() is session


def test_access_scope_is_orm_free_dto() -> None:
    scope = AccessScope(
        resource_names=("orders", "payments"),
        allowed_targets=frozenset({(1, 10)}),
        row_filters=({"table": "orders", "filter": "oid=1"},),
        row_restricted_tables=frozenset({"orders"}),
    )
    fingerprint = access_scope_fingerprint(scope)

    assert scope.resource_names == ("orders", "payments")
    assert len(fingerprint) == 64
    assert not hasattr(scope, "table_objects")
    with pytest.raises(TypeError):
        AccessScope(table_objects=())  # type: ignore[call-arg]


def test_access_scope_snapshot_outlives_orm_payload() -> None:
    table = SimpleNamespace(id=7, table_name="fin_list")
    field = SimpleNamespace(id=21)
    scope = AccessScope(
        resource_names=(table.table_name,),
        allowed_targets=frozenset({(int(table.id), int(field.id))}),
    )

    del table.table_name
    del table.id
    del field.id

    assert scope.resource_names == ("fin_list",)
    assert scope.allowed_targets == frozenset({(7, 21)})
    assert access_scope_fingerprint(scope)


def test_project_schema_resources_never_uses_fence_as_projection() -> None:
    from apps.datasource.access import project_schema_resources

    scope = AccessScope(resource_names=("a", "b", "c"))
    assert project_schema_resources(None, scope) is None
    assert project_schema_resources(("b", "z"), scope) == ["b"]
    assert project_schema_resources((), scope) == []
    assert project_schema_resources(("z",), scope) == []
