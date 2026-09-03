---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:ca-fee@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: enum
title: CA费订单
page_key: order_no
domain: ca_fee
aliases:
- 缴费订单
- CA服务费订单
anchors:
- order_no
---
# CA费订单

企业一次CA服务费缴费申请及其支付、协议和服务周期记录。

```ground:enum
enum: order_no
fields:
- ca_fee_order.order_no
- ca_fee_order.order_status
values:
  PENDING:
    label: 待支付
  PAID:
    label: 已支付
  CLOSED:
    label: 已关闭
  EXPIRED:
    label: 已过期
```

## 关联
- [[ca_fee_order|ca_fee_order]]
