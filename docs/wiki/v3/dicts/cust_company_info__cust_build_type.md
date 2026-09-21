---
type: dict
title: cust_company_info.cust_build_type
page_key: cust_company_info__cust_build_type
belong: dicts
status: draft
anchors: [cust_company_info.cust_build_type]
sources: ['database_profile:cust_company_info.cust_build_type', 'database_schema:cust_company_info.cust_build_type',
  'code_path:CustBuildTypeConstant.java:12', 'code_path:CustBuildTypeConstant.java:7']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_company_info]
---

# cust_company_info.cust_build_type

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `cust_company_info.cust_build_type`，表页 [[tables/cust_company_info]]。

## 取值

```ground:dict
dict: cust_company_info__cust_build_type
fields: [cust_company_info.cust_build_type]
values:
  AGW_BUILD: {trust: confirmed, label: 平台录入, evidence: 'code_path:CustBuildTypeConstant.java:12'}
  PC_BUILD: {trust: confirmed, label: 客户录入, evidence: 'code_path:CustBuildTypeConstant.java:7'}
  SIMPLE: {trust: proposed}
triage: keep
```
