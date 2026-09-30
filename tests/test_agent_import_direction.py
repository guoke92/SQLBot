"""Lock product-agent import direction: Host must not import ChatBI loop internals."""

from __future__ import annotations

import ast
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
_AGENT = _BACKEND / "apps" / "chat" / "agent"
_CONVERSATION = _BACKEND / "apps" / "conversation"


def _module_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text())
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def test_host_runtime_does_not_import_product_agent() -> None:
    src = (_CONVERSATION / "runtime.py").read_text()
    assert "apps.chat.graphs.nodes" not in src
    assert "apps.chat.agent" not in src
    assert "try_publish_query_salvage" not in src
    imports = _module_imports(_CONVERSATION / "runtime.py")
    assert "apps.conversation.graph_hooks" in imports or "graph_hooks" in src


def test_host_runtime_context_does_not_import_product_tools() -> None:
    src = (_CONVERSATION / "runtime_context.py").read_text()
    assert "build_agent_tools" not in src
    assert "apps.chat.agent" not in src
    assert "apps.chat.agent_config" not in src
    assert "try_hydrate" in src


def test_host_tooling_does_not_import_knowledge_plane() -> None:
    src = (_CONVERSATION / "tooling.py").read_text()
    assert "agent_knowledge" not in src
    assert "AgentKnowledgePlane" not in src


def test_loop_does_not_call_wiki_or_sql_tools() -> None:
    src = (_AGENT / "loop.py").read_text()
    assert "apps.chat.tools.execute_sql" not in src
    assert "apps.chat.tools.wiki_search" not in src
    assert "apps.chat.tools.catalog_tools" not in src


def test_agent_package_does_not_import_conversation_runtime_salvage() -> None:
    forbidden = "apps.conversation.runtime"
    for path in _AGENT.rglob("*.py"):
        names = _module_imports(path)
        assert forbidden not in names, path
