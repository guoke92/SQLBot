"""Schema & knowledge maps for the planner prompt.

Visibility precedes gap-signaling: the planner can only declare
``missing_concepts`` for concepts it can see exist. The schema map lists the
AccessScope-fenced catalog one line per table (tiered by catalog size); the
knowledge map lists active published units one line each. Both are cheap
deterministic queries recomputed per planning attempt — they are prompt
content, not persisted ``planning_context`` state.
"""

from __future__ import annotations

from typing import Any

from sqlmodel import Session, select

from apps.datasource.models.datasource import CoreTable
from apps.knowledge.compile import active_published_units

_FULL_TIER_MAX = 40
_GROUP_TIER_MAX = 300
_KNOWLEDGE_MAP_MAX = 30
_COMMENT_WIDTH = 40
_DESCRIPTION_WIDTH = 60
_CHAR_BUDGET = 6000
# Beyond this catalog size the map is dropped entirely: a large governed
# catalog is expected to carry a mature knowledge package (units already
# encode table semantics), and a raw name list that big adds noise, not
# signal. Recall then leans on the knowledge plane + planner gap-signaling.
_CATALOG_MAP_MAX = 20


def _clip(text: str, width: int) -> str:
    text = " ".join(str(text or "").split())
    return text[:width] + ("…" if len(text) > width else "")


def render_schema_map(
    session: Session,
    *,
    ds: Any,
    access_scope: Any = None,
    exclude: frozenset[str] | set[str] | None = None,
) -> str:
    """One compact catalog inventory line per table, tiered by size.

    ≤40 tables: full lines. ≤300: grouped by database/schema prefix with the
    table names inline. Beyond that: group summary counts only. Always fenced
    by the AccessScope table names. ``exclude`` removes tables already in the
    schema window — the map's job is exactly the *complement* of the window
    (what exists but the model has not seen), so window tables would only be
    noise. Catalogs beyond ``_CATALOG_MAP_MAX`` tables render no map at all:
    the knowledge package owns table semantics there.
    """
    ds_id = int(getattr(ds, "id", 0) or 0)
    if ds_id <= 0:
        return ""
    tables = list(
        session.exec(
            select(CoreTable)
            .where(
                CoreTable.ds_id == ds_id,
                CoreTable.checked == True,  # noqa: E712
            )
            .order_by(CoreTable.table_name.asc())
        ).all()
    )
    if access_scope is not None:
        allowed = set(access_scope.resource_names)
        tables = [table for table in tables if table.table_name in allowed]
    if len(tables) > _CATALOG_MAP_MAX:
        return ""
    if exclude:
        tables = [table for table in tables if table.table_name not in exclude]
    if not tables:
        return ""

    def _line(table: CoreTable) -> str:
        bits = [str(table.table_name)]
        comment = _clip(table.custom_comment, _COMMENT_WIDTH)
        if comment:
            bits.append(comment)
        if table.approx_rows is not None:
            bits.append(f"~{int(table.approx_rows)}行")
        return " | ".join(bits)

    lines: list[str]
    if len(tables) <= _FULL_TIER_MAX:
        lines = [_line(table) for table in tables]
    else:
        groups: dict[str, list[str]] = {}
        for table in tables:
            group = str(table.database_name or "").strip() or "default"
            groups.setdefault(group, []).append(str(table.table_name))
        lines = []
        for group in sorted(groups):
            names = groups[group]
            if len(tables) <= _GROUP_TIER_MAX:
                lines.append(f"== {group} ({len(names)}): " + ", ".join(names))
            else:
                lines.append(f"== {group} ({len(names)} tables)")

    header = f"【Schema map】({len(tables)} tables — 检索窗口之外仍可能有可用表)"
    body = "\n".join(lines)
    if len(body) > _CHAR_BUDGET:
        body = body[:_CHAR_BUDGET].rstrip() + "\n…(截断)"
    return header + "\n" + body + "\n"


