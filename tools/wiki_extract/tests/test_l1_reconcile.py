"""L1 aggregate / validate / emit — no live database."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from tools.wiki_extract.cli import main
from tools.wiki_extract.emit import _assert_isolated
from tools.wiki_extract.l1.loader import load_intermediate
from tools.wiki_extract.l1.reconcile import compile_l1
from tools.wiki_extract.l1.schema import IrError, normalize_document


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _catalog() -> dict:
    return {
        "database": "lowcode_pplatform",
        "tables": {
            "cust_company_info": {
                "columns": {
                    "id": {"type": "bigint"},
                    "code": {"type": "varchar"},
                    "name": {"type": "varchar"},
                    "enable": {"type": "varchar"},
                    "cust_build_status": {"type": "varchar"},
                    "cust_status": {"type": "varchar"},
                    "certification_no": {"type": "varchar"},
                    "cust_build_type": {"type": "varchar"},
                    "identify_style": {"type": "varchar"},
                }
            },
            "cust_project_rel": {
                "columns": {
                    "id": {"type": "bigint"},
                    "ref_cust_project_rel_cust_company_info": {"type": "varchar"},
                    "project_id": {"type": "varchar"},
                    "enable": {"type": "varchar"},
                }
            },
        },
    }


def _l0_table_page() -> str:
    return """---
type: table
title: 客户信息主表
page_key: cust_company_info
belong: tables
status: draft
anchors: [cust_company_info]
sources: ['database_schema:lowcode_pplatform.cust_company_info']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
---

# 客户信息主表

```ground:table
table: cust_company_info
database: lowcode_pplatform
description: 客户信息主表
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name]
clusters:
- key: common
  title: 通用
  include: always
fields:
- name: id
  data_type: number
  cluster: common
- name: code
  data_type: string
  cluster: common
- name: enable
  data_type: string
  cluster: common
- name: cust_build_status
  data_type: string
  dictionary: cust_company_info__cust_build_status
```

## 关联关系

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_project_rel.ref_cust_project_rel_cust_company_info
cardinality: one_to_many
trust: proposed
authenticity: unknown
evidence: database_profile:lowcode_pplatform.cust_company_info.id
```
"""


def _l0_rel_page() -> str:
    return """---
type: table
title: 客户项目关联表
page_key: cust_project_rel
belong: tables
status: draft
anchors: [cust_project_rel]
sources: ['database_schema:lowcode_pplatform.cust_project_rel']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
---

# 客户项目关联表

```ground:table
table: cust_project_rel
database: lowcode_pplatform
description: 客户项目关联表
inactive: false
primary_key: [id]
clusters:
- key: common
  title: 通用
  include: always
fields:
- name: id
  data_type: number
  cluster: common
- name: ref_cust_project_rel_cust_company_info
  data_type: string
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_project_rel.ref_cust_project_rel_cust_company_info
cardinality: one_to_many
trust: proposed
authenticity: unknown
```
"""


def _l0_dict_page() -> str:
    return """---
type: dict
title: cust_company_info.cust_build_status
page_key: cust_company_info__cust_build_status
belong: dicts
status: draft
anchors: [cust_company_info.cust_build_status]
sources: ['database_profile:cust_company_info.cust_build_status']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
---

# cust_company_info.cust_build_status

```ground:dict
dict: cust_company_info__cust_build_status
fields: [cust_company_info.cust_build_status]
values:
  BUILD_SUCCESS: {trust: proposed}
  INIT: {trust: proposed}
