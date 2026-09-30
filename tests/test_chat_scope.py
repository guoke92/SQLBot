"""Chat-scoped caching: datasource connection + access scope reuse across turns."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.steps import chat_scope as cs  # noqa: E402
from apps.datasource.access import AccessScope  # noqa: E402

# ── 缓存单元 ──────────────────────────────────────────────────────────────────


def test_connection_cache_ttl_and_invalidate(monkeypatch) -> None:
    cs.clear_chat_scope_cache()
    now = [1000.0]
    monkeypatch.setattr(cs.time, "monotonic", lambda: now[0])

    assert cs.connection_fresh(8) is False
    cs.remember_connection(8)
    assert cs.connection_fresh(8) is True

    now[0] += cs.CONNECTION_TTL_SEC + 1
    assert cs.connection_fresh(8) is False  # TTL 过期

    cs.remember_connection(8)
    cs.invalidate_connection(8)
    assert cs.connection_fresh(8) is False  # 失效即剔除


def test_scope_cache_distinguishes_none_from_missing(monkeypatch) -> None:
    cs.clear_chat_scope_cache()
    now = [1000.0]
    monkeypatch.setattr(cs.time, "monotonic", lambda: now[0])

    assert cs.is_missing(cs.cached_access_scope(1, 8, 5)) is True

    cs.remember_access_scope(1, 8, 5, None)  # 外部/无范围也是有效缓存值
    cached = cs.cached_access_scope(1, 8, 5)
    assert cs.is_missing(cached) is False
    assert cached is None

    scope = AccessScope(resource_names=("d_task",))
    cs.remember_access_scope(1, 8, 5, scope)
    got = cs.cached_access_scope(1, 8, 5)
    assert isinstance(got, AccessScope)
    assert got.resource_names == ("d_task",)

    # 不同 user 不共享
    assert cs.is_missing(cs.cached_access_scope(1, 8, 6)) is True

    now[0] += cs.SCOPE_TTL_SEC + 1
    assert cs.is_missing(cs.cached_access_scope(1, 8, 5)) is True


def test_execution_connection_failure_invalidates_cache() -> None:
    # 执行期连接失败反哺缓存：由 execute_queries_node 的失效分支保证
    # （kind == "connection" → invalidate_connection）。此处验证缓存语义闭环。
    cs.clear_chat_scope_cache()
    cs.remember_connection(8)
    assert cs.connection_fresh(8) is True
    cs.invalidate_connection(8)  # 执行失败路径调用
    assert cs.connection_fresh(8) is False


# ── 执行详情标签完整性 ────────────────────────────────────────────────────────


def test_summarize_label_present_in_all_locales() -> None:
    for loc in ("zh-CN", "en", "zh-TW", "ko-KR"):
        data = json.loads((_ROOT / "frontend/src/i18n" / f"{loc}.json").read_text())
        assert data["chat"]["log"].get("SUMMARIZE"), f"{loc} missing chat.log.SUMMARIZE"

