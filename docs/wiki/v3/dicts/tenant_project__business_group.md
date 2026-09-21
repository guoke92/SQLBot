---
type: dict
title: tenant_project.business_group
page_key: tenant_project__business_group
belong: dicts
status: draft
anchors: [tenant_project.business_group]
sources: ['database_profile:tenant_project.business_group']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [tenant_project]
---

# tenant_project.business_group

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `tenant_project.business_group`，表页 [[tables/tenant_project]]。

## 取值

```ground:dict
dict: tenant_project__business_group
fields: [tenant_project.business_group]
values:
  部门a: {trust: proposed}
  '11': {trust: proposed}
triage: hold
needs_review: true
```
