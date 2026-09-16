---
type: process
title: CA 服务费订单状态机
page_key: ca_fee_order_status
domain: CA证书收费
status: draft
aliases: [订单状态机]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:CaFeeOrderService.java", "code:CaFeeOrderApplication.java"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: processes
field_targets: [ca_fee_order.order_status]
---

作用于 [[ca_fee_order]] 的 `order_status`（字典 [[order_status]]）。`PENDING` 是可支付、可签协议、可关闭的状态；进入 `PAID` 时回写企业 [[ca_fee_company_pay_status]]。

运行时迁移只有 `PENDING → PAID` 与 `PENDING → CLOSED`。`EXPIRED` 在枚举中（已过期），但没有迁入边、库中也没有该值。库中偶发的 `PAIDING` / `UNPAID` 不在枚举里，见 [[order_status]]。

```ground:process
name: CA服务费订单状态
field: ca_fee_order.order_status
states:
  - value: PENDING
    label: 未缴费
    source: code_enum
  - value: PAID
    label: 已缴费
    source: code_enum
  - value: CLOSED
    label: 已关闭
    source: code_enum
  - value: EXPIRED
    label: 已过期
    source: code_enum
transitions:
  - from: PENDING
    event: 支付成功 markPaid
    to: PAID
    evidence: code_path:CaFeeOrderService.java:279
  - from: PENDING
    event: 关闭订单 closeOrder
    to: CLOSED
    evidence: code_path:CaFeeOrderApplication.java
  - from: PENDING
    event: 批量白名单命中并关闭待缴单
    to: CLOSED
    evidence: code_path:CaFeeLedgerOperateService.java
```
