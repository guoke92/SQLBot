"""Conversation core unit tests (no DB, no LLM network).

Imports conversation submodules directly so test discovery does not depend on
sqlbot_xpack side effects from ``apps.ai_model`` (via conversation.__init__).
"""

from __future__ import annotations

import importlib.util
import json
import sys
import types
from pathlib import Path
from typing import Any

try:
    import pytest
except ModuleNotFoundError:  # minimal local run without pytest installed
    class _Raises:
        def __init__(self, exc_type):
            self.exc_type = exc_type

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            if exc_type is None:
                raise AssertionError(f"Expected {self.exc_type!r} to be raised")
            return issubclass(exc_type, self.exc_type)

    class pytest:  # type: ignore[no-redef]
        @staticmethod
        def raises(exc_type):
            return _Raises(exc_type)


_BACKEND = Path(__file__).resolve().parents[1] / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))


def _ensure_pkg(name: str) -> None:
    if name not in sys.modules:
        m = types.ModuleType(name)
        m.__path__ = []  # type: ignore[attr-defined]
        sys.modules[name] = m


def _load(name: str, rel: str) -> Any:
    path = _BACKEND / rel
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_ensure_pkg("apps")
_ensure_pkg("apps.conversation")

events = _load("apps.conversation.events", "apps/conversation/events.py")
registry = _load("apps.conversation.registry", "apps/conversation/registry.py")
# load sink before runtime (runtime imports sink)
sink = _load("apps.conversation.sink", "apps/conversation/sink.py")
runtime = _load("apps.conversation.runtime", "apps/conversation/runtime.py")

emit = events.emit
clear_registry = registry.clear_registry
get_graph = registry.get_graph
has_graph = registry.has_graph
list_graphs = registry.list_graphs
register_graph = registry.register_graph
unregister_graph = registry.unregister_graph
StreamRunner = runtime.StreamRunner
run_graph = runtime.run_graph
submit_graph = runtime.submit_graph
StreamSink = sink.StreamSink
resolve_sink = sink.resolve_sink


class TestEmit:
    def test_emit_frame_shape(self) -> None:
        frame = emit({"type": "id", "id": 42})
        assert frame.startswith("data:")
        assert frame.endswith("\n\n")
        payload = json.loads(frame[len("data:") :].strip())
        assert payload == {"type": "id", "id": 42}

    def test_emit_preserves_fields(self) -> None:
        frame = emit(
            {
                "type": "analysis-result",
                "content": "hello",
                "reasoning_content": "think",
            }
        )
        payload = json.loads(frame[len("data:") :].strip())
        assert payload["content"] == "hello"
        assert payload["reasoning_content"] == "think"


class TestRegistry:
    def setup_method(self) -> None:
        clear_registry()

    def teardown_method(self) -> None:
        clear_registry()

    def test_register_and_get(self) -> None:
        def builder(ctx):  # noqa: ANN001
            return iter([emit({"type": "finish"})])

        register_graph("echo", builder)
        assert has_graph("echo")
        assert "echo" in list_graphs()
        assert get_graph("echo") is builder

    def test_missing_raises(self) -> None:
        with pytest.raises(KeyError):
            get_graph("missing")


class TestStreamRunner:
    def test_submit_and_await(self) -> None:
        runner = StreamRunner()

        def gen():
            yield emit({"type": "id", "id": 1})
            yield emit({"type": "finish"})

        runner.submit(gen)
        while runner.is_running(timeout=0.05):
            pass
        chunks = list(runner.await_result())
        assert len(chunks) == 2
        assert "id" in chunks[0]


class TestSink:
    def test_resolve_sink(self) -> None:
        assert resolve_sink(in_chat=True, stream=True) == "sse"
        assert resolve_sink(in_chat=False, stream=True) == "markdown"
        assert resolve_sink(in_chat=False, stream=False) == "json"

    def test_error_chunks_sse(self) -> None:
        chunks = list(StreamSink("sse").error_chunks("boom"))
        assert len(chunks) == 1
        body = json.loads(chunks[0][len("data:") :].strip())
        assert body == {"content": "boom", "type": "error"}

    def test_error_chunks_markdown(self) -> None:
        chunks = list(StreamSink("markdown").error_chunks("boom"))
        assert chunks[0].startswith("&#x274c;")
        assert "boom" in chunks[1]


