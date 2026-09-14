---
type: concept
title: 注销
page_key: writeoff
domain: 企业建档与认证
status: draft
aliases:
  - WRITEOFF
  - DISABLE
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustCompanyInfoApplication.java:diable
contract_version: "0.1"
maps_to: cust_company_info.cust_status
field_targets:
  - cust_company_info.cust_status
  - cust_status.WRITEOFF
  - cust_company_info.enable
adjudication: synonym
also_confused_with:
  - cust_company_info.enable
belong: concepts
field_targets: [cust_company_info.cust_status]
sources: ["enrich:wiki-admin"]
---

"注销"是生命周期终态：调用 `diable()` 把 `cust_status` 置为 `WRITEOFF`，并同时冻结该企业下的全部用户。业务叙述中的"主动注销"即此动作。

## 边界与歧义

与 `enable` 字段的边界：`enable` 表达企业是否启用，与 `cust_status='WRITEOFF'` 不是同一维度；不要把 `enable='N'` 读作注销。

## 需求背景

需求文档主张"已通过 → 已注销"（anchor，双源：code_path:CustCompanyInfoApplication.java:diable:custStatusOperator + reqdoc:已通过转已冻结或已注销），并伴随用户冻结。注销后是否仍允许变更，见 [[rules/applying_record_uniqueness]] 中的未证实主张。

## 版本演进

v0 初稿：以 `custStatusOperator` 的 `allowStatusList` 校验与写值点为准。

关联：[[concepts/freeze]]、[[processes/cust_status_state_machine]]、[[rules/cust_status_sync_third_party]]。

相关：[[cust_company_info]]
