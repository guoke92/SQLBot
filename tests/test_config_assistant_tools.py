from __future__ import annotations

import asyncio
import os
import sys
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

_BACKEND = Path(__file__).resolve().parents[1] / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))
os.environ["UPLOAD_DIR"] = "/tmp/sqlbot-test-file"

from common.core.config import settings  # noqa: E402

settings.UPLOAD_DIR = os.environ["UPLOAD_DIR"]

import sqlbot_xpack  # noqa: E402, F401  # main.py initializes xpack before app routes
from apps.config_assistant import nodes as config_nodes  # noqa: E402
from apps.config_assistant.tools import dictionary as dictionary_tools  # noqa: E402
from apps.config_assistant.tools import metadata as metadata_tools  # noqa: E402
from apps.config_assistant.tools import terminology as terminology_tools  # noqa: E402
from apps.datasource import metadata_service, relation_service  # noqa: E402
from apps.datasource.crud import datasource as datasource_crud  # noqa: E402
from apps.datasource.models.datasource import (  # noqa: E402
    CoreDatasource,
    CoreField,
    CoreTable,
    CreateDatasource,
    TableObj,
)
from apps.chat.models.chat_model import Chat, ChatRecord  # noqa: E402
from apps.dictionary.models import (  # noqa: E402
    DictionaryRefreshResult,
    DictionaryStatus,
)
from apps.conversation import turn as conversation_turn  # noqa: E402


def _admin_user() -> SimpleNamespace:
    return SimpleNamespace(
        id=1,
        oid=1,
        isAdmin=True,
        weight=1,
        language="zh-CN",
    )


def test_config_turn_is_initialized_before_graph_submission(monkeypatch) -> None:
    calls: list[str] = []
    user = _admin_user()
    chat = Chat(
        id=7,
        oid=1,
        create_by=1,
        chat_type="config",
        datasource=None,
        engine_type="",
    )

    class FakeSession:
        def get(self, model, item_id):
            if model is Chat and item_id == 7:
                return chat
            return None

    async def fake_default_config():
        calls.append("model_config")
        return SimpleNamespace(model_id=3, model_name="test")

    monkeypatch.setattr(config_nodes, "get_default_chat_config", fake_default_config)
    monkeypatch.setattr(
        config_nodes,
        "build_tools",
        lambda _user: calls.append("tools") or [],
    )
    monkeypatch.setattr(
        config_nodes,
        "get_chat_model",
        lambda _config: calls.append("model") or object(),
    )
    monkeypatch.setattr(
        config_nodes,
        "load_text_history",
        lambda *_args, **_kwargs: calls.append("history") or [],
    )

    def fake_save_question(**_kwargs):
        calls.append("record")
        return ChatRecord(id=99, chat_id=7, question="list datasources")

    monkeypatch.setattr(config_nodes, "save_question", fake_save_question)
    state = asyncio.run(
        config_nodes.initialize_config_state(
            FakeSession(),
            user=user,
            chat_id=7,
            question=" list datasources ",
            base_state={"sink": "sse"},
        )
    )
    assert calls == ["model_config", "tools", "model", "history", "record"]
    assert state["record_id"] == 99
    assert state["question"] == "list datasources"
    assert state["outcome"]["status"] == "running"


def test_turn_failure_uses_shared_persistence_boundary(monkeypatch) -> None:
    session = object()

    @contextmanager
    def fake_session_scope():
        yield session

    persisted: list[tuple[object, int, bool, str]] = []
    monkeypatch.setattr(conversation_turn, "session_scope", fake_session_scope)
    monkeypatch.setattr(
        conversation_turn,
        "persist_snapshot",
        lambda current_session, record_id, *, terminal, error: persisted.append(
            (current_session, record_id, terminal, error)
        ),
    )
    conversation_turn.persist_turn_failure(99, "late failure")
    assert persisted == [(session, 99, True, "late failure")]


def test_datasource_tool_view_excludes_internal_payloads() -> None:
    datasource = CoreDatasource(
        id=7,
        name="demo",
        description="demo datasource",
        type="mysql",
        type_name="MySQL",
        configuration="encrypted",
        oid=1,
        create_by=1,
        status="Success",
        num="2",
        table_relation=[{"shape": "edge"}],
        embedding="[1,2,3]",
        recommended_config=1,
    )
    result = metadata_tools._public_ds(datasource)
    assert result["configuration_present"] is True
    assert "configuration" not in result
    assert "embedding" not in result
    assert "table_relation" not in result


