---
type: concept
title: 运营人员变更
page_key: concept_operator_change
belong: concepts
domain: 企业变更与运营变更
status: published
aliases: ["操作人员变更", "operation change"]
oid: 1

sources: ["db", "enrich:wiki-admin"]
contract_version: "0.1"
maps_to: "cust_oper_change_record.change_type"
field_targets: ["cust_oper_change_record.change_type"]
adjudication: "boundary"
also_confused_with: ["企业变更 cust_change_record"]
coverage_note: 术语边界
scope:
  databases: [lowcode_pplatform]
---

“运营人员变更”专指企业所属运营人员（operator）的变更，记录在 `cust_oper_change_record` 表中，以 `change_type` 区分变更类型。它与 `cust_change_record` 的企业信息变更不同，后者关注企业自身资料的修改。

## 需求背景

边界说明：`cust_oper_change_record` 记录企业运营人员的变更，与 `cust_change_record` 的企业信息变更不同。

## 版本演进

暂无。

相关：[[cust_oper_change_record]]
