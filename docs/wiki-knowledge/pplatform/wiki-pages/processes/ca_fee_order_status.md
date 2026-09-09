---
type: process
title: CA收费订单状态机
page_key: ca_fee_order_status
belong: processes
domain: ca_cert_fee
status: published
aliases: []
oid: 1

sources: ["code", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [ca_fee_order.order_status]
scope:
  databases: [lowcode_pplatform]
---

# CA收费订单状态机

业务定位：定义 `ca_fee_order.order_status` 字段的状态集合与流转规则，覆盖订单从创建到完结的生命周期。

## 需求背景

订单状态是收费流程的核心控制点。需要明确哪些状态是终态、哪些事件触发状态变更，以确保业务操作合规。

## 版本演进

当前版本仅包含 `markPaid` 和 `closeOrder` 两个事件，后续可能补充过期、退款等事件。

```ground:process
name: ca_fee_order_status
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
    event: markPaid
    to: PAID
    evidence: code_path:CaFeeOrderApplication.java:markPaid
  - from: PENDING
    event: closeOrder
    to: CLOSED
    evidence: code_path:CaFeeOrderApplication.java:closeOrder
```

[[ca_fee_order]] · [[pending_order]] · [[paid_order]]