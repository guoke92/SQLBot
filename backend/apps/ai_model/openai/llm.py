from collections.abc import Iterator, Mapping
from typing import Any, cast

from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import (
    AIMessageChunk,
    BaseMessage,
    BaseMessageChunk,
    ChatMessageChunk,
    FunctionMessageChunk,
    HumanMessageChunk,
    SystemMessageChunk,
)
from langchain_core.messages.ai import UsageMetadata
from langchain_core.messages.tool import ToolMessageChunk, tool_call_chunk
from langchain_core.outputs import ChatGenerationChunk
from langchain_core.outputs.chat_generation import ChatGeneration
from langchain_core.runnables import RunnableConfig, ensure_config
from langchain_openai import ChatOpenAI
from langchain_openai.chat_models.base import _create_usage_metadata

from apps.ai_model.call_log import begin_llm_call_log, finish_llm_call_log
from apps.ai_model.openai.responses_compat import install_openai_compat
from apps.ai_model.runtime import normalize_message_parts

install_openai_compat()


def _convert_delta_to_message_chunk(
    _dict: Mapping[str, Any], default_class: type[BaseMessageChunk]
) -> BaseMessageChunk:
    id_ = _dict.get("id")
    role = cast(str, _dict.get("role"))
    content = cast(str, _dict.get("content") or "")
    additional_kwargs: dict = {}
    # 兼容 reasoning_content (DeepSeek等) 和 reasoning (Ollama/LMStudio GPT-OSS) 两种字段
    reasoning_content = _dict.get("reasoning_content")
    if not reasoning_content:
        reasoning_content = _dict.get("reasoning")
    if reasoning_content:
        additional_kwargs["reasoning_content"] = reasoning_content
    if _dict.get("function_call"):
        function_call = dict(_dict["function_call"])
        if "name" in function_call and function_call["name"] is None:
            function_call["name"] = ""
        additional_kwargs["function_call"] = function_call
    tool_call_chunks = []
    if raw_tool_calls := _dict.get("tool_calls"):
        additional_kwargs["tool_calls"] = raw_tool_calls
        try:
            tool_call_chunks = [
                tool_call_chunk(
                    name=rtc["function"].get("name"),
                    args=rtc["function"].get("arguments"),
                    id=rtc.get("id"),
                    index=rtc["index"],
                )
                for rtc in raw_tool_calls
            ]
        except KeyError:
            pass

    if role == "user" or default_class == HumanMessageChunk:
        return HumanMessageChunk(content=content, id=id_)
    elif role == "assistant" or default_class == AIMessageChunk:
        return AIMessageChunk(
            content=content,
            additional_kwargs=additional_kwargs,
            id=id_,
            tool_call_chunks=tool_call_chunks,  # type: ignore[arg-type]
        )
    elif role in ("system", "developer") or default_class == SystemMessageChunk:
        if role == "developer":
            additional_kwargs = {"__openai_role__": "developer"}
        else:
            additional_kwargs = {}
        return SystemMessageChunk(
            content=content, id=id_, additional_kwargs=additional_kwargs
        )
    elif role == "function" or default_class == FunctionMessageChunk:
        return FunctionMessageChunk(content=content, name=_dict["name"], id=id_)
    elif role == "tool" or default_class == ToolMessageChunk:
        return ToolMessageChunk(
            content=content, tool_call_id=_dict["tool_call_id"], id=id_
        )
    elif role or default_class == ChatMessageChunk:
        return ChatMessageChunk(content=content, role=role, id=id_)
    else:
        return default_class(content=content, id=id_)


