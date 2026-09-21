---
type: rule
title: 订单 EXPIRED 未见落库
page_key: expired_enum_unused
belong: rules
domain: ca_fee
status: draft
field_targets: [ca_fee_order.order_status]
sources: ['code_path:cafee/CaFeeOrderService.java:312']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [ca_fee_order]
---

# 订单 EXPIRED 未见落库

枚举有 EXPIRED，现网未见 setOrderStatus(EXPIRED)。到期关待缴单写 CLOSED，宽表到期写 UNPAID。

```ground:rule
rule: 订单 EXPIRED 未见落库
field_targets: [ca_fee_order.order_status]
impact: write_constraint
content: 枚举有 EXPIRED，现网未见 setOrderStatus(EXPIRED)。到期关待缴单写 CLOSED，宽表到期写 UNPAID。
evidence: code_path:cafee/CaFeeOrderService.java:312
```

## 页面链接

- [[tables/ca_fee_order]]
- [[dicts/ca_fee_order__order_status]]
- [[processes/ca_fee_order__order_status]]
