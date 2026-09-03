---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:project-approval@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: pattern
title: 审批中的项目审批有多少
page_key: count-running-approvals
domain: 项目管理
anchors:
- tenant_project_approval
---
# 审批中的项目审批有多少

问法：审批中的项目审批有多少

```ground:pattern
pattern: count-running-approvals
question: 审批中的项目审批有多少
sql: SELECT COUNT(DISTINCT id) AS running_approval_count FROM tenant_project_approval
  WHERE wf_status = 'RUNNING' AND enable = 'Y'
verification: PENDING_VALIDATION
```

## 关联
- [[tenant_project_approval]]
