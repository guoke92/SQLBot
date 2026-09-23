---
type: dict
title: short_link.enable
page_key: short_link__enable
belong: dicts
status: draft
anchors: [short_link.enable]
sources: ['database_profile:short_link.enable', 'database_schema:short_link.enable']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [short_link]
---

# short_link.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `short_link.enable`，表页 [[tables/short_link]]。

## 取值

```ground:dict
dict: short_link__enable
fields: [short_link.enable]
values:
  Y: {trust: proposed, label: 启用}
  N: {trust: proposed, label: 停用, evidence: 'agent_review:binary_switch_pair'}
triage: keep
```
