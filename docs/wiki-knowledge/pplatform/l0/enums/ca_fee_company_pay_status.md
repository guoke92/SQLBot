---
type: enum
title: ca_fee_company_pay_status
page_key: ca_fee_company_pay_status
belong: enums
status: draft
aliases: []
anchors:
- ca_fee_company_pay_status
sources:
- database_profile:ca_fee_company.pay_status
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# ca_fee_company_pay_status

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: ca_fee_company_pay_status
fields:
- ca_fee_company.pay_status
values:
  UNPAID:
    confidence: proposed
  PAID:
    confidence: proposed
ambiguous: false
```
