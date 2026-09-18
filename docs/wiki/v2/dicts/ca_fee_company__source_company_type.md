---
type: dict
title: ca_fee_company.source_company_type
page_key: ca_fee_company__source_company_type
belong: dicts
status: draft
anchors: [ca_fee_company.source_company_type]
sources: ['database_profile:ca_fee_company.source_company_type']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [ca_fee_company]
---

# ca_fee_company.source_company_type

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `ca_fee_company.source_company_type`，表页 [[tables/ca_fee_company]]。

## 取值

```ground:dict
dict: ca_fee_company__source_company_type
fields: [ca_fee_company.source_company_type]
values:
  SUPPLIER: {trust: proposed}
  CORE: {trust: proposed}
  PROJECT_COMPANY: {trust: proposed}
triage: keep
```
