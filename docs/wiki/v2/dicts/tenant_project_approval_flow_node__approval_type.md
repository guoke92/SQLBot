---
type: dict
title: tenant_project_approval_flow_node.approval_type
page_key: tenant_project_approval_flow_node__approval_type
belong: dicts
status: draft
anchors: [tenant_project_approval_flow_node.approval_type]
sources: ['database_profile:tenant_project_approval_flow_node.approval_type']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [tenant_project_approval_flow_node]
---

# tenant_project_approval_flow_node.approval_type

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `tenant_project_approval_flow_node.approval_type`，表页 [[tables/tenant_project_approval_flow_node]]。

## 取值

```ground:dict
dict: tenant_project_approval_flow_node__approval_type
fields: [tenant_project_approval_flow_node.approval_type]
values:
  ONLINE_APPROVAL: {trust: proposed}
  BACK_AGREEMENT: {trust: proposed}
triage: keep
```
