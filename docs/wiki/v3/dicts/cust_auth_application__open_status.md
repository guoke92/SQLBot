---
type: dict
title: cust_auth_application.open_status
page_key: cust_auth_application__open_status
belong: dicts
status: draft
anchors: [cust_auth_application.open_status]
sources: ['database_profile:cust_auth_application.open_status', 'database_schema:cust_auth_application.open_status',
  'code_path:CustProductActiveConstant.java:13', 'code_path:CustProductActiveConstant.java:15',
  'code_path:CustProductActiveConstant.java:11']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_auth_application]
---

# cust_auth_application.open_status

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `cust_auth_application.open_status`，表页 [[tables/cust_auth_application]]。

## 取值

```ground:dict
dict: cust_auth_application__open_status
fields: [cust_auth_application.open_status]
values:
  OPENING: {trust: confirmed, label: 开通中, evidence: 'code_path:CustProductActiveConstant.java:13'}
  OPENED: {trust: confirmed, label: 已开通, evidence: 'code_path:CustProductActiveConstant.java:15'}
  NOT_OPENED: {trust: confirmed, label: 未开通, evidence: 'code_path:CustProductActiveConstant.java:11'}
triage: keep
```
