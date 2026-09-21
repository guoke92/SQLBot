---
type: dict
title: tenant_project_approval.simple_mode
page_key: tenant_project_approval__simple_mode
belong: dicts
status: draft
anchors: [tenant_project_approval.simple_mode]
sources: ['database_profile:tenant_project_approval.simple_mode']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [tenant_project_approval]
---

# tenant_project_approval.simple_mode

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `tenant_project_approval.simple_mode`，表页 [[tables/tenant_project_approval]]。

## 取值

```ground:dict
dict: tenant_project_approval__simple_mode
fields: [tenant_project_approval.simple_mode]
values:
  N: {trust: proposed}
  Y: {trust: proposed}
triage: hold
needs_review: true
```
