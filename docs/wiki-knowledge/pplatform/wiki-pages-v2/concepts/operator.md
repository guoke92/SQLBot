---
type: concept
title: 运营人员/经办人
page_key: concept.operator
domain: 企业变更与运营变更
status: draft
aliases: [operator, person_id, 经办人]
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_person_info
  - db:cust_oper_change_record
contract_version: "0.1"
maps_to: cust_oper_change_record.before_operator_id / after_operator_id
field_targets: [cust_oper_change_record.before_operator_id, cust_oper_change_record.after_operator_id]
adjudication: boundary
also_confused_with: [cust_oper_change_record.person_id, cust_person_info.operator_id]
sources: ["enrich:wiki-admin"]
---

「运营人员」与「经办人」在 [[tables.cust_oper_change_record]] 上是两组不同字段：`before_operator_*` / `after_operator_*` 指平台运营人员（被变更的对象）；`person_id` / `person_name` 指企业联系人（变更主体，即经办人）。[[tables.cust_person_info]] 的 `operator_id` 则是该联系人当前绑定的运营人冗余，属于当前态而非流水。

## 需求背景

一次运营人员调整的主体是联系人、客体是运营人员，字段命名上都带 `operator`/`person`，极易读反变更方向；本概念固定「谁被改、改成谁、由谁触发」的指代关系，配合 [[rules.oper-change-record-query]] 使用。

## 版本演进

v0.1：首次登记，边界判定来自字段语义分析。

相关：[[cust_oper_change_record]]
