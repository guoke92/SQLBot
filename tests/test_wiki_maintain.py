"""Wiki maintenance: merge keys, trust cap, import replay, and promote gate."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_BACKEND = _ROOT / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from apps.knowledge.wiki.contract import parse_page  # noqa: E402
from apps.knowledge.wiki.materialize import (  # noqa: E402
    blank_page,
    compose_import_body,
    materialize_markdown,
    promotion_blockers,
)

_DICT = """---
type: dict
title: 支付状态
page_key: ca_fee_company__pay_status
belong: dicts
status: published
sources:
  - code_path:Fee.java:1
contract_version: "0.1"
---

# 支付状态

导入说明。

```ground:dict
dict: ca_fee_company__pay_status
fields:
  - ca_fee_company.pay_status
values:
  UNPAID:
    trust: confirmed
    label: 未缴费
  PAID:
    trust: confirmed
    label: 已缴费
triage: keep
```
"""

_DICT_REIMPORT = _DICT.replace("导入说明。", "新基线说明。").replace(
    "status: published", "status: draft"
)

_TABLE = """---
type: table
title: 企业
page_key: ca_fee_company
belong: tables
status: draft
sources: []
contract_version: "0.1"
---

# 企业

## 关联

```ground:table
table: ca_fee_company
fields:
  - name: certification_no
    type: string
    desc: 统一社会信用代码
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.certification_no
right: ca_fee_company.certification_no
cardinality: many_to_one
trust: confirmed
evidence: code_path:Fee.java:10
```
"""

_PROCESS = """---
type: process
title: 异步任务
page_key: async_io_task__status
belong: processes
status: draft
sources: []
contract_version: "0.1"
---

# 异步任务

