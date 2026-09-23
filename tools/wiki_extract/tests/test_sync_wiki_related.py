"""sync_wiki_related preserves soft table peers (non-EQUI related)."""

from __future__ import annotations

from pathlib import Path

import yaml

from tools.wiki_extract.sync_wiki_related import run_sync


def test_sync_preserves_soft_table_related(tmp_path: Path) -> None:
    wiki = tmp_path / "wiki"
    tables = wiki / "tables"
    tables.mkdir(parents=True)
    (wiki / "concepts").mkdir()

    (tables / "alpha.md").write_text(
        "---\n"
        "type: table\n"
        "page_key: alpha\n"
        "related: [beta, soft_peer, alpha__enable]\n"
        "---\n\n"
        "# alpha\n\n"
        "## 关联关系\n\n"
        "```ground:relation\n"
        "type: EQUI_JOIN\n"
        "left: alpha.id\n"
        "right: beta.alpha_id\n"
        "trust: confirmed\n"
        "```\n\n"
        "## 页面链接\n\n"
        "### 关联表\n\n"
        "- [[tables/beta]]\n",
        encoding="utf-8",
    )
    (tables / "beta.md").write_text(
        "---\n"
        "type: table\n"
        "page_key: beta\n"
        "related: [alpha]\n"
        "---\n\n"
        "# beta\n\n"
        "## 关联关系\n\n"
        "## 页面链接\n\n",
        encoding="utf-8",
    )
    (tables / "soft_peer.md").write_text(
        "---\n"
        "type: table\n"
        "page_key: soft_peer\n"
        "related: [alpha]\n"
        "---\n\n"
        "# soft_peer\n\n"
        "## 页面链接\n\n",
        encoding="utf-8",
    )

    stats = run_sync(wiki_dir=wiki, mirror_fences=True, concept_links=False)
    assert stats["edges"] >= 1

    front = yaml.safe_load(
        (tables / "alpha.md").read_text(encoding="utf-8").split("---\n", 2)[1]
    )
    related = list(front.get("related") or [])
    assert "beta" in related  # join neighbor
    assert "soft_peer" in related  # soft peer preserved
    assert "alpha__enable" in related  # non-table kept

    body = (tables / "alpha.md").read_text(encoding="utf-8")
    assert "[[tables/soft_peer]]" in body
    assert "[[tables/beta]]" in body
