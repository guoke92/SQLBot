---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:project-code@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: pattern
title: 启用的项目码记录有多少
page_key: count-enabled-project-code-records
domain: 项目管理
anchors:
- cust_project_code_record
---
# 启用的项目码记录有多少

问法：启用的项目码记录有多少

```ground:pattern
pattern: count-enabled-project-code-records
question: 启用的项目码记录有多少
sql: 'SELECT COUNT(id) AS project_code_record_count FROM cust_project_code_record
  WHERE enable = ''Y''

  '
verification: PENDING_VALIDATION
```

## 关联
- [[cust_project_code_record]]
