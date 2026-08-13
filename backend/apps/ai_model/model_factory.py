import json
from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Any

from langchain.chat_models.base import BaseChatModel
from langchain_community.llms import VLLMOpenAI
from langchain_openai import AzureChatOpenAI
from pydantic import BaseModel
from sqlmodel import Session, select

from apps.ai_model.openai.llm import BaseChatOpenAI
from apps.system.models.system_model import AiModelDetail
from common.core.config import settings
from common.core.db import engine
from common.utils.crypto import sqlbot_decrypt
from common.utils.utils import prepare_model_arg

# from langchain_community.llms import Tongyi, VLLM

class LLMConfig(BaseModel):
    """Base configuration class for large language models"""
    model_id: int | None = None
    model_type: str  # Model type: openai/tongyi/vllm etc.
    model_name: str  # Specific model name
    api_key: str | None = None
    api_base_url: str | None = None
    additional_params: dict[str, Any] = {}

    class Config:
        frozen = True

    def __hash__(self):
        if hasattr(self, 'additional_params') and isinstance(self.additional_params, dict):
            hashable_params = frozenset((k, tuple(v) if isinstance(v, list | dict) else v)
                                        for k, v in self.additional_params.items())
        else:
            hashable_params = None

        return hash((
            self.model_id,
            self.model_type,
            self.model_name,
            self.api_key,
            self.api_base_url,
            hashable_params
        ))


class BaseLLM(ABC):
    """Abstract base class for large language models"""

    def __init__(self, config: LLMConfig):
        self.config = config
        self._llm = self._init_llm()

    @abstractmethod
    def _init_llm(self) -> BaseChatModel:
        """Initialize specific large language model instance"""
        pass

    @property
    def llm(self) -> BaseChatModel:
        """Return the langchain LLM instance"""
        return self._llm

    def _request_params(self) -> dict[str, Any]:
        """Return caller settings with bounded process defaults.

        Copy the mapping because ``LLMConfig`` is cached and frozen; mutating
        its nested dict made one model construction affect later requests.
        """
        params = dict(self.config.additional_params or {})
        params.setdefault("request_timeout", settings.LLM_REQUEST_TIMEOUT_SEC)
        params.setdefault("max_retries", settings.LLM_MAX_RETRIES)
        return params


class OpenAIvLLM(BaseLLM):
    def _init_llm(self) -> VLLMOpenAI:
        params = self._request_params()
        return VLLMOpenAI(
            openai_api_key=self.config.api_key or 'Empty',
            openai_api_base=self.config.api_base_url,
            model_name=self.config.model_name,
            streaming=True,
            **params,
        )


class OpenAIAzureLLM(BaseLLM):
    def _init_llm(self) -> AzureChatOpenAI:
        params = self._request_params()
        api_version = params.pop("api_version", None)
        deployment_name = params.pop("deployment_name", None)
        return AzureChatOpenAI(
            azure_endpoint=self.config.api_base_url,
            api_key=self.config.api_key or 'Empty',
            model_name=self.config.model_name,
            api_version=api_version,
            deployment_name=deployment_name,
            streaming=True,
            **params,
        )


class OpenAILLM(BaseLLM):
    def _init_llm(self) -> BaseChatModel:
        params = self._request_params()
        return BaseChatOpenAI(
            model=self.config.model_name,
            api_key=self.config.api_key or 'Empty',
            base_url=self.config.api_base_url,
            stream_usage=True,
            **params,
        )

    def generate(self, prompt: str) -> str:
        return self.llm.invoke(prompt)


class LLMFactory:
    """Large Language Model Factory Class"""

    _llm_types: dict[str, type[BaseLLM]] = {
        "openai": OpenAILLM,
        "tongyi": OpenAILLM,
        "vllm": OpenAIvLLM,
        "azure": OpenAIAzureLLM,
    }

    @classmethod
    @lru_cache(maxsize=32)
    def create_llm(cls, config: LLMConfig) -> BaseLLM:
        llm_class = cls._llm_types.get(config.model_type)
        if not llm_class:
            raise ValueError(f"Unsupported LLM type: {config.model_type}")
        return llm_class(config)

    @classmethod
    def register_llm(cls, model_type: str, llm_class: type[BaseLLM]):
        """Register new model type"""
        cls._llm_types[model_type] = llm_class


#  todo
""" def get_llm_config(aimodel: AiModelDetail) -> LLMConfig:
    config = LLMConfig(
        model_type="openai",
        model_name=aimodel.name,
        api_key=aimodel.api_key,
        api_base_url=aimodel.endpoint,
        additional_params={"temperature": aimodel.temperature}
    )
    return config """


async def get_default_config(custom_model_id: int | None = None) -> LLMConfig:
    with Session(engine) as session:
        db_model: AiModelDetail | None = None
        if custom_model_id:
            db_model = session.get(AiModelDetail, custom_model_id)
        if not db_model:
            db_model = session.exec(
                select(AiModelDetail).where(AiModelDetail.default_model)
            ).first()
        if not db_model:
            raise Exception("The system default model has not been set")

        additional_params = {}
        if db_model.config:
            try:
                config_raw = json.loads(db_model.config)
                additional_params = {item["key"]: prepare_model_arg(item.get('val')) for item in config_raw if
                                     "key" in item and "val" in item}
            except Exception:
                pass
        if not db_model.api_domain.startswith("http"):
            db_model.api_domain = await sqlbot_decrypt(db_model.api_domain)
            if db_model.api_key:
                db_model.api_key = await sqlbot_decrypt(db_model.api_key)

        # 构造 LLMConfig
        return LLMConfig(
            model_id=db_model.id,
            model_type="openai" if db_model.protocol == 1 else "vllm",
            model_name=db_model.base_model,
            api_key=db_model.api_key,
            api_base_url=db_model.api_domain,
            additional_params=additional_params,
        )
