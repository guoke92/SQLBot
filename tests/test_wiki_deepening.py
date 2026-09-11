"""Wiki deepening tests — enum merge bindings / schema render / value translate.

覆盖 P1（枚举归并与泛列防复发）、P2（table 页 schema 渲染 + 列全集）、
P3（结果枚举值→描述翻译）三段。
"""

from __future__ import annotations

import sys
from pathlib import Path


_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.chat.steps.wiki_recall import translate_enum_cells  # noqa: E402
from apps.chat.steps.wiki_schema import WikiSchemaRenderer  # noqa: E402
from apps.knowledge.wiki.baseline import (  # noqa: E402
    _carrier_for_factory,
)
from apps.knowledge.wiki.contract import lint_page, parse_page  # noqa: E402

# ── P1：泛列黑名单与强证据绑定 ───────────────────────────────────────────────


def test_generic_column_blacklist_blocks_exact_and_prefix() -> None:
    """泛列（type/status/code…）exact-name 与 prefix-strip 双路都被拦。"""
    column_index = {
        "type": ["a.type", "b.type"],
        "status": ["a.status", "b.status"],
        "identify_style": ["cust_company_info.identify_style"],
        "cust_status": ["cust_company_info.cust_status"],
    }
    real_columns = {
        "a": {"type", "status"},
        "b": {"type", "status"},
        "cust_company_info": {"identify_style", "cust_status"},
    }
    table_bindings: dict[str, list[dict]] = {
        "cust_company_info.identify_style": [{"enum": "IdentifyTypeConstant"}]
    }
    entries = [{"field": "identify_type", "enum": "IdentifyTypeConstant", "values": []}]
    carrier = _carrier_for_factory(
        column_index,
        real_columns,
        table_bindings,
        entries,
        prefixes=("cust_",),
    )
    # exact-name 泛列 → unbound
    carriers, binding = carrier("status")
    assert carriers == [] and binding == "unbound"
    carriers, binding = carrier("type")
    assert carriers == [] and binding == "unbound"
    # 专有列前缀剥离 → 命中
    carriers, binding = carrier("cust_identify_style")
    assert "cust_company_info.identify_style" in carriers
    # 强证据 → 命中
    carriers, binding = carrier("identify_type")
    assert (
        "cust_company_info.identify_style" in carriers and binding == "setter-evidence"
    )


def test_lint_enum_generic_column_multi_table() -> None:
    """泛列承载多表 → ENUM_GENERIC_COLUMN lint error。"""
    page = parse_page(
        "---\ntype: enum\ntitle: s\npage_key: s\nstatus: published\n---\n- [[x]]\n"
        "```ground:enum\nenum: s\nfields: [a.status, b.status, c.status]\n"
        "values:\n  A:\n    label: 甲\n```\n"
    )
    catalog = {
        "tables": {
            "a": {"fields": {"status": {}}},
            "b": {"fields": {"status": {}}},
            "c": {"fields": {"status": {}}},
        },
        "enums": {},
    }
    codes = {f.code for f in lint_page(page, known_keys={"x"}, catalog=catalog)}
    assert "ENUM_GENERIC_COLUMN" in codes


# ── P2：wiki schema 渲染 ────────────────────────────────────────────────────


def test_schema_renderer_wiki_first_db_fallback(tmp_path: Path) -> None:
    class _Page:
        def __init__(self, body: str):
            self.body = body

    class _Store:
        def __init__(self):
            self.pages = {
                "t_wiki": _Page(
                    "```ground:table\ntable: t_wiki\ndesc: 维基表\n"
                    "fields:\n  - name: state\n    type: string\n"
                    "    phys: varchar(64)\n    desc: 状态\n"
                    "    topk: A|B\n```\n"
                )
                # t_missing 无 ground 块 → db 直渲
            }

    renderer = WikiSchemaRenderer(
        _Store(),
        {
            "tables": {
                "t_missing": {
                    "comment": "缺页表",
                    "columns": {"x": {"type": "int", "comment": "列x"}},
                }
            }
        },
    )
    text = renderer.render(["t_wiki", "t_missing"])
    assert "state:varchar, 状态, topk=A|B" in text
    assert "## 维基表 (t_wiki)" in text
    assert "## 缺页表 (t_missing) [db]" in text
    assert renderer._missing == ["t_missing"]


