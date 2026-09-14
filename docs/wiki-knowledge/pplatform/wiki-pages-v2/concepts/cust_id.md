---
type: concept
title: 企业ID / 客户ID
page_key: cust_id
domain: 企业变更与运营变更
status: draft
aliases: [custId, 企业ID, 客户ID]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - db:cust_change_record
  - code:CustChangeApplication.java
contract_version: "0.1"
maps_to: cust_change_record.cust_id
field_targets:
  - cust_change_record.cust_id
adjudication: boundary
also_confused_with:
  - cust_change_record.oper_cust_id
  - cust_change_record.id
belong: concepts
field_targets: [cust_change_record.cust_id]
---

「企业ID / 客户ID」在本域默认指 `cust_change_record.cust_id`，其取值是本平台企业主键，对应 [[cust_company_info]].`id`（不是 `code`）。

边界：`cust_id` 是本平台 `cust_company_info.id`；`oper_cust_id` 是运营中台客户 ID（外部系统）；`id` 是变更记录主键。三者不可互换，尤其在流程重建时 `companyId` 必须等于当前登录企业（[[change_rebuild]]）。

## 需求背景

变更业务跨平台与运营中台两侧，两侧对「客户」的编号体系不同，历史上出现过把中台 ID 当本平台 ID 使用的问题，故显式固化边界。

## 版本演进

v0.1：首次建立术语桥。

相关页面：[[cust_change_record]]、[[change_rebuild]]、[[before_after_comparison]]、[[cust_company_info]]。