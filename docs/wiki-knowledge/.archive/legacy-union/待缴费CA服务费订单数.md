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
title: 待缴费CA服务费订单数
page_key: 待缴费CA服务费订单数
domain: cafee
field_targets:
- ca_fee_order.id
- ca_fee_order.project_id
---
# 待缴费CA服务费订单数

ca_fee_order 中 order_status=PENDING 且 enable=Y 的订单数。

```ground:metric
metric: 待缴费CA服务费订单数
field: ca_fee_order.id
grain:
- ca_fee_order.project_id
aggregation: COUNT
```

## 关联
- [[ca_fee_order]]
