---
type: dict
title: cust_project_pushcust.enable
page_key: cust_project_pushcust__enable
belong: dicts
status: draft
anchors: [cust_project_pushcust.enable]
sources: ['database_profile:cust_project_pushcust.enable', 'database_schema:cust_project_pushcust.enable']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [cust_project_pushcust]
---

# cust_project_pushcust.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `cust_project_pushcust.enable`，表页 [[tables/cust_project_pushcust]]。

## 取值

```ground:dict
dict: cust_project_pushcust__enable
fields: [cust_project_pushcust.enable]
values:
  Y: {trust: proposed, label: 启用}
  N: {trust: proposed, label: 停用, evidence: 'agent_review:binary_switch_pair'}
triage: keep
```
