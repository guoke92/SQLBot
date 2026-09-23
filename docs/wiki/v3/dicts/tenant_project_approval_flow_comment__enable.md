---
type: dict
title: tenant_project_approval_flow_comment.enable
page_key: tenant_project_approval_flow_comment__enable
belong: dicts
status: draft
anchors: [tenant_project_approval_flow_comment.enable]
sources: ['database_profile:tenant_project_approval_flow_comment.enable', 'database_schema:tenant_project_approval_flow_comment.enable']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [tenant_project_approval_flow_comment]
---

# tenant_project_approval_flow_comment.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `tenant_project_approval_flow_comment.enable`，表页 [[tables/tenant_project_approval_flow_comment]]。

## 取值

```ground:dict
dict: tenant_project_approval_flow_comment__enable
fields: [tenant_project_approval_flow_comment.enable]
values:
  Y: {trust: proposed, label: 启用}
  N: {trust: proposed, label: 停用, evidence: 'agent_review:binary_switch_pair'}
triage: keep
```
