---
type: concept
title: 客户状态
page_key: customer_status
domain: 企业建档与认证
status: draft
aliases:
  - cust_status
oid: 1
scope:
  databases: []
sources:
  - db:cust_company_info.cust_status
contract_version: "0.1"
maps_to: cust_company_info.cust_status
adjudication: boundary
also_confused_with:
  - 认证状态
boundary: 客户状态包括生效、冻结、注销等，与认证状态独立。
sources: ["enrich:wiki-admin"]
belong: concepts
field_targets: [cust_company_info.cust_status]
---

“客户状态”指 `cust_company_info.cust_status`，表达企业作为客户实体的经营状态：新增（`ADD`）、生效（`EFFECT`）、冻结（`FREEZE`）、注销（`WRITEOFF`）等。流转细节见 [[customer_status_machine]]。

它与 [[auth_status]]（认证状态）相互独立，仅在“认证成功 → 客户生效”这一条联动规则上耦合（见 [[auth_success_sets_customer_effective]]）。判断“企业是否可经营”需要同时看两个状态，见 [[effective_company]]。

## 需求背景

暂无需求文档主张。冻结、注销动作会连带影响企业下用户，见 [[freeze_company_freezes_admin]]、[[writeoff_company_freezes_all_users]]。

## 版本演进

- v0.1：依据语义分析建立 concept 页，裁定与认证状态的边界。

相关：[[cust_company_info]]
