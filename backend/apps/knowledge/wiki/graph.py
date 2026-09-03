"""Wikilink adjacency graph with alias resolution (llm-wiki search.rs port)."""

from __future__ import annotations

from apps.knowledge.wiki.contract import WikiPage, normalize_link_target

AliasMap = dict[str, str]
Adjacency = dict[str, set[str]]


def fold_key(name: str) -> str:
    """Lookup folding: snake/kebab 等价（v0 草稿自身两种写法并存，解析层收敛）."""
    return normalize_link_target(name).replace("_", "-")


def build_graph(pages: dict[str, WikiPage]) -> tuple[Adjacency, AliasMap]:
    """Undirected adjacency over ``[[wikilink]]`` edges + alias resolution map.

    Each page registers its page_key, title and aliases (folded) — the same
    4-alias registration idea llm-wiki uses for link targets.
    """
    alias_map: AliasMap = {}
    for key, page in pages.items():
        for name in page.identity_aliases:
            alias_map.setdefault(fold_key(name), key)

    adjacency: Adjacency = {key: set() for key in pages}
    for key, page in pages.items():
        for link in page.links:
            # 查询与注册同键折叠（snake/kebab 等价）——曾经原样查询导致
            # snake_case 目标解析失败、图扩展丢边（[[cust_company_info]] 不可达）。
            target = alias_map.get(fold_key(link.target))
            if target is None or target == key:
                continue
            adjacency[key].add(target)
            adjacency.setdefault(target, set()).add(key)
    return adjacency, alias_map
