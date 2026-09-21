---
type: dict
title: cust_group_rel.status
page_key: cust_group_rel__status
belong: dicts
status: draft
anchors: [cust_group_rel.status]
sources: ['database_profile:cust_group_rel.status', 'database_schema:cust_group_rel.status']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [cust_group_rel]
---

# cust_group_rel.status

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `cust_group_rel.status`，表页 [[tables/cust_group_rel]]。

## 取值

```ground:dict
dict: cust_group_rel__status
fields: [cust_group_rel.status]
values:
  EFFECTIVE: {trust: proposed, label: 已生效, evidence: 'database_schema:cust_group_rel.status'}
  INEFFECTIVE: {trust: proposed, label: 未生效, evidence: 'database_schema:cust_group_rel.status'}
  REJECTED: {trust: proposed, label: 已拒绝, evidence: 'database_schema:cust_group_rel.status'}
triage: keep
```
