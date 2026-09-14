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
from apps.knowledge.wiki.ingest import reconcile_page, sanitize_llm_page  # noqa: E402
from apps.knowledge.wiki.pipeline import (  # noqa: E402
    _drop_anchored_blocks,
    _drop_duplicate_blocks,
    merge_enum_page,
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


_SEMANTIC_COLUMNS = """---
type: table
title: 客户信息主表
page_key: table.cust_company_info
status: draft
oid: 1
contract_version: "0.1"
---

业务叙述保留。

```ground:table
table: cust_company_info
columns:
  - field: cust_build_status
    meaning: 认证审批进度
```
"""


_SEMANTIC_NO_GROUND = """---
type: table
title: 客户信息主表
page_key: tables/cust_company_info
status: draft
oid: 1
contract_version: "0.1"
---

只有散文，没有 ground 块。
"""


def test_merge_columns_dialect_keeps_baseline_fields() -> None:
    merged = merge_same_key_page(_BASELINE, _SEMANTIC_COLUMNS)
    page = parse_page(merged, page_key="cust_company_info", belong="tables")
    block = next(b for b in page.ground_blocks if b.kind == "table")
    from apps.knowledge.wiki.contract import compact_block

    data = compact_block(block.data)
    fields = {f["name"]: f for f in data["fields"]}
    assert set(fields) >= {"id", "cust_build_status", "cust_status"}
    assert fields["cust_build_status"].get("desc") == "认证审批进度"
    assert "columns:" not in merged
    assert page.page_key == "cust_company_info"
    assert "业务叙述保留" in page.body


def test_merge_missing_ground_keeps_baseline_table_block() -> None:
    merged = merge_same_key_page(_BASELINE, _SEMANTIC_NO_GROUND)
    page = parse_page(merged, page_key="cust_company_info", belong="tables")
    block = next(b for b in page.ground_blocks if b.kind == "table")
    names = [f["name"] for f in block.data["fields"]]
    assert names == ["id", "cust_build_status", "cust_status"]
    assert "只有散文" in page.body


def test_compact_block_maps_columns_to_fields() -> None:
    from apps.knowledge.wiki.contract import compact_block

    data = compact_block(
        {
            "table": "t",
            "columns": [{"field": "id", "meaning": "主键", "data_type": "number"}],
        }
    )
    assert "columns" not in data
    assert data["fields"][0]["name"] == "id"
    assert data["fields"][0]["desc"] == "主键"
    assert data["fields"][0]["type"] == "number"


def test_stamp_frontmatter_strips_prefix_and_backfills_targets() -> None:
    from apps.knowledge.wiki.contract import stamp_frontmatter

    raw = """---
type: concept
title: 录入方式
page_key: concepts/build_type
status: draft
maps_to: cust_company_info.cust_build_type
contract_version: "0.1"
---

正文
"""
    stamped = stamp_frontmatter(raw, stem="build_type", belong="concepts")
    page = parse_page(stamped, page_key="build_type", belong="concepts")
    assert page.page_key == "build_type"
    assert page.belong == "concepts"
    assert page.field_targets == ("cust_company_info.cust_build_type",)


# ── reconcile_page：db 对账 + 回证行号 ────────────────────────────────────────


@pytest.fixture()
def db_env(tmp_path: Path) -> tuple[Path, Path, Path]:
    db_dir = tmp_path / "db"
    db_dir.mkdir()
    (db_dir / "db-catalog.yaml").write_text(
        yaml.safe_dump(
            {
                "tables": {
                    "cust_company_info": {"columns": {"id": {}, "cust_status": {}}}
                }
            }
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


def test_reconcile_enum_list_values_does_not_crash(db_env: tuple[Path, Path, Path]) -> None:
    from apps.knowledge.wiki.contract import compact_block

    _tmp, db_dir, repo = db_env
    page = """---
type: enum
title: cust_status
page_key: cust_status
status: draft
---
```ground:enum
enum: cust_status
fields: [cust_company_info.cust_status]
values:
  - value: EFFECT
    label: 已生效
  - value: ADD
    label: 未生效
```
"""
    findings = reconcile_page(page, db_dir=db_dir, repo=repo)
    assert all(f.get("code") != "PAGE_CONTRACT_FAILED" for f in findings)
    data = compact_block({"values": [{"value": "EFFECT", "label": "已生效"}]})
    assert "EFFECT" in data["values"]


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


def _load_skill_script(name: str) -> object:
    import importlib.util

    path = _ROOT / ".cursor" / "skills" / "knowledge-extraction" / "scripts" / name
    spec = importlib.util.spec_from_file_location(name.replace(".py", ""), path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_enum_stored_as_name_vs_dictkey(tmp_path: Path) -> None:
    mod = _load_skill_script("extract-enums.py")
    src = tmp_path / "src" / "main" / "java"
    src.mkdir(parents=True)
    (src / "AccountTypeEnum.java").write_text(
        """
public enum AccountTypeEnum {
    BANK("1", "银行"),
    RECEIVED("received", "收款");
}
"""
    )
    (src / "Use.java").write_text(
        """
class Use {
  void w() {
    a.setAccountType(AccountTypeEnum.BANK.name());
    a.setAccountType(AccountTypeEnum.BANK.name());
    b.setKind(AccountTypeEnum.RECEIVED.getDictKey());
  }
}
"""
    )
    enums, _bindings = mod.extract(tmp_path)
    mod.attach_accessors(tmp_path, enums, [])
    by_name = {v["java_name"]: v for v in enums[0]["values"]}
    assert by_name["BANK"]["value"] == "1"
    assert by_name["BANK"]["stored_as"] == "name"
    assert by_name["RECEIVED"]["stored_as"] == "dictKey"


def test_same_property_copy_emits_shared_key(tmp_path: Path) -> None:
    mod = _load_skill_script("extract-relationships.py")
    pkg = tmp_path / "src" / "main" / "java"
    pkg.mkdir(parents=True)
    (pkg / "CustCompanyInfoDO.java").write_text(
        """
@TableName("cust_company_info")
class CustCompanyInfoDO {
  private String certificationNo;
}
"""
    )
    (pkg / "CustPersonInfoDO.java").write_text(
        """
@TableName("cust_person_info")
class CustPersonInfoDO {
  private String certificationNo;
}
"""
    )
    (pkg / "Svc.java").write_text(
        """
class Svc {
  void copy(CustPersonInfoDO person, CustCompanyInfoDO company) {
    person.setCertificationNo(company.getCertificationNo());
  }
}
"""
    )
    do_table = mod.do_index(tmp_path)
    rels = mod.extract_same_property(tmp_path, do_table)
    assert any(
        r["left_field"] == "certification_no"
        and r["right_field"] == "certification_no"
        and r["kind"] == "SHARED_KEY"
        for r in rels
    )


def test_yaml_enum_key_preserves_leading_zero() -> None:
    from apps.knowledge.wiki.baseline import _yaml_enum_key

    dumped = "values:\n  " + _yaml_enum_key("01") + ":\n    label: 线上\n"
    loaded = yaml.safe_load(dumped)
    assert list(loaded["values"].keys()) == ["01"]


def test_constant_interface_and_constants_plural(tmp_path: Path) -> None:
    mod = _load_skill_script("extract-enums.py")
    pkg = tmp_path / "src" / "main" / "java" / "constant" / "cust"
    pkg.mkdir(parents=True)
    (pkg / "IdentifyTypeConstant.java").write_text(
        """
public interface IdentifyTypeConstant {
	/** 邀请认证-客户录入 */
	String INVITE = "INVITE";
	/** 自主认证 */
	String SELF = "SELF";
}
"""
    )
    (pkg / "CustUpdateItemCodeConstants.java").write_text(
        """
public interface CustUpdateItemCodeConstants {
	/*** 企业信息变更 **/
	String UN0001="UN0001";
	String UN0002="UN0002";
}
"""
    )
    (pkg / "Use.java").write_text(
        """
class Use {
  void w(CustCompanyInfoDO doo) {
    doo.setIdentifyStyle(IdentifyTypeConstant.INVITE);
    doo.setItemCode(CustUpdateItemCodeConstants.UN0001);
  }
}
"""
    )
    constants = mod.constant_enums(tmp_path)
    by_name = {c["enum"]: c for c in constants}
    assert "IdentifyTypeConstant" in by_name
    assert by_name["IdentifyTypeConstant"]["kind"] == "interface"
    assert {v["value"] for v in by_name["IdentifyTypeConstant"]["values"]} == {
        "INVITE",
        "SELF",
    }
    assert "CustUpdateItemCodeConstants" in by_name
    unlabeled = [
        v
        for v in by_name["CustUpdateItemCodeConstants"]["values"]
        if v.get("unlabeled")
    ]
    assert unlabeled and unlabeled[0]["value"] == "UN0002"
    bindings = mod.setter_bindings(tmp_path)
    assert "IdentifyTypeConstant" in bindings.get("identify_style", [])
    assert "CustUpdateItemCodeConstants" in bindings.get("item_code", [])


def test_merge_enum_keeps_baseline_keys_and_llm_notes() -> None:
    baseline = """---
type: enum
title: account_type
page_key: account_type
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
contract_version: "0.1"
---

# account_type

```ground:enum
enum: account_type
fields: [cust_account_info.account_type]
values:
  "1":
    label: "银行"
    java_name: "BANK"
  "BANK":
    label: "银行"
    stored_as: name
```
"""
    semantic = """---
type: enum
title: 账户类型
page_key: account_type
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
contract_version: "0.1"
---

# 账户类型

写值点使用 AccountTypeEnum.BANK.name()。

```ground:enum
enum: account_type
fields: [cust_account_info.account_type]
values:
  "1":
    label: "银行账户"
    stored_as: dictKey
    note: "setter 使用 getDictKey 的少数路径"
  "BANK":
    label: "银行"
    stored_as: name
    note: "主路径 .name() 落库"
```
"""
    merged = merge_enum_page(baseline, semantic)
    page = parse_page(merged, page_key="account_type")
    block = next(b for b in page.ground_blocks if b.kind == "enum")
    values = {str(k): v for k, v in (block.data.get("values") or {}).items()}
    assert "1" in values and "BANK" in values
    assert values["1"]["label"] == "银行"
    assert "银行账户" in (values["1"].get("aliases") or [])
    assert "name()" in str(values["BANK"].get("note") or "")
    assert "写值点使用" in merged


def test_block_substrate_includes_constant_enums(tmp_path: Path) -> None:
    from apps.knowledge.wiki.ingest import _block_substrate

    sub = tmp_path / "sub"
    db = tmp_path / "db"
    sub.mkdir()
    db.mkdir()
    (db / "db-catalog.yaml").write_text(
        "tables:\n  cust_company_info:\n    columns:\n      identify_style: {}\n      cust_status: {}\n"
    )
    (sub / "extract-enums.yaml").write_text(
        """
enums: []
constant_enums:
  - enum: IdentifyTypeConstant
    kind: interface
    field: identify_style
    values:
      - value: INVITE
        display: 邀请认证
table_bindings:
  cust_company_info.identify_style:
    - enum: IdentifyTypeConstant
"""
    )
    (sub / "extract-relationships.yaml").write_text(
        """
relationships:
  - left_table: cust_company_info
    left_field: company_type
    right_table: cust_project_rel
    right_field: company_type
    kind: SHARED_KEY
"""
    )
    text = _block_substrate(sub, db, ["cust_company_info"])
    assert "IdentifyTypeConstant" in text
    assert "constant_enums" in text or "枚举/常量基线" in text
    assert "SHARED_KEY" in text
    assert "可推翻" in text


def test_merge_keeps_resident_domain_against_later_topic() -> None:
    baseline = _BASELINE.replace("status: draft", "domain: 企业建档与认证状态机\nstatus: draft")
    later = _SEMANTIC.replace("domain: 企业建档", "domain: 平台内部服务对接")
    merged = merge_same_key_page(baseline, later)
    assert "domain: 企业建档与认证状态机" in merged
    assert "平台内部服务对接" not in merged.split("\n---\n")[0]


def test_merge_enum_ignores_illegal_stored_as() -> None:
    baseline = """---
type: enum
title: account_type
page_key: account_type
domain: 基线
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
contract_version: "0.1"
---

```ground:enum
enum: account_type
fields: [cust_account_info.account_type]
values:
  "1":
    label: "银行"
    java_name: "BANK"
    stored_as: dictKey
  "BANK":
    label: "银行"
    stored_as: name
```
"""
    semantic = """---
type: enum
title: 账户类型
page_key: account_type
domain: 企业银行账户
status: draft
oid: 1
scope:
  databases:
    - customer_management
contract_version: "0.1"
---

散文。

```ground:enum
enum: account_type
fields: [cust_account_info.account_type]
values:
  "1":
    label: "银行"
    stored_as: dictParam 数字形态
    note: "getDictParam=1 与 name()=BANK"
  "BANK":
    label: "银行"
    stored_as: name
    note: "DB 48428 条为 BANK"
```
"""
    merged = merge_enum_page(baseline, semantic)
    assert "dictParam" not in merged
    assert "getDictParam=1" not in merged
    assert "stored_as: name" in merged
    assert "databases: [lowcode_pplatform]" in merged.split("\n---\n")[0]
    assert "DB 48428" in merged


def test_setter_skips_non_do_receiver(tmp_path: Path) -> None:
    mod = _load_skill_script("extract-enums.py")
    pkg = tmp_path / "src" / "main" / "java"
    pkg.mkdir(parents=True)
    (pkg / "CustCompanyInfoDO.java").write_text(
        """
@TableName("cust_company_info")
class CustCompanyInfoDO {
  private String signMode;
}
"""
    )
    (pkg / "Use.java").write_text(
        """
class Use {
  void w(CustCompanyInfoDO company) {
    BaseContractDataSource ds = new BaseContractDataSource();
    ds.setSignMode(SignModeEnum.ON_LINE);
  }
}
"""
    )
    bound = mod.setter_table_bindings(tmp_path)
    assert "cust_company_info.sign_mode" not in bound


def test_sanitize_missing_opening_frontmatter_fence() -> None:
    raw = """type: table
title: 客户角色表
page_key: cust_role_info
status: draft
oid: 1
contract_version: "0.1"
---

# 客户角色表
"""
    fixed = sanitize_llm_page(raw)
    assert fixed.startswith("---\n")
    page = parse_page(fixed, page_key="cust_role_info", belong="tables")
    assert page.title == "客户角色表"
    assert page.page_key == "cust_role_info"


def test_extract_lowercase_enum_constants(tmp_path: Path) -> None:
    mod = _load_skill_script("extract-enums.py")
    src = tmp_path / "src" / "main" / "java"
    src.mkdir(parents=True)
    (src / "UserTypeEnum.java").write_text(
        """
public enum UserTypeEnum {
    admin("accountAdmin", "管理员"),
    operator("accountNormal", "经办人"),
    guest("accountGuest", "游客");

    public static UserTypeEnum of(String dictKey) {
        return null;
    }
}
"""
    )
    (src / "Use.java").write_text(
        """
class Use {
  void w() {
    p.setUserType(UserTypeEnum.admin.getDictKey());
    p.setUserType(UserTypeEnum.operator.getDictKey());
  }
}
"""
    )
    enums, _bindings = mod.extract(tmp_path)
    mod.attach_accessors(tmp_path, enums, [])
    by_java = {v["java_name"]: v for v in enums[0]["values"]}
    assert by_java["admin"]["value"] == "accountAdmin"
    assert by_java["operator"]["value"] == "accountNormal"
    assert by_java["admin"]["stored_as"] == "dictKey"


def test_merge_enum_dedupes_notes_and_drops_undeclared_name_key() -> None:
    baseline = """---
type: enum
title: sign_mode
page_key: sign_mode
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
contract_version: "0.1"
---

```ground:enum
enum: sign_mode
fields: [cust_company_info.sign_mode]
values:
  "01":
    label: "线上"
    java_name: "ON_LINE"
  "ONLINE":
    label: "线上"
    java_name: "ON_LINE"
    stored_as: name
    note: "DB 实测键 ONLINE；与 Java ON_LINE（dictKey 01）同常量，该列主路径不落 dictKey"
```
"""
    semantic = """---
type: enum
title: sign_mode
page_key: sign_mode
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
contract_version: "0.1"
---

```ground:enum
enum: sign_mode
fields: [cust_company_info.sign_mode]
values:
  "ONLINE":
    label: "线上"
    stored_as: name
    note: "DB 实测键 ONLINE；与 Java ON_LINE（dictKey 01）同常量，该列主路径不落 dictKey；db 分布存在但代码枚举未声明（REVIEW）；DB 实测键 ONLINE；与 Java ON_LINE（dictKey 01）同常量，该列主路径不落 dictKey"
    aliases: ["ONLINE"]
```
"""
    merged = merge_enum_page(baseline, semantic)
    assert merged.count("DB 实测键 ONLINE") == 1
    assert "代码枚举未声明" not in merged
    assert 'aliases: ["ONLINE"]' not in merged


def test_repair_rewrites_java_name_predicates(tmp_path: Path) -> None:
    from apps.knowledge.wiki.repair import (
        _dictkey_rewrites,
        _rewrite_java_name_predicates,
    )

    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "extract-enums.yaml").write_text(
        """
enums:
  - enum: UserTypeEnum
    values:
      - value: accountAdmin
        java_name: admin
      - value: accountNormal
        java_name: operator
table_bindings:
  cust_person_info.user_type:
    - enum: UserTypeEnum
"""
    )
    pages = tmp_path / "pages"
    (pages / "calibers").mkdir(parents=True)
    (pages / "tables").mkdir()
    (pages / "calibers" / "admin_user.md").write_text(
        "predicate: \"cust_person_info.user_type = 'admin'\"\n"
    )
    (pages / "tables" / "cust_user_rel.md").write_text(
        "user_type='admin' 是旧表真值\n"
    )
    rewrites = _dictkey_rewrites(sub)
    changed = _rewrite_java_name_predicates(pages, rewrites)
    assert changed == 1
    assert "accountAdmin" in (pages / "calibers" / "admin_user.md").read_text()
    assert "user_type='admin'" in (pages / "tables" / "cust_user_rel.md").read_text()


