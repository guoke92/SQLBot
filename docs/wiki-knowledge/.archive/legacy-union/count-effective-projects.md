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
page_key: count-effective-projects
domain: 项目管理
anchors:
- tenant_project
---
# 已生效的租户项目有多少

问法：已生效的租户项目有多少

```ground:pattern
pattern: count-effective-projects
question: 已生效的租户项目有多少
sql: SELECT COUNT(DISTINCT id) AS effective_project_count FROM tenant_project WHERE
  project_status = '1' AND enable = 'Y'
verification: PENDING_VALIDATION
```

## 关联
- [[tenant_project]]
