---
type: dict
title: cust_group_rel.root_flag
page_key: cust_group_rel__root_flag
belong: dicts
status: draft
anchors: [cust_group_rel.root_flag]
sources: ['database_profile:cust_group_rel.root_flag', 'database_schema:cust_group_rel.root_flag']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [cust_group_rel]
---

# cust_group_rel.root_flag

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `cust_group_rel.root_flag`，表页 [[tables/cust_group_rel]]。

## 取值

```ground:dict
dict: cust_group_rel__root_flag
fields: [cust_group_rel.root_flag]
values:
  N: {trust: proposed, label: 不是, evidence: 'database_schema:cust_group_rel.root_flag'}
  Y: {trust: proposed, label: 是, evidence: 'database_schema:cust_group_rel.root_flag'}
triage: keep
```
