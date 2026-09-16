---
type: enum
title: tenant_project_approval_flow_node_operate_type
page_key: tenant_project_approval_flow_node_operate_type
belong: enums
status: draft
aliases: []
anchors:
- tenant_project_approval_flow_node_operate_type
sources:
- database_profile:tenant_project_approval_flow_node.operate_type
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# tenant_project_approval_flow_node_operate_type

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: tenant_project_approval_flow_node_operate_type
fields:
- tenant_project_approval_flow_node.operate_type
values:
  pass:
    confidence: proposed
  back:
    confidence: proposed
  reject:
    confidence: proposed
  delegate:
    confidence: proposed
  revoke:
    confidence: proposed
ambiguous: false
```
