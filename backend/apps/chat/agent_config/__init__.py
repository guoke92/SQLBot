"""Agent runtime configuration: versioned system prompt, tool overrides, loop bounds.

Public surface kept minimal so the agent hot path only pays for the loader:

    from apps.chat.agent_config import load_agent_config

Administration lives in ``api`` / ``service`` and is imported only by the router.
"""

from apps.chat.agent_config.loader import (
    AgentRuntimeConfig,
    install_agent_config,
    invalidate_agent_config,
    load_agent_config,
    load_agent_config_for_run,
)

__all__ = [
    "AgentRuntimeConfig",
    "install_agent_config",
    "invalidate_agent_config",
    "load_agent_config",
    "load_agent_config_for_run",
]
