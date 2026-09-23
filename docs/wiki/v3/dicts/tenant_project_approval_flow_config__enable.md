---
type: dict
title: tenant_project_approval_flow_config.enable
page_key: tenant_project_approval_flow_config__enable
belong: dicts
status: draft
anchors: [tenant_project_approval_flow_config.enable]
sources: ['database_profile:tenant_project_approval_flow_config.enable', 'database_schema:tenant_project_approval_flow_config.enable']
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
related: [tenant_project_approval_flow_config]
---

# tenant_project_approval_flow_config.enable

L0 字典候选：label 仅来自列注释解析（proposed）；无映射则省略。空值已丢弃。
物理列 `tenant_project_approval_flow_config.enable`，表页 [[tables/tenant_project_approval_flow_config]]。

## 取值

```ground:dict
dict: tenant_project_approval_flow_config__enable
fields: [tenant_project_approval_flow_config.enable]
values:
  Y: {trust: proposed, label: 启用}
  N: {trust: proposed, label: 停用}
triage: keep
```
