---
type: dict
title: tenant_project_approval.project_type
page_key: tenant_project_approval__project_type
belong: dicts
status: draft
anchors: [tenant_project_approval.project_type]
sources: ['database_profile:tenant_project_approval.project_type', 'database_schema:tenant_project_approval.project_type']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [tenant_project_approval]
---

# tenant_project_approval.project_type

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `tenant_project_approval.project_type`，表页 [[tables/tenant_project_approval]]。

## 取值

```ground:dict
dict: tenant_project_approval__project_type
fields: [tenant_project_approval.project_type]
values:
  STANDARD: {trust: proposed, label: 标准, evidence: 'database_schema:tenant_project_approval.project_type'}
  REGULAR: {trust: proposed, label: 常规, evidence: 'database_schema:tenant_project_approval.project_type'}
triage: keep
```
