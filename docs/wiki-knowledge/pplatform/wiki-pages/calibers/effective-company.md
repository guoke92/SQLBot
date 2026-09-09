---
type: caliber
title: 有效企业
page_key: effective-company
belong: calibers
domain: 企业建档与准入
status: published
aliases: [未注销企业]
oid: 1

sources: ["db", "code", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [cust_company_info.cust_status, cust_company_info.enable]
scope:
  databases: [lowcode_pplatform]
---

# 有效企业

本口径识别未注销且启用中的企业，排除已注销（WRITEOFF）的企业，无论其是否处于冻结状态。用于常规业务范围内的客户集合。

## 需求背景

注销是客户生命周期的终态，由 [[customer-lifecycle-status-machine]] 的“注销”事件置为 WRITEOFF。有效企业口径常与 [[authenticated-company]] 配合使用：有效不一定已认证，已认证一定有效（前提 enable=Y）。

## 版本演进

口径证据来自代码 `custStatusOperator` 中注销状态为 WRITEOFF。

```ground:caliber
name: 有效企业
predicate: "cust_company_info.cust_status <> 'WRITEOFF' AND cust_company_info.enable = 'Y'"
scope: 未注销且启用中的企业
evidence: "code:custStatusOperator 注销状态为 WRITEOFF"
```

相关概念：[[freeze]]；相关表：[[cust_company_info]]