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
maps_to: cust_person_info
field_targets: ["cust_person_info.user_type", "cust_person_info.ref_cust_company_info"]
adjudication: boundary
also_confused_with: [用户账号, 运营人员]
boundary: "企业联系人存储于 cust_person_info，通过 ref_cust_company_info 关联企业，user_type 区分角色（accountAdmin/accountNormal/accountGuest）"
scope:
  databases: [lowcode_pplatform]
---

企业联系人是存储在 `cust_person_info` 中的人员实体，通过 `ref_cust_company_info` 与企业关联。联系人角色由 `user_type` 区分：管理员 `accountAdmin`、经办人 `accountNormal`、游客 `accountGuest`。在 AMS 联系人第三方对接中，企业联系人是核心业务对象。

## 需求背景
AMS 通知新增/更新/同步企业联系人，均以企业联系人实体为操作目标。联系人的来源、推送渠道、建档状态等字段支撑同步判定与状态展示。

## 版本演进
初始版本基于语义桥提取，明确了企业联系人与用户账号、运营人员的边界。

[[cust_person_info]] [[admin]] [[operator]] [[user_type]]