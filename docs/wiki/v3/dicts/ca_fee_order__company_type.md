---
type: dict
title: ca_fee_order.company_type
page_key: ca_fee_order__company_type
belong: dicts
status: draft
anchors: [ca_fee_order.company_type]
sources: ['database_profile:ca_fee_order.company_type', 'database_schema:ca_fee_order.company_type',
  'code_path:CustCompanyTypeEnum.java:15', 'code_path:CustCompanyTypeEnum.java:18']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [ca_fee_order]
---

# ca_fee_order.company_type

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `ca_fee_order.company_type`，表页 [[tables/ca_fee_order]]。

## 取值

```ground:dict
dict: ca_fee_order__company_type
fields: [ca_fee_order.company_type]
values:
  SUPPLIER: {trust: confirmed, label: 供应商, evidence: 'code_path:CustCompanyTypeEnum.java:15'}
  CORE: {trust: confirmed, label: 核心企业, evidence: 'code_path:CustCompanyTypeEnum.java:18'}
  PROJECT_COMPANY: {trust: proposed}
triage: keep
```
