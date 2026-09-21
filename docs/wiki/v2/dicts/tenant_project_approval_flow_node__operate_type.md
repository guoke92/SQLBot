---
type: dict
title: tenant_project_approval_flow_node.operate_type
page_key: tenant_project_approval_flow_node__operate_type
belong: dicts
status: draft
anchors: [tenant_project_approval_flow_node.operate_type]
sources: ['database_profile:tenant_project_approval_flow_node.operate_type']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [tenant_project_approval_flow_node]
---

# tenant_project_approval_flow_node.operate_type

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `tenant_project_approval_flow_node.operate_type`，表页 [[tables/tenant_project_approval_flow_node]]。

## 取值

```ground:dict
dict: tenant_project_approval_flow_node__operate_type
fields: [tenant_project_approval_flow_node.operate_type]
values:
  pass: {trust: proposed}
  back: {trust: proposed}
  reject: {trust: proposed}
  delegate: {trust: proposed}
  revoke: {trust: proposed}
triage: keep
```
