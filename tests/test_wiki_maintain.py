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
    assert "客服把未缴费叫待支付" in body
    assert "新基线说明。" in body
    assert "## 维护说明" not in body
    assert body.count("客服把未缴费叫待支付") == 1


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
    assert not str(failed[0].get("evidence") or "").startswith("user_statement:")
    assert "user_statement:run-3" in page.sources


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
    assert "recall_pages" in (
        _ROOT / "backend/apps/knowledge/wiki/maintain/tools.py"
    ).read_text(encoding="utf-8")


def test_vote_starts_one_dialogue_without_leaving_chat() -> None:
    service = (
        _ROOT / "backend/apps/knowledge/wiki/maintain/service.py"
    ).read_text(encoding="utf-8")
    capture = service.split("def capture_voted_record", 1)[1].split("\ndef ", 1)[0]
    sediment = service.split("def sediment_record", 1)[1].split("\ndef ", 1)[0]
    start = service.split("async def start_voted_dialogue", 1)[1].split("\ndef ", 1)[0]
    assert "open_maintain_chat" not in capture
    assert "open_maintain_chat" not in sediment
    assert "find_active_dialogue" in start
    assert "open_maintain_chat" in start
    assert 'submit_graph("wiki_maintain"' in start
    chat_api = (_ROOT / "backend/apps/chat/api/chat.py").read_text(encoding="utf-8")
    feedback = chat_api.split("async def chat_record_feedback", 1)[1].split(
        "\n@router", 1
    )[0]
    assert "start_voted_dialogue" in feedback
    listing = (_ROOT / "backend/apps/chat/curd/chat.py").read_text(encoding="utf-8")
    assert 'Chat.chat_type != "wiki"' in listing
    chat_page = (_ROOT / "frontend/src/views/chat/index.vue").read_text(encoding="utf-8")
    assert "sedimentToWiki" not in chat_page
    submit = chat_page.split("async function submitFeedback", 1)[1].split(
        "async function", 1
    )[0]
    assert "router.push" not in submit
    from apps.knowledge.wiki.maintain.service import _lane

    assert _lane("queued") == "processing"
    assert _lane("running") == "processing"
    assert _lane("awaiting_input") == "pending"
    assert _lane("succeeded") == "done"


def test_a_selected_record_is_not_a_pending_dialogue() -> None:
    service = (
        _ROOT / "backend/apps/knowledge/wiki/maintain/service.py"
    ).read_text(encoding="utf-8")
    listing = service.split("def list_dialogues", 1)[1].split("\ndef ", 1)[0]
    start = service.split("async def start_voted_dialogue", 1)[1].split("\ndef ", 1)[0]
    assert '"kind": "source"' not in listing
    assert "i18n_wiki_vote_up" in start
    assert "i18n_wiki_vote_down" in start
    vote = (_ROOT / "backend/locales/zh-CN.json").read_text(encoding="utf-8")
    assert "用户认同此对话的输出结果" in vote
    assert "不要提案" in vote
    assert "用户不认同这次对话的输出" in vote
    page = (_ROOT / "frontend/src/views/knowledge/dialogue.vue").read_text(encoding="utf-8")
    picker = page.split("function addRecords", 1)[1].split("function pasteDocument", 1)[0]
    assert "captureMaterials" not in picker
    assert "kind: 'record'" in picker


def test_a_filed_proposal_finishes_instead_of_interrupting() -> None:
    from apps.knowledge.wiki.maintain.nodes import _route_when_idle

    assert (
        _route_when_idle(has_proposals=True, note_only=False, nudges=0, tools_open=True)
        == "finish"
    )
    assert (
        _route_when_idle(has_proposals=False, note_only=True, nudges=0, tools_open=True)
        == "finish"
    )
    assert (
        _route_when_idle(has_proposals=False, note_only=False, nudges=0, tools_open=True)
        == "nudge_propose"
    )
    assert (
        _route_when_idle(has_proposals=False, note_only=False, nudges=0, tools_open=False)
        == "finish"
    )
    page = (_ROOT / "frontend/src/views/knowledge/dialogue.vue").read_text(encoding="utf-8")
    assert "change-list" in page
    assert "chatProposals" in page
    assert "review-dock" not in page


