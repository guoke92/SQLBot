---
type: dict
title: tenant_project.project_status
page_key: tenant_project__project_status
belong: dicts
status: draft
anchors: [tenant_project.project_status]
sources: ['database_profile:tenant_project.project_status']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [tenant_project]
---

# tenant_project.project_status

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `tenant_project.project_status`，表页 [[tables/tenant_project]]。

## 取值

```ground:dict
dict: tenant_project__project_status
fields: [tenant_project.project_status]
values:
  '1': {trust: proposed}
  '0': {trust: proposed}
  '2': {trust: proposed}
triage: keep
```
