---
type: dict
title: tenant_project_approval_flow_node.approval_type
page_key: tenant_project_approval_flow_node__approval_type
belong: dicts
status: draft
anchors: [tenant_project_approval_flow_node.approval_type]
sources: ['database_profile:tenant_project_approval_flow_node.approval_type', 'database_schema:tenant_project_approval_flow_node.approval_type',
  'code_path:ProjectApprovalTypeEnum.java:12', 'code_path:ProjectApprovalTypeEnum.java:13']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [tenant_project_approval_flow_node]
---

# tenant_project_approval_flow_node.approval_type

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `tenant_project_approval_flow_node.approval_type`，表页 [[tables/tenant_project_approval_flow_node]]。

## 取值

```ground:dict
dict: tenant_project_approval_flow_node__approval_type
fields: [tenant_project_approval_flow_node.approval_type]
values:
  ONLINE_APPROVAL: {trust: confirmed, label: 项目上线审批, evidence: 'code_path:ProjectApprovalTypeEnum.java:12'}
  BACK_AGREEMENT: {trust: confirmed, label: 后补合作协议, evidence: 'code_path:ProjectApprovalTypeEnum.java:13'}
triage: keep
```
