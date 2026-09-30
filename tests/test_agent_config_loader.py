"""Agent runtime configuration: override resolution, caching, validation."""

import json
import threading
from collections.abc import Iterator
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from apps.chat.agent_config import loader
from apps.chat.agent_config.defaults import (
    DEFAULT_TOOL_NAMES,
    LOOP_PARAM_DEFAULTS,
    LOOP_PARAM_SPECS,
    default_tools,
)
from apps.chat.agent_config.models import AgentConfigSaveRequest, AgentConfigSnapshot
from apps.chat.agent_config.service import (
    ConfigValidationError,
    default_snapshot,
    validate_snapshot,
)
from apps.chat.agent_knowledge import EXECUTION_ROUND_LIMIT
from apps.chat.task.agent_prompt import _SYSTEM_PROMPT_TEMPLATE


@pytest.fixture(autouse=True)
def _no_db(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Every test is hermetic: no test may depend on a reachable database."""
    monkeypatch.delenv(loader.DISABLE_ENV, raising=False)
    monkeypatch.setattr(loader, "read_published", lambda session: None)
    loader.invalidate_agent_config()
    yield
    loader.invalidate_agent_config()


def _row(**overrides: Any) -> SimpleNamespace:
    payload: dict[str, Any] = {
        "version_no": 1,
        "prompt_body": _SYSTEM_PROMPT_TEMPLATE,
        "tools": {},
        "loop_params": {},
    }
    payload.update(overrides)
    return SimpleNamespace(**payload)


def _published(monkeypatch: pytest.MonkeyPatch, row: Any) -> None:
    monkeypatch.setattr(loader, "read_published", lambda session: row)


def test_no_published_row_equals_code_defaults() -> None:
    config = loader.load_agent_config()
    assert config.prompt_version == "code"
    assert config.prompt_template == _SYSTEM_PROMPT_TEMPLATE
    assert config.param("execution_round_limit", -1) == EXECUTION_ROUND_LIMIT
    assert config.loop_params == LOOP_PARAM_DEFAULTS
    assert set(config.tools) == set(DEFAULT_TOOL_NAMES)


def test_disable_env_skips_db_entirely(monkeypatch: pytest.MonkeyPatch) -> None:
    def _explode(_session: Any) -> Any:
        raise AssertionError("DB must not be touched when disabled")

    monkeypatch.setenv(loader.DISABLE_ENV, "1")
    monkeypatch.setattr(loader, "read_published", _explode)
    assert loader.load_agent_config().prompt_version == "code"


def test_published_row_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    _published(
        monkeypatch,
        _row(
            version_no=7,
            prompt_body="OVERRIDE {execution_limit}",
            tools={
                "get_table_schema": {"enabled": False},
                "lookup_values": {"description": "custom text"},
            },
            loop_params={"execution_round_limit": 3},
        ),
    )
    config = loader.load_agent_config()
    assert config.prompt_version == "v7"
    assert config.prompt_template == "OVERRIDE {execution_limit}"
    assert config.param("execution_round_limit", -1) == 3
    assert config.tool_enabled("get_table_schema") is False
    assert config.tool_parallel_safe("get_table_schema") is False
    assert config.tool_description("lookup_values", "inline") == "custom text"
    # Untouched keys keep code defaults.
    assert config.tool_description("get_dict_values", "inline") == "inline"
    assert config.param("probe_sql_limit", -1) == LOOP_PARAM_DEFAULTS["probe_sql_limit"]


def test_unknown_and_out_of_range_values_are_ignored(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _published(
        monkeypatch,
        _row(
            tools={"not_a_tool": {"enabled": False}},
            loop_params={"execution_round_limit": 999, "nope": 1},
        ),
    )
    config = loader.load_agent_config()
    assert "not_a_tool" not in config.tools
    assert config.param("execution_round_limit", -1) == 20  # clamped to spec max
    assert "nope" not in config.loop_params


def test_required_tool_is_re_enabled_at_read_time(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Defence in depth: a hand-edited row cannot brick the agent's exits."""
    _published(
        monkeypatch,
        _row(tools={"request_clarification": {"enabled": False}}),
    )
    assert loader.load_agent_config().tool_enabled("request_clarification") is True


def test_db_failure_degrades_to_code_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _boom(_session: Any) -> Any:
        raise RuntimeError("connection refused")

    monkeypatch.setattr(loader, "read_published", _boom)
    config = loader.load_agent_config()
    assert config.prompt_version == "code"
    assert config.prompt_template == _SYSTEM_PROMPT_TEMPLATE


def test_corrupt_row_degrades_to_code_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _published(monkeypatch, _row(prompt_body="   "))
    assert loader.load_agent_config().prompt_template == _SYSTEM_PROMPT_TEMPLATE


def test_conversation_reads_do_not_poll_the_database(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = {"n": 0}

    def _read(_session: Any) -> Any:
        calls["n"] += 1
        return _row(version_no=1, prompt_body="FIRST {execution_limit}")

    monkeypatch.setattr(loader, "read_published", _read)
    assert loader.load_agent_config().prompt_template.startswith("FIRST")
    assert loader.load_agent_config().prompt_template.startswith("FIRST")
    assert calls["n"] == 1

    # A later published row is invisible until the cache is dropped or replaced.
    monkeypatch.setattr(
        loader,
        "read_published",
        lambda _session: _row(version_no=2, prompt_body="SECOND {execution_limit}"),
    )
    assert loader.load_agent_config().prompt_template.startswith("FIRST")
    loader.invalidate_agent_config()
    assert loader.load_agent_config().prompt_template.startswith("SECOND")


def test_install_replaces_the_cache_without_a_database_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = {"n": 0}

    def _read(_session: Any) -> Any:
        calls["n"] += 1
        return _row(version_no=1, prompt_body="FIRST {execution_limit}")

    monkeypatch.setattr(loader, "read_published", _read)
    loader.load_agent_config()
    loader.install_agent_config(
        loader.config_from_row(
            _row(version_no=2, prompt_body="SECOND {execution_limit}")
        )
    )
    assert loader.load_agent_config().prompt_version == "v2"
    assert calls["n"] == 1


def test_in_flight_load_cannot_overwrite_a_publish(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    entered = threading.Event()
    release = threading.Event()

    def _read(_session: Any) -> Any:
        entered.set()
        assert release.wait(2)
        return _row(version_no=1, prompt_body="OLD {execution_limit}")

    monkeypatch.setattr(loader, "read_published", _read)
    found: dict[str, Any] = {}

    def _load() -> None:
        found["config"] = loader.load_agent_config()

    thread = threading.Thread(target=_load)
    thread.start()
    assert entered.wait(2)
    loader.install_agent_config(
        loader.config_from_row(_row(version_no=2, prompt_body="NEW {execution_limit}"))
    )
    release.set()
    thread.join(2)
    assert not thread.is_alive()
    assert found["config"].prompt_template.startswith("NEW")
    assert loader.load_agent_config().prompt_template.startswith("NEW")


def test_default_tool_names_match_the_registry() -> None:
    """Drift guard: a new tool must show up on the management page."""
    from apps.chat.tools.registry import build_agent_tools

    tools = build_agent_tools(SimpleNamespace(ds=None, datasource=None))
    assert {tool.name for tool in tools} == set(DEFAULT_TOOL_NAMES)


def test_tool_filters_and_description_override() -> None:
    from apps.chat.tools.registry import build_agent_tools

    service = SimpleNamespace(ds=None, datasource=None)
    baseline = build_agent_tools(service)
    assert baseline[0].name == "get_table_schema"

    config = loader.AgentRuntimeConfig(
        prompt_template=_SYSTEM_PROMPT_TEMPLATE,
        prompt_version="code",
        tools={
            **{name: dict(cfg) for name, cfg in default_tools().items()},
            "get_table_schema": {
                "enabled": False,
                "description": None,
                "parallel_safe": True,
                "round_budget": None,
            },
            "lookup_values": {
                "enabled": True,
                "description": "short override",
                "parallel_safe": True,
                "round_budget": None,
            },
        },
        loop_params=dict(LOOP_PARAM_DEFAULTS),
    )
    names = [tool.name for tool in build_agent_tools(service, config=config)]
    assert "get_table_schema" not in names
    assert len(names) == len(DEFAULT_TOOL_NAMES) - 1
    custom = build_agent_tools(service, config=config)
    lookup = next(tool for tool in custom if tool.name == "lookup_values")
    assert lookup.description == "short override"
    # Untouched tools keep their literal description byte-for-byte.
    base_search = next(tool for tool in baseline if tool.name == "search_knowledge")
    custom_search = next(tool for tool in custom if tool.name == "search_knowledge")
    assert custom_search.description == base_search.description


# --------------------------------------------------------------------------- #
# Validation
# --------------------------------------------------------------------------- #


def _snapshot(**overrides: Any) -> AgentConfigSnapshot:
    data = default_snapshot().model_dump()
    data.update(overrides)
    return AgentConfigSnapshot.model_validate(data)


def test_default_snapshot_is_valid() -> None:
    cleaned = validate_snapshot(_snapshot())
    assert cleaned.prompt_body == _SYSTEM_PROMPT_TEMPLATE
    assert set(cleaned.loop_params) == set(LOOP_PARAM_DEFAULTS)


@pytest.mark.parametrize(
    ("overrides", "key"),
    [
        ({"prompt_body": "   "}, "agent_config.err_prompt_empty"),
        ({"prompt_body": "too short"}, "agent_config.err_prompt_length"),
        (
            {"prompt_body": _SYSTEM_PROMPT_TEMPLATE.replace("{execution_limit}", "5")},
            "agent_config.err_prompt_placeholder_missing",
        ),
        (
            {"prompt_body": "extra {rogue_placeholder}\n" + _SYSTEM_PROMPT_TEMPLATE},
            "agent_config.err_prompt_placeholder_invalid",
        ),
        ({"loop_params": {"nope": 3}}, "agent_config.err_param_unknown"),
        (
            {"loop_params": {"execution_round_limit": 99}},
            "agent_config.err_param_range",
        ),
        (
            {"tools": {"nope": {"enabled": True}}},
            "agent_config.err_tool_unknown",
        ),
        (
            {"tools": {"request_clarification": {"enabled": False}}},
            "agent_config.err_tool_required",
        ),
        (
            {"tools": {"get_table_schema": {"round_budget": 999}}},
            "agent_config.err_tool_budget",
        ),
    ],
)
def test_invalid_snapshots_are_rejected(overrides: dict[str, Any], key: str) -> None:
    with pytest.raises(ConfigValidationError) as excinfo:
        validate_snapshot(_snapshot(**overrides))
    assert excinfo.value.key == key


def test_escaped_braces_in_the_prompt_are_allowed() -> None:
    """The shipped prompt contains ``{{option_id, ...}}`` literals — must pass."""
    assert "{{option_id" in _SYSTEM_PROMPT_TEMPLATE
    validate_snapshot(_snapshot())


def test_fully_escaped_execution_limit_is_rejected() -> None:
    body = _SYSTEM_PROMPT_TEMPLATE.replace("{execution_limit}", "{{execution_limit}}")
    with pytest.raises(ConfigValidationError) as excinfo:
        validate_snapshot(_snapshot(prompt_body=body))
    assert excinfo.value.key == "agent_config.err_prompt_placeholder_missing"


def test_dropped_required_section_is_rejected() -> None:
    body = _SYSTEM_PROMPT_TEMPLATE.replace("## 6. 最终回答", "## 六 最终回答")
    with pytest.raises(ConfigValidationError) as excinfo:
        validate_snapshot(_snapshot(prompt_body=body))
    assert excinfo.value.key == "agent_config.err_prompt_section_missing"


def test_tool_description_override_must_not_be_overlong() -> None:
    with pytest.raises(ConfigValidationError) as excinfo:
        validate_snapshot(
            _snapshot(tools={"get_table_schema": {"description": "x" * 2001}})
        )
    assert excinfo.value.key == "agent_config.err_tool_description"


def test_save_request_round_trips_through_validation() -> None:
    payload = AgentConfigSaveRequest.model_validate(default_snapshot().model_dump())
    cleaned = validate_snapshot(payload)
    assert cleaned.change_note is None
    assert cleaned.tools["execute_sql_sandbox"].enabled is True


# --------------------------------------------------------------------------- #
# Management-page contract
# --------------------------------------------------------------------------- #


def test_meta_exposes_every_tool_and_param() -> None:
    """The page renders whatever the API advertises — no second source of truth."""
    from apps.chat.agent_config.api import build_meta

    meta = build_meta()
    assert meta["tool_names"] == list(DEFAULT_TOOL_NAMES)
    assert [param["key"] for param in meta["params"]] == [
        spec.key for spec in LOOP_PARAM_SPECS
    ]
    assert set(meta["required_tool_names"]) <= set(meta["tool_names"])
    bounds = meta["tool_round_budget"]
    assert bounds["min"] == 0 and bounds["max"] == 20
    assert meta["prompt"]["placeholder"] in _SYSTEM_PROMPT_TEMPLATE


def test_frontend_i18n_covers_tools_and_params() -> None:
    """Drift guard: a new tool/param must not render as a raw identifier."""
    root = Path(__file__).resolve().parents[1] / "frontend" / "src" / "i18n"
    for name in ("zh-CN.json", "en.json"):
        payload = json.loads((root / name).read_text(encoding="utf-8"))
        namespace = payload["agent_config"]
        for tool in DEFAULT_TOOL_NAMES:
            assert tool in namespace["tools"], f"{name}: agent_config.tools.{tool}"
        for spec in LOOP_PARAM_SPECS:
            assert spec.label_key in namespace["params"], (
                f"{name}: agent_config.params.{spec.label_key}"
            )
        # Keys the page looks up dynamically must exist too.
        for status in ("draft", "published", "archived"):
            assert namespace.get(f"status_{status}"), f"{name}: status_{status}"
        assert {"code", "published", "draft"} <= set(namespace["source"])
