---
type: dict
title: tenant_project.cover_operator
page_key: tenant_project__cover_operator
belong: dicts
status: draft
anchors: [tenant_project.cover_operator]
sources: ['database_profile:tenant_project.cover_operator']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [tenant_project]
---

# tenant_project.cover_operator

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `tenant_project.cover_operator`，表页 [[tables/tenant_project]]。

## 取值

```ground:dict
dict: tenant_project__cover_operator
fields: [tenant_project.cover_operator]
values:
  Y: {trust: proposed}
  N: {trust: proposed}
triage: hold
needs_review: true
```
