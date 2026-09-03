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
    # <protocol> meta JSON 段已并入 protocol_rules 文本，不再单独渲染
    assert "<protocol>" not in rendered


def test_empty_prose_sections_are_omitted() -> None:
    rendered = render_planner_input(
        schema="orders(id)",
        sample_data="",
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


def test_query_agent_clarifies_across_recalled_tables() -> None:
    source = query_agent._QUERY_AGENT_SYSTEM
    assert "召回了多张相关表" in source
    assert "禁止只根据一张表澄清" in source
    assert "召回了多张相关表" in query_agent._REVIEWER_SYSTEM


def test_query_agent_reuses_confirmed_calibers_on_continue() -> None:
    source = query_agent._QUERY_AGENT_SYSTEM
    assert "被引用轮次已确认的口径必须沿用" in source
    assert "禁止再次澄清同一主体、金额、日期、层级槽位" in source
    assert "被引用轮次已确认的口径不得再以 clarify 复问" in query_agent._REVIEWER_SYSTEM
    agent_source = inspect.getsource(query_agent.run_query_agent)
    assert "prior_user_evidence" in agent_source


def test_accept_does_not_advance_batch_index() -> None:
    source = (
        _ROOT / "backend" / "apps" / "chat" / "graphs" / "nodes" / "nlq"
        / "execution.py"
    ).read_text()
    assert source.count('"step_index": step_index + 1') == 1
    repair_idx = source.index('"decision": "repair"')
    plus_idx = source.index('"step_index": step_index + 1')
    assert plus_idx > repair_idx
    assert plus_idx < source.index('"decision": "accept"', repair_idx)


def test_execution_schema_refresh_is_not_user_visible() -> None:
    source = (
        _ROOT / "backend" / "apps" / "chat" / "graphs" / "nodes" / "nlq"
        / "execution.py"
    ).read_text()
    schema = (_ROOT / "backend" / "apps" / "chat" / "steps" / "schema.py").read_text()
    assert 'brief="refresh schema"' in source
    refresh = source.split('brief="refresh schema"', 1)[1][:200]
    assert "audit=False" in refresh
    assert "if not audit:" in schema
    assert "user-visible" in schema
    node = (
        _ROOT / "backend" / "apps" / "chat" / "graphs" / "nodes" / "nlq"
        / "execution.py"
    ).read_text()
    assert "execution_schema_resources(" in node
    assert (
        "orjson.dumps(payload).decode()"
        not in node.split("def execute_queries_node", 1)[1].split(
            "def generate_charts_node", 1
        )[0]
    )


def test_planning_does_not_skip_review_on_wall_clock_budget() -> None:
    source = (
        _ROOT / "backend" / "apps" / "chat" / "graphs" / "nodes" / "nlq"
        / "planning.py"
    ).read_text()
    assert "REVIEW_BUDGET_EXHAUSTED" not in source
    assert "planning budget leaves no time" not in source
    assert "查询规划已达到时间上限" not in source
    assert "_planning_call_timeout_sec" in source


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


def test_maps_are_xml_sections_with_readable_newlines() -> None:
    """地图是多行散文清单 — 必须走 XML section, 不得 JSON 转义换行."""
    schema_map = (
        "【Schema map】(2 tables)\nd_organization | 机构表 | ~559行\nd_task | 任务\n"
    )
    knowledge_map = "【Knowledge map】\n交付时效口径 | 研发效能 | 及时率定义\n"
    rendered = render_planner_input(
        schema="# Table: d_task\n[(id:bigint)]",
        schema_map=schema_map,
        knowledge_map=knowledge_map,
        structured={"context": {"resources": ["d_task"]}},
    )

    assert (
        "<schema_map>\n【Schema map】" in rendered
        and "d_organization | 机构表" in rendered
    )
    assert (
        "<knowledge_map>\n【Knowledge map】" in rendered and "交付时效口径" in rendered
    )
    map_body = rendered.split("<schema_map>\n")[1].split("\n</schema_map>")[0]
    assert map_body.count("\n") >= 2  # 换行原样保留
    assert "\\n" not in map_body  # 未被 JSON 转义
    # 地图紧跟 schema（它是 schema 的目录）
    assert rendered.index("</schema>") < rendered.index("<schema_map>")


def test_maps_empty_strings_omit_sections() -> None:
    rendered = render_planner_input(schema="s", schema_map="", knowledge_map="")
    assert "schema_map" not in rendered
    assert "knowledge_map" not in rendered


def test_truncation_notice_renders_only_when_dropped() -> None:
    rendered = render_planner_input(
        schema="s",
        truncation_notice="",
        structured={},
    )
    assert "truncation_notice" not in rendered

    notice = "以下上下文经过预算截断…\n- schema_text（约 500 tokens）"
    rendered = render_planner_input(schema="s", truncation_notice=notice)
    assert rendered.startswith("<truncation_notice>")
    assert "以下上下文经过预算截断" in rendered


def test_render_no_dead_parameters() -> None:
    """terminology/query_examples 死通道已删除 — 渲染签名不再接受。"""
    import inspect

    from apps.chat.planning_prompt import render_planner_input as rpi

    params = inspect.signature(rpi).parameters
    assert "terminology" not in params
    assert "query_examples" not in params
    assert "truncation_notice" in params
