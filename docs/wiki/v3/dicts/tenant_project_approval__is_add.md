---
type: dict
title: tenant_project_approval.is_add
page_key: tenant_project_approval__is_add
belong: dicts
status: draft
anchors: [tenant_project_approval.is_add]
sources: ['database_profile:tenant_project_approval.is_add', 'database_schema:tenant_project_approval.is_add']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [tenant_project_approval]
---

# tenant_project_approval.is_add

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `tenant_project_approval.is_add`，表页 [[tables/tenant_project_approval]]。

## 取值

```ground:dict
dict: tenant_project_approval__is_add
fields: [tenant_project_approval.is_add]
values:
  Y: {trust: proposed, label: 是, evidence: 'database_schema:tenant_project_approval.is_add'}
  N: {trust: proposed, label: 否, evidence: 'database_schema:tenant_project_approval.is_add'}
triage: hold
needs_review: true
```
