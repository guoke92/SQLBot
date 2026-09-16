---
type: enum
title: tenant_project_approval_flow_config_node_code
page_key: tenant_project_approval_flow_config_node_code
belong: enums
status: draft
aliases: []
anchors:
- tenant_project_approval_flow_config_node_code
sources:
- database_profile:tenant_project_approval_flow_config.node_code
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# tenant_project_approval_flow_config_node_code

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: tenant_project_approval_flow_config_node_code
fields:
- tenant_project_approval_flow_config.node_code
values:
  PROJECT_CONFIG:
    confidence: proposed
  OTHER:
    confidence: proposed
  PROJECT_MANAGER:
    confidence: proposed
  OPERATION:
    confidence: proposed
  BUSINESS_MANAGER:
    confidence: proposed
  LEGAL_REVIEW:
    confidence: proposed
  LEGAL_PROCESS:
    confidence: proposed
ambiguous: false
```
