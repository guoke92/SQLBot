---
type: dict
title: tenant_project_approval_flow_config.flow_code
page_key: tenant_project_approval_flow_config__flow_code
belong: dicts
status: draft
anchors: [tenant_project_approval_flow_config.flow_code]
sources: ['database_profile:tenant_project_approval_flow_config.flow_code', 'database_schema:tenant_project_approval_flow_config.flow_code',
  'code_path:ProjectApprovalFlowCodeEnum.java:18', 'code_path:ProjectApprovalFlowCodeEnum.java:17',
  'code_path:ProjectApprovalFlowCodeEnum.java:16']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [tenant_project_approval_flow_config]
---

# tenant_project_approval_flow_config.flow_code

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。 初审 hold：证据不足，保留待人工确认。
物理列 `tenant_project_approval_flow_config.flow_code`，表页 [[tables/tenant_project_approval_flow_config]]。

## 取值

```ground:dict
dict: tenant_project_approval_flow_config__flow_code
fields: [tenant_project_approval_flow_config.flow_code]
values:
  REGULAR: {trust: confirmed, label: 常规项目流程, evidence: 'code_path:ProjectApprovalFlowCodeEnum.java:18'}
  STANDARD: {trust: confirmed, label: 标准项目流程, evidence: 'code_path:ProjectApprovalFlowCodeEnum.java:17'}
  NO_ONLINE: {trust: confirmed, label: 无需上线审批, evidence: 'code_path:ProjectApprovalFlowCodeEnum.java:16'}
triage: hold
needs_review: true
```