class TestRunGraph:
    def setup_method(self) -> None:
        clear_registry()

    def teardown_method(self) -> None:
        clear_registry()

    def test_run_generator_builder(self) -> None:
        def builder(ctx, **kwargs):  # noqa: ANN001, ANN003
            assert ctx == {"hello": "world"}

            def _gen():
                yield emit({"type": "message", "content": "hi"})
                yield emit({"type": "finish"})

            return _gen()

        register_graph("echo", builder)
        frames = list(run_graph("echo", {"hello": "world"}))
        assert len(frames) == 2
        body = json.loads(frames[0][len("data:") :].strip())
        assert body["type"] == "message"
        assert body["content"] == "hi"

    def test_run_langgraph_custom_stream(self) -> None:
        from typing import TypedDict

        from langgraph.config import get_stream_writer
        from langgraph.graph import END, START, StateGraph

        class S(TypedDict, total=False):
            x: int

        def node(state: S) -> S:
            w = get_stream_writer()
            w(emit({"type": "analysis-result", "content": "ok"}))
            w(emit({"type": "analysis_finish"}))
            return {}

        def builder(ctx, **kwargs):  # noqa: ANN001, ANN003
            g = StateGraph(S)
            g.add_node("n", node)
            g.add_edge(START, "n")
            g.add_edge("n", END)
            return g.compile()

        register_graph("analysis_probe", builder)
        frames = list(run_graph("analysis_probe", {}))
        assert len(frames) == 2
        body = json.loads(frames[0][len("data:") :].strip())
        assert body["type"] == "analysis-result"

    def test_submit_graph_is_sole_entry(self) -> None:
        def builder(ctx, **kwargs):  # noqa: ANN001, ANN003
            def _gen():
                yield emit({"type": "finish"})

            return _gen()

        register_graph("only", builder)
        runner = submit_graph("only", {"sink": "sse"})
        while runner.is_running(timeout=0.05):
            pass
        chunks = list(runner.await_result())
        assert len(chunks) == 1
        body = json.loads(chunks[0][len("data:") :].strip())
        assert body["type"] == "finish"

    def test_submit_graph_error_uses_sink(self) -> None:
        def builder(ctx, **kwargs):  # noqa: ANN001, ANN003
            def _gen():
                raise RuntimeError("explode")
                yield  # pragma: no cover

            return _gen()

        register_graph("boom", builder)
        runner = submit_graph("boom", {"sink": "sse"})
        while runner.is_running(timeout=0.05):
            pass
        chunks = list(runner.await_result())
        assert len(chunks) == 1
        body = json.loads(chunks[0][len("data:") :].strip())
        assert body["type"] == "error"
        assert "explode" in body["content"]


class TestProductionGraphSurface:
    """Sanity: YAML topology files exist for all five product graph keys."""

    def test_product_graph_yaml_files_exist(self) -> None:
        """YAML files under graphs/current/ must exist for each production key."""
        expected = {
            "chat": "graphs/current/chat.yaml",
            "analysis": "graphs/current/analysis.yaml",
            "predict": "graphs/current/predict.yaml",
            "recommend": "graphs/current/recommend.yaml",
            "config": "graphs/current/config.yaml",
        }
        for key, rel in expected.items():
            path = _BACKEND / rel
            assert path.exists(), f"missing YAML for {key!r} at {rel}"
            text = path.read_text(encoding="utf-8")
            assert f"graph_key: {key}" in text, f"{rel} must declare graph_key: {key}"

    def test_no_register_graph_in_graph_modules(self) -> None:
        """Graph modules are thin re-exports; register_graph lives only in loader."""
        stale_files = [
            "apps/chat/graphs/nlq.py",
            "apps/chat/graphs/analysis.py",
            "apps/chat/graphs/predict.py",
            "apps/chat/graphs/recommend.py",
            "apps/config_assistant/graph.py",
        ]
        for rel in stale_files:
            text = (_BACKEND / rel).read_text(encoding="utf-8")
            assert "register_graph(" not in text, (
                f"{rel} must not contain register_graph() — registration is YAML-driven"
            )


