"""Surgical wiki scrub: drop polluted dicts + comment_fk fences."""

from __future__ import annotations

from pathlib import Path

import yaml

from tools.wiki_extract.scrub_wiki import run_scrub


def test_scrub_drops_sp_no_dict_and_adds_comment_fk(tmp_path: Path) -> None:
    wiki = tmp_path / "wiki"
    tables = wiki / "tables"
    dicts = wiki / "dicts"
    raw = wiki / "_raw"
    for d in (tables, dicts, raw):
        d.mkdir(parents=True)

    catalog = {
        "database": "db",
        "tables": {
            "wechat_project_approval_apply": {
                "primary_key": ["id"],
                "columns": {
                    "id": {"type": "bigint", "comment": ""},
                    "sp_no": {"type": "varchar(32)", "comment": "审批单号"},
                },
            },
            "tenant_project_approval": {
                "primary_key": ["id"],
                "columns": {
                    "id": {"type": "bigint", "comment": ""},
                    "sp_no": {
                        "type": "varchar(32)",
                        "comment": "立项审批编号（wechat_project_approval_apply#sp_no）",
                    },
                    "enable": {"type": "varchar(1)", "comment": "是否启用"},
                    "node_order": {"type": "int", "comment": "节点顺序"},
                },
            },
        },
    }
    profile = {
        "tables": {
            "tenant_project_approval": {
                "column_stats": {
                    "sp_no": {
                        "distinct": 2,
                        "values": {"202604270003": 1, "MN-202606230165": 1},
                    },
                    "enable": {"distinct": 1, "values": {"Y": 10}},
                    "node_order": {
                        "distinct": 3,
                        "values": {"1": 1, "2": 1, "3": 1},
                    },
                }
            }
        }
    }
    (raw / "catalog.yaml").write_text(
        yaml.safe_dump(catalog, allow_unicode=True), encoding="utf-8"
    )
    (raw / "profile.yaml").write_text(
        yaml.safe_dump(profile, allow_unicode=True), encoding="utf-8"
    )

    (tables / "wechat_project_approval_apply.md").write_text(
        "---\ntype: table\npage_key: wechat_project_approval_apply\nrelated: []\n---\n"
        "# wechat\n\n## 字段\n\n```ground:table\n"
        "table: wechat_project_approval_apply\nfields:\n"
        "- name: id\n  type: number\n"
        "- name: sp_no\n  type: string\n"
        "```\n",
        encoding="utf-8",
    )
    (tables / "tenant_project_approval.md").write_text(
        "---\n"
        "type: table\n"
        "page_key: tenant_project_approval\n"
        "related:\n"
        "- tenant_project_approval__sp_no\n"
        "- tenant_project_approval__enable\n"
        "---\n"
        "# approval\n\n"
        "## 字段\n\n"
        "```ground:table\n"
        "table: tenant_project_approval\n"
        "fields:\n"
        "- name: id\n"
        "  type: number\n"
        "- name: sp_no\n"
        "  type: string\n"
        "  desc: 立项审批编号（wechat_project_approval_apply#sp_no）\n"
        "  dict: ['202604270003', MN-202606230165]\n"
        "- name: enable\n"
        "  type: string\n"
        "  desc: 是否启用\n"
        "  dict: [Y]\n"
        "- name: node_order\n"
        "  type: number\n"
        "  desc: 节点顺序\n"
        "  dict: ['1', '2', '3']\n"
        "```\n\n"
        "## 页面链接\n\n"
        "### 字典\n\n"
        "- [[dicts/tenant_project_approval__sp_no]]（`tenant_project_approval.sp_no`）\n"
        "- [[dicts/tenant_project_approval__enable]]（`tenant_project_approval.enable`）\n"
        "- [[dicts/tenant_project_approval__node_order]]（`tenant_project_approval.node_order`）\n",
        encoding="utf-8",
    )
    for key in (
        "tenant_project_approval__sp_no",
        "tenant_project_approval__enable",
        "tenant_project_approval__node_order",
    ):
        (dicts / f"{key}.md").write_text(f"# {key}\n", encoding="utf-8")

    report = run_scrub(wiki_dir=wiki, raw_dir=raw, chat=None, write=True)
    assert report["fields_dict_cleared"] >= 2
    text = (tables / "tenant_project_approval.md").read_text(encoding="utf-8")
    assert "name: sp_no" in text
    assert "dict: ['202604270003'" not in text
    assert "dict: ['1', '2', '3']" not in text
    assert "wechat_project_approval_apply.sp_no" in text
    assert "source: comment_fk" in text
    assert "tenant_project_approval__sp_no" not in (
        yaml.safe_load(
            text.split("---\n", 2)[1]
        ).get("related")
        or []
    )
    assert not (dicts / "tenant_project_approval__sp_no.md").exists()
    assert not (dicts / "tenant_project_approval__node_order.md").exists()
    # enable kept as binary switch (incomplete Y only; no LLM fill)
    assert "name: enable" in text
    ground = yaml.safe_load(
        __import__("re").search(r"```ground:table\n([\s\S]*?)\n```", text).group(1)
    )
    enable = next(f for f in ground["fields"] if f["name"] == "enable")
    assert list(enable.get("dict") or []) == ["Y"]
    node = next(f for f in ground["fields"] if f["name"] == "node_order")
    assert "dict" not in node
    sp = next(f for f in ground["fields"] if f["name"] == "sp_no")
    assert "dict" not in sp
