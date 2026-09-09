---
type: concept
title: 企业联系人
page_key: enterprise-contact
belong: concepts
domain: AMS联系人第三方对接
status: published
aliases: [联系人, 人员, 客户人员]
oid: 1
sources:
  - code
contract_version: "0.1"
maps_to: CustPersonInfoDO
field_targets: []
adjudication: boundary
also_confused_with: [用户账号, 运营人员]
boundary: "企业联系人存储于CustPersonInfoDO，通过refCustCompanyInfo关联企业，userType区分角色"
scope:
  databases: [lowcode_pplatform]
---

企业联系人是存储在 CustPersonInfoDO 中的人员实体，通过 refCustCompanyInfo 与企业关联。联系人可拥有管理员、经办人、游客等角色，由 userType 区分。在 AMS 联系人第三方对接中，企业联系人是核心业务对象。

## 需求背景
AMS 通知新增/更新/同步企业联系人，均以企业联系人实体为操作目标。联系人的来源、推送渠道、建档状态等字段支撑同步判定与状态展示。

## 版本演进
初始版本基于语义桥提取，明确了企业联系人与用户账号、运营人员的边界。

[[cust_person_info_do]] [[admin]] [[operator]]