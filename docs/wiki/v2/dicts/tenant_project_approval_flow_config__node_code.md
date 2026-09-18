---
type: dict
title: tenant_project_approval_flow_config.node_code
page_key: tenant_project_approval_flow_config__node_code
belong: dicts
status: draft
anchors: [tenant_project_approval_flow_config.node_code]
sources: ['database_profile:tenant_project_approval_flow_config.node_code']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [tenant_project_approval_flow_config]
---

# tenant_project_approval_flow_config.node_code

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `tenant_project_approval_flow_config.node_code`，表页 [[tables/tenant_project_approval_flow_config]]。

## 取值

```ground:dict
dict: tenant_project_approval_flow_config__node_code
fields: [tenant_project_approval_flow_config.node_code]
values:
  PROJECT_CONFIG: {trust: proposed}
  OTHER: {trust: proposed}
  PROJECT_MANAGER: {trust: proposed}
  OPERATION: {trust: proposed}
  BUSINESS_MANAGER: {trust: proposed}
  LEGAL_REVIEW: {trust: proposed}
  LEGAL_PROCESS: {trust: proposed}
triage: keep
```
