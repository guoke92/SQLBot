---
type: caliber
title: 企业已锁定年费
page_key: company_fee_locked
domain: CA证书收费
status: draft
aliases:
  - fee_locked = Y
oid: 1
scope:
  databases:
    - unknown
sources:
  - db
  - code_path:CaFeeRuleEngineService.java
contract_version: "0.1"
belong: calibers
---

该口径指 [[ca_fee_company]] 中 `fee_locked = 'Y'`，表示企业已锁定年费标准（`locked_annual_fee`）。在年费定价链中，锁定价优先于项目角色价，见 [[annual_fee_pricing_chain]]。

## 需求背景

首次缴费成功后需要固定价格，避免项目调价影响已购企业的续费金额；因此需要「是否已锁定」的可判定口径。

## 版本演进

- v0（本页）：依据语义分析口径证据建立。

```ground:caliber
name: 企业已锁定年费
predicate: ca_fee_company.fee_locked = 'Y'
scope: 年费定价链锁定价优先
evidence: db + CaFeeRuleEngineService.java
```