class BaseChatOpenAI(ChatOpenAI):
    def _completions_wire(self) -> bool:
        return getattr(self, "use_responses_api", None) is not True

    def _should_delegate_chunk(self, chunk: Mapping[str, Any]) -> bool:
        if not self._completions_wire():
            return True
        chunk_type = chunk.get("type")
        if isinstance(chunk_type, str) and chunk_type.startswith("response."):
            return True
        nested = chunk.get("chunk")
        nested_choices = nested.get("choices") if isinstance(nested, Mapping) else None
        choices = chunk.get("choices") or nested_choices
        return not choices and "output" in chunk

    def _inject_max_tokens(self, payload: dict[str, Any]) -> dict[str, Any]:
        max_tokens = self.max_tokens
        if max_tokens and self._completions_wire():
            payload["max_tokens"] = max_tokens
        return payload

    def _strip_completions_only_payload(
        self, payload: dict[str, Any]
    ) -> dict[str, Any]:
        if self._completions_wire():
            return payload
        payload.pop("stream_usage", None)
        payload.pop("stream_options", None)
        return payload

    def _prepare_stream_kwargs(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        prepared = dict(kwargs)
        if self._completions_wire():
            prepared["stream_usage"] = True
        else:
            prepared.pop("stream_usage", None)
            prepared.pop("stream_options", None)
        return prepared

    @property
    def _default_params(self) -> dict[str, Any]:
        return self._inject_max_tokens(super()._default_params)

    def _get_request_payload(
        self,
        input_: LanguageModelInput,
        *,
        stop: list[str] | None = None,
        **kwargs: Any,
    ) -> dict:
        if not self._completions_wire():
            kwargs.pop("stream_usage", None)
            kwargs.pop("stream_options", None)
        payload = super()._get_request_payload(input_, stop=stop, **kwargs)
        payload = self._strip_completions_only_payload(self._inject_max_tokens(payload))
        # Persist the wire body as-sent, before the HTTP round-trip.
        object.__setattr__(self, "_active_llm_call_log_id", begin_llm_call_log(payload))
        return payload

    usage_metadata: dict = {}

    def get_last_generation_info(self) -> dict[str, Any] | None:
        return self.usage_metadata

    def _finish_active_call_log(
        self,
        *,
        response_content: str | None = None,
        reasoning_content: str | None = None,
        error: str | None = None,
    ) -> None:
        log_id = getattr(self, "_active_llm_call_log_id", None)
        if log_id is None:
            return
        object.__setattr__(self, "_active_llm_call_log_id", None)
        finish_llm_call_log(
            log_id,
            response_content=response_content,
            reasoning_content=reasoning_content,
            error=error,
        )

    def _stream(self, *args: Any, **kwargs: Any) -> Iterator[ChatGenerationChunk]:
        kwargs = self._prepare_stream_kwargs(kwargs)
        content_parts: list[str] = []
        reasoning_parts: list[str] = []
        error_text: str | None = None
        try:
            for chunk in super()._stream(*args, **kwargs):
                if chunk.message.usage_metadata is not None:
                    self.usage_metadata = chunk.message.usage_metadata
                parts = normalize_message_parts(chunk.message)
                if parts.content:
                    content_parts.append(parts.content)
                if parts.reasoning:
                    reasoning_parts.append(parts.reasoning)
                yield chunk
        except Exception as exc:
            error_text = f"{type(exc).__name__}: {exc}"
            raise
        finally:
            self._finish_active_call_log(
                response_content="".join(content_parts) or None,
                reasoning_content="".join(reasoning_parts) or None,
                error=error_text,
            )

    def _convert_chunk_to_generation_chunk(
        self,
        chunk: dict,
        default_chunk_class: type,
        base_generation_info: dict | None,
    ) -> ChatGenerationChunk | None:
        if chunk.get("type") == "content.delta":  # from beta.chat.completions.stream
            return None
        if self._should_delegate_chunk(chunk):
            return super()._convert_chunk_to_generation_chunk(
                chunk, default_chunk_class, base_generation_info
            )
        token_usage = chunk.get("usage")
        choices = (
            chunk.get("choices", [])
            # from beta.chat.completions.stream
            or chunk.get("chunk", {}).get("choices", [])
        )

        usage_metadata: UsageMetadata | None = (
            _create_usage_metadata(token_usage)
            if token_usage and token_usage.get("prompt_tokens")
            else None
        )
        if len(choices) == 0:
            # logprobs is implicitly None
            generation_chunk = ChatGenerationChunk(
                message=default_chunk_class(content="", usage_metadata=usage_metadata)
            )
            return generation_chunk

        choice = choices[0]
        if choice["delta"] is None:
            return None

        message_chunk = _convert_delta_to_message_chunk(
            choice["delta"], default_chunk_class
        )
        generation_info = {**base_generation_info} if base_generation_info else {}

        if finish_reason := choice.get("finish_reason"):
            generation_info["finish_reason"] = finish_reason
            if model_name := chunk.get("model"):
                generation_info["model_name"] = model_name
            if system_fingerprint := chunk.get("system_fingerprint"):
                generation_info["system_fingerprint"] = system_fingerprint

        logprobs = choice.get("logprobs")
        if logprobs:
            generation_info["logprobs"] = logprobs

        if usage_metadata and isinstance(message_chunk, AIMessageChunk):
            message_chunk.usage_metadata = usage_metadata

        generation_chunk = ChatGenerationChunk(
            message=message_chunk, generation_info=generation_info or None
        )
        return generation_chunk

    def invoke(
        self,
        input: LanguageModelInput,
        config: RunnableConfig | None = None,
        *,
        stop: list[str] | None = None,
        **kwargs: Any,
    ) -> BaseMessage:
        config = ensure_config(config)
        error_text: str | None = None
        chat_result: BaseMessage | None = None
        try:
            chat_result = cast(
                ChatGeneration,
                self.generate_prompt(
                    [self._convert_input(input)],
                    stop=stop,
                    callbacks=config.get("callbacks"),
                    tags=config.get("tags"),
                    metadata=config.get("metadata"),
                    run_name=config.get("run_name"),
                    run_id=config.pop("run_id", None),
                    **kwargs,
                ).generations[0][0],
            ).message
        except Exception as exc:
            error_text = f"{type(exc).__name__}: {exc}"
            # Streaming path already finished the log in ``_stream``; only
            # non-stream generate leaves the pending id for us to close.
            self._finish_active_call_log(error=error_text)
            raise

        self.usage_metadata = (
            chat_result.response_metadata["token_usage"]
            if "token_usage" in chat_result.response_metadata
            else chat_result.usage_metadata
        )
        # Non-streaming generate does not go through ``_stream``; persist here.
        if getattr(self, "_active_llm_call_log_id", None) is not None:
            parts = normalize_message_parts(chat_result)
            self._finish_active_call_log(
                response_content=parts.content or None,
                reasoning_content=parts.reasoning or None,
            )
        return chat_result
