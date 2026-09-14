---
type: concept
title: 变更状态/审核状态
page_key: change-status
domain: 企业变更与运营变更
status: draft
aliases: [status, checkStatus, 审核状态]
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_change_record
  - db:cust_company_info
contract_version: "0.1"
maps_to: cust_change_record.status
field_targets: [cust_change_record.status]
adjudication: boundary
also_confused_with: [cust_company_info.check_status, cust_company_info.act_procinst_status, cust_company_info.cust_status]
sources: ["enrich:wiki-admin"]
belong: concepts
---

「变更状态 / 审核状态」在本域内指 [[tables.cust_change_record]] 的 `status`，即变更单维度的审批状态（`CheckStatus` 枚举），状态机见 [[processes.cust-change-record-status]]。它与三个字段容易混淆：`cust_company_info.check_status` 是企业准入审核状态（决定能否发起变更，见 [[calibers.company-change-enable]]）；`cust_company_info.act_procinst_status` 是工作流引擎侧审批状态；`cust_company_info.cust_status` 是企业生命周期状态（见 [[processes.cust-company-info-status]]）。

## 需求背景

同一家企业同时存在「准入审批」「变更审批」「工作流实例状态」「生命周期状态」四条不同粒度的状态线，字段命名相近但归属对象不同；本概念用于在口径与规则页之间固定指代，避免把企业状态当作单据状态使用。

## 版本演进

v0.1：首次登记，边界判定来自字段语义分析。

相关：[[cust_change_record]]
