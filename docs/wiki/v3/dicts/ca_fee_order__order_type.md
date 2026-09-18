---
type: dict
title: ca_fee_order.order_type
page_key: ca_fee_order__order_type
belong: dicts
status: draft
anchors: [ca_fee_order.order_type]
sources: ['database_profile:ca_fee_order.order_type', 'database_schema:ca_fee_order.order_type',
  'code_path:CaFeeOrderTypeEnum.java:18', 'code_path:CaFeeOrderTypeEnum.java:15',
  'code_path:CaFeeOrderTypeEnum.java:17', 'code_path:CaFeeOrderTypeEnum.java:16']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [ca_fee_order]
---

# ca_fee_order.order_type

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `ca_fee_order.order_type`，表页 [[tables/ca_fee_order]]。

## 取值

```ground:dict
dict: ca_fee_order__order_type
fields: [ca_fee_order.order_type]
values:
  STOCK: {trust: confirmed, label: 存量补录, evidence: 'code_path:CaFeeOrderTypeEnum.java:18'}
  FIRST: {trust: confirmed, label: 首次缴费, evidence: 'code_path:CaFeeOrderTypeEnum.java:15'}
  RENEW_EXPIRED: {trust: confirmed, label: 已到期续费, evidence: 'code_path:CaFeeOrderTypeEnum.java:17'}
  RENEW: {trust: confirmed, label: 即将到期续费, evidence: 'code_path:CaFeeOrderTypeEnum.java:16'}
triage: keep
```
