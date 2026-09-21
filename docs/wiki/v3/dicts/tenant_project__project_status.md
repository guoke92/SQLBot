---
type: dict
title: tenant_project.project_status
page_key: tenant_project__project_status
belong: dicts
status: draft
anchors: [tenant_project.project_status]
sources: ['database_profile:tenant_project.project_status', 'database_schema:tenant_project.project_status',
  'code_path:ProjectStatusEnum.java:24', 'code_path:ProjectStatusEnum.java:20', 'code_path:ProjectStatusEnum.java:28']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [tenant_project]
---

# tenant_project.project_status

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `tenant_project.project_status`，表页 [[tables/tenant_project]]。

## 取值

```ground:dict
dict: tenant_project__project_status
fields: [tenant_project.project_status]
values:
  '1': {trust: confirmed, label: 已生效, evidence: 'code_path:ProjectStatusEnum.java:24'}
  '0': {trust: confirmed, label: 待生效, evidence: 'code_path:ProjectStatusEnum.java:20'}
  '2': {trust: confirmed, label: 已失效, evidence: 'code_path:ProjectStatusEnum.java:28'}
triage: keep
```
