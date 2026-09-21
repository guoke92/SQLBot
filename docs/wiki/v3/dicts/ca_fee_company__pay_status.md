---
type: dict
title: ca_fee_company.pay_status
page_key: ca_fee_company__pay_status
belong: dicts
status: draft
anchors: [ca_fee_company.pay_status]
sources: ['database_profile:ca_fee_company.pay_status', 'database_schema:ca_fee_company.pay_status',
  'code_path:CaFeeCompanyPayStatusEnum.java:16', 'code_path:CaFeeCompanyPayStatusEnum.java:15']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [ca_fee_company]
---

# ca_fee_company.pay_status

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `ca_fee_company.pay_status`，表页 [[tables/ca_fee_company]]。

## 取值

```ground:dict
dict: ca_fee_company__pay_status
fields: [ca_fee_company.pay_status]
values:
  UNPAID: {trust: confirmed, label: 未缴费, evidence: 'code_path:CaFeeCompanyPayStatusEnum.java:16'}
  PAID: {trust: confirmed, label: 已缴费, evidence: 'code_path:CaFeeCompanyPayStatusEnum.java:15'}
triage: keep
```
