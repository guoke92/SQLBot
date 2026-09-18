---
type: dict
title: ca_fee_order.pay_method
page_key: ca_fee_order__pay_method
belong: dicts
status: draft
anchors: [ca_fee_order.pay_method]
sources: ['database_profile:ca_fee_order.pay_method', 'database_schema:ca_fee_order.pay_method',
  'code_path:CaFeePayMethodEnum.java:15']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [ca_fee_order]
---

# ca_fee_order.pay_method

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。 初审 hold：证据不足，保留待人工确认。
物理列 `ca_fee_order.pay_method`，表页 [[tables/ca_fee_order]]。

## 取值

```ground:dict
dict: ca_fee_order__pay_method
fields: [ca_fee_order.pay_method]
values:
  BOCOM: {trust: confirmed, label: 交e保对公打款, evidence: 'code_path:CaFeePayMethodEnum.java:15'}
triage: hold
needs_review: true
```
