---
type: dict
title: tenant_project_approval_flow.node_status
page_key: tenant_project_approval_flow__node_status
belong: dicts
status: draft
anchors: [tenant_project_approval_flow.node_status]
sources: ['database_profile:tenant_project_approval_flow.node_status', 'database_schema:tenant_project_approval_flow.node_status',
  'code_path:ProjectApprovalNodeStatusEnum.java:16', 'code_path:ProjectApprovalNodeStatusEnum.java:18',
  'code_path:ProjectApprovalNodeStatusEnum.java:17', 'code_path:ProjectApprovalNodeStatusEnum.java:19']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [tenant_project_approval_flow]
---

# tenant_project_approval_flow.node_status

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `tenant_project_approval_flow.node_status`，表页 [[tables/tenant_project_approval_flow]]。

## 取值

```ground:dict
dict: tenant_project_approval_flow__node_status
fields: [tenant_project_approval_flow.node_status]
values:
  PENDING: {trust: confirmed, label: 待审批, evidence: 'code_path:ProjectApprovalNodeStatusEnum.java:16'}
  APPROVED: {trust: confirmed, label: 已通过, evidence: 'code_path:ProjectApprovalNodeStatusEnum.java:18'}
  APPROVING: {trust: confirmed, label: 审批中, evidence: 'code_path:ProjectApprovalNodeStatusEnum.java:17'}
  REJECTED: {trust: confirmed, label: 已拒绝, evidence: 'code_path:ProjectApprovalNodeStatusEnum.java:19'}
triage: keep
```
