"""Re-export the product-agent system prompt."""

from apps.chat.agent.prompt import (
    _SHARED_PROMPT_TEMPLATE,
    _SLOT_SECTIONS,
    _SYSTEM_PROMPT_TEMPLATE,
    build_agent_system_prompt,
    render_system_prompt_template,
)

__all__ = [
    "_SHARED_PROMPT_TEMPLATE",
    "_SLOT_SECTIONS",
    "_SYSTEM_PROMPT_TEMPLATE",
    "build_agent_system_prompt",
    "render_system_prompt_template",
]
