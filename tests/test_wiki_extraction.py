"""Extraction-layer regression tests (plan review fixes).

覆盖审查报告点名的三个零覆盖面：
1. merge_same_key_page —— G1"丢全量字段"回归的防线；
2. reconcile_page —— 门禁语义（TABLE_NOT_IN_DB / FIELD_NOT_IN_DB / 回证行号）；
3. run_unit 的丢块规则（anchor 丢块 / 整页拒绝 / 重复块删除）；
4. filters.CodeIgnore / ReqdocFilter —— gitignore 语义（! 反选最后匹配生效）。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.knowledge.wiki.contract import parse_page  # noqa: E402
from apps.knowledge.wiki.filters import CodeIgnore, ReqdocFilter  # noqa: E402
from apps.knowledge.wiki.ingest import reconcile_page  # noqa: E402
from apps.knowledge.wiki.pipeline import (  # noqa: E402
    _drop_anchored_blocks,
    _drop_duplicate_blocks,
    merge_same_key_page,
)

# ── merge_same_key_page：基线字段保全 + 语义 desc 并入 ────────────────────────


_BASELINE = """---
type: table
title: 客户信息主表
page_key: cust_company_info
status: draft
anchors: [cust_company_info]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml"]
contract_version: "0.1"
---

# 客户信息主表

```ground:table
table: cust_company_info
database: lowcode_pplatform
desc: 客户信息主表
inactive: false
fields:
  - name: id
    type: number
    desc: 表主键
  - name: cust_build_status
    type: string
    dict: cust_build_status
  - name: cust_status
    type: string
```
"""

_SEMANTIC = """---
type: table
title: 客户信息主表
page_key: cust_company_info
domain: 企业建档
status: draft
aliases: [客户主档]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["semantic"]
contract_version: "0.1"
---

# 客户信息主表

**业务定位**：企业主档，含认证与生命周期状态。

```ground:table
table: cust_company_info
fields:
  - name: cust_build_status
    meaning: 认证审批进度
  - name: ghost_field
    meaning: 不存在的字段
```
"""


def test_merge_preserves_baseline_fields_and_merges_desc() -> None:
    merged = merge_same_key_page(_BASELINE, _SEMANTIC)
    page = parse_page(merged, page_key="cust_company_info")
    block = next(b for b in page.ground_blocks if b.kind == "table")
    fields = {f["name"]: f for f in block.data["fields"]}
    # 基线 3 字段全量保留（G1 防线）
    assert set(fields) >= {"id", "cust_build_status", "cust_status"}
    # 语义 desc 并入（meaning → desc 归一）
    assert fields["cust_build_status"].get("desc") == "认证审批进度"
    # 基线已有 desc 不被覆盖
    assert fields["id"]["desc"] == "表主键"
    # 语义独有字段保留（对账层负责 FIELD_NOT_IN_DB）
    assert "ghost_field" in fields
    # 散文保留语义页业务叙述 + status 归 draft
    assert "业务定位" in page.body
    assert page.status == "draft"
    # 磁盘形态：紧凑键（type/desc/dict），无 data_type/description 残留
    assert "data_type:" not in merged and "description:" not in merged
    assert "    type: string" in merged


# ── reconcile_page：db 对账 + 回证行号 ────────────────────────────────────────


@pytest.fixture()
def db_env(tmp_path: Path) -> tuple[Path, Path, Path]:
    db_dir = tmp_path / "db"
    db_dir.mkdir()
    (db_dir / "db-catalog.yaml").write_text(
        yaml.safe_dump(
            {"tables": {"cust_company_info": {"columns": {"id": {}, "cust_status": {}}}}}
        )
    )
    repo = tmp_path / "repo"
    src = repo / "svc" / "Svc.java"
    src.parent.mkdir(parents=True)
    src.write_text("\n" * 30 + "checkBefore();\n")
    return tmp_path, db_dir, repo


def test_reconcile_table_and_field_not_in_db(db_env: tuple[Path, Path, Path]) -> None:
    _tmp, db_dir, repo = db_env
    page = """---
