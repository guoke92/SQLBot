---
type: process
title: ca_fee_company.pay_status
page_key: ca_fee_company_pay_status
belong: processes
domain: CA证书收费与订单
status: published
aliases: ["企业缴费状态机"]
oid: 1

sources: ["db", "code", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [ca_fee_company.pay_status]
scope:
  databases: [lowcode_pplatform]
---

ca_fee_company.pay_status 描述企业维度的 CA 服务费缴费状态在 UNPAID 和 PAID 之间流转，支付成功时更新为已缴费，服务到期时自动转回未缴费。

## 需求背景

需要从企业维度区分是否已完成当期 CA 服务费缴费，并在服务到期后自动将企业打回未缴费状态，为续费流程提供依据。

## 版本演进

v0.1 草稿：基于代码枚举与 CaFeeOrderService/CaFeeRenewalService 证据建立；其中支付成功更新企业快照的转换在语义分析中标注为“推断”，建议进一步核实代码路径。

```ground:process
name: ca_fee_company.pay_status
field: pay_status
states:
  - value: UNPAID
    label: 未缴费
    source: code_enum
  - value: PAID
    label: 已缴费
    source: code_enum
transitions:
  - from: UNPAID
    event: markPaid（支付成功时更新企业快照）
    to: PAID
    evidence: code_path:CaFeeOrderService.markPaid (推断)
  - from: PAID
    event: serviceExpired（服务到期）
    to: UNPAID
    evidence: code_path:CaFeeRenewalService.markServiceExpired
```

相关：[[ca_fee_company]]、[[unpaid_company]]、[[paid_company]]、[[service_expiry_processing]]