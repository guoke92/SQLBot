---
type: concept
title: 经办人
page_key: concept_operator_person
belong: concepts
domain: customer
status: published
aliases: ["operator", "operator person"]
oid: 1
sources: ["enrich:wiki-admin"]
contract_version: "0.1"
maps_to: "cust_person_info.user_type = 'accountNormal'"
field_targets: ["cust_person_info.user_type"]
adjudication: boundary
also_confused_with:
  - "管理员"
boundary: "user_type区分：accountAdmin 管理员、accountNormal 经办人、accountGuest 游客"
scope:
  databases: [lowcode_pplatform]
---

经办人是企业联系人的一种类型，属于 `cust_person_info` 表中 `user_type = 'accountNormal'` 的记录，用于处理企业事务。

## 需求背景

在AMS场景中，经办人可能来自AMS同步或内部新增，其同步状态、实名认证状态等需单独管理。经办人与管理员均由 `user_type` 字段区分。

## 版本演进

术语定义无文档声明冲突。

相关：[[cust_person_info]] [[user_type]]
