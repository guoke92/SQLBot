---
type: process
title: 企业缴费状态机
page_key: ca_fee_company_pay_status
domain: CA证书收费
status: draft
aliases: [企业缴费状态]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:CaFeeOrderService.java", "code:CaFeeRenewalService.java"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: processes
field_targets: [ca_fee_company.pay_status]
---

作用于 [[ca_fee_company]] 的 `pay_status`（字典 [[pay_status]]）。企业维度汇总，与订单 [[ca_fee_order_status]] 分开。

`UNPAID` 不等于「立刻要缴费」——白名单豁免见 [[whitelist_exempt]]。

```ground:process
name: 企业缴费状态
field: ca_fee_company.pay_status
states:
  - value: PAID
    label: 已缴费
    source: code_enum
  - value: UNPAID
    label: 未缴费
    source: code_enum
transitions:
  - from: UNPAID
    event: 订单缴费成功回写企业缴费状态
    to: PAID
    evidence: code_path:CaFeeOrderService.java:450
  - from: PAID
    event: 服务到期处理 markServiceExpired
    to: UNPAID
    evidence: code_path:CaFeeRenewalService.java
```