def test_prose_answer_is_sent_back_to_propose() -> None:
    from langchain_core.messages import AIMessage

    from apps.knowledge.wiki.maintain.nodes import (
        _closes_without_patches,
        nudge_propose_node,
    )
    from apps.conversation.messages import deserialize_messages

    assert _closes_without_patches([AIMessage(content="WIKI_NOTE: 不用改")])
    assert _closes_without_patches(
        [AIMessage(content=[{"type": "text", "text": "WIKI_NOTE: 不用改"}])]
    )
    assert not _closes_without_patches([AIMessage(content="建议改 aliases")])
    nudged = nudge_propose_node({"messages": [], "wiki_propose_nudges": 0})
    assert nudged["wiki_propose_nudges"] == 1
    text = deserialize_messages(nudged["messages"])[-1].content
    assert "propose_patch" in str(text)


def test_reverted_alias_stays_gone_on_replay() -> None:
    alias = {
        "op": "add_alias",
        "origin": "conversation",
        "status": "applied",
        "claim_path": "aliases",
        "source_ref": "conversation:1/2",
        "payload": {"alias": "缴费状态"},
    }
    kept = materialize_markdown(_DICT, [alias, {"op": "revert_marker", "status": "applied"}])
    assert "缴费状态" in kept.body
    undone = materialize_markdown(_DICT, [{**alias, "status": "reverted"}])
    assert "缴费状态" not in undone.body


def test_conversation_cannot_confirm_structure_or_labels() -> None:
    from apps.knowledge.wiki.maintain.materials import cap_claim

    assert cap_claim("conversation", "structure", "confirmed") == "refuse"
    assert cap_claim("conversation", "enum_label", "confirmed") == "proposed"
    assert cap_claim("conversation", "relation", "confirmed") == "proposed"
    assert cap_claim("conversation", "pattern", "confirmed") == "proposed"
    assert cap_claim("document", "structure", "confirmed") == "refuse"
    assert cap_claim("import", "structure", "confirmed") == "confirmed"


def test_supplement_keeps_the_decision_as_revise() -> None:
    from apps.knowledge.wiki.maintain.nodes import _decision

    assert _decision([{"text": "再补一条枚举说明"}]) == ("revise", "再补一条枚举说明")
    assert _decision([{"option_id": "reject"}])[0] == "reject"
    assert _decision([{"option_id": "accept"}]) == ("accept", "")


def test_related_page_is_not_outside_the_target() -> None:
    from apps.knowledge.wiki.maintain.service import classify_scope

    class _Empty:
        def exec(self, *_args: object, **_kwargs: object) -> object:
            return self

        def first(self) -> None:
            return None

    focus = {
        "corpus_key": "",
        "pages": [{"belong": "dicts", "page_key": "ca_fee_company__pay_status"}],
        "related": [{"belong": "tables", "page_key": "ca_fee_company"}],
    }
    assert (
        classify_scope(_Empty(), "dicts", "ca_fee_company__pay_status", focus) == "target"
    )
    assert classify_scope(_Empty(), "tables", "ca_fee_company", focus) == "related"
    assert classify_scope(_Empty(), "concepts", "other", focus) == "outside"


def test_proposal_reason_is_the_observation_only() -> None:
    from apps.knowledge.wiki.maintain.service import (
        proposal_basis,
        proposal_detail,
        proposal_reason,
    )

    class _Row:
        op = "add_alias"
        claim_path = "concepts/oper_staff_field#aliases.企业运营人员"
        page_key = "oper_staff_field"
        observation = {"excerpt": "哪些企业运营人员为空", "locator": "conversation:410/954"}
        payload = {"note": "这是主张正文，不是改动理由", "alias": "企业运营人员"}
        source_ref = "conversation:410/954"

    assert proposal_reason(_Row()) == ""
    assert proposal_detail(_Row()) == "企业运营人员"
    assert proposal_basis(_Row()) == "conversation:410/954 · 哪些企业运营人员为空"

    class _Stored:
        op = "upsert_claim"
        claim_path = "concepts/oper_staff_field#notes"
        page_key = "oper_staff_field"
        observation = {"reason": "问数把企业运营人员当成了建档经办人"}
        payload = {"note": "不要用这段"}
        source_ref = ""

    assert proposal_reason(_Stored()) == "问数把企业运营人员当成了建档经办人"
    assert proposal_detail(_Stored()) == "concepts/oper_staff_field#notes"


