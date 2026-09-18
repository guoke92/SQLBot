---
type: dict
title: tenant_project.config_model
page_key: tenant_project__config_model
belong: dicts
status: draft
anchors: [tenant_project.config_model]
sources: ['database_profile:tenant_project.config_model']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [tenant_project]
---

# tenant_project.config_model

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `tenant_project.config_model`，表页 [[tables/tenant_project]]。

## 取值

```ground:dict
dict: tenant_project__config_model
fields: [tenant_project.config_model]
values:
  admin: {trust: proposed}
  normal: {trust: proposed}
triage: keep
```