def test_schema_line_format_schema_field_labels_compatible() -> None:
    """渲染行格式必须被 presentation.schema_field_labels 解析（前端列 label 源）。"""
    from apps.chat.presentation import schema_field_labels

    class _Page:
        def __init__(self, body: str):
            self.body = body

    class _Store:
        def __init__(self):
            self.pages = {
                "t": _Page(
                    "```ground:table\ntable: t\ndesc: 表\n"
                    "fields:\n  - name: cust_status\n    type: string\n"
                    "    phys: varchar(64)\n    desc: 客户状态\n```\n"
                )
            }

    text = WikiSchemaRenderer(_Store(), {}).render(["t"])
    labels = schema_field_labels(text)
    assert labels.get("cust_status") == "客户状态"


# ── P3：枚举值翻译 ──────────────────────────────────────────────────────────


def test_translate_enum_cells_basic_and_miss() -> None:
    maps = {"cust_company_info.identify_style": {"INVITE_AGW": "邀请认证-内管录入"}}
    rows = [
        {"identify_style": "INVITE_AGW", "name": "甲公司"},
        {"identify_style": "SELF", "name": "乙公司"},
    ]
    translated, labels = translate_enum_cells(["identify_style", "name"], rows, maps)
    assert translated[0]["identify_style"] == "邀请认证-内管录入"
    assert translated[1]["identify_style"] == "SELF"  # 无映射原样
    assert translated[0]["name"] == "甲公司"
    assert labels == {"identify_style": {"INVITE_AGW": "邀请认证-内管录入"}}


def test_translate_enum_cells_empty_and_none() -> None:
    rows = [{"a": "x"}]
    out, labels = translate_enum_cells(["a"], rows, {})
    assert out == rows and labels == {}
    out2, labels2 = translate_enum_cells(["a"], [], {"t.a": {"x": "甲"}})
    assert out2 == [] and labels2 == {}


def test_translate_enum_cells_multi_table_same_column_merges() -> None:
    """多表同名列：值集取并（不同表的同名列枚举都可用）。"""
    maps = {
        "a.status": {"ADD": "新增"},
        "b.status": {"EFFECT": "生效"},
    }
    rows = [{"status": "ADD"}, {"status": "EFFECT"}]
    translated, _ = translate_enum_cells(["status"], rows, maps)
    assert translated[0]["status"] == "新增"
    assert translated[1]["status"] == "生效"


def test_schema_renderer_inlines_enum_labels(tmp_path: Path) -> None:
    """dict 指针指向的枚举页 value→label 走 labels=，topk 保持库内值。"""
    from types import SimpleNamespace

    from apps.chat.presentation import schema_field_labels

    enum_page = SimpleNamespace(
        body="```ground:enum\nenum: state\nfields: [t.state]\nvalues:\n"
        "  A:\n    label: 甲类\n  B:\n    label: 乙类\n```\n",
        ground_blocks=[
            SimpleNamespace(
                kind="enum",
                data={
                    "enum": "state",
                    "fields": ["t.state"],
                    "values": {"A": {"label": "甲类"}, "B": {"label": "乙类"}},
                },
                raw="",
            )
        ],
    )
    table_page = SimpleNamespace(
        body="```ground:table\ntable: t\ndesc: 表\n"
        "fields:\n  - name: state\n    type: string\n"
        "    phys: varchar(64)\n    desc: 状态\n    dict: state\n"
        "    topk: A|B\n  - name: plain\n    type: string\n"
        "    phys: varchar(64)\n    desc: 普通列\n    topk: X|Y\n```\n",
        ground_blocks=[],
    )

    class _Store:
        pages = {"state": enum_page, "t": table_page}

    text_out = WikiSchemaRenderer(_Store(), {}).render(["t"])
    assert (
        "state:varchar, 状态, topk=A|B, labels=A:甲类|B:乙类, enum=state"
    ) in text_out
    # 无 dict 指针的列保持裸 topk
    assert "plain:varchar, 普通列, topk=X|Y" in text_out
    # 前端列 label 不受内联影响
    labels = schema_field_labels(text_out)
    assert labels.get("state") == "状态"
    assert labels.get("plain") == "普通列"


