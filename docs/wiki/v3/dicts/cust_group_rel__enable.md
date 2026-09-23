---
type: dict
title: cust_group_rel.enable
page_key: cust_group_rel__enable
belong: dicts
status: draft
anchors: [cust_group_rel.enable]
sources: ['database_profile:cust_group_rel.enable', 'database_schema:cust_group_rel.enable']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [cust_group_rel]
---

# cust_group_rel.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `cust_group_rel.enable`，表页 [[tables/cust_group_rel]]。

## 取值

```ground:dict
dict: cust_group_rel__enable
fields: [cust_group_rel.enable]
values:
  Y: {trust: proposed, label: 启用}
  N: {trust: proposed, label: 停用, evidence: 'agent_review:binary_switch_pair'}
triage: keep
```
