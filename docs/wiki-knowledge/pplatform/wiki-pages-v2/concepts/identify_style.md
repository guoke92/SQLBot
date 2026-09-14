---
type: concept
title: 认证方式
page_key: identify_style
domain: 企业建档与认证
status: draft
aliases:
  - identify_style
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustCompanyInfoApplication.java
  - code_path:ApplyCompanyInfoApplication.java
contract_version: "0.1"
maps_to: cust_company_info.identify_style
field_targets:
  - cust_company_info.identify_style
  - cust_company_info.cust_build_type
adjudication: boundary
also_confused_with:
  - cust_company_info.cust_build_type
belong: concepts
field_targets: [cust_company_info.identify_style]
sources: ["enrich:wiki-admin"]
---

> (document_claim，未证实) 本页 ## 版本演进 含需求文档主张，尚未在代码中证实。

"认证方式"指企业以哪条路径完成认证：`INVITE_AGW`（平台录入邀请认证）、`INVITE`（客户录入邀请认证）、`SELF`（自主认证）、`SIMPLE`（简易认证）。它决定提交后进入哪条泳道、是否需要运营中台审核，见 [[rules/self_invite_need_audit]]、[[rules/finance_simple_direct_effect]]。

## 边界与歧义

与 `cust_build_type` 的边界：`identify_style` 表示认证路径（INVITE/INVITE_AGW/SELF/SIMPLE），`cust_build_type` 表示录入端（AGW_BUILD 运营/内管端、PC_BUILD 客户端）。两者是独立维度，不可互相代替或混用；DB 中 `cust_build_type` 出现 `SIMPLE` 属脏值，见 [[tables/cust_company_info]] 的 REVIEW。

## 需求背景

邀请/自主认证需经运营中台审核，简易认证无需审批，这一差异完全由本字段驱动，因此字段取值一旦写错，会影响整条审批链路。

## 版本演进

- (document_claim，未证实) 用户邀请与注册流程（邀请码 8 位 30 天有效、邮件异步、SSO/AMS 同步）：未在给定链路文件中发现实现，涉及 UserFacade/EmailAsyncService，属另一模块，与本页 INVITE 认证方式的入口相关但尚未证实。

关联：[[processes/cust_build_status_state_machine]]、[[calibers/is_simple_building]]、[[calibers/need_register_ca_not_open]]。

相关：[[cust_company_info]]
