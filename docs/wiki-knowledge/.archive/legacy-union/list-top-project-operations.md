---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:op-user-coverage@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: pattern
title: 微企链有哪些置顶项目运营关系
page_key: list-top-project-operations
domain: operation
anchors:
- wec_project_operation_rel
---
# 微企链有哪些置顶项目运营关系

问法：微企链有哪些置顶项目运营关系

```ground:pattern
pattern: list-top-project-operations
question: 微企链有哪些置顶项目运营关系
sql: 'SELECT id, wec_project_id, op_contact_a, top_flag

  FROM wec_project_operation_rel

  WHERE top_flag = ''1'''
verification: PENDING_VALIDATION
```

## 关联
- [[wec_project_operation_rel]]
