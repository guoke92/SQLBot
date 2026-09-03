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
title: 项目码领取记录有多少
page_key: count-project-code-records
domain: 项目管理
anchors:
- cust_project_code_record
---
# 项目码领取记录有多少

问法：项目码领取记录有多少

```ground:pattern
pattern: count-project-code-records
question: 项目码领取记录有多少
sql: 'SELECT COUNT(1) AS project_code_record_count

  FROM cust_project_code_record

  WHERE enable = ''Y''

  '
verification: PENDING_VALIDATION
```

## 关联
- [[cust_project_code_record]]
