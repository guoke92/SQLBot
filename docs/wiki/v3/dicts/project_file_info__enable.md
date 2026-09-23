---
type: dict
title: project_file_info.enable
page_key: project_file_info__enable
belong: dicts
status: draft
anchors: [project_file_info.enable]
sources: ['database_profile:project_file_info.enable', 'database_schema:project_file_info.enable']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [project_file_info]
---

# project_file_info.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `project_file_info.enable`，表页 [[tables/project_file_info]]。

## 取值

```ground:dict
dict: project_file_info__enable
fields: [project_file_info.enable]
values:
  Y: {trust: proposed, label: 启用}
  N: {trust: proposed, label: 停用, evidence: 'agent_review:binary_switch_pair'}
triage: keep
```