def test_sql_datasource_configuration_requires_canonical_fields() -> None:
    with pytest.raises(ValueError, match="username"):
        metadata_tools._normalize_configuration(
            "starrocks",
            {
                "host": "db.local",
                "port": 9030,
                "user": "reader",
                "password": "secret",
                "database": "analytics",
            },
        )

    normalized = metadata_tools._normalize_configuration(
        "starrocks",
        {
            "host": "db.local",
            "port": 9030,
            "username": "reader",
            "password": "secret",
            "database": "analytics",
        },
    )
    assert normalized["username"] == "reader"
    assert "user" not in normalized


def test_create_datasource_validates_before_atomic_catalog_sync(
    monkeypatch,
) -> None:
    events: list[str] = []

    class FakeProtocol:
        def check_connection(self, _ds, _trans, is_raise):
            assert is_raise is True
            events.append("check")
            return True

        def get_tables(self, _ds):
            events.append("catalog")
            return [SimpleNamespace(tableName="orders", tableComment="Orders")]

        def supports(self, _capability):
            return False

        def engine_display_name(self, _ds):
            return "StarRocks"

    class FakeSession:
        added = None

        def add(self, item):
            events.append("add")
            self.added = item

        def flush(self):
            assert self.added is not None
            self.added.id = 77
            events.append("flush")

        def refresh(self, _item):
            events.append("refresh")

    protocol = FakeProtocol()
    monkeypatch.setattr(
        datasource_crud,
        "get_protocol_for_ds",
        lambda _ds: protocol,
    )
    monkeypatch.setattr(
        datasource_crud,
        "check_name",
        lambda *_args, **_kwargs: events.append("name"),
    )

    def fake_sync(_session, ds, tables):
        assert ds.id == 77
        assert [table.table_name for table in tables] == ["orders"]
        events.append("sync")

    monkeypatch.setattr(datasource_crud, "sync_catalog", fake_sync)
    result = asyncio.run(
        datasource_crud.create_ds(
            FakeSession(),
            lambda value: value,
            _admin_user(),
            CreateDatasource(
                name="analytics",
                type="starrocks",
                configuration="encrypted",
                tables=[CoreTable(table_name="orders", table_comment="Orders")],
            ),
        )
    )
    assert result.id == 77
    assert result.num == "1/1"
    assert events == [
        "name",
        "check",
        "catalog",
        "add",
        "flush",
        "refresh",
        "sync",
    ]


def test_metadata_service_uses_embedding_aware_table_write(monkeypatch) -> None:
    table = CoreTable(
        id=11,
        ds_id=7,
        checked=True,
        table_name="orders",
        table_comment="Orders",
        custom_comment="Orders",
    )

    class FakeSession:
        def get(self, _model, _id):
            return table

        def add(self, item) -> None:
            assert item is table

        def commit(self) -> None:
            pass

    monkeypatch.setattr(
        metadata_service, "run_save_table_embeddings", lambda _ids: None
    )
    monkeypatch.setattr(metadata_service, "run_save_ds_embeddings", lambda _ids: None)
    result = metadata_service.update_table_metadata(
        FakeSession(),
        table_id=11,
        checked=False,
        custom_comment="Order facts",
    )
    assert result.checked is False
    assert result.custom_comment == "Order facts"


def test_metadata_service_uses_embedding_aware_field_write(monkeypatch) -> None:
    field = CoreField(
        id=21,
        ds_id=7,
        table_id=11,
        checked=True,
        field_name="amount",
        field_type="decimal",
        field_comment="Amount",
        custom_comment="Amount",
        field_index=1,
    )

    class FakeSession:
        def get(self, _model, _id):
            return field

        def add(self, item) -> None:
            assert item is field

        def commit(self) -> None:
            pass

    monkeypatch.setattr(
        metadata_service, "run_save_table_embeddings", lambda _ids: None
    )
    monkeypatch.setattr(metadata_service, "run_save_ds_embeddings", lambda _ids: None)
    result = metadata_service.update_field_metadata(
        FakeSession(),
        field_id=21,
        custom_comment="Order amount",
    )
    assert result.custom_comment == "Order amount"


