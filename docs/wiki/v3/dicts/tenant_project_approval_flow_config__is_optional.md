---
type: dict
title: tenant_project_approval_flow_config.is_optional
page_key: tenant_project_approval_flow_config__is_optional
belong: dicts
status: draft
anchors: [tenant_project_approval_flow_config.is_optional]
sources: ['database_profile:tenant_project_approval_flow_config.is_optional', 'database_schema:tenant_project_approval_flow_config.is_optional']
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
related: [tenant_project_approval_flow_config]
---

# tenant_project_approval_flow_config.is_optional

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `tenant_project_approval_flow_config.is_optional`，表页 [[tables/tenant_project_approval_flow_config]]。

## 取值

```ground:dict
dict: tenant_project_approval_flow_config__is_optional
fields: [tenant_project_approval_flow_config.is_optional]
values:
  N: {trust: proposed, label: 否}
  Y: {trust: proposed, label: 是}
triage: keep
```