class TestConfigAssistantSurface:
    """Static guards for the config primary graph (no DB / no xpack)."""

    def test_config_state_uses_bound_tools_not_tools_channel(self) -> None:
        text = (_BACKEND / "apps/config_assistant/nodes.py").read_text(encoding="utf-8")
        assert "bound_tools: List" in text
        assert "def run_tools_node" in text

    def test_config_process_uses_chatlog_not_tool_trace(self) -> None:
        """Process channel is ChatLog (TOOL_CALL/CONFIG_AGENT); no tool_trace dual path."""
        text = (_BACKEND / "apps/config_assistant/nodes.py").read_text(encoding="utf-8")
        assert "tool_trace" not in text
        assert "OperationEnum.TOOL_CALL" in text
        assert "OperationEnum.CONFIG_AGENT" in text
        assert "start_log" in text and "end_log" in text
        # Final answer is plain text only.
        assert "final_text or tool_trace" not in text
        assert 'answer = final_text' in text or "answer = final_text" in text

    def test_operation_enum_has_config_ops(self) -> None:
        text = (_BACKEND / "apps/chat/models/chat_model.py").read_text(encoding="utf-8")
        assert "TOOL_CALL = '14'" in text
        assert "CONFIG_AGENT = '15'" in text

    def test_config_tools_have_no_execsql(self) -> None:
        text = (_BACKEND / "apps/config_assistant/tools.py").read_text(encoding="utf-8")
        names = [
            "list_datasources",
            "get_datasource",
            "create_datasource",
            "update_datasource",
            "check_datasource",
            "list_catalog_tables",
            "list_selected_tables",
            "choose_tables",
            "list_catalog_fields",
            "list_table_fields",
            "update_table_meta",
            "update_field_meta",
            "get_sample_data",
        ]
        for n in names:
            assert f'name="{n}"' in text, f"missing tool registration {n}"
        # No business SQL execution tool registration (mentions in docs are fine).
        assert "name=\"execSql\"" not in text
        assert "name=\"runSql\"" not in text
        assert "name=\"execute_sql\"" not in text
        assert "def exec" not in text
        assert "_assert_ds_in_workspace" in text
        assert "_assert_ds_writable" in text
        assert "aes_encrypt" in text
        assert "run_coro_sync" in text
        # choose_tables supports mode=add|remove|set (single write path via chooseTables).
        assert 'mode: str = Field' in text or 'mode: str =' in text
        assert 'normalized == "add"' in text or 'mode="add"' in text
        assert 'normalized == "set"' in text
        assert '{"add", "remove", "set"}' in text or '"remove"' in text
        # Sample preview reuses protocol sample path — not a free SQL / chart pipeline.
        assert "get_table_sample_data" in text
        assert "CAP_SAMPLE_DATA" in text
        assert "generate_chart" not in text
        assert "save_chart" not in text

    def test_config_prompt_forbids_execsql(self) -> None:
        text = (_BACKEND / "apps/config_assistant/prompt.py").read_text(encoding="utf-8")
        assert "execSql" in text
        assert "SYSTEM_PROMPT" in text
        # Add-table cookbook: default mode=add, never set with only new names.
        assert 'mode="add"' in text
        assert "choose_tables" in text
        # Sample preview cookbook; chart analysis routed to NLQ.
        assert "get_sample_data" in text
        assert "CAP_SAMPLE_DATA" in text
        assert "NLQ" in text

    def test_node_name_channel_collision_rule(self) -> None:
        """LangGraph forbids node ids that equal state channel keys — prove rename works."""
        from typing import TypedDict

        from langgraph.graph import END, START, StateGraph

        class S(TypedDict, total=False):
            tools: list
            bound_tools: list

        def _n(state: S) -> S:
            return state

        # Bad: node id collides with `tools` channel.
        raised = False
        try:
            bad = StateGraph(S)
            bad.add_node("tools", _n)
            bad.add_edge(START, "tools")
            bad.add_edge("tools", END)
            bad.compile()
        except Exception:
            raised = True
        assert raised, "LangGraph should reject node id that collides with state channel"

        # Good: run_tools style name works.
        good = StateGraph(S)
        good.add_node("run_tools", _n)
        good.add_edge(START, "run_tools")
        good.add_edge("run_tools", END)
        compiled = good.compile()
        assert compiled is not None


    def test_async_util_exported_helper(self) -> None:
        async_util = _load("apps.conversation.async_util", "apps/conversation/async_util.py")

        async def _one() -> int:
            return 1

        assert async_util.run_coro_sync(_one()) == 1


