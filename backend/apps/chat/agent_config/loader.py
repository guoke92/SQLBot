"""Effective agent configuration: process-local cache, DB only on a miss.

The conversation path reads the cache and does not poll the database. A miss
(process start, or an explicit invalidation) loads the published row once and
fills the cache. Publish and rollback install the new snapshot directly, so a
read that was already in flight cannot write an older row back over it.
"""

from __future__ import annotations

import os
import threading
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from sqlmodel import Session, select

from apps.chat.agent_config.defaults import (
    DEFAULT_PARALLEL_SAFE,
    LOOP_PARAM_DEFAULTS,
    LOOP_PARAM_SPECS,
    REQUIRED_TOOL_NAMES,
    default_tools,
)
from apps.chat.agent_config.models import (
    SCOPE_GLOBAL,
    AgentConfigStatus,
    AgentConfigVersion,
)
from common.core.db import engine
from common.utils.utils import SQLBotLogUtil

#: Set to ``1`` to hard-disable DB lookups (used by DB-less test processes).
DISABLE_ENV = "AGENT_CONFIG_DISABLE_DB"


@dataclass(frozen=True)
class AgentRuntimeConfig:
    prompt_template: str
    #: ``"code"`` when running on code defaults, otherwise ``"v<version_no>"``
    prompt_version: str
    tools: Mapping[str, Mapping[str, Any]]
    loop_params: Mapping[str, int]

    def param(self, key: str, default: int) -> int:
        value = self.loop_params.get(key)
        return (
            value if isinstance(value, int) and not isinstance(value, bool) else default
        )

    def tool_enabled(self, name: str) -> bool:
        tool = self.tools.get(name)
        if tool is None:
            return True
        return bool(tool.get("enabled", True))

    def tool_parallel_safe(self, name: str) -> bool:
        """Only enabled tools are dispatchable, so a disabled tool is never safe."""
        if not self.tool_enabled(name):
            return False
        tool = self.tools.get(name)
        override = tool.get("parallel_safe") if tool else None
        if isinstance(override, bool):
            return override
        return name in DEFAULT_PARALLEL_SAFE

    def tool_description(self, name: str, inline: str) -> str:
        tool = self.tools.get(name)
        override = tool.get("description") if tool else None
        if isinstance(override, str) and override.strip():
            return override
        return inline

    def tool_round_budget(self, name: str) -> int | None:
        tool = self.tools.get(name)
        value = tool.get("round_budget") if tool else None
        if isinstance(value, int) and not isinstance(value, bool):
            return value
        return None


_cache_lock = threading.Lock()
_cache: AgentRuntimeConfig | None = None
#: Bumped on install and invalidation so an in-flight DB read cannot refill stale data.
_cache_epoch = 0
_specs_by_key = {spec.key: spec for spec in LOOP_PARAM_SPECS}


def _db_disabled() -> bool:
    return str(os.environ.get(DISABLE_ENV) or "").strip().lower() in {
        "1",
        "true",
        "yes",
    }


def _code_default() -> AgentRuntimeConfig:
    from apps.chat.task.agent_prompt import _SYSTEM_PROMPT_TEMPLATE

    return AgentRuntimeConfig(
        prompt_template=_SYSTEM_PROMPT_TEMPLATE,
        prompt_version="code",
        tools={name: dict(cfg) for name, cfg in default_tools().items()},
        loop_params=dict(LOOP_PARAM_DEFAULTS),
    )


def merge_tools(raw: Mapping[str, Any] | None) -> dict[str, dict[str, Any]]:
    """Overlay a stored tool map on the code defaults, key by key."""
    merged = default_tools()
    for name, payload in (raw or {}).items():
        if name not in merged or not isinstance(payload, Mapping):
            continue
        entry = merged[name]
        enabled = payload.get("enabled")
        if isinstance(enabled, bool):
            entry["enabled"] = enabled
        description = payload.get("description")
        if isinstance(description, str):
            entry["description"] = description or None
        parallel_safe = payload.get("parallel_safe")
        if isinstance(parallel_safe, bool):
            entry["parallel_safe"] = parallel_safe
        round_budget = payload.get("round_budget")
        if isinstance(round_budget, int) and not isinstance(round_budget, bool):
            entry["round_budget"] = round_budget
        if not entry["enabled"] and name in REQUIRED_TOOL_NAMES:
            SQLBotLogUtil.warning(
                "agent config: refusing to disable required tool %s", name
            )
            entry["enabled"] = True
    return merged


