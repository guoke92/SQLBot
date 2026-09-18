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

    Bare names (page_key / title / aliases) register only when unique across
    the store. ``belong/page_key`` always registers so ambiguous slugs can be
    written as ``[[dicts/pay_status]]``.
    """
    claims: dict[str, list[str]] = {}
    for key, page in pages.items():
        names = [
            key,
            page.store_key,
            f"{page.belong}/{page.page_key}" if page.belong else "",
            page.page_key,
            page.title,
            *page.aliases,
        ]
        seen_folded: set[str] = set()
        for name in names:
            folded = fold_key(name)
            if not folded or folded in seen_folded:
                continue
            seen_folded.add(folded)
            bucket = claims.setdefault(folded, [])
            if key not in bucket:
                bucket.append(key)

    alias_map: AliasMap = {
        name: keys[0] for name, keys in claims.items() if len(keys) == 1
    }

    adjacency: Adjacency = {key: set() for key in pages}
    for key, page in pages.items():
        for link in page.links:
            target = alias_map.get(fold_key(link.target))
            if target is None or target == key:
                continue
            adjacency[key].add(target)
            adjacency.setdefault(target, set()).add(key)
    return adjacency, alias_map
