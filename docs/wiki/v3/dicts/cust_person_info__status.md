---
type: dict
title: cust_person_info.status
page_key: cust_person_info__status
belong: dicts
status: draft
anchors: [cust_person_info.status]
sources: ['database_profile:cust_person_info.status', 'database_schema:cust_person_info.status',
  'code_path:CustPersonStatusConstant.java:11', 'code_path:CustPersonStatusConstant.java:13',
  'code_path:CustPersonStatusConstant.java:17', 'code_path:CustPersonStatusConstant.java:15']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_person_info]
---

# cust_person_info.status

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `cust_person_info.status`，表页 [[tables/cust_person_info]]。

## 取值

```ground:dict
dict: cust_person_info__status
fields: [cust_person_info.status]
values:
  ADD: {trust: confirmed, label: 未激活, evidence: 'code_path:CustPersonStatusConstant.java:11'}
  EFFECT: {trust: confirmed, label: 已激活, evidence: 'code_path:CustPersonStatusConstant.java:13'}
  FREEZE: {trust: confirmed, label: 冻结, evidence: 'code_path:CustPersonStatusConstant.java:17'}
  N: {trust: proposed}
  WRITEOFF: {trust: confirmed, label: 注销, evidence: 'code_path:CustPersonStatusConstant.java:15'}
triage: keep
```
