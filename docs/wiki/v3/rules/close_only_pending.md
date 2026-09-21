---
type: rule
title: 仅未缴费订单可关闭
page_key: close_only_pending
belong: rules
domain: ca_fee
status: draft
field_targets: [ca_fee_order.order_status]
sources: ['code_path:cafee/CaFeeOrderService.java:302']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [ca_fee_order]
---

# 仅未缴费订单可关闭

closeOrder 只关 PENDING。关单不改 ca_fee_company.pay_status。

```ground:rule
rule: 仅未缴费订单可关闭
field_targets: [ca_fee_order.order_status]
impact: write_constraint
content: closeOrder 只关 PENDING。关单不改 ca_fee_company.pay_status。
evidence: code_path:cafee/CaFeeOrderService.java:302
```

## 页面链接

- [[tables/ca_fee_order]]
- [[dicts/ca_fee_order__order_status]]
- [[processes/ca_fee_order__order_status]]