def test_combined_metadata_write_rejects_field_from_another_table(
    monkeypatch,
) -> None:
    table = CoreTable(
        id=11,
        ds_id=7,
        checked=True,
        table_name="orders",
        table_comment="",
        custom_comment="",
    )
    foreign_field = CoreField(
        id=21,
        ds_id=7,
        table_id=12,
        checked=True,
        field_name="customer_id",
        field_type="bigint",
        field_comment="",
        custom_comment="",
        field_index=1,
    )

    class FakeSession:
        def get(self, model, item_id):
            if model is CoreTable and item_id == 11:
                return table
            if model is CoreField and item_id == 21:
                return foreign_field
            return None

        def add(self, _item) -> None:
            pass

        def commit(self) -> None:
            raise AssertionError("invalid metadata must not be committed")

    monkeypatch.setattr(
        metadata_service, "run_save_table_embeddings", lambda _ids: None
    )
    monkeypatch.setattr(metadata_service, "run_save_ds_embeddings", lambda _ids: None)
    incoming_table = table.model_copy()
    incoming_field = foreign_field.model_copy()
    incoming_field.table_id = 11
    try:
        metadata_service.update_table_and_fields_metadata(
            FakeSession(),
            TableObj(table=incoming_table, fields=[incoming_field]),
        )
    except ValueError as exc:
        assert "does not belong to table" in str(exc)
    else:
        raise AssertionError("foreign field metadata was accepted")


def test_dictionary_refresh_returns_partial_results(monkeypatch) -> None:
    @contextmanager
    def fake_session_scope():
        yield object()

    monkeypatch.setattr(dictionary_tools, "session_scope", fake_session_scope)
    monkeypatch.setattr(
        dictionary_tools,
        "refresh_configs",
        lambda *_args, **_kwargs: [
            DictionaryRefreshResult(
                id=1,
                status=DictionaryStatus.READY,
                value_count=3,
            ),
            DictionaryRefreshResult(
                id=2,
                status=DictionaryStatus.EMPTY,
                error="connection failed",
            ),
        ],
    )
    tool = next(
        item
        for item in dictionary_tools.build_dictionary_tools(_admin_user())
        if item.name == "refresh_dictionary_values"
    )
    result = tool.invoke({"config_ids": [1, 2]})
    assert result["ok"] is False
    assert result["summary"] == "Refreshed 1/2 dictionary fields"
    assert result["error"] == "1 dictionary field refreshes failed"
    assert [item["id"] for item in result["data"]] == [1, 2]


def test_create_terminology_tool_returns_created_id(monkeypatch) -> None:
    @contextmanager
    def fake_session_scope():
        yield object()

    monkeypatch.setattr(terminology_tools, "session_scope", fake_session_scope)
    monkeypatch.setattr(
        terminology_tools,
        "create_terminology",
        lambda *_args, **_kwargs: 42,
    )
    tool = next(
        item
        for item in terminology_tools.build_terminology_tools(_admin_user())
        if item.name == "save_terminology"
    )
    result = tool.invoke(
        {
            "word": "GMV",
            "description": "Gross merchandise value",
            "other_words": [],
            "datasource_ids": [],
            "enabled": True,
        }
    )
    assert result == {
        "ok": True,
        "summary": "Terminology created",
        "data": {
            "id": 42,
            "word": "GMV",
            "description": "Gross merchandise value",
            "other_words": [],
            "specific_ds": False,
            "datasource_ids": [],
            "enabled": True,
        },
        "error": None,
        "failure": None,
    }