type: table
title: t
page_key: ghost
status: draft
---
```ground:table
table: ghost_table
fields:
  - name: nope
```
"""
    findings = reconcile_page(page, db_dir=db_dir, repo=repo)
    codes = {f["code"] for f in findings}
    assert codes == {"TABLE_NOT_IN_DB"}
    assert findings[0]["anchor"] == "table:ghost_table"


def test_reconcile_field_not_in_db_with_anchor(db_env: tuple[Path, Path, Path]) -> None:
    _tmp, db_dir, repo = db_env
    page = """---
type: table
title: t
page_key: cust_company_info
status: draft
---
```ground:table
table: cust_company_info
fields:
  - name: not_a_column
```
"""
    findings = reconcile_page(page, db_dir=db_dir, repo=repo)
    assert [f["code"] for f in findings] == ["FIELD_NOT_IN_DB"]
    assert findings[0]["anchor"] == "table:cust_company_info"


def test_reconcile_evidence_line_validation(db_env: tuple[Path, Path, Path]) -> None:
    _tmp, db_dir, repo = db_env
    good = """---
type: rule
title: r
page_key: r1
status: draft
---
```ground:rule
rule: 合法回证
evidence: code_path:svc/Svc.java:31
```
"""
    bad = good.replace("svc/Svc.java:31", "svc/Missing.java:1")
    ok = reconcile_page(good, db_dir=db_dir, repo=repo)
    assert ok == []
    bad_findings = reconcile_page(bad, db_dir=db_dir, repo=repo)
    assert [f["code"] for f in bad_findings] == ["EVIDENCE_FILE_MISSING"]
    assert bad_findings[0]["anchor"] == "rule:合法回证"


# ── 丢块规则：anchor 丢块 / 重复块删除 ────────────────────────────────────────


def test_drop_anchored_blocks_removes_only_matching_fence() -> None:
    content = """```ground:table
table: ghost_table
fields:
  - name: x
```

散文保留。

```ground:table
table: cust_company_info
fields:
  - name: id
```
"""
    cleaned = _drop_anchored_blocks(content, [{"anchor": "table:ghost_table"}])
    assert "ghost_table" not in cleaned
    assert "cust_company_info" in cleaned
    assert "散文保留" in cleaned


def test_drop_duplicate_blocks_keeps_first() -> None:
    content = """```ground:rule
rule: 同名规则
content: 第一处
```
```ground:rule
rule: 同名规则
content: 第二处
```
"""
    cleaned = _drop_duplicate_blocks(content)
    assert cleaned.count("ground:rule") == 1
    assert "第一处" in cleaned and "第二处" not in cleaned


# ── filters：gitignore 语义 ───────────────────────────────────────────────────


def test_code_ignore_negation_last_match_wins() -> None:
    ci = CodeIgnore(["*/dto/*", "!*/dto/*Invite*.java"])
    assert not ci.should_scan("app/src/main/java/x/dto/FooDTO.java")
    assert ci.should_scan("app/src/main/java/x/dto/InviteReq.java")
    assert ci.should_scan("app/src/main/java/x/service/XService.java")


def test_code_ignore_default_excludes() -> None:
    ci = CodeIgnore([])
    assert not ci.should_scan("module/target/classes/A.class")
    assert not ci.should_scan("module/src/test/java/ATest.java")
    assert ci.should_scan("module/src/main/java/A.java")


def test_reqdoc_filter_include_only_default(tmp_path: Path) -> None:
    f = ReqdocFilter.load(tmp_path / "missing.yaml")
    assert f.should_use("concepts/认证方式.md")
    assert f.should_use("entities/cust_project_rel表.md")
    assert not f.should_use("entities/张彬伟.md")  # 人物页隔离
    assert not f.should_use("queries/open-q.md")
