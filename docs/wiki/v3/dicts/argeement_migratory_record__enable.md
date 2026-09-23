---
type: dict
title: argeement_migratory_record.enable
page_key: argeement_migratory_record__enable
belong: dicts
status: draft
anchors: [argeement_migratory_record.enable]
sources: ['database_profile:argeement_migratory_record.enable', 'database_schema:argeement_migratory_record.enable']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [argeement_migratory_record]
---

# argeement_migratory_record.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `argeement_migratory_record.enable`，表页 [[tables/argeement_migratory_record]]。

## 取值

```ground:dict
dict: argeement_migratory_record__enable
fields: [argeement_migratory_record.enable]
values:
  Y: {trust: proposed, label: 启用}
  N: {trust: proposed, label: 停用, evidence: 'agent_review:binary_switch_pair'}
triage: keep
```
