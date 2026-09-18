---
type: dict
title: cust_person_info.company_type
page_key: cust_person_info__company_type
belong: dicts
status: draft
anchors: [cust_person_info.company_type]
sources: ['database_profile:cust_person_info.company_type']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [cust_person_info]
---

# cust_person_info.company_type

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `cust_person_info.company_type`，表页 [[tables/cust_person_info]]。

## 取值

```ground:dict
dict: cust_person_info__company_type
fields: [cust_person_info.company_type]
values:
  SUPPLIER: {trust: proposed}
  CORE: {trust: proposed}
  FINANCE: {trust: proposed}
  PROJECT_COMPANY: {trust: proposed}
  CORPORATION_COMPANY: {trust: proposed}
  PLATFORM_OPERATOR_COMPANY: {trust: proposed}
  DEALER: {trust: proposed}
  CORE_MANAGER: {trust: proposed}
  '["SUPPLIER"]': {trust: proposed}
triage: keep
```
