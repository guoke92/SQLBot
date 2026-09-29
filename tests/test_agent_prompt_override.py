"""System prompt rendering honours the DB override and the per-turn frozen snapshot."""

from typing import Any

import pytest

from apps.chat.agent_config import loader
from apps.chat.agent_config.defaults import LOOP_PARAM_DEFAULTS, default_tools
from apps.chat.task.agent_prompt import (
    _SYSTEM_PROMPT_TEMPLATE,
    build_agent_system_prompt,
    render_system_prompt_template,
)
from apps.conversation.runtime_context import (
    attach_runtime,
    detach_runtime,
    worker_scope,
)


@pytest.fixture(autouse=True)
def _no_db(monkeypatch: pytest.MonkeyPatch) -> Any:
    monkeypatch.delenv(loader.DISABLE_ENV, raising=False)
    monkeypatch.setattr(loader, "read_published", lambda session: None)
    loader.invalidate_agent_config()
    yield
    loader.invalidate_agent_config()


def _config(prompt: str = "OVERRIDE {execution_limit}", limit: int = 3) -> Any:
    return loader.AgentRuntimeConfig(
        prompt_template=prompt,
        prompt_version="v9",
        tools={name: dict(cfg) for name, cfg in default_tools().items()},
        loop_params={**LOOP_PARAM_DEFAULTS, "execution_round_limit": limit},
    )


def test_no_override_is_byte_identical_to_the_code_template() -> None:
    """The regression gate: without a published row nothing may change."""
    assert render_system_prompt_template() == _SYSTEM_PROMPT_TEMPLATE.format(
        execution_limit=5
    )


def test_override_renders_with_the_configured_limit() -> None:
    assert render_system_prompt_template(config=_config(limit=7)) == "OVERRIDE 7"


def test_unrenderable_override_is_not_substituted() -> None:
    """A body that failed validation must not render as the code default."""
    broken = _config(prompt="bad {undefined_placeholder}")
    with pytest.raises(KeyError):
        render_system_prompt_template(config=broken)


def test_build_agent_system_prompt_prefixes_the_override() -> None:
    text = build_agent_system_prompt(config=_config())
    assert text.splitlines()[0] == "OVERRIDE 3"


def test_turn_snapshot_wins_over_the_process_cache() -> None:
    """A publish landing mid-turn must not swap the prompt under the run."""
    frozen = _config(prompt="FROZEN {execution_limit}", limit=2)
    run_id = "run-freeze-test"
    with worker_scope(run_id, "token"):
        attach_runtime(run_id, agent_config=frozen)
        try:
            assert render_system_prompt_template() == "FROZEN 2"
            assert loader.load_agent_config_for_run() is frozen
        finally:
            detach_runtime(run_id)


def test_without_a_run_the_process_config_applies() -> None:
    assert loader.load_agent_config_for_run().prompt_version == "code"


def test_loop_param_default_used_when_key_absent() -> None:
    config = loader.AgentRuntimeConfig(
        prompt_template="{execution_limit}",
        prompt_version="v1",
        tools={},
        loop_params={},
    )
    assert config.param("execution_round_limit", 11) == 11


def test_tool_helpers_degrade_gracefully_for_unlisted_tools() -> None:
    config = loader.AgentRuntimeConfig(
        prompt_template="{execution_limit}",
        prompt_version="v1",
        tools={},
        loop_params={},
    )
    assert config.tool_enabled("brand_new_tool") is True
    assert config.tool_description("brand_new_tool", "inline") == "inline"
    assert config.tool_round_budget("brand_new_tool") is None
    assert config.tool_parallel_safe("brand_new_tool") is False
