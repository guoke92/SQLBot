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
title: CA费实缴金额
page_key: CA费实缴金额
domain: ca_fee
field_targets:
- ca_fee_order.pay_amount
- ca_fee_order.order_status
---
# CA费实缴金额

已支付订单的实缴金额合计

```ground:metric
metric: CA费实缴金额
field: ca_fee_order.pay_amount
grain:
- ca_fee_order.order_status
aggregation: SUM
```

## 关联
- [[ca_fee_order]]
