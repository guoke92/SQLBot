---
type: rule
title: 服务期内已缴费规则
page_key: already_paid_in_service
domain: CA证书收费
status: draft
aliases:
  - ALREADY_PAID
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeeRuleEngineService.java
contract_version: "0.1"
belong: rules
---

`ca_fee_company.service_end >= today`，或存在 `PAID` 且服务期覆盖今天的订单时，`feeStatus=PAID`，`needPay=false`，`exemptReason=ALREADY_PAID`。判定依据是 [[ca_fee_company]] 的当前服务期与 [[ca_fee_order]] 的服务期快照，口径见 [[order_status_paid]]、[[company_pay_status_paid]]，术语见 [[service_period]]。

## 需求背景

服务期内不得重复收费；企业级服务期可能因数据同步滞后，故补充「订单快照覆盖今天」的兜底判断。

## 版本演进

- v0（本页）：依据语义分析规则证据建立。

```ground:rule
name: 服务期内已缴费规则
content: ca_fee_company.service_end>=today，或存在 PAID 且服务期覆盖今天的订单，则 feeStatus=PAID，needPay=false，exemptReason=ALREADY_PAID
impact: 服务期内不重复收费
field_targets:
  - ca_fee_company.service_end
  - ca_fee_order.order_status
  - ca_fee_order.service_end
evidence: CaFeeRuleEngineService.evaluate
```