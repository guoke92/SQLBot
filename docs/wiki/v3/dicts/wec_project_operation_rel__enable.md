---
type: dict
title: wec_project_operation_rel.enable
page_key: wec_project_operation_rel__enable
belong: dicts
status: draft
anchors: [wec_project_operation_rel.enable]
sources: ['database_profile:wec_project_operation_rel.enable', 'database_schema:wec_project_operation_rel.enable']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [wec_project_operation_rel]
---

# wec_project_operation_rel.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `wec_project_operation_rel.enable`，表页 [[tables/wec_project_operation_rel]]。

## 取值

```ground:dict
dict: wec_project_operation_rel__enable
fields: [wec_project_operation_rel.enable]
values:
  Y: {trust: proposed, label: 启用}
  N: {trust: proposed, label: 停用, evidence: 'agent_review:binary_switch_pair'}
triage: keep
```
