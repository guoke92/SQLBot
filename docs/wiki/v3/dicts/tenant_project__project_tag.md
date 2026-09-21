---
type: dict
title: tenant_project.project_tag
page_key: tenant_project__project_tag
belong: dicts
status: draft
anchors: [tenant_project.project_tag]
sources: ['database_profile:tenant_project.project_tag']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [tenant_project]
---

# tenant_project.project_tag

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `tenant_project.project_tag`，表页 [[tables/tenant_project]]。

## 取值

```ground:dict
dict: tenant_project__project_tag
fields: [tenant_project.project_tag]
values:
  PRD: {trust: proposed}
  TEST: {trust: proposed}
triage: hold
needs_review: true
```
