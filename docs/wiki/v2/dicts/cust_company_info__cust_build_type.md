---
type: dict
title: cust_company_info.cust_build_type
page_key: cust_company_info__cust_build_type
belong: dicts
status: draft
anchors: [cust_company_info.cust_build_type]
sources: ['database_profile:cust_company_info.cust_build_type']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [cust_company_info]
---

# cust_company_info.cust_build_type

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `cust_company_info.cust_build_type`，表页 [[tables/cust_company_info]]。

## 取值

```ground:dict
dict: cust_company_info__cust_build_type
fields: [cust_company_info.cust_build_type]
values:
  AGW_BUILD: {trust: proposed}
  PC_BUILD: {trust: proposed}
  SIMPLE: {trust: proposed}
triage: keep
```
