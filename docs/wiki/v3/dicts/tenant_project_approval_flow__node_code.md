---
type: dict
title: tenant_project_approval_flow.node_code
page_key: tenant_project_approval_flow__node_code
belong: dicts
status: draft
anchors: [tenant_project_approval_flow.node_code]
sources: ['database_profile:tenant_project_approval_flow.node_code', 'database_schema:tenant_project_approval_flow.node_code',
  'code_path:ProjectApprovalNodeCodeEnum.java:17', 'code_path:ProjectApprovalNodeCodeEnum.java:20',
  'code_path:ProjectApprovalNodeCodeEnum.java:21', 'code_path:ProjectApprovalNodeCodeEnum.java:16',
  'code_path:ProjectApprovalNodeCodeEnum.java:18', 'code_path:ProjectApprovalNodeCodeEnum.java:19',
  'code_path:ProjectApprovalNodeCodeEnum.java:22', 'code_path:ProjectApprovalNodeCodeEnum.java:23']
created: '2026-09-23'
updated: '2026-09-23'
contract_version: '0.1'
related: [tenant_project_approval_flow]
---

# tenant_project_approval_flow.node_code

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `tenant_project_approval_flow.node_code`，表页 [[tables/tenant_project_approval_flow]]。

## 取值

```ground:dict
dict: tenant_project_approval_flow__node_code
fields: [tenant_project_approval_flow.node_code]
values:
  PROJECT_MANAGER: {trust: confirmed, label: 方案经理, evidence: 'code_path:ProjectApprovalNodeCodeEnum.java:17'}
  BUSINESS_MANAGER: {trust: confirmed, label: 业务经理审批, evidence: 'code_path:ProjectApprovalNodeCodeEnum.java:20'}
  OPERATION: {trust: confirmed, label: 运营审批, evidence: 'code_path:ProjectApprovalNodeCodeEnum.java:21'}
  PROJECT_CONFIG: {trust: confirmed, label: 方案配置, evidence: 'code_path:ProjectApprovalNodeCodeEnum.java:16'}
  LEGAL_PROCESS: {trust: confirmed, label: 法务经办, evidence: 'code_path:ProjectApprovalNodeCodeEnum.java:18'}
  LEGAL_REVIEW: {trust: confirmed, label: 法务复核, evidence: 'code_path:ProjectApprovalNodeCodeEnum.java:19'}
  OTHER: {trust: confirmed, label: 其他, evidence: 'code_path:ProjectApprovalNodeCodeEnum.java:22'}
  SUPPLEMENT_AGREEMENT: {trust: confirmed, label: 补充协议, evidence: 'code_path:ProjectApprovalNodeCodeEnum.java:23'}
triage: keep
```
