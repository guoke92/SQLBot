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
title: 项目审批分页清单（默认最新轮）
page_key: page-approval-list
domain: 项目审批
anchors:
- tenant_project
- tenant_project_approval
---
# 项目审批分页清单（默认最新轮）

问法：项目审批分页清单（默认最新轮）

```ground:pattern
pattern: page-approval-list
question: 项目审批分页清单（默认最新轮）
sql: SELECT tpa.*, tp.name AS project_name FROM tenant_project_approval tpa LEFT JOIN
  tenant_project tp ON tp.code = tpa.ref_tenant_project_approval_tenant_project WHERE
  tpa.enable = 'Y' AND tpa.is_latest = 'Y' ORDER BY tpa.initiate_time IS NULL DESC,
  tpa.initiate_time DESC, tpa.update_time DESC
verification: PENDING_VALIDATION
```

## 关联
- [[tenant_project]]
- [[tenant_project_approval]]
