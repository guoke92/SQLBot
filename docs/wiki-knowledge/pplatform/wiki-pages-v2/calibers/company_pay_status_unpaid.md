---
type: caliber
title: 企业未缴费口径
page_key: company_pay_status_unpaid
domain: CA证书收费
status: draft
aliases:
  - 企业未缴费
oid: 1
scope:
  databases:
    - unknown
sources:
  - db
  - code_path:CaFeeLedgerQueryService.java
contract_version: "0.1"
belong: calibers
---

企业未缴费口径指 [[ca_fee_company]] 中 `pay_status = 'UNPAID'` 的行，用于台账统计与未缴费企业筛选。命中本口径不等于必须立即缴费，仍需通过豁免与放行规则（见 [[whitelist_exempt]]、[[defer_pay_exempt]]、[[multi_project_pass]]）。

## 需求背景

企业级未缴是汇总结论，订单级待缴是可操作对象，二者混用会导致运营误操作，故单列口径，辨析见 [[pending_payment]]。

## 版本演进

- v0（本页）：依据语义分析口径证据建立。

```ground:caliber
name: 企业未缴费口径
predicate: ca_fee_company.pay_status = 'UNPAID'
scope: 台账统计、未缴费企业筛选
evidence: db + CaFeeLedgerQueryService.java
```