---
type: dict
title: wechat_project_approval_field_history.enable
page_key: wechat_project_approval_field_history__enable
belong: dicts
status: draft
anchors: [wechat_project_approval_field_history.enable]
sources: ['database_profile:wechat_project_approval_field_history.enable', 'database_schema:wechat_project_approval_field_history.enable']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [wechat_project_approval_field_history]
---

# wechat_project_approval_field_history.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `wechat_project_approval_field_history.enable`，表页 [[tables/wechat_project_approval_field_history]]。

## 取值

```ground:dict
dict: wechat_project_approval_field_history__enable
fields: [wechat_project_approval_field_history.enable]
values:
  Y: {trust: proposed, label: 启用}
  N: {trust: proposed, label: 停用, evidence: 'agent_review:binary_switch_pair'}
triage: keep
```