def test_alias_patch_keeps_unrelated_lists_on_one_line() -> None:
    page = """---
type: concept
title: 联系人运营人员
aliases: [运营人员]
field_targets: [cust_person_info.operator_id, cust_person_info.operator_realname]
related: [cust_person_info]
---

# 联系人运营人员
"""
    result = materialize_markdown(
        page,
        [
            {
                "op": "add_alias",
                "origin": "conversation",
                "status": "applied",
                "claim_path": "aliases",
                "source_ref": "conversation:410/954",
                "payload": {"alias": "企业运营人员"},
            }
        ],
    )
    assert "aliases: [运营人员, 企业运营人员]" in result.body
    assert (
        "field_targets: [cust_person_info.operator_id, cust_person_info.operator_realname]"
        in result.body
    )
    assert "related: [cust_person_info]" in result.body
    assert "conversation:410/954" in result.body


def test_page_body_rejects_snapshot_counts_and_non_filter_fields() -> None:
    from apps.knowledge.wiki.maintain.tools import create_page_payload, page_body_issues

    counted, counted_error = create_page_payload(
        {
            "title": "运营人员为空企业",
            "predicate": "全部联系人 operator_realname 为空",
            "boundary": "全库 94,994 家中 45,821 家为空，占 48.2%。",
        },
        "calibers",
        "oper_staff_empty",
    )
    assert counted is None
    assert "计数或占比" in counted_error
    excluded, excluded_error = create_page_payload(
        {
            "title": "运营人员为空企业",
            "predicate": "全部联系人 operator_realname 为空",
            "boundary": "未按 cust_build_status 过滤。",
            "field_targets": [
                "cust_person_info.operator_realname",
                "cust_company_info.cust_build_status",
            ],
        },
        "calibers",
        "oper_staff_empty",
    )
    assert excluded is None
    assert "cust_build_status" in excluded_error
    assert page_body_issues({"text": "记录口径 10395 条。"})
    assert "页面原文" in page_body_issues(
        {"text": "document_claim:企业信息维护-运营人员字段.md 判空看姓名。"}
    )
    assert "查询语句" in page_body_issues(
        {"predicate": "NOT EXISTS (SELECT 1 FROM cust_person_info p)"}
    )
    assert "operator_id" in page_body_issues(
        {
            "predicate": "联系人 operator_realname 为空",
            "field_targets": [
                "cust_person_info.operator_id",
                "cust_person_info.operator_realname",
            ],
        }
    )


def test_create_page_writes_the_caliber_instead_of_an_empty_title() -> None:
    from apps.knowledge.wiki.maintain.tools import create_page_payload

    empty, missing = create_page_payload(
        {"title": "运营人员为空企业"}, "calibers", "company_no_operator"
    )
    assert empty is None
    assert "predicate" in missing
    payload, error = create_page_payload(
        {
            "title": "运营人员为空企业",
            "predicate": "COALESCE(oper_cnt, 0) = 0",
            "boundary": "无联系人档案与有联系人未分配要分开。",
            "field_targets": ["cust_person_info.operator_realname"],
            "text": "判空看 operator_realname，不看 operator_id。",
            "trust": "confirmed",
        },
        "calibers",
        "company_no_operator",
    )
    assert error == ""
    assert payload is not None
    assert "trust" not in payload
    result = materialize_markdown(
        "",
        [
            {
                "op": "create_page",
                "origin": "conversation",
                "status": "applied",
                "source_ref": "conversation:408/950",
                "payload": payload,
            }
        ],
    )
    assert result.outcomes[0].status == "applied"
    block = next(item for item in parse_page(result.body).ground_blocks if item.kind == "caliber")
    assert block.data["predicate"] == "COALESCE(oper_cnt, 0) = 0"
    assert "无联系人档案" in block.data["boundary"]
    assert "operator_realname" in result.body
    assert "94,994" not in result.body
    assert "## 维护说明" not in result.body
    typed = materialize_markdown(
        "",
        [
            {
                "op": "create_page",
                "origin": "conversation",
                "status": "applied",
                "source_ref": "conversation:408/950",
                "payload": {
                    "type": "caliber",
                    "title": "企业运营人员为空",
                    "trust": "proposed",
                    "belong": "calibers",
                    "page_key": "company_oper_staff_empty",
                    "aliases": ["运营人员为空"],
                    "predicate": "企业主档下不存在 operator_realname 非空的联系人",
                    "boundary": "分母是企业主档全部企业，包含没有任何联系人档案的企业",
                    "field_targets": [
                        "cust_person_info.operator_id",
                        "cust_person_info.operator_realname",
                    ],
                },
            }
        ],
    )
    assert typed.outcomes[0].status == "applied"
    assert "主张路径无法落地" not in typed.body
    assert typed.body.index("没有任何联系人档案") < typed.body.index("```ground:caliber")
    typed_page = parse_page(typed.body)
    assert "运营人员为空" in typed_page.aliases
    typed_block = next(item for item in typed_page.ground_blocks if item.kind == "caliber")
    assert typed_block.data["predicate"] == "企业主档下不存在 operator_realname 非空的联系人"
    assert "没有任何联系人档案" in typed_block.data["boundary"]
    assert typed_block.data["field_targets"] == ["cust_person_info.operator_realname"]
    queried = materialize_markdown(
        "",
        [
            {
                "op": "create_page",
                "origin": "conversation",
                "status": "applied",
                "source_ref": "conversation:408/950",
                "payload": {
                    "belong": "calibers",
                    "page_key": "company_oper_staff_empty",
                    "title": "企业运营人员为空",
                    "boundary": "任一联系人 operator_realname 非空即视为已分配。",
                    "predicate": "NOT EXISTS (SELECT 1 FROM cust_person_info p WHERE p.operator_realname <> '')",
                    "field_targets": [
                        "cust_person_info.operator_id",
                        "cust_person_info.operator_realname",
                    ],
                },
            }
        ],
    )
    assert "NOT EXISTS" not in queried.body
    assert "已视为已分配" not in queried.body
    assert "视为已分配" in queried.body
    assert "operator_id" not in queried.body


