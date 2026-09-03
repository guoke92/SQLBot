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
title: 订单类型
page_key: order_type
domain: CA认证与服务费
aliases:
- 首次缴费
- 续费
- 存量补录
anchors:
- order_type
---
# 订单类型

FIRST 首次缴费 / RENEW 即将到期续费 / RENEW_EXPIRED 已到期续费 / STOCK 存量补录 （项目开收费后对存量关联企业补建）。

```ground:enum
enum: order_type
fields:
- ca_fee_order.order_type
values:
  FIRST:
    label: 首次缴费
  RENEW:
    label: 即将到期续费
  RENEW_EXPIRED:
    label: 已到期续费
  STOCK:
    label: 存量补录
```

## 关联
- [[ca_fee_order|ca_fee_order]]
