---
type: concept
title: 变更状态
page_key: change_status
domain: 企业变更与运营变更
status: draft
aliases: [status, 审核状态, 变更流程状态]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - db:cust_change_record
  - db:cust_company_info
  - code:CustChangeApplication.java
contract_version: "0.1"
maps_to: cust_change_record.status
field_targets:
  - cust_change_record.status
adjudication: boundary
also_confused_with:
  - cust_company_info.check_status
  - cust_company_info.cust_status
belong: concepts
field_targets: [cust_change_record.status]
sources: ["enrich:wiki-admin"]
---

「变更状态」默认指 `cust_change_record.status`，即单条变更流程的审核状态，取值与流转见 [[cust_change_record_status]]。

边界：`cust_change_record.status` 是单条变更流程状态；`cust_company_info.check_status` 是企业准入审核状态（[[cust_company_info]]）；`cust_company_info.cust_status` 是企业生命周期状态（[[cust_company_info_cust_status]]）。三者分属不同表、不同轴，不可互相替代。

## 需求背景

变更业务同时受「本条变更走到哪」「企业能否变更」「企业是否已在变更」三类判断影响，状态字段被复用时极易串台，本术语桥用于固定默认所指。

## 版本演进

v0.1：首次建立术语桥。

相关页面：[[cust_change_record_status]]、[[cust_company_info_cust_status]]、[[checking_company_cannot_change]]、[[company_in_change]]。

相关：[[cust_change_record]]
