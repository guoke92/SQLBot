---
type: enum
title: tenant_project_approval_flow_node_approval_type
page_key: tenant_project_approval_flow_node_approval_type
belong: enums
status: draft
aliases: []
anchors:
- tenant_project_approval_flow_node_approval_type
sources:
- database_profile:tenant_project_approval_flow_node.approval_type
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# tenant_project_approval_flow_node_approval_type

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: tenant_project_approval_flow_node_approval_type
fields:
- tenant_project_approval_flow_node.approval_type
values:
  ONLINE_APPROVAL:
    confidence: proposed
  BACK_AGREEMENT:
    confidence: proposed
ambiguous: false
```