def test_schema_renderer_enum_page_missing_keeps_raw_topk() -> None:
    """枚举页缺失/无 ground 块时回退裸 topk(与 enum_maps_for 同源宽松)。"""
    from types import SimpleNamespace

    table_page = SimpleNamespace(
        body="```ground:table\ntable: t\ndesc: 表\n"
        "fields:\n  - name: state\n    type: string\n"
        "    phys: varchar(64)\n    desc: 状态\n    dict: gone\n"
        "    topk: A|B\n```\n",
        ground_blocks=[],
    )

    class _Store:
        pages = {"t": table_page}  # "gone" 页不存在

    text_out = WikiSchemaRenderer(_Store(), {}).render(["t"])
    assert "state:varchar, 状态, topk=A|B, enum=gone" in text_out


# ── A4：锚点闭包（anchors.py） ──────────────────────────────────────────────


def _ns_page(**kwargs):
    from types import SimpleNamespace

    return SimpleNamespace(**kwargs)


def test_anchor_tables_from_anchors_field_targets_and_maps_to() -> None:
    """闭包三来源：anchors / field_targets / maps_to（含 表.列 解析）。"""
    from apps.knowledge.wiki.anchors import anchor_tables

    class _Store:
        pages = {
            "cust_company_info": _ns_page(),
            "cust_person_info": _ns_page(),
            "tenant_project": _ns_page(),
            "caliber-x": _ns_page(
                anchors=["cust_company_info"],
                field_targets=["cust_person_info.status"],
                maps_to="tenant_project.id = '123'",
            ),
        }

    tables = anchor_tables(_Store(), ["caliber-x"])
    assert tables == ["cust_company_info", "cust_person_info", "tenant_project"]


def test_anchor_tables_dedup_and_missing_filtered() -> None:
    """去重保序；无表页的引用不进闭包（由 anchor_tables_missing 上报）。"""
    from apps.knowledge.wiki.anchors import anchor_tables, anchor_tables_missing

    class _Page:
        anchors = ["cust_company_info", "ghost_table"]
        field_targets = ["cust_company_info.id"]
        maps_to = ""

    class _Store:
        pages = {"cust_company_info": _ns_page(), "p": _Page()}

    tables = anchor_tables(_Store(), ["p"])
    assert tables == ["cust_company_info"]
    assert anchor_tables_missing(_Store(), ["p"]) == ["ghost_table"]


def test_closure_tables_cap_and_truncated_count() -> None:
    """闭包上限由 max_tables 决定：超出截断并返回截断数。"""
    from apps.knowledge.wiki.anchors import closure_tables

    tables_in_store = {f"t{i}": _ns_page() for i in range(10)}

    class _Page:
        anchors = tuple(f"t{i}" for i in range(10))
        field_targets = ()
        maps_to = ""

    class _Store:
        pages = {**tables_in_store, "p": _Page()}

    closure, truncated = closure_tables(_Store(), ["p"], max_tables=6)
    assert len(closure) == 6
    assert truncated == 4
    default, default_cut = closure_tables(_Store(), ["p"])
    assert len(default) == 4
    assert default_cut == 6


# ── A5：渲染器关联段（关系通道） ────────────────────────────────────────────


def test_schema_renderer_renders_relation_section() -> None:
    """表页「## 关联表」节 → `关联:` 渲染行进 schema_text（JOIN 路径）。"""
    page = _ns_page(
        body=(
            "```ground:table\ntable: cust_group_rel\ndesc: 集团关系表\n"
            "fields:\n  - name: cust_id\n    type: bigint\n    desc: 客户\n```\n"
            "\n## 关联表\n\n"
            "- [[cust_company_info]]：cust_group_rel.cust_id → cust_company_info.id"
            "（write-flow:CustGroupMapper.xml，confirmed）\n"
            "- [[tenant_project]]：cust_group_rel.project_id → tenant_project.id"
            "（ref-convention，suggested）\n"
        )
    )

    class _Store:
        pages = {"cust_group_rel": page}

    text = WikiSchemaRenderer(_Store(), {}).render(["cust_group_rel"])
    assert (
        "关联: cust_group_rel.cust_id → cust_company_info.id "
        "(cust_company_info) [write-flow]"
    ) in text
    assert (
        "关联: cust_group_rel.project_id → tenant_project.id "
        "(tenant_project) [ref-convention]"
    ) in text
    assert "suggested" not in text
    assert "confirmed" not in text
    assert "CustGroupMapper" not in text
    assert "evidence" not in text


