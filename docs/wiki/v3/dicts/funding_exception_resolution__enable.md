---
type: dict
title: funding_exception_resolution.enable
page_key: funding_exception_resolution__enable
belong: dicts
status: draft
anchors: [funding_exception_resolution.enable]
sources: ['database_profile:funding_exception_resolution.enable', 'database_schema:funding_exception_resolution.enable']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [funding_exception_resolution]
---

# funding_exception_resolution.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `funding_exception_resolution.enable`，表页 [[tables/funding_exception_resolution]]。

## 取值

```ground:dict
dict: funding_exception_resolution__enable
fields: [funding_exception_resolution.enable]
values:
  Y: {trust: proposed, label: 启用}
  N: {trust: proposed, label: 停用, evidence: 'agent_review:binary_switch_pair'}
triage: keep
```
