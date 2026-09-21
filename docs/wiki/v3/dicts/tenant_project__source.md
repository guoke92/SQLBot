---
type: dict
title: tenant_project.source
page_key: tenant_project__source
belong: dicts
status: draft
anchors: [tenant_project.source]
sources: ['database_profile:tenant_project.source']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [tenant_project]
---

# tenant_project.source

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `tenant_project.source`，表页 [[tables/tenant_project]]。

## 取值

```ground:dict
dict: tenant_project__source
fields: [tenant_project.source]
values:
  pplatform: {trust: proposed}
  ACFLOW: {trust: proposed}
  RVSFACTOR_PC: {trust: proposed}
  ORDER: {trust: proposed}
  STORAGE: {trust: proposed}
triage: hold
needs_review: true
```
