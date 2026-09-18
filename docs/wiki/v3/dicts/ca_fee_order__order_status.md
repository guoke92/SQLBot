---
type: dict
title: ca_fee_order.order_status
page_key: ca_fee_order__order_status
belong: dicts
status: draft
anchors: [ca_fee_order.order_status]
sources: ['database_profile:ca_fee_order.order_status', 'database_schema:ca_fee_order.order_status',
  'code_path:CaFeeOrderStatusEnum.java:17', 'code_path:CaFeeOrderStatusEnum.java:15',
  'code_path:CaFeeOrderStatusEnum.java:16', 'code_path:CaFeeOrderStatusEnum.java:18']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [ca_fee_order]
---

# ca_fee_order.order_status

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `ca_fee_order.order_status`，表页 [[tables/ca_fee_order]]。

## 取值

```ground:dict
dict: ca_fee_order__order_status
fields: [ca_fee_order.order_status]
values:
  CLOSED: {trust: confirmed, label: 已关闭, evidence: 'code_path:CaFeeOrderStatusEnum.java:17'}
  PENDING: {trust: confirmed, label: 未缴费, evidence: 'code_path:CaFeeOrderStatusEnum.java:15'}
  PAID: {trust: confirmed, label: 已缴费, evidence: 'code_path:CaFeeOrderStatusEnum.java:16'}
  PAIDING: {trust: proposed}
  UNPAID: {trust: proposed}
  EXPIRED: {trust: confirmed, label: 已过期, evidence: 'code_path:CaFeeOrderStatusEnum.java:18'}
triage: keep
```
