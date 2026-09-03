---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:ca-fee-collection@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: enum
title: 订单状态
page_key: order_status
domain: CA认证与服务费
aliases:
- 待缴费订单
- 已缴费订单
- 已关闭订单
anchors:
- order_status
---
# 订单状态

ca_fee_order.order_status：PENDING 未缴费（新建单）→ PAID 已缴费 / CLOSED 已关闭。 EXPIRED 枚举存在但无写值点（残留值）。订单侧无 UNPAID 值——"待缴费"用 PENDING 表达。

```ground:enum
enum: order_status
fields:
- ca_fee_order.order_status
values:
  PENDING:
    label: 未缴费
  PAID:
    label: 已缴费
  CLOSED:
    label: 已关闭
  EXPIRED:
    label: 已过期（无写值点，残留值）
```

## 关联
- [[ca_fee_order|ca_fee_order]]