def test_relation_replace_preserves_table_layout_and_complete_ports() -> None:
    datasource = CoreDatasource(
        id=7,
        name="demo",
        description="",
        type="mysql",
        type_name="MySQL",
        configuration="encrypted",
        oid=1,
        create_by=1,
        table_relation=[
            {
                "id": 11,
                "shape": "er-rect",
                "label": "old_orders",
                "position": {"x": 333, "y": 444},
                "ports": [],
            },
            {
                "id": 12,
                "shape": "er-rect",
                "label": "customers",
                "position": {"x": 555, "y": 666},
                "ports": [],
            },
            {
                "id": "old_edge",
                "shape": "edge",
                "source": {"cell": 11, "port": 21},
                "target": {"cell": 12, "port": 23},
            },
        ],
    )
    tables = {
        11: CoreTable(
            id=11,
            ds_id=7,
            checked=True,
            table_name="orders",
            table_comment="",
            custom_comment="",
        ),
        12: CoreTable(
            id=12,
            ds_id=7,
            checked=True,
            table_name="customers",
            table_comment="",
            custom_comment="",
        ),
    }
    fields = {
        21: CoreField(
            id=21,
            ds_id=7,
            table_id=11,
            checked=True,
            field_name="customer_id",
            field_type="bigint",
            field_comment="",
            custom_comment="",
            field_index=1,
        ),
        22: CoreField(
            id=22,
            ds_id=7,
            table_id=11,
            checked=True,
            field_name="amount",
            field_type="decimal",
            field_comment="",
            custom_comment="",
            field_index=2,
        ),
        23: CoreField(
            id=23,
            ds_id=7,
            table_id=12,
            checked=True,
            field_name="id",
            field_type="bigint",
            field_comment="",
            custom_comment="",
            field_index=1,
        ),
    }

    class FakeListQuery:
        def __init__(self, rows):
            self._rows = rows

        def filter(self, *_args):
            return self

        def order_by(self, *_args):
            return self

        def all(self):
            return list(self._rows)

    class FakeExecResult:
        def all(self):
            return []

        def first(self):
            return None

    class FakeSession:
        def get(self, model, item_id):
            if model is CoreDatasource:
                return datasource if item_id == 7 else None
            if model is CoreTable:
                return tables.get(item_id)
            if model is CoreField:
                return fields.get(item_id)
            return None

        def query(self, model):
            if model is CoreTable:
                return FakeListQuery(list(tables.values()))
            if model is CoreField:
                return FakeListQuery(list(fields.values()))
            return FakeListQuery([])

        def exec(self, _stmt):
            return FakeExecResult()

        def add(self, _item) -> None:
            pass

        def commit(self) -> None:
            pass

    graph = relation_service.replace_field_relations(
        FakeSession(),
        oid=1,
        ds_id=7,
        relations=[{"source_field_id": 21, "target_field_id": 23}],
    )
    nodes = {item["id"]: item for item in graph if item["shape"] != "edge"}
    assert nodes[11]["position"] == {"x": 333, "y": 444}
    assert nodes[12]["position"] == {"x": 555, "y": 666}
    assert [port["id"] for port in nodes[11]["ports"]["items"]] == [21, 22]

    invalid_graph = list(graph)
    invalid_graph[0] = {
        **invalid_graph[0],
        "ports": {"items": [{"id": 23, "group": "list"}]},
    }
    with pytest.raises(HTTPException, match="does not belong"):
        relation_service.save_relation_graph(
            FakeSession(),
            oid=1,
            ds_id=7,
            graph=invalid_graph,
        )


def test_relation_reconcile_prunes_stale_catalog_references() -> None:
    datasource = CoreDatasource(
        id=7,
        name="demo",
        description="",
        type="mysql",
        type_name="MySQL",
        configuration="encrypted",
        oid=1,
        create_by=1,
        table_relation=[
            {
                "id": 11,
                "shape": "er-rect",
                "label": "removed_orders",
                "position": {"x": 10, "y": 20},
                "ports": {"items": [{"id": 21, "group": "list"}]},
            },
            {
                "id": 12,
                "shape": "er-rect",
                "label": "old_customers",
                "position": {"x": 30, "y": 40},
                "ports": {"items": [{"id": 23, "group": "list"}]},
            },
            {
                "id": "removed_edge",
                "shape": "edge",
                "source": {"cell": 11, "port": 21},
                "target": {"cell": 12, "port": 23},
            },
        ],
    )
    table = CoreTable(
        id=12,
        ds_id=7,
        checked=True,
        table_name="customers",
        table_comment="",
        custom_comment="",
    )
    fields = [
        CoreField(
            id=23,
            ds_id=7,
            table_id=12,
            checked=True,
            field_name="id",
            field_type="bigint",
            field_comment="",
            custom_comment="",
            field_index=1,
        ),
        CoreField(
            id=24,
            ds_id=7,
            table_id=12,
            checked=True,
            field_name="name",
            field_type="varchar",
            field_comment="",
            custom_comment="",
            field_index=2,
        ),
    ]

    class FakeQuery:
        def __init__(self, model):
            self.model = model

        def filter(self, *_args):
            return self

        def order_by(self, *_args):
            return self

        def all(self):
            if self.model is CoreTable:
                return [table]
            if self.model is CoreField:
                return fields
            return []

    class FakeSession:
        commits = 0

        def get(self, model, item_id):
            if model is CoreDatasource and item_id == 7:
                return datasource
            return None

        def query(self, model):
            return FakeQuery(model)

        def add(self, _item) -> None:
            pass

        def commit(self) -> None:
            self.commits += 1

    session = FakeSession()
    graph = relation_service.reconcile_relation_graph(
        session,
        oid=1,
        ds_id=7,
        commit=False,
    )
    assert session.commits == 0
    assert len(graph) == 1
    assert graph[0]["id"] == 12
    assert graph[0]["label"] == "customers"
    assert graph[0]["position"] == {"x": 30, "y": 40}
    assert [port["id"] for port in graph[0]["ports"]["items"]] == [23, 24]
