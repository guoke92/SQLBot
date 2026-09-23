---
type: dict
title: migratory_user_record.enable
page_key: migratory_user_record__enable
belong: dicts
status: draft
anchors: [migratory_user_record.enable]
sources: ['database_profile:migratory_user_record.enable', 'database_schema:migratory_user_record.enable']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [migratory_user_record]
---

# migratory_user_record.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `migratory_user_record.enable`，表页 [[tables/migratory_user_record]]。

## 取值

```ground:dict
dict: migratory_user_record__enable
fields: [migratory_user_record.enable]
values:
  Y: {trust: proposed, label: 启用}
  N: {trust: proposed, label: 停用, evidence: 'agent_review:binary_switch_pair'}
triage: keep
```
