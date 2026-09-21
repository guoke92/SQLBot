---
type: rule
title: 仅未缴费订单可支付
page_key: mark_paid_only_pending
belong: rules
domain: ca_fee
status: draft
field_targets: [ca_fee_order.order_status]
sources: ['code_path:cafee/CaFeeOrderService.java:400']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [ca_fee_order]
---

# 仅未缴费订单可支付

markPaid 只接受 PENDING；已是 PAID 直接返回；其他状态拒绝。

```ground:rule
rule: 仅未缴费订单可支付
field_targets: [ca_fee_order.order_status]
impact: write_constraint
content: markPaid 只接受 PENDING；已是 PAID 直接返回；其他状态拒绝。
evidence: code_path:cafee/CaFeeOrderService.java:400
```

## 页面链接

- [[tables/ca_fee_order]]
- [[dicts/ca_fee_order__order_status]]
- [[processes/ca_fee_order__order_status]]
