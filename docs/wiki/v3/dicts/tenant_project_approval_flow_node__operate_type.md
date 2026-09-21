---
type: dict
title: tenant_project_approval_flow_node.operate_type
page_key: tenant_project_approval_flow_node__operate_type
belong: dicts
status: draft
anchors: [tenant_project_approval_flow_node.operate_type]
sources: ['database_profile:tenant_project_approval_flow_node.operate_type', 'database_schema:tenant_project_approval_flow_node.operate_type',
  'code_path:ProjectApprovalOperateTypeEnum.java:16', 'code_path:ProjectApprovalOperateTypeEnum.java:18',
  'code_path:ProjectApprovalOperateTypeEnum.java:17', 'code_path:ProjectApprovalOperateTypeEnum.java:19',
  'code_path:ProjectApprovalOperateTypeEnum.java:20']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [tenant_project_approval_flow_node]
---

# tenant_project_approval_flow_node.operate_type

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `tenant_project_approval_flow_node.operate_type`，表页 [[tables/tenant_project_approval_flow_node]]。

## 取值

```ground:dict
dict: tenant_project_approval_flow_node__operate_type
fields: [tenant_project_approval_flow_node.operate_type]
values:
  pass: {trust: confirmed, label: 同意, evidence: 'code_path:ProjectApprovalOperateTypeEnum.java:16'}
  back: {trust: confirmed, label: 退回, evidence: 'code_path:ProjectApprovalOperateTypeEnum.java:18'}
  reject: {trust: confirmed, label: 驳回, evidence: 'code_path:ProjectApprovalOperateTypeEnum.java:17'}
  delegate: {trust: confirmed, label: 转审, evidence: 'code_path:ProjectApprovalOperateTypeEnum.java:19'}
  revoke: {trust: confirmed, label: 撤销, evidence: 'code_path:ProjectApprovalOperateTypeEnum.java:20'}
triage: keep
```
