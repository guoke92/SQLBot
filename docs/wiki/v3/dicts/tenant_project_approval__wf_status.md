---
type: dict
title: tenant_project_approval.wf_status
page_key: tenant_project_approval__wf_status
belong: dicts
status: draft
anchors: [tenant_project_approval.wf_status]
sources: ['database_profile:tenant_project_approval.wf_status', 'database_schema:tenant_project_approval.wf_status',
  'code_path:ProjectApprovalWorkflowStatusEnum.java:17', 'code_path:ProjectApprovalWorkflowStatusEnum.java:18',
  'code_path:ProjectApprovalWorkflowStatusEnum.java:19', 'code_path:ProjectApprovalWorkflowStatusEnum.java:16']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [tenant_project_approval]
---

# tenant_project_approval.wf_status

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `tenant_project_approval.wf_status`，表页 [[tables/tenant_project_approval]]。

## 取值

```ground:dict
dict: tenant_project_approval__wf_status
fields: [tenant_project_approval.wf_status]
values:
  RUNNING: {trust: confirmed, label: 审批中, evidence: 'code_path:ProjectApprovalWorkflowStatusEnum.java:17'}
  FINISHED: {trust: confirmed, label: 审批通过, evidence: 'code_path:ProjectApprovalWorkflowStatusEnum.java:18'}
  TERMINATED: {trust: confirmed, label: 审批拒绝, evidence: 'code_path:ProjectApprovalWorkflowStatusEnum.java:19'}
  PENDING: {trust: confirmed, label: 待发起, evidence: 'code_path:ProjectApprovalWorkflowStatusEnum.java:16'}
  REVOKED: {trust: proposed}
triage: keep
```
