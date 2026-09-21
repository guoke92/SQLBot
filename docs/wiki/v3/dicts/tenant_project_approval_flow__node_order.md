---
type: dict
title: tenant_project_approval_flow.node_order
page_key: tenant_project_approval_flow__node_order
belong: dicts
status: draft
anchors: [tenant_project_approval_flow.node_order]
sources: ['database_profile:tenant_project_approval_flow.node_order', 'database_schema:tenant_project_approval_flow.node_order']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [tenant_project_approval_flow]
---

# tenant_project_approval_flow.node_order

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `tenant_project_approval_flow.node_order`，表页 [[tables/tenant_project_approval_flow]]。

## 取值

```ground:dict
dict: tenant_project_approval_flow__node_order
fields: [tenant_project_approval_flow.node_order]
values:
  '1': {trust: proposed, label: 开始, evidence: 'database_schema:tenant_project_approval_flow.node_order'}
  '2': {trust: proposed}
  '3': {trust: proposed}
  '4': {trust: proposed}
  '5': {trust: proposed}
  '6': {trust: proposed}
triage: hold
needs_review: true
```
