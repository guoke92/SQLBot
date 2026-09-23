"""LLM runtime adapter: Completions default, Responses opt-in, stream normalize."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from langchain_core.messages import AIMessage  # noqa: E402

from apps.ai_model.model_factory import LLMConfig, OpenAILLM  # noqa: E402
from apps.ai_model.openai.llm import BaseChatOpenAI  # noqa: E402
from apps.ai_model.runtime import (  # noqa: E402
    apply_openai_ctor_kwargs,
    has_reasoning_payload,
    normalize_message_parts,
    resolve_llm_capabilities,
)
from apps.chat.steps.stream import consume_llm, process_stream  # noqa: E402


class _Chunk:
    def __init__(
        self,
        content: object = "",
        reasoning: str = "",
        extra: dict | None = None,
        response_metadata: dict | None = None,
    ) -> None:
        self.content = content
        if extra is not None:
            self.additional_kwargs = extra
        elif reasoning:
            self.additional_kwargs = {"reasoning_content": reasoning}
        else:
            self.additional_kwargs = {}
        self.usage_metadata = None
        self.tool_calls: list = []
        self.invalid_tool_calls: list = []
        self.response_metadata = response_metadata or {}
        self.id = None

    def __add__(self, other: _Chunk) -> _Chunk:
        left = self.content
        right = other.content
        if isinstance(left, list) or isinstance(right, list):
            left_list = left if isinstance(left, list) else []
            right_list = right if isinstance(right, list) else []
            content: object = left_list + right_list
        else:
            content = f"{left}{right}"
        extra = dict(self.additional_kwargs)
        extra.update(other.additional_kwargs)
        metadata = dict(self.response_metadata)
        metadata.update(other.response_metadata)
        return _Chunk(content=content, extra=extra, response_metadata=metadata)


def test_completions_kwargs_reasoning_content() -> None:
    parts = normalize_message_parts(
        SimpleNamespace(
            content="答",
            additional_kwargs={"reasoning_content": "想"},
        )
    )
    assert parts.content == "答"
    assert parts.reasoning == "想"


def test_completions_kwargs_reasoning_alias() -> None:
    parts = normalize_message_parts(
        SimpleNamespace(content="答", additional_kwargs={"reasoning": "想"})
    )
    assert parts.content == "答"
    assert parts.reasoning == "想"


def test_responses_content_blocks_split_visible_and_thought() -> None:
    parts = normalize_message_parts(
        SimpleNamespace(
            content=[
                {
                    "type": "reasoning",
                    "summary": [{"type": "summary_text", "text": "推演"}],
                },
                {"type": "text", "text": "答"},
            ],
            additional_kwargs={},
        )
    )
    assert parts.content == "答"
    assert parts.reasoning == "推演"


def test_encrypted_reasoning_envelope_is_not_shown() -> None:
    envelope = {
        "id": "65f11ba6-c550-49a9-9284-6cd76b4e69ab",
        "summary": [],
        "type": "reasoning",
        "encrypted_content": "85d2255c-5636-4774-9960-55c38a2ab5ef-0",
        "status": "in_progress",
    }
    parts = normalize_message_parts(
        SimpleNamespace(content="", additional_kwargs={"reasoning": envelope})
    )
    assert parts.content == ""
    assert parts.reasoning == ""
    assert has_reasoning_payload(
        SimpleNamespace(content="", additional_kwargs={"reasoning": envelope})
    )


def test_reasoning_plaintext_not_blocked_by_encrypted_envelope() -> None:
    parts = normalize_message_parts(
        SimpleNamespace(
            content="",
            additional_kwargs={
                "reasoning": {
                    "type": "reasoning",
                    "encrypted_content": "enc-0",
                    "summary": [],
                    "content": [{"type": "reasoning_text", "text": "真实思考"}],
                }
            },
        )
    )
    assert parts.reasoning == "真实思考"


def test_reasoning_text_delta_is_converted_to_thought() -> None:
    from langchain_openai.chat_models import base as openai_base

    chunk = SimpleNamespace(
        type="response.reasoning_text.delta",
        delta="先看订单表",
        output_index=0,
        content_index=0,
        item_id="rs_1",
    )
    _index, _output_index, _sub_index, generation = (
        openai_base._convert_responses_chunk_to_generation_chunk(chunk, -1, -1, -1)
    )
    assert generation is not None
    parts = normalize_message_parts(generation.message)
    assert parts.reasoning == "先看订单表"
    assert parts.content == ""


def test_reasoning_text_deltas_stream_as_thought_text() -> None:
    from langchain_openai.chat_models import base as openai_base

    def _delta(text: str) -> object:
        _index, _output_index, _sub_index, generation = (
            openai_base._convert_responses_chunk_to_generation_chunk(
                SimpleNamespace(
                    type="response.reasoning_text.delta",
                    delta=text,
                    output_index=0,
                    content_index=0,
                    item_id="rs_1",
                ),
                -1,
                -1,
                -1,
            )
        )
        assert generation is not None
        return generation.message

    chunks = list(process_stream(iter([_delta("先看"), _delta("订单表")])))
    assert "".join(str(item.get("reasoning_content") or "") for item in chunks) == (
        "先看订单表"
    )
    assert all(item["has_reasoning"] for item in chunks)


def test_responses_summary_deltas_stream_as_thought_text() -> None:
    chunks = list(
        process_stream(
            iter(
                [
                    _Chunk(
                        extra={
                            "reasoning": {
                                "id": "r1",
                                "summary": [],
                                "type": "reasoning",
                                "encrypted_content": "enc-0",
                                "status": "in_progress",
                            }
                        }
                    ),
                    _Chunk(
                        extra={
                            "reasoning": {
                                "summary": [
                                    {"index": 0, "type": "summary_text", "text": "先看"}
                                ]
                            }
                        }
                    ),
                    _Chunk(
                        extra={
                            "reasoning": {
                                "summary": [
                                    {
                                        "index": 0,
                                        "type": "summary_text",
                                        "text": "表结构",
                                    }
                                ]
                            }
                        }
                    ),
                    _Chunk(content="下一步"),
                ]
            )
        )
    )
    assert "".join(str(item.get("reasoning_content") or "") for item in chunks) == (
        "先看表结构"
    )
    assert chunks[0]["has_reasoning"] is True
    assert "".join(str(item.get("content") or "") for item in chunks) == "下一步"


def test_process_stream_xml_think_tags() -> None:
    chunks = list(
        process_stream(
            iter([_Chunk(content="<think>内部</think>可见")]),
            enable_tag_parsing=True,
            start_tag="<think>",
            end_tag="</think>",
        )
    )
    assert (
        "".join(str(item.get("reasoning_content") or "") for item in chunks) == "内部"
    )
    assert "".join(str(item.get("content") or "") for item in chunks) == "可见"


def test_process_stream_list_content_does_not_raise() -> None:
    chunks = list(
        process_stream(
            iter(
                [
                    _Chunk(
                        content=[
                            {"type": "reasoning", "content": "想"},
                            {"type": "text", "text": "答"},
                        ]
                    )
                ]
            )
        )
    )
    assert [item["content"] for item in chunks] == ["答"]
    assert [item["reasoning_content"] for item in chunks] == ["想"]


def test_factory_defaults_to_completions_pin() -> None:
    capabilities, rest = resolve_llm_capabilities(
        {"temperature": 0.2, "extra_body": {"enable_thinking": False}}
    )
    assert capabilities.wire == "completions"
    assert capabilities.reasoning is None
    assert rest["extra_body"] == {"enable_thinking": False}
    ctor = apply_openai_ctor_kwargs(
        {"temperature": 0.2, "extra_body": {"enable_thinking": True}}
    )
    assert ctor["use_responses_api"] is False
    assert "reasoning" not in ctor
    assert ctor["extra_body"] == {"enable_thinking": True}


def test_factory_reasoning_effort_opts_into_responses() -> None:
    ctor = apply_openai_ctor_kwargs({"reasoning_effort": "low"})
    assert ctor["use_responses_api"] is True
    assert ctor["reasoning"] == {"effort": "low"}
    assert "summary" not in ctor["reasoning"]


def test_factory_reasoning_effort_max_and_aliases() -> None:
    from apps.ai_model.runtime import normalize_reasoning_effort

    assert normalize_reasoning_effort("max") == "max"
    assert normalize_reasoning_effort("medium") == "high"
    assert normalize_reasoning_effort("minimal") == "low"
    assert normalize_reasoning_effort("ultra") == "max"
    ctor = apply_openai_ctor_kwargs({"reasoning_effort": "max"})
    assert ctor["use_responses_api"] is True
    assert ctor["reasoning"] == {"effort": "max"}
    aliased = apply_openai_ctor_kwargs({"reasoning_effort": "medium"})
    assert aliased["reasoning"] == {"effort": "high"}


def test_factory_reasoning_effort_none_on_responses() -> None:
    ctor = apply_openai_ctor_kwargs(
        {"use_responses_api": True, "reasoning_effort": "none"}
    )
    assert ctor["use_responses_api"] is True
    assert ctor["reasoning"] == {"effort": "none"}
    assert "summary" not in ctor["reasoning"]


def test_factory_reasoning_effort_none_alone_stays_completions() -> None:
    ctor = apply_openai_ctor_kwargs({"reasoning_effort": "none"})
    assert ctor["use_responses_api"] is False
    assert "reasoning" not in ctor
    assert ctor["extra_body"]["thinking"] == {"type": "disabled"}


def test_factory_explicit_use_responses_api() -> None:
    ctor = apply_openai_ctor_kwargs({"use_responses_api": "true"})
    assert ctor["use_responses_api"] is True
    assert "summary" not in (ctor.get("reasoning") or {})


def test_factory_drops_responses_summary_for_deepseek() -> None:
    ctor = apply_openai_ctor_kwargs(
        {
            "use_responses_api": True,
            "reasoning": {"effort": "high", "summary": "concise"},
        }
    )
    assert ctor["reasoning"] == {"effort": "high"}
    assert "summary" not in ctor["reasoning"]


def test_overlay_reasoning_effort_overrides_model_default() -> None:
    from apps.ai_model.model_factory import LLMConfig, with_reasoning_effort
    from apps.conversation.llm import llm_capabilities_view

    base = LLMConfig(
        model_type="openai",
        model_name="deepseek-flash",
        additional_params={"use_responses_api": True, "reasoning_effort": "low"},
    )
    assert llm_capabilities_view(base)["default_effort"] == "low"
    overlay = with_reasoning_effort(base, "high")
    ctor = apply_openai_ctor_kwargs(overlay.additional_params)
    assert ctor["reasoning"] == {"effort": "high"}
    assert with_reasoning_effort(base, "bogus") is base
    assert with_reasoning_effort(base, None) is base
    none_overlay = with_reasoning_effort(base, "none")
    assert apply_openai_ctor_kwargs(none_overlay.additional_params)["reasoning"] == {
        "effort": "none"
    }


def test_completions_echoes_reasoning_content_for_tool_rounds() -> None:
    from langchain_core.messages import AIMessage
    from langchain_openai.chat_models import base as openai_base

    import apps.ai_model.openai.llm  # noqa: F401  — installs compat patches
    from apps.ai_model.openai.responses_compat import install_openai_compat

    install_openai_compat()
    payload = openai_base._convert_message_to_dict(
        AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "lookup",
                    "args": {"q": "1"},
                    "id": "call_1",
                    "type": "tool_call",
                }
            ],
            additional_kwargs={"reasoning_content": "先查表再回答"},
        )
    )
    assert payload["reasoning_content"] == "先查表再回答"
    assert payload["tool_calls"]


def test_responses_echo_rewrites_openai_reasoning_to_deepseek_shape() -> None:
    from langchain_core.messages import AIMessage, HumanMessage
    from langchain_openai.chat_models import base as openai_base

    import apps.ai_model.openai.llm  # noqa: F401
    from apps.ai_model.openai.responses_compat import (
        install_openai_compat,
        normalize_responses_reasoning_item,
    )

    install_openai_compat()
    openai_shaped = {
        "id": "rs_1",
        "type": "reasoning",
        "status": "in_progress",
        "summary": [
            {"type": "summary_text", "text": "先看订单表再聚合金额"},
        ],
        "encrypted_content": "enc-0",
    }
    assert normalize_responses_reasoning_item(openai_shaped) == {
        "type": "reasoning",
        "id": "rs_1",
        "status": "completed",
        "content": [{"type": "reasoning_text", "text": "先看订单表再聚合金额"}],
    }
    assert (
        normalize_responses_reasoning_item(
            {
                "type": "reasoning",
                "status": "in_progress",
                "summary": [],
                "encrypted_content": "enc-0",
            }
        )
        is None
    )

    items = openai_base._construct_responses_api_input(
        [
            HumanMessage(content="查一下"),
            AIMessage(
                content=[
                    openai_shaped,
                    {
                        "type": "output_text",
                        "text": "好的",
                        "id": "msg_1",
                        "annotations": [],
                    },
                    {
                        "type": "function_call",
                        "name": "lookup",
                        "arguments": "{}",
                        "call_id": "call_1",
                        "id": "fc_1",
                    },
                ]
            ),
        ]
    )
    reasoning_items = [item for item in items if item.get("type") == "reasoning"]
    assert len(reasoning_items) == 1
    assert reasoning_items[0] == {
        "type": "reasoning",
        "id": "rs_1",
        "status": "completed",
        "content": [{"type": "reasoning_text", "text": "先看订单表再聚合金额"}],
    }
    assert "encrypted_content" not in reasoning_items[0]
    assert "summary" not in reasoning_items[0]


def test_responses_stream_accepts_dict_output_item() -> None:
    from langchain_openai.chat_models import base as openai_base

    import apps.ai_model.openai.llm  # noqa: F401
    from apps.ai_model.openai.responses_compat import install_openai_compat

    install_openai_compat()
    message_event = SimpleNamespace(
        type="response.output_item.added",
        output_index=0,
        item={"type": "message", "id": "msg_1", "role": "assistant"},
    )
    _, _, _, message_chunk = openai_base._convert_responses_chunk_to_generation_chunk(
        message_event, -1, -1, -1
    )
    assert message_chunk is not None
    assert message_chunk.message.id == "msg_1"

    reasoning_event = SimpleNamespace(
        type="response.output_item.added",
        output_index=1,
        item={
            "type": "reasoning",
            "id": "rs_1",
            "summary": [{"type": "summary_text", "text": ""}],
            "encrypted_content": None,
        },
    )
    _, _, _, reasoning_chunk = openai_base._convert_responses_chunk_to_generation_chunk(
        reasoning_event, -1, -1, -1
    )
    assert reasoning_chunk is not None
    reasoning = reasoning_chunk.message.additional_kwargs["reasoning"]
    assert reasoning["type"] == "reasoning"
    assert reasoning["id"] == "rs_1"
    assert "encrypted_content" not in reasoning


def test_openai_llm_pins_completions_for_qwen_extra_body() -> None:
    llm = OpenAILLM(
        LLMConfig(
            model_type="openai",
            model_name="qwen-plus",
            api_key="Empty",
            api_base_url="https://example.invalid/v1",
            additional_params={"extra_body": {"enable_thinking": False}},
        )
    ).llm
    assert getattr(llm, "use_responses_api", None) is False


def test_openai_llm_opts_into_responses_from_effort() -> None:
    llm = OpenAILLM(
        LLMConfig(
            model_type="openai",
            model_name="gpt-5",
            api_key="Empty",
            api_base_url="https://api.openai.com/v1",
            additional_params={"reasoning_effort": "low"},
        )
    ).llm
    assert getattr(llm, "use_responses_api", None) is True
    assert getattr(llm, "reasoning", None) == {"effort": "low"}


def test_max_tokens_injected_only_on_completions() -> None:
    completions = BaseChatOpenAI(
        model="gpt-4",
        api_key="Empty",
        use_responses_api=False,
        max_tokens=128,
    )
    assert completions._inject_max_tokens({})["max_tokens"] == 128
    responses = BaseChatOpenAI(
        model="gpt-4",
        api_key="Empty",
        use_responses_api=True,
        max_tokens=128,
    )
    assert "max_tokens" not in responses._inject_max_tokens({})


def test_stream_usage_not_passed_on_responses(monkeypatch: Any) -> None:
    completions = BaseChatOpenAI(
        model="gpt-4",
        api_key="Empty",
        use_responses_api=False,
    )
    assert completions._prepare_stream_kwargs({})["stream_usage"] is True
    responses = BaseChatOpenAI(
        model="gpt-4",
        api_key="Empty",
        use_responses_api=True,
        reasoning={"effort": "low"},
    )
    prepared = responses._prepare_stream_kwargs(
        {"stream_usage": True, "stream_options": {"include_usage": True}}
    )
    assert "stream_usage" not in prepared
    assert "stream_options" not in prepared
    from langchain_core.messages import HumanMessage

    monkeypatch.setattr(
        "apps.ai_model.openai.llm.begin_llm_call_log", lambda _payload: None
    )
    payload = responses._get_request_payload(
        [HumanMessage(content="hi")],
        stream_usage=True,
        stream=True,
    )
    assert "stream_usage" not in payload
    assert "stream_options" not in payload


def test_consume_llm_flattens_string_stream() -> None:
    class _Model:
        def stream(self, _messages: object):
            yield _Chunk(reasoning="think ")
            yield _Chunk(content='{"decision":"ready"}')

    result = consume_llm(_Model(), [])
    assert result.reasoning == "think "
    assert result.content == '{"decision":"ready"}'
    assert isinstance(result.message, AIMessage)
    assert result.message.content == '{"decision":"ready"}'


def test_consume_llm_preserves_structured_content() -> None:
    blocks = [
        {"type": "reasoning", "content": "想"},
        {"type": "text", "text": "答"},
    ]

    class _Model:
        def stream(self, _messages: object):
            yield _Chunk(content=blocks, response_metadata={"id": "resp_1"})

    result = consume_llm(_Model(), [])
    assert result.content == "答"
    assert result.reasoning == "想"
    assert result.message.content == blocks
    assert result.message.additional_kwargs.get("reasoning_content") == "想"
