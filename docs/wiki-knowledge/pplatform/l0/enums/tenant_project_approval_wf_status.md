---
type: enum
title: tenant_project_approval_wf_status
page_key: tenant_project_approval_wf_status
belong: enums
status: draft
aliases: []
anchors:
- tenant_project_approval_wf_status
sources:
- database_profile:tenant_project_approval.wf_status
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
recall: true
---

# tenant_project_approval_wf_status

L0 枚举候选：仅 profile 代码值，无代码 label。

## 取值

```ground:enum
enum: tenant_project_approval_wf_status
fields:
- tenant_project_approval.wf_status
values:
  RUNNING:
    confidence: proposed
  FINISHED:
    confidence: proposed
  TERMINATED:
    confidence: proposed
  PENDING:
    confidence: proposed
  REVOKED:
    confidence: proposed
ambiguous: false
```
