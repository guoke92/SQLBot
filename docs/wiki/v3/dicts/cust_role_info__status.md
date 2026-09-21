---
type: dict
title: cust_role_info.status
page_key: cust_role_info__status
belong: dicts
status: draft
anchors: [cust_role_info.status]
sources: ['database_profile:cust_role_info.status', 'database_schema:cust_role_info.status',
  'code_path:CustRoleStatusConstant.java:11', 'code_path:CustRoleStatusConstant.java:13',
  'code_path:CustRoleStatusConstant.java:15', 'code_path:CustRoleStatusConstant.java:17']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_role_info]
---

# cust_role_info.status

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `cust_role_info.status`，表页 [[tables/cust_role_info]]。

## 取值

```ground:dict
dict: cust_role_info__status
fields: [cust_role_info.status]
values:
  ADD: {trust: confirmed, label: 未激活, evidence: 'code_path:CustRoleStatusConstant.java:11'}
  EFFECT: {trust: confirmed, label: 已激活, evidence: 'code_path:CustRoleStatusConstant.java:13'}
  WRITEOFF: {trust: confirmed, label: 注销, evidence: 'code_path:CustRoleStatusConstant.java:15'}
  FREEZE: {trust: confirmed, label: 冻结, evidence: 'code_path:CustRoleStatusConstant.java:17'}
triage: keep
```
