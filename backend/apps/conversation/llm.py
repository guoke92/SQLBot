"""Single access point for LangChain chat models used by conversation graphs/steps."""

from __future__ import annotations

from typing import Any

from langchain.chat_models.base import BaseChatModel

from apps.ai_model.model_factory import (
    LLMConfig,
    LLMFactory,
    get_default_config,
    with_reasoning_effort,
)
from apps.ai_model.runtime import normalize_reasoning_effort, resolve_llm_capabilities
from apps.system.crud.aimodel_manage import get_ai_model_list_by_workspace


def get_chat_model(config: LLMConfig) -> BaseChatModel:
    """Build the LangChain ``BaseChatModel`` for a given config."""
    return LLMFactory.create_llm(config).llm


async def get_default_chat_config(custom_model_id: int | None = None) -> LLMConfig:
    """Resolve default (or specialized) model config from DB."""
    return await get_default_config(custom_model_id)


def specialized_model_id(
    session: Any,
    current_user: Any | None,
    current_assistant: Any | None,
) -> int | None:
    """Workspace-allowed custom model on an embedded assistant, else None."""
    if current_assistant is None or not getattr(
        current_assistant, "enable_custom_model", False
    ):
        return None
    custom_model = getattr(current_assistant, "custom_model", None)
    if not custom_model or current_user is None:
        return None
    ws_id = getattr(current_user, "oid", None)
    if not ws_id:
        return None
    models = get_ai_model_list_by_workspace(session, ws_id)
    if any(str(model.id) == str(custom_model) for model in models):
        try:
            return int(str(custom_model))
        except (TypeError, ValueError):
            return None
    return None


async def resolve_chat_llm_config(
    session: Any,
    current_user: Any | None = None,
    current_assistant: Any | None = None,
    reasoning_effort: Any | None = None,
) -> LLMConfig:
    """Resolve the model this turn will call, with an optional effort overlay."""
    config = await get_default_chat_config(
        specialized_model_id(session, current_user, current_assistant)
    )
    return with_reasoning_effort(config, reasoning_effort)


def llm_capabilities_view(config: LLMConfig) -> dict[str, Any]:
    """Public chat-composer view of the active model's reasoning defaults."""
    capabilities, _rest = resolve_llm_capabilities(config.additional_params)
    default_effort = None
    if capabilities.reasoning:
        default_effort = normalize_reasoning_effort(capabilities.reasoning.get("effort"))
    return {
        "model_id": config.model_id,
        "model_name": config.model_name,
        "wire": capabilities.wire,
        "default_effort": default_effort,
    }
