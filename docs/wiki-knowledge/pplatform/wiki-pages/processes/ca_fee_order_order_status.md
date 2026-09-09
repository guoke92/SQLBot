---
type: process
title: ca_fee_order.order_status
page_key: ca_fee_order_order_status
belong: processes
domain: CA证书收费与订单
status: published
aliases: ["订单状态机"]
oid: 1

sources: ["db", "code", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [ca_fee_order.order_status]
scope:
  databases: [lowcode_pplatform]
---

ca_fee_order.order_status 描述 CA 服务费订单从 PENDING 到 PAID 或 CLOSED 的状态流转。EXPIRED 状态在枚举中存在，但语义分析显示未实际使用迁移。

## 需求背景

需要跟踪缴费订单的支付与关闭状态，确保支付成功后可标记为已缴费，未支付订单可被关闭，同时避免使用未落地的过期状态。

## 版本演进

v0.1 草稿：基于代码枚举与 CaFeeOrderService 方法证据建立基础状态机，后续需结合实际业务场景补充异常状态与事件。

```ground:process
name: ca_fee_order.order_status
field: order_status
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
    label: 已过期（枚举存在但未见实际迁移）
    source: code_enum
transitions:
  - from: PENDING
    event: markPaid
    to: PAID
    evidence: code_path:CaFeeOrderService.markPaid
  - from: PENDING
    event: closeOrder
    to: CLOSED
    evidence: code_path:CaFeeOrderService.closeOrder
```

相关：[[ca_fee_order]]、[[pending_order]]、[[paid_order]]、[[agreement_signing_precondition]]、[[bocom_payment_confirmation]]