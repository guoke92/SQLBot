---
type: concept
title: 经办人
page_key: concepts/operator
domain: AMS联系人第三方对接
status: published
aliases: [操作员, operator]
oid: 1
sources:
  - code
contract_version: "0.1"
maps_to: "CustPersonInfoDO.userType='operator'"
field_targets: ["CustPersonInfoDO.userType"]
adjudication: boundary
also_confused_with: [运营人员]
boundary: "经办人属于企业联系人，运营人员是平台运营人员，存储在operator字段"
scope:
  databases: [lowcode_pplatform]
---

经办人是企业联系人的一种角色，由 CustPersonInfoDO.userType 等于 operator 标识。与平台运营人员不同，经办人属于企业联系人实体。

## 需求背景
AMS 通知更新经办人信息、查询同步状态等场景均涉及经办人。经办人同步状态判定条件是 operatorPushSystem 包含目标渠道或来源为 AMS。

## 版本演进
初始版本基于语义桥提取，明确经办人与运营人员的边界。

[[enterprise_contact]] [[admin]] [[cust_person_info_do]]