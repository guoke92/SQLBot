"""Single access point for LangChain chat models used by conversation graphs/steps."""

from __future__ import annotations

from typing import Optional

from langchain.chat_models.base import BaseChatModel

from apps.ai_model.model_factory import LLMConfig, LLMFactory, get_default_config


def get_chat_model(config: LLMConfig) -> BaseChatModel:
    """Build the LangChain ``BaseChatModel`` for a given config."""
    return LLMFactory.create_llm(config).llm


async def get_default_chat_config(custom_model_id: Optional[int] = None) -> LLMConfig:
    """Resolve default (or specialized) model config from DB."""
    return await get_default_config(custom_model_id)
