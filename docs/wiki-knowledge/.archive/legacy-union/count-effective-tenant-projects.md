---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:tenant-project-lifecycle@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: pattern
title: 已生效的租户项目有多少
page_key: count-effective-tenant-projects
domain: 项目管理
anchors:
- tenant_project
---
# 已生效的租户项目有多少

问法：已生效的租户项目有多少

```ground:pattern
pattern: count-effective-tenant-projects
question: 已生效的租户项目有多少
sql: "SELECT COUNT(1) AS effective_project_count\nFROM tenant_project\nWHERE project_status\
  \ = '1'\n  AND enable = 'Y'\n"
verification: PENDING_VALIDATION
```

## 关联
- [[tenant_project]]