def render_knowledge_map(
    session: Session,
    *,
    oid: int,
    ds_id: int,
    hit_keys: list[str] | None = None,
    databases: list[str] | None = None,
) -> str:
    """One line per active published knowledge unit bound to this datasource.

    wiki 后端（G6）：渲染 wiki 页面清单（tables/enums/concepts/… 子目录的
    published 页），规划器看到的"知识地图"与召回语料同源。
    ``databases`` = 当前数据源物理库名（scope.databases 围栏，与召回围栏同源）。
    ``hit_keys`` 非空时（wiki 后端）只渲染召回命中页——prompt 瘦身；
    plan gate 的 missing_concepts 校验走完整目录，不受此影响。
    """
    if _wiki_backend_active(ds_id):
        return _wiki_knowledge_map(ds_id, hit_keys=hit_keys, databases=databases or [])
    rows = active_published_units(session, oid=oid, datasource_id=ds_id)
    rows = sorted(
        rows, key=lambda row: (str(row[0].domain or ""), str(row[0].title or ""))
    )
    if not rows:
        return ""
    lines: list[str] = []
    for unit, revision in rows[:_KNOWLEDGE_MAP_MAX]:
        description = ""
        content = revision.content
        if isinstance(content, dict):
            description = _clip(content.get("description"), _DESCRIPTION_WIDTH)
        bits = [str(unit.title or unit.unit_key), str(unit.domain or "")]
        if description:
            bits.append(description)
        lines.append(" | ".join(bit for bit in bits if bit))
    hidden = len(rows) - len(lines)
    if hidden > 0:
        lines.append(f"…(+{hidden} more)")
    header = "【Knowledge map】(已发布知识单元 — 口径/指标/规则以单元定义为准)"
    return header + "\n" + "\n".join(lines) + "\n"


def _wiki_backend_active(ds_id: int) -> bool:
    """KNOWLEDGE_BACKEND=wiki 且该 DS 已灰度——复用 wiki_recall 的单一判定。"""
    from apps.chat.steps.wiki_recall import wiki_backend_active

    return wiki_backend_active(ds_id)


def _wiki_knowledge_map(
    ds_id: int,  # noqa: ARG001 — 仅 allowlist判定经 _wiki_backend_active 使用
    hit_keys: list[str] | None = None,
    databases: list[str] | None = None,
) -> str:
    """wiki 页面清单（type|page_key|title 一行一页，封顶 _KNOWLEDGE_MAP_MAX）。

    ``hit_keys``：本轮召回命中的页。提供时只渲染命中页（chat 167：560 页
    目录里 32 行 + "(+527 more)" 对规划器是纯噪音——召回明细已由
    business_knowledge 段承载，地图只回答"还有哪些可用"）。
    ``databases``：物理库名围栏（scope.databases），与召回围栏同源。"""
    try:
        from apps.chat.steps.wiki_recall import _store

        store = _store()
        if store is None:
            return ""
        db_names = {str(name).strip().lower() for name in (databases or [])}
        if hit_keys:
            pages = [
                store.pages[key]
                for key in dict.fromkeys(hit_keys)
                if key in store.pages and store.pages[key].status == "published"
            ]
        else:
            pages = [
                page
                for page in store.pages.values()
                if page.status == "published"
                and (not page.databases or db_names & set(page.databases))
            ]
        pages.sort(key=lambda p: (p.type, p.page_key))
        if not pages:
            return ""
        lines = [
            f"{p.type} | {p.page_key} | {p.title}" for p in pages[:_KNOWLEDGE_MAP_MAX]
        ]
        hidden = len(pages) - len(lines)
        if hidden > 0:
            lines.append(f"…(+{hidden} more)")
        header = "【Knowledge map】(wiki 页面 — 口径/枚举/关系以页面锚点块为准)"
        return header + "\n" + "\n".join(lines) + "\n"
    except Exception:  # noqa: BLE001 — wiki 层零影响约定
        return ""
