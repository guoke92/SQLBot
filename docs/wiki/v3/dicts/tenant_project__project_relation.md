---
type: dict
title: tenant_project.project_relation
page_key: tenant_project__project_relation
belong: dicts
status: draft
anchors: [tenant_project.project_relation]
sources: ['database_profile:tenant_project.project_relation']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [tenant_project]
---

# tenant_project.project_relation

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `tenant_project.project_relation`，表页 [[tables/tenant_project]]。

## 取值

```ground:dict
dict: tenant_project__project_relation
fields: [tenant_project.project_relation]
values:
  '111': {trust: proposed}
  '1111': {trust: proposed}
triage: hold
needs_review: true
```
