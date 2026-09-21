---
type: dict
title: tenant_project_approval_flow.node_status
page_key: tenant_project_approval_flow__node_status
belong: dicts
status: draft
anchors: [tenant_project_approval_flow.node_status]
sources: ['database_profile:tenant_project_approval_flow.node_status']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [tenant_project_approval_flow]
---

# tenant_project_approval_flow.node_status

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `tenant_project_approval_flow.node_status`，表页 [[tables/tenant_project_approval_flow]]。

## 取值

```ground:dict
dict: tenant_project_approval_flow__node_status
fields: [tenant_project_approval_flow.node_status]
values:
  PENDING: {trust: proposed}
  APPROVED: {trust: proposed}
  APPROVING: {trust: proposed}
  REJECTED: {trust: proposed}
triage: keep
```
