---
type: caliber
title: CA状态正常
page_key: ca_status_normal
domain: CA证书收费
status: draft
aliases:
  - ca_status = NORMAL
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

该口径指 [[ca_fee_company]] 中 `ca_status = 'NORMAL'`，用于 CA 有效性判断。`NORMAL` 是签章中台归一化后的正常态，见 [[ca_fee_company_ca_status]]、[[ca_status_cancelled]]、[[ca_status_unknown]]。

## 需求背景

收费与签章是两条链路（辨析见 [[ca_service_fee]]）：收费判定需要知道企业当前 CA 是否可用，故在收费前置检查中读取 CA 归一化状态。

## 版本演进

- v0（本页）：依据语义分析口径证据建立。

```ground:caliber
name: CA状态正常
predicate: ca_fee_company.ca_status = 'NORMAL'
scope: CA有效性判断
evidence: db + CaCertificationPreCheckApplication.java
```