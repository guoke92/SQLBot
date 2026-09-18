---
type: dict
title: cust_company_info.data_type
page_key: cust_company_info__data_type
belong: dicts
status: draft
anchors: [cust_company_info.data_type]
sources: ['database_profile:cust_company_info.data_type', 'database_schema:cust_company_info.data_type',
  'code_path:CustDataTypeConstant.java:12', 'code_path:CustDataTypeConstant.java:14',
  'code_path:CustDataTypeConstant.java:16']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_company_info]
---

# cust_company_info.data_type

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `cust_company_info.data_type`，表页 [[tables/cust_company_info]]。

## 取值

```ground:dict
dict: cust_company_info__data_type
fields: [cust_company_info.data_type]
values:
  '1': {trust: confirmed, label: 主数据, evidence: 'code_path:CustDataTypeConstant.java:12'}
  '0': {trust: confirmed, label: 流程数据, evidence: 'code_path:CustDataTypeConstant.java:14'}
  '2': {trust: confirmed, label: 编辑过程, evidence: 'code_path:CustDataTypeConstant.java:16'}
triage: keep
```