```
"""


def _seed_l0(root: Path) -> None:
    _write(root / "_raw" / "catalog.yaml", yaml.safe_dump(_catalog(), allow_unicode=True))
    _write(root / "tables" / "cust_company_info.md", _l0_table_page())
    _write(root / "tables" / "cust_project_rel.md", _l0_rel_page())
    _write(root / "dicts" / "cust_company_info__cust_build_status.md", _l0_dict_page())
    _write(root / "instance_index.yaml", "entries: []\n")


def _seed_ir(root: Path, *, hallucinate: bool = False) -> None:
    table = "ghost_table" if hallucinate else "cust_company_info"
    _write(
        root / "code" / "cust" / "table_enhancements.yaml",
        f"""kind: table_enhancements
domain: cust
tables:
  {table}:
    default_filter:
      predicate: "{table}.enable = 'Y'"
      evidence: code_path:CustCompanyIfoEnchanceService.java:653
    written_with_groups:
      - fields: [cust_build_status, cust_status]
        evidence: code_path:CustCompanyInfoDao.java:58
""",
    )
    _write(
        root / "code" / "cust" / "processes.yaml",
        """kind: processes
domain: cust
processes:
  - process_key: cust_company_info__cust_build_status
    table: cust_company_info
    field: cust_build_status
    description: 建档状态机
    stages:
      - stage: 提交
        transitions:
          - from: INIT
            event: 简易提交
            to: AWAIT_CUST_CONFIRM
            evidence: code_path:CustCompanyInfoApplication.java:2028
""",
    )
    _write(
        root / "code" / "cust" / "calibers_rules.yaml",
        """kind: calibers_rules
domain: cust
calibers:
  - caliber_key: effective_company
    predicate: "cust_company_info.enable = 'Y'"
    field_targets: [cust_company_info.enable]
    boundary: 启用企业
    evidence: code_path:CustCompanyIfoEnchanceService.java:647
rules:
  - rule_key: certification_no_unique
    field_targets: [cust_company_info.certification_no]
    impact: write_constraint
    content: 统码不可重复
    evidence: code_path:CustCompanyInfoApplication.java:5220
""",
    )
    _write(
        root / "code" / "cust" / "relations_dicts.yaml",
        """kind: relations_dicts
domain: cust
confirmed_relations:
  - left: cust_company_info.code
    right: cust_project_rel.ref_cust_project_rel_cust_company_info
    type: EQUI_JOIN
    cardinality: one_to_many
    join_role: identity
    evidence: code_path:CustCompanyQueryMapper.xml:97
dict_labels:
  cust_company_info__cust_build_status:
    table: cust_company_info
    column: cust_build_status
    values:
      INIT: { label: 初始化, evidence: code_path:CustBuildStatusEnum.java:14 }
      BUILD_SUCCESS: { label: 认证成功, evidence: code_path:CustBuildStatusEnum.java:17 }
""",
    )
    _write(
        root / "code" / "cust" / "scenarios.yaml",
        """kind: scenarios
domain: cust
scenarios:
  - scenario_key: company_build
    hubs:
      - table: cust_company_info
        role: master
""",
    )
    _write(
        root / "docs" / "cust_management_concepts.yaml",
        """kind: concepts
domain: cust
doc_source: example.md
concepts:
  - concept_key: platform_entry
    title: 平台录入
    maps_to: cust_company_info.cust_build_type
    field_targets: [cust_company_info.cust_build_type]
    also_confused_with: [identify_style]
    adjudication: boundary
    explanation: 建档录入方式，不是认证渠道。
    evidence: document_claim:example.md#1
""",
    )
    _write(
        root / "docs" / "platform_metrics.yaml",
        """kind: metrics
domain: cust
metrics:
  - metric_key: effective_company_count
    caliber: effective_company
    grain_table: cust_company_info
    aggregation: count_distinct
    field: cust_company_info.id
    evidence: code_path:CustCompanyIfoEnchanceService.java:647
""",
    )
    _write(
        root / "docs" / "platform_display.yaml",
        """kind: display
items:
  - title: 版本演进
    page_key: platform_version_history
    content: 排期不进召回
""",
    )


def _seed_code(root: Path) -> None:
    files = {
        "CustCompanyIfoEnchanceService.java": "\n" * 660,
        "CustCompanyInfoDao.java": "\n" * 70,
        "CustCompanyInfoApplication.java": "\n" * 5230,
        "CustCompanyQueryMapper.xml": "\n" * 100,
        "CustBuildStatusEnum.java": "\n" * 20,
    }
    for name, body in files.items():
        _write(root / "src" / name, body)


def test_schema_rejects_unknown_kind(tmp_path: Path) -> None:
    path = tmp_path / "weird.yaml"
    path.write_text("kind: nope\n", encoding="utf-8")
    with pytest.raises(IrError):
        normalize_document(path, {"kind": "nope"})


def test_hallucinated_table_is_review_not_confirmed(tmp_path: Path) -> None:
    l0 = tmp_path / "l0"
    ir = tmp_path / "ir"
    out = tmp_path / "v3"
    code = tmp_path / "code"
    _seed_l0(l0)
    _seed_ir(ir, hallucinate=True)
    _seed_code(code)
    stats = compile_l1(
        l0_dir=l0,
        intermediate_dir=ir,
        out_dir=out,
        code_root=code,
    )
    assert stats["errors"] >= 1
    reviews = yaml.safe_load((out / ".runs" / "l1" / "reviews.yaml").read_text(encoding="utf-8"))
    kinds = {item["kind"] for item in reviews["items"]}
    assert "TABLE_NOT_IN_DB" in kinds
    table_md = (out / "tables" / "cust_company_info.md").read_text(encoding="utf-8")
    assert "ghost_table" not in table_md
    assert "default_filter" not in table_md


def test_l1_compile_upgrades_and_emits_nine_types(tmp_path: Path) -> None:
    l0 = tmp_path / "l0"
    ir = tmp_path / "ir"
    out = tmp_path / "v3"
    code = tmp_path / "code"
    _seed_l0(l0)
    _seed_ir(ir)
    _seed_code(code)
    stats = compile_l1(
        l0_dir=l0,
        intermediate_dir=ir,
        out_dir=out,
        code_root=code,
    )
    assert stats["errors"] == 0
    assert stats["concepts"] >= 1
    assert stats["processes"] == 1
    assert stats["calibers"] == 1
    assert stats["metrics"] == 1
    assert stats["rules"] == 1
    assert stats["scenarios"] >= 1
    rel_page = (out / "tables" / "cust_project_rel.md").read_text(encoding="utf-8")
    assert "cust_company_info.code" in rel_page
    assert "trust: confirmed" in rel_page
    assert "trust: disputed" in rel_page
    assert "cust_company_info.id" in rel_page
    reviews = yaml.safe_load((out / ".runs" / "l1" / "reviews.yaml").read_text(encoding="utf-8"))
    kinds = {item["kind"] for item in reviews["items"]}
    assert "JOIN_CONFLICT" in kinds
    assert "sides:" in rel_page
    dict_page = (out / "dicts" / "cust_company_info__cust_build_status.md").read_text(
        encoding="utf-8"
    )
    assert "label: 初始化" in dict_page
    assert "trust: confirmed" in dict_page
    table_page = (out / "tables" / "cust_company_info.md").read_text(encoding="utf-8")
    assert "default_filter:" in table_page
    assert "written_with:" in table_page
    assert "clusters:" not in table_page
    assert "## 字段簇" not in table_page
    assert "cluster:" not in table_page
    assert "data_type:" not in table_page
    assert "dictionary:" not in table_page
    assert "  type: string" in table_page
    assert "dict: [BUILD_SUCCESS, INIT]" in table_page
    assert "label: [认证成功, 初始化]" in table_page
    assert "[[dicts/cust_company_info__cust_build_status]]" in table_page
    summary = (out / "concepts" / "catalog_summary.md").read_text(encoding="utf-8")
    assert "- cust_company_info:" in summary
    assert "page_key: catalog_summary" in summary
    assert "主要字段：" not in summary
    company_line = next(
        line for line in summary.splitlines() if "- cust_company_info:" in line
    )
    assert company_line.startswith("- cust_company_info:")
    assert "客户企业信息主表" in company_line
    assert len(company_line) < 200
    index = (out / "_index.md").read_text(encoding="utf-8")
    assert "[[concepts/catalog_summary]]" in index
    assert (out / "processes" / "cust_company_info__cust_build_status.md").exists()
    assert (out / "concepts" / "platform_entry.md").exists()
    assert (out / "concepts" / "platform_version_history.md").exists()
    concept = (out / "concepts" / "platform_entry.md").read_text(encoding="utf-8")
    assert "[[tables/cust_company_info]]" in concept
    assert "[[concepts/identify_style]]" not in concept
    process = (out / "processes" / "cust_company_info__cust_build_status.md").read_text(
        encoding="utf-8"
    )
    assert "[[tables/cust_company_info]]" in process
    assert "[[dicts/cust_company_info__cust_build_status]]" in process
    caliber = (out / "calibers" / "effective_company.md").read_text(encoding="utf-8")
    assert "[[tables/cust_company_info]]" in caliber
    rule = (out / "rules" / "certification_no_unique.md").read_text(encoding="utf-8")
    assert "[[tables/cust_company_info]]" in rule
    scenario = (out / "scenarios" / "company_build.md").read_text(encoding="utf-8")
    assert "[[tables/cust_company_info]]" in scenario
    metric = (out / "metrics" / "effective_company_count.md").read_text(encoding="utf-8")
    assert "[[tables/cust_company_info]]" in metric
    assert "[[calibers/effective_company]]" in metric
    display = (out / "concepts" / "platform_version_history.md").read_text(encoding="utf-8")
    assert "recall: false" in display
    assert "[[concepts/catalog_summary]]" in display
    assert "status: draft" in (out / "calibers" / "effective_company.md").read_text(
        encoding="utf-8"
    )
    assert (out / "_raw" / "l1_intermediate" / "code" / "cust" / "processes.yaml").exists()


def test_live_ir_cust_walk_keys() -> None:
    bundle = load_intermediate(Path("docs/wiki/v2/_raw/l1_intermediate"))
    rule_keys = {item["rule_key"] for item in bundle.rules}
    assert "unique_admin_per_company_role" in rule_keys
    assert "simple_auth_no_ca" in rule_keys
    assert "freeze_cascade" in rule_keys
    assert "change_requires_onway_check" in rule_keys
    caliber_keys = {item["caliber_key"] for item in bundle.calibers}
    assert "company_admin" in caliber_keys
    process_keys = {item["process_key"] for item in bundle.processes}
    assert "cust_person_info__status" in process_keys
    assert "cust_invite_info__progress" in process_keys
    rights = {item["right"] for item in bundle.relations}
    assert "cust_customized_product.cust_id" in rights
    assert "cust_shareholder_info.ref_cust_company_info" in rights
    assert "cust_invite_info.invite_cust_id" in rights
    assert bundle.dict_labels["cust_person_info__user_type"]["values"]["accountAdmin"]["label"] == "管理员"


def test_l1_coverage_lists_unenhanced_tables(tmp_path: Path) -> None:
    l0 = tmp_path / "l0"
    ir = l0 / "_raw" / "l1_intermediate"
    catalog = {
        "tables": {
            "cust_company_info": {"columns": {"id": {}, "code": {}}},
            "cust_orphan_sat": {"columns": {"id": {}, "cust_id": {}}},
        }
    }
    _write(l0 / "_raw" / "catalog.yaml", yaml.safe_dump(catalog, allow_unicode=True))
    _write(
        ir / "code" / "cust" / "table_enhancements.yaml",
        "kind: table_enhancements\ndomain: cust\ntables:\n  cust_company_info: {}\n",
    )
    from tools.wiki_extract.l1.coverage import coverage_report

    report = coverage_report(l0_dir=l0, prefix="cust")
    assert report["missing_tables"] == ["cust_orphan_sat"]
    assert "cust_company_info" in report["enhanced_tables"]


def test_join_conflict_marks_id_edge_disputed(tmp_path: Path) -> None:
    l0 = tmp_path / "l0"
    ir = tmp_path / "ir"
    out = tmp_path / "v3"
    code = tmp_path / "code"
    _seed_l0(l0)
    _seed_ir(ir)
    _seed_code(code)
    compile_l1(l0_dir=l0, intermediate_dir=ir, out_dir=out, code_root=code)
    rel_page = (out / "tables" / "cust_project_rel.md").read_text(encoding="utf-8")
    assert "disputed — 与已确认边冲突" in rel_page
    assert "left: cust_company_info.id" in rel_page
    assert "left: cust_company_info.code" in rel_page
    reviews = yaml.safe_load((out / ".runs" / "l1" / "reviews.yaml").read_text(encoding="utf-8"))
    conflicts = [item for item in reviews["items"] if item["kind"] == "JOIN_CONFLICT"]
    assert conflicts
    assert "cust_company_info.id=" in conflicts[0]["target"]


def test_cli_l1(tmp_path: Path) -> None:
    l0 = tmp_path / "l0"
    ir = tmp_path / "ir"
    out = tmp_path / "v3"
    _seed_l0(l0)
    _seed_ir(ir)
    rc = main(
        [
            "l1",
            "--l0",
            str(l0),
            "--intermediate",
            str(ir),
            "--out",
            str(out),
            "--skip-code-check",
        ]
    )
    assert rc == 0
    assert (out / "rules" / "certification_no_unique.md").exists()


def test_refuses_wiki_pages_dir(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        _assert_isolated(tmp_path / "wiki-pages-v3")


def test_load_rejects_yml_extension(tmp_path: Path) -> None:
    _write(tmp_path / "foo.yml", "kind: display\nitems:\n  - title: x\n")
    with pytest.raises(IrError):
        load_intermediate(tmp_path)
