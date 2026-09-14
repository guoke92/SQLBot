---
type: caliber
title: 企业已缴费口径
page_key: company_pay_status_paid
domain: CA证书收费
status: draft
aliases:
  - 企业已缴费
  - PAY_STAUS_PAID
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

企业已缴费口径指 [[ca_fee_company]] 中 `pay_status = 'PAID'` 的行，用于台账统计与已缴费企业筛选。它与订单级「已缴费」是两个层级，辨析见 [[paid_payment]]。

## 需求背景

台账需要以企业为单位给出已缴费名单，而不是按订单行罗列；服务期内不重复收费的判定亦会参考该状态（见 [[already_paid_in_service]]）。

## 版本演进

- v0（本页）：依据语义分析口径证据建立。

```ground:caliber
name: 企业已缴费口径
predicate: ca_fee_company.pay_status = 'PAID'
scope: 台账统计、已缴费企业筛选
evidence: db + CaFeeLedgerQueryService.java
```