class TestEmbeddingRecallContract:
    """Table/DS vector recall is settings-owned; no LLMService/API embedding flag."""

    def test_llm_service_has_no_embedding_param(self) -> None:
        text = (_BACKEND / "apps/chat/task/llm.py").read_text(encoding="utf-8")
        assert "embedding" not in text.split("def __init__")[1].split("def ")[0]
        assert "self.embedding" not in text
        assert "TABLE_EMBEDDING_ENABLED" in text  # docstring contract

    def test_chat_graphs_steps_never_pass_embedding_kwarg(self) -> None:
        roots = [
            _BACKEND / "apps/chat/graphs",
            _BACKEND / "apps/chat/steps",
            _BACKEND / "apps/chat/api",
            _BACKEND / "apps/chat/task",
        ]
        # Real keyword-arg usage only (not docstrings mentioning the rule).
        import re

        code_kw = re.compile(r"(?<![`\w])embedding\s*=\s*(True|False|embedding|\w+)")
        offenders: list[str] = []
        for root in roots:
            if not root.exists():
                continue
            for path in root.rglob("*.py"):
                for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                    stripped = line.lstrip()
                    if stripped.startswith("#"):
                        continue
                    if code_kw.search(line):
                        offenders.append(f"{path.relative_to(_BACKEND)}:{i}:{line.strip()}")
        assert not offenders, "chat layer must not pass embedding=; offenders:\n" + "\n".join(offenders)

    def test_nlq_chart_uses_resource_filter_not_embedding_override(self) -> None:
        text = (_BACKEND / "apps/chat/graphs/nodes/nlq.py").read_text(encoding="utf-8")
        assert "embedding=False" not in text
        # Agentic batch loop uses table_list for resource filtering in chart generation
        assert "table_list=" in text

    def test_match_table_schema_omits_embedding_kwarg(self) -> None:
        text = (_BACKEND / "apps/chat/steps/schema.py").read_text(encoding="utf-8")
        assert "retrieve_schema(" in text
        assert "embedding=" not in text.split("retrieve_schema(")[1].split(")")[0]
        assert "TABLE_EMBEDDING_ENABLED" in text


class TestCreateChatConfigContract:
    """curd.create_chat is the single truth for config DS requirement."""

    def test_config_chat_type_resolved_before_ds_required_check(self) -> None:
        text = (_BACKEND / "apps/chat/curd/chat.py").read_text(encoding="utf-8")
        # Locate create_chat body and ensure chat_type/config gate precedes DS raise.
        start = text.index("def create_chat(")
        body = text[start : start + 1800]
        idx_type = body.index('chat_type not in ("chat", "config")')
        idx_config = body.index('chat_type == "config"')
        idx_ds = body.index('raise Exception("Datasource cannot be None")')
        assert idx_type < idx_config < idx_ds, (
            "config must force require_datasource=False before DS None check"
        )

    def test_dynamic_ds_types_single_source(self) -> None:
        constants = (_BACKEND / "apps/chat/constants.py").read_text(encoding="utf-8")
        assert "DYNAMIC_DS_TYPES" in constants
        assert "[1, 3]" in constants or "(1, 3)" in constants
        # No second literal lists in high-traffic modules.
        for rel in (
            "apps/chat/curd/chat.py",
            "apps/chat/task/llm.py",
            "apps/chat/graphs/nodes/nlq.py",
            "apps/chat/steps/datasource.py",
        ):
            text = (_BACKEND / rel).read_text(encoding="utf-8")
            assert "from apps.chat.constants import DYNAMIC_DS_TYPES" in text or (
                "from apps.chat.constants import" in text and "DYNAMIC_DS_TYPES" in text
            ), f"{rel} must import DYNAMIC_DS_TYPES from constants"
            assert "DYNAMIC_DS_TYPES = [1, 3]" not in text
            assert "type in (1, 3)" not in text


