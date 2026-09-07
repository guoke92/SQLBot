"""Guard production modules against user-visible CJK literals and business prefixes."""

from __future__ import annotations

import ast
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"

# Modules rewritten by the unified process-timeline work. Prompt templates and
# locales are excluded: user-visible copy belongs in i18n files.
_SCAN_FILES = [
    _BACKEND / "apps/conversation/process_timeline.py",
    _BACKEND / "apps/conversation/tooling.py",
    _BACKEND / "apps/conversation/agent.py",
    _BACKEND / "apps/chat/graphs/nodes/unified_agent.py",
    _BACKEND / "apps/chat/graphs/nodes/agent_finalize.py",
    _BACKEND / "apps/chat/graphs/nodes/agent_clarify.py",
    _BACKEND / "apps/chat/tools/metadata.py",
    _BACKEND / "apps/chat/tools/execute_sql.py",
    _BACKEND / "apps/chat/steps/enum_display.py",
]
_PREFIX_FILES = [
    *_SCAN_FILES,
    _BACKEND / "apps/knowledge/wiki/baseline.py",
]

_CJK_RE = r"[\u3400-\u9fff]"
_BANNED_PREFIX_TOKENS = ("cust_", "tenant_", "platform_")


def _string_literals(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    docstring_ids = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
            body = list(node.body)
            if (
                body
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)
            ):
                docstring_ids.add(id(body[0].value))
    values: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if id(node) in docstring_ids:
                continue
            values.append(node.value)
    return values


def test_process_timeline_modules_have_no_cjk_string_literals() -> None:
    import re

    pattern = re.compile(_CJK_RE)
    hits: list[str] = []
    for path in _SCAN_FILES:
        assert path.exists(), path
        for literal in _string_literals(path):
            if pattern.search(literal):
                hits.append(f"{path.relative_to(_ROOT)}: {literal[:80]}")
    assert hits == []


def test_no_hardcoded_business_column_prefixes() -> None:
    hits: list[str] = []
    for path in _PREFIX_FILES:
        assert path.exists(), path
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "_BUSINESS_PREFIXES":
                        hits.append(str(path))
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if node.value in _BANNED_PREFIX_TOKENS:
                    hits.append(f"{path}: {node.value}")
    assert hits == []