def test_relation_lines_do_not_pollute_schema_field_labels() -> None:
    """关联行不以字段行形态出现——不进 presentation.schema_field_labels 候选池。"""
    from apps.chat.presentation import schema_field_labels

    schema = (
        "## 表 (t)\n"
        "id:bigint, 主键\n"
        "关联: t.id → r.id (r) [write-flow]\n"
        "status:varchar(8), 状态\n"
    )
    labels = schema_field_labels(schema)
    assert labels == {"id": "主键", "status": "状态"}


def test_db_fallback_renders_ref_index_relations() -> None:
    """db 直渲兜底：ref_* 列 + 右表在 catalog → db-index 关联行。"""
    renderer = WikiSchemaRenderer(
        None,
        {
            "tables": {
                "t": {
                    "comment": "左表",
                    "columns": {
                        "id": {"type": "bigint", "comment": "主键"},
                        "ref_tenant_project": {"type": "bigint", "comment": "项目"},
                    },
                },
                "tenant_project": {
                    "comment": "项目表",
                    "columns": {"id": {"type": "bigint", "comment": "主键"}},
                },
            }
        },
    )
    text = renderer.render(["t"])
    assert (
        "关联: t.ref_tenant_project → tenant_project.id (tenant_project) [db-index]"
        in text
    )


# ── A6：enrich（wiki_enrich.py） ────────────────────────────────────────────


def _write_page(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


_TABLE_PAGE = (
    "---\ntype: table\ntitle: 主表\npage_key: t1\nstatus: published\n"
    "oid: 1\nscope:\n  databases: [db]\n"
    'sources: ["db:db-catalog.yaml"]\ncontract_version: "0.1"\n---\n\n'
    "# 主表\n\n（基线页：1 字段，行数估计 0。）\n\n"
    "```ground:table\ntable: t1\ndatabase: db\ndesc: 主表\nfields:\n"
    "  - name: id\n    type: bigint\n```\n"
)


def _make_corpus(tmp_path: Path) -> Path:
    """mini 语料：1 表页 t1 + substrate 双文件（relationships + db catalog）。"""
    import sys

    repo = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo / "scripts"))
    pages = tmp_path / "wiki-pages"
    _write_page(pages / "tables" / "t1.md", _TABLE_PAGE)
    system = tmp_path / "sys"
    substrate = system / "substrate"
    substrate.mkdir(parents=True, exist_ok=True)
    (substrate / "extract-relationships.yaml").write_text(
        "schema_version: '1.0'\nrelationships:\n"
        "- left_table: t2\n  left_field: t1_id\n"
        "  right_table: t1\n  right_field: id\n"
        "  evidence: mapper:T2Mapper.xml\n",
        encoding="utf-8",
    )
    (system / "db").mkdir(parents=True, exist_ok=True)
    (system / "db" / "db-catalog.yaml").write_text(
        "tables:\n  t1:\n    comment: 主表\n"
        "    columns:\n      id: {type: bigint, comment: 主键}\n"
        "  t2:\n    comment: 从表\n"
        "    columns:\n      t1_id: {type: bigint, comment: 主表}\n",
        encoding="utf-8",
    )
    (system / "db" / "db-profile.yaml").write_text(
        "tables:\n  t1:\n    rows_estimate: 42\n", encoding="utf-8"
    )
    return pages


