---
type: enum
title: ca_fee_order_invoice_status
page_key: ca_fee_order_invoice_status
belong: enums
status: draft
aliases: []
anchors:
- ca_fee_order_invoice_status
sources:
- database_profile:ca_fee_order.invoice_status
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# ca_fee_order_invoice_status

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: ca_fee_order_invoice_status
fields:
- ca_fee_order.invoice_status
values:
  PENDING:
    confidence: proposed
  ISSUED:
    confidence: proposed
ambiguous: false
```
