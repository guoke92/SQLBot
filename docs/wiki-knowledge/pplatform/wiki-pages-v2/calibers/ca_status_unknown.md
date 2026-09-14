---
type: caliber
title: CA状态未知
page_key: ca_status_unknown
domain: CA证书收费
status: draft
aliases:
  - ca_status = UNKNOWN
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

该口径指 [[ca_fee_company]] 中 `ca_status = 'UNKNOWN'`，作为查询失败或企业未注册时的兜底展示态。它不是业务终态，而是「中台未给出确定结论」的表达。

## 需求背景

中台查询可能失败或企业尚未在签章侧注册，需要与其他状态区分，避免被误判为正常或失效。

## 版本演进

- v0（本页）：依据语义分析口径证据建立。

```ground:caliber
name: CA状态未知
predicate: ca_fee_company.ca_status = 'UNKNOWN'
scope: 查询失败/未注册兜底展示
evidence: db + CaCertificationPreCheckApplication.java
```