def test_enrich_adds_relations_links_and_is_idempotent(tmp_path: Path) -> None:
    """enrich：表页关联节（双通道）+ 断链补链；第二遍零改动（幂等）。"""
    import importlib.util

    repo = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location(
        "wiki_enrich", repo / "scripts" / "wiki_enrich.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    pages = _make_corpus(tmp_path)
    # 指向 tmp 语料的同系统底稿（sys/）
    substrate = mod._Substrate(
        pages,
        substrate_dir=tmp_path / "sys" / "substrate",
        db_dir=tmp_path / "sys" / "db",
    )

    # 语义页引用 t1（表页存在）→ 补链
    semantic = (
        "---\ntype: caliber\ntitle: 口径\npage_key: cal-x\nstatus: published\n"
        'oid: 1\nscope:\n  databases: [db]\ncontract_version: "0.1"\n'
        "field_targets: [t1.id]\n---\n\n正文\n"
    )
    _write_page(pages / "calibers" / "cal-x.md", semantic)

    table_page = pages / "tables" / "t1.md"
    updated = mod.enrich_table_page(
        table_page.read_text(encoding="utf-8"), substrate, "t1"
    )
    assert "## 关联表" in updated
    assert "[[t2]]：t1.id → t2.t1_id（mapper:T2Mapper.xml，confirmed）" in updated
    assert "行数估计 42" in updated

    linked = mod.enrich_semantic_page(semantic, {"t1"})
    assert "相关：[[t1]]" in linked

    # 幂等：再跑一遍零变化
    again = mod.enrich_table_page(updated, substrate, "t1")
    assert again == updated
    assert "相关：[[t1]]" in mod.enrich_semantic_page(linked, {"t1"})


def test_normalize_scope_three_states(tmp_path: Path) -> None:
    """scope 三态归一：旧 ds_id/点式/平铺→块式 databases；字符串→coverage_note；新块式不动。"""
    import importlib.util

    repo = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location(
        "wiki_enrich", repo / "scripts" / "wiki_enrich.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    def _page(key: str, scope_line: str) -> str:
        return (
            "---\ntype: rule\ntitle: r\npage_key: "
            f"{key}\nstatus: published\noid: 1\n{scope_line}---\n正文\n"
        )

    legacy_block = _page("r1", "scope:\n  datasources: [15]\n")
    dotted = _page("r1b", "scope.datasources: [15]\n")
    flat = _page("r1c", "datasources: [15]\n")
    plain = _page("r2", "scope: 企业\n")
    block = _page("r3", "scope:\n  databases: [db]\n")
    for legacy in (legacy_block, dotted, flat):
        d = mod.normalize_scope(legacy, database="db")
        assert "scope:\n  databases: [db]" in d, legacy
        assert "datasources" not in d, legacy
    p = mod.normalize_scope(plain)
    assert "coverage_note: 企业" in p
    assert "databases" not in p  # 字符串 scope 不再补围栏
    assert mod.normalize_scope(block, database="db") == block


def test_enrich_semantic_page_requires_known_table() -> None:
    """引用的表无表页 → 不补链（防把 DTO/幻觉表写成锚链）。"""
    import importlib.util

    repo = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location(
        "wiki_enrich", repo / "scripts" / "wiki_enrich.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    semantic = (
        "---\ntype: concept\ntitle: c\npage_key: c1\nstatus: published\n"
        "maps_to: MessageContext.verifyCode = 'X'\n---\n正文\n"
    )
    assert mod.enrich_semantic_page(semantic, {"t1"}) == semantic


# ── A7：lint 新码 ───────────────────────────────────────────────────────────


def test_lint_semantic_page_unlinked_table_advisory() -> None:
    """语义页引用表未出链 → SEMANTIC_PAGE_UNLINKED_TABLE（advisory）。"""
    page = parse_page(
        "---\ntype: caliber\ntitle: c\npage_key: cal-y\nstatus: published\n"
        "field_targets: [t_a.id]\n---\n- [[other]]\n正文无表链\n"
    )
    findings = lint_page(page, known_keys={"other", "t_a"})
    assert "SEMANTIC_PAGE_UNLINKED_TABLE" in {f.code for f in findings}


def test_lint_semantic_page_unlinked_skips_non_table_refs_with_catalog() -> None:
    """带 catalog 时：DTO 类引用（MessageContext.verifyCode）不误报。"""
    page = parse_page(
        "---\ntype: concept\ntitle: c\npage_key: c2\nstatus: published\n"
        "maps_to: MessageContext.verifyCode = 'X'\n---\n- [[x]]\n正文\n"
    )
    findings = lint_page(
        page, known_keys={"x"}, catalog={"tables": {"t_a": {"fields": {}}}}
    )
    assert "SEMANTIC_PAGE_UNLINKED_TABLE" not in {f.code for f in findings}


def test_lint_table_page_no_relations_advisory() -> None:
    """表页无关联节 → TABLE_PAGE_NO_RELATIONS（孤表提示）。"""
    page = parse_page(
        "---\ntype: table\ntitle: t\npage_key: t_lone\nstatus: published\n"
        "---\n- [[x]]\n```ground:table\ntable: t_lone\nfields: []\n```\n"
    )
    findings = lint_page(page, known_keys={"x"})
    assert "TABLE_PAGE_NO_RELATIONS" in {f.code for f in findings}
