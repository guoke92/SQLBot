---
type: dict
title: cust_company_lifecycle_info.type
page_key: cust_company_lifecycle_info__type
belong: dicts
status: draft
anchors: [cust_company_lifecycle_info.type]
sources: ['database_profile:cust_company_lifecycle_info.type']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [cust_company_lifecycle_info]
---

# cust_company_lifecycle_info.type

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `cust_company_lifecycle_info.type`，表页 [[tables/cust_company_lifecycle_info]]。

## 取值

```ground:dict
dict: cust_company_lifecycle_info__type
fields: [cust_company_lifecycle_info.type]
values:
  FRZ: {trust: proposed}
  UNFRZ: {trust: proposed}
triage: keep
```
