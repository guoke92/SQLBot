---
type: dict
title: tenant_project_approval_flow_node.node_code
page_key: tenant_project_approval_flow_node__node_code
belong: dicts
status: draft
anchors: [tenant_project_approval_flow_node.node_code]
sources: ['database_profile:tenant_project_approval_flow_node.node_code', 'database_schema:tenant_project_approval_flow_node.node_code',
  'code_path:ProjectApprovalNodeCodeEnum.java:17', 'code_path:ProjectApprovalNodeCodeEnum.java:16',
  'code_path:ProjectApprovalNodeCodeEnum.java:20', 'code_path:ProjectApprovalNodeCodeEnum.java:21',
  'code_path:ProjectApprovalNodeCodeEnum.java:18', 'code_path:ProjectApprovalNodeCodeEnum.java:19']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [tenant_project_approval_flow_node]
---

# tenant_project_approval_flow_node.node_code

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `tenant_project_approval_flow_node.node_code`，表页 [[tables/tenant_project_approval_flow_node]]。

## 取值

```ground:dict
dict: tenant_project_approval_flow_node__node_code
fields: [tenant_project_approval_flow_node.node_code]
values:
  PROJECT_MANAGER: {trust: confirmed, label: 方案经理, evidence: 'code_path:ProjectApprovalNodeCodeEnum.java:17'}
  PROJECT_CONFIG: {trust: confirmed, label: 方案配置, evidence: 'code_path:ProjectApprovalNodeCodeEnum.java:16'}
  BUSINESS_MANAGER: {trust: confirmed, label: 业务经理审批, evidence: 'code_path:ProjectApprovalNodeCodeEnum.java:20'}
  OPERATION: {trust: confirmed, label: 运营审批, evidence: 'code_path:ProjectApprovalNodeCodeEnum.java:21'}
  LEGAL_PROCESS: {trust: confirmed, label: 法务经办, evidence: 'code_path:ProjectApprovalNodeCodeEnum.java:18'}
  LEGAL_REVIEW: {trust: confirmed, label: 法务复核, evidence: 'code_path:ProjectApprovalNodeCodeEnum.java:19'}
triage: keep
```