```ground:process
process: async_io_task__status
stages:
  - stage: 执行
    transitions:
      - from: PENDING
        event: start
        to: RUNNING
        evidence: code_path:Task.java:1
```
"""


def _values(body: str) -> dict:
    page = parse_page(body)
    block = next(item for item in page.ground_blocks if item.kind == "dict")
    return block.data["values"]


def test_confirmed_label_is_kept_and_a_new_code_stays_proposed() -> None:
    result = materialize_markdown(
        _DICT,
        [
            {
                "op": "upsert_claim",
                "origin": "conversation",
                "status": "applied",
                "claim_path": "dicts/ca_fee_company__pay_status#values.UNPAID",
                "source_ref": "conversation:9/3",
                "payload": {"label": "未付费", "trust": "confirmed"},
            },
            {
                "op": "upsert_claim",
                "origin": "conversation",
                "status": "applied",
                "claim_path": "dicts/ca_fee_company__pay_status#values.WAIVED",
                "source_ref": "conversation:9/3",
                "payload": {"label": "免缴", "trust": "confirmed"},
            },
        ],
    )
    values = _values(result.body)
    assert values["UNPAID"]["label"] == "未缴费"
    assert values["UNPAID"]["trust"] == "confirmed"
    assert values["WAIVED"]["trust"] == "proposed"
    assert values["WAIVED"]["label"] == "免缴"
    assert result.outcomes[0].status == "conflicted"
    assert result.outcomes[1].status == "applied"
    assert "枚举 UNPAID 含义冲突" in result.body
    assert "conversation:9/3" in result.body


def test_proposed_patch_does_not_change_the_page() -> None:
    result = materialize_markdown(
        _DICT,
        [
            {
                "op": "upsert_claim",
                "origin": "conversation",
                "status": "proposed",
                "claim_path": "values.UNPAID",
                "payload": {"label": "改掉"},
            }
        ],
    )
    assert _values(result.body)["UNPAID"]["label"] == "未缴费"
    assert "改掉" not in result.body
    assert result.outcomes[0].status == "proposed"


def test_import_replays_alias_and_keeps_status() -> None:
    alias = {
        "op": "add_alias",
        "origin": "maintain",
        "status": "applied",
        "claim_path": "aliases",
        "source_ref": "user_statement:run-1",
        "payload": {"alias": "缴费状态"},
    }
    first = materialize_markdown(_DICT, [alias])
    assert "缴费状态" in first.body
    body, status = compose_import_body(
        _DICT_REIMPORT, [alias], existing_status="published"
    )
    assert "缴费状态" in body
    assert "新基线说明。" in body
    assert "导入说明。" not in body
    assert status == "published"
    assert parse_page(body).status == "published"


def test_notes_survive_a_new_baseline() -> None:
    note = {
        "op": "upsert_claim",
        "origin": "document",
        "status": "applied",
        "claim_path": "notes",
        "source_ref": "document:4",
        "payload": {"text": "客服把未缴费叫待支付"},
    }
    body, _status = compose_import_body(
        _DICT_REIMPORT, [note], existing_status="published"
    )
    assert "## 维护说明" in body
    assert "客服把未缴费叫待支付" in body
    assert "新基线说明。" in body
    assert body.count("## 维护说明") == 1


def test_missing_field_conflicts_and_existing_note_is_appended() -> None:
    result = materialize_markdown(
        _TABLE,
        [
            {
                "op": "upsert_claim",
                "origin": "maintain",
                "status": "applied",
                "claim_path": "fields.not_a_column",
                "payload": {"desc": "不存在"},
            },
            {
                "op": "upsert_claim",
                "origin": "maintain",
                "status": "applied",
                "claim_path": "fields.certification_no",
                "source_ref": "user_statement:run-2",
                "payload": {"desc": "营业执照号"},
            },
        ],
    )
    assert result.outcomes[0].status == "conflicted"
    assert "字段 not_a_column 不存在" in result.body
    assert "营业执照号" in result.body
    assert "统一社会信用代码" in result.body


def test_confirmed_relation_cardinality_is_not_replaced() -> None:
    result = materialize_markdown(
        _TABLE,
        [
            {
                "op": "upsert_claim",
                "origin": "conversation",
                "status": "applied",
                "claim_path": "relations",
                "payload": {
                    "left": "cust_company_info.certification_no",
                    "right": "ca_fee_company.certification_no",
                    "cardinality": "one_to_one",
                    "trust": "confirmed",
                },
            }
        ],
    )
    assert result.outcomes[0].status == "conflicted"
    assert "many_to_one" in result.body
    assert "关系基数冲突" in result.body


def test_stage_transition_appends_once() -> None:
    patch = {
        "op": "upsert_claim",
        "origin": "maintain",
        "status": "applied",
        "claim_path": "stages.执行",
        "source_ref": "user_statement:run-3",
        "payload": {"from": "RUNNING", "event": "fail", "to": "FAILED"},
    }
    once = materialize_markdown(_PROCESS, [patch])
    twice = materialize_markdown(once.body, [patch])
    page = parse_page(twice.body)
    block = next(item for item in page.ground_blocks if item.kind == "process")
    transitions = block.data["stages"][0]["transitions"]
    failed = [item for item in transitions if item["to"] == "FAILED"]
    assert len(failed) == 1
    assert failed[0]["evidence"] == "user_statement:run-3"


def test_create_page_refuses_physical_pages_and_drafts_a_concept() -> None:
    refused = materialize_markdown(
        "",
        [
            {
                "op": "create_page",
                "origin": "maintain",
                "status": "applied",
                "payload": {
                    "belong": "tables",
                    "page_key": "ca_fee_company",
                    "title": "企业",
                },
            }
        ],
    )
    assert refused.outcomes[0].status == "conflicted"
    assert refused.body.strip() == ""
    created = materialize_markdown(
        "",
        [
            {
                "op": "create_page",
                "origin": "document",
                "status": "applied",
                "source_ref": "document:8",
                "payload": {
                    "belong": "concepts",
                    "page_key": "fee_rule",
                    "title": "费用规则",
                },
            }
        ],
    )
    page = parse_page(created.body)
    assert page.type == "concept"
    assert page.status == "draft"
    assert page.belong == "concepts"
    assert "document:8" in page.sources


def test_promote_blocks_duplicate_ground_and_unpublished_closure() -> None:
    clean = blank_page(
        belong="concepts",
        page_key="fee_rule",
        title="费用规则",
        source_ref="user_statement:1",
    )
    assert promotion_blockers(clean, siblings=[]) == []
    duplicated = clean + (
        "\n```ground:caliber\ncaliber: fee_rule\npredicate: enable = 'Y'\n```\n"
        "\n```ground:caliber\ncaliber: fee_rule\npredicate: enable = 'N'\n```\n"
    )
    codes = {item.code for item in promotion_blockers(duplicated, siblings=[])}
    assert "DUPLICATE_GROUND_BLOCK" in codes
    linked = clean.replace(
        "# 费用规则", "# 费用规则\n\n见 [[tables/ca_fee_company]]。\n"
    )
    blockers = promotion_blockers(
        linked,
        siblings=[
            {"belong": "tables", "page_key": "ca_fee_company", "status": "draft"},
        ],
    )
    assert any(item.code == "CLOSURE_UNPUBLISHED" for item in blockers)
    published = promotion_blockers(
        linked,
        siblings=[
            {"belong": "tables", "page_key": "ca_fee_company", "status": "published"},
        ],
    )
    assert published == []


def test_promote_patch_is_the_status_writer() -> None:
    drafted = blank_page(
        belong="rules", page_key="once", title="只答一次", source_ref="user_statement:1"
    )
    result = materialize_markdown(
        "",
        [
            {
                "op": "create_page",
                "origin": "maintain",
                "status": "applied",
                "source_ref": "user_statement:1",
                "payload": {"belong": "rules", "page_key": "once", "title": "只答一次"},
            },
            {
                "op": "promote",
                "origin": "maintain",
                "status": "applied",
                "payload": {"status": "published"},
            },
        ],
    )
    assert parse_page(result.body).status == "published"
    assert parse_page(drafted).status == "draft"


def test_single_source_replaces_caliber_and_another_source_reviews() -> None:
    base = """---
