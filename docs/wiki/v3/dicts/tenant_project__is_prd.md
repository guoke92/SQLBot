---
type: dict
title: tenant_project.is_prd
page_key: tenant_project__is_prd
belong: dicts
status: draft
anchors: [tenant_project.is_prd]
sources: ['database_profile:tenant_project.is_prd', 'database_schema:tenant_project.is_prd']
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
related: [tenant_project]
---

# tenant_project.is_prd

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `tenant_project.is_prd`，表页 [[tables/tenant_project]]。

## 取值

```ground:dict
dict: tenant_project__is_prd
fields: [tenant_project.is_prd]
values:
  Y: {trust: proposed, label: 是}
  N: {trust: proposed, label: 否}
triage: keep
```