def merge_loop_params(raw: Mapping[str, Any] | None) -> dict[str, int]:
    """Overlay stored loop params on the code defaults, clamped to spec bounds."""
    merged = dict(LOOP_PARAM_DEFAULTS)
    for key, value in (raw or {}).items():
        spec = _specs_by_key.get(key)
        if spec is None or isinstance(value, bool) or not isinstance(value, int):
            continue
        merged[key] = max(spec.minimum, min(spec.maximum, value))
    return merged


def config_from_row(row: AgentConfigVersion) -> AgentRuntimeConfig:
    """Runtime snapshot for a published row. Does not touch the cache."""
    return _from_row(row)


def _from_row(row: AgentConfigVersion) -> AgentRuntimeConfig:
    # A published row always carries a body (enforced on save); empty means the
    # row is corrupt, so fall back to the code prompt rather than sending "".
    if not str(row.prompt_body or "").strip():
        return _code_default()
    return AgentRuntimeConfig(
        prompt_template=str(row.prompt_body),
        prompt_version=f"v{row.version_no}",
        tools=merge_tools(row.tools if isinstance(row.tools, Mapping) else None),
        loop_params=merge_loop_params(
            row.loop_params if isinstance(row.loop_params, Mapping) else None
        ),
    )


def read_published(session: Session) -> AgentConfigVersion | None:
    """Latest published revision for the global scope, if any."""
    return session.exec(
        select(AgentConfigVersion)
        .where(AgentConfigVersion.scope_key == SCOPE_GLOBAL)
        .where(AgentConfigVersion.status == AgentConfigStatus.PUBLISHED.value)
        .order_by(AgentConfigVersion.version_no.desc())  # type: ignore[arg-type]
        .limit(1)
    ).first()


def _load_uncached() -> AgentRuntimeConfig:
    if _db_disabled():
        return _code_default()
    try:
        with Session(engine) as session:
            row = read_published(session)
    except Exception as exc:  # noqa: BLE001 — DB must never break the agent path
        SQLBotLogUtil.warning(
            "agent config: DB read failed, using code defaults: %s", exc
        )
        return _code_default()
    if row is None:
        return _code_default()
    try:
        return _from_row(row)
    except Exception as exc:  # noqa: BLE001
        SQLBotLogUtil.warning(
            "agent config: bad published row, using defaults: %s", exc
        )
        return _code_default()


def load_agent_config() -> AgentRuntimeConfig:
    """Cached config. Reads the database only when the cache is empty."""
    global _cache
    while True:
        with _cache_lock:
            if _cache is not None:
                return _cache
            epoch = _cache_epoch
        config = _load_uncached()
        with _cache_lock:
            # Publish/rollback installs under this lock. Prefer that snapshot
            # over a read that started against the previous row.
            if _cache is not None:
                return _cache
            if _cache_epoch == epoch:
                _cache = config
                return config


def install_agent_config(config: AgentRuntimeConfig) -> None:
    """Make ``config`` the process cache immediately. Does not read the database."""
    global _cache, _cache_epoch
    with _cache_lock:
        _cache_epoch += 1
        _cache = config


def load_agent_config_for_run() -> AgentRuntimeConfig:
    """Config frozen for the current worker run, else the process-wide snapshot.

    ``init_agent_turn`` attaches the snapshot once per turn, which keeps
    prompt / tool set / round budget mutually consistent even if a publish lands
    mid-turn. Outside a worker (unit tests, scripted callers) this degrades to
    :func:`load_agent_config`.
    """
    from apps.conversation.runtime_context import (
        current_worker_identity,
        peek_runtime,
    )

    run_id, _token = current_worker_identity()
    if run_id:
        values = peek_runtime(run_id) or {}
        frozen = values.get("agent_config")
        if isinstance(frozen, AgentRuntimeConfig):
            return frozen
    return load_agent_config()


def invalidate_agent_config() -> None:
    """Drop the cached snapshot. The next conversation read loads the database."""
    global _cache, _cache_epoch
    with _cache_lock:
        _cache_epoch += 1
        _cache = None
