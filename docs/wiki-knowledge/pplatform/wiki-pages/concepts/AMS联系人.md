---
type: concept
title: AMS联系人
page_key: concept_ams_contact
domain: customer
status: published
aliases: ["AMS来源联系人", "第三方联系人"]
oid: 1
sources: ["enrich:wiki-admin"]
contract_version: "0.1"
maps_to: "cust_person_info.source = 'AMS'"
field_targets: []
adjudication: boundary
also_confused_with:
  - "普通联系人"
boundary: "仅表示来源为AMS同步，用户类型可以是经办人/管理员"
scope:
  databases: [lowcode_pplatform]
---

AMS联系人是指来源字段为 `AMS` 的联系人记录，表示该联系人由AMS系统同步而来，而非仅限某种用户类型。

## 需求背景

在AMS对接中，来源为AMS的联系人在同步状态判断、产品过滤等方面有特殊处理，例如查询用户列表时AMS来源直接视为已同步。

## 版本演进

术语来自代码字段值，与口径「AMS来源联系人」一致。

相关：[[cust_person_info]]
