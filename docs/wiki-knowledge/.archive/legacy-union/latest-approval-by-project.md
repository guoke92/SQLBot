---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:project-online-approval@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: pattern
title: 按项目查最新审批
page_key: latest-approval-by-project
domain: 项目审批
anchors:
- tenant_project_approval
---
# 按项目查最新审批

问法：按项目查最新审批

```ground:pattern
pattern: latest-approval-by-project
question: 按项目查最新审批
sql: SELECT * FROM tenant_project_approval WHERE ref_tenant_project_approval_tenant_project
  = ? AND enable = 'Y' AND is_latest = 'Y' ORDER BY initiate_time DESC LIMIT 1
verification: PENDING_VALIDATION
```

## 关联
- [[tenant_project_approval]]
