---
type: dict
title: ca_fee_order.invoice_status
page_key: ca_fee_order__invoice_status
belong: dicts
status: draft
anchors: [ca_fee_order.invoice_status]
sources: ['database_profile:ca_fee_order.invoice_status', 'database_schema:ca_fee_order.invoice_status',
  'code_path:CaFeeInvoiceStatusEnum.java:15', 'code_path:CaFeeInvoiceStatusEnum.java:16',
  'code_path:CaFeeInvoiceStatusEnum.java:17', 'code_path:CaFeeInvoiceStatusEnum.java:18']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [ca_fee_order]
---

# ca_fee_order.invoice_status

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `ca_fee_order.invoice_status`，表页 [[tables/ca_fee_order]]。

## 取值

```ground:dict
dict: ca_fee_order__invoice_status
fields: [ca_fee_order.invoice_status]
values:
  PENDING: {trust: confirmed, label: 开票中, evidence: 'code_path:CaFeeInvoiceStatusEnum.java:15'}
  ISSUED: {trust: confirmed, label: 已开票, evidence: 'code_path:CaFeeInvoiceStatusEnum.java:16'}
  FAILED: {trust: confirmed, label: 开票失败, evidence: 'code_path:CaFeeInvoiceStatusEnum.java:17'}
triage: keep
```
