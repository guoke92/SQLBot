---
type: dict
title: short_link.is_forever
page_key: short_link__is_forever
belong: dicts
status: draft
anchors: [short_link.is_forever]
sources: ['database_profile:short_link.is_forever', 'database_schema:short_link.is_forever']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [short_link]
---

# short_link.is_forever

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `short_link.is_forever`，表页 [[tables/short_link]]。

## 取值

```ground:dict
dict: short_link__is_forever
fields: [short_link.is_forever]
values:
  Y: {trust: proposed, label: 是}
  N: {trust: proposed, label: 否, evidence: 'agent_review:binary_switch_pair'}
triage: keep
```
