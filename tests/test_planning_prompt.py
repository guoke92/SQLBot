from __future__ import annotations

import inspect
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.planning_prompt import (  # noqa: E402
    ProtocolPromptBits,
    render_planner_input,
)
from apps.chat.steps import query_agent  # noqa: E402


def test_schema_quotes_are_not_json_escaped() -> None:
    schema = '# Table: t\n("company_name": varchar)'
    rendered = render_planner_input(
        schema=schema,
        protocol=ProtocolPromptBits(
            type_key="starrocks",
            identifier_quote="`",
            rules="必须外层加反引号（`）。",
        ),
        structured={"evidence": [{"kind": "user_question", "text": "q"}]},
    )
    assert '"company_name"' in rendered
    assert '\\"company_name\\"' not in rendered
    assert "\\n" not in rendered.split("<evidence>", 1)[0]
    assert "外层加反引号（`）" in rendered
    assert "<schema>" in rendered
    assert "<protocol_rules>" in rendered
    assert '"protocol_type": "starrocks"' in rendered
    assert '"identifier_quote": "`"' in rendered


def test_empty_prose_sections_are_omitted() -> None:
    rendered = render_planner_input(
        schema="orders(id)",
        sample_data="",
        terminology="   ",
        structured={"entity_bindings": {}},
    )
    assert "<schema>" in rendered
    assert "<sample_data>" not in rendered
    assert "<terminology>" not in rendered
    assert "<entity_bindings>" not in rendered


def test_semantic_and_physical_paths_share_renderer() -> None:
    source = inspect.getsource(query_agent)
    assert "render_planner_input" in source
    assert "orjson.dumps(context)" not in source
    assert "protocol_generation_rules" not in source
    assert "json_schema()" not in source
    assert source.count("render_planner_input(") >= 2


def test_protocol_prompt_bits_stay_on_dialect_rules() -> None:
    from types import SimpleNamespace

    from apps.chat.planning_prompt import protocol_prompt_bits

    bits = protocol_prompt_bits(
        SimpleNamespace(
            protocol=SimpleNamespace(type_key="mysql"),
            enable_sql_row_limit=True,
        )
    )
    assert bits.type_key == "mysql"
    assert "chart-type" not in bits.rules
    assert "基本示例" not in bits.rules
    assert "`" in bits.rules or "反引号" in bits.rules


def test_consume_llm_prefers_stream_and_assembles_reasoning() -> None:
    from types import SimpleNamespace

    from apps.chat.steps.stream import consume_llm

    class _Chunk:
        def __init__(self, content: str = "", reasoning: str = "") -> None:
            self.content = content
            self.additional_kwargs = (
                {"reasoning_content": reasoning} if reasoning else {}
            )
            self.usage_metadata = None

    class _Model:
        def stream(self, _messages: object):
            yield _Chunk(reasoning="think ")
            yield _Chunk(content='{"decision":"ready"}')

    result = consume_llm(_Model(), [])
    assert result.reasoning == "think "
    assert result.content == '{"decision":"ready"}'

    class _InvokeOnly:
        def invoke(self, _messages: object) -> SimpleNamespace:
            return SimpleNamespace(
                content="ok",
                additional_kwargs={"reasoning_content": "why"},
                usage_metadata={},
                response_metadata={},
            )

    invoked = consume_llm(_InvokeOnly(), [])
    assert invoked.content == "ok"
    assert invoked.reasoning == "why"
