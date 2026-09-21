---
type: dict
title: tenant_project_approval.project_type
page_key: tenant_project_approval__project_type
belong: dicts
status: draft
anchors: [tenant_project_approval.project_type]
sources: ['database_profile:tenant_project_approval.project_type', 'database_schema:tenant_project_approval.project_type',
  'code_path:ProjectApprovalProjectTypeEnum.java:16', 'code_path:ProjectApprovalProjectTypeEnum.java:17']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [tenant_project_approval]
---

# tenant_project_approval.project_type

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `tenant_project_approval.project_type`，表页 [[tables/tenant_project_approval]]。

## 取值

```ground:dict
dict: tenant_project_approval__project_type
fields: [tenant_project_approval.project_type]
values:
  STANDARD: {trust: confirmed, label: 标准项目, evidence: 'code_path:ProjectApprovalProjectTypeEnum.java:16'}
  REGULAR: {trust: confirmed, label: 常规项目, evidence: 'code_path:ProjectApprovalProjectTypeEnum.java:17'}
triage: keep
```
