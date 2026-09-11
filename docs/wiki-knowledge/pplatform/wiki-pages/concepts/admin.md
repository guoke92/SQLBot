---
type: concept
title: 管理员
page_key: admin
belong: concepts
domain: AMS联系人第三方对接
status: published
aliases: [企业管理员, admin]
oid: 1
sources:
  - code
contract_version: "0.1"
maps_to: "cust_person_info.user_type='accountAdmin'"
field_targets: ["cust_person_info.user_type"]
adjudication: boundary
also_confused_with: [经办人, 游客]
boundary: "user_type=accountAdmin 表示企业管理员，accountNormal 表示经办人，accountGuest 表示游客"
scope:
  databases: [lowcode_pplatform]
---

管理员是企业联系人的一种角色，由 `cust_person_info.user_type = 'accountAdmin'` 标识。在 AMS 联系人第三方对接中，管理员的同步状态判定规则与经办人略有不同。

## 需求背景
查询企业用户列表时，管理员的同步状态判定包含“系统链路已通过”分支，与经办人相区别。

## 版本演进
初始版本基于语义桥提取，明确管理员与经办人、游客的边界。

[[enterprise_contact]] [[operator]] [[cust_person_info]] [[user_type]]