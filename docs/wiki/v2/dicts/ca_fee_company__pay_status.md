---
type: dict
title: ca_fee_company.pay_status
page_key: ca_fee_company__pay_status
belong: dicts
status: draft
anchors: [ca_fee_company.pay_status]
sources: ['database_profile:ca_fee_company.pay_status', 'database_schema:ca_fee_company.pay_status']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [ca_fee_company]
---

# ca_fee_company.pay_status

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `ca_fee_company.pay_status`，表页 [[tables/ca_fee_company]]。

## 取值

```ground:dict
dict: ca_fee_company__pay_status
fields: [ca_fee_company.pay_status]
values:
  UNPAID: {trust: proposed, label: 未缴费, evidence: 'database_schema:ca_fee_company.pay_status'}
  PAID: {trust: proposed, label: 已缴费, evidence: 'database_schema:ca_fee_company.pay_status'}
triage: keep
```
