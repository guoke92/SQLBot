---
type: dict
title: funding_rule_info.enable
page_key: funding_rule_info__enable
belong: dicts
status: draft
anchors: [funding_rule_info.enable]
sources: ['database_profile:funding_rule_info.enable', 'database_schema:funding_rule_info.enable']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [funding_rule_info]
---

# funding_rule_info.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `funding_rule_info.enable`，表页 [[tables/funding_rule_info]]。

## 取值

```ground:dict
dict: funding_rule_info__enable
fields: [funding_rule_info.enable]
values:
  Y: {trust: proposed, label: 启用}
  N: {trust: proposed, label: 停用, evidence: 'agent_review:binary_switch_pair'}
triage: keep
```
