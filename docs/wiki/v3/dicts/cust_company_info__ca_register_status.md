---
type: dict
title: cust_company_info.ca_register_status
page_key: cust_company_info__ca_register_status
belong: dicts
status: draft
anchors: [cust_company_info.ca_register_status]
sources: ['database_profile:cust_company_info.ca_register_status', 'database_schema:cust_company_info.ca_register_status',
  'code_path:OpenStatus.java:20']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_company_info]
---

# cust_company_info.ca_register_status

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `cust_company_info.ca_register_status`，表页 [[tables/cust_company_info]]。

## 取值

```ground:dict
dict: cust_company_info__ca_register_status
fields: [cust_company_info.ca_register_status]
values:
  N: {trust: confirmed, label: 未开通, evidence: 'code_path:OpenStatus.java:20'}
  Y: {trust: confirmed, label: 已开通, evidence: 'code_path:OpenStatus.java:20'}
  P: {trust: confirmed, label: 开通中, evidence: 'code_path:OpenStatus.java:20'}
triage: keep
```
