---
type: dict
title: cust_project_code_record.type
page_key: cust_project_code_record__type
belong: dicts
status: draft
anchors: [cust_project_code_record.type]
sources: ['database_profile:cust_project_code_record.type', 'database_schema:cust_project_code_record.type',
  'code_path:CustBuildTypeConstant.java:7']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_project_code_record]
---

# cust_project_code_record.type

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `cust_project_code_record.type`，表页 [[tables/cust_project_code_record]]。

## 取值

```ground:dict
dict: cust_project_code_record__type
fields: [cust_project_code_record.type]
values:
  PC_BUILD: {trust: confirmed, label: 客户录入, evidence: 'code_path:CustBuildTypeConstant.java:7'}
```