type: caliber
title: 已签约
page_key: signed
belong: calibers
status: draft
sources:
  - document:1
contract_version: "0.1"
---

# 已签约

```ground:caliber
caliber: 已签约
predicate: status = 'SIGNED'
```
"""
    replaced = materialize_markdown(
        base,
        [
            {
                "op": "upsert_claim",
                "origin": "document",
                "status": "applied",
                "claim_path": "predicate",
                "source_ref": "document:1",
                "payload": {"predicate": "status = 'SIGNED_OK'"},
            },
            {
                "op": "upsert_claim",
                "origin": "conversation",
                "status": "applied",
                "claim_path": "predicate",
                "source_ref": "conversation:1/2",
                "payload": {"predicate": "status = 'OTHER'"},
            },
        ],
    )
    block = next(
        item
        for item in parse_page(replaced.body).ground_blocks
        if item.kind == "caliber"
    )
    assert block.data["predicate"] == "status = 'SIGNED_OK'"
    assert replaced.outcomes[0].status == "applied"
    assert replaced.outcomes[1].status == "conflicted"
    assert "caliber 已有其他来源" in replaced.body
    assert "OTHER" not in block.data["predicate"]


def test_new_page_can_receive_a_following_claim() -> None:
    result = materialize_markdown(
        "",
        [
            {
                "op": "create_page",
                "origin": "document",
                "status": "applied",
                "source_ref": "document:8",
                "payload": {
                    "belong": "calibers",
                    "page_key": "signed",
                    "title": "已签约",
                },
            },
            {
                "op": "upsert_claim",
                "origin": "document",
                "status": "applied",
                "claim_path": "predicate",
                "source_ref": "document:8",
                "payload": {"predicate": "status = 'SIGNED'"},
            },
        ],
    )
    page = parse_page(result.body)
    assert page.status == "draft"
    block = next(item for item in page.ground_blocks if item.kind == "caliber")
    assert block.data["predicate"] == "status = 'SIGNED'"
    assert result.outcomes[0].status == "applied"
    assert result.outcomes[1].status == "applied"


def test_relation_path_and_unconfirmed_cardinality_conflict() -> None:
    result = materialize_markdown(
        _TABLE,
        [
            {
                "op": "upsert_claim",
                "origin": "maintain",
                "status": "applied",
                "claim_path": (
                    "relations.cust_company_info.certification_no"
                    "__ca_fee_company.certification_no"
                ),
                "payload": {"cardinality": "one_to_one"},
            },
            {
                "op": "upsert_claim",
                "origin": "maintain",
                "status": "applied",
                "claim_path": "relations.a.id__b.id",
                "payload": {"cardinality": "one_to_many", "trust": "confirmed"},
            },
            {
                "op": "upsert_claim",
                "origin": "conversation",
                "status": "applied",
                "claim_path": "relations.a.id__b.id",
                "source_ref": "conversation:2/2",
                "payload": {"cardinality": "one_to_one"},
            },
        ],
    )
    assert result.outcomes[0].status == "conflicted"
    assert result.outcomes[1].status == "applied"
    assert result.outcomes[2].status == "conflicted"
    relations = [
        item.data
        for item in parse_page(result.body).ground_blocks
        if item.kind == "relation"
    ]
    added = next(item for item in relations if item["left"] == "a.id")
    assert added["cardinality"] == "one_to_many"
    assert added["trust"] == "proposed"


def test_table_structure_stays_on_the_import_baseline() -> None:
    result = materialize_markdown(
        _TABLE,
        [
            {
                "op": "upsert_claim",
                "origin": "document",
                "status": "applied",
                "claim_path": "primary_key",
                "payload": {"primary_key": ["id"]},
            }
        ],
    )
    assert result.outcomes[0].status == "conflicted"
    table = next(
        item for item in parse_page(result.body).ground_blocks if item.kind == "table"
    )
    assert "primary_key" not in table.data
    assert "表级结构以导入基线为准" in result.body


def test_import_update_does_not_reset_page_disabled() -> None:
    text = (_ROOT / "backend/apps/knowledge/wiki/corpus_store.py").read_text(
        encoding="utf-8"
    )
    assert "page_disabled" not in text


def test_chat_graph_does_not_write_wiki() -> None:
    chat = (_ROOT / "backend/graphs/current/chat.yaml").read_text(encoding="utf-8")
    config = (_ROOT / "backend/graphs/current/config.yaml").read_text(encoding="utf-8")
    assert "materialize" not in chat
    assert "wiki_maintain" not in config
    maintain = (_ROOT / "backend/graphs/current/wiki_maintain.yaml").read_text(
        encoding="utf-8"
    )
    assert "await_accept" in maintain
    assert "apply_patches_node" in maintain
