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
type: rule
title: 订单侧无 UNPAID 值
page_key: 订单侧无-UNPAID-值
domain: CA认证与服务费
field_targets:
- ca_fee_order.order_status
---
# 订单侧无 UNPAID 值

订单用 PENDING 表达"未缴费"；EXPIRED 枚举无写值点（台账编辑也仅允许 PENDING/PAID）， 查询不应依赖 EXPIRED。

```ground:rule
rule: order-status-no-unpaid
field_targets:
- ca_fee_order.order_status
impact: query_constraint
content: 订单用 PENDING 表达"未缴费"；EXPIRED 枚举无写值点（台账编辑也仅允许 PENDING/PAID）， 查询不应依赖 EXPIRED。
scope: 订单状态过滤
```

## 关联
- [[ca_fee_order]]