class TestGraphLoader:
    """Graph spec parsing + YAML topology validation (no DB, no LLM)."""

    def _load_spec_module(self):
        return _load("apps.conversation.graph_spec", "apps/conversation/graph_spec.py")

    def _load_routers_builtin(self):
        return _load("apps.conversation.routers_builtin", "apps/conversation/routers_builtin.py")

    def _parse_current_yaml(self, filename: str):
        import yaml as _yaml

        spec_mod = self._load_spec_module()
        path = _BACKEND / "graphs" / "current" / filename
        raw = _yaml.safe_load(path.read_text(encoding="utf-8"))
        return spec_mod.parse_graph_spec(raw, source_path=str(path))

    def test_parse_chat_yaml(self) -> None:
        spec = self._parse_current_yaml("chat.yaml")
        assert spec.graph_key == "chat"
        assert spec.version == 1
        assert "prepare_record" in spec.nodes
        assert "fail" in spec.nodes
        # At least one edge from START
        assert any(
            (hasattr(e, "source") and e.source == "START") for e in spec.edges
        )

    def test_parse_analysis_yaml(self) -> None:
        spec = self._parse_current_yaml("analysis.yaml")
        assert spec.graph_key == "analysis"
        assert "prepare" in spec.nodes

    def test_parse_predict_yaml(self) -> None:
        spec = self._parse_current_yaml("predict.yaml")
        assert spec.graph_key == "predict"
        assert "parse" in spec.nodes

    def test_parse_recommend_yaml(self) -> None:
        spec = self._parse_current_yaml("recommend.yaml")
        assert spec.graph_key == "recommend"
        assert "generate" in spec.nodes

    def test_parse_config_yaml(self) -> None:
        spec = self._parse_current_yaml("config.yaml")
        assert spec.graph_key == "config"
        assert "agent" in spec.nodes

    def test_ok_or_fail_router(self) -> None:
        builtins = self._load_routers_builtin()
        route = builtins.ok_or_fail("next_node")
        assert route({"error": None}) == "next_node"
        assert route({"error": "boom"}) == "fail"
        assert route({}) == "next_node"

    def test_parse_bad_yaml_missing_graph_key(self) -> None:
        spec_mod = self._load_spec_module()
        with pytest.raises(Exception):
            spec_mod.parse_graph_spec({"version": 1, "state": "x.y", "nodes": {"a": "b"}, "edges": []})

    def test_parse_bad_yaml_unknown_router_type(self) -> None:
        spec_mod = self._load_spec_module()
        raw = {
            "version": 1,
            "graph_key": "x",
            "state": "x.y",
            "nodes": {"a": "x.y", "fail": "x.y"},
            "edges": [
                {"from": "START", "to": "a"},
                {"from": "a", "router": {"type": "bogus"}, "paths": {"b": "fail"}},
            ],
        }
        with pytest.raises(Exception):
            spec_mod.parse_graph_spec(raw, source_path="test")

    def test_target_chat_yaml_parses(self) -> None:
        """Target chat.yaml must parse even though it's not default-loaded."""
        import yaml as _yaml

        spec_mod = self._load_spec_module()
        path = _BACKEND / "graphs" / "target" / "chat.yaml"
        raw = _yaml.safe_load(path.read_text(encoding="utf-8"))
        spec = spec_mod.parse_graph_spec(raw, source_path=str(path))
        assert spec.graph_key == "chat"
        assert "dlg_resolve_anchor" in spec.nodes
        assert "route_turn" in spec.nodes


if __name__ == "__main__":
    # Manual runner when pytest is not installed.
    results = []
    for cls_name, cls in list(globals().items()):
        if not (isinstance(cls, type) and cls_name.startswith("Test")):
            continue
        inst = cls()
        for name in dir(inst):
            if not name.startswith("test_"):
                continue
            if hasattr(inst, "setup_method"):
                inst.setup_method()
            try:
                getattr(inst, name)()
                results.append((f"{cls_name}.{name}", "PASS"))
            except Exception as e:  # noqa: BLE001
                results.append((f"{cls_name}.{name}", f"FAIL: {e}"))
            finally:
                if hasattr(inst, "teardown_method"):
                    inst.teardown_method()
    for name, status in results:
        print(f"{status:4} {name}")
    failed = [r for r in results if r[1] != "PASS"]
    if failed:
        raise SystemExit(1)
    print(f"\n{len(results)} passed")
