---
type: dict
title: cust_project_rel.company_type
page_key: cust_project_rel__company_type
belong: dicts
status: draft
anchors: [cust_project_rel.company_type]
sources: ['database_profile:cust_project_rel.company_type']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [cust_project_rel]
---

# cust_project_rel.company_type

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `cust_project_rel.company_type`，表页 [[tables/cust_project_rel]]。

## 取值

```ground:dict
dict: cust_project_rel__company_type
fields: [cust_project_rel.company_type]
values:
  SUPPLIER: {trust: proposed}
  CORE: {trust: proposed}
  FINANCE: {trust: proposed}
  PROJECT_COMPANY: {trust: proposed}
  CORPORATION_COMPANY: {trust: proposed}
  PLATFORM_OPERATOR_COMPANY: {trust: proposed}
  DEALER: {trust: proposed}
  CORE_MANAGER: {trust: proposed}
  PLATFORM_OPREATOR_COMPANY: {trust: proposed}
triage: keep
```
