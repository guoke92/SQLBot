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
type: metric
title: CA费订单数
page_key: CA费订单数
domain: ca_fee
field_targets:
- ca_fee_order.id
- ca_fee_order.order_status
---
# CA费订单数

按订单状态统计订单行数

```ground:metric
metric: CA费订单数
field: ca_fee_order.id
grain:
- ca_fee_order.order_status
aggregation: COUNT
```

## 关联
- [[ca_fee_order]]
