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
type: pattern
title: 各订单状态的CA费订单数
page_key: order-status-distribution
domain: ca_fee
anchors:
- ca_fee_order
---
# 各订单状态的CA费订单数

问法：各订单状态的CA费订单数

```ground:pattern
pattern: order-status-distribution
question: 各订单状态的CA费订单数
sql: 'SELECT order_status, COUNT(*) AS order_count FROM ca_fee_order

  WHERE enable = ''Y'' GROUP BY order_status'
verification: PENDING_VALIDATION
```

## 关联
- [[ca_fee_order]]
