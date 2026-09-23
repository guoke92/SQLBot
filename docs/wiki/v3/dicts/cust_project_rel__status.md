---
type: dict
title: cust_project_rel.status
page_key: cust_project_rel__status
belong: dicts
status: draft
anchors: [cust_project_rel.status]
sources: ['database_profile:cust_project_rel.status', 'database_schema:cust_project_rel.status']
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
related: [cust_project_rel]
---

# cust_project_rel.status

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `cust_project_rel.status`，表页 [[tables/cust_project_rel]]。

## 取值

```ground:dict
dict: cust_project_rel__status
fields: [cust_project_rel.status]
values:
  '1': {trust: proposed, label: 是}
  '0': {trust: proposed, label: 否}
triage: keep
```