def test_notes_claim_reads_text_or_notes() -> None:
    page = """---
type: concept
title: 联系人运营人员
page_key: oper_staff_field
belong: concepts
status: draft
sources: ['code_path:CustPersonApplication.java:900']
contract_version: '0.1'
---

# 联系人运营人员
"""
    result = materialize_markdown(
        page,
        [
            {
                "op": "upsert_claim",
                "origin": "conversation",
                "status": "applied",
                "claim_path": "notes",
                "source_ref": "conversation:410/954",
                "payload": {"notes": "判空看 operator_realname，不看 operator_id。"},
            }
        ],
    )
    assert result.outcomes[0].status == "applied"
    assert "判空看 operator_realname" in result.body
    assert "说明为空" not in result.body
    assert "## 维护说明" not in result.body
    assert "来源：" not in result.body


def test_wiki_analysis_loop_is_not_on_the_query_round_budget() -> None:
    from apps.knowledge.wiki.maintain.nodes import _MAX_TOOL_ROUNDS
    from apps.knowledge.wiki.maintain.prompt import render_system

    assert _MAX_TOOL_ROUNDS >= 24
    prompt = render_system({"corpus_key": "demo"})
    assert "返回的 answer" in prompt
    assert "不要用表名或单个宽词做全库搜索" in prompt
    assert "口径给 predicate" in prompt
    assert "不要写进 payload" in prompt
    assert "不要把一次问数拆成" in prompt
    assert "下一次问到同一件事" in prompt
    assert "页面推不出" in prompt
    tool_src = (
        _ROOT / "backend/apps/knowledge/wiki/maintain/tools.py"
    ).read_text(encoding="utf-8")
    reader = tool_src.split("def read_source", 1)[1].split("\n    def ", 1)[0]
    assert "_record_preview" in reader
    assert "sql_answer" not in reader


def test_record_preview_reads_the_turn_answer() -> None:
    from apps.knowledge.wiki.maintain.service import _record_preview

    class _Record:
        id = 950
        chat_id = 408
        question = "平台合作了多少家金融机构"
        sql_answer = ""
        analysis = ""
        sql = ""
        feedback = "up"
        feedback_comment = ""
        answer = {
            "content": "共接入 39 家金融机构",
            "datasets": [{"title": "机构", "sql": "select 1"}],
        }

    view = _record_preview(_Record())  # type: ignore[arg-type]
    assert "39 家" in view["body"]
    assert "```sql" in view["body"]
    assert view["feedback"] == "up"
    assert view["chat_id"] == 408
    assert view["record_id"] == 950


def test_maintain_chat_takes_the_corpus_from_the_path() -> None:
    from apps.knowledge.api.wiki import MaintainChatBody

    body = MaintainChatBody.model_validate(
        {"pages": [{"belong": "dicts", "page_key": "pay_status"}], "source_ids": [1], "brief": "你好"}
    )
    assert "corpus_key" not in MaintainChatBody.model_fields
    assert body.source_ids == [1]
