---
type: caliber
title: CA状态失效
page_key: ca_status_cancelled
domain: CA证书收费
status: draft
aliases:
  - ca_status = CANCELLED
  - CA注销
oid: 1
scope:
  databases:
    - unknown
sources:
  - db
  - code_path:CaCertificationPreCheckApplication.java
contract_version: "0.1"
belong: calibers
---

该口径指 [[ca_fee_company]] 中 `ca_status = 'CANCELLED'`，覆盖 CA 注销／作废／失效三种中台语义的归并结果，用于 CA 失效提示与重置开通状态。

## 需求背景

失效态需要显式提示并触发开通状态重置，否则企业会停留在「看似有效」的收费判定上。

## 版本演进

- v0（本页）：依据语义分析口径证据建立。

```ground:caliber
name: CA状态失效
predicate: ca_fee_company.ca_status = 'CANCELLED'
scope: CA失效提示与重置开通状态
evidence: db + CaCertificationPreCheckApplication.java
```