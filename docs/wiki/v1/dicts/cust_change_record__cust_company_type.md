---
type: dict
title: cust_change_record.cust_company_type
page_key: cust_change_record__cust_company_type
belong: dicts
status: draft
anchors: [cust_change_record.cust_company_type]
sources: ['database_profile:cust_change_record.cust_company_type']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [cust_change_record]
---

# cust_change_record.cust_company_type

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `cust_change_record.cust_company_type`，表页 [[tables/cust_change_record]]。

## 取值

```ground:dict
dict: cust_change_record__cust_company_type
fields: [cust_change_record.cust_company_type]
values:
  SUPPLIER: {trust: proposed}
  CORE: {trust: proposed}
  FINANCE: {trust: proposed}
  PROJECT_COMPANY: {trust: proposed}
  CORPORATION_COMPANY: {trust: proposed}
  PLATFORM_OPERATOR_COMPANY: {trust: proposed}
  '["CORE","SUPPLIER"]': {trust: proposed}
  '["CORE"]': {trust: proposed}
  '["SUPPLIER"]': {trust: proposed}
  '["SUPPLIER","CORE"]': {trust: proposed}
  DEALER: {trust: proposed}
  CORE_MANAGER: {trust: proposed}
triage: keep
```
