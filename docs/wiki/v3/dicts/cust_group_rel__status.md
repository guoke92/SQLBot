---
type: dict
title: cust_group_rel.status
page_key: cust_group_rel__status
belong: dicts
status: draft
anchors: [cust_group_rel.status]
sources: ['database_profile:cust_group_rel.status', 'database_schema:cust_group_rel.status',
  'code_path:CustGroupRelStatusEnum.java:20', 'code_path:CustGroupRelStatusEnum.java:19',
  'code_path:CustGroupRelStatusEnum.java:21']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_group_rel]
---

# cust_group_rel.status

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `cust_group_rel.status`，表页 [[tables/cust_group_rel]]。

## 取值

```ground:dict
dict: cust_group_rel__status
fields: [cust_group_rel.status]
values:
  EFFECTIVE: {trust: confirmed, label: 已生效, evidence: 'code_path:CustGroupRelStatusEnum.java:20'}
  INEFFECTIVE: {trust: confirmed, label: 未生效, evidence: 'code_path:CustGroupRelStatusEnum.java:19'}
  REJECTED: {trust: confirmed, label: 已拒绝, evidence: 'code_path:CustGroupRelStatusEnum.java:21'}
triage: keep
```
