---
type: dict
title: tenant_project.enable
page_key: tenant_project__enable
belong: dicts
status: draft
anchors: [tenant_project.enable]
sources: ['database_profile:tenant_project.enable']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [tenant_project]
---

# tenant_project.enable

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `tenant_project.enable`，表页 [[tables/tenant_project]]。

## 取值

```ground:dict
dict: tenant_project__enable
fields: [tenant_project.enable]
values:
  Y: {trust: proposed}
triage: keep